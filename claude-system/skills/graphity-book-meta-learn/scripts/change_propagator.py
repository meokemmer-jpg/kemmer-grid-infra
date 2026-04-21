#!/usr/bin/env python3
"""
change_propagator.py -- Masterplan-Change-Propagation [CRUX-MK]
Wave-3 W10 Konsens: 5-Stufen-FSM (ChangeSet -> Invalidation -> AutoReDraft -> Manual -> AtomicPromotion).

Leitregel: "Propagation ist nicht alles neu schreiben, sondern Delta bauen + Kapitel
invalidieren + selektiv redraften + atomisch promoten."

Stufen:
  1. Semantic ChangeSet Build  -- klassifiziert additive | constraint_change | structural
  2. Chapter Invalidation      -- setze chapter_state clean|stale_review|stale_redraft|blocked
  3. Auto Re-Draft Lane (shadow)  -- nur bei stale_redraft + lokal
  4. Manual Structural Review -- Tasks statt Rewrites bei structural
  5. Atomic Promotion Gate    -- Martin approved, alle consistent

Anti-Patterns:
  - Keine direkten canon-writes
  - Kein globales Re-Draft bei jedem Bump
  - Chapter split/merge immer manuell
  - Keine interpretative Auto-Propagation

Usage:
    python change_propagator.py --stage 1 --db <sqlite> --book <slug> --masterplan-new <path>
    python change_propagator.py --stage 2 --db <sqlite> --book <slug> --revision-id <id>
    python change_propagator.py --stage 5 --db <sqlite> --book <slug> --revision-id <id> --promote
"""

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


STRUCTURAL_KEYWORDS = [
    "chapter split", "chapter merge", "chapter reorder", "chapter delete",
    "spine change", "pov change", "character removed", "character added",
    "timeline change", "setting change"
]


def stage1_changeset(conn, book_id, masterplan_new_path, based_on=None, created_by="claude"):
    """Stufe 1: Semantic ChangeSet Build."""
    masterplan_text = Path(masterplan_new_path).read_text(encoding="utf-8", errors="replace")
    text_hash = hashlib.sha256(masterplan_text.encode()).hexdigest()[:16]

    # Klassifikation (Heuristik)
    classification = "additive"
    lower = masterplan_text.lower()
    for kw in STRUCTURAL_KEYWORDS:
        if kw in lower:
            classification = "structural"
            break
    if classification == "additive":
        # Check fuer constraint_change (lens/tone/wordbudget changes)
        for kw in ["primary_lens", "secondary_lens", "word_budget", "forbidden_lens", "tone_constraint"]:
            if kw in lower:
                classification = "constraint_change"
                break

    revision_id = f"{book_id}_{text_hash}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    change_set = {
        "masterplan_hash": text_hash,
        "masterplan_path": masterplan_new_path,
        "length_chars": len(masterplan_text),
        "classification": classification,
        "structural_markers": [kw for kw in STRUCTURAL_KEYWORDS if kw in lower],
    }

    conn.execute("""
        INSERT INTO book_revisions
            (revision_id, book_id, based_on, masterplan_ref, change_set_json,
             classification, status, created_by)
        VALUES (?, ?, ?, ?, ?, ?, 'draft', ?)
    """, (revision_id, book_id, based_on, masterplan_new_path,
          json.dumps(change_set, ensure_ascii=False), classification, created_by))
    conn.commit()

    return {
        "stage": 1,
        "revision_id": revision_id,
        "classification": classification,
        "structural_markers": change_set["structural_markers"],
    }


