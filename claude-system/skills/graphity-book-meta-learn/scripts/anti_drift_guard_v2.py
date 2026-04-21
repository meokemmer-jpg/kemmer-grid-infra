#!/usr/bin/env python3
"""
anti_drift_guard_v2.py -- Typklassen-Contract-Validator [CRUX-MK]
v2 Rewrite post Cross-LLM-Wargame 2026-04-19 (Codex + Gemini + Grok).

SUPERSEDED v1 (flache 11-Ebenen-Liste). v2 verwendet Codex-Typklassen:
- spine              (1 required)
- primary_lens       (1 required)
- secondary_lens     (0..1 Counter-Force)
- global_invariants  (N frozen, count NOT as dominants)
- forbidden_lenses   (explicit exclusions)
- meta_frame         (0..1 optional)

Anti-Drift-Tiers (Grok-Dissens-Opt-In):
- default:              primary=1, secondary=0..1, total_active<=3
- meta_narrative_opt_in: primary=1, secondary=0..3, total_active<=5 (bei 1M-Context)

Sliding-Window-Drift-Check (Gemini): Alle 200 Token Dichte der Marker pruefen.

Usage:
    python anti_drift_guard_v2.py --check <kapitel.md> --contract <contract.yaml>
    python anti_drift_guard_v2.py --check <kapitel.md> --tier meta_narrative_opt_in
    python anti_drift_guard_v2.py --check <kapitel.md> --sliding-window 200

Exit-Codes:
    0 = OK
    1 = WARN (Drift-Naehe)
    2 = BLOCK (Contract-Violation)
    3 = ERROR
"""

import argparse
import json
import re
import sys
from collections import Counter
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
# TIER-CONFIG (Grok-Dissens Opt-In)
# ==========================================================================

TIER_CONFIG = {
    "default": {
        "primary_slots": 1,
        "secondary_slots_max": 1,
        "total_active_max": 3,   # primary + secondary + meta
        "description": "Codex+Gemini Konsens, default fuer alle Kategorien"
    },
    "meta_narrative_opt_in": {
        "primary_slots": 1,
        "secondary_slots_max": 3,
        "total_active_max": 5,
        "requires_context_window": 500000,
        "description": "Grok-Empfehlung fuer House-of-Leaves-Style Meta-Narrative, 1M-Context Opt-In"
    },
    "business_doc": {
        "primary_slots": 1,       # 1 Claim
        "secondary_slots_max": 2, # 1 Evidence + 1 Risk
        "total_active_max": 3,
        "description": "K4 Operativ: Claim + Evidenz + Risiko"
    },
    "didactic": {
        "primary_slots": 1,       # 1 Lernziel
        "secondary_slots_max": 1, # 1 Progression
        "total_active_max": 2,
        "description": "K3 Didaktisch"
    }
}


# ==========================================================================
# LENS-MARKER (fuer Sliding-Window-Detection)
# ==========================================================================

LENS_MARKERS = {
    "STAHL": [r"(?i)schattenkind", r"(?i)sonnenkind", r"(?i)glaubenssatz"],
    "BERNE": [r"(?i)eltern.?ich", r"(?i)kind.?ich", r"(?i)erwachsenen.?ich", r"(?i)transaktion"],
    "SPIRAL": [r"(?i)spiral.?stufe", r"(?i)\b(?:blau|orange|gruen|gelb)e?\s+stufe"],
    "VOSS": [r"(?i)labeling", r"(?i)mirroring", r"(?i)calibrated", r"(?i)taktische\s+empath"],
    "KOERPER": [r"(?i)kiefer(n)?", r"(?i)zittern", r"(?i)atem", r"(?i)koerper\w*"],
    "GREENE": [r"(?i)verdecktes?\s+ziel", r"(?i)macht\w*", r"(?i)greene"],
    "CIALDINI": [r"(?i)cialdini", r"(?i)pre.?suasion", r"(?i)reciprocity"],
    "TALEB": [r"(?i)antifragil", r"(?i)skin\s+in\s+the\s+game", r"(?i)taleb"],
    "GIRARD": [r"(?i)mimetisch", r"(?i)girard", r"(?i)opferlogik"],
    "KAESTNER": [r"(?i)kaestner", r"(?i)zaertliche\s+schaerfe"],
    "RAND": [r"(?i)\brand\b", r"(?i)atlas\s+shrugged"],
    "DISC": [r"(?i)\bDISC\b", r"(?i)primaer\s+[DISC]"],
    "WOLYNN": [r"(?i)wolynn", r"(?i)transgenerational"],
    "MASLOW": [r"(?i)maslow", r"(?i)beduerfnishierarchie"],
    "VAN_DER_KOLK": [r"(?i)van\s+der\s+kolk", r"(?i)body\s+keeps"],
    "EIC": [r"(?i)eic.?konzept", r"(?i)eic.?theorie"],
}


