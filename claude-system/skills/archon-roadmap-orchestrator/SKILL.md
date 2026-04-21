---
name: archon-roadmap-orchestrator
description: |
  Orchestriert META-ROADMAP.md + Branch-Koordination via Event-Log + TTL-Leases + Capability-aware Modell-Routing + Token-Guard (Zeitwertverfassung).
  Triggers (run): "roadmap orchestrate", "sync roadmap", "orchestrate branches", "roadmap planen", "task verteilen", "/roadmap-orchestrate"
  Triggers (shadow): "dry-run roadmap", "shadow orchestrate"
  Triggers (report): "roadmap status", "orchestrator report", "rho dashboard"
  Capability: Event-driven 11-Node-DAG mit Semantic-Fingerprint-Dedupe, TTL-Leases+Heartbeats, Capability-aware Fallback, Context-Cache, Web-Enrichment-Worker. Token-Guard enforced rho-Gain-Schwelle + Budget-Hardcap.
  NICHT: Pure Roadmap-Datei-Single-Source-of-Truth. Architektur ist Event-Log + Materialized State + Planner (siehe branch-hub/cross-llm/2026-04-18-Orchestrator-Skill-Wargame.md).
crux-mk: true
version: 2.0.0
origin: opus-4.7-METADD-2026-04-18 (Gemini+Codex-drafted, Claude-integrated, 3/3 Cross-LLM-MODIFY-gewargamed)
meta-ebene: E3
cross-llm-belegung: branch-hub/cross-llm/2026-04-18-Orchestrator-Skill-Wargame.md
---

# /archon-roadmap-orchestrator [CRUX-MK]

## Wann nutzen

- Du willst **zentrale Priorisierung** aller offenen Meta-Tasks ueber alle aktiven Claude-Sessions (METADD, METAOPS, Work-C1/C2/D, META-C2)
- Du willst **Duplikat-Erkennung** via Semantic-Fingerprint wenn mehrere Branches scheinbar gleiche Tasks haben
- Du willst **Token-Budget-Enforcement** via rho-Guard (Zeitwertverfassung)
- Du willst **Modell-Routing** nach Task-Type + Load + Rate-Limits (Capability-aware, nicht Size-Downgrade)
- Du willst **Branch-Load-Balancing** via TTL-Leases mit Heartbeats

NICHT fuer: Einmal-Priorisierungen (da reicht BEACON + manuelle Decision).

## Architektur (Event-Log + Materialized State + Planner)

```
Branches emittieren Events ──► branch-hub/state/event-log.jsonl (append-only)
                                    │
                                    ▼
                     scripts/collect_roadmap_state.py
                                    │
                                    ▼
                       state/roadmap-materialized.json
                                    │
                                    ▼
                         Event-Driven Planner (11-Node-DAG)
                                    │
                ┌─────────┬─────────┼─────────┬─────────┐
                ▼         ▼         ▼         ▼         ▼
           token-guard  dedupe   prioritize  route    web-enrich
                │         │         │         │         │
                └─────────┴─────┬───┴─────────┴─────────┘
                                ▼
                        TTL-Lease-Assignment
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
               Branch-A    Branch-B    Branch-C
                 inbox       inbox       inbox
```

## Pentagon-Ablauf

### Phase 1: PLAN
Martin entscheidet Scope. Default: `/roadmap-orchestrate` = alle aktiven Branches + alle OFFEN-Tasks.

Filter moeglich:
- `--focus meta` (nur E2-E5-Tasks)
- `--focus code` (nur Implementation-Tasks)
- `--branch METADD` (nur fuer eine Branch)
- `--dry-run` (Shadow-Mode, kein Inbox-Write)

### Phase 2: SPEC
Nodes laufen in `workflow.yaml`-DAG. Jeder Node hat:
- `timeout_sec`, `budget_tokens`, `output_artifacts`
- Session-Strategie: `fresh` (Adjudication/Red-Team) oder `continue-with-cache` (Priorisierung, Context-wiederverwendbar)

### Phase 3: IMPLEMENT
Python-Scripts in `scripts/`. Siehe Interface-Tabelle unten.

### Phase 4: TEST
`tests/smoke_test.py` — Mock-Roadmap + Mock-Events, assert materialized state korrekt + inbox-writes + rho-Bilanz > 0.

### Phase 5: REFINE
Audit-Log + Martin-Review-Log (beim Dark-Factory DF-06 in `.archon/dark-factory/DF-06/review-log.jsonl`).

## Scripts-Interface (alle in `scripts/`)

| Script | Zweck | CLI |
|--------|-------|-----|
| `event_log_append.py` | Append events | `--branch --type --task-id --payload` |
| `collect_roadmap_state.py` | Rebuild materialized | `[--rebuild-from-scratch]` |
| `detect_roadmap_conflicts.py` | Conflicts + Cycles + SLA | `[--since-cursor] [--branch]` |
| `semantic_fingerprint_dedup.py` | Dedupe-Kandidaten | `--threshold 0.7` |
| `model_router.py` | Capability-aware Routing | `--task-type --context-tokens` |
| `ttl_lease_manager.py` | Leases issue/renew/release/sweep | Subcommands |
| `write_inbox_assignments.py` | Inbox-Writes | `--assignments-json` |
| `token_guard.py` | Budget + rho-Enforcement | `--init --check --record --finalize --report` |
| `global_optima_check.py` | Hot-reload Global-Optima | `[--validate]` |
| `propagate_optima.py` | Hook bei optima-Change | (auto) |
| `web_enrichment.py` | Perplexity/Firecrawl | `--queries-json` |

