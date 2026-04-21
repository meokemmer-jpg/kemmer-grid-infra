#!/usr/bin/env python3
# Session-Start-Hook: Cache-Health + 1h-TTL Env-Var Check [CRUX-MK]
# Gap-1 + Gap-7 Mechanik: Prueft ob ENABLE_PROMPT_CACHING_1H gesetzt ist
# + liefert Orchestration-Brief (DF-10) an Claude als Bootstrap-Payload.

"""
Outputs (zu stdout, fuer Claude-Bootstrap-Anzeige):
  - Env-Check Warnung wenn ENABLE_PROMPT_CACHING_1H nicht gesetzt
  - Summary: Top-3 Templates, Top-3 LLM-Routes, Haiku-Fallback-Count aus
    ~/.claude/data/orchestration-brief.md (falls DF-10 bereits gelaufen ist)
"""

import os
import sys
from pathlib import Path


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

BRIEF = Path("~/.claude/data/orchestration-brief.md").expanduser()
CACHE_REPORT = Path("~/.claude/data/cache-health-report.json").expanduser()


def main():
    lines = ["[CRUX-MK] Token-Orchestration Session-Start-Check"]

    # 1h-TTL Env-Var check
    if os.environ.get("ENABLE_PROMPT_CACHING_1H", "").lower() == "true":
        lines.append("  [OK] ENABLE_PROMPT_CACHING_1H=true (1h-Cache aktiv)")
    else:
        lines.append("  [WARN] ENABLE_PROMPT_CACHING_1H nicht gesetzt -> 5m TTL Default (Issue #46829)")
        lines.append("         Fix: setx ENABLE_PROMPT_CACHING_1H true + Terminal neu")

    # Orchestration-Brief
    if BRIEF.exists():
        lines.append("  [INFO] Orchestration-Brief verfuegbar:")
        try:
            with open(BRIEF, "r", encoding="utf-8") as f:
                # Nur erste 10 Zeilen fuer kompakten Bootstrap
                for i, line in enumerate(f):
                    if i >= 10:
                        break
                    lines.append(f"    {line.rstrip()}")
        except Exception as e:
            lines.append(f"  [WARN] Brief-Read-Fehler: {e}")
    else:
        lines.append("  [INFO] Kein DF-10-Brief noch (erste Runs oder Shadow-Mode).")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
