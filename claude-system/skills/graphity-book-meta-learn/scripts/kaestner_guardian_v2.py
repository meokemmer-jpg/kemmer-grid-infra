#!/usr/bin/env python3
"""
kaestner_guardian_v2.py -- Staffel-Satzlaenge + Adjektiv-Fasten [CRUX-MK]
Wave-2 W5 Konsens: Codex+Gemini 2/2 MODIFY auf Base-Inheritance-Modell.

Changes v1 -> v2:
- Staffel-Hard-Cap pro Kategorie (statt globaler 20-Worte-Regel)
- Adjektiv-Fasten (max 1 Adjektiv pro Satz) - Gemini-Innovation
- Konkretheits-Index fuer Kaestner-Ton
- Base-Inheritance-Modell (Global + Category-Overrides)

Usage:
    python kaestner_guardian_v2.py --check <file> --category K1
    python kaestner_guardian_v2.py --check <file> --category K6 --report-json
"""

import argparse
import io
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

# BIAS-036 Fix: Force UTF-8 stdout on Windows to handle Unicode chars like \u03c9
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


# ==========================================================================
# CONFIG (Base-Inheritance post Wave-2 W5)
# ==========================================================================

GLOBAL_RULES = {
    "max_adjectives_per_sentence": 1,   # Gemini: Adjektiv-Fasten
    "forbidden_emojis": True,
    "forbidden_svo_violation": False,   # Warnung, nicht Block
    "require_active_voice": True,
}

CATEGORY_CONFIG = {
    "K1":  {"hard_cap_words": 22, "soft_min": 8,  "soft_max": 18, "name": "Narrativ"},
    "K1a": {"hard_cap_words": 40, "soft_min": 8,  "soft_max": 30, "name": "Kemmer-Stil (bewusste lange Parataxen)"},   # Martin-Direktive 2026-04-19: Kategorie heisst "Kemmer-Stil"
    "K1b": {"hard_cap_words": 65, "soft_min": 8,  "soft_max": 50, "name": "Kemmer-Stil-Extrem (Prolog/Kuechentisch-Szenen)"},  # Martin-Direktive 2026-04-19: K1b fuer Extrem-Parataxen bis 75 Worte
    "K2":  {"hard_cap_words": 25, "soft_min": 12, "soft_max": 22, "name": "Argumentativ/Sachbuch"},
    "K3":  {"hard_cap_words": 18, "soft_min": 10, "soft_max": 15, "name": "Didaktisch"},
    "K4":  {"hard_cap_words": 20, "soft_min": 10, "soft_max": 18, "name": "Operativ"},
    "K5":  {"hard_cap_words": 20, "soft_min": 10, "soft_max": 18, "name": "Referenziell"},
    "K6":  {"hard_cap_words": 14, "soft_min": 6,  "soft_max": 14, "name": "Tech-Manual"},
}

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

# Kaestner-Ton: Konkretheits-Proxy (Gemini-Empfehlung)
ABSTRACT_NOUNS = [
    r"(?i)\b(?:loesung|ansatz|herangehensweise|moeglichkeit|tendenz)\b",
    r"(?i)\b(?:prozess|struktur|funktion|system|mechanismus)\b",
    r"(?i)\b(?:aspekt|dimension|ebene|faktor|element)\b",
]

# Simple Adjektiv-Detektor (Heuristik, nicht linguistisch perfekt)
# Endungen: -e, -er, -es, -en, -em nach Substantiven oder Artikeln
ADJEKTIV_PATTERN = re.compile(
    r"\b(?:der|die|das|den|dem|ein|eine|einer|eines|einen|einem)\s+"
    r"((?:[A-ZÄÖÜa-zäöüß]+(?:e|er|es|en|em|ig|isch|lich)\s+){1,3})"
    r"(?=[A-ZÄÖÜ][a-zäöüß]+)"
)

EMOJI_PATTERN = re.compile(
    r"[\U0001F300-\U0001F9FF"
    r"\U0001F600-\U0001F64F"
    r"\U0001F680-\U0001F6FF"
    r"\U00002600-\U000027BF"
    r"\U0001FA70-\U0001FAFF"
    r"]", re.UNICODE)

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ])")

# Passiv-Heuristik (wird/werden + Partizip)
PASSIV_PATTERN = re.compile(
    r"\b(?:wird|werden|wurde|wurden|worden|sein|ist|sind|war|waren)\s+[a-zäöüß]+(?:t|en|et)\b",
    re.IGNORECASE
)


# ==========================================================================
# CHECK FUNCTIONS
# ==========================================================================

def count_words(sentence):
    return len(re.findall(r"\b\w+\b", sentence))


def count_adjectives(sentence):
    """Heuristik: zaehlt Adjektive ueber Artikel+Adj+Subst-Muster."""
    matches = ADJEKTIV_PATTERN.findall(sentence)
    # Jedes Match kann mehrere Adjektive enthalten (Trennung ueber Whitespace)
    count = 0
    for m in matches:
        count += len([w for w in m.strip().split() if len(w) > 3])
    return count


def count_abstract_nouns(sentence):
    count = 0
    for p in ABSTRACT_NOUNS:
        count += len(re.findall(p, sentence))
    return count


