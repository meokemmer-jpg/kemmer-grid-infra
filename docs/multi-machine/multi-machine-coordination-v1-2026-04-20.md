---
type: coordination-blueprint
version: v1.0
date: 2026-04-20
from: Opus47-Work-D2 (PC 1 Primary)
to: all (existing + future Physical Machines)
scope: Multi-Machine-Skalierung Kemmer-System
crux-mk: true
---

# Multi-Machine Coordination Blueprint v1.0 [CRUX-MK]

Zentrale Steuerungs-Referenz fuer 1-4 Physical Machines + Mac-Gemma4-Server.
Ergaenzt `rules/parallel-session.md` (Multi-Branch-auf-gleicher-Machine) um **Cross-Machine**-Dimension.

## Machine-Inventar (Stand 2026-04-20)

| Machine | Rolle | Branch-Lane-Prefix | Scheduled-Tasks | Git-Push | NLM-Login |
|---------|-------|--------------------|-----------------|----------|-----------|
| **PC 1 (Martin-Primary)** | MASTER | alle existing (F1-F899) | ALLE (DF-05/06/07/08/10, vault-hub-sync, activity-stats) | `main` push-Recht (Shadow-Mode) | aktiv |
| **PC 2** | WORKER-E | F900-F999 + B550-B599 | **KEINE** | nur Feature-Branches | **kein Login** (Vault-Spiegel nutzen) |
| **PC 3** | WORKER-F | F1000-F1099 + B600-B649 | **KEINE** | nur Feature-Branches | **kein Login** |
| **PC 4** | WORKER-G | F1100-F1199 + B650-B699 | **KEINE** | nur Feature-Branches | **kein Login** |
| **Mac** | LLM-SERVER | n/a | n/a | n/a | n/a |

## Kernregeln (MUST)

### MR-1 Master-Singleton
Scheduled-Tasks mit Prefix `DF-`, `NLM-`, `Claude-`, `Vault-` sind **ausschliesslich auf PC 1 Master**. Worker-PC hat diese Prefixes **deaktiviert/leer**. Durchsetzung via Bootstrap-Pre-Flight-Check (`schtasks /query`).

### MR-2 Instanz-Workspace-Pflicht
Jeder Worker-PC hat eigenen Workspace: `Claude-Vault/areas/family/instance-<branch-name>-pc<N>/`. WIP-Writes, Drafts, Session-Reports dort. Canon-Dateien nur mit Lock.

### MR-3 BEACON-Lock via Heartbeat
Vor BEACON-Write: alle `branch-hub/status/*-status.md` Modification-Time pruefen. Wenn anderer Worker < 5 Min aktiv: **warten oder Inbox-Nachricht statt BEACON**. Siehe `rules/parallel-session.md §4`.

### MR-4 Push-Rechte
- `main`: nur PC 1 (Master). Worker **nie** `git push origin main`.
- Feature-Branches: jeder PC kann `gh pr create`. Master-Review + Merge erforderlich.
- `git push --force*`: verboten fuer alle (ausser Martin explizit).

### MR-5 Rules-Konsistenz
`~/.claude/rules/` muss auf allen PCs **hash-identisch** sein. Sync via GitHub. Divergenz = Incident (action-log).

### MR-6 Settings-Lokal
`~/.claude/settings.json` kann PC-spezifisch sein (MCP-Hosts, Keys), aber **Hooks + Rules-Loader + MCP-Server-Liste muessen hash-identisch**. Divergenz = `settings.local.json` (bereits Claude-Code-Konvention).

### MR-7 NLM-Single-Login
NotebookLM hat 1 Session/Google-Account. **Nur PC 1 hat Login**. Worker lesen `Claude-Vault/resources/_from-nlm/` (vollstaendiger Spiegel, taeglich aktualisiert durch DF-06).

### MR-8 Cross-PC-Inbox
Kommunikation zwischen PCs: `branch-hub/inbox/to-<branch>-pc<N>.md`. Keine Direct-Writes in fremde Status-Files.

## Soft-Guidelines (SHOULD)

### SG-1 Task-Portfolio-Split
- PC 1: Strategie, Phronesis, K_0/Q_0, Rules, Master-Koordination
- PC 2: Delegate-Heavy (Copilot/Codex/Gemini-Parallel), Rule-Audit, Knowledge-Janitor
- PC 3: Meta-Audit, Monthly-Reports, Seed-Updates
- PC 4: Docs, Wargames, Pattern-Scans

Pull via META-ROADMAP IDLE-PRIO. WIP-Marker setzen. Nach Abschluss ABGESCHLOSSEN.

### SG-2 Handoff-Schreiben alle 4h oder bei Context >70%
Pre-Compact-Write-Zwang (M9 aus `branch-hub/canon/antifragile-crash-structure-v1.0`) gilt auch Cross-Machine. Siehe `branch-hub/learnings/crash-reports/2026-04-19-work-d2-compact-data-loss.md`.

### SG-3 Gemma4-Preferenz fuer Routine
Wenn Mac-Gemma4 erreichbar: Routine-Tasks (Klassifikation, Summarization kurz, Boilerplate) via Gemma4 statt Opus. Endpoint-Check vor Nutzung:
```bash
curl -s http://<mac-ip>:11434/v1/models | head -20
```

## Anti-Pattern (MUST NOT)

