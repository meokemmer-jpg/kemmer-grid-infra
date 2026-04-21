#!/usr/bin/env python3
"""
category_router.py -- C1-C7 Buch-Klassifikator [CRUX-MK]
MYZ00021 Vorarbeit (2026-04-19)

Klassifiziert Buch-Projekt in eine der 7 Kategorien basierend auf Masterplan-Inhalt.
Gibt Pipeline-Variante + Template-Mapping zurueck.

Usage:
    python category_router.py --input <masterplan.md>
    python category_router.py --input <masterplan.md> --json
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

CATEGORY_SIGNALS = {
    "C1-roman": {
        "patterns": [
            r"(?i)\b(?:figur|charakter|protagonist|antagonist)\b",
            r"(?i)\b(?:plot|handlung|dramaturgie|akt\s+\d)\b",
            r"(?i)\b(?:szene|szenen|dialog|schauplatz)\b",
            r"(?i)\b(?:schattenkind|sonnenkind)\b",  # Stahl-Signal
            r"(?i)\b(?:roman|novelle|erzaehlung|geschichte)\b",
        ],
        "weight": 1.0,
        "pipeline": "phase_1_masterplan -> phase_2_kochrezept -> phase_3_kapitel_iter -> phase_4_wargame -> phase_5_produktionsbibel -> phase_6_pmo",
        "templates": ["T1_zutaten", "T2_character_psychogramm", "T3_figuren_kapitel_bogen"],
        "ebenen_max": 11,
    },
    "C2-sachbuch": {
        "patterns": [
            r"(?i)\b(?:these|argument|evidenz|fallstudie)\b",
            r"(?i)\b(?:autor|expert|forschung|studie)\b",
            r"(?i)\b(?:leadership|strategy|management|business)\b",
            r"(?i)\b(?:kapitel\s+\d+\s*[-:]\s*[A-Z])\b",  # Nummerierte Kapitel mit Titel
        ],
        "weight": 1.0,
        "pipeline": "phase_1_thesenplan -> phase_2_argument_graph -> phase_3_fallstudien -> phase_4_wargame -> phase_5_produktionsbibel -> phase_6_pmo",
        "templates": ["T1_quellen_matrix", "T2_argument_kette", "T3_thesen_verlauf"],
        "ebenen_max": 6,
    },
    "C3-interaktiv": {
        "patterns": [
            r"(?i)\b(?:lernziel|lehrplan|didakt|uebung)\b",
            r"(?i)\b(?:anton|conny|dana|bernd)\b",  # Mathebuch-Charaktere
            r"(?i)\b(?:aufgabe|quiz|dialog\s+zwischen)\b",
            r"(?i)\b(?:interaktiv|multi.?character)\b",
        ],
        "weight": 1.0,
        "pipeline": "phase_1_lernziel_matrix -> phase_2_character_profile -> phase_3_dialog_pfade -> phase_4_wargame -> phase_5_produktionsbibel -> phase_6_pmo",
        "templates": ["T1_lernziel_zutaten", "T2_lernziel_character_map", "T3_interaktions_pfad"],
        "ebenen_max": 8,  # 3D Lernziel x Charakter x Interaktion
    },
    "C4-verlags-doc": {
        "patterns": [
            r"(?i)\b(?:kpi|roi|p&l|board|governance|pmo)\b",
            r"(?i)\b(?:graphity|verlag|publisher)\b",
            r"(?i)\b(?:mckinsey|executive\s+summary|exec.?layer)\b",
            r"(?i)\b(?:arithmetik|zahlenwerk)\b",
        ],
        "weight": 1.0,
        "pipeline": "phase_1_executive_frame -> phase_2_daten_architektur -> phase_3_kapitel_fact_based -> phase_4_wargame -> phase_5_produktionsbibel -> phase_6_pmo_reflection",
        "templates": ["T1_kpi_matrix", "T2_governance_layer", "T3_entscheidungs_fluss"],
        "ebenen_max": 5,
    },
    "C5-co-autor": {
        "patterns": [
            r"(?i)\b(?:co.?autor|mit.?autor|gemeinsam\s+geschrieben)\b",
            r"(?i)\b(?:bertram|schramm|gieske)\b",  # Turning-Tide-Co-Autoren
            r"(?i)\b(?:bim|baukulturelle)\b",
            r"(?i)\b(?:meeting|workshop|zyklus)\b",
        ],
        "weight": 1.0,
        "pipeline": "phase_1_autor_rollen -> phase_2_voice_fingerprints -> phase_3_kapitel_alternierend -> phase_4_wargame_voice_diff -> phase_5_produktionsbibel -> phase_6_pmo",
        "templates": ["T1_autor_matrix", "T2_voice_fingerprint", "T3_meeting_zyklus"],
        "ebenen_max": 6,
    },
    "C6-tech-manual": {
        "patterns": [
            r"(?i)\b(?:spec|specification|api|code.?beispiel)\b",
            r"(?i)\b(?:checkliste|prozess.?schritt|compliance)\b",
            r"(?i)\b(?:hotelbau|bau|technik|manual)\b",
            r"(?i)\b(?:schritt\s+\d+|diagramm)\b",
        ],
        "weight": 1.0,
        "pipeline": "phase_1_prozess_architektur -> phase_2_spec_refs -> phase_3_kapitel_prozess_schritte -> phase_4_wargame_compliance -> phase_5_produktionsbibel -> phase_6_pmo",
        "templates": ["T1_spec_matrix", "T2_prozess_schritt_psychogramm", "T3_compliance_bogen"],
        "ebenen_max": 5,
    },
    "C7-meta": {
        "patterns": [
            r"(?i)\b(?:destillat|synthese|rezeption|extraktion)\b",
            r"(?i)\b(?:930|bibliothek|audible|wargame\s+buch)\b",
            r"(?i)\b(?:isomorphie|mapping|quellen.?attribution)\b",
        ],
        "weight": 1.0,
        "pipeline": "phase_1_quellen_plan -> phase_2_extraktion_regeln -> phase_3_destillat_drafts -> phase_4_wargame_consistency -> phase_5_produktionsbibel -> phase_6_pmo",
        "templates": ["T1_quellen_attribution", "T2_destillat_schema", "T3_isomorphie_map"],
        "ebenen_max": 4,
    },
}


def classify(text):
    """Gibt (winner, scores_dict, confidence) zurueck."""
    scores = {}
    text_lower = text.lower()

    for cat, config in CATEGORY_SIGNALS.items():
        count = 0
        for pattern in config["patterns"]:
            count += len(re.findall(pattern, text))
        scores[cat] = count * config["weight"]

    if max(scores.values()) == 0:
        return "unclassified", scores, 0.0

    winner = max(scores, key=scores.get)
    total = sum(scores.values())
    confidence = scores[winner] / total if total > 0 else 0.0
    return winner, scores, confidence


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"ERROR: {path}", file=sys.stderr)
        sys.exit(2)

    text = path.read_text(encoding="utf-8")
    winner, scores, conf = classify(text)

    config = CATEGORY_SIGNALS.get(winner, {})

    result = {
        "input": str(path),
        "category": winner,
        "confidence": round(conf, 3),
        "scores": scores,
        "pipeline": config.get("pipeline", "unknown"),
        "templates": config.get("templates", []),
        "ebenen_max": config.get("ebenen_max", 0),
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Category: {winner} (confidence {conf:.2%})")
        print(f"Scores: {sorted(scores.items(), key=lambda x: -x[1])[:3]}")
        print(f"Pipeline: {config.get('pipeline')}")
        print(f"Templates: {config.get('templates')}")
        print(f"Max Ebenen: {config.get('ebenen_max')}")


if __name__ == "__main__":
    main()
