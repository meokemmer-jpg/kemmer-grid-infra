#!/usr/bin/env python3
"""
ttl_lease_manager.py - Lease-Lifecycle mit Heartbeats + Auto-Expiry

Usage:
  python ttl_lease_manager.py --issue --task-id O1b --branch METADD --duration-min 240
  python ttl_lease_manager.py --renew --lease-id lease-xxx
  python ttl_lease_manager.py --release --lease-id lease-xxx
  python ttl_lease_manager.py --sweep   # expire all expired leases

Persists: branch-hub/state/leases.json (current active) + writes event to event-log
"""
import argparse, hashlib, json, os, sys
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

HUB = os.environ.get("BRANCH_HUB", "G:/Meine Ablage/Claude-Knowledge-System/branch-hub")
LEASES_PATH = os.path.join(HUB, "state", "leases.json")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from event_log_append import append_event

def load_leases():
    if not os.path.exists(LEASES_PATH):
        return {"leases": []}
    with open(LEASES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_leases(data):
    os.makedirs(os.path.dirname(LEASES_PATH), exist_ok=True)
    with open(LEASES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def now():
    return datetime.now(timezone.utc).astimezone()

def issue(task_id: str, branch: str, duration_min: int, model: str = "") -> dict:
    data = load_leases()
    lid = "lease-" + hashlib.sha256(f"{task_id}|{branch}|{now().isoformat()}".encode()).hexdigest()[:12]
    lease = {
        "lease_id": lid,
        "task_id": task_id,
        "branch": branch,
        "assigned_model": model,
        "issued_at": now().isoformat(),
        "expires_at": (now() + timedelta(minutes=duration_min)).isoformat(),
        "heartbeat_interval_min": 15,
        "last_heartbeat_at": now().isoformat(),
        "status": "active",
        "renewal_count": 0,
        "max_renewals": 4
    }
    data.setdefault("leases", []).append(lease)
    save_leases(data)
    append_event(branch, "task-claimed", task_id,
                 {"lease_id": lid, "expires_at": lease["expires_at"], "assigned_model": model})
    return lease

def renew(lease_id: str, extend_min: int = 240) -> dict:
    data = load_leases()
    for l in data.get("leases", []):
        if l["lease_id"] == lease_id and l["status"] == "active":
            if l["renewal_count"] >= l["max_renewals"]:
                return {"error": "max-renewals-exceeded", "lease_id": lease_id}
            l["renewal_count"] += 1
            l["last_heartbeat_at"] = now().isoformat()
            l["expires_at"] = (now() + timedelta(minutes=extend_min)).isoformat()
            save_leases(data)
            append_event(l["branch"], "lease-renewed", l["task_id"],
                         {"lease_id": lease_id, "new_expires_at": l["expires_at"],
                          "renewal_count": l["renewal_count"]})
            return l
    return {"error": "lease-not-found", "lease_id": lease_id}

def release(lease_id: str) -> dict:
    data = load_leases()
    for l in data.get("leases", []):
        if l["lease_id"] == lease_id:
            l["status"] = "released"
            save_leases(data)
            append_event(l["branch"], "task-completed", l["task_id"],
                         {"lease_id": lease_id, "released_by_branch": True})
            return l
    return {"error": "lease-not-found"}

def sweep() -> list:
    data = load_leases()
    current = now()
    expired = []
    for l in data.get("leases", []):
        if l["status"] != "active":
            continue
        exp = datetime.fromisoformat(l["expires_at"])
        if exp < current:
            l["status"] = "expired"
            expired.append(l)
            append_event(l["branch"], "lease-expired", l["task_id"],
                         {"lease_id": l["lease_id"], "expired_at": current.isoformat()})
    if expired:
        save_leases(data)
    return expired

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="action", required=True)
    i = sub.add_parser("issue"); i.add_argument("--task-id", required=True); i.add_argument("--branch", required=True); i.add_argument("--duration-min", type=int, default=240); i.add_argument("--model", default="")
    r = sub.add_parser("renew"); r.add_argument("--lease-id", required=True); r.add_argument("--extend-min", type=int, default=240)
    rel = sub.add_parser("release"); rel.add_argument("--lease-id", required=True)
    sub.add_parser("sweep")
    args = p.parse_args()
    if args.action == "issue":
        print(json.dumps(issue(args.task_id, args.branch, args.duration_min, args.model), indent=2))
    elif args.action == "renew":
        print(json.dumps(renew(args.lease_id, args.extend_min), indent=2))
    elif args.action == "release":
        print(json.dumps(release(args.lease_id), indent=2))
    elif args.action == "sweep":
        expired = sweep()
        print(json.dumps({"expired_count": len(expired), "expired_ids": [l["lease_id"] for l in expired]}, indent=2))

if __name__ == "__main__":
    main()