- **AP-1:** Worker aktiviert DF-* Scheduled-Task → NLM-Quota-Kollision
- **AP-2:** Worker pushed `main` → non-ff-Konflikt + Rule-Divergenz
- **AP-3:** 2 PCs schreiben parallel selbe Canon-Datei → Drive-Sync-Duplikat-Kaskade
- **AP-4:** Worker aendert `~/.claude/rules/` ohne Git-Commit + Push → Cross-PC-Divergenz
- **AP-5:** Worker loggt in NLM ein → PC 1 Session-Expire
- **AP-6:** Mac rollt neues Gemma4-Modell ohne Endpoint-Kompatibilitaet-Check → Skill-Failures auf allen PCs

## Onboarding-Checkliste neue PC

- [ ] Drive-G verfuegbar
- [ ] Claude Code v2.0+ installiert
- [ ] CLIs installiert (codex/gemini/copilot/gh/git/python)
- [ ] Env-Vars gesetzt (GEMINI_API_KEY Pflicht)
- [ ] Scheduled-Tasks dieser PC LEER (DF-*/NLM-*/Claude-*/Vault-*)
- [ ] Seed-Import aus GitHub
- [ ] Branch-Name gewaehlt (Work-E/F/G-PC<N>)
- [ ] Lane reserviert in REGISTRY
- [ ] Instanz-Workspace angelegt
- [ ] status-Datei initialisiert
- [ ] BEACON-1-Liner appended (mit Lock-Check)
- [ ] META-ROADMAP Idle-Loop verstanden (PFLICHT-Read)
- [ ] Erstes IL-Item gepullt

## Beziehung zu existierenden Rules

- **Ergaenzt `rules/parallel-session.md`** (bisher nur same-machine Multi-Branch)
- **Ergaenzt `rules/drive-sync-mitigation.md`** (jetzt mit Machine-Boundary)
- **Ergaenzt `rules/agent-types.md`** (Master/Worker-Dichotomie neu)
- **Nutzt `rules/token-engpass-hierarchie.md`** (Gemma4 wird neue Stufe 3 zwischen Opus und Flat)

## Beziehung zu existierenden Findings

- `FINDING-DRIVE-SYNC-CHAOS-2026-04-18.md` — primaere Gefahrenquelle
- `FINDING-DF06-V2-CROSS-LLM-HARDENING-2026-04-19.md` — DF-06 Architektur
- `FINDING-TOKEN-EFFICIENCY-PATTERN-MYZ-2026-04-19.md` — Multi-Subagent-Pattern (uebertragbar auf Multi-Machine)
- `CR-2026-04-19-001` — Crash-Report (Lesson fuer Pre-Compact-Write-Zwang auch Cross-Machine)

## ⚠️ rho-Prognose KORRIGIERT (2026-04-20, Wargame-Ergebnis)

**Ursprueng. Blueprint-Wert:** +18k-54k EUR/J Multi-Machine-allein (zu optimistisch, "hebel"-Annahme ungepruef).
**Korrigiert nach Wargame Claude-Multi-Machine-Hebel** (`branch-hub/findings/WARGAME-CLAUDE-MULTI-MACHINE-HEBEL-2026-04-20.md`):

- Multi-Machine allein (ohne Grid): **+10k-24k EUR/J** unter 3 Bedingungen (Worker=Delegate-Orchestrator, max 2 Worker bis Git-Backend, Koordinations-Automatisierung)
- **KRITISCH:** Anthropic Rate-Limits sind per-account, nicht per-machine → Claude-Opus-Hebel ist Illusion. Nur Delegate-LLMs (Codex/Gemini/Grok/Copilot) werden parallelisiert

**Vollausbau erst wenn Multi-Machine + Low-Cost AI Grid kombiniert** (siehe `WARGAME-LOW-COST-AI-GRID-2026-04-20.md`):
- Phase 1 (Mac + 1 Worker): +€500-1500/Mo
- Phase 2 (Mac + GPU + 2 Worker): +€1500-3000/Mo
- Phase 3 (Grid-Full + 4 Worker): +€2500-5000/Mo = **+30k-60k EUR/J (Vollausbau)**

**Phased Commitment empfohlen**, kein Full-Commit auf 4 PCs + Grid upfront.

## Aktivierung

**Shadow-Mode (jetzt):** PC 2 Boot als Test. Blueprint dokumentiert aber Rule-Status `.PROPOSAL`.

**Nach 3 erfolgreichen PC 2 Sessions (kein Drive-Conflict, keine Scheduled-Task-Duplikation):** Martin-Approval → `rules/multi-machine-coordination.md` aktivieren (ohne `.PROPOSAL`).

**Nach Mac-Gemma4-Live (erst Test auf LAN-Endpoint, dann Skill-Integration via Config-Flag):** rho-Engpass-Hierarchie updaten in `rules/token-engpass-hierarchie.md` (Gemma4 Stufe 3 einfuegen).

## Master-Handoff (fuer PC 1 Primary)

Dieses File + `memory/session_bootstrap_multi_machine_2026-04-20.md` ist Koordinations-Grundlage.

PC 1 Primary (Work-D2 oder Nachfolger) MUSS:
- Incoming PR-Reviews (PC 2-4 pushen Feature-Branches)
- Konflikt-Arbitrierung bei Drive-Sync-Duplikaten (Master-Decision)
- Scheduled-Task-Exklusivitaet wahren
- Daily-Check ob Worker-PCs Scheduled-Task-Duplikate entwickelt haben (settings-drift)

[CRUX-MK]
