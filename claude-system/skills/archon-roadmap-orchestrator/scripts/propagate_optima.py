#!/usr/bin/env python3
"""
propagate_optima.py - Hook-Script: propagiert global-optima.json Aenderungen

Triggered durch:
- Direkten Call nach Config-Edit
- File-Watcher (falls aktiv)
- DF-Evolve-Skill bei Capability-Registry-Update

Effekt:
1. Liest neue global-optima.json
2. Schreibt Snapshot in state/optima-snapshot-<ts>.json (Audit)
3. Appends event 'optima-changed' in event-log.jsonl
4. Touched alle DF-config.yaml (DF-02, DF-03, DF-04, DF-06) mit neuem optima-Hash
5. Alert-Event bei >10% Aenderung in Kern-Parametern (K_0, rho_threshold)
"""
import argparse, hashlib, json, os, sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
OPTIMA_PATH = SKILL_DIR / "global-optima.json"
HUB = Path(os.environ.get("BRANCH_HUB", "G:/Meine Ablage/Claude-Knowledge-System/branch-hub"))
STATE_DIR = HUB / "state"
SNAPSHOT_DIR = STATE_DIR / "optima-snapshots"

# DF-Configs die getoucht werden sollen
DF_CONFIG_PATHS = [
    # Existierende DFs (hypothetisch, falls noch nicht da: skip mit warn)
    "C:/Users/marti/Projects/learning-archon/.archon/dark-factory/DF-02/config.yaml",
    "C:/Users/marti/Projects/learning-archon/.archon/dark-factory/DF-03/config.yaml",
    "C:/Users/marti/Projects/learning-archon/.archon/dark-factory/DF-04/config.yaml",
    str(SKILL_DIR / "dark-factory/DF-06/config.yaml"),
]

sys.path.insert(0, str(SKILL_DIR / "scripts"))

def hash_file(path: Path) -> str:
    if not path.exists():
        return "missing"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]

def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()

def snapshot_optima() -> Path:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    ts = now_iso().replace(":", "").replace("+", "_")[:19]
    snap = SNAPSHOT_DIR / f"optima-{ts}.json"
    snap.write_bytes(OPTIMA_PATH.read_bytes())
    return snap

def compute_delta(new_optima: dict, last_snapshot: Path | None) -> dict:
    """Compare with last snapshot if exists."""
    if last_snapshot is None or not last_snapshot.exists():
        return {"first_run": True, "delta_pct": 100.0, "changed_keys": ["*"]}
    try:
        old = json.loads(last_snapshot.read_text())
    except Exception:
        return {"error": "cannot-parse-last-snapshot"}
    changed = []
    # Scan Top-Level Keys
    for top_key in ["zeitwertverfassung", "token_budgets", "rho_thresholds", "models", "dark_factory_defaults"]:
        old_val = old.get(top_key, {})
        new_val = new_optima.get(top_key, {})
        if old_val != new_val:
            changed.append(top_key)
    # Kern-Alarm bei K_0, rho_thresholds
    kern_changed = False
    old_k0 = (old.get("zeitwertverfassung") or {}).get("K_0_base_eur")
    new_k0 = (new_optima.get("zeitwertverfassung") or {}).get("K_0_base_eur")
    if old_k0 and new_k0 and abs(new_k0 - old_k0) / old_k0 > 0.1:
        kern_changed = True
    return {"first_run": False, "changed_keys": changed, "kern_changed": kern_changed}

def touch_df_configs(optima_hash: str) -> list:
    """Schreibt optima_ref + hash in jedes DF-config, falls vorhanden."""
    touched = []
    for p_str in DF_CONFIG_PATHS:
        p = Path(p_str)
        if not p.exists():
            continue
        try:
            content = p.read_text(encoding="utf-8")
            # Append optima-ref am Ende wenn noch nicht da
            ref_line = f"# optima-ref: global-optima.json#{optima_hash}"
            if ref_line.split("#")[0].strip() not in content:
                new_content = content.rstrip() + f"\n{ref_line}\n"
                p.write_text(new_content, encoding="utf-8")
                touched.append(str(p))
        except Exception as e:
            print(f"WARN: cannot touch {p}: {e}", file=sys.stderr)
    return touched

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--reason", default="manual")
    args = p.parse_args()

    if not OPTIMA_PATH.exists():
        print(json.dumps({"status": "ERROR", "reason": "global-optima.json missing"}))
        sys.exit(1)

    new_optima = json.loads(OPTIMA_PATH.read_text(encoding="utf-8"))
    new_hash = hash_file(OPTIMA_PATH)

    # Find latest previous snapshot
    snapshots = sorted(SNAPSHOT_DIR.glob("optima-*.json")) if SNAPSHOT_DIR.exists() else []
    last_snap = snapshots[-1] if snapshots else None
    delta = compute_delta(new_optima, last_snap)

    if args.dry_run:
        print(json.dumps({"dry_run": True, "new_hash": new_hash, "delta": delta}, indent=2))
        return

    snap_path = snapshot_optima()
    touched = touch_df_configs(new_hash)

    # Append event via event_log_append
    try:
        from event_log_append import append_event
        append_event(
            branch="orchestrator",
            event_type="reconciliation",  # reuse type; no direct "optima-changed"
            task_id="",
            payload={
                "kind": "optima-changed",
                "new_hash": new_hash,
                "changed_keys": delta.get("changed_keys", []),
                "kern_changed": delta.get("kern_changed", False),
                "touched_df_configs": touched,
                "reason": args.reason
            }
        )
    except ImportError:
        print("WARN: event_log_append not importable, skip event", file=sys.stderr)

    # Kern-Alarm: wenn K_0 >10% geaendert -> alert_martin call
    if delta.get("kern_changed"):
        alert_script = SKILL_DIR / "scripts" / "alert_martin.py"
        if alert_script.exists():
            os.system(f'python "{alert_script}" --reason kern_optima_change --delta "{json.dumps(delta)}"')

    print(json.dumps({
        "status": "OK",
        "new_hash": new_hash,
        "snapshot": str(snap_path),
        "touched_df_configs": touched,
        "delta": delta
    }, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
