# SUPERSEDED — Lies stattdessen: rules/audit-trail.md [CRUX-MK]
# WARNUNG: Dieses Dokument ist veraltet seit 2026-04-18 (METAOPS Mission-2).
# Aktuelle Version: ~/.claude/rules/audit-trail.md §3 (unveraendert subsumiert).

# Workflow State Regel [CRUX-MK] (ARCHIV)

## PFLICHT bei jedem groesseren Arbeitsschritt

Nach Abschluss eines Arbeitsschritts (Adapter implementiert, Wargame fertig, Datei erstellt):
1. Aktualisiere `G:/Meine Ablage/Claude-Knowledge-System/branch-hub/workflow-state/{dein-branch-name}-state.json`
2. Setze "step", "status", "checkpoint", "updated"
3. Bei Blockade: Setze "blocked_on" mit Beschreibung

## PFLICHT bei Session-Start (Bootstrap Level 0)
Lies `workflow-state/{dein-name}-state.json`. Wenn vorhanden:
- Setze dort fort wo die letzte Session aufgehoert hat
- NICHT von vorn anfangen wenn status="in_progress"

## Format
```json
{
  "branch": "name",
  "task": "aufgabe",
  "phase": "phase_x",
  "step": "aktueller_schritt",
  "status": "in_progress|completed|blocked",
  "checkpoint": {"file": "pfad", "progress": "x/y"},
  "blocked_on": null,
  "updated": "ISO-timestamp"
}
```

## SAE-Isomorphie
Dies ist MYZ-32 (Event-State-Tracker) fuer Branches.
