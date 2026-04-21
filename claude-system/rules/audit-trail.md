# Audit-Trail [CRUX-MK]

Merged aus `action-logging.md` + `permission-audit.md` + `workflow-state.md` durch METAOPS 2026-04-18.
Drei parallele Log-Streams fuer Rueckabwickelbarkeit: Writes (action-log), Permissions (permission-log), Workflows (workflow-state).

## §1 Action-Log (Writes/Edits)

### PFLICHT nach JEDEM Write/Edit an wichtige Dateien

Nach Write oder Edit an folgenden Pfaden, schreibe 1 Zeile (append) in
`G:/Meine Ablage/Claude-Knowledge-System/branch-hub/audit/action-log.jsonl`:

**Wichtige Pfade (IMMER loggen):**
- SAE-v8/** (jede Code-Aenderung)
- branch-hub/** (jede Kommunikation)
- ~/.claude/rules/** (jede Regel-Aenderung)
- ~/.claude/settings.json (jede Config-Aenderung)
- ~/.claude/CLAUDE.md (jede Bootstrap-Aenderung)
- MEMORY.md (jede Memory-Aenderung)
- ~/.claude/scripts/** (jede Hook-Infrastruktur-Aenderung)

**Format:**
```
{"ts":"ISO","branch":"name","action":"WRITE|EDIT|DELETE","target":"pfad","reason":"kurz","source":"aufgabe"}
```

**NICHT loggen (Selbstexemption, CROSS-LLM-2OF3-HARDENED Grok+Codex 2026-04-19 P4):**
- Temporaere Dateien, Scratch-Arbeit
- Reine Lese-Operationen
- Explorative Suchen (Glob, Grep)
- **`branch-hub/audit/*.jsonl`** — sonst Log-Loop (Write an action-log.jsonl triggert action-log-Write fuer action-log-Write, infinite Rekursion)
- **`branch-hub/workflow-state/*.json`** — Self-Reference-Exemption aus gleichem Grund
- **Status-Touches** (`branch-hub/status/*-status.md` mit ausschliesslich Timestamp-Update ohne Content-Change) — Heartbeat-Metadaten sind nicht auditrelevant

**Warum Selbstexemption mechanisch noetig:** Pfad-Matcher `branch-hub/**` schliesst `branch-hub/audit/*.jsonl` syntaktisch ein. Ohne explizite NICHT-Loggen-Liste waere jeder action-log-Write ein audit-triggernder Write. Log-Loop ohne Termination.

## §2 Permission-Log (Tool-Berechtigungen)

### PFLICHT nach JEDER Permission-Entscheidung

Wenn Martin eine Tool-Nutzung genehmigt oder ablehnt, oder wenn settings.json eine automatische Erlaubnis erteilt:
1. Schreibe 1 Zeile (append) in `G:/Meine Ablage/Claude-Knowledge-System/branch-hub/audit/permission-log.jsonl`
2. Format: `{"ts":"ISO","branch":"name","tool":"Tool(pattern)","decision":"ALLOW|DENY|AUTO","by":"martin|settings","scope":"session|permanent"}`

### VOR einer Permission-Anfrage

Lies die letzten 20 Zeilen von permission-log.jsonl. Wenn Martin dieselbe Permission bereits in einer frueheren Session erlaubt hat: Erwaehne das ("Martin hat Bash(rm) am 2026-04-09 erlaubt"). Das spart Martin's Zeit.

### VERBOTENE Operationen (DENY immer, kein Override)

- `Bash(rm -rf /)` oder aehnliche rekursive Root-Loeschungen
- `Bash(git push --force main)` oder `--force master`
- Jede Operation die Credentials/Secrets exponiert

## §3 Workflow-State (Multi-Step-Fortschritt, CROSS-LLM-2OF3-HARDENED Grok+Codex 2026-04-19)

### PFLICHT nach jedem objektiven Workflow-Trigger

"Groesserer Arbeitsschritt" war subjektiv. Mechanische Trigger-Liste (JEDER Trigger → Update der workflow-state-Datei):

1. **Plan-Step abgeschlossen** (z.B. Todo-Item von in_progress → completed)
2. **Phase-Wechsel** (z.B. Mission-1 → Mission-2, Phase A → Phase B)
3. **Block/Unblock-Event** (externe Ressource wird verfuegbar / Blockade entsteht)
4. **Handoff-relevanter Write** (Artefakt das Nachfolger lesen muss: Finding, Decision-Card, Rule-Edit, Skill-Update)
5. **Session-Ende / /compact** (explizit)

Update-Inhalte: "step", "status", "checkpoint", "updated"
Bei Blockade: "blocked_on" mit Beschreibung + ISO-Zeitstempel

### Multi-Session-Ownership (Owner-oder-Lease)

Wenn mehrere Sessions denselben Branch-Namen bedienen (z.B. Fork-Session, Restart-Session):

**Owner-Regel (Default):** Ein Branch hat zu jedem Zeitpunkt **genau 1 Session als Owner** des workflow-state.json. Second Session detectiert Owner via:
```yaml
# In workflow-state/<branch>-state.json:
owner_session_id: "2d80f504-0b4b-49bf-bf8b-ced50ace099c"
owner_last_touch: "2026-04-19T09:30:00Z"
```

Wenn `owner_last_touch < now - 30 Min`: Owner-Lease expired. Neue Session darf Ownership uebernehmen (owner_session_id ueberschreiben + BEACON-Notiz).

Wenn `owner_last_touch >= now - 30 Min`: Neue Session forked → eigener Branch-Name oder wartet.

**Alternative Lease-Regel (fuer Hoch-Frequenz-Parallel):** TTL-basierter Lock (5 Min TTL), via `workflow-state/<branch>-lock.json`. Alle Sessions refreshen Lock alle 2 Min oder geben ab.

Fuer Arbitrierung bei Konflikt: **Verweis auf `parallel-session.md §2 Resolver-Kaskade`**.

### PFLICHT bei Session-Start (Bootstrap Level 0)

Lies `workflow-state/{dein-name}-state.json`. Wenn vorhanden:
- Setze dort fort wo die letzte Session aufgehoert hat
- NICHT von vorn anfangen wenn status="in_progress"
- Pruefe owner_last_touch → wenn > 30 Min alt: Ownership uebernehmen

### Format (erweitert)

```json
{
  "branch": "name",
  "task": "aufgabe",
  "phase": "phase_x",
  "step": "aktueller_schritt",
  "status": "in_progress|completed|blocked",
  "checkpoint": {"file": "pfad", "progress": "x/y"},
  "blocked_on": null,
  "updated": "ISO-timestamp",
  "owner_session_id": "uuid-of-claude-session",
  "owner_last_touch": "ISO-timestamp"
}
```

## §4 Zusammenwirken der 3 Logs

- **action-log.jsonl**: was wurde geschrieben? (Aenderungs-Historie)
- **permission-log.jsonl**: was durfte geschrieben werden? (Rechte-Historie)
- **workflow-state/{branch}.json**: wie weit war der Workflow? (Fortschritts-State)

Zusammen = vollstaendige Rueckabwickelbarkeit. "Wer hat wann was mit welcher Berechtigung in welcher Phase geschrieben."

### Beispiel-Korrelation bei Incident

1. Problem erkannt: `SAE-v8/core/governance.py` hat falschen Wert
2. action-log durchsuchen: welche Writes an dieser Datei?
3. permission-log korrelieren: war die Aktion autorisiert?
4. workflow-state pruefen: in welcher Phase / Step entstand die Aenderung?

Damit: Incident-Root-Cause-Analyse in Minuten statt Stunden.

## Zweck (uebergeordnet)

Der "Flugschreiber" des Branch-Systems. Bei Problemen rueckabwickelbar. Ohne Audit-Trail: Incidents sind undebugbar.

## SAE-Isomorphie

- **§1 Action-Log:** `AuditEntry` (frozen dataclass in `core/models.py`)
- **§2 Permission-Log:** `COSMOS Compliance-Layer` + `AuditEntry` fuer Branches
- **§3 Workflow-State:** `MYZ-32 Event-State-Tracker` fuer Branches
- **§4 Korrelation:** `Incident-Forensik` (SAE: `incident_response.py`)

## SUPERSEDED Predecessors (2026-04-18)

Diese Datei ersetzt:
- `action-logging.md` (§1 Writes, unveraendert subsumiert)
- `permission-audit.md` (§2 Permissions, unveraendert subsumiert)
- `workflow-state.md` (§3 Workflow, unveraendert subsumiert)

Neu in diesem Merge: **§4 Zusammenwirken** — die drei Logs waren vorher implizit korreliert, jetzt explizit dokumentiert als einheitlicher Audit-Trail.

[CRUX-MK]