# ==========================================================================
# CONTRACT-LOADER
# ==========================================================================

def load_contract(contract_path):
    """Laedt Kapitel-Contract aus YAML."""
    with open(contract_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_contract(contract, tier_config):
    """Prueft ob Contract selbst valide ist (vor Kapitel-Check)."""
    errors = []

    if not contract.get("spine"):
        errors.append("spine fehlt (required)")
    if not contract.get("primary_lens"):
        errors.append("primary_lens fehlt (required)")

    secondary = contract.get("secondary_lenses", [])
    if isinstance(secondary, str):
        secondary = [secondary] if secondary else []
    if len(secondary) > tier_config["secondary_slots_max"]:
        errors.append(f"secondary_lenses {len(secondary)} > max {tier_config['secondary_slots_max']}")

    active_count = 1  # primary
    active_count += len(secondary)
    if contract.get("meta_frame"):
        active_count += 1
    if active_count > tier_config["total_active_max"]:
        errors.append(f"total_active {active_count} > max {tier_config['total_active_max']}")

    return errors


# ==========================================================================
# LENS-DETECTION im Text
# ==========================================================================

def detect_lenses(text):
    """Gibt dict {lens_name: match_count} zurueck."""
    detected = {}
    for lens, patterns in LENS_MARKERS.items():
        count = 0
        for p in patterns:
            count += len(re.findall(p, text))
        if count > 0:
            detected[lens] = count
    return detected


def sliding_window_check(text, window_tokens=200, min_dominant_density=0.5):
    """
    Gemini-Ansatz: Sliding-Window alle N Tokens.
    Prueft ob die dominanten Layer regelmaessig auftauchen.

    Token-Approximation: 1 Token ≈ 0.75 Worte, also window_tokens*0.75 Worte.
    """
    words = text.split()
    window_words = int(window_tokens * 0.75)
    windows = []

    for i in range(0, len(words), window_words // 2):  # 50% overlap
        window_text = " ".join(words[i:i + window_words])
        lenses = detect_lenses(window_text)
        windows.append({
            "start_word": i,
            "end_word": i + window_words,
            "detected_lenses": lenses,
            "total_markers": sum(lenses.values()),
        })

    return windows


# ==========================================================================
# CONTRACT vs REALITY Check
# ==========================================================================

def check_kapitel_against_contract(text, contract, tier_config):
    """
    Prueft Kapitel-Text gegen Chapter-Contract.
    Returns: {violations: [...], warnings: [...], detected_lenses: {...}}
    """
    result = {
        "violations": [],
        "warnings": [],
        "detected_lenses": {},
        "sliding_windows": [],
    }

    # Detect all lenses in text
    detected = detect_lenses(text)
    result["detected_lenses"] = detected

    # Expected lenses
    primary = contract.get("primary_lens", "").upper()
    secondary_raw = contract.get("secondary_lenses", [])
    if isinstance(secondary_raw, str):
        secondary_raw = [secondary_raw]
    secondary = [s.upper() for s in secondary_raw]
    forbidden = [f.upper() for f in contract.get("forbidden_lenses", [])]
    global_invariants = [g.upper() for g in contract.get("global_invariants", [])]

    # Allowed = primary + secondary + global_invariants (frozen counts not as dominant)
    allowed = {primary, *secondary, *global_invariants}

    # Forbidden-Check
    for lens, count in detected.items():
        if lens in forbidden:
            result["violations"].append({
                "type": "forbidden_lens_present",
                "lens": lens,
                "count": count,
                "message": f"Forbidden lens '{lens}' appears {count}x"
            })

    # Dominance-Check: Wieviele nicht-allowed Lenses dominieren?
    dominant_threshold = 3  # 3+ Markers = gilt als aktiv dominiert
    unallowed_dominant = [
        (lens, count) for lens, count in detected.items()
        if lens not in allowed and count >= dominant_threshold
    ]

    if len(unallowed_dominant) > 0:
        result["violations"].append({
            "type": "unallowed_dominant_lens",
            "lenses": unallowed_dominant,
            "message": f"{len(unallowed_dominant)} lenses not in contract.allowed but dominate text"
        })

    # Primary-Presence-Check
    primary_count = detected.get(primary, 0)
    if primary_count < dominant_threshold:
        result["warnings"].append({
            "type": "primary_lens_weak",
            "lens": primary,
            "count": primary_count,
            "threshold": dominant_threshold,
            "message": f"Primary lens '{primary}' has only {primary_count} markers (< {dominant_threshold})"
        })

    # Sliding-Window-Check
    windows = sliding_window_check(text, window_tokens=200)
    result["sliding_windows"] = windows
    windows_without_primary = sum(
        1 for w in windows if w["detected_lenses"].get(primary, 0) == 0
    )
    if windows_without_primary > len(windows) * 0.3:  # >30% Fenster ohne Primary
        result["warnings"].append({
            "type": "primary_lens_drift",
            "windows_without_primary": windows_without_primary,
            "total_windows": len(windows),
            "message": f"Primary lens disappears in {windows_without_primary}/{len(windows)} windows (>30%)"
        })

    return result


def classify_severity(check_result):
    if check_result["violations"]:
        return "BLOCK"
    if check_result["warnings"]:
        return "WARN"
    return "OK"


# ==========================================================================
# MAIN
# ==========================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", required=True, help="Pfad zu Kapitel-Markdown")
    ap.add_argument("--contract", help="Pfad zu chapter_contract.yaml (optional, inferred from frontmatter if absent)")
    ap.add_argument("--tier", default="default", choices=list(TIER_CONFIG.keys()))
    ap.add_argument("--sliding-window", type=int, default=200, help="Window-Groesse in Tokens")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    path = Path(args.check)
    if not path.exists():
        print(f"ERROR: {path}", file=sys.stderr)
        sys.exit(3)

    text = path.read_text(encoding="utf-8")

    # Strip frontmatter
    text_no_fm = re.sub(r"^---\n[\s\S]*?\n---\n", "", text, count=1)

    # Load contract
    contract = None
    if args.contract:
        contract = load_contract(args.contract)
    else:
        # Try to parse from frontmatter of kapitel itself
        fm_match = re.match(r"^---\n([\s\S]*?)\n---\n", text)
        if fm_match:
            try:
                fm_data = yaml.safe_load(fm_match.group(1))
                if "chapter_contract" in fm_data:
                    contract = fm_data["chapter_contract"]
            except yaml.YAMLError:
                pass

    if not contract:
        print("ERROR: No chapter_contract found (neither --contract nor embedded in frontmatter)", file=sys.stderr)
        sys.exit(3)

    tier_cfg = TIER_CONFIG[args.tier]

    # Validate contract itself
    contract_errors = validate_contract(contract, tier_cfg)
    if contract_errors:
        print(f"CONTRACT INVALID for tier '{args.tier}':", file=sys.stderr)
        for e in contract_errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(2)

    # Check text against contract
    check_result = check_kapitel_against_contract(text_no_fm, contract, tier_cfg)
    severity = classify_severity(check_result)

    result = {
        "file": str(path),
        "severity": severity,
        "tier": args.tier,
        "contract": contract,
        "check_result": check_result,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"[{severity}] File: {path}")
        print(f"Tier: {args.tier} ({tier_cfg['description']})")
        print(f"Contract: primary={contract.get('primary_lens')}, secondary={contract.get('secondary_lenses', [])}, forbidden={contract.get('forbidden_lenses', [])}")
        print(f"Detected lenses: {json.dumps(check_result['detected_lenses'], ensure_ascii=False)}")
        print(f"Sliding windows: {len(check_result['sliding_windows'])}")
        for v in check_result["violations"]:
            print(f"  VIOLATION: {v['message']}")
        for w in check_result["warnings"]:
            print(f"  WARN: {w['message']}")

    if severity == "BLOCK":
        sys.exit(2)
    if severity == "WARN":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
