#!/usr/bin/env python3
"""
FALLBACK-retention-sweep.py

=== SWEEP-SCRIPT FUER FALLBACK-MANAGEMENT ===

Prueft FALLBACK-manifest.json und identifiziert Kandidaten fuer Loeschung:
- Fallback hat >= min_successful_runs_without_trigger mal NICHT getriggert
- Fallback ist min_days_active Tage alt

Output: Report mit Deletion-Kandidaten + Empfehlung pro Fallback.
Schreibt Alert in BULLETIN.md wenn Kandidaten gefunden.

Usage:
  python FALLBACK-retention-sweep.py                # Report auf stdout
  python FALLBACK-retention-sweep.py --auto-notify  # + BULLETIN-Alert
  python FALLBACK-retention-sweep.py --delete <name>  # Interaktiv loeschen (verlangt Martin-Approval)

Scheduled: monatlich via Scheduled Task oder als Teil des Deep-Pass.
"""
import argparse, json, os, shutil, sys
from datetime import datetime, timezone
from pathlib import Path

FALLBACK_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = FALLBACK_DIR / "FALLBACK-manifest.json"
HUB = Path(os.environ.get("BRANCH_HUB", "G:/Meine Ablage/Claude-Knowledge-System/branch-hub"))
BULLETIN = HUB / "BULLETIN.md"
AUDIT = HUB / "audit" / "fallback-sweep.jsonl"


def load_manifest():
    with open(MANIFEST, "r", encoding="utf-8") as f:
        return json.load(f)


def save_manifest(m):
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2, ensure_ascii=False)


def sweep(auto_notify=False):
    m = load_manifest()
    policy = m.get("retention_policy", {})
    min_runs = policy.get("min_successful_runs_without_trigger", 30)
    min_days = policy.get("min_days_active", 30)

    now = datetime.now(timezone.utc)
    candidates = []
    active = []

    for name, fb in m.get("fallbacks", {}).items():
        triggered = fb.get("triggered_count", 0)
        successes = fb.get("success_count_without_this_fallback", 0)
        created = fb.get("created_at", "")
        try:
            created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            age_days = (now - created_dt).days
        except Exception:
            age_days = 0

        is_candidate = (
            triggered == 0
            and successes >= min_runs
            and age_days >= min_days
        )

        entry = {
            "name": name,
            "file": fb.get("file"),
            "type": fb.get("type"),
            "triggered_count": triggered,
            "successes_without_this": successes,
            "age_days": age_days,
            "to_delete_when": fb.get("to_delete_when"),
            "is_deletion_candidate": is_candidate
        }
        if is_candidate:
            candidates.append(entry)
        else:
            active.append(entry)

    report = {
        "ts": now.isoformat(),
        "policy": {"min_runs": min_runs, "min_days": min_days},
        "total_fallbacks": len(m.get("fallbacks", {})),
        "deletion_candidates": candidates,
        "still_active": active
    }

    # Append to sweep history
    m.setdefault("sweep_history", []).append({
        "ts": report["ts"],
        "n_candidates": len(candidates),
        "n_active": len(active)
    })
    save_manifest(m)

    # Audit
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": report["ts"],
            "op": "sweep",
            "n_candidates": len(candidates),
            "n_active": len(active)
        }) + "\n")

    # BULLETIN-Alert falls Kandidaten
    if auto_notify and candidates:
        alert = (f"\n[FALLBACK-SWEEP {report['ts']}] "
                 f"{len(candidates)} Fallback(s) Kandidat fuer Loeschung: "
                 f"{', '.join(c['name'] for c in candidates)}. "
                 f"Martin-Approval Pflicht. See FALLBACK-manifest.json.\n")
        try:
            with open(BULLETIN, "a", encoding="utf-8") as f:
                f.write(alert)
        except Exception as e:
            sys.stderr.write(f"WARN: BULLETIN-write failed: {e}\n")

    return report


def delete_fallback(name: str):
    m = load_manifest()
    fb = m.get("fallbacks", {}).get(name)
    if not fb:
        print(json.dumps({"error": f"fallback '{name}' not in manifest"}))
        sys.exit(1)

    fpath = fb.get("file")
    if fpath and fpath != "N/A" and not fpath.startswith("fallback/"):
        print(json.dumps({"error": f"invalid file path: {fpath}"}))
        sys.exit(1)

    if fpath and fpath != "N/A":
        full = FALLBACK_DIR.parent / fpath
        if full.exists():
            full.unlink()

    del m["fallbacks"][name]
    save_manifest(m)
    print(json.dumps({"deleted": name, "status": "OK", "note": "Martin-approval must have been obtained manually"}))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--auto-notify", action="store_true")
    p.add_argument("--delete", help="Name of fallback to delete (requires Martin-approval)")
    args = p.parse_args()

    if args.delete:
        delete_fallback(args.delete)
    else:
        report = sweep(auto_notify=args.auto_notify)
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
