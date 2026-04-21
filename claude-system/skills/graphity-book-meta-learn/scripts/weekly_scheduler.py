#!/usr/bin/env python3
"""
weekly_scheduler.py -- Review-Gated Knapsack Scheduler [CRUX-MK]
Wave-3 W11 Konsens: Martin-Review-Minuten = Engpass, nicht Generation.

Prioritaets-Funktion:
  P_i = rho_i * Fortschritt_i * Interest_i * Deadline_i
  Fortschritt_i = 0.4 + 0.6 * Reifegrad_i
  Reifegrad_i = 0.3*Masterplan + 0.3*Kapitelstruktur + 0.3*Draft-Abdeckung + 0.1*Wargame

Task-Score:
  Value_t = P_i * Readiness_t * DraftGain_t
  Score_t = Value_t / (1 + ReviewCost_t)

Constraints:
  WIP_MAX = 3 aktive Buecher
  R_week = hartes Review-Budget-Limit
  Dead-Man-Switch: 60 Tage ohne progress -> PAUSED
  Context-Capsule: Pro Buch Namespace-Isolation

Usage:
    python weekly_scheduler.py --plan --db <sqlite> --week 2026-04-21 --review-budget 180
    python weekly_scheduler.py --metrics-update --db <sqlite> --book <slug> [--rho 400000] [--interest 1.2]
    python weekly_scheduler.py --report --db <sqlite>
"""

import argparse
import json
import sqlite3
import sys
import uuid
from datetime import datetime, timedelta



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

WIP_MAX = 3
DEAD_MAN_DAYS = 60


def book_priority(conn, book_id):
    """P_i Berechnung + Dead-Man-Check."""
    row = conn.execute("""
        SELECT rho_eur_year, masterplan_progress, chapter_map_progress,
               draft_coverage, wargame_progress, martin_interest,
               deadline_iso, last_progress_at, status
        FROM book_metrics WHERE book_id = ?
    """, (book_id,)).fetchone()
    if not row:
        return 0.0, "no_metrics"

    (rho, mp, cmp, dc, wg, interest, deadline, last_prog, status) = row

    if status == "hibernated":
        return 0.0, "hibernated"

    # Dead-Man-Check
    if last_prog:
        last = datetime.fromisoformat(last_prog.split("T")[0] if "T" in last_prog else last_prog)
        days = (datetime.now() - last).days
        if days > DEAD_MAN_DAYS:
            conn.execute("UPDATE book_metrics SET status='paused' WHERE book_id=?", (book_id,))
            conn.commit()
            return 0.0, f"paused_dead_man_{days}d"

    reife = (0.3 * (mp or 0) + 0.3 * (cmp or 0) +
             0.3 * (dc or 0) + 0.1 * (wg or 0))
    fortschritt = 0.4 + 0.6 * reife

    # Deadline-Faktor
    deadline_factor = 1.0
    if deadline:
        try:
            d = datetime.fromisoformat(deadline.split("T")[0] if "T" in deadline else deadline)
            days_to = max(1, (d - datetime.now()).days)
            deadline_factor = 1.0 + (90.0 / days_to)  # naehe -> hoeher
        except Exception:
            pass

    # rho normalisiert (durch Portfolio-Median -- hier approx gegen 100k)
    rho_norm = (rho or 0) / 100000.0

    P = rho_norm * fortschritt * (interest or 1.0) * deadline_factor
    return P, f"active (reife={reife:.2f}, deadline_x={deadline_factor:.2f})"


