# Copilot-CLI-First [CRUX-MK]

**Aktiviert:** 2026-04-19 durch Martin-Direktive "go verbessere es fuer alle".
**Belegt-durch:** Live-Test 2026-04-19T00:30 — `copilot -p "..."` = 1 Premium-Request (9s), **flat via Copilot Pro+ $39/Monat**. Claude-Opus-Equivalent: ~$0.70 pro Task (Faktor 27x teurer).
**Meta-Ebene:** E3 (Methoden-Audit — Token-Engpass-Routing)

## Kernregel

**Vor jedem nicht-strategischen Code-/Docs-/Research-Task:** Pruefe ob Copilot CLI es koennte. Wenn JA: delegiere via `copilot -p` (oder `--add-github-mcp-toolset all` bei GitHub-API-Tasks) statt Claude-Opus-Tokens zu verbrennen.

## Entscheidungs-Matrix

| Task-Typ | Primary-Tool | Claude-Rolle |
|----------|--------------|--------------|
| Code-Generation (neue Funktionen, Tests, Refactors) | `copilot -p` | Review + Integration |
| Docs-Drafting (README, API-Docs, Changelogs) | `copilot -p` | Final-Cut + Tone |
| Code-Explanation / Bug-Suche | `copilot -p --add-dir <repo>` | Synthese bei Multi-Root-Cause |
| GitHub-API-Tasks (Issues/PRs/Actions/Search) | `copilot --add-github-mcp-toolset all -p` | Orchestrierung |
| Deterministische Fixes (Typos, Imports, Linting) | `copilot -p` | Approval |
| Strategie / Phronesis / K_0-Relevanz | **Claude-Opus only** | Lead |
| Meta-Audit (E3+) / Cross-LLM-Synthese | **Claude-Opus + andere LLMs** | Lead |
| Familien / Q_0-Relevanz | **Claude-Opus only** | Lead |

## Invocation-Pattern

```bash
# Non-interactive, in CI/Scripts:
copilot -p "Task-Beschreibung" --allow-all-tools

# Mit expliziten Directories:
copilot -p "..." --add-dir /path/to/repo --add-dir /path/to/tests

# Mit GitHub-MCP (Issues, PRs, etc.):
copilot -p "..." --add-github-mcp-toolset all

# Reasoning-Effort skaliert (low = billig, xhigh = fuer hard tasks):
copilot -p "..." --effort high
```

## rho-Rechnung (empirisch)

- **Claude-Opus-Task (20k in / 5k out):** ~$0.70 OPEX
- **Copilot-CLI-Task (aequivalent):** 1 Premium-Request
  - Pro+ Basis: 1500 Premium-Requests/Monat inkludiert
  - Marginal-Cost: $0 bis 1500/Monat erreicht
  - Danach: ~$0.04/Request
- **Break-Even:** Jeder Claude-Task der ein Copilot-Task sein koennte = $0.70 Ersparnis
- **Lambda:** bei 10 solcher Tasks/Tag = ~$200/Monat Ersparnis = **~€2400/Jahr**

## Hard-No-Delegate (immer Claude-Opus)

- Decisions mit K_0-Relevanz (Kapital, Wegzugssteuer, Vermoegens-Transfer)
- Decisions mit Q_0-Relevanz (Familien-Beziehungen, Brueder-Kohaesion)
- Architekt-Entscheidungen (Welle-Progression, Phronesis, Doktrin)
- Cross-LLM-Synthese (erfordert Modell-Divergenz-Bewusstsein)
- Rule-/CRUX-Aenderungen (Meta-Harness §8c Verfassungsrang)

## Soft-Delegate-Regel

Wenn Task den Hard-No-Delegate-Filter PASSIERT:
1. Prompt kompakt formulieren (200-400 Worte)
2. `copilot -p "<prompt>" --allow-all-tools` aufrufen
3. Output validieren (quick Review)
4. Bei Zweifel: Claude-Opus als Second-Opinion **nach** Copilot-Draft

## Anti-Patterns

- **Claude-Opus fuer Boilerplate:** 50-Zeilen-Dockerfile generieren lassen = Token-Verschwendung
- **Claude fuer Multi-File-Refactors:** Copilot CLI hat `--add-dir` und Edit-Tools
- **Copilot CLI fuer Strategie:** Copilot optimiert lokal, nicht global (kein CRUX-Bewusstsein)
- **Copilot ohne CRUX-Check:** Delegate-Prompt muss CRUX-Constraints enthalten wenn relevant

