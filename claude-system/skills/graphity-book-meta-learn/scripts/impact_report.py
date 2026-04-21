#!/usr/bin/env python3
"""
impact_report.py -- Entity-Change-Impact-Scanner [CRUX-MK]
Wave-1 CrossRef Konsens (Codex): "Nicht propagieren, sondern reindizieren + Impact-Report".

Funktionen:
- Bei Entity-Aenderung: welche Kapitel sind betroffen?
- Bei Entity-Loeschung: wo wird noch referenziert?
- Bei introduced_in-Aenderung: temporale Inkonsistenzen?
- Bei Alias-Aenderung: Rename-Impact ueber alle Buecher?

Usage:
    python impact_report.py --db <registry.sqlite> --entity <entity_id>
    python impact_report.py --db <registry.sqlite> --entity <entity_id> --change-type renamed --new-value NEW_ID
    python impact_report.py --db <registry.sqlite> --scan-orphans
    python impact_report.py --db <registry.sqlite> --scan-temporal-violations
"""

import argparse
import json
import sqlite3
import sys


def impact_entity_change(conn, entity_id, change_type="modified", new_value=None):
    """Gibt Dict mit betroffenen Buechern/Kapiteln zurueck."""
    report = {
        "entity_id": entity_id,
        "change_type": change_type,
        "new_value": new_value,
        "affected_books": [],
        "affected_chapters": [],
        "affected_edges_count": 0,
        "affected_aliases_count": 0,
        "resolver_refs_count": 0,
    }

    # Buecher mit Occurrence
    rows = conn.execute("""
        SELECT DISTINCT book_id FROM book_occurrences WHERE entity_id = ?
    """, (entity_id,)).fetchall()
    report["affected_books"] = [r[0] for r in rows]

    # Kapitel mit Edges
    edge_rows = conn.execute("""
        SELECT DISTINCT book_id, chapter_num FROM edges
        WHERE (source_entity = ? OR target_entity = ?) AND chapter_num IS NOT NULL
        ORDER BY book_id, chapter_num
    """, (entity_id, entity_id)).fetchall()
    report["affected_chapters"] = [{"book_id": r[0], "chapter_num": r[1]} for r in edge_rows]

    # Edges-Count
    edge_count = conn.execute("""
        SELECT COUNT(*) FROM edges WHERE source_entity = ? OR target_entity = ?
    """, (entity_id, entity_id)).fetchone()[0]
    report["affected_edges_count"] = edge_count

    # Aliases
    alias_count = conn.execute("""
        SELECT COUNT(*) FROM aliases WHERE entity_id = ?
    """, (entity_id,)).fetchone()[0]
    report["affected_aliases_count"] = alias_count

    # Resolver-Log refs
    try:
        resolver_count = conn.execute("""
            SELECT COUNT(*) FROM resolver_log
            WHERE placeholder LIKE '%' || ? || '%'
        """, (entity_id,)).fetchone()[0]
        report["resolver_refs_count"] = resolver_count
    except sqlite3.OperationalError:
        pass

    # Chapter-Contracts die Entity als primary_lens/secondary_lens referenzieren
    contract_rows = conn.execute("""
        SELECT book_id, chapter_num, primary_lens, secondary_lens
        FROM chapter_contracts
        WHERE primary_lens = ? OR secondary_lens = ?
    """, (entity_id, entity_id)).fetchall()
    report["affected_contracts"] = [
        {"book_id": r[0], "chapter_num": r[1], "role": "primary" if r[2] == entity_id else "secondary"}
        for r in contract_rows
    ]

    # Bei Rename: schreibe Vorschlag fuer SQL-Updates
    if change_type == "renamed" and new_value:
        report["proposed_sql"] = [
            f"UPDATE entities SET entity_id = '{new_value}' WHERE entity_id = '{entity_id}';",
            f"UPDATE book_occurrences SET entity_id = '{new_value}' WHERE entity_id = '{entity_id}';",
            f"UPDATE edges SET source_entity = '{new_value}' WHERE source_entity = '{entity_id}';",
            f"UPDATE edges SET target_entity = '{new_value}' WHERE target_entity = '{entity_id}';",
            f"UPDATE aliases SET entity_id = '{new_value}' WHERE entity_id = '{entity_id}';",
            f"UPDATE chapter_contracts SET primary_lens = '{new_value}' WHERE primary_lens = '{entity_id}';",
            f"UPDATE chapter_contracts SET secondary_lens = '{new_value}' WHERE secondary_lens = '{entity_id}';",
        ]

    # Impact-Report-Eintrag in DB
    conn.execute("""
        INSERT INTO impact_reports
            (entity_id, change_type, book_id, affected_chapters, action_taken)
        VALUES (?, ?, ?, ?, 'report_generated')
    """, (
        entity_id, change_type,
        report["affected_books"][0] if report["affected_books"] else None,
        json.dumps(report["affected_chapters"], ensure_ascii=False),
    ))
    conn.commit()

    return report


def scan_orphans(conn):
    """Entities die nie in book_occurrences oder edges auftauchen."""
    rows = conn.execute("""
        SELECT e.entity_id, e.canonical_name
        FROM entities e
        WHERE e.entity_id NOT IN (SELECT DISTINCT entity_id FROM book_occurrences)
          AND e.entity_id NOT IN (SELECT DISTINCT source_entity FROM edges)
          AND e.entity_id NOT IN (SELECT DISTINCT target_entity FROM edges)
    """).fetchall()
    return [{"entity_id": r[0], "canonical_name": r[1]} for r in rows]


def scan_temporal_violations(conn):
    """Verweise vor introduced_in."""
    rows = conn.execute("SELECT * FROM v_temporal_violations").fetchall()
    return [dict(r) for r in rows]


def scan_dominance_violations(conn):
    """Kapitel mit >2 dominanten Lenses."""
    rows = conn.execute("SELECT * FROM v_dominance_violations").fetchall()
    return [dict(r) for r in rows]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--entity")
    ap.add_argument("--change-type", default="modified",
                    choices=["modified", "renamed", "deprecated", "archived"])
    ap.add_argument("--new-value")
    ap.add_argument("--scan-orphans", action="store_true")
    ap.add_argument("--scan-temporal-violations", action="store_true")
    ap.add_argument("--scan-dominance-violations", action="store_true")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    if args.scan_orphans:
        result = {"orphaned_entities": scan_orphans(conn)}
    elif args.scan_temporal_violations:
        result = {"temporal_violations": scan_temporal_violations(conn)}
    elif args.scan_dominance_violations:
        result = {"dominance_violations": scan_dominance_violations(conn)}
    elif args.entity:
        result = impact_entity_change(conn, args.entity, args.change_type, args.new_value)
    else:
        # Combined scan
        result = {
            "orphaned_entities": scan_orphans(conn),
            "temporal_violations": scan_temporal_violations(conn),
            "dominance_violations": scan_dominance_violations(conn),
        }

    conn.close()

    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    # Exit-Code nach Severity
    total_issues = 0
    if "temporal_violations" in result:
        total_issues += len(result["temporal_violations"])
    if "dominance_violations" in result:
        total_issues += len(result["dominance_violations"])

    sys.exit(2 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
