---
description: Schreibt maschinenlesbaren JSON-Snapshot der Session in branch-hub/snapshots/
trigger: Vor Session-Ende, vor /compact, bei /snapshot
crux-mk: true
---

# /snapshot [CRUX-MK]

## Wann aufrufen
- VOR jedem Session-Ende (PFLICHT)
- VOR /compact
- Bei Martin's Anfrage

## Schritte
1. Bestimme Branch-Name und Datum
2. Schreibe `G:/Meine Ablage/Claude-Knowledge-System/branch-hub/snapshots/{branch}-{YYYY-MM-DD}.json`:

```json
{
  "branch": "{name}",
  "date": "{YYYY-MM-DD}",
  "context_fill_pct": {geschaetzt},
  "bootstrap_level": "{0|1|2|3}",
  "session_duration_hours": {geschaetzt},
  "loaded_files": ["{liste der gelesenen Dateien}"],
  "api_knowledge": {
    "{system}": {"auth": "...", "rate_limit": "...", "key_endpoints": ["..."]}
  },
  "decisions_made": ["{liste der Entscheidungen}"],
  "findings_written": ["{liste der Findings}"],
  "open_items": ["{was noch offen ist}"],
  "workflow_state": "{verweis auf workflow-state/{branch}-state.json}",
  "warnings": ["{Probleme die aufgetreten sind}"],
  "next_session_should": ["{was die naechste Session zuerst tun muss}"]
}
```

3. Dieser Snapshot ist MASCHINENLESBAR -- die naechste Session kann ihn parsen statt Prosa-Handoff zu interpretieren.

## Unterschied zu Knowledge-Diff
- Knowledge-Diff = WAS GELERNT (Prosa, fuer Menschen)
- Session-Snapshot = SYSTEMZUSTAND (JSON, fuer Maschinen)
- BEIDE schreiben. Nicht entweder-oder.

## SAE-Isomorphie
Dies ist Event.to_json() + Agent State Persistence fuer Branches.
