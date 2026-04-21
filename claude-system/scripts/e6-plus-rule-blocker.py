#!/usr/bin/env python3
"""
E6+-Rule-Blocker Pre-Write-Hook [CRUX-MK]

Blockiert/Warnt Writes zu neuen Rule-Dateien in ~/.claude/rules/ mit Namen `meta-e[6-99]-*.md`
ohne ausreichende Irreduzibilitaets-Begruendung.

Hintergrund: FIXPUNKT-4 sagt "5 ist operativer Cutoff". E6+ sind nur zulaessig bei
nachweisbarer irreduzibler Semantik (nicht auf E5 reduzierbar). Cross-LLM-Run #4 hat
legitime E6-Kandidaten benannt (Governance, Interop, Utility, Ethisch-teleologisch,
formale Verifikation). Fuer jede neue E6+-Rule: Irreduzibilitaets-Nachweis Pflicht.

Author: Opus 4.7 METAOPS, 2026-04-18
Mission-1, Hook-3 von 4
Rules: meta-stack-fixpunkte.md FIXPUNKT-4 (Endlichkeit der Meta-Stacks)

Scope (Pflicht):
- ~/.claude/rules/meta-e[6-9]-*.md  (einstellig 6-9)
- ~/.claude/rules/meta-e[1-9][0-9]-*.md (zweistellig 10-99)

Check:
- Frontmatter MUSS Feld `e6-justification: "<text>"` oder `e-level-justification: "<text>"` haben
- Text >= 100 Zeichen (sonst WARN)
- Bonus: MUSS mindestens eine der 5 legitimen Kategorien erwaehnen
  (Governance, Interoperabilitaet, Nutzen/Kosten, Ethisch, Verifikation)

Exit-Codes:
    0 = OK / OUT-OF-SCOPE
    1 = WARN
    2 = BLOCK (ENFORCE-mode)

Usage:
    python e6-plus-rule-blocker.py <file-path> [--content-stdin] [--mode=CHECK|ENFORCE|AUDIT]
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime
from pathlib import Path

SCOPE_REGEX = re.compile(r"\.claude[/\\]rules[/\\]meta-e([6-9]|[1-9][0-9])-[\w\-]+\.md$", re.IGNORECASE)

# v2 METAD2 (2026-04-19): Auf Basis 4-Iter-Test (Codex+Gemini+Copilot, 8 Frames):
# Nur 3 Domaenen halten als echtes E6 stand. K2 Interop und K5 Verifikation sind
# 3/3 STABIL E5 ueber alle Iterationen — diese werden NICHT mehr als legitime E6-Domaenen
# anerkannt. Bei E6+ mit "interoperabilitaet" oder "verifikation" als einziger Begruendung
# WARN (vermutlich Meta-Inflation).

LEGITIMATE_CATEGORIES = [
    # 3 echte E6-Domaenen (3/3-Konsens nach Iter-Test 2026-04-19):
    "werte",            # Werte-Setzung (ex K3 Nutzen revidiert via Codex-Kippung)
    "wert",
    "telos",
    "teleolog",         # ethisch-teleologisch (K4)
    "ethik",
    "ethisch",
    "nutzen",           # Nutzen-Definition (nicht Optimierung)
    "verfassung",       # Verfassungs-Setzung (Konstitution > Konstituiertes, K1 split-Lesart)
    "konstitution",
    "konstituier",
    "pouvoir constituant",
]

# v2 RETIRED (3/3 Konsens E5-stabil, KEINE legitime E6-Domaene mehr):
RETIRED_CATEGORIES = [
    "interoperab",  # Stack-Vergleich = Engineering-Mapping
    "verifikation",  # Verifikations-Akt = E5-Vollzug. Letztbegruendung waere E6 (siehe ethisch/verfassung)
    "formal",        # Formale Verifikation alleine reicht nicht
]

MIN_JUSTIFICATION_LENGTH = 100

# v2 METAD2: E6+ verlangt explizites Martin-Approval-Frontmatter
MARTIN_APPROVAL_KEY = "martin-approval"

AUDIT_LOG = Path("G:/Meine Ablage/Claude-Knowledge-System/branch-hub/audit/e6-plus-rule-blocker.jsonl")


def is_in_scope(file_path: str) -> tuple[bool, int | None]:
    """Returns (in_scope, e_level)"""
    norm = file_path.replace("\\", "/")
    m = SCOPE_REGEX.search(norm)
    if not m:
        return False, None
    e_level = int(m.group(1))
    return True, e_level


def extract_frontmatter(content: str) -> dict | None:
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 4)
    if end == -1:
        return None
    fm_text = content[4:end]
    fm = {}
    current_key = None
    for line in fm_text.split("\n"):
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            key, _, value = line.partition(":")
            current_key = key.strip()
            fm[current_key] = value.strip()
        elif current_key and (line.startswith(" ") or line.startswith("\t")):
            fm[current_key] = fm.get(current_key, "") + " " + line.strip()
    return fm


def validate_justification(fm: dict) -> tuple[str, str]:
    """v2 METAD2 (2026-04-19): erweitert um RETIRED-Detection + Martin-Approval-Pflicht.
    Returns (status, message)"""
    justification = fm.get("e6-justification") or fm.get("e-level-justification") or ""
    justification = justification.strip().strip("\"'")

    if not justification:
        return "BLOCK", "E6+ Rule ohne e6-justification/e-level-justification-Frontmatter (FIXPUNKT-4 Irreduzibilitaet-Pflicht)"

    if len(justification) < MIN_JUSTIFICATION_LENGTH:
        return "WARN", f"Justification nur {len(justification)} Zeichen (>= {MIN_JUSTIFICATION_LENGTH} empfohlen). Nenne die irreduzible Semantik konkret."

    justification_lower = justification.lower()
    matched_legit = [c for c in LEGITIMATE_CATEGORIES if c in justification_lower]
    matched_retired = [c for c in RETIRED_CATEGORIES if c in justification_lower]

    if not matched_legit and matched_retired:
        return "BLOCK", (
            f"Justification nennt nur RETIRED-Kategorien {matched_retired} "
            f"(durch METAD2-Iter-Test 2026-04-19 als E5-stabil erwiesen). "
            f"Echte E6-Domaenen: Werte/Telos/Verfassung. Re-Klassifizieren als E5."
        )

    if not matched_legit:
        return "WARN", (
            f"Justification nennt keine der legitimen E6-Domaenen "
            f"(Werte/Telos/Verfassung — siehe rules/meta-stack-fixpunkte.md FIXPUNKT-4). "
            f"Re-pruefen ob wirklich E6+ oder E5-reduzibel."
        )

    # v2 Martin-Approval-Check (K_0-naehe bei Verfassungs-Setzung, Q_0 bei Werte-Setzung)
    martin_approval = fm.get(MARTIN_APPROVAL_KEY, "").strip().strip("\"'")
    if not martin_approval:
        return "WARN", (
            f"E6+ Rule mit Domaene {matched_legit} ohne {MARTIN_APPROVAL_KEY}-Frontmatter. "
            f"E6 = Werte/Telos/Verfassung = K_0/Q_0-naehe = L13 Martin-Phronesis-Pflicht. "
            f"Frontmatter-Feld erforderlich: {MARTIN_APPROVAL_KEY}: <YYYY-MM-DD oder approval-id>"
        )

    return "OK", f"Justification OK ({len(justification)} Zeichen, Domaenen: {','.join(matched_legit)}, approved: {martin_approval})"


def log_audit(entry: dict):
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        sys.stderr.write(f"[e6-plus-blocker] Audit-Log failed: {e}\n")


def main():
    parser = argparse.ArgumentParser(description="E6+ Rule Blocker [CRUX-MK]")
    parser.add_argument("file_path")
    parser.add_argument("--content-stdin", action="store_true")
    parser.add_argument("--mode", default="CHECK", choices=["CHECK", "ENFORCE", "AUDIT"])
    args = parser.parse_args()

    timestamp = datetime.now().isoformat()
    entry = {
        "ts": timestamp,
        "tool": "e6-plus-rule-blocker",
        "file": args.file_path,
        "mode": args.mode,
    }

    try:
        in_scope, e_level = is_in_scope(args.file_path)
        if not in_scope:
            entry["status"] = "OUT-OF-SCOPE"
            log_audit(entry)
            if args.mode != "AUDIT":
                print(f"[e6-plus-blocker] OUT-OF-SCOPE: {args.file_path}")
            return 0

        entry["e_level"] = e_level

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
        status, message = validate_justification(fm)
        entry["status"] = status
        entry["message"] = message
        log_audit(entry)

        if status == "OK":
            if args.mode != "AUDIT":
                print(f"[e6-plus-blocker] OK (E{e_level}-Rule mit Justification): {message}")
            return 0
        elif status == "WARN":
            sys.stderr.write(f"[e6-plus-blocker] WARN E{e_level}-Rule {args.file_path}: {message}\n")
            return 1 if args.mode == "ENFORCE" else 0
        else:
            sys.stderr.write(f"[e6-plus-blocker] BLOCK E{e_level}-Rule {args.file_path}: {message}\n")
            return 2 if args.mode == "ENFORCE" else 1

    except Exception as e:
        entry["status"] = "ERROR"
        entry["error"] = str(e)
        log_audit(entry)
        sys.stderr.write(f"[e6-plus-blocker] ERROR: {e}\n")
        return 3


if __name__ == "__main__":
    sys.exit(main())
