---
description: Schreibt persistenten Workflow-Checkpoint in branch-hub/workflow-state/
trigger: Nach jedem groesseren Arbeitsschritt oder bei /checkpoint
crux-mk: true
---

# /checkpoint [CRUX-MK]

## Schritte
1. Bestimme deinen Branch-Namen (aus REGISTRY.md oder Session-Kontext)
2. Schreibe/Aktualisiere `G:/Meine Ablage/Claude-Knowledge-System/branch-hub/workflow-state/{branch}-state.json`:
   ```json
   {
     "branch": "{name}",
     "task": "{aktuelle Hauptaufgabe}",
     "phase": "{phase}",
     "step": "{aktueller Schritt}",
     "status": "in_progress|completed|blocked",
     "checkpoint": {
       "file": "{letzte bearbeitete Datei}",
       "progress": "{Fortschritt}",
       "tests": {"written": 0, "passing": 0}
     },
     "blocked_on": null,
     "updated": "{ISO-timestamp}"
   }
   ```
3. Wenn TASK-BOARD.md existiert: Aktualisiere den entsprechenden Eintrag

## Wann aufrufen
- Nach jeder abgeschlossenen Phase/Aufgabe
- Vor /compact
- Vor Session-Ende
- Bei Blockade
