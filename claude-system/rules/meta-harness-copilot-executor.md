# Meta-Harness §8f: Copilot-Executor-Pattern [CRUX-MK]

**Aktiviert:** 2026-04-19 durch Martin-Direktive "baue auch die Archons Meta Harnesse".
**Ergaenzt:** `~/.claude/rules/meta-harness.md` Organ 8 Stem Cell.
**Meta-Ebene:** E3 (Methoden-Audit — Executor-Routing)

## §8f Copilot-Executor-Pattern (NEU)

Meta-Harness §8a-e sagte bisher implizit: Subagenten = Claude-Instanzen. Ab jetzt:

**Executor-Trinity fuer Skill-/Archon-/DF-Nodes:**

| Executor | Rolle | Token-Profil | Trigger |
|----------|-------|--------------|---------|
| **Claude-Opus** | Conservative (Strategy, Synthese, K_0/Q_0) | Teuer ($$$), slow | Default fuer Meta-Level E4+, Phronesis |
| **Copilot CLI** | Aggressive (Code, Docs, GitHub-MCP) | Flat via Pro+ ($0 marg.) | Default fuer deterministische Code-Tasks |
| **Codex / Gemini / Grok** | Contrarian (Divergent Perspektiven) | Flat via Abos ($0 marg.) | Default fuer Cross-LLM-Haertung |

## Routing-Regel

Jeder Skill- / Archon- / DF-Node bekommt neues Pflichtfeld `executor-priority`:

```yaml
executor-priority:
  primary: copilot | claude | codex | gemini | grok | hybrid
  fallback: claude | other
  rationale: <1 Satz warum primary gewaehlt>
```

## Integration-Points

### 1. Archon-Workflows
Jeder Node mit `type: cli-executor` kann primary-copilot haben:
```yaml
nodes:
  - id: code-generation
    type: cli-executor
    executor-priority:
      primary: copilot
      fallback: claude
      rationale: "Deterministische Code-Gen, keine K_0-Relevanz"
    command: copilot -p "..." --allow-all-tools
```

### 2. Dark-Factories
DFs bekommen `executor_matrix` in config:
```yaml
executor_matrix:
  synthesis: copilot
  validation: gemini
  audit: claude-opus-only
  emergency-fallback: claude-opus
```

DF-03 (Multi-LLM) wird so erweitert: Copilot als 3. Flat-LLM neben Codex+Gemini.
DF-01..DF-06 bekommen monatlich ein Retrofit durch Skill `dark-factory-evolve`.

### 3. Skills (SKILL.md)
Neue Frontmatter-Felder:
```yaml
executor-priority:
  primary: copilot | claude | hybrid
  hard-no-delegate: [K_0, Q_0, Phronesis, Meta-E4+, Cross-LLM-Synthese]
```

### 4. Subagent-Invocation
Claude-Agent-Tool-Prompts bekommen Standard-Intro-Zeile:
> "Wenn dein Task deterministische Code-Gen / Docs / GitHub-API-Call ist:
> delegiere an `copilot -p "<prompt>" --allow-all-tools` statt selbst zu antworten.
> Siehe rules/copilot-cli-first.md fuer Decision-Matrix."

## rho-Rechnung Meta-Harness

Vor §8f:
- Lambda Subagenten-Runs / Monat: ~50 (Multi-Branch-System)
- Claude-Opus-Tokens pro Run: ~25k (durchschnittlich)
- OPEX: 50 * 25k * $0.000075 = $93.75/Monat = ~$1125/Jahr

Nach §8f (40% Delegate-Rate realistisch):
- Claude-only: 30 Runs * 25k = 750k Tokens
- Copilot-delegated: 20 Runs * 1 Premium = flat (Pro+ Kontingent)
- Claude-OPEX: 750k * $0.000075 = $56.25/Monat = ~$675/Jahr
- **Ersparnis: $450/Jahr, skaliert mit Lambda**

## Self-Improvement-Loop (§8b Self-Edit erweitert)

`meta-learn` Skill bekommt Zusatz-Check nach jedem Session-Ende:
1. Welche Subagenten-Runs haetten delegiert werden koennen? (Retrospektiv)
2. Delegate-Rate vs Optimum (Ziel: 40-60% fuer Code-Tasks)
3. Bei Delegate-Rate < 20% ueber 5 Sessions: Rule-Review (zu konservativ?)
4. Bei Delegate-Rate > 70% + Qualitaets-Drop: Rule-Review (zu aggressiv?)

