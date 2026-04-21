#!/usr/bin/env python3
"""
resolve_crx.py -- CRX-Placeholder-Resolver [CRUX-MK]
Wave-1 CrossRef Konsens (Codex+Gemini): Hard-Block bei Build-Fail, Soft-Warn bei heuristischen Vorschlaegen.

Placeholder-Format:
    {{CRX:ENTITY_ID}}                       - Nur Entity
    {{CRX:ENTITY_ID:FIGUR_ID}}              - Entity im Kontext einer Figur
    {{CRX:ENTITY_ID:FIGUR_ID:KAP-NN}}       - Vollständig qualifiziert

Usage:
    python resolve_crx.py --input <kapitel.md> --db <registry.sqlite> --book <slug>
    python resolve_crx.py --input <kapitel.md> --db ... --book ... --mode draft    # soft-warn
    python resolve_crx.py --input <kapitel.md> --db ... --book ... --mode release  # hard-block

Exit-Codes:
    0 = Alle Placeholders resolved
    1 = WARN (Soft-Warn in Draft-Mode)
    2 = BLOCK (unresolved refs in Release-Mode)
"""

import argparse
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

PLACEHOLDER_PATTERN = re.compile(
    r"\{\{CRX:([A-Z0-9_-]+)(?::([A-Z0-9_-]+))?(?::(KAP-\d+|\d+))?\}\}"
)


def resolve_single(conn, entity_id, figur_id=None, kapitel=None, book_id=None):
    """Gibt (resolved_text, severity, reason) zurueck."""
    # 1. Entity existiert?
    row = conn.execute(
        "SELECT entity_id, canonical_name, description FROM entities WHERE entity_id = ?",
        (entity_id,)
    ).fetchone()

    if not row:
        # Try alias-lookup
        alias_row = conn.execute(
            "SELECT entity_id FROM aliases WHERE alias = ? AND (book_id = ? OR book_id IS NULL) LIMIT 1",
            (entity_id, book_id)
        ).fetchone()
        if not alias_row:
            return None, "block", f"Unknown entity: {entity_id}"
        entity_id = alias_row[0]
        row = conn.execute(
            "SELECT entity_id, canonical_name, description FROM entities WHERE entity_id = ?",
            (entity_id,)
        ).fetchone()

    # 2. Figur-Scope-Check (wenn figur_id gegeben)
    if figur_id:
        figur_exists = conn.execute(
            "SELECT 1 FROM entities WHERE entity_id = ? AND entity_type = 'figur'",
            (figur_id,)
        ).fetchone()
        if not figur_exists:
            return None, "block", f"Unknown figur: {figur_id}"

        # Figur aktiv im Buch?
        if book_id:
            active = conn.execute(
                "SELECT 1 FROM book_occurrences WHERE book_id = ? AND entity_id = ?",
                (book_id, figur_id)
            ).fetchone()
            if not active:
                return None, "warn", f"Figur {figur_id} not active in book {book_id}"

    # 3. Kapitel-Scope-Check (wenn kapitel gegeben)
    if kapitel and book_id:
        kap_num = int(kapitel.replace("KAP-", "")) if kapitel.startswith("KAP-") else int(kapitel)

        # Temporal-Check: Verweis vor introduced_in?
        temporal = conn.execute("""
            SELECT introduced_in FROM book_occurrences
            WHERE book_id = ? AND entity_id = ? AND introduced_in IS NOT NULL
        """, (book_id, entity_id)).fetchone()

        if temporal and temporal[0] > kap_num:
            return None, "block", f"Temporal violation: {entity_id} introduced in Kap {temporal[0]}, referenced in Kap {kap_num}"

    # 4. Resolve: canonical_name zurueck
    return row[1], "ok", "resolved"


def resolve_text(conn, text, book_id=None, mode="draft"):
    """Resolved alle Placeholders im Text. Gibt (output, report) zurueck."""
    report = {
        "total": 0,
        "ok": 0,
        "warn": 0,
        "block": 0,
        "unresolved": [],
    }

    resolver_log_entries = []

    def replace_fn(match):
        report["total"] += 1
        placeholder = match.group(0)
        entity_id = match.group(1)
        figur_id = match.group(2)
        kapitel = match.group(3)

        resolved, severity, reason = resolve_single(
            conn, entity_id, figur_id, kapitel, book_id
        )

        resolver_log_entries.append({
            "placeholder": placeholder,
            "entity_id": entity_id,
            "figur_id": figur_id,
            "kapitel": kapitel,
            "severity": severity,
            "reason": reason,
            "resolved_to": resolved,
        })

        if severity == "ok":
            report["ok"] += 1
            return resolved
        elif severity == "warn":
            report["warn"] += 1
            report["unresolved"].append({"placeholder": placeholder, "reason": reason})
            if mode == "release":
                return f"[UNRESOLVED:{entity_id}]"
            return f"{resolved or placeholder} [WARN]"
        else:  # block
            report["block"] += 1
            report["unresolved"].append({"placeholder": placeholder, "reason": reason})
            return f"[BLOCK:{entity_id}:{reason}]"

    output = PLACEHOLDER_PATTERN.sub(replace_fn, text)

    # Log to SQLite
    for entry in resolver_log_entries:
        conn.execute("""
            INSERT INTO resolver_log
                (book_id, chapter_num, placeholder, resolved_to, severity, reason)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            book_id,
            int(entry["kapitel"].replace("KAP-", "")) if entry["kapitel"] and entry["kapitel"].startswith("KAP-") else None,
            entry["placeholder"],
            entry["resolved_to"],
            entry["severity"],
            entry["reason"],
        ))
    conn.commit()

    return output, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--book", help="book_id (optional, fuer Scope-Checks)")
    ap.add_argument("--mode", choices=["draft", "release"], default="draft")
    ap.add_argument("--output", help="Output-File (default: stdout)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"ERROR: {path}", file=sys.stderr)
        sys.exit(3)

    text = path.read_text(encoding="utf-8")

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    output, report = resolve_text(conn, text, args.book, args.mode)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        if not args.json:
            print(output)

    conn.close()

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False), file=sys.stderr)

    print(f"[resolve_crx] {report['ok']}/{report['total']} OK, {report['warn']} WARN, {report['block']} BLOCK", file=sys.stderr)

    if args.mode == "release" and (report["block"] > 0 or report["warn"] > 0):
        sys.exit(2)
    if report["block"] > 0:
        sys.exit(2)
    if report["warn"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
