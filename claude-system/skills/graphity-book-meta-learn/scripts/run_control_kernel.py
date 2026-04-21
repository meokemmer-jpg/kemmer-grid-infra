#!/usr/bin/env python3
"""
run_control_kernel.py -- E11 Run-Control-Kernel [CRUX-MK]
Dark-Factory Tier-2-Pflicht. Codex-Empfehlung Wave-1 (2/2 + Grok-keep).

Funktionen:
- 2-fails Hard-Stop
- Tagesbudget in EUR (Hardcap)
- JSONL-Audit-Trail pro Run
- Kill-Switch (DISABLED.flag)
- one-run = one-commit Disziplin
- Martin-Alert bei Budget-Breach / 2-Fails / Quality-Drop

Usage:
    python run_control_kernel.py --init --run-id <uuid>
    python run_control_kernel.py --check-preflight
    python run_control_kernel.py --record-fail --run-id <uuid> --reason "..."
    python run_control_kernel.py --record-success --run-id <uuid> --cost-eur 0.05
    python run_control_kernel.py --status
    python run_control_kernel.py --alert-martin --message "..."

Exit-Codes:
    0 = OK / Proceed
    1 = WARN (near budget)
    2 = BLOCK (kill-switch aktiv, budget breach, 2-fails)
    3 = ERROR
"""

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
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

# ==========================================================================
# CONFIG
# ==========================================================================

DARK_FACTORY_ROOT = Path("G:/Meine Ablage/Claude-Knowledge-System/dark-factory/DF-07-graphity-book-writer")
AUDIT_LOG = DARK_FACTORY_ROOT / "audit.jsonl"
DISABLED_FLAG = DARK_FACTORY_ROOT / "DISABLED.flag"
STATE_FILE = DARK_FACTORY_ROOT / "run_control_state.json"
BUDGET_FILE = DARK_FACTORY_ROOT / "daily_budget.json"

DEFAULT_DAILY_BUDGET_EUR = 15.0   # Wave-2 token-guard: realistisch hoeher als 5 EUR
DEFAULT_MAX_PER_RUN_EUR = 3.0
MAX_CONSECUTIVE_FAILS = 2
MARTIN_ALERT_PATH = Path("G:/Meine Ablage/Claude-Knowledge-System/branch-hub/inbox/to-martin-df07-alerts.md")


# ==========================================================================
# HELPERS
# ==========================================================================

def ensure_dirs():
    DARK_FACTORY_ROOT.mkdir(parents=True, exist_ok=True)
    MARTIN_ALERT_PATH.parent.mkdir(parents=True, exist_ok=True)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def today_key():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def append_audit(entry):
    entry["ts"] = now_iso()
    ensure_dirs()
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_state():
    if not STATE_FILE.exists():
        return {
            "initialized_at": now_iso(),
            "runs_total": 0,
            "fails_total": 0,
            "consecutive_fails": 0,
            "last_run_id": None,
            "last_run_at": None,
            "last_fail_reason": None,
        }
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(state):
    ensure_dirs()
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def load_budget():
    if not BUDGET_FILE.exists():
        return {"daily": {}}
    return json.loads(BUDGET_FILE.read_text(encoding="utf-8"))


def save_budget(budget):
    ensure_dirs()
    BUDGET_FILE.write_text(json.dumps(budget, indent=2), encoding="utf-8")


def today_spent():
    budget = load_budget()
    return budget["daily"].get(today_key(), 0.0)


def record_spend(cost_eur):
    budget = load_budget()
    budget["daily"].setdefault(today_key(), 0.0)
    budget["daily"][today_key()] += cost_eur
    save_budget(budget)


# ==========================================================================
# PRE-FLIGHT CHECKS
# ==========================================================================

def check_preflight(verbose=False):
    """Gibt (ok, reason) zurueck. False = block."""
    # Kill-switch
    if DISABLED_FLAG.exists():
        flag_content = DISABLED_FLAG.read_text(encoding="utf-8") if DISABLED_FLAG.stat().st_size > 0 else "no-reason"
        return False, f"DISABLED.flag aktiv: {flag_content}"

    # State-Check
    state = load_state()
    if state["consecutive_fails"] >= MAX_CONSECUTIVE_FAILS:
        return False, f"{state['consecutive_fails']} consecutive fails >= {MAX_CONSECUTIVE_FAILS}"

    # Budget-Check
    spent = today_spent()
    if spent >= DEFAULT_DAILY_BUDGET_EUR:
        return False, f"Daily budget exhausted: {spent:.2f} EUR >= {DEFAULT_DAILY_BUDGET_EUR:.2f} EUR"

    if verbose:
        return True, f"OK. Today spent {spent:.2f}/{DEFAULT_DAILY_BUDGET_EUR} EUR, fails {state['consecutive_fails']}/{MAX_CONSECUTIVE_FAILS}"
    return True, "OK"


# ==========================================================================
# ALERT MARTIN
# ==========================================================================

