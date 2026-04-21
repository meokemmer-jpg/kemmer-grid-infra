#!/usr/bin/env python3
# [CRUX-MK] Layer 0 — Shared Runtime-Library fuer alle Kemmer-Scripts
# Eine Zeile Import, sofortiger CRUX-Gate-Check beim Import.
# Verwendung in jedem executable Script: `from crux_runtime import *` (oder manueller call)

"""
CRUX-Runtime-Library.

Import-Verhalten: Beim Import wird kill-switch geprueft. Wenn aktiv: sys.exit(1).
Gibt Utility-Funktionen fuer CRUX-Logging + rho-Tracking.

Minimal-Integration in jedem Script:

    # Am Top nach Imports:
    try:
        import sys, pathlib
        sys.path.insert(0, str(pathlib.Path.home() / ".claude" / "scripts"))
        import crux_runtime  # raises SystemExit if kill-switch active
    except ImportError:
        pass  # graceful degradation falls crux_runtime fehlt
"""

import json
import pathlib
import sys
import datetime

CRUX_DIR = pathlib.Path.home() / ".kemmer-grid"
CRUX_DIR.mkdir(exist_ok=True)
KILL_FLAG = CRUX_DIR / "killed.flag"
SCRIPT_EVENTS = CRUX_DIR / "script-events.jsonl"


def check_kill_switch(script_name: str = None) -> None:
    """Raises SystemExit(1) if kill-switch flag exists."""
    if KILL_FLAG.exists():
        caller = script_name or sys.argv[0] if sys.argv else "unknown"
        print(f"[CRUX-MK] Kill-Switch aktiv ({KILL_FLAG}). Script '{caller}' terminiert.", file=sys.stderr)
        sys.exit(1)


def log_script_event(script: str, action: str, verdict: str = "PASS", **kwargs) -> None:
    """Append-Log fuer Script-Events. Non-blocking bei File-Fail."""
    entry = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "script": script,
        "action": action,
        "verdict": verdict,
    }
    entry.update(kwargs)
    try:
        with open(SCRIPT_EVENTS, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def crux_gate(
    action: str,
    estimated_rho: str,
    k0_risk: str = "unknown",
    q0_risk: str = "unknown",
    i_min: str = "unknown",
    l_martin: str = "unknown",
    wargame: str = "none",
) -> str:
    """
    In-Python-Wrapper um crux-check logic.
    Returns 'PASS' | 'WARN' | 'REJECT'. Blockiert bei REJECT via SystemExit.
    """
    check_kill_switch()

    verdict = "PASS"
    reasons = []

    if k0_risk == "high":
        verdict = "REJECT"
        reasons.append("K_0 high risk")
    if q0_risk == "high":
        verdict = "REJECT"
        reasons.append("Q_0 high risk")
    if i_min == "negative":
        verdict = "REJECT"
        reasons.append("I_min negative")

    if verdict == "PASS" and any(w in estimated_rho.lower() for w in ["unclear", "unknown", "n/a"]):
        verdict = "WARN"
        reasons.append("rho unklar")

    if verdict == "PASS" and wargame == "none" and (k0_risk == "medium" or q0_risk == "medium"):
        verdict = "WARN"
        reasons.append("substantielle Aktion ohne Wargame")

    log_script_event(
        script=sys.argv[0] if sys.argv else "python",
        action=action,
        verdict=verdict,
        rho=estimated_rho, k0=k0_risk, q0=q0_risk,
        i_min=i_min, l_martin=l_martin, wargame=wargame,
        reasons="; ".join(reasons),
    )

    if verdict == "REJECT":
        print(f"[CRUX-MK] REJECT {action}: {'; '.join(reasons)}", file=sys.stderr)
        sys.exit(1)

    if verdict == "WARN":
        print(f"[CRUX-MK] WARN {action}: {'; '.join(reasons)}", file=sys.stderr)

    return verdict


# Auto-Check on import
check_kill_switch()
