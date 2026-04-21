#!/usr/bin/env python3
# PostToolUse-Hook: Token-Usage-Logger [CRUX-MK]
# Logs every tool-call's token usage to JSONL for DF-10.
# Lightweight (no heavy imports), tolerates missing data.

"""
Hook-Input via stdin (JSON):
{
  "tool_name": "...",
  "input": {...},
  "output": "..." or structured,
  "usage": {                 # if available from Claude Code internals
    "input_tokens": N,
    "output_tokens": N,
    "cache_read_input_tokens": N,
    "cache_creation_input_tokens": N,
    "stop_reason": "end_turn|max_tokens|...",
  },
  "task_class": "..."        # if classifier ran
}

Writes to:
  ~/.claude/data/token-usage-log.jsonl
  ~/.claude/data/cache-metrics-log.jsonl
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

# BIAS-036 Fix: UTF-8 fuer Windows cp1252
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

TOKEN_LOG = Path("~/.claude/data/token-usage-log.jsonl").expanduser()
CACHE_LOG = Path("~/.claude/data/cache-metrics-log.jsonl").expanduser()


def safe_append(path, entry):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        # Hooks must never crash the main call
        print(f"[TOKEN-LOGGER WARN] {e}", file=sys.stderr)


def main():
    # Read hook input (stdin JSON expected when Claude Code provides it;
    # fallback to no-op for unsupported cases)
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        data = json.loads(raw)
    except Exception:
        return

    tool_name = data.get("tool_name", "unknown")
    usage = data.get("usage", {})
    task_class = data.get("task_class", "unknown")

    # Token-Usage-Entry
    token_entry = {
        "ts": datetime.now().isoformat(),
        "tool_name": tool_name,
        "task_class": task_class,
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "stop_reason": usage.get("stop_reason", "unknown"),
        "llm_provider": data.get("llm_provider", "claude_opus"),
    }
    safe_append(TOKEN_LOG, token_entry)

    # Cache-Metrics-Entry (separates Log damit DF-10 effizient scannen kann)
    cache_entry = {
        "ts": token_entry["ts"],
        "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0),
        "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0),
        "ephemeral_5m_input_tokens": usage.get("cache_creation", {}).get("ephemeral_5m_input_tokens", 0),
        "ephemeral_1h_input_tokens": usage.get("cache_creation", {}).get("ephemeral_1h_input_tokens", 0),
    }
    if any(v > 0 for k, v in cache_entry.items() if k != "ts"):
        safe_append(CACHE_LOG, cache_entry)


if __name__ == "__main__":
    main()