## CLAUDE.md Evolution (§8c Anbindung)

CLAUDE.md §18 Installed Skills bekommt neue Zeile (pending bei naechstem Bootstrap):
| 11 | copilot-delegate | Skill | ~/.claude/skills/copilot-delegate/ | Aktiviert 2026-04-19 |

## Hook Self-Modification (§8d Anbindung)

Pre-Subagent-Hook wird vorgeschlagen (pending Martin-Approval):
- Vor Agent-Spawn: Frage "Kann copilot-delegate diesen Auftrag erfuellen?"
- Bei JA: Invoke copilot-delegate Skill statt Agent
- Konfidenz-Map persistent in finding-library.json

## CRUX-Bindung

- **K_0:** geschuetzt (Hard-No-Delegate-Filter in allen Integration-Points)
- **Q_0:** geschuetzt (Familien/Phronesis bleiben Claude-Opus)
- **I_min:** erhoeht (strukturiertes Executor-Routing)
- **W_0:** +$450-2400/Jahr je nach Lambda
- **rho:** direkt positiv, Lambda-skalierend

## Falsifikations-Bedingung

- Delegate-Rate > 70% aber Brier-Score-Drop > 10%: Rule zurueckdrehen
- Copilot Pro+ Kontingent chronisch exhausted: Delegate-Rate senken
- Claude-Opus wird billiger als Copilot CLI: Rule revidieren

## SAE-Isomorphie

Trinity-Pattern auf Executor-Ebene isomorph zu SAE-Trinity-Slot (Conservative/
Aggressive/Contrarian). Voting-Mechanismus bei Cross-LLM-Check entspricht
`core/trinity.py::update_scores`. Relegation bei Quality-Drop entspricht
MYZ-27 Relegation.

## Cross-LLM-Audit 2026-04-19 (PATCH-Log)

**Audit-Datum:** 2026-04-19T16:10+02:00
**Cross-LLM-Reviewers:** Codex gpt-5.4 + Grok 4.20-reasoning (via MCP, 0 EUR marginal via Sunk-Cost-Abos)
**Verdict:** CONDITIONAL (nicht HARDENED, gemaess `rules/cross-llm-pflicht-e3-plus.md`)
**Audit-File:** `branch-hub/cross-llm/2026-04-19-Multi-Provider-Rule-meta-harness-copilot.md`
**Priority:** MITTEL
**Key-Weakness:** Trinity-Illusion (Latent-Space-Overlap > 0.85); Self-Measurement ohne externe Kontrolle (Goodhart)

### PATCH-Liste (Pending Implementation)
- **P1 Trinity-Reframe: Anti-Pattern korrigieren - Claude/Copilot/Codex sind NOISE-VARIATION, nicht Fundamentaldiversitaet. Erwartung reduzieren auf 5-15% Quality-Delta pro Model.**
- **P2 Context-Switch-Cost in rho: Jedes Routing kostet ~500 Tokens Overhead (Prompt-Serialisierung + Response-Parsing + Cache-Invalidation). Bei Lambda > 50 Tasks/Monat relevant. Formel: rho_delegate = saving - 500*lambda.**
- **P3 Externe Audit-Hook: Martin-manual-Review + Randomisierte Samples (N=5/Monat). Nicht Claude-self-measurement.**
- **P4 Quality-Ceiling: Baseline Brier-Score N=20 bis Q2 2026 gegen Hugging-Face-Leaderboard (externe GT).**

### Status
- Rule bleibt AKTIV (keine Rollback erforderlich).
- Patches sind Backlog-Items, umzusetzen wenn Baseline-Daten vorliegen.
- Verdict-Promotion auf CROSS-LLM-2OF3-HARDENED moeglich nach P1-P3 Umsetzung.
- Empirische Bestaetigung: Pentagon-Live-Run 2026-04-19 validierte Kern-Schwaechen (siehe `branch-hub/findings/PENTAGON-AUDIT-LIVE-2026-04-19.md`).



[CRUX-MK]
