#!/usr/bin/env python3
"""
kaestner_guardian.py -- Stil-Invariante Pre-Write-Validator [CRUX-MK]
Vorarbeit MYZ00025-E3 (2026-04-19)

Prueft einen Kapitel-Abschnitt gegen Kaestner-Ton-Regeln:
- Satz-Laenge max 20 Woerter (writing-style.md)
- Keine Filler-Phrasen
- Keine Motivations-Rhetorik
- Keine Emojis
- Ton-Matrix-Konsistenz (optional, pro Figur)

Exit-Codes:
    0 = OK
    1 = WARN (Drift detected, aber nicht Bloecken)
    2 = BLOCK (harte Verletzung, muss korrigiert werden)
    3 = ERROR (Input-Fehler)

Usage:
    python kaestner_guardian.py --check <abschnitt.md>
    python kaestner_guardian.py --check <abschnitt.md> --block-on-warn
    python kaestner_guardian.py --check <abschnitt.md> --report-json
"""

import argparse
import json
import re
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

# ========================================
# KAESTNER-REGELN (aus writing-style.md + CLAUDE.md §1)
# ========================================

MAX_WORDS_PER_SENTENCE = 20

FILLER_PHRASES = [
    r"(?i)\b(?:es\s+ist\s+wichtig\s+zu\s+erwaehnen|wie\s+bereits\s+erwaehnt)\b",
    r"(?i)\b(?:in\s+der\s+tat|in\s+gewissem\s+sinne|letztendlich)\b",
    r"(?i)\b(?:einfach\s+ausgedrueckt|mit\s+anderen\s+worten)\b",
    r"(?i)\b(?:am\s+ende\s+des\s+tages|all\s+things\s+considered)\b",
    r"(?i)\b(?:nichtsdestotrotz|gleichermassen|gleichwohl)\b",
]

MOTIVATION_RHETORIC = [
    r"(?i)\b(?:spannend(?:e|es|er)?|faszinierend(?:e|es|er)?|begeisternd)\b",
    r"(?i)\b(?:wir\s+(?:alle|gemeinsam)\s+(?:koennen|werden|schaffen))\b",
    r"(?i)\b(?:lass(?:t)?\s+uns\s+gemeinsam)\b",
    r"(?i)\b(?:deine\s+reise|dein\s+weg\s+zu)\b",
    r"(?i)\b(?:unglaublich(?:e|es|er)?|erstaunlich(?:e|es|er)?)\b",
]

EMOJI_PATTERN = re.compile(
    r"[\U0001F300-\U0001F9FF"
    r"\U0001F600-\U0001F64F"
    r"\U0001F680-\U0001F6FF"
    r"\U0001F000-\U0001F0FF"
    r"\U0001F100-\U0001F1FF"
    r"\U00002600-\U000027BF"
    r"\U0001FA70-\U0001FAFF"
    r"]", re.UNICODE)

# Saetze aufsplitten (grob, nicht linguistisch korrekt aber pragmatisch)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")


def count_words(sentence):
    return len(sentence.strip().split())


def check_text(text, strict_sentence_cap=True):
    """Gibt dict mit violations zurueck."""
    violations = {
        "long_sentences": [],  # (sentence, word_count)
        "filler_phrases": [],  # (phrase, context)
        "motivation_rhetoric": [],  # (phrase, context)
        "emojis": [],  # (emoji, context)
    }

    # Strip code-blocks first (technische Referenzen pro Zeile OK)
    text_clean = re.sub(r"```[\s\S]*?```", "", text)
    text_clean = re.sub(r"`[^`]+`", "", text_clean)

    # Satz-Laengen-Check
    sentences = SENTENCE_SPLIT.split(text_clean)
    for s in sentences:
        s = s.strip()
        if not s or s.startswith("#") or s.startswith("|") or s.startswith("-"):
            continue  # Skip Headers, Tabellen, Listen
        wc = count_words(s)
        if wc > MAX_WORDS_PER_SENTENCE and strict_sentence_cap:
            violations["long_sentences"].append({"sentence": s[:100] + "...", "word_count": wc})

    # Filler-Phrases
    for pattern in FILLER_PHRASES:
        for m in re.finditer(pattern, text_clean):
            start = max(0, m.start() - 30)
            end = min(len(text_clean), m.end() + 30)
            violations["filler_phrases"].append({
                "phrase": m.group(),
                "context": text_clean[start:end].replace("\n", " "),
            })

    # Motivation-Rhetoric
    for pattern in MOTIVATION_RHETORIC:
        for m in re.finditer(pattern, text_clean):
            start = max(0, m.start() - 30)
            end = min(len(text_clean), m.end() + 30)
            violations["motivation_rhetoric"].append({
                "phrase": m.group(),
                "context": text_clean[start:end].replace("\n", " "),
            })

    # Emojis
    for m in EMOJI_PATTERN.finditer(text_clean):
        start = max(0, m.start() - 20)
        end = min(len(text_clean), m.end() + 20)
        violations["emojis"].append({
            "emoji": m.group(),
            "context": text_clean[start:end].replace("\n", " "),
        })

    return violations


def classify_severity(violations):
    """Gibt 'OK' / 'WARN' / 'BLOCK' zurueck."""
    emoji_count = len(violations["emojis"])
    filler_count = len(violations["filler_phrases"])
    motivation_count = len(violations["motivation_rhetoric"])
    long_sent_count = len(violations["long_sentences"])

    if emoji_count > 0 or motivation_count >= 3:
        return "BLOCK"
    if filler_count >= 5 or long_sent_count >= 5:
        return "BLOCK"
    if motivation_count >= 1 or filler_count >= 2 or long_sent_count >= 2:
        return "WARN"
    return "OK"


def format_report(violations, severity, file_path):
    lines = []
    lines.append(f"# Kaestner-Guardian Report [{severity}]")
    lines.append(f"File: {file_path}\n")

    for key, items in violations.items():
        if items:
            lines.append(f"## {key} ({len(items)})")
            for it in items[:10]:
                lines.append(f"- {json.dumps(it, ensure_ascii=False)}")
            if len(items) > 10:
                lines.append(f"- ... (+{len(items)-10} more)")
            lines.append("")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", required=True, help="Pfad zu Markdown-Abschnitt")
    ap.add_argument("--block-on-warn", action="store_true")
    ap.add_argument("--report-json", action="store_true")
    ap.add_argument("--no-sentence-cap", action="store_true", help="Satz-Laenge nicht pruefen")
    args = ap.parse_args()

    path = Path(args.check)
    if not path.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(3)

    text = path.read_text(encoding="utf-8")

    # Frontmatter-Block entfernen (YAML zwischen --- ---)
    text = re.sub(r"^---\n[\s\S]*?\n---\n", "", text, count=1)

    violations = check_text(text, strict_sentence_cap=not args.no_sentence_cap)
    severity = classify_severity(violations)

    if args.report_json:
        print(json.dumps({
            "file": str(path),
            "severity": severity,
            "violations": violations,
        }, indent=2, ensure_ascii=False))
    else:
        print(format_report(violations, severity, str(path)))

    if severity == "BLOCK":
        sys.exit(2)
    if severity == "WARN" and args.block_on_warn:
        sys.exit(2)
    if severity == "WARN":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