## Integration in Skill-Stack

- Skill `copilot-delegate` (parallel zu dieser Rule) orchestriert die Delegation
- Archon-Workflows koennen Copilot CLI als Step-Executor nutzen (statt Claude-Subagent) fuer deterministische Phasen
- DF (Dark-Factories) bekommen Copilot-CLI-Integration als Default-Executor fuer Code-Tasks (DF-03 hat bereits Codex+Gemini — Copilot ergaenzt als 3. Flat-LLM)

## SAE-Isomorphie

Trinity-Pattern auf LLM-Executor-Ebene: **Claude-Opus = Conservative (hohe Qualitaet, teuer), Copilot CLI = Aggressive (schnell, flat), Codex/Gemini = Contrarian (diverse Perspektiven)**. Best-of-3 via Voting oder Router-Decision nach Task-Typ.

## CRUX-Bindung

- **K_0:** geschuetzt (keine kostenrelevanten Decisions an Copilot)
- **Q_0:** geschuetzt (keine Familien-Decisions an Copilot)
- **I_min:** erhoeht (strukturierte Delegation-Matrix)
- **W_0:** direkt positiv — 27x Token-Ersparnis pro delegierbarem Task
- **rho:** +€2400/Jahr realistische Baseline, skaliert mit Lambda

## Falsifikations-Bedingung

Diese Rule falsifiziert wenn:
- Copilot CLI Output-Qualitaet bei delegierbaren Tasks < 80% Claude-Opus-Niveau (Brier-Score ueber 20 Samples)
- Pro+-Premium-Requests-Kontingent chronisch ueberschritten (Marginal-Cost > Claude-Break-Even)
- Copilot CLI nicht mehr verfuegbar / subscription-Wechsel

**Revision-Trigger:** Monatliches Review via Skill `meta-learn`. Bei Qualitaets-Drop Delegation-Matrix enger (mehr Claude-Opus).

## Cross-LLM-Audit 2026-04-19 (PATCH-Log)

**Audit-Datum:** 2026-04-19T16:10+02:00
**Cross-LLM-Reviewers:** Codex gpt-5.4 + Grok 4.20-reasoning (via MCP, 0 EUR marginal via Sunk-Cost-Abos)
**Verdict:** CONDITIONAL (nicht HARDENED, gemaess `rules/cross-llm-pflicht-e3-plus.md`)
**Audit-File:** `branch-hub/cross-llm/2026-04-19-Multi-Provider-Rule-copilot-cli.md`
**Priority:** MITTEL
**Key-Weakness:** 80%-Delegability-Assumption unvalidiert; Quality-Ceiling ohne Baseline

### PATCH-Liste (Pending Implementation)
- **P1 Operationalisierung Hard-No-Delegate-Filter: YAML-Liste in Pre-Tool-Use-Hook pruefbar. K_0/Q_0/Phronesis/Meta-E4+ muessen mechanisch erkannt werden (nicht nur als Doku).**
- **P2 Baseline Brier-Score-Plan: N=20 Code-Tasks (Copilot vs Claude-Opus vs Codex), Q2 2026 durchzufuehren. Framework in DF-07 einbinden.**
- **P3 Clarify 80%-Delegability: Aktuelle Zahl = Assumption, nicht validiert. Realistischer Bereich: 45-65% (empirisch offen). CONDITIONAL bis Baseline vorliegt.**
- **P4 Quality-Ceiling Falsifikation: Brier-Drop > 15% ueber 20-Sample-Fenster -> Rule-Rollback auf Claude-primary.**

### Status
- Rule bleibt AKTIV (keine Rollback erforderlich).
- Patches sind Backlog-Items, umzusetzen wenn Baseline-Daten vorliegen.
- Verdict-Promotion auf CROSS-LLM-2OF3-HARDENED moeglich nach P1-P3 Umsetzung.
- Empirische Bestaetigung: Pentagon-Live-Run 2026-04-19 validierte Kern-Schwaechen (siehe `branch-hub/findings/PENTAGON-AUDIT-LIVE-2026-04-19.md`).



[CRUX-MK]
