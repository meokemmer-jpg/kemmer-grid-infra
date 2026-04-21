#!/usr/bin/env python3
"""
token_guard.py - Zentraler Token-Guard mit Zeitwertverfassung (rho=CM*L-OPEX-h*L*W)

9OS-MYZ-35-inspiriert, angepasst fuer Claude-Orchestrator + Dark-Factories.

Usage:
  python token_guard.py --init --workflow roadmap-orchestrate-v2
  python token_guard.py --check --workflow <name> --model <model> --estimated-input 50000 --estimated-output 5000 --task-type priorization
  python token_guard.py --record --workflow <name> --model <model> --input 48000 --output 4500 --action "priorize-tasks"
  python token_guard.py --finalize --workflow <name>
  python token_guard.py --report [--workflow <name>] [--days 7]
  python token_guard.py --guard --action "x" --estimated-cost-eur 2.5 [--ceiling-override]
"""
import argparse, hashlib, json, os, sys
from datetime import datetime, timezone, timedelta
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

SKILL_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
OPTIMA_PATH = SKILL_DIR / "global-optima.json"
HUB = Path(os.environ.get("BRANCH_HUB", "G:/Meine Ablage/Claude-Knowledge-System/branch-hub"))
STATE_DIR = HUB / "state"
AUDIT_DIR = HUB / "audit"
GLOBAL_LOG = STATE_DIR / "token-global-log.jsonl"
AUDIT_LOG = AUDIT_DIR / "token-guard.jsonl"

def _now():
    return datetime.now(timezone.utc).astimezone().isoformat()

def _load_optima():
    if not OPTIMA_PATH.exists():
        return {}
    return json.loads(OPTIMA_PATH.read_text(encoding="utf-8"))

def _budget_path(wf):
    return STATE_DIR / f"token-budget-{wf}.json"

def _load_budget(wf):
    p = _budget_path(wf)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))

def _save_budget(wf, data):
    p = _budget_path(wf)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def _append_log(path, entry):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def _cost_eur(optima, model, input_tok, output_tok):
    m = (optima.get("models") or {}).get(model, {})
    ci = m.get("cost_per_1k_input", 0.005)
    co = m.get("cost_per_1k_output", 0.020)
    return (input_tok / 1000.0) * ci + (output_tok / 1000.0) * co

def cmd_init(args, optima):
    budget_total = (optima.get("token_budgets") or {}).get("per_workflow_default_eur", 2.0)
    data = {
        "workflow": args.workflow,
        "init_at": _now(),
        "budget_total_eur": budget_total,
        "budget_used_eur": 0.0,
        "records": [],
        "cm_cumulative_eur": 0.0,
        "status": "ACTIVE"
    }
    _save_budget(args.workflow, data)
    _append_log(AUDIT_LOG, {"ts": _now(), "op": "init", "workflow": args.workflow, "budget_total_eur": budget_total})
    print(json.dumps({"workflow": args.workflow, "status": "OK",
                      "budget_total_eur": budget_total,
                      "budget_remaining_pct": 1.0,
                      "recommendation": "proceed"}, indent=2))

def cmd_check(args, optima):
    data = _load_budget(args.workflow)
    if not data:
        print(json.dumps({"status": "ERROR", "reason": "budget-not-initialized"}))
        sys.exit(1)
    est_cost = _cost_eur(optima, args.model, args.estimated_input, args.estimated_output)
    projected_used = data["budget_used_eur"] + est_cost
    total = data["budget_total_eur"]
    warn_pct = (optima.get("token_budgets") or {}).get("per_session_warn_pct", 0.7)
    block_pct = (optima.get("token_budgets") or {}).get("per_session_block_pct", 0.95)
    ceiling = (optima.get("token_budgets") or {}).get("per_action_ceiling_eur", 5.0)

    status = "OK"
    rec = "proceed"
    if est_cost > ceiling:
        status = "BLOCK"
        rec = "abort-per-action-ceiling"
    elif projected_used >= total * block_pct:
        status = "BLOCK"
        rec = "abort-budget-exhausted"
    elif projected_used >= total * warn_pct:
        status = "WARN"
        rec = "throttle-or-use-smaller-model"

    out = {
        "workflow": args.workflow,
        "model": args.model,
        "estimated_cost_eur": round(est_cost, 4),
        "budget_used_eur": round(data["budget_used_eur"], 4),
        "budget_total_eur": total,
        "projected_used_eur": round(projected_used, 4),
        "projected_remaining_pct": round(max(0, (total - projected_used) / total), 3),
        "status": status,
        "recommendation": rec
    }
    print(json.dumps(out, indent=2))
    if status == "BLOCK":
        sys.exit(1)