def stage2_invalidate(conn, book_id, revision_id):
    """Stufe 2: Chapter Invalidation + Impact Scoring."""
    # Hole alle chapter_contracts fuer book
    chapters = conn.execute("""
        SELECT chapter_num, primary_lens, secondary_lens, status
        FROM chapter_contracts WHERE book_id = ?
    """, (book_id,)).fetchall()

    # Hole revision classification
    rev = conn.execute("""
        SELECT classification, change_set_json FROM book_revisions WHERE revision_id = ?
    """, (revision_id,)).fetchone()
    if not rev:
        return {"error": f"Revision {revision_id} not found"}
    classification = rev[0]

    invalidations = []
    for chap_num, primary, secondary, status in chapters:
        if classification == "structural":
            chap_state, impact = "blocked", 1.0
            reasons = ["structural_change"]
        elif classification == "constraint_change":
            chap_state, impact = "stale_redraft", 0.6
            reasons = ["constraint_change"]
        else:  # additive
            chap_state, impact = "stale_review", 0.3
            reasons = ["additive_review"]

        conn.execute("""
            INSERT INTO chapter_invalidations
                (book_id, chapter_num, revision_id, chapter_state, impact_score, reasons_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (book_id, chap_num, revision_id, chap_state, impact, json.dumps(reasons)))
        invalidations.append({
            "chapter": chap_num, "state": chap_state, "impact": impact
        })
    conn.commit()

    return {
        "stage": 2,
        "revision_id": revision_id,
        "classification": classification,
        "invalidations": invalidations,
        "summary": {
            "blocked": sum(1 for i in invalidations if i["state"] == "blocked"),
            "stale_redraft": sum(1 for i in invalidations if i["state"] == "stale_redraft"),
            "stale_review": sum(1 for i in invalidations if i["state"] == "stale_review"),
        }
    }


def stage3_auto_redraft_plan(conn, book_id, revision_id):
    """Stufe 3: Liste Kapitel die AUTO-redrafted werden duerfen (nur stale_redraft)."""
    rows = conn.execute("""
        SELECT chapter_num, impact_score FROM chapter_invalidations
        WHERE book_id = ? AND revision_id = ?
          AND chapter_state = 'stale_redraft' AND resolved_at IS NULL
        ORDER BY impact_score DESC
    """, (book_id, revision_id)).fetchall()
    return {
        "stage": 3,
        "auto_redraft_candidates": [{"chapter": r[0], "impact": r[1]} for r in rows],
        "note": "Nur auf shadow-branch generieren. Martin review vor Canon-Promotion."
    }


def stage4_manual_review_tasks(conn, book_id, revision_id):
    """Stufe 4: Task-Liste fuer strukturelle/globale Aenderungen."""
    rows = conn.execute("""
        SELECT chapter_num, reasons_json FROM chapter_invalidations
        WHERE book_id = ? AND revision_id = ?
          AND chapter_state = 'blocked' AND resolved_at IS NULL
    """, (book_id, revision_id)).fetchall()
    tasks = []
    for chap, reasons_json in rows:
        reasons = json.loads(reasons_json)
        task_type = "re-outline"
        if "chapter split" in str(reasons) or "chapter merge" in str(reasons):
            task_type = "split/merge"
        tasks.append({
            "chapter": chap,
            "task_type": task_type,
            "reasons": reasons,
            "estimated_martin_minutes": 15 if task_type == "re-outline" else 30,
        })
    return {"stage": 4, "manual_tasks": tasks}


def stage5_atomic_promotion(conn, book_id, revision_id, promote=False):
    """Stufe 5: Atomic Promotion Gate."""
    # Pruefe: alle invalidations resolved oder noop?
    unresolved = conn.execute("""
        SELECT COUNT(*) FROM chapter_invalidations
        WHERE book_id = ? AND revision_id = ? AND resolved_at IS NULL
    """, (book_id, revision_id)).fetchone()[0]

    if unresolved > 0:
        return {
            "stage": 5,
            "ready_to_promote": False,
            "unresolved_count": unresolved,
            "action": "BLOCKED: resolve all invalidations first"
        }

    if not promote:
        return {
            "stage": 5,
            "ready_to_promote": True,
            "action": "READY (use --promote to execute)"
        }

    # Execute promotion
    conn.execute("""
        UPDATE book_revisions SET status = 'active', promoted_at = ?
        WHERE revision_id = ?
    """, (datetime.now().isoformat(), revision_id))
    # Supersede previous
    conn.execute("""
        UPDATE book_revisions SET status = 'superseded'
        WHERE book_id = ? AND revision_id != ? AND status = 'active'
    """, (book_id, revision_id))
    conn.commit()

    return {
        "stage": 5,
        "ready_to_promote": True,
        "action": "PROMOTED",
        "revision_id": revision_id,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, required=True, choices=[1, 2, 3, 4, 5])
    ap.add_argument("--db", required=True)
    ap.add_argument("--book", required=True)
    ap.add_argument("--masterplan-new")
    ap.add_argument("--revision-id")
    ap.add_argument("--based-on")
    ap.add_argument("--promote", action="store_true")
    ap.add_argument("--created-by", default="claude")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)

    if args.stage == 1:
        if not args.masterplan_new:
            print("ERROR: stage 1 requires --masterplan-new", file=sys.stderr)
            sys.exit(3)
        result = stage1_changeset(conn, args.book, args.masterplan_new, args.based_on, args.created_by)
    elif args.stage == 2:
        if not args.revision_id:
            print("ERROR: stage 2 requires --revision-id", file=sys.stderr); sys.exit(3)
        result = stage2_invalidate(conn, args.book, args.revision_id)
    elif args.stage == 3:
        result = stage3_auto_redraft_plan(conn, args.book, args.revision_id)
    elif args.stage == 4:
        result = stage4_manual_review_tasks(conn, args.book, args.revision_id)
    elif args.stage == 5:
        result = stage5_atomic_promotion(conn, args.book, args.revision_id, args.promote)

    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    sys.exit(0 if "error" not in result else 2)


if __name__ == "__main__":
    main()
