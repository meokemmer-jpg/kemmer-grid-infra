#!/usr/bin/env python3
# Skill-Usage-Logger [CRUX-MK]
# Invoked via PreToolUse-Hook on Skill tool or via PostToolUse hook
# Logs every skill invocation to ~/.claude/data/skill-usage-log.jsonl
# DF-10 uses this for empirical skill-cleanup after 30 days.

"""
Hook-Input via stdin (JSON):
  {"tool_name": "Skill", "input": {"skill": "...", "args": "..."}}

Writes to:
  ~/.claude/data/skill-usage-log.jsonl

Purpose:
  Identify unused skills (via 30+ day audit). Score skills by:
  - invocation_count per month
  - task_class distribution
  - rho_gain correlation (if quality_score tracked)

Future (DF-10 Phase-2):
  - Auto-disable skills with 0 invocations in 30 days
  - Suggest skill consolidation for overlapping skills
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

LOG = Path("~/.claude/data/skill-usage-log.jsonl").expanduser()


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        data = json.loads(raw)
    except Exception:
        return

    tool_name = data.get("tool_name", "")
    if tool_name != "Skill":
        return  # Only log Skill invocations

    input_data = data.get("input", {})
    skill_name = input_data.get("skill", "unknown")

    entry = {
        "ts": datetime.now().isoformat(),
        "skill": skill_name,
        "args_provided": bool(input_data.get("args")),
    }

    LOG.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[SKILL-LOGGER WARN] {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
