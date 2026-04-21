#!/usr/bin/env python3
"""
context_injector.py -- E12 State-Aware RAG Context-Injector [CRUX-MK]
Gemini-Empfehlung Wave-1 (kritischer als Fact-Checker).

Zweck:
- Fuer neuen Abschnitt den relevanten Context aus Buch-State extrahieren
- Previous Chapters + Figuren-Zustaende + Etablierte Fakten injizieren
- Token-Budget-begrenzt (default 4000 Token pro Injektion)

Pipeline:
1. Lies Buch-State aus SQLite (book_occurrences, edges, chapter_contracts)
2. Lies vorherige Kapitel-Drafts (Markdown-Archiv)
3. Relevance-Score pro Context-Fragment
4. Top-N Fragmente zusammensetzen bis Budget erreicht
5. Output: JSON mit context_bundle fuer LLM-Prompt

Usage:
    python context_injector.py --book <book_id> --target-chapter <N> --budget-tokens 4000
    python context_injector.py --book souveraene-maschine --target-chapter 15 --json

Dependencies:
    pip install sqlite3 (built-in), pyyaml
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

try:
    import yaml
except ImportError:
    print("ERROR: pip install pyyaml", file=sys.stderr)
    sys.exit(3)


# ==========================================================================
# CONFIG
# ==========================================================================

DB_PATH = Path("G:/Meine Ablage/Claude-Knowledge-System/dark-factory/DF-07-graphity-book-writer/registry.sqlite")
BOOKS_ROOT = Path("G:/Meine Ablage/Claude-Knowledge-System/graphity-books")
DEFAULT_BUDGET_TOKENS = 4000
WORDS_PER_TOKEN = 0.75   # rough approximation


# ==========================================================================
# CONTEXT-ELEMENT-TYPES (Gemini + Codex-Synthese)
# ==========================================================================

CONTEXT_ELEMENTS = [
    "book_summary",              # 1 Satz Buch-These (immer, small budget)
    "chapter_contract",          # Contract des Target-Kapitels (immer)
    "figures_active",            # Aktive Figuren + psychol. Zustand (C1/C3)
    "theses_established",        # Etablierte Argumente (C2/C4)
    "facts_introduced",          # Gesichert etablierte Fakten
    "previous_chapter_summary",  # Kurz-Summary Kapitel N-1
    "cross_references",          # Relevante CRX aus anderen Kapiteln
    "forbidden_lenses",          # Anti-Drift-Guard-Hinweis
    "style_invariants",          # Kaestner-Ton + Voice-Signatures
]


# ==========================================================================
# DB-QUERIES
# ==========================================================================

def db_connect():
    if not DB_PATH.exists():
        return None
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def get_book_meta(conn, book_id):
    row = conn.execute("SELECT * FROM books WHERE book_id = ?", (book_id,)).fetchone()
    return dict(row) if row else None


def get_active_figures(conn, book_id, chapter_num):
    """Figuren, die bis zu diesem Kapitel eingefuehrt wurden und Prominence >= 2"""
    rows = conn.execute("""
        SELECT e.entity_id, e.canonical_name, e.description, bo.introduced_in, bo.last_seen, bo.prominence
        FROM entities e
        JOIN book_occurrences bo ON e.entity_id = bo.entity_id
        WHERE bo.book_id = ?
          AND e.entity_type = 'figur'
          AND (bo.introduced_in IS NULL OR bo.introduced_in <= ?)
          AND (bo.last_seen IS NULL OR bo.last_seen >= ?)
        ORDER BY bo.prominence DESC, e.canonical_name
    """, (book_id, chapter_num, chapter_num)).fetchall()
    return [dict(r) for r in rows]


def get_theses_established(conn, book_id, chapter_num):
    rows = conn.execute("""
        SELECT e.entity_id, e.canonical_name, e.description, bo.introduced_in
        FROM entities e
        JOIN book_occurrences bo ON e.entity_id = bo.entity_id
        WHERE bo.book_id = ?
          AND e.entity_type IN ('these', 'zutat')
          AND bo.introduced_in IS NOT NULL
          AND bo.introduced_in < ?
        ORDER BY bo.introduced_in DESC
        LIMIT 20
    """, (book_id, chapter_num)).fetchall()
    return [dict(r) for r in rows]


def get_chapter_contract(conn, book_id, chapter_num):
    row = conn.execute("""
        SELECT * FROM chapter_contracts
        WHERE book_id = ? AND chapter_num = ?
    """, (book_id, chapter_num)).fetchone()
    return dict(row) if row else None


def get_cross_references(conn, book_id, chapter_num, limit=10):
    rows = conn.execute("""
        SELECT ed.source_entity, ed.target_entity, ed.relation_type, ed.chapter_num, ed.note
        FROM edges ed
        WHERE ed.book_id = ?
          AND ed.chapter_num IS NOT NULL
          AND ed.chapter_num < ?
        ORDER BY ed.chapter_num DESC, ed.edge_id DESC
        LIMIT ?
    """, (book_id, chapter_num, limit)).fetchall()
    return [dict(r) for r in rows]


# ==========================================================================
# PREVIOUS-CHAPTER-READ (fallback wenn DB leer)
# ==========================================================================

def read_previous_chapter_summary(book_id, chapter_num, max_words=300):
    """Liest vorheriges Kapitel-Markdown-File, extrahiert erste N Worte der Summary."""
    prev_num = chapter_num - 1
    if prev_num < 1:
        return None

    # Mehrere moegliche Pfade
    candidates = [
        BOOKS_ROOT / book_id / f"kapitel_{prev_num:02d}.md",
        BOOKS_ROOT / book_id / f"chapter-{prev_num:02d}.md",
        BOOKS_ROOT / book_id / "kapitel" / f"{prev_num:02d}.md",
    ]
    for path in candidates:
        if path.exists():
            text = path.read_text(encoding="utf-8")
            # Strip frontmatter
            text = re.sub(r"^---\n[\s\S]*?\n---\n", "", text, count=1)
            # Get first max_words words
            words = text.split()[:max_words]
            return " ".join(words)

    return None


# ==========================================================================
# RELEVANCE-SCORING (simple heuristic)
# ==========================================================================

def score_element(element_type, data, target_chapter_contract=None):
    """Gibt Relevance-Score 0-1. Simple: contract-match > prominence > recency."""
    if not data:
        return 0.0

    base_score = 0.5

    # Contract-Match-Bonus
    if target_chapter_contract:
        primary = (target_chapter_contract.get("primary_lens") or "").upper()
        secondary = (target_chapter_contract.get("secondary_lens") or "").upper()
        if primary and isinstance(data, dict):
            if data.get("entity_id", "").upper() == primary:
                base_score += 0.4
            elif data.get("entity_id", "").upper() == secondary:
                base_score += 0.2

    # Prominence-Bonus
    if isinstance(data, dict) and "prominence" in data:
        base_score += 0.1 * (data.get("prominence", 1) - 1)

    return min(1.0, base_score)


# ==========================================================================
# CONTEXT-BUNDLE-BUILDER
# ==========================================================================

def build_context_bundle(book_id, target_chapter, budget_tokens=DEFAULT_BUDGET_TOKENS):
    """Baut Context-Bundle unter Budget-Constraint."""
    bundle = {
        "book_id": book_id,
        "target_chapter": target_chapter,
        "budget_tokens": budget_tokens,
        "elements": {},
        "total_tokens_estimate": 0,
    }

    conn = db_connect()
    if not conn:
        bundle["error"] = f"DB not found at {DB_PATH}"
        # Fallback: nur File-based
        prev_summary = read_previous_chapter_summary(book_id, target_chapter)
        if prev_summary:
            words = len(prev_summary.split())
            bundle["elements"]["previous_chapter_summary"] = {
                "content": prev_summary,
                "tokens_estimate": int(words / WORDS_PER_TOKEN),
            }
            bundle["total_tokens_estimate"] += int(words / WORDS_PER_TOKEN)
        return bundle

    # Element 1: Book-Meta (small, always)
    book = get_book_meta(conn, book_id)
    if book:
        book_summary = f"{book['title']} ({book['primary_category']}, Phase {book['phase']})"
        bundle["elements"]["book_summary"] = {"content": book_summary, "tokens_estimate": 50}
        bundle["total_tokens_estimate"] += 50

    # Element 2: Chapter Contract (small, always)
    contract = get_chapter_contract(conn, book_id, target_chapter)
    if contract:
        contract_str = yaml.dump({
            "spine": contract.get("spine"),
            "primary_lens": contract.get("primary_lens"),
            "secondary_lens": contract.get("secondary_lens"),
            "forbidden_lenses": contract.get("forbidden_lenses"),
        }, allow_unicode=True)
        tokens_est = int(len(contract_str.split()) / WORDS_PER_TOKEN)
        bundle["elements"]["chapter_contract"] = {"content": contract_str, "tokens_estimate": tokens_est}
        bundle["total_tokens_estimate"] += tokens_est

    # Element 3: Active Figures (scored, budget-limited)
    remaining = budget_tokens - bundle["total_tokens_estimate"]
    if remaining > 500:
        figures = get_active_figures(conn, book_id, target_chapter)
        figures_content = []
        figures_tokens = 0
        for f in figures[:5]:   # top 5 prominence-sorted
            f_str = f"- {f['canonical_name']}: {f.get('description', '')[:200]}"
            f_tokens = int(len(f_str.split()) / WORDS_PER_TOKEN)
            if figures_tokens + f_tokens > remaining * 0.4:
                break
            figures_content.append(f_str)
            figures_tokens += f_tokens
        if figures_content:
            bundle["elements"]["figures_active"] = {
                "content": "\n".join(figures_content),
                "tokens_estimate": figures_tokens,
            }
            bundle["total_tokens_estimate"] += figures_tokens

    # Element 4: Theses Established (budget-limited)
    remaining = budget_tokens - bundle["total_tokens_estimate"]
    if remaining > 500:
        theses = get_theses_established(conn, book_id, target_chapter)
        theses_content = []
        theses_tokens = 0
        for t in theses[:10]:
            t_str = f"- {t['canonical_name']}: {t.get('description', '')[:150]}"
            t_tokens = int(len(t_str.split()) / WORDS_PER_TOKEN)
            if theses_tokens + t_tokens > remaining * 0.3:
                break
            theses_content.append(t_str)
            theses_tokens += t_tokens
        if theses_content:
            bundle["elements"]["theses_established"] = {
                "content": "\n".join(theses_content),
                "tokens_estimate": theses_tokens,
            }
            bundle["total_tokens_estimate"] += theses_tokens

    # Element 5: Previous Chapter Summary (budget-limited)
    remaining = budget_tokens - bundle["total_tokens_estimate"]
    if remaining > 300:
        prev_summary = read_previous_chapter_summary(book_id, target_chapter, max_words=int(remaining * 0.4))
        if prev_summary:
            tokens_est = int(len(prev_summary.split()) / WORDS_PER_TOKEN)
            bundle["elements"]["previous_chapter_summary"] = {
                "content": prev_summary,
                "tokens_estimate": tokens_est,
            }
            bundle["total_tokens_estimate"] += tokens_est

    # Element 6: Cross-References (rest of budget)
    remaining = budget_tokens - bundle["total_tokens_estimate"]
    if remaining > 200:
        refs = get_cross_references(conn, book_id, target_chapter)
        refs_content = []
        refs_tokens = 0
        for r in refs[:5]:
            r_str = f"- {r['source_entity']} -> {r['target_entity']} ({r['relation_type']}, Kap {r['chapter_num']})"
            r_tokens = int(len(r_str.split()) / WORDS_PER_TOKEN)
            if refs_tokens + r_tokens > remaining:
                break
            refs_content.append(r_str)
            refs_tokens += r_tokens
        if refs_content:
            bundle["elements"]["cross_references"] = {
                "content": "\n".join(refs_content),
                "tokens_estimate": refs_tokens,
            }
            bundle["total_tokens_estimate"] += refs_tokens

    conn.close()
    return bundle


def render_bundle_as_prompt(bundle):
    """Rendert Context-Bundle als LLM-Prompt-Section."""
    lines = ["# Context-Injection (State-Aware RAG)\n"]
    for element_type, data in bundle["elements"].items():
        lines.append(f"## {element_type}")
        lines.append(data["content"])
        lines.append("")
    lines.append(f"(Context-Token-Estimate: {bundle['total_tokens_estimate']} / Budget: {bundle['budget_tokens']})")
    return "\n".join(lines)


# ==========================================================================
# MAIN
# ==========================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True, help="book_id")
    ap.add_argument("--target-chapter", type=int, required=True)
    ap.add_argument("--budget-tokens", type=int, default=DEFAULT_BUDGET_TOKENS)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    bundle = build_context_bundle(args.book, args.target_chapter, args.budget_tokens)

    if args.json:
        print(json.dumps(bundle, indent=2, ensure_ascii=False, default=str))
    else:
        print(render_bundle_as_prompt(bundle))

    return 0


if __name__ == "__main__":
    sys.exit(main())
