#!/usr/bin/env python3
"""
anti_drift_guard.py -- max-N-Ebenen-Validator [CRUX-MK]
MYZ00025 Vorarbeit (2026-04-19)

Prueft Playbook/Kapitel-Dokumente gegen Ebenen-Cap (Anti-Drift-Mechanik).
Martin-Empirie: LLM-Attention-Drift bei > 11-14 Ebenen (Souveraene Maschine: 11).

Usage:
    python anti_drift_guard.py --check <playbook.md> --max-ebenen 11
    python anti_drift_guard.py --check <kapitel.md> --max-dominant 2 --category C1-roman
    python anti_drift_guard.py --check <file> --json

Exit-Codes:
    0 = OK
    1 = WARN (nahe am Cap)
    2 = BLOCK (Cap ueberschritten)
"""

import argparse
import json
import re
import sys
from pathlib import Path


def count_ebenen_in_kapitel(text):
    """Zaehlt verschiedene Ebenen-Marker in einem Kapitel-Abschnitt."""
    ebenen_markers = set()

    patterns = [
        r"(?i)schattenkind|sonnenkind",  # Stahl
        r"(?i)transaktion|eltern.?ich|kind.?ich|erwachsenen.?ich",  # Berne
        r"(?i)spiral.?(?:stufe|dynamics)|(?:blau|orange|gruen|gelb)\s+(?:als\s+)?spiral",  # Spiral
        r"(?i)labeling|mirroring|calibrated|taktische\s+empath",  # Voss
        r"(?i)koerper|van\s+der\s+kolk|kiefer|zittern",  # Van der Kolk
        r"(?i)macht|greene|verdecktes\s+ziel",  # Greene
        r"(?i)cialdini|pre.?suasion|reciprocity",  # Cialdini
        r"(?i)antifragil|skin\s+in\s+the\s+game|taleb",  # Taleb
        r"(?i)girard|mimetisch|opferlogik",  # Girard
        r"(?i)rand\b|atlas\s+shrugged",  # Rand
        r"(?i)kaestner|zaertliche\s+schaerfe",  # Kaestner-Ton
        r"(?i)disc.?profil|\bDISC\b",  # DISC
        r"(?i)wolynn|transgenerational",  # Wolynn
        r"(?i)maslow|beduerfnis",  # Maslow
        r"(?i)eic.?konzept|eic.?theorie",  # EIC buchspezifisch
    ]

    names = ["stahl", "berne", "spiral", "voss", "koerper", "greene", "cialdini",
             "taleb", "girard", "rand", "kaestner", "disc", "wolynn", "maslow", "eic"]

    for i, pattern in enumerate(patterns):
        if re.search(pattern, text):
            ebenen_markers.add(names[i])

    return ebenen_markers


def count_dominant_einfluss(text):
    """Zaehlt wie viele 'Dominanter Einfluss' pro Kapitel genannt sind."""
    # Sucht nach Zeilen die "dominant" + "Einfluss" enthalten und zaehlt , oder +
    dominant_lines = re.findall(r"(?i)dominant\w*\s*einfluss[^\n]*", text)
    counts = []
    for line in dominant_lines:
        # Zaehle Autor-Namen in der Zeile (durch , oder + getrennt)
        # Einfache Heuristik: zaehle Grossbuchstaben-Woerter als Autor
        authors = re.findall(r"\b[A-ZÄÖÜ][a-zäöüß]{3,}\b", line)
        # Filter Stop-Woerter
        stopwords = {"Dominant", "Einfluss", "Dominanter", "Dominantes"}
        authors = [a for a in authors if a not in stopwords]
        counts.append(len(authors))
    return counts


def split_kapitel(text):
    """Splittet Dokument in Kapitel via '## Kap' oder '# Kapitel'."""
    parts = re.split(r"(?im)^#{1,2}\s+(?:kapitel|kap\b)\s*\d+", text)
    if len(parts) == 1:
        return [("full", text)]
    return [(f"kapitel-{i}", p) for i, p in enumerate(parts, 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", required=True)
    ap.add_argument("--max-ebenen", type=int, default=11)
    ap.add_argument("--max-dominant", type=int, default=2)
    ap.add_argument("--category", default="C1-roman", help="C1-C7")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    path = Path(args.check)
    if not path.exists():
        print(f"ERROR: {path}", file=sys.stderr)
        sys.exit(2)

    text = path.read_text(encoding="utf-8")
    kapitel = split_kapitel(text)

    violations = []
    warnings = []

    for name, content in kapitel:
        ebenen = count_ebenen_in_kapitel(content)
        dominant_counts = count_dominant_einfluss(content)

        if len(ebenen) > args.max_ebenen:
            violations.append({
                "kapitel": name,
                "type": "ebenen_cap",
                "count": len(ebenen),
                "max": args.max_ebenen,
                "ebenen": sorted(ebenen),
            })
        elif len(ebenen) > args.max_ebenen - 1:
            warnings.append({
                "kapitel": name,
                "type": "ebenen_near_cap",
                "count": len(ebenen),
                "max": args.max_ebenen,
            })

        for dc in dominant_counts:
            if dc > args.max_dominant:
                violations.append({
                    "kapitel": name,
                    "type": "dominant_einfluss_cap",
                    "count": dc,
                    "max": args.max_dominant,
                })

    severity = "OK"
    if violations:
        severity = "BLOCK"
    elif warnings:
        severity = "WARN"

    result = {
        "file": str(path),
        "severity": severity,
        "category": args.category,
        "kapitel_count": len(kapitel),
        "violations": violations,
        "warnings": warnings,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"[{severity}] File: {path}")
        print(f"Kapitel analysiert: {len(kapitel)}")
        print(f"Category: {args.category} (max_ebenen={args.max_ebenen}, max_dominant={args.max_dominant})")
        for v in violations:
            print(f"  VIOLATION: {json.dumps(v, ensure_ascii=False)}")
        for w in warnings:
            print(f"  WARN: {json.dumps(w, ensure_ascii=False)}")

    if severity == "BLOCK":
        sys.exit(2)
    if severity == "WARN":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
