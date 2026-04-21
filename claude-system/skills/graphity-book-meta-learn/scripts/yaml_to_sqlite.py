#!/usr/bin/env python3
"""
yaml_to_sqlite.py -- Graphity Registry Build-Script [CRUX-MK]
Wave-1 CrossRef-Wargame Konsens: YAML-Authoring -> SQLite-Build-Index.

Konvertiert:
    graphity-registry/entities/*.yaml -> entities table
    graphity-registry/books/<slug>/book.yaml -> books table
    graphity-registry/books/<slug>/occurrences.yaml -> book_occurrences
    graphity-registry/books/<slug>/edges.yaml -> edges
    graphity-registry/books/<slug>/aliases.yaml -> aliases
    graphity-registry/books/<slug>/chapter_contracts.yaml -> chapter_contracts

Initialisiert auch state-machine-Tables (leer) fuer DF-07.

Usage:
    python yaml_to_sqlite.py --registry <path> --db <output.sqlite>
    python yaml_to_sqlite.py --registry <path> --db <output.sqlite> --validate-only
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pip install pyyaml", file=sys.stderr)
    sys.exit(3)


SCHEMA_FILES = [
    "cross-reference-index.schema.sql",
    "state-machine-extensions.schema.sql",
    "wave3-extensions.schema.sql",
]


def init_schema(conn, schemas_dir):
    """Fuehre alle Schema-SQL-Files aus."""
    for sf in SCHEMA_FILES:
        path = Path(schemas_dir) / sf
        if not path.exists():
            print(f"WARN: Schema not found: {path}", file=sys.stderr)
            continue
        sql = path.read_text(encoding="utf-8")
        conn.executescript(sql)
        print(f"Schema loaded: {sf}", file=sys.stderr)


def load_yaml(path):
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_entities(conn, registry_root):
    """Lese entities/*.yaml und upsert in entities-Tabelle."""
    entities_dir = Path(registry_root) / "entities"
    if not entities_dir.exists():
        print(f"WARN: entities dir missing: {entities_dir}", file=sys.stderr)
        return 0

    count = 0
    for yml in entities_dir.glob("*.yaml"):
        data = load_yaml(yml)
        if not data:
            continue
        conn.execute("""
            INSERT OR REPLACE INTO entities
                (entity_id, entity_type, canonical_name, description, source_reference, source_quote, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("entity_id") or yml.stem,
            data.get("entity_type", "zutat"),
            data.get("canonical_name", yml.stem),
            data.get("description"),
            data.get("source_reference"),
            data.get("source_quote"),
            json.dumps(data.get("metadata", {}), ensure_ascii=False),
        ))
        count += 1
    return count


def load_book(conn, book_slug, book_dir):
    """Lese ein Buch-Verzeichnis und insert alle zugehoerigen Rows."""
    stats = {"books": 0, "occurrences": 0, "edges": 0, "aliases": 0, "contracts": 0}

    # book.yaml
    book_data = load_yaml(book_dir / "book.yaml")
    if not book_data:
        print(f"WARN: book.yaml missing in {book_dir}", file=sys.stderr)
        return stats

    conn.execute("""
        INSERT OR REPLACE INTO books
            (book_id, title, category_bitmask, primary_category, ebenen_profile,
             phase, status, author_count, bundle_parent, metadata_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        book_slug,
        book_data.get("title", book_slug),
        book_data.get("category_bitmask", 1),
        book_data.get("primary_category", "K1_narrativ"),
        book_data.get("ebenen_profile", "default"),
        book_data.get("phase", 1),
        book_data.get("status", "active"),
        book_data.get("author_count", 1),
        book_data.get("bundle_parent"),
        json.dumps(book_data.get("metadata", {}), ensure_ascii=False),
    ))
    stats["books"] = 1

    # occurrences.yaml
    occ_data = load_yaml(book_dir / "occurrences.yaml")
    if occ_data and "occurrences" in occ_data:
        for occ in occ_data["occurrences"]:
            conn.execute("""
                INSERT OR REPLACE INTO book_occurrences
                    (book_id, entity_id, introduced_in, last_seen, first_mention_context,
                     local_alias, prominence, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                book_slug,
                occ["entity_id"],
                occ.get("introduced_in"),
                occ.get("last_seen"),
                occ.get("first_mention_context"),
                occ.get("local_alias"),
                occ.get("prominence", 1),
                json.dumps(occ.get("metadata", {}), ensure_ascii=False),
            ))
            stats["occurrences"] += 1

    # edges.yaml
    edge_data = load_yaml(book_dir / "edges.yaml")
    if edge_data and "edges" in edge_data:
        for e in edge_data["edges"]:
            conn.execute("""
                INSERT INTO edges
                    (source_entity, target_entity, relation_type, book_id,
                     chapter_num, confidence, note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                e["source"], e["target"], e["relation"],
                book_slug,
                e.get("chapter"),
                e.get("confidence", 1.0),
                e.get("note"),
            ))
            stats["edges"] += 1

    # aliases.yaml
    alias_data = load_yaml(book_dir / "aliases.yaml")
    if alias_data and "aliases" in alias_data:
        for a in alias_data["aliases"]:
            conn.execute("""
                INSERT OR REPLACE INTO aliases (alias, entity_id, book_id, context)
                VALUES (?, ?, ?, ?)
            """, (a["alias"], a["entity_id"], book_slug, a.get("context")))
            stats["aliases"] += 1

    # chapter_contracts.yaml
    contract_data = load_yaml(book_dir / "chapter_contracts.yaml")
    if contract_data and "contracts" in contract_data:
        for c in contract_data["contracts"]:
            conn.execute("""
                INSERT OR REPLACE INTO chapter_contracts
                    (book_id, chapter_num, spine, primary_lens, secondary_lens,
                     global_invariants, forbidden_lenses, meta_frame,
                     word_budget_min, word_budget_max, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                book_slug, c["chapter_num"],
                c.get("spine"),
                c.get("primary_lens"),
                c.get("secondary_lens"),
                json.dumps(c.get("global_invariants", []), ensure_ascii=False),
                json.dumps(c.get("forbidden_lenses", []), ensure_ascii=False),
                c.get("meta_frame"),
                c.get("word_budget_min"),
                c.get("word_budget_max"),
                c.get("status", "draft"),
            ))
            stats["contracts"] += 1

    return stats


def validate_registry(registry_root):
    """Pre-build Validation: YAML-Syntax, Entity-ID-Kollisionen, etc."""
    errors = []
    entities_dir = Path(registry_root) / "entities"
    seen_ids = set()

    if entities_dir.exists():
        for yml in entities_dir.glob("*.yaml"):
            try:
                data = load_yaml(yml)
                eid = data.get("entity_id") or yml.stem
                if eid in seen_ids:
                    errors.append(f"Duplicate entity_id: {eid} in {yml}")
                seen_ids.add(eid)
            except yaml.YAMLError as e:
                errors.append(f"YAML-Error in {yml}: {e}")

    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True, help="graphity-registry root")
    ap.add_argument("--db", required=True, help="SQLite output path")
    ap.add_argument("--schemas", default="C:/Users/marti/.claude/skills/graphity-book-meta-learn/schemas")
    ap.add_argument("--validate-only", action="store_true")
    args = ap.parse_args()

    # Validate first
    errors = validate_registry(args.registry)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if args.validate_only:
        print("Registry valid.")
        sys.exit(0)

    # Build SQLite
    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    init_schema(conn, args.schemas)

    total_stats = {
        "entities": load_entities(conn, args.registry),
        "books": 0, "occurrences": 0, "edges": 0, "aliases": 0, "contracts": 0,
    }

    books_dir = Path(args.registry) / "books"
    if books_dir.exists():
        for book_subdir in books_dir.iterdir():
            if book_subdir.is_dir():
                s = load_book(conn, book_subdir.name, book_subdir)
                for k, v in s.items():
                    total_stats[k] += v

    conn.commit()
    conn.close()

    print(json.dumps(total_stats, indent=2))


if __name__ == "__main__":
    main()
