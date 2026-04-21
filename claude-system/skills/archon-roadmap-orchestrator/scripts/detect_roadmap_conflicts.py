#!/usr/bin/env python3
"""detect_roadmap_conflicts.py - Conflicts, Cycles, Parallel-Claims, SLA-Breach, Budget-Breach."""
import sys, os, json, argparse
from datetime import datetime, timezone, timedelta


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

HELPER_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HELPER_PATH)
try:
    from event_log_append import append_event, semantic_fingerprint
except ImportError:
    def append_event(*a, **kw): pass
    def semantic_fingerprint(t, d, r=""): return str(hash((t, tuple(d or []))))

HUB = os.environ.get("BRANCH_HUB", "G:/Meine Ablage/Claude-Knowledge-System/branch-hub")
ROADMAP = os.path.join(HUB, "state", "roadmap-materialized.json")
EVENT_LOG = os.path.join(HUB, "state", "event-log.jsonl")

def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        sys.stderr.write(f"WARN: {path}: {e}\n")
        return {}

def _load_events(path):
    out = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
    except Exception as e:
        sys.stderr.write(f"WARN: {path}: {e}\n")
    return out

def find_cycles(tasks):
    cycles = []
    visited = set()
    def visit(tid, stack):
        if tid in stack:
            cycles.append(stack[stack.index(tid):])
            return
        if tid in visited:
            return
        visited.add(tid)
        for d in tasks.get(tid, {}).get("depends_on", []) or []:
            visit(d, stack + [tid])
    for tid in tasks:
        if tid not in visited:
            visit(tid, [])
    return cycles

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--since-cursor", default=None)
    p.add_argument("--branch", default=None)
    args = p.parse_args()

    rm = _load_json(ROADMAP)
    events = _load_events(EVENT_LOG)
    tasks = rm.get("tasks", {})
    if args.branch:
        tasks = {k: v for k, v in tasks.items() if v.get("branch") == args.branch}

    now = datetime.now(timezone.utc)
    conflicts = []

    # Duplikate
    fp_map = {}
    for tid, t in tasks.items():
        fp = semantic_fingerprint(t.get("title", ""), t.get("depends_on", []) or [])
        if fp in fp_map:
            conflicts.append({"kind": "duplicate", "task_id": tid,
                              "details": f"fingerprint-match with {fp_map[fp]}"})
        else:
            fp_map[fp] = tid

    # Cycles
    for c in find_cycles(tasks):
        conflicts.append({"kind": "cycle", "task_id": c[0], "details": " -> ".join(c) + f" -> {c[0]}"})

    # Parallel-Claims: gleicher task_id von >1 Branch in Events
    claim_branches = {}
    for ev in events:
        if ev.get("event_type") == "task-claimed":
            tid = ev.get("task_id")
            claim_branches.setdefault(tid, set()).add(ev.get("branch"))
    for tid, bs in claim_branches.items():
        if len(bs) > 1 and tid in tasks:
            conflicts.append({"kind": "parallel-claim", "task_id": tid,
                              "details": f"claimed by: {sorted(bs)}"})

    # SLA-Breach
    last_act = {}
    for ev in events:
        tid = ev.get("task_id")
        ts = ev.get("ts") or ev.get("timestamp")
        if tid and ts:
            try:
                t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if tid not in last_act or t > last_act[tid]:
                    last_act[tid] = t
            except Exception:
                continue
    for tid, t in tasks.items():
        if t.get("status") in ("claimed", "in-progress"):
            la = last_act.get(tid)
            if la and (now - la) > timedelta(hours=8):
                conflicts.append({"kind": "sla-breach", "task_id": tid,
                                  "details": f"no-progress-since {la.isoformat()}"})

    # Budget-Breach (pro Branch Summe rho_est)
    branch_load = rm.get("branch_load", {})
    totals = {}
    for tid, t in tasks.items():
        if t.get("status") in ("claimed", "in-progress"):
            b = t.get("branch")
            if not b: continue
            try:
                rho_str = str(t.get("rho_est", "0")).replace("k", "000").split("-")[-1].strip().replace("/J", "").replace("+", "")
                rho = int("".join(c for c in rho_str if c.isdigit()) or 0)
                totals[b] = totals.get(b, 0) + rho
            except Exception:
                pass
    for b, tot in totals.items():
        cap = branch_load.get(b, {}).get("capacity_pct", 100) * 1000
        if tot > cap:
            conflicts.append({"kind": "budget-breach", "branch": b,
                              "details": f"rho_sum {tot} > cap {cap}"})

    severity = "low"
    if any(c["kind"] in ("cycle", "parallel-claim") for c in conflicts):
        severity = "high"
    elif len(conflicts) > 5:
        severity = "mid"

    for c in conflicts:
        append_event(branch="orchestrator", event_type="conflict-detected",
                     task_id=c.get("task_id", ""), payload=c)

    print(json.dumps({"conflicts": conflicts,
                      "summary": f"{len(conflicts)} conflicts detected.",
                      "severity": severity}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
