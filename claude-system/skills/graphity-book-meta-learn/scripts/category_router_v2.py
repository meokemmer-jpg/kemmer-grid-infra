#!/usr/bin/env python3
"""
category_router_v2.py -- Bitmask-Assignment [CRUX-MK]
Wave-1 Grok-Dissens-Integration: Hybrid-Kategorien via Bitmask statt Enum.

Changes v1 -> v2:
- 5 Kern-Kategorien K1-K5 als Bitmask-Flags (Codex+Gemini-Konsens)
- Hybrid-Erkennung: Buch kann mehrere Flags setzen (Grok-Dissens)
- Primary-Category-Auswahl fuer Pipeline-Routing
- Overlays: Co-Author, Bundle, Biografisch

Bitmask-Schema:
  0b0000001 = K1 Narrativ
  0b0000010 = K2 Argumentativ/Sachbuch
  0b0000100 = K3 Didaktisch/Interaktiv
  0b0001000 = K4 Operativ/Verlags-Doc
  0b0010000 = K5 Referenziell/Meta
  0b0100000 = Co-Author-Overlay
  0b1000000 = Bundle/Serie-Overlay

Beispiel:
  Meta-Tech-Roman (K1+K4+K5) = 0b0011001 = 25
  Co-Author-Sachbuch (K2+Co-Author) = 0b0100010 = 34

Usage:
    python category_router_v2.py --input <masterplan.md>
    python category_router_v2.py --input <masterplan.md> --json
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

# ==========================================================================
# BITMASK-FLAGS
# ==========================================================================

FLAGS = {
    "K1_narrativ":      0b0000001,
    "K2_argumentativ":  0b0000010,
    "K3_didaktisch":    0b0000100,
    "K4_operativ":      0b0001000,
    "K5_referenziell":  0b0010000,
    "overlay_co_author": 0b0100000,
    "overlay_bundle":    0b1000000,
    "overlay_biografisch": 0b10000000,
}


# ==========================================================================
# DETECTION-PATTERNS (per Flag)
# ==========================================================================

FLAG_PATTERNS = {
    "K1_narrativ": [
        r"(?i)\b(?:figur|charakter|protagonist|antagonist)\b",
        r"(?i)\b(?:plot|handlung|dramaturgie|akt\s+\d)\b",
        r"(?i)\b(?:szene|dialog|schauplatz|erzaehler)\b",
        r"(?i)\b(?:schattenkind|sonnenkind)\b",
        r"(?i)\b(?:roman|novelle|erzaehlung)\b",
    ],
    "K2_argumentativ": [
        r"(?i)\b(?:these|argument|evidenz|fallstudie)\b",
        r"(?i)\b(?:autor|expert|forschung|studie)\b",
        r"(?i)\b(?:leadership|strategy|business)\b",
        r"(?i)\b(?:kapitel\s+\d+\s*[-:]\s*[A-ZÄÖÜ])\b",
    ],
    "K3_didaktisch": [
        r"(?i)\b(?:lernziel|lehrplan|didakt|uebung)\b",
        r"(?i)\b(?:anton|conny|dana|bernd)\b",
        r"(?i)\b(?:aufgabe|quiz|dialog\s+zwischen)\b",
        r"(?i)\b(?:interaktiv|multi.?character|lehrbuch)\b",
    ],
    "K4_operativ": [
        r"(?i)\b(?:kpi|roi|p&l|board|governance|pmo)\b",
        r"(?i)\b(?:graphity|verlag|publisher)\b",
        r"(?i)\b(?:mckinsey|executive\s+summary)\b",
        r"(?i)\b(?:arithmetik|zahlenwerk|playbook)\b",
    ],
    "K5_referenziell": [
        r"(?i)\b(?:destillat|synthese|rezeption|extraktion)\b",
        r"(?i)\b(?:930|bibliothek|audible|wargame\s+buch)\b",
        r"(?i)\b(?:isomorphie|mapping|quellen.?attribution)\b",
        r"(?i)\b(?:tech(?:nisches)?\s+manual|checkliste|spec)\b",  # Tech-Manual als K5-Subtyp (Codex-merge)
    ],
    "overlay_co_author": [
        r"(?i)\b(?:co.?autor|mit.?autor|gemeinsam\s+geschrieben)\b",
        r"(?i)\b(?:bertram|schramm|gieske)\b",
        r"(?i)\b(?:mehrere\s+autoren|multi.?autor)\b",
    ],
    "overlay_bundle": [
        r"(?i)\b(?:serie|reihe|band\s+\d+|buch\s+\d+\s+von)\b",
        r"(?i)\b(?:programm|bundle|trilogie)\b",
    ],
    "overlay_biografisch": [
        r"(?i)\b(?:biografie|biography|memoir|autobiografie)\b",
        r"(?i)\b(?:lebenserinnerung|geschichte\s+meines)\b",
    ],
}


# ==========================================================================
# DETECTION LOGIC
# ==========================================================================

def compute_flag_scores(text):
    """Zaehlt Matches pro Flag."""
    scores = {}
    for flag_name, patterns in FLAG_PATTERNS.items():
        count = 0
        for p in patterns:
            count += len(re.findall(p, text))
        scores[flag_name] = count
    return scores


def compute_bitmask(scores, threshold=2):
    """Aktiviere Flag wenn Score >= threshold. Primary-Category bleibt Einzel-Max."""
    bitmask = 0
    active_flags = []
    for flag_name, score in scores.items():
        if score >= threshold:
            bitmask |= FLAGS[flag_name]
            active_flags.append(flag_name)

    # Fallback: wenn keine Flag aktiviert, nimm den Max
    if bitmask == 0 and scores:
        max_flag = max(scores, key=scores.get)
        if scores[max_flag] > 0:
            bitmask = FLAGS[max_flag]
            active_flags.append(max_flag)

    return bitmask, active_flags


def get_primary_category(scores, active_flags):
    """Primary = hoechster Score unter Kern-Flags (nicht Overlays)."""
    core_flags = [f for f in active_flags if f.startswith("K")]
    if not core_flags:
        return "unclassified"
    return max(core_flags, key=lambda f: scores[f])


def is_hybrid(active_flags):
    core_count = sum(1 for f in active_flags if f.startswith("K"))
    return core_count >= 2


# ==========================================================================
# PIPELINE-CONFIG pro Kategorie
# ==========================================================================

PIPELINE_CONFIG = {
    "K1_narrativ": {
        "phases": ["masterplan", "kochrezept", "kapitel_iter", "wargame", "produktionsbibel", "pmo"],
        "templates": ["T1_zutaten", "T2_character_psychogramm", "T3_figuren_kapitel_bogen"],
        "anti_drift_tier": "default",  # oder "meta_narrative_opt_in" bei 1M-Context + Hybrid
        "ebenen_max": 11,
        "crossref_storage_hint": "YAML (wenn <2k Refs) oder SQLite (2-20k)",
    },
    "K2_argumentativ": {
        "phases": ["thesenplan", "argument_graph", "fallstudien", "wargame", "produktionsbibel", "pmo"],
        "templates": ["T1_quellen_matrix", "T2_argument_kette", "T3_thesen_verlauf"],
        "anti_drift_tier": "default",
        "ebenen_max": 6,
        "crossref_storage_hint": "SQLite mit claims_table (Fact-Provenance)",
    },
    "K3_didaktisch": {
        "phases": ["lernziel_matrix", "character_profile", "dialog_pfade", "wargame", "produktionsbibel", "pmo"],
        "templates": ["T1_lernziel_zutaten", "T2_lernziel_character_map", "T3_interaktions_pfad"],
        "anti_drift_tier": "didactic",
        "ebenen_max": 8,
        "crossref_storage_hint": "SQLite (Lernziel × Charakter × Interaktion)",
    },
    "K4_operativ": {
        "phases": ["executive_frame", "daten_architektur", "fact_based_kapitel", "wargame", "produktionsbibel", "pmo_reflection"],
        "templates": ["T1_kpi_matrix", "T2_governance_layer", "T3_entscheidungs_fluss"],
        "anti_drift_tier": "business_doc",
        "ebenen_max": 5,
        "crossref_storage_hint": "SQLite + Formal-Verification-Gates fuer KPIs",
    },
    "K5_referenziell": {
        "phases": ["quellen_plan", "extraktion_regeln", "destillat_drafts", "wargame", "produktionsbibel", "pmo"],
        "templates": ["T1_quellen_attribution", "T2_destillat_schema", "T3_isomorphie_map"],
        "anti_drift_tier": "default",
        "ebenen_max": 4,
        "crossref_storage_hint": "Shared-Library + Quellen-Attribution",
    },
}


# ==========================================================================
# MAIN
# ==========================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--threshold", type=int, default=2, help="Min-Score to activate flag")
    args = ap.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"ERROR: {path}", file=sys.stderr)
        sys.exit(2)

    text = path.read_text(encoding="utf-8")

    scores = compute_flag_scores(text)
    bitmask, active_flags = compute_bitmask(scores, threshold=args.threshold)
    primary = get_primary_category(scores, active_flags)
    hybrid = is_hybrid(active_flags)

    overlays = [f for f in active_flags if f.startswith("overlay_")]

    pipeline = PIPELINE_CONFIG.get(primary, {})

    result = {
        "input": str(path),
        "bitmask": bitmask,
        "bitmask_binary": bin(bitmask),
        "active_flags": active_flags,
        "primary_category": primary,
        "is_hybrid": hybrid,
        "overlays": overlays,
        "scores": scores,
        "pipeline_config": pipeline,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Primary: {primary} (hybrid: {hybrid})")
        print(f"Bitmask: {bin(bitmask)} = {bitmask}")
        print(f"Active: {active_flags}")
        print(f"Overlays: {overlays}")
        print(f"Pipeline: {pipeline.get('phases', [])}")
        print(f"Templates: {pipeline.get('templates', [])}")
        print(f"Anti-Drift-Tier: {pipeline.get('anti_drift_tier')}")
        print(f"Ebenen-Max: {pipeline.get('ebenen_max')}")
        print(f"CrossRef-Hint: {pipeline.get('crossref_storage_hint')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