def cmd_record(args, optima):
    data = _load_budget(args.workflow)
    if not data:
        print(json.dumps({"status": "ERROR", "reason": "budget-not-initialized"}))
        sys.exit(1)
    actual_cost = _cost_eur(optima, args.model, args.input, args.output)
    # CM lookup: if task-type known
    task_type = getattr(args, "task_type", None) or args.action.split("-")[0] if "-" in args.action else args.action
    cm_map = (optima.get("zeitwertverfassung") or {}).get("CM_base_eur_per_action", {})
    cm = cm_map.get(task_type, 10.0)

    rec = {
        "ts": _now(),
        "action": args.action,
        "model": args.model,
        "input_tokens": args.input,
        "output_tokens": args.output,
        "actual_cost_eur": round(actual_cost, 4),
        "cm_eur": cm,
        "rho_run": round(cm - actual_cost, 4)
    }
    data["records"].append(rec)
    data["budget_used_eur"] = round(data["budget_used_eur"] + actual_cost, 4)
    data["cm_cumulative_eur"] = round(data["cm_cumulative_eur"] + cm, 4)
    _save_budget(args.workflow, data)
    _append_log(GLOBAL_LOG, {"workflow": args.workflow, **rec})

    remaining_pct = max(0, (data["budget_total_eur"] - data["budget_used_eur"]) / data["budget_total_eur"])
    print(json.dumps({
        "workflow": args.workflow,
        "recorded_cost_eur": round(actual_cost, 4),
        "budget_used_eur": data["budget_used_eur"],
        "budget_remaining_pct": round(remaining_pct, 3),
        "rho_run": rec["rho_run"],
        "rho_cumulative": round(data["cm_cumulative_eur"] - data["budget_used_eur"], 4)
    }, indent=2))

def cmd_finalize(args, optima):
    data = _load_budget(args.workflow)
    if not data:
        print(json.dumps({"status": "ERROR", "reason": "budget-not-initialized"}))
        sys.exit(1)
    data["finalized_at"] = _now()
    data["status"] = "FINALIZED"
    rho_total = data["cm_cumulative_eur"] - data["budget_used_eur"]
    data["rho_total_eur"] = round(rho_total, 4)

    # Alert wenn rho < 0
    alert = None
    if rho_total < 0:
        alert = "rho-negative"
        hook = (optima.get("hooks") or {}).get("on_rho_negative")
        if hook:
            try:
                os.system(f"{hook} --workflow {args.workflow} --rho {rho_total}")
            except Exception:
                pass

    _save_budget(args.workflow, data)
    _append_log(AUDIT_LOG, {"ts": _now(), "op": "finalize", "workflow": args.workflow,
                            "budget_used_eur": data["budget_used_eur"],
                            "rho_total_eur": rho_total, "alert": alert})
    print(json.dumps({
        "workflow": args.workflow,
        "status": "FINALIZED",
        "budget_used_eur": data["budget_used_eur"],
        "cm_cumulative_eur": data["cm_cumulative_eur"],
        "rho_total_eur": data["rho_total_eur"],
        "n_actions": len(data["records"]),
        "alert": alert
    }, indent=2))

