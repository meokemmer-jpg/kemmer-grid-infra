#!/usr/bin/env python3
"""
context_capsule.py -- Pro-Buch-Namespace-Isolation [CRUX-MK]
Wave-3 W11 Konsens: Vector-Namespace-Isolation verhindert Character-Leakage
zwischen parallelen Buchprojekten.

Mechanismen:
  - Whitelist-Entities pro Buch (erlaubt in Generation)
  - Negative-List (Entities anderer aktiver Buecher)
  - Terminology-Whitelist (Buch-spezifische Begriffe)
  - Style-Rules (Kaestner-Cap, Adjektiv-Fasten, forbidden lenses)
  - Collision-Detection: NER-Diff Post-Generation

Usage:
    python context_capsule.py --build --db <sqlite> --book <slug>
    python context_capsule.py --check <kapitel.md> --db <sqlite> --book <slug>
    python context_capsule.py --rebuild-all --db <sqlite>
"""

import argparse
import hashlib
import json
import re
import sqlite3
import sys
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

def build_capsule(conn, book_id):
    """Baut Context-Capsule aus existierendem Registry-State."""
    # Whitelist: alle Entities die im book_occurrences stehen
    whitelist = [r[0] for r in conn.execute("""
        SELECT entity_id FROM book_occurrences WHERE book_id = ?
    """, (book_id,)).fetchall()]

    # Aliases des Buches
    aliases = [r[0] for r in conn.execute("""
        SELECT alias FROM aliases WHERE book_id = ? OR book_id IS NULL
    """, (book_id,)).fetchall()]

    # Terminology aus chapter_contracts (primary_lens, secondary_lens als Terminologie)
    rows = conn.execute("""
        SELECT primary_lens, secondary_lens, global_invariants, forbidden_lenses
        FROM chapter_contracts WHERE book_id = ?
    """, (book_id,)).fetchall()
    lenses = set()
    forbidden = set()
    invariants = []
    for primary, secondary, gi, fl in rows:
        if primary: lenses.add(primary)
        if secondary: lenses.add(secondary)
        if fl:
            try:
                for x in json.loads(fl): forbidden.add(x)
            except: pass
        if gi:
            try:
                invariants.extend(json.loads(gi))
            except: pass

    # Negative-List: entities anderer AKTIVER Buecher, die NICHT in diesem Buch vorkommen
    other_books = [r[0] for r in conn.execute("""
        SELECT book_id FROM books WHERE book_id != ? AND status = 'active'
    """, (book_id,)).fetchall()]
    negative = set()
    for other in other_books:
        other_ents = [r[0] for r in conn.execute("""
            SELECT entity_id FROM book_occurrences WHERE book_id = ?
        """, (other,)).fetchall()]
        for e in other_ents:
            if e not in whitelist:
                negative.add((e, other))

    # Get book category for style-rules
    book_row = conn.execute("SELECT primary_category FROM books WHERE book_id = ?", (book_id,)).fetchone()
    category = book_row[0] if book_row else "K1_narrativ"
    style_rules = {
        "category": category,
        "kaestner_cap": {"K1_narrativ": 22, "K2_argumentativ": 25, "K3_didaktisch": 18,
                          "K4_operativ": 20, "K5_referenziell": 20}.get(category, 22),
        "adjektiv_cap": 1,
        "forbidden_lenses": sorted(forbidden),
        "allowed_lenses": sorted(lenses),
        "global_invariants": list(set(invariants)),
    }

    namespace_hash = hashlib.sha256(f"{book_id}|{','.join(sorted(whitelist))}".encode()).hexdigest()[:16]

    capsule = {
        "book_id": book_id,
        "namespace_hash": namespace_hash,
        "whitelist_entities": sorted(set(whitelist)),
        "aliases": sorted(set(aliases)),
        "terminology": {"lenses": sorted(lenses)},
        "style_rules": style_rules,
        "negative_list": [{"entity": e, "source_book": b} for e, b in sorted(negative)],
    }

    # Persist
    conn.execute("""
        INSERT OR REPLACE INTO context_capsules
            (book_id, namespace_hash, whitelist_entities_json, terminology_json,
             style_rules_json, negative_list_json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (book_id, namespace_hash,
          json.dumps(capsule["whitelist_entities"], ensure_ascii=False),
          json.dumps(capsule["terminology"], ensure_ascii=False),
          json.dumps(capsule["style_rules"], ensure_ascii=False),
          json.dumps(capsule["negative_list"], ensure_ascii=False)))
    conn.commit()

    return capsule


def check_chapter(conn, text, book_id, chapter_num=None):
    """Pruefe Kapitel-Text gegen Capsule. Liefert collisions."""
    row = conn.execute("""
        SELECT whitelist_entities_json, negative_list_json, style_rules_json
        FROM context_capsules WHERE book_id = ?
    """, (book_id,)).fetchone()
    if not row:
        return {"error": f"No capsule for {book_id}. Run --build first."}, "error"

    whitelist = set(json.loads(row[0]))
    negative = json.loads(row[1])
    negative_map = {n["entity"]: n["source_book"] for n in negative}
    style = json.loads(row[2])

    collisions = []

    # Check negative-list (entity-leak)
    for neg_entity, source_book in negative_map.items():
        # Simple substring/regex matching (case-insensitive, word-boundary)
        pattern = rf"\b{re.escape(neg_entity)}\b"
        if re.search(pattern, text, re.IGNORECASE):
            collisions.append({
                "type": "entity_leak",
                "token": neg_entity,
                "source_book": source_book,
                "severity": "block"
            })

    # Check forbidden-lenses: suchen ob Lens-Marker im Text auftauchen
    LENS_MARKERS = {
        "GREENE": ["48 gesetze", "macht-spiel", "greene"],
        "CIALDINI": ["reziprozitaet", "sozialer beweis", "cialdini"],
        "RAND": ["objektivismus", "ayn rand", "selbstinteresse als tugend"],
    }
    for forbidden_lens in style.get("forbidden_lenses", []):
        markers = LENS_MARKERS.get(forbidden_lens, [])
        for marker in markers:
            if marker.lower() in text.lower():
                collisions.append({
                    "type": "style_leak",
                    "token": marker,
                    "forbidden_lens": forbidden_lens,
                    "severity": "warn"
                })

    # Persist collisions
    if collisions and chapter_num:
        for c in collisions:
            conn.execute("""
                INSERT INTO collision_checks
                    (book_id, chapter_num, collision_type, offending_token,
                     source_book, severity, action)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (book_id, chapter_num, c["type"], c["token"],
                  c.get("source_book"), c["severity"], "detected"))
        conn.commit()

    severity = "ok"
    if any(c["severity"] == "block" for c in collisions): severity = "block"
    elif collisions: severity = "warn"

    return {
        "book_id": book_id,
        "chapter_num": chapter_num,
        "collisions": collisions,
        "severity": severity,
        "capsule_whitelist_size": len(whitelist),
        "negative_list_size": len(negative_map),
    }, severity


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--rebuild-all", action="store_true")
    ap.add_argument("--check")
    ap.add_argument("--db", required=True)
    ap.add_argument("--book")
    ap.add_argument("--chapter", type=int)
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)

    if args.build:
        if not args.book:
            print("ERROR: --build requires --book", file=sys.stderr); sys.exit(3)
        result = build_capsule(conn, args.book)
    elif args.rebuild_all:
        books = [r[0] for r in conn.execute("SELECT book_id FROM books WHERE status='active'").fetchall()]
        result = {"rebuilt": []}
        for b in books:
            c = build_capsule(conn, b)
            result["rebuilt"].append({"book": b, "whitelist_size": len(c["whitelist_entities"])})
    elif args.check:
        if not args.book:
            print("ERROR: --check requires --book", file=sys.stderr); sys.exit(3)
        text = Path(args.check).read_text(encoding="utf-8", errors="replace")
        result, severity = check_chapter(conn, text, args.book, args.chapter)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit({"ok": 0, "warn": 1, "block": 2, "error": 3}.get(severity, 3))
    else:
        ap.print_help(); sys.exit(3)

    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    sys.exit(0)


if __name__ == "__main__":
    main()