def alert_martin(reason, run_id=None, severity="WARN"):
    ensure_dirs()
    ts = now_iso()
    with open(MARTIN_ALERT_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n---\n## DF-07 Alert [{severity}] @ {ts}\n")
        f.write(f"- run_id: {run_id or 'n/a'}\n")
        f.write(f"- reason: {reason}\n")
    append_audit({"event": "martin_alert", "severity": severity, "reason": reason, "run_id": run_id})


# ==========================================================================
# COMMANDS
# ==========================================================================

def cmd_init(run_id=None):
    run_id = run_id or str(uuid.uuid4())
    ok, reason = check_preflight()
    if not ok:
        print(f"BLOCK: {reason}", file=sys.stderr)
        append_audit({"event": "run_blocked", "reason": reason, "run_id": run_id})
        sys.exit(2)

    state = load_state()
    state["runs_total"] += 1
    state["last_run_id"] = run_id
    state["last_run_at"] = now_iso()
    save_state(state)

    append_audit({"event": "run_init", "run_id": run_id})
    print(f"OK run_id={run_id}")
    return 0


def cmd_record_fail(run_id, reason):
    state = load_state()
    state["fails_total"] += 1
    state["consecutive_fails"] += 1
    state["last_fail_reason"] = reason
    save_state(state)

    append_audit({"event": "run_fail", "run_id": run_id, "reason": reason, "consecutive_fails": state["consecutive_fails"]})

    if state["consecutive_fails"] >= MAX_CONSECUTIVE_FAILS:
        alert_martin(f"{MAX_CONSECUTIVE_FAILS} consecutive fails - DF-07 auto-disabled", run_id, "CRITICAL")
        DISABLED_FLAG.write_text(f"AUTO-DISABLED {now_iso()}: {state['consecutive_fails']} consecutive fails", encoding="utf-8")
        print(f"CRITICAL: Auto-disabled after {state['consecutive_fails']} fails", file=sys.stderr)
        sys.exit(2)
    print(f"FAIL recorded. consecutive={state['consecutive_fails']}")
    return 0


def cmd_record_success(run_id, cost_eur=0.0):
    state = load_state()
    state["consecutive_fails"] = 0   # Reset on success
    save_state(state)

    record_spend(cost_eur)
    spent = today_spent()

    append_audit({"event": "run_success", "run_id": run_id, "cost_eur": cost_eur, "today_total_eur": spent})

    # Budget-Warning
    if spent > DEFAULT_DAILY_BUDGET_EUR * 0.8:
        alert_martin(f"Daily budget 80% reached: {spent:.2f}/{DEFAULT_DAILY_BUDGET_EUR} EUR", run_id, "WARN")

    print(f"OK cost={cost_eur:.4f} today_total={spent:.2f}/{DEFAULT_DAILY_BUDGET_EUR}")
    return 0


def cmd_status(verbose=False):
    state = load_state()
    spent = today_spent()
    disabled = DISABLED_FLAG.exists()

    status = {
        "disabled": disabled,
        "disabled_reason": DISABLED_FLAG.read_text(encoding="utf-8") if disabled else None,
        "runs_total": state["runs_total"],
        "fails_total": state["fails_total"],
        "consecutive_fails": state["consecutive_fails"],
        "last_run_id": state["last_run_id"],
        "last_run_at": state["last_run_at"],
        "today_spent_eur": spent,
        "daily_budget_eur": DEFAULT_DAILY_BUDGET_EUR,
        "budget_pct": spent / DEFAULT_DAILY_BUDGET_EUR if DEFAULT_DAILY_BUDGET_EUR else 0,
    }
    print(json.dumps(status, indent=2, default=str))
    return 0


def cmd_enable():
    if DISABLED_FLAG.exists():
        DISABLED_FLAG.unlink()
        # Reset consecutive fails on manual re-enable
        state = load_state()
        state["consecutive_fails"] = 0
        save_state(state)
        append_audit({"event": "manually_reenabled"})
        print("ENABLED (DISABLED.flag removed, fails reset)")
    else:
        print("Already enabled")
    return 0


def cmd_disable(reason=""):
    ensure_dirs()
    DISABLED_FLAG.write_text(f"MANUAL {now_iso()}: {reason}", encoding="utf-8")
    append_audit({"event": "manually_disabled", "reason": reason})
    print(f"DISABLED: {reason}")
    return 0


# ==========================================================================
# MAIN
# ==========================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--check-preflight", action="store_true")
    ap.add_argument("--record-fail", action="store_true")
    ap.add_argument("--record-success", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--enable", action="store_true")
    ap.add_argument("--disable", action="store_true")
    ap.add_argument("--alert-martin", action="store_true")
    ap.add_argument("--run-id")
    ap.add_argument("--reason", default="")
    ap.add_argument("--cost-eur", type=float, default=0.0)
    ap.add_argument("--message", default="")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if args.init:
        return cmd_init(args.run_id)
    if args.check_preflight:
        ok, reason = check_preflight(verbose=True)
        print(reason)
        sys.exit(0 if ok else 2)
    if args.record_fail:
        if not args.run_id:
            print("ERROR: --run-id required", file=sys.stderr)
            sys.exit(3)
        return cmd_record_fail(args.run_id, args.reason)
    if args.record_success:
        if not args.run_id:
            print("ERROR: --run-id required", file=sys.stderr)
            sys.exit(3)
        return cmd_record_success(args.run_id, args.cost_eur)
    if args.status:
        return cmd_status(args.verbose)
    if args.enable:
        return cmd_enable()
    if args.disable:
        return cmd_disable(args.reason)
    if args.alert_martin:
        alert_martin(args.message, args.run_id, "INFO")
        return 0

    ap.print_help()
    return 3


if __name__ == "__main__":
    sys.exit(main())
