#!/usr/bin/env python3
"""
DF-06 BEACON-Monitor [CRUX-MK]
Detects Parallel-Session-Konflikte: 2+ BEACON-Eintraege binnen <5 Min = Race-Condition-Indikator.

Author: Opus 4.7 METAD2, 2026-04-18 Phronesis-P3
Target: ~5 Min cron, deterministisch, kein LLM-Call.

Logic:
1. Read BEACON.md
2. Extract last N "LETZTE AENDERUNG: <ISO>" timestamps
3. Compute deltas between consecutive
4. If any delta < 300s AND von different "VON: ..." branches: ALERT
5. Append to audit/beacon-monitor.jsonl

Exit-Codes:
  0 = OK (no conflicts)
  1 = ALERT (conflicts detected, logged but non-blocking)
"""
import re
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BEACON = Path("G:/Meine Ablage/Claude-Knowledge-System/branch-hub/BEACON.md")
AUDIT = Path("G:/Meine Ablage/Claude-Knowledge-System/branch-hub/audit/beacon-monitor.jsonl")
WINDOW_SECONDS = 300  # 5 Min
LOOKBACK = 10         # check last N entries

PATTERN = re.compile(r"LETZTE AENDERUNG:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:[+-]\d{2}:?\d{2}|Z)?)\s*\|\s*VON:\s*([^|]+?)\s*\|", re.IGNORECASE)


def parse_iso(ts: str) -> datetime | None:
    try:
        # Normalize +02:00 vs +0200
        if re.match(r".+[+-]\d{4}$", ts):
            ts = ts[:-2] + ":" + ts[-2:]
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def main():
    if not BEACON.exists():
        print(f"BEACON not found: {BEACON}")
        return 0

    content = BEACON.read_text(encoding="utf-8", errors="replace")
    matches = PATTERN.findall(content)
    if len(matches) < 2:
        return 0

    # Most recent first; collect (ts, branch)
    entries = []
    for ts_str, branch in matches[:LOOKBACK]:
        ts = parse_iso(ts_str)
        if ts:
            entries.append((ts, branch.strip()))

    conflicts = []
    for i in range(len(entries) - 1):
        ts_new, branch_new = entries[i]
        ts_old, branch_old = entries[i + 1]
        delta = (ts_new - ts_old).total_seconds()
        if 0 <= delta < WINDOW_SECONDS and branch_new != branch_old:
            conflicts.append({
                "newer": {"ts": ts_new.isoformat(), "branch": branch_new},
                "older": {"ts": ts_old.isoformat(), "branch": branch_old},
                "delta_seconds": delta,
            })

    log_entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": "beacon-monitor",
        "entries_scanned": len(entries),
        "conflicts": len(conflicts),
        "conflict_details": conflicts[:5],
    }
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    if conflicts:
        sys.stderr.write(f"[beacon-monitor] {len(conflicts)} parallel-session-conflict(s) in last {WINDOW_SECONDS}s window\n")
        for c in conflicts[:3]:
            sys.stderr.write(f"  {c['older']['branch']} -> {c['newer']['branch']} ({c['delta_seconds']:.0f}s)\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
