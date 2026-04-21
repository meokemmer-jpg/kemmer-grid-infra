#!/usr/bin/env python3
"""
parse_claude_conversations.py -- Stream-Parser fuer Claude.ai Chat-Export
[CRUX-MK] Vorarbeit MYZ00036 (2026-04-19)

Parst 231 MB conversations.json via ijson-Streaming (kein in-memory load).
Output: 1 Markdown-Datei pro Conversation mit Frontmatter.

Usage:
    python parse_claude_conversations.py \\
        --input "G:/Meine Ablage/Claude-Vault/resources/ai-chats/claude/conversations.json" \\
        --output "G:/Meine Ablage/Claude-Knowledge-System/nlm-library/claude-chat-archive/by-project" \\
        --projects "G:/Meine Ablage/Claude-Vault/resources/ai-chats/claude/projects.json" \\
        [--dry-run]

Abhaengigkeiten:
    pip install ijson pyyaml

rho-Bilanz:
    CM: ~30-60k EUR/J (alle zukuenftigen MYZ-Tasks profitieren)
    Effort: 5-8h Python + Debug
    Break-Even: Session 3-4 nach Completion
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
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
    import ijson
    import yaml
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}. Install via: pip install ijson pyyaml", file=sys.stderr)
    sys.exit(1)


# ========================================
# CATEGORY CLASSIFIER (B401 C1-C7)
# ========================================

CATEGORY_PATTERNS = {
    "C1-roman": [
        r"(?i)souveraene\s+maschine|elena|rolf|miriam|kalkuel|arche|kon(?:v|f)ergenz",
        r"(?i)fiction|novel|roman\s+kapitel|plot|figur",
    ],
    "C2-sachbuch": [
        r"(?i)symbiotic\s+minds|ai\s+leadership|superior\s+leadership",
        r"(?i)these|argument|case\s+stud",
    ],
    "C3-interaktiv": [
        r"(?i)mathematik\s+der\s+macht|mathebuch|anton|conny|dana|bernd",
        r"(?i)interaktiv|didaktisch|lernziel",
    ],
    "C4-verlags-doc": [
        r"(?i)graphity|pmo\s+playbook|familienboard|arithmetik",
        r"(?i)board.?praesentation|governance",
    ],
    "C5-co-autor": [
        r"(?i)turning\s+the\s+tide|leaders\s+and\s+ai|bertram|schramm|gieske",
        r"(?i)bim|co.?autor",
    ],
    "C6-tech-manual": [
        r"(?i)hotelbau|manual|checkliste|spec.?ref",
    ],
    "C7-meta": [
        r"(?i)930\s+buecher|destillat|isomorphie|rezeption",
    ],
}

PRIVATE_PATTERNS = [
    r"(?i)familie|gerdi|thomas|sebastian|cape\s+coral|wegzug",
    r"(?i)kpm|portfolio|steuer|etf|blackrock",
    r"(?i)aerztlich|medizin|gesundheit|cortisol|blutpanel",
]

BOOK_PROMPT_PATTERNS = [
    (r"(?i)schreibe?\s+(?:einen?\s+)?masterplan", "masterplan"),
    (r"(?i)erstelle?\s+(?:ein|eine)?\s+playbook", "playbook"),
    (r"(?i)produktionsbibel", "produktionsbibel"),
    (r"(?i)kochrezept", "kochrezept"),
    (r"(?i)11\s+ebenen|elf\s+ebenen", "11-ebenen"),
    (r"(?i)character\s+psychogramm|figur\s+psychogramm", "psychogramm"),
    (r"(?i)kapitel\s+\d+\s+schreiben", "kapitel-schreiben"),
    (r"(?i)wargame\s+kapitel|wargame\s+buch", "wargame"),
    (r"(?i)cross.?reference|cross.?ref\s+index", "cross-ref"),
    (r"(?i)kaestner.?ton|kaestner.?stil", "kaestner"),
    (r"(?i)zutaten.?matrix", "zutaten-matrix"),
    (r"(?i)schattenkind|sonnenkind", "stahl-psychologie"),
    (r"(?i)voss|taktische\s+empathie|labeling", "voss-empathie"),
    (r"(?i)cialdini|pre.?suasion|commitment", "cialdini-influence"),
]


def classify_conversation(title, messages_sample):
    """Gibt (category, is_private, matched_patterns) zurueck."""
    text = (title or "") + " " + messages_sample[:5000]

    matched_book_prompts = []
    for pattern, label in BOOK_PROMPT_PATTERNS:
        if re.search(pattern, text):
            matched_book_prompts.append(label)

    is_private = any(re.search(p, text) for p in PRIVATE_PATTERNS)

    # Category-Scoring
    scores = {cat: 0 for cat in CATEGORY_PATTERNS}
    for cat, patterns in CATEGORY_PATTERNS.items():
        for p in patterns:
            scores[cat] += len(re.findall(p, text))

    top_cat = max(scores, key=scores.get) if max(scores.values()) > 0 else "unclassified"

    return top_cat, is_private, matched_book_prompts


def sanitize_filename(s):
    s = re.sub(r"[^\w\-. ]", "_", s)[:80].strip()
    return s or "untitled"


def parse_projects(projects_path):
    """Liest projects.json ein fuer UUID->Name-Mapping."""
    try:
        with open(projects_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {p.get("uuid"): p.get("name", "no-name") for p in data if isinstance(p, dict)}
    except Exception as e:
        print(f"WARN: Could not parse projects.json: {e}", file=sys.stderr)
        return {}


def process_conversation(conv, output_dir, project_map, dry_run=False):
    """Processiert EINE Conversation, schreibt MD-Datei."""
    uuid = conv.get("uuid", "no-uuid")
    title = conv.get("name", "Untitled")
    created = conv.get("created_at", "")
    updated = conv.get("updated_at", "")
    project_uuid = conv.get("project_uuid")
    project_name = project_map.get(project_uuid, None)

    messages = conv.get("chat_messages", []) or []
    msg_count = len(messages)

    # Sample fuer Classifier (erste 3 Messages)
    messages_sample = ""
    for msg in messages[:3]:
        content = msg.get("content", [])
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "text":
                    messages_sample += c.get("text", "") + "\n"
        elif isinstance(content, str):
            messages_sample += content + "\n"

    category, is_private, book_prompts = classify_conversation(title, messages_sample)

    # Ziel-Pfad
    sub_dir = "private" if is_private else category
    date_folder = (created[:7] if created else "unknown").replace(":", "-")
    filename = f"{sanitize_filename(title)}-{uuid[:8]}.md"
    target_path = Path(output_dir) / sub_dir / date_folder / filename

    if dry_run:
        return {
            "uuid": uuid,
            "category": category,
            "is_private": is_private,
            "book_prompts": book_prompts,
            "target": str(target_path),
            "skipped": True,
        }

    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Frontmatter
    frontmatter = {
        "type": "claude-chat-conversation",
        "uuid": uuid,
        "title": title,
        "created": created,
        "last_message": updated,
        "project_uuid": project_uuid,
        "project_name": project_name,
        "message_count": msg_count,
        "category": category,
        "dsgvo_private": is_private,
        "book_prompts_matched": book_prompts,
        "source": "conversations.json 2026-04-08",
        "crux_mk": True,
    }

    # Markdown-Body
    body_lines = ["---"]
    body_lines.append(yaml.dump(frontmatter, allow_unicode=True, sort_keys=False).strip())
    body_lines.append("---\n")
    body_lines.append(f"# {title}\n")

    for i, msg in enumerate(messages, 1):
        sender = msg.get("sender", "unknown")
        msg_created = msg.get("created_at", "")
        body_lines.append(f"\n## Msg-{i:03d} [{sender}] {msg_created}\n")

        content = msg.get("content", [])
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "text":
                    body_lines.append(c.get("text", ""))
        elif isinstance(content, str):
            body_lines.append(content)

    body_lines.append("\n\n[CRUX-MK]\n")

    with open(target_path, "w", encoding="utf-8") as f:
        f.write("\n".join(body_lines))

    return {
        "uuid": uuid,
        "category": category,
        "is_private": is_private,
        "book_prompts": book_prompts,
        "target": str(target_path),
        "msg_count": msg_count,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Pfad zu conversations.json")
    ap.add_argument("--output", required=True, help="Pfad zu nlm-library/claude-chat-archive")
    ap.add_argument("--projects", default=None, help="Pfad zu projects.json")
    ap.add_argument("--dry-run", action="store_true", help="Nur classifizieren, nicht schreiben")
    ap.add_argument("--limit", type=int, default=0, help="Max Conversations (0 = alle)")
    args = ap.parse_args()

    project_map = parse_projects(args.projects) if args.projects else {}
    print(f"Project-Map: {len(project_map)} Projekte", file=sys.stderr)

    stats = {
        "total": 0,
        "by_category": {},
        "private_count": 0,
        "book_prompt_matches": {},
    }

    index_entries = []

    with open(args.input, "rb") as f:
        # ijson-Streaming: items am Root (conversations.json ist ein Top-Level-Array)
        for conv in ijson.items(f, "item"):
            stats["total"] += 1
            result = process_conversation(conv, args.output, project_map, dry_run=args.dry_run)

            cat = result["category"]
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
            if result["is_private"]:
                stats["private_count"] += 1
            for bp in result["book_prompts"]:
                stats["book_prompt_matches"][bp] = stats["book_prompt_matches"].get(bp, 0) + 1

            index_entries.append(result)

            if stats["total"] % 20 == 0:
                print(f"Processed {stats['total']} conversations...", file=sys.stderr)

            if args.limit and stats["total"] >= args.limit:
                break

    # INDEX.md schreiben
    if not args.dry_run:
        index_path = Path(args.output) / "INDEX.md"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("# Claude Chat Archive INDEX [CRUX-MK]\n\n")
            f.write(f"Generated: {datetime.utcnow().isoformat()}Z\n\n")
            f.write(f"**Total:** {stats['total']} Conversations\n\n")
            f.write("## By Category\n\n")
            for cat, count in sorted(stats["by_category"].items()):
                f.write(f"- {cat}: {count}\n")
            f.write(f"\n## Private (DSGVO)\n\n")
            f.write(f"- Private-geflaggt: {stats['private_count']}\n")
            f.write("\n## Book-Prompt-Matches (B401)\n\n")
            for bp, count in sorted(stats["book_prompt_matches"].items(), key=lambda x: -x[1]):
                f.write(f"- {bp}: {count}\n")
            f.write("\n## Conversations (sortable)\n\n")
            f.write("| UUID | Category | Private | Msgs | Book-Prompts | Target |\n")
            f.write("|------|----------|---------|------|--------------|--------|\n")
            for e in index_entries:
                bps = ",".join(e.get("book_prompts", []))
                priv = "YES" if e["is_private"] else ""
                f.write(f"| {e['uuid'][:8]} | {e['category']} | {priv} | {e.get('msg_count',0)} | {bps} | {e['target']} |\n")
        print(f"INDEX written: {index_path}", file=sys.stderr)

    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