def check_text(text, category_config):
    """Pruefe Text gegen Category-Config + Global-Rules."""
    violations = {
        "hard_cap_violations": [],
        "adjektiv_ueberschreitungen": [],
        "filler_phrases": [],
        "motivation_rhetoric": [],
        "emojis": [],
        "passiv_alerts": [],
    }
    stats = {
        "sentences_total": 0,
        "abstract_nouns_total": 0,
        "concrete_nouns_ratio_estimate": 0.0,
    }

    # Clean text (strip code-blocks)
    text_clean = re.sub(r"```[\s\S]*?```", "", text)
    text_clean = re.sub(r"`[^`]+`", "", text_clean)

    sentences = SENTENCE_SPLIT.split(text_clean)

    hard_cap = category_config["hard_cap_words"]
    soft_max = category_config["soft_max"]
    max_adj = GLOBAL_RULES["max_adjectives_per_sentence"]

    for s in sentences:
        s_clean = s.strip()
        if not s_clean or s_clean.startswith("#") or s_clean.startswith("|") or s_clean.startswith("-"):
            continue

        stats["sentences_total"] += 1
        wc = count_words(s_clean)

        # Hard-Cap-Check
        if wc > hard_cap:
            violations["hard_cap_violations"].append({
                "sentence": s_clean[:150] + ("..." if len(s_clean) > 150 else ""),
                "word_count": wc,
                "hard_cap": hard_cap,
            })

        # Adjektiv-Fasten (Gemini)
        adj_count = count_adjectives(s_clean)
        if adj_count > max_adj:
            violations["adjektiv_ueberschreitungen"].append({
                "sentence": s_clean[:150] + ("..." if len(s_clean) > 150 else ""),
                "adjectives": adj_count,
                "max": max_adj,
            })

        # Abstract-Noun-Count (fuer Konkretheits-Index)
        stats["abstract_nouns_total"] += count_abstract_nouns(s_clean)

        # Passiv-Check
        if PASSIV_PATTERN.search(s_clean) and GLOBAL_RULES["require_active_voice"]:
            violations["passiv_alerts"].append({
                "sentence": s_clean[:150] + ("..." if len(s_clean) > 150 else "")
            })

    # Filler/Motivation/Emoji (ganzes Text)
    for pattern in FILLER_PHRASES:
        for m in re.finditer(pattern, text_clean):
            violations["filler_phrases"].append({
                "phrase": m.group(),
                "position": m.start(),
            })

    for pattern in MOTIVATION_RHETORIC:
        for m in re.finditer(pattern, text_clean):
            violations["motivation_rhetoric"].append({
                "phrase": m.group(),
                "position": m.start(),
            })

    for m in EMOJI_PATTERN.finditer(text_clean):
        violations["emojis"].append({"emoji": m.group(), "position": m.start()})

    # Konkretheits-Ratio (Proxy fuer Kaestner-Ton)
    if stats["sentences_total"] > 0:
        stats["concrete_nouns_ratio_estimate"] = round(
            1.0 - (stats["abstract_nouns_total"] / max(1, stats["sentences_total"] * 2)),
            3
        )

    return violations, stats


def classify_severity(violations, stats):
    """OK / WARN / BLOCK."""
    if violations["emojis"]:
        return "BLOCK", "Emojis gefunden (verboten)"
    if len(violations["hard_cap_violations"]) >= 3:
        return "BLOCK", f"{len(violations['hard_cap_violations'])} Saetze ueber Hard-Cap"
    if len(violations["motivation_rhetoric"]) >= 3:
        return "BLOCK", f"{len(violations['motivation_rhetoric'])} Motivations-Rhetorik-Treffer"
    if len(violations["adjektiv_ueberschreitungen"]) >= 5:
        return "BLOCK", f"{len(violations['adjektiv_ueberschreitungen'])} Adjektiv-Fasten-Verletzungen"

    warnings = (
        len(violations["hard_cap_violations"]) +
        len(violations["adjektiv_ueberschreitungen"]) +
        len(violations["filler_phrases"]) +
        len(violations["motivation_rhetoric"]) +
        len(violations["passiv_alerts"])
    )
    if warnings >= 3:
        return "WARN", f"{warnings} Gesamtwarnungen"

    # Konkretheits-Index (Kaestner-Ton)
    if stats["concrete_nouns_ratio_estimate"] < 0.6:
        return "WARN", f"Konkretheits-Index {stats['concrete_nouns_ratio_estimate']} < 0.6 (abstrakt)"

    return "OK", "Pass"


# ==========================================================================
# MAIN
# ==========================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", required=True)
    ap.add_argument("--category", default="K1", choices=list(CATEGORY_CONFIG.keys()))
    ap.add_argument("--report-json", action="store_true")
    args = ap.parse_args()

    path = Path(args.check)
    if not path.exists():
        print(f"ERROR: {path}", file=sys.stderr)
        sys.exit(3)

    text = path.read_text(encoding="utf-8")
    # Strip frontmatter
    text = re.sub(r"^---\n[\s\S]*?\n---\n", "", text, count=1)

    config = CATEGORY_CONFIG[args.category]
    violations, stats = check_text(text, config)
    severity, reason = classify_severity(violations, stats)

    result = {
        "file": str(path),
        "category": args.category,
        "category_name": config["name"],
        "hard_cap": config["hard_cap_words"],
        "severity": severity,
        "reason": reason,
        "violations": violations,
        "stats": stats,
    }

    if args.report_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"[{severity}] {reason}")
        print(f"Kategorie: {args.category} ({config['name']}, hard_cap={config['hard_cap_words']})")
        print(f"Saetze: {stats['sentences_total']}")
        print(f"Konkretheits-Index: {stats['concrete_nouns_ratio_estimate']}")
        for vtype, items in violations.items():
            if items:
                print(f"  {vtype}: {len(items)}")
                for item in items[:3]:
                    print(f"    - {json.dumps(item, ensure_ascii=False)[:120]}")

    if severity == "BLOCK":
        sys.exit(2)
    if severity == "WARN":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
