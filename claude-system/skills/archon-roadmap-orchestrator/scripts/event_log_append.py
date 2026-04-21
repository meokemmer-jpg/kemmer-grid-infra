#!/usr/bin/env python3
"""
event_log_append.py - Append-only Event-Writer fuer Orchestrator v2

Usage:
  python event_log_append.py --branch METADD --type task-created --task-id O1 \
      --payload '{"title": "..."}' [--parent evt-xxx]

Persists: branch-hub/state/event-log.jsonl
"""
import argparse, hashlib, json, os, sys
from datetime import datetime, timezone


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
LOG_PATH = os.path.join(HUB, "state", "event-log.jsonl")

VALID_TYPES = {
    "task-created", "task-claimed", "task-progress", "task-completed",
    "task-blocked", "task-failed", "lease-renewed", "lease-expired",
    "conflict-detected", "dedup-candidate", "budget-breach",
    "sla-breach", "priority-changed", "reconciliation", "martin-override"
}

def semantic_fingerprint(title: str, deps: list, repo_path: str = "") -> str:
    """Simple fingerprint: normalized title + sorted deps + path."""
    normalized = " ".join(title.lower().split())
    deps_str = ",".join(sorted(deps or []))
    raw = f"{normalized}|{deps_str}|{repo_path}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def next_event_id() -> str:
    """Atomic next-id via line-count of event-log."""
    if not os.path.exists(LOG_PATH):
        return "evt-000000000001"
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        n = sum(1 for _ in f)
    return f"evt-{n+1:012d}"

def append_event(branch: str, event_type: str, task_id: str, payload: dict,
                 parent_event_id: str = None, fingerprint: str = None) -> str:
    assert event_type in VALID_TYPES, f"Invalid type: {event_type}"
    event = {
        "event_id": next_event_id(),
        "ts": datetime.now(timezone.utc).astimezone().isoformat(),
        "branch": branch,
        "event_type": event_type,
        "task_id": task_id,
        "payload": payload
    }
    if parent_event_id:
        event["parent_event_id"] = parent_event_id
    if fingerprint:
        event["semantic_fingerprint"] = fingerprint
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event["event_id"]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--branch", required=True)
    p.add_argument("--type", required=True, choices=sorted(VALID_TYPES))
    p.add_argument("--task-id", default="")
    p.add_argument("--payload", default="{}", help="JSON string")
    p.add_argument("--parent", default=None)
    p.add_argument("--title", default=None, help="If set, generate fingerprint")
    p.add_argument("--deps", default="", help="Comma-separated depends_on")
    args = p.parse_args()
    payload = json.loads(args.payload)
    fp = semantic_fingerprint(args.title, args.deps.split(",") if args.deps else []) if args.title else None
    eid = append_event(args.branch, args.type, args.task_id, payload, args.parent, fp)
    print(eid)

if __name__ == "__main__":
    main()
