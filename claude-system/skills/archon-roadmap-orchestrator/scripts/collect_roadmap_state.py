#!/usr/bin/env python3
"""
collect_roadmap_state.py - Reactively baut roadmap-materialized.json aus event-log.jsonl

Usage:
  python collect_roadmap_state.py [--rebuild-from-scratch]

Persists: branch-hub/state/roadmap-materialized.json
Reads:    branch-hub/state/event-log.jsonl
          branch-hub/REGISTRY.md (fuer Branch-Info)
          branch-hub/META-ROADMAP.md (fuer Canonical Task-Liste)
"""
import argparse, json, os, re
from datetime import datetime, timezone

HUB = os.environ.get("BRANCH_HUB", "G:/Meine Ablage/Claude-Knowledge-System/branch-hub")
LOG_PATH = os.path.join(HUB, "state", "event-log.jsonl")
MATERIALIZED_PATH = os.path.join(HUB, "state", "roadmap-materialized.json")
REGISTRY_PATH = os.path.join(HUB, "REGISTRY.md")
ROADMAP_PATH = os.path.join(HUB, "META-ROADMAP.md")

def read_events(cursor: str = None) -> list:
    """Reads events, optionally only after cursor."""
    if not os.path.exists(LOG_PATH):
        return []
    events = []
    started = cursor is None
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if started:
                events.append(ev)
            elif ev.get("event_id") == cursor:
                started = True
    return events

def apply_event(state: dict, ev: dict) -> dict:
    """Event-Sourcing: reduce event onto state."""
    et = ev.get("event_type")
    tid = ev.get("task_id")
    ts = ev.get("ts")
    branch = ev.get("branch")
    payload = ev.get("payload", {})
    tasks = state.setdefault("tasks", {})
    leases = state.setdefault("active_leases", [])
    conflicts = state.setdefault("conflicts", [])

    if et == "task-created":
        tasks[tid] = {"status": "open", "branch": branch, "created_at": ts, **payload}
    elif et == "task-claimed":
        if tid in tasks:
            tasks[tid]["status"] = "claimed"
            tasks[tid]["branch"] = payload.get("claimed_by", branch)
            tasks[tid]["claimed_at"] = ts
    elif et == "task-progress":
        if tid in tasks:
            tasks[tid]["status"] = "in-progress"
            tasks[tid]["last_progress_at"] = ts
    elif et == "task-completed":
        if tid in tasks:
            tasks[tid]["status"] = "done"
            tasks[tid]["completed_at"] = ts
        # Remove matching leases
        state["active_leases"] = [l for l in leases if l.get("task_id") != tid]
    elif et == "task-blocked":
        if tid in tasks:
            tasks[tid]["status"] = "blocked"
            tasks[tid]["blocked_reason"] = payload.get("reason", "")
    elif et == "task-failed":
        if tid in tasks:
            tasks[tid]["status"] = "failed"
            tasks[tid]["fail_reason"] = payload.get("reason", "")
    elif et == "lease-renewed":
        for l in leases:
            if l.get("lease_id") == payload.get("lease_id"):
                l["last_heartbeat_at"] = ts
                l["expires_at"] = payload.get("new_expires_at")
                l["renewal_count"] = l.get("renewal_count", 0) + 1
    elif et == "lease-expired":
        state["active_leases"] = [l for l in leases if l.get("lease_id") != payload.get("lease_id")]
        if tid in tasks:
            tasks[tid]["status"] = "open"  # re-open for re-assignment
    elif et == "conflict-detected":
        conflicts.append({"ts": ts, "task_ids": payload.get("task_ids", []), "kind": payload.get("kind", "")})
    elif et == "reconciliation":
        state["last_reconciliation"] = ts
    elif et == "martin-override":
        if tid in tasks:
            tasks[tid].update(payload.get("overrides", {}))
            tasks[tid]["martin_override_at"] = ts

    state["event_log_cursor"] = ev.get("event_id")
    return state

def rebuild(from_scratch: bool = False) -> dict:
    if from_scratch or not os.path.exists(MATERIALIZED_PATH):
        state = {
            "schema_version": "1.0",
            "last_rebuild": datetime.now(timezone.utc).astimezone().isoformat(),
            "event_log_cursor": None,
            "tasks": {},
            "conflicts": [],
            "active_leases": [],
            "branch_load": {}
        }
        events = read_events(cursor=None)
    else:
        with open(MATERIALIZED_PATH, "r", encoding="utf-8") as f:
            state = json.load(f)
        events = read_events(cursor=state.get("event_log_cursor"))

    for ev in events:
        state = apply_event(state, ev)

    state["last_rebuild"] = datetime.now(timezone.utc).astimezone().isoformat()
    return state

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rebuild-from-scratch", action="store_true")
    p.add_argument("--print", action="store_true")
    args = p.parse_args()
    state = rebuild(args.rebuild_from_scratch)
    os.makedirs(os.path.dirname(MATERIALIZED_PATH), exist_ok=True)
    with open(MATERIALIZED_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    if args.print:
        print(json.dumps(state, indent=2, ensure_ascii=False))
    else:
        n_tasks = len(state.get("tasks", {}))
        n_active = sum(1 for t in state.get("tasks", {}).values() if t.get("status") in ("claimed", "in-progress"))
        n_leases = len(state.get("active_leases", []))
        print(f"State rebuilt: {n_tasks} tasks ({n_active} active), {n_leases} leases, cursor={state.get('event_log_cursor')}")

if __name__ == "__main__":
    main()
