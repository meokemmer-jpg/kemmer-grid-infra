# SUPERSEDED — Lies stattdessen: rules/audit-trail.md [CRUX-MK]
# WARNUNG: Dieses Dokument ist veraltet seit 2026-04-18 (METAOPS Mission-2).
# Aktuelle Version: ~/.claude/rules/audit-trail.md §1 (unveraendert subsumiert).

# Action Logging [CRUX-MK] (ARCHIV)

## PFLICHT nach JEDEM Write/Edit an wichtige Dateien

Nach Write oder Edit an folgenden Pfaden, schreibe 1 Zeile (append) in
`G:/Meine Ablage/Claude-Knowledge-System/branch-hub/audit/action-log.jsonl`:

### Wichtige Pfade (IMMER loggen):
- SAE-v8/** (jede Code-Aenderung)
- branch-hub/** (jede Kommunikation)
- ~/.claude/rules/** (jede Regel-Aenderung)
- ~/.claude/settings.json (jede Config-Aenderung)
- ~/.claude/CLAUDE.md (jede Bootstrap-Aenderung)
- MEMORY.md (jede Memory-Aenderung)

### Format:
`{"ts":"ISO","branch":"name","action":"WRITE|EDIT|DELETE","target":"pfad","reason":"kurz","source":"aufgabe"}`

### NICHT loggen:
- Temporaere Dateien, Scratch-Arbeit
- Reine Lese-Operationen
- Explorative Suchen (Glob, Grep)

## Zweck
Der "Flugschreiber" des Branch-Systems. Bei Problemen rueckabwickelbar.
SAE-Isomorphie: AuditEntry (frozen dataclass in core/models.py).
