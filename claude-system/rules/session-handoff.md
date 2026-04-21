---
description: Vector Space Disjunction -- Session-Handoff-Regel fuer ALLE Fenster
globs: "**/*"
---

# Session-Handoff-Regel (Vector Space Disjunction)

**Mathematisch bewiesen:** I(C_A; y_{t+k}) → 0
Session-Handoffs (--continue, --resume, /compact, Kontextwechsel) sind LOSSY.

## PFLICHT bei jeder Session / jedem /compact / jedem Kontextwechsel:
1. Kritische Entscheidungen + Begruendungen in DATEIEN schreiben
2. Memory-Dateien aktualisieren (MEMORY.md + spezifische .md)
3. Todos/Offene Punkte in persistente Dateien sichern
4. [CRUX-MK] Marker in allen persistenten Dateien verankern
5. NotebookLM als externe Wissensbasis nutzen (kein KV-Cache-Verlust)
6. Wargame-Ergebnisse (Findings, Cards) IMMER als Dateien speichern

## Hierarchie
- Shared-KV-Cache = lossless (gleiche Session, kein Wechsel)
- Same-Provider, neue Session = LOSSY (--continue verliert Context)
- Cross-Provider = IMPOSSIBLE (verschiedene Repraesentationen)

## Konsequenz
Vertraue NICHT dem Context. Vertraue Dateien.
Was nicht in einer Datei steht, existiert nach dem naechsten /compact NICHT MEHR.
