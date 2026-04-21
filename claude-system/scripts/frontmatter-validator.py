#!/usr/bin/env python3
"""
Frontmatter-Validator Pre-Write-Hook [CRUX-MK]

Prueft dass Canon-Writes ein gueltiges `meta-ebene: E1|E2|E3|E4|E5` Frontmatter-Feld haben.

Author: Opus 4.7 METAOPS, 2026-04-18
Mission-1, Hook-1 von 4
Rules: meta-stack-fixpunkte.md FIXPUNKT-1 + meta-governance-framework.md G11

Modi:
- CHECK (default): nur loggt, blockiert nicht
- ENFORCE: blockiert Writes die Pflicht verletzen
- AUDIT: loggt ohne stdout-Output

Canon-Pfade (Pflicht):
- Claude-Vault/areas/family/Subnautica-Fragment-Map*
- Claude-Vault/docs/decision-cards/
- branch-hub/findings/FINDING-*
- branch-hub/cross-llm/
- Claude-Vault/resources/mathe/B*-*
- Claude-Vault/00-moc/MOC-*

Ausnahmen (kein meta-ebene noetig):
- *.jsonl, *.log, *.sh, *.ps1, *.py, *.txt, *.yaml, *.yml, *.json (keine Canon-Files)
- branch-hub/audit/*
- branch-hub/status/*
- branch-hub/inbox/*
- CLAUDE.md, MEMORY.md, BEACON.md, REGISTRY.md, BULLETIN.md (Meta-Files)
- README.md (Orientierungs-Files)

Usage:
    python frontmatter-validator.py <file-path> [--content-stdin] [--mode=CHECK|ENFORCE|AUDIT]

Exit-Codes:
    0 = OK (pass-through)
    1 = WARN (missing meta-ebene aber Canon-Pfad)
    2 = BLOCK (invalid meta-ebene Wert)
    3 = ERROR (script-internal)

Audit-Log:
    Anhang an G:/Meine Ablage/Claude-Knowledge-System/branch-hub/audit/frontmatter-validator.jsonl
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime
from pathlib import Path

VALID_EBENEN = {"E1", "E2", "E3", "E4", "E5"}

CANON_PATTERNS = [
    r"Claude-Vault[/\\]areas[/\\]family[/\\]Subnautica-Fragment-Map",
    # decision-cards/ entfernt aus Pflicht-Scope (METAD2 Phase-2 2026-04-18):
    # 84% der bestehenden DCs nutzen eigenes Schema ohne meta-ebene-Key.
    # WARN-Volumen war kein echter Defekt sondern Schema-Mismatch.
    # Falls Schema-Migration spaeter durchgefuehrt: Pattern wieder aktivieren.
    # r"Claude-Vault[/\\]docs[/\\]decision-cards[/\\]",
    r"branch-hub[/\\]findings[/\\]FINDING-",
    r"branch-hub[/\\]cross-llm[/\\]",
    r"Claude-Vault[/\\]resources[/\\]mathe[/\\]B\d+-",
    r"Claude-Vault[/\\]00-moc[/\\]MOC-",
]

EXEMPT_EXTENSIONS = {".jsonl", ".log", ".sh", ".ps1", ".py", ".txt", ".yaml", ".yml", ".json"}
EXEMPT_NAMES = {"CLAUDE.md", "MEMORY.md", "BEACON.md", "REGISTRY.md", "BULLETIN.md", "README.md"}
EXEMPT_PATH_PATTERNS = [
    r"branch-hub[/\\]audit[/\\]",
    r"branch-hub[/\\]status[/\\]",
    r"branch-hub[/\\]inbox[/\\]",
    r"memory[/\\]session_",
    r"\.claude[/\\]scripts[/\\]",
    r"\.claude[/\\]rules[/\\]",
    r"\.claude[/\\]skills[/\\]",
]

AUDIT_LOG = Path("G:/Meine Ablage/Claude-Knowledge-System/branch-hub/audit/frontmatter-validator.jsonl")


def is_canon_path(file_path: str) -> bool:
    norm = file_path.replace("\\", "/")
    for pattern in CANON_PATTERNS:
        if re.search(pattern, norm, re.IGNORECASE):
            return True
    return False


def is_exempt(file_path: str) -> bool:
    p = Path(file_path)
    if p.suffix.lower() in EXEMPT_EXTENSIONS:
        return True
    if p.name in EXEMPT_NAMES:
        return True
    norm = file_path.replace("\\", "/")
    for pattern in EXEMPT_PATH_PATTERNS:
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


def validate_meta_ebene(fm: dict) -> tuple[str, str]:
    """Returns (status, message). status: OK|WARN|BLOCK

    v2 (METAD2 Mission-1b 2026-04-18): Praefix-Tolerance.
    Real-World-Test zeigte: Authors schreiben `meta-ebene: E1 (Empirisch)`,
    `meta-ebene: E4 - Audit-Audit`, etc. — Annotation darf nicht BLOCK ausloesen,
    solange der Wert mit E1-E5 BEGINNT.
    """
    if "meta-ebene" not in fm:
        return "WARN", "Canon-File fehlt meta-ebene-Key (Pflicht fuer FIXPUNKT-1)"
    val = fm["meta-ebene"].strip().strip("\"'")
    if not val:
        return "WARN", "meta-ebene-Key vorhanden aber leer"
    # Praefix-Match: erlaubte Werte beginnen mit E1-E5, optional gefolgt von Trennzeichen + Annotation
    m = re.match(r"^(E[1-5])\b", val)
    if not m:
        return "BLOCK", f"meta-ebene-Wert '{val[:60]}' beginnt nicht mit E1-E5"
    ebene = m.group(1)
    if val == ebene:
        return "OK", f"meta-ebene={ebene}"
    else:
        return "OK", f"meta-ebene={ebene} (annotation: '{val[:50]}')"


def log_audit(entry: dict):
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        sys.stderr.write(f"[frontmatter-validator] Audit-Log failed: {e}\n")


def main():
    parser = argparse.ArgumentParser(description="Frontmatter-Validator Pre-Write-Hook [CRUX-MK]")
    parser.add_argument("file_path")
    parser.add_argument("--content-stdin", action="store_true", help="Read content from stdin")
    parser.add_argument("--mode", default="CHECK", choices=["CHECK", "ENFORCE", "AUDIT"])
    args = parser.parse_args()

    timestamp = datetime.now().isoformat()
    entry = {
        "ts": timestamp,
        "tool": "frontmatter-validator",
        "file": args.file_path,
        "mode": args.mode,
    }

    try:
        if is_exempt(args.file_path):
            entry["status"] = "EXEMPT"
            entry["reason"] = "Extension/Pfad in Ausnahme-Liste"
            log_audit(entry)
            if args.mode != "AUDIT":
                print(f"[frontmatter-validator] EXEMPT: {args.file_path}")
            return 0

        if not is_canon_path(args.file_path):
            entry["status"] = "NON-CANON"
            log_audit(entry)
            if args.mode != "AUDIT":
                print(f"[frontmatter-validator] NON-CANON (keine Pflicht): {args.file_path}")
            return 0

        # Canon-Pfad: Frontmatter-Pflicht
        if args.content_stdin:
            content = sys.stdin.read()
        elif os.path.exists(args.file_path):
            with open(args.file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        else:
            entry["status"] = "FILE_MISSING_PRE_WRITE"
            log_audit(entry)
            return 0  # Pre-Write: File existiert noch nicht, skip (Content kommt mit Write)

        fm = extract_frontmatter(content)
        if fm is None:
            entry["status"] = "NO_FRONTMATTER"
            entry["canon_path"] = True
            log_audit(entry)
            msg = f"[frontmatter-validator] WARN {args.file_path}: Canon-File ohne Frontmatter"
            if args.mode == "ENFORCE":
                sys.stderr.write(msg + " (BLOCKED in ENFORCE-mode)\n")
                return 2
            else:
                sys.stderr.write(msg + "\n")
                return 1

        status, message = validate_meta_ebene(fm)
        entry["status"] = status
        entry["message"] = message
        log_audit(entry)

        if status == "OK":
            if args.mode != "AUDIT":
                print(f"[frontmatter-validator] OK: {message}")
            return 0
        elif status == "WARN":
            sys.stderr.write(f"[frontmatter-validator] WARN {args.file_path}: {message}\n")
            return 1 if args.mode == "ENFORCE" else 0
        else:  # BLOCK
            sys.stderr.write(f"[frontmatter-validator] BLOCK {args.file_path}: {message}\n")
            return 2 if args.mode == "ENFORCE" else 1

    except Exception as e:
        entry["status"] = "ERROR"
        entry["error"] = str(e)
        log_audit(entry)
        sys.stderr.write(f"[frontmatter-validator] ERROR: {e}\n")
        return 3


if __name__ == "__main__":
    sys.exit(main())