## Token-Guard (Kern-Innovation, Zeitwertverfassung)

Jeder Node wird durch `token_guard.py` umrahmt:
- **Pre**: `--check` schaetzt cost_eur, blockt wenn > Budget oder Hardcap
- **Post**: `--record` loggt actual cost, berechnet rho_run = CM - OPEX
- **Finalize**: `--finalize` aggregiert Run, alert wenn rho < 0

Globale Werte aus `global-optima.json`:
- CM_base pro Task-Type (meta-audit 25 EUR, priorization 15 EUR, ...)
- h_opportunity (0.08/Jahr)
- Lambda_typical (pro Task-Type)
- K_0_base, Q_0_min, I_min_threshold
- Token-Budgets, Daily-Global-Cap (50 EUR)

## Global-Optima-Hooks (Variable Propagation)

Bei Aenderung `global-optima.json`:
1. Hook `on_optima_change` triggert `propagate_optima.py`
2. Script liest neuen Stand + schreibt:
   - `branch-hub/state/optima-snapshot-<ts>.json` (fuer Audit)
   - Appends event: `optima-changed` in event-log
   - Touched alle DF-config.yaml (DF-02, DF-03, DF-04, DF-06) mit neuem optima-Ref
3. Bei naechstem DF-Run liest jeder `config.yaml` automatisch den neuen Stand

Damit: 1 zentrale Config-Aenderung → alle Dark-Factories + Workflows + Orchestrator sehen sie sofort.

## Dark-Factory DF-06 (Level 5, Shadow-Mode 150 Decisions)

Scheduled via Windows Task Scheduler. Trigger:
- **Event-Driven**: bei task-created, conflict-detected, budget-breach, sla-breach
- **30-Min-Debounce**: nicht haeufiger als alle 30 Min
- **6h-Reconciliation-Sweep**: Tagesfenster-Aufraeumung

Pflicht-Bedingungen (alle 10 aus `rules/when-to-archon.md` Tier 2):
1. Lambda: Event-based ~10-30/Tag ✓
2. Narrow Scope: nur META-ROADMAP + BEACON + Inbox ✓
3. Determinismus: 90% Bash/Python ✓
4. Rollback: git revert < 60s ✓
5. Test-Coverage: tests/ >= 90% ✓
6. K_0 geschuetzt: KEIN Code-Touch ✓
7. Q_0 messbar: Conflicts/Duplikate ✓
8. Escalation: 2 Fails → Martin-Alert ✓
9. Hardcap: 2 EUR/Run × 30/Tag = 60 EUR/Tag (CAP override 12 EUR) ✓
10. Audit: action-log + dark-factory.jsonl ✓

## Cross-LLM-Belegung

Vor Production: Cross-LLM-Wargame durchgefuehrt (3/3 MODIFY, CROSS-LLM-2OF3-HARDENED).
Patches eingearbeitet: Event-Log-Arch, TTL-Leases, Semantic-Dedupe, Capability-Fallback, Volume-basierter Shadow-Mode, Web-Enrichment-Node separat.
Belegung: `branch-hub/cross-llm/2026-04-18-Orchestrator-Skill-Wargame.md`

## Anti-Patterns

1. **Roadmap-Datei als Wahrheit** (Wargame-Finding 3/3 REJECT) → Event-Log ist Wahrheit, Datei ist Projection
2. **4h-Cron-only** (REJECT) → Event-driven mit 30-Min-Debounce
3. **Size-Downgrade bei Rate-Limit** (REJECT) → Backoff oder Alternative same-capability
4. **Fresh-Session ueberall** (REJECT) → nur bei Adjudication/Red-Team, sonst Cache-Cost-Win
5. **Hardcoded Limits-Matrix** (REJECT) → `capability-registry.json` timestamped
6. **Ohne Token-Guard** (REJECT) → jeder Node durch `token_guard.py --check/--record`

## rho-Bilanz (Wargame-validiert)

- CM pro Orchestrierung: 15-35 EUR
- Lambda: 10-30/Tag
- OPEX: 0.2-0.8 EUR/Run
- rho_jaehrlich: 40-80k EUR/J
- Cascade (andere Branches 0.5-1h/Tag gespart): +80-150k EUR/J
- **Total: +120-230k EUR/J** (Amdahl-Grenze-kompatibel)

## Falsifikations-Bedingung

Empirical Claim. Falsifiziert wenn:
- Nach 30 Runs: Durchsatz-Gain < 1.3x
- Martin-Reviews < 60% "useful"
- Semantic-Fingerprint > 10% False-Positive-Duplicates
- Orchestrator-Overhead > 20% der gesparten Branch-Zeit

## CRUX-Bindung

- K_0: indirekt (bessere Meta-Entscheidungen → K_0-Schaden-Reduktion)
- Q_0: direkt (epistemische Integritaet der Meta-Regel-Orchestrierung)
- I_min: stark erhoeht (Event-Sourcing + Capability-Registry)
- W_0: effizient (Token-Guard-Enforcement, keine Budget-Explosion)

[CRUX-MK]
