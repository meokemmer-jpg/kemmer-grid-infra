#!/usr/bin/env python3
"""
FALLBACK-detect-empty-title-patch.py

=== FALLBACK-ROUTINE (NUR FALLBACK, NACH N SUCCESSFUL RUNS LOESCHBAR) ===

Type: bug-workaround
Reason: detect_roadmap_conflicts.py erzeugt false-positive duplicates
        bei Tasks ohne title-Feld (semantic_fingerprint("", []) == same hash).

Wrap-Script: liest raw detect_roadmap_conflicts-Output, filtert
Duplicates heraus die auf leeren Titeln basieren. In Production
mit echten Tasks nicht noetig.

To-Delete-When: 30 successful Light-Pass-Runs mit echten Titeln
                UND detect_roadmap_conflicts.py upstream gepatched
                UND false-positive-rate < 5% gemessen

Usage (anstelle von direktem detect_roadmap_conflicts.py):
  python FALLBACK-detect-empty-title-patch.py
"""
import json, os, subprocess, sys


# [CRUX-MK] Runtime-Gate (Layer 0)
try:
    import sys as _crux_sys, pathlib as _crux_path
    _crux_sys.path.insert(0, str(_crux_path.Path.home() / ".claude" / "scripts"))
    import crux_runtime as _crux_rt  # auto-checks kill-switch on import
except (ImportError, SystemExit):
    import sys as _crux_sys
    _crux_kf = _crux_path.Path.home() / ".kemmer-grid" / "killed.flag" if '_crux_path' in dir() else None
    if _crux_kf and _crux_kf.exists(): _crux_sys.exit(1)
# /[CRUX-MK] Runtime-Gate

HUB = os.environ.get("BRANCH_HUB", "G:/Meine Ablage/Claude-Knowledge-System/branch-hub")
ROADMAP = os.path.join(HUB, "state", "roadmap-materialized.json")
SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")


def main():
    # Load roadmap to identify empty-title tasks
    empty_title_tasks = set()
    try:
        with open(ROADMAP, "r", encoding="utf-8") as f:
            data = json.load(f)
        for tid, t in (data.get("tasks") or {}).items():
            if not (t.get("title") or "").strip():
                empty_title_tasks.add(tid)
    except Exception as e:
        sys.stderr.write(f"FALLBACK: cannot read roadmap: {e}\n")

    # Run upstream detect
    try:
        r = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "detect_roadmap_conflicts.py")],
            capture_output=True, text=True, timeout=30
        )
        raw = r.stdout
    except Exception as e:
        print(json.dumps({"error": f"FALLBACK: upstream-detect failed: {e}"}))
        sys.exit(1)

    try:
        result = json.loads(raw)
    except Exception:
        print(raw)
        return

    # Filter: remove duplicates referencing empty-title tasks
    filtered = []
    removed = 0
    for c in result.get("conflicts", []):
        if c.get("kind") == "duplicate":
            tid = c.get("task_id")
            details = c.get("details", "")
            if tid in empty_title_tasks or any(e in details for e in empty_title_tasks):
                removed += 1
                continue
        filtered.append(c)

    result["conflicts"] = filtered
    result["summary"] = f"{len(filtered)} conflicts (filtered {removed} empty-title false-positives via FALLBACK)."
    result["_fallback_applied"] = "FALLBACK-detect-empty-title-patch"
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
