#!/usr/bin/env python3
"""
template_engine.py -- T1/T2/T3 Skeleton-Generator [CRUX-MK]
Extrahiert Kategorie-Templates aus MYZ00006/MYZ00008/MYZ00009/MYZ00010/MYZ00011-Findings
und generiert Skeleton-Output fuer Buch-Produktion.

Nutzt Registry (SQLite) + Leitfossil-Findings (Markdown) als Input.
Ist KEIN LLM-Generator; baut Skeleton-YAML mit {{TODO}}-Placeholders
die spaeter durch LLM-Call oder Martin gefuellt werden.

Usage:
    python template_engine.py --category K1_narrativ --template T1 --book souveraene-maschine --db <sqlite>
    python template_engine.py --category K2_argumentativ --template T2 --thesis "L=Decision×Implementation" --db <sqlite>
    python template_engine.py --category K3_didaktisch --template T3 --pilot "Zeitwertverfassung" --db <sqlite>
    python template_engine.py --list-templates --db <sqlite>
"""

import argparse
import io
import json
import re
import sqlite3
import sys
from pathlib import Path

# BIAS-036 Pattern: Force UTF-8 stdout on Windows fuer Unicode-Chars (→, ×, ...)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

FINDINGS_DIR = Path("G:/Meine Ablage/Claude-Knowledge-System/branch-hub/findings")

CATEGORY_FINDING_MAP = {
    "K1_narrativ":     ["MYZ00006-Templates-Cat-1-Roman.md"],
    "K2_argumentativ": ["MYZ00008-Templates-Cat-2-Business-Sachbuch.md"],
    "K3_didaktisch":   ["MYZ00009-Templates-Cat-3-Didaktisch.md"],
    "K4_operativ":     ["MYZ00010-Templates-Cat-4-Operativ.md"],
    "K5_referenziell": ["MYZ00011-Templates-Cat-5-Referenziell.md"],
}

TEMPLATE_DESCRIPTIONS = {
    "K1_narrativ": {
        "T1": "Zutaten-Matrix (34 Einfluesse, Autor-Werke)",
        "T2": "Character-Psychogramm (18 Schichten pro Figur)",
        "T3": "Figuren-Kapitel-Bogen (22 Kap x 11 Ebenen)",
    },
    "K2_argumentativ": {
        "T1": "Quellen-Matrix (Kahneman/Moltke/Shannon/Taleb/...)",
        "T2": "These-Psychogramm (8 Schichten: Axiom-Kern → Skin-in-the-Game)",
        "T3": "Argumentations-Bogen (22 Kap mit Thesen-Gewicht + Gegenthesen)",
    },
    "K3_didaktisch": {
        "T1": "Lernziel-Zutaten-Matrix (12 Lernziele, Bloom + VARK)",
        "T2": "Character-Lernziel-Map (4 Kern: Anton/Conny/Dana/Bernd, 10 Schichten)",
        "T3": "Interaktions-Pfad-Bogen (16 Kap, ~6.5h Lernzeit)",
    },
    "K4_operativ": {
        "T1": "KPI-Matrix",
        "T2": "Governance-Layer (Authority/RACI)",
        "T3": "Entscheidungs-Fluss",
    },
    "K5_referenziell": {
        "T1": "Quellen-Attribution-Matrix",
        "T2": "Destillat-Schema (5 Kern-Konzepte)",
        "T3": "Isomorphie-Map",
    },
}


def find_book_context(conn, book_id):
    """Lade Book-Meta + Entities + Chapter-Contracts aus SQLite."""
    book = conn.execute(
        "SELECT title, primary_category, ebenen_profile, phase, status FROM books WHERE book_id = ?",
        (book_id,)
    ).fetchone()
    if not book:
        return None

    entities = [dict(zip(["entity_id", "entity_type", "canonical_name"],
                         row)) for row in conn.execute("""
        SELECT e.entity_id, e.entity_type, e.canonical_name
        FROM entities e
        JOIN book_occurrences bo ON e.entity_id = bo.entity_id
        WHERE bo.book_id = ? ORDER BY bo.prominence DESC
    """, (book_id,)).fetchall()]

    chapters = [dict(zip(["chapter_num", "spine", "primary_lens", "secondary_lens", "status"],
                         row)) for row in conn.execute("""
        SELECT chapter_num, spine, primary_lens, secondary_lens, status
        FROM chapter_contracts WHERE book_id = ? ORDER BY chapter_num
    """, (book_id,)).fetchall()]

    return {
        "book_id": book_id,
        "title": book[0], "category": book[1],
        "ebenen": book[2], "phase": book[3], "status": book[4],
        "entities": entities,
        "chapters": chapters,
    }