def cmd_report(args, optima):
    days = args.days or 7
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    records = []
    if GLOBAL_LOG.exists():
        with open(GLOBAL_LOG, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    r = json.loads(line)
                    t = datetime.fromisoformat(r.get("ts", "").replace("Z", "+00:00"))
                    if t >= cutoff:
                        if args.workflow and r.get("workflow") != args.workflow:
                            continue
                        records.append(r)
                except Exception:
                    pass
    agg_model = {}
    agg_wf = {}
    total_cost = 0.0
    total_cm = 0.0
    for r in records:
        m = r.get("model", "unknown")
        wf = r.get("workflow", "unknown")
        c = r.get("actual_cost_eur", 0)
        cm = r.get("cm_eur", 0)
        agg_model.setdefault(m, {"cost": 0, "cm": 0, "n": 0})
        agg_wf.setdefault(wf, {"cost": 0, "cm": 0, "n": 0})
        agg_model[m]["cost"] += c; agg_model[m]["cm"] += cm; agg_model[m]["n"] += 1
        agg_wf[wf]["cost"] += c; agg_wf[wf]["cm"] += cm; agg_wf[wf]["n"] += 1
        total_cost += c; total_cm += cm

    print(json.dumps({
        "days": days,
        "n_records": len(records),
        "total_cost_eur": round(total_cost, 4),
        "total_cm_eur": round(total_cm, 4),
        "total_rho_eur": round(total_cm - total_cost, 4),
        "per_model": {k: {"cost_eur": round(v["cost"], 4), "cm_eur": round(v["cm"], 4),
                          "rho_eur": round(v["cm"] - v["cost"], 4), "n": v["n"]} for k, v in agg_model.items()},
        "per_workflow": {k: {"cost_eur": round(v["cost"], 4), "cm_eur": round(v["cm"], 4),
                             "rho_eur": round(v["cm"] - v["cost"], 4), "n": v["n"]} for k, v in agg_wf.items()}
    }, indent=2, ensure_ascii=False))

def cmd_guard(args, optima):
    ceiling = (optima.get("token_budgets") or {}).get("per_action_ceiling_eur", 5.0)
    if args.estimated_cost_eur > ceiling and not args.ceiling_override:
        print(json.dumps({"status": "BLOCK", "reason": f"cost {args.estimated_cost_eur} > ceiling {ceiling}",
                          "recommendation": "abort-or-override"}))
        sys.exit(1)
    print(json.dumps({"status": "OK", "action": args.action,
                      "estimated_cost_eur": args.estimated_cost_eur,
                      "ceiling_eur": ceiling, "override": args.ceiling_override}))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--init", action="store_true")
    p.add_argument("--check", action="store_true")
    p.add_argument("--record", action="store_true")
    p.add_argument("--finalize", action="store_true")
    p.add_argument("--report", action="store_true")
    p.add_argument("--guard", action="store_true")
    p.add_argument("--workflow", default=None)
    p.add_argument("--model", default="claude-opus-4-7-1m")
    p.add_argument("--estimated-input", type=int, default=0)
    p.add_argument("--estimated-output", type=int, default=0)
    p.add_argument("--input", type=int, default=0)
    p.add_argument("--output", type=int, default=0)
    p.add_argument("--action", default="")
    p.add_argument("--task-type", default=None)
    p.add_argument("--days", type=int, default=None)
    p.add_argument("--estimated-cost-eur", type=float, default=0.0)
    p.add_argument("--ceiling-override", action="store_true")
    args = p.parse_args()

    optima = _load_optima()
    if args.init:
        if not args.workflow: sys.exit("--workflow required")
        cmd_init(args, optima)
    elif args.check:
        if not args.workflow: sys.exit("--workflow required")
        cmd_check(args, optima)
    elif args.record:
        if not args.workflow: sys.exit("--workflow required")
        cmd_record(args, optima)
    elif args.finalize:
        if not args.workflow: sys.exit("--workflow required")
        cmd_finalize(args, optima)
    elif args.report:
        cmd_report(args, optima)
    elif args.guard:
        cmd_guard(args, optima)
    else:
        p.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
