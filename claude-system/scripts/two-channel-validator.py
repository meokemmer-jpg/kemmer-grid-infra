#!/usr/bin/env python3
"""
Zwei-Kanal-Regel-Validator Pre-Write-Hook [CRUX-MK]

Prueft dass Decision-Cards und Findings die FIXPUNKT-2 Zwei-Kanal-Regel einhalten:
Meta-Score (meta_assessment / meta-ebene-verdict) darf NIE in Objekt-Score (object_score / rho-gain)
verrechnet werden. Validity-Flag / decision_effect-Felder muessen separat sein.

Author: Opus 4.7 METAOPS, 2026-04-18
Mission-1, Hook-2 von 4
Rules: meta-stack-fixpunkte.md FIXPUNKT-2 (Zwei-Kanal-Regel)

Scope (Pflicht):
- Claude-Vault/docs/decision-cards/
- branch-hub/findings/FINDING-
- branch-hub/cross-llm/ (Verdict-Dokumente)

Check-Regeln:
R1 (BLOCK): Formel-Pattern `object_score = ... meta_assessment ...` oder `combined_score` oder explizite Addition
R2 (WARN): Datei hat beide Felder (`object_score` + `meta_assessment`) aber kein `decision_effect`
R3 (WARN): Datei hat `object_score` und `meta-ebene: E[3-5]` aber weder `validity_flag` noch `policy_gate`

Exit-Codes:
    0 = OK
    1 = WARN
    2 = BLOCK (ENFORCE-mode)

Usage:
    python two-channel-validator.py <file-path> [--content-stdin] [--mode=CHECK|ENFORCE|AUDIT]
"""

import os
import sys
import re
import json
import argparse
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

SCOPE_PATTERNS = [
    r"Claude-Vault[/\\]docs[/\\]decision-cards[/\\]",
    r"branch-hub[/\\]findings[/\\]FINDING-",
    r"branch-hub[/\\]cross-llm[/\\]",
]

FORBIDDEN_PATTERNS = [
    # Formel-Vermischung
    (r"object_score\s*[=:]\s*.*meta[_\-]?(assessment|ebene|score)", "R1-BLOCK: object_score wird mit Meta-Wert verrechnet"),
    (r"combined[_\-]?score\s*[=:]", "R1-BLOCK: combined_score verletzt Zwei-Kanal-Trennung (FIXPUNKT-2)"),
    (r"rho[_\-]?gain\s*[=:]\s*.*meta[_\-]?assessment", "R1-BLOCK: rho_gain darf meta_assessment nicht enthalten"),
    (r"total[_\-]?score\s*=\s*object[_\-]?score\s*\+\s*meta", "R1-BLOCK: totale Summation Objekt+Meta"),
]

AUDIT_LOG = Path("G:/Meine Ablage/Claude-Knowledge-System/branch-hub/audit/two-channel-validator.jsonl")


def is_in_scope(file_path: str) -> bool:
    norm = file_path.replace("\\", "/")
    for pattern in SCOPE_PATTERNS:
        if re.search(pattern, norm, re.IGNORECASE):
            return True
    return False


def extract_frontmatter(content: str) -> dict | None:
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 4)
    if end == -1:
        return None
    fm_text = content[4:end]
    fm = {}
    for line in fm_text.split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()
    return fm


def check_forbidden_formulas(content: str) -> list[tuple[str, str]]:
    violations = []
    for pattern, msg in FORBIDDEN_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
            violations.append(("BLOCK", msg))
    return violations


def check_decision_effect_presence(fm: dict, content: str) -> list[tuple[str, str]]:
    warnings = []
    body_lower = content.lower()
    has_object = "object_score" in body_lower or "object-score" in body_lower
    has_meta = "meta_assessment" in body_lower or "meta-assessment" in body_lower
    has_decision_effect = "decision_effect" in body_lower or "decision-effect" in body_lower
    has_validity = "validity_flag" in body_lower or "validity-flag" in body_lower
    has_policy = "policy_gate" in body_lower or "policy-gate" in body_lower

    if has_object and has_meta and not has_decision_effect:
        warnings.append(("WARN", "R2-WARN: object_score+meta_assessment vorhanden, aber kein decision_effect-Feld (Zwei-Kanal unvollstaendig)"))

    ebene = fm.get("meta-ebene", "").strip().strip("\"'")
    if ebene in {"E3", "E4", "E5"} and has_object and not (has_validity or has_policy):
        warnings.append(("WARN", f"R3-WARN: object_score auf {ebene} ohne validity_flag/policy_gate — pruefe ob Meta-Information Prozess-Fuehrung beeinflussen sollte"))

    return warnings


def log_audit(entry: dict):
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        sys.stderr.write(f"[two-channel-validator] Audit-Log failed: {e}\n")


def main():
    parser = argparse.ArgumentParser(description="Zwei-Kanal-Regel-Validator [CRUX-MK]")
    parser.add_argument("file_path")
    parser.add_argument("--content-stdin", action="store_true")
    parser.add_argument("--mode", default="CHECK", choices=["CHECK", "ENFORCE", "AUDIT"])
    args = parser.parse_args()

    timestamp = datetime.now().isoformat()
    entry = {
        "ts": timestamp,
        "tool": "two-channel-validator",
        "file": args.file_path,
        "mode": args.mode,
    }

    try:
        if not is_in_scope(args.file_path):
            entry["status"] = "OUT-OF-SCOPE"
            log_audit(entry)
            if args.mode != "AUDIT":
                print(f"[two-channel-validator] OUT-OF-SCOPE: {args.file_path}")
            return 0

        if args.content_stdin:
            content = sys.stdin.read()
        elif os.path.exists(args.file_path):
            with open(args.file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        else:
            entry["status"] = "FILE_MISSING_PRE_WRITE"
            log_audit(entry)
            return 0

        fm = extract_frontmatter(content) or {}
        blocks = check_forbidden_formulas(content)
        warns = check_decision_effect_presence(fm, content)

        entry["blocks"] = [m for _, m in blocks]
        entry["warnings"] = [m for _, m in warns]

        if blocks:
            entry["status"] = "BLOCK"
            log_audit(entry)
            for _, msg in blocks:
                sys.stderr.write(f"[two-channel-validator] BLOCK {args.file_path}: {msg}\n")
            return 2 if args.mode == "ENFORCE" else 1

        if warns:
            entry["status"] = "WARN"
            log_audit(entry)
            for _, msg in warns:
                sys.stderr.write(f"[two-channel-validator] WARN {args.file_path}: {msg}\n")
            return 1 if args.mode == "ENFORCE" else 0

        entry["status"] = "OK"
        log_audit(entry)
        if args.mode != "AUDIT":
            print(f"[two-channel-validator] OK: keine Zwei-Kanal-Verletzung in {args.file_path}")
        return 0

    except Exception as e:
        entry["status"] = "ERROR"
        entry["error"] = str(e)
        log_audit(entry)
        sys.stderr.write(f"[two-channel-validator] ERROR: {e}\n")
        return 3


if __name__ == "__main__":
    sys.exit(main())