def extract_template_block(finding_path, template_id):
    """Extrahiert den T1/T2/T3 YAML-Block aus einem Findings-MD."""
    if not finding_path.exists():
        return None, f"Finding not found: {finding_path}"

    text = finding_path.read_text(encoding="utf-8", errors="replace")

    # Regex: finde Section "# TEMPLATE T1" oder "## T1" bis zum naechsten Template-Header
    patterns = [
        rf"#+\s*TEMPLATE\s+{template_id}\s+[-—]\s+[^\n]+\n(.*?)(?=\n#+\s*TEMPLATE\s+T\d|\Z)",
        rf"#+\s*{template_id}\s+K[1-5][-_]\w+.*?\n(.*?)(?=\n#+\s*T[123]\s+K[1-5]|\n#+\s*[A-Z]{{3,}}|\Z)",
        rf"#+\s*{template_id}\s*[:\-]\s+[^\n]+\n(.*?)(?=\n#+\s*T[123]|\Z)",
    ]

    for p in patterns:
        m = re.search(p, text, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip(), None

    return None, f"Template {template_id} not found in {finding_path.name}"


def generate_skeleton(category, template_id, book_context, thesis=None, pilot=None):
    """Generiert Skeleton-YAML mit {{TODO}}-Placeholders."""
    findings = CATEGORY_FINDING_MAP.get(category, [])
    if not findings:
        return {"error": f"Unknown category: {category}"}

    finding_path = FINDINGS_DIR / findings[0]
    template_block, err = extract_template_block(finding_path, template_id)

    header = {
        "generated_at": None,
        "category": category,
        "template_id": template_id,
        "template_type": TEMPLATE_DESCRIPTIONS.get(category, {}).get(template_id, "unknown"),
        "source_finding": str(finding_path.name),
        "book_context": book_context if book_context else "[no book context provided]",
        "thesis": thesis,
        "pilot_theme": pilot,
    }

    if err:
        return {
            **header,
            "status": "SKELETON_FALLBACK",
            "fallback_instruction": f"Manuelle Befuellung noetig. {err}",
            "template_block_structure": TEMPLATE_DESCRIPTIONS.get(category, {}).get(template_id),
        }

    # Extract key fields (heuristisch: alle YAML-Keys die auftauchen)
    field_pattern = re.compile(r"^\s*(\w+):\s*", re.MULTILINE)
    fields = sorted(set(field_pattern.findall(template_block)))[:30]

    return {
        **header,
        "status": "SKELETON_FROM_LEITFOSSIL",
        "suggested_fields": fields,
        "leitfossil_reference": f"Copy structure from {finding_path.name} section {template_id}",
        "next_step": "Fill TODO-placeholders via LLM-call or Martin-Phronesis",
        "template_block_preview_chars": len(template_block),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list-templates", action="store_true")
    ap.add_argument("--category", choices=list(CATEGORY_FINDING_MAP.keys()))
    ap.add_argument("--template", choices=["T1", "T2", "T3"])
    ap.add_argument("--book", help="book_id fuer SQLite-Context")
    ap.add_argument("--thesis", help="Fuer K2 These-Psychogramm")
    ap.add_argument("--pilot", help="Fuer K3 Pilot-Lernziel-Thema")
    ap.add_argument("--db", required=True)
    ap.add_argument("--generate-llm-prompt", action="store_true",
                    help="Gibt LLM-Prompt fuer Skeleton-Fuellung aus (nicht LLM-Call selbst)")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)

    if args.list_templates:
        result = {
            cat: TEMPLATE_DESCRIPTIONS.get(cat, {})
            for cat in CATEGORY_FINDING_MAP
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0)

    if not (args.category and args.template):
        print("ERROR: --category + --template required", file=sys.stderr)
        ap.print_help()
        sys.exit(3)

    book_context = find_book_context(conn, args.book) if args.book else None
    result = generate_skeleton(args.category, args.template, book_context,
                                thesis=args.thesis, pilot=args.pilot)

    if args.generate_llm_prompt and "error" not in result:
        # Generiere Codex/Gemini-fertigen Prompt zum Befuellen des Skeleton
        findings_path = FINDINGS_DIR / CATEGORY_FINDING_MAP[args.category][0]
        llm_prompt = f"""Generiere einen vollstaendig gefuellten {args.template}-Block fuer Graphity-Buch Kategorie {args.category}.

VORLAGE/Struktur: Leitfossil `{findings_path.name}` Section {args.template}
Zweck: {result.get('template_type', 'unknown')}
Book-Context: {json.dumps(book_context, indent=2, ensure_ascii=False, default=str) if book_context else '[no book]'}
{f"Thesis: {args.thesis}" if args.thesis else ""}
{f"Pilot-Theme: {args.pilot}" if args.pilot else ""}
Suggested-Fields: {result.get('suggested_fields', [])}

AUFTRAG: YAML-Block analog zur Leitfossil-Vorlage. Keine Motivationsrhetorik. Kaestner-Ton.
Ausgabe: nur das YAML, keine Meta-Kommentare."""
        result["llm_prompt_for_codex_or_gemini"] = llm_prompt
        result["next_step_cli"] = (
            f"echo '<llm_prompt>' | codex exec --skip-git-repo-check -- "
            f"or: echo '<llm_prompt>' | gemini -p 'YAML-only output'"
        )

    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    sys.exit(0 if "error" not in result else 2)


if __name__ == "__main__":
    main()
