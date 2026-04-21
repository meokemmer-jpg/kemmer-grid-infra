#!/usr/bin/env python3
# PreToolUse-Hook: Token-Budget-Enforcer [CRUX-MK]
# Reads DF-10 scores.json and applies max_tokens hints per task-class.
# Shadow-Mode: logs only, does not enforce.
# Live-Mode: would inject max_tokens into request (needs Claude Code internals access).

"""
Hook-Input via stdin (JSON):
  {"tool_name": "...", "input": {...}}

Reads:
  ~/.claude/data/output-budget-scores.json
  ~/.claude/data/DF-10-STOP.flag (if exists: no-op)

Behavior:
  1. Classify task (simple heuristic for now; later Haiku-based)
  2. Lookup recommended_max_tokens in scores.json
  3. Shadow-Mode: log decision to ~/.claude/data/budget-decisions-log.jsonl
  4. Live-Mode (future): inject hint
"""

import sys
import json
from pathlib import Path
from datetime import datetime


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

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

STOP_FLAG = Path("~/.claude/data/DF-10-STOP.flag").expanduser()
SCORES = Path("~/.claude/data/output-budget-scores.json").expanduser()
DECISIONS_LOG = Path("~/.claude/data/budget-decisions-log.jsonl").expanduser()


FALLBACK_CLASSES = {
    "trivial_response": 200,
    "routine_classification": 500,
    "quick_answer": 1000,
    "substantive_analysis": 3000,
    "long_synthesis": 8000,
    "full_artifact": 15000,
    "emergency": 64000,
}


def classify_task_heuristic(data):
    """Phase-1 simple heuristic. Phase-2: Haiku-basiert."""
    tool = data.get("tool_name", "").lower()
    # Tool-basierte Pre-Klassifikation (rough)
    if tool in ("bash", "glob", "grep", "read"):
        return "routine_classification"
    if tool == "write":
        return "full_artifact"
    if tool == "edit":
        return "substantive_analysis"
    if tool == "agent" or tool == "task":
        return "long_synthesis"
    return "substantive_analysis"


def main():
    if STOP_FLAG.exists():
        return  # Kill-switch active

    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        data = json.loads(raw)
    except Exception:
        return

    task_class = classify_task_heuristic(data)

    recommended = FALLBACK_CLASSES.get(task_class, 3000)
    source = "fallback_static"
    if SCORES.exists():
        try:
            with open(SCORES, "r", encoding="utf-8") as f:
                scores = json.load(f)
            if task_class in scores:
                recommended = scores[task_class].get("recommended_max_tokens", recommended)
                source = "df10_scores"
        except Exception:
            pass

    # Shadow-Mode: log only
    decision = {
        "ts": datetime.now().isoformat(),
        "tool_name": data.get("tool_name"),
        "classified_as": task_class,
        "recommended_max_tokens": recommended,
        "source": source,
        "mode": "shadow",
    }
    DECISIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(DECISIONS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(decision, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[BUDGET-ENFORCER WARN] {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
