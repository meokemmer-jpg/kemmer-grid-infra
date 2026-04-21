# SUPERSEDED — Lies stattdessen: rules/audit-trail.md [CRUX-MK]
# WARNUNG: Dieses Dokument ist veraltet seit 2026-04-18 (METAOPS Mission-2).
# Aktuelle Version: ~/.claude/rules/audit-trail.md §2 (unveraendert subsumiert).

# Permission Audit Trail [CRUX-MK] (ARCHIV)

## PFLICHT nach JEDER Permission-Entscheidung

Wenn Martin eine Tool-Nutzung genehmigt oder ablehnt, oder wenn settings.json eine automatische Erlaubnis erteilt:
1. Schreibe 1 Zeile (append) in `G:/Meine Ablage/Claude-Knowledge-System/branch-hub/audit/permission-log.jsonl`
2. Format: `{"ts":"ISO","branch":"name","tool":"Tool(pattern)","decision":"ALLOW|DENY|AUTO","by":"martin|settings","scope":"session|permanent"}`

## VOR einer Permission-Anfrage
Lies die letzten 20 Zeilen von permission-log.jsonl. Wenn Martin dieselbe Permission bereits in einer frueheren Session erlaubt hat: Erwaehne das ("Martin hat Bash(rm) am 2026-04-09 erlaubt"). Das spart Martin's Zeit.

## VERBOTENE Operationen (DENY immer, kein Override)
- `Bash(rm -rf /)` oder aehnliche rekursive Root-Loeschungen
- `Bash(git push --force main)` oder `--force master`
- Jede Operation die Credentials/Secrets exponiert

## SAE-Isomorphie
Dies ist COSMOS Compliance-Layer + AuditEntry fuer Branches.