def ready_chapters(conn, book_id):
    """Liste Kapitel die bereit zum Schreiben sind (contract existiert, status=draft)."""
    rows = conn.execute("""
        SELECT chapter_num, spine, primary_lens, word_budget_max, status
        FROM chapter_contracts
        WHERE book_id = ? AND status IN ('draft', 'ready')
        ORDER BY chapter_num
    """, (book_id,)).fetchall()
    tasks = []
    for chap, spine, primary, wb_max, status in rows:
        # Readiness-Heuristik: spine + primary_lens vorhanden
        readiness = 1.0 if (spine and primary) else 0.5
        # DraftGain: Umfang (word_budget) als Proxy
        draft_gain = min((wb_max or 3000) / 3000.0, 2.0)
        # ReviewCost: geschaetzt 10 min pro 1000 Worte
        review_minutes = max(5, (wb_max or 3000) // 500)
        tasks.append({
            "chapter": chap,
            "readiness": readiness,
            "draft_gain": draft_gain,
            "review_minutes": review_minutes,
            "spine": spine[:60] if spine else "",
            "primary_lens": primary,
        })
    return tasks


def plan_week(conn, week_start, r_week_budget):
    """Greedy-Knapsack mit WIP_MAX + Review-Budget."""
    books = conn.execute("""
        SELECT book_id FROM books WHERE status = 'active'
    """).fetchall()

    candidates = []
    for (book_id,) in books:
        P, reason = book_priority(conn, book_id)
        if P == 0:
            continue
        for task in ready_chapters(conn, book_id):
            value = P * task["readiness"] * task["draft_gain"]
            score = value / (1 + task["review_minutes"])
            candidates.append({
                "book": book_id, "chapter": task["chapter"],
                "score": score, "value": value,
                "review_minutes": task["review_minutes"],
                "primary_lens": task["primary_lens"],
                "spine": task["spine"],
            })

    candidates.sort(key=lambda x: x["score"], reverse=True)

    plan = []
    active_books = set()
    review_used = 0
    skipped = []

    for task in candidates:
        skip_reason = None
        if task["book"] not in active_books and len(active_books) >= WIP_MAX:
            skip_reason = "wip_max"
        elif review_used + task["review_minutes"] > r_week_budget:
            skip_reason = "budget"

        if skip_reason:
            skipped.append({**task, "skipped_reason": skip_reason})
            continue

        plan.append(task)
        active_books.add(task["book"])
        review_used += task["review_minutes"]

    run_id = f"week_{week_start}_{uuid.uuid4().hex[:8]}"
    conn.execute("""
        INSERT INTO scheduler_runs
            (run_id, week_start, r_week_budget_minutes, wip_max,
             selected_tasks_json, total_review_minutes, skipped_tasks_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (run_id, week_start, r_week_budget, WIP_MAX,
          json.dumps(plan), review_used, json.dumps(skipped[:20])))
    conn.commit()

    return {
        "run_id": run_id,
        "week_start": week_start,
        "r_week_budget": r_week_budget,
        "plan": plan,
        "total_review_minutes": review_used,
        "active_books": list(active_books),
        "candidates_total": len(candidates),
        "skipped_count": len(skipped),
    }


def update_metrics(conn, book_id, **kwargs):
    """Update book_metrics (upsert)."""
    existing = conn.execute("SELECT book_id FROM book_metrics WHERE book_id=?", (book_id,)).fetchone()
    if not existing:
        conn.execute("INSERT INTO book_metrics (book_id, last_progress_at) VALUES (?, ?)",
                     (book_id, datetime.now().isoformat()))

    for k, v in kwargs.items():
        if v is None:
            continue
        col = {"rho": "rho_eur_year", "mp": "masterplan_progress",
               "cmp": "chapter_map_progress", "dc": "draft_coverage",
               "wg": "wargame_progress", "interest": "martin_interest",
               "deadline": "deadline_iso"}.get(k, k)
        conn.execute(f"UPDATE book_metrics SET {col}=?, computed_at=? WHERE book_id=?",
                     (v, datetime.now().isoformat(), book_id))
    conn.execute("UPDATE book_metrics SET last_progress_at=? WHERE book_id=?",
                 (datetime.now().isoformat(), book_id))
    conn.commit()
    return {"book_id": book_id, "updated": list(kwargs.keys())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--metrics-update", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--db", required=True)
    ap.add_argument("--week", default=datetime.now().strftime("%Y-%m-%d"))
    ap.add_argument("--review-budget", type=int, default=180, help="Martin-Review-Minuten pro Woche")
    ap.add_argument("--book")
    ap.add_argument("--rho", type=float)
    ap.add_argument("--mp", type=float)
    ap.add_argument("--cmp", type=float, dest="cmp")
    ap.add_argument("--dc", type=float)
    ap.add_argument("--wg", type=float)
    ap.add_argument("--interest", type=float)
    ap.add_argument("--deadline")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)

    if args.plan:
        result = plan_week(conn, args.week, args.review_budget)
    elif args.metrics_update:
        if not args.book:
            print("ERROR: --metrics-update requires --book", file=sys.stderr); sys.exit(3)
        result = update_metrics(conn, args.book, rho=args.rho, mp=args.mp,
                                 cmp=args.cmp, dc=args.dc, wg=args.wg,
                                 interest=args.interest, deadline=args.deadline)
    elif args.report:
        rows = conn.execute("SELECT * FROM v_book_priority LIMIT 10").fetchall()
        cols = [d[0] for d in conn.execute("SELECT * FROM v_book_priority LIMIT 0").description]
        result = [dict(zip(cols, r)) for r in rows]
    else:
        ap.print_help(); sys.exit(3)

    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    sys.exit(0)


if __name__ == "__main__":
    main()
