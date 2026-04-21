#!/usr/bin/env python3
"""write_inbox_assignments.py - appended Task-Assignments in branch-hub/inbox/to-<branch>.md"""
import sys, os, json, argparse
from datetime import datetime, timezone

HELPER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HELPER)
try:
    from event_log_append import append_event
except ImportError:
    def append_event(*a, **kw): pass

HUB = os.environ.get("BRANCH_HUB", "G:/Meine Ablage/Claude-Knowledge-System/branch-hub")
INBOX = os.path.join(HUB, "inbox")

TEMPLATE = """
---
## Assignment {task_id} [CRUX-MK]

**Task:** {task_id} - {title}
**Lease:** {lease_id}
**Assigned-Model:** {assigned_model}
**rho_est:** {rho_est}
**Depends-on:** {depends_on}
**Context:** {context_pointer}

**Instructions:**
{instructions}

**Report back:**
- `python scripts/event_log_append.py --branch {branch} --type task-progress --task-id {task_id} --payload '{{"note": "..."}}'`
- oder direkter Write in `branch-hub/findings/`

**Escalate to Martin:** bei K_0/Q_0-Beruehrung oder unklaren Dependencies
---
"""

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--assignments-json", required=True)
    args = p.parse_args()

    try:
        with open(args.assignments_json, "r", encoding="utf-8") as f:
            assignments = json.load(f)
    except Exception as e:
        sys.stderr.write(f"ERROR assignments: {e}\n")
        sys.exit(1)

    os.makedirs(INBOX, exist_ok=True)
    updated = set()
    for e in assignments:
        branch = e.get("branch", "unknown")
        tid = e.get("task_id", "N/A")
        inbox_path = os.path.join(INBOX, f"to-{branch}.md")
        md = TEMPLATE.format(
            task_id=tid,
            title=e.get("title", ""),
            lease_id=e.get("lease_id", ""),
            assigned_model=e.get("assigned_model", ""),
            rho_est=e.get("rho_est", ""),
            depends_on=e.get("depends_on", []),
            context_pointer=e.get("context_pointer", ""),
            instructions=e.get("instructions", ""),
            branch=branch
        )
        try:
            with open(inbox_path, "a", encoding="utf-8") as f:
                f.write(md)
            updated.add(inbox_path)
            append_event(branch=branch, event_type="task-claimed", task_id=tid,
                         payload={"lease_id": e.get("lease_id"),
                                  "assigned_model": e.get("assigned_model"),
                                  "assigned_at": datetime.now(timezone.utc).astimezone().isoformat()})
        except Exception as ex:
            sys.stderr.write(f"WARN inbox-write {inbox_path}: {ex}\n")

    print(json.dumps({"updated_inboxes": sorted(updated)}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
