# ChatGPT-Pro-First (Codex CLI Routing) [CRUX-MK]

**Aktiviert:** 2026-04-19 durch Martin-Direktive "ChatGPT Pro nutzen wir auch nicht maximal optimal".
**Belegt durch:** Codex CLI Live-Tests (Tier-1/2-Modelle in DF-03 v2.0, Cross-LLM-Runs METADD).
**Meta-Ebene:** E3 (Methoden-Audit)

## Kernregel

**ChatGPT Pro = Max-Codex-Access** (6x Rate-Limits vs Plus, alle gpt-5.x Modelle).
Nutze Codex CLI ueber:
- **`codex exec`** — non-interactive scripting (bisher genutzt)
- **`codex review`** — code review (neu erschlossen 2026-04-19)
- **`codex mcp-server`** — als MCP-Server in Claude Code (aktiviert 2026-04-19)

## Model-Matrix (Codex-exposed gpt-5 Familie)

| Model | Rolle | Use-Case | Cost-Profil |
|-------|-------|----------|-------------|
| **gpt-5.4** | Frontier-Pro | Meta-Reasoning, Strategie-Reviews, Deep Analysis | Premium (Pro-Abo-Rate) |
| **gpt-5.4-mini** | Kompakt | Routine-Classification, kurze Reviews | Low |
| **gpt-5.3-codex** | Code-Focus | Code-Generation, Refactor, Debug | Mid |
| **gpt-5.3-codex-spark** | Speed-Code | Quick fixes, autocomplete-level | Low |
| **gpt-5.2** | Balanced | Default fuer unklare Tasks | Mid |
| **gpt-5.2-codex** | Code v2 | Stable Code-Tasks | Mid |
| **gpt-5.1-codex-mini** | Lightweight | CI/CD, grosse Batch-Runs | Low |
| **gpt-5.1-codex-max** | Legacy-Max | Long-Context-Code (pre-5.4) | Mid-High |

## Entscheidungs-Matrix (wann Codex vs andere)

| Task-Typ | Primary | Reason |
|----------|---------|--------|
| Code-Review (PR, Pre-Commit) | **Codex `review`** | Native Review-Command, strukturiert |
| Adversarial Cross-Check | Codex gpt-5.4 | Adversarial im DF-03 bewaehrt |
| Research-Synthesis | Codex gpt-5.4 | Deep Research Pro-Tier |
| Boilerplate Code-Gen | Copilot CLI | flat via Pro+, schnell |
| Quick Q&A Fakten | Gemini | flat, gut fuer Fakten |
| Real-time-Web / X | Grok-MCP | Live-Search + X-Feed |
| Strategie / K_0 / Phronesis | **Claude Opus** | non-delegate |
| Multi-Step Complex Reasoning | Codex gpt-5.4 mit `-m gpt-5.4` | Pro-Model-Tier |

## Invocation-Patterns

### Codex exec (non-interactive)
```bash
codex exec --skip-git-repo-check "<prompt>"
codex exec -m gpt-5.4 "<prompt>"                     # explicit Pro-model
codex exec -c model="gpt-5.3-codex" "<prompt>"       # via config
```

### Codex review (Pre-Commit-Hook-Kandidat!)
```bash
codex review                          # review current branch vs main
codex review --uncommitted            # staged/unstaged/untracked
codex review "focus: security, n+1"   # custom instructions
```

### Codex MCP (ueber Claude Code)
Nach Session-Restart: `mcp__codex-mcp__*` Tools verfuegbar.
Invocation: automatisch von Claude (via Skill-Matching) oder explicit via Skill-Tool.

## Hard-No-Delegate (immer Claude-Opus)

Wie rules/copilot-cli-first.md:
- K_0 (Kapital-Decisions)
- Q_0 (Familie)
- Phronesis (L13)
- Meta-E4+ (Cross-LLM-Synthese selbst)
- Rule-/CRUX-Aenderungen

## rho-Rechnung

**ChatGPT Pro:** ~$200/Mo flat = $2400/Jahr Sunk-Cost.
**Nicht-Nutzung:** 0 EUR Gain, voller Sunk-Cost → rho_negativ.
**Volle-Nutzung:** jeder Codex-Call ersetzt Claude-Opus-Call:
- Lambda 5 Calls/Tag * 20k Tokens = 100k Tokens/Tag
- Claude-Opus-Cost fuer 100k Tokens: ~$7/Tag = $200/Mo
- **Break-Even: exakt 1 Pro-Monat** = jede weitere Nutzung ist purer rho-Gain
- Bei Lambda 20 Calls/Tag: $800/Mo Ersparnis, **Netto +$600/Mo = ~€7000/Jahr**

## Pre-Commit-Hook-Kandidat (neue Rule)

`codex review --uncommitted` vor jedem `git commit` laufen lassen (via .git/hooks/pre-commit):
- Blockiert Commits bei kritischen Issues
- Flat-Cost (Pro-Abo inkludiert)
- rho-Beispiel: 1 bug-catch pro Monat = 4h vermieden = ~€800

## Anti-Patterns

- **Claude-Opus fuer Code-Review** wenn `codex review` existiert = Token-Verschwendung
- **Kein Model-Tier-Routing**: alle Tasks an gpt-5.4 statt gpt-5.1-codex-mini fuer kleine Tasks
- **Codex ignorieren** in Multi-LLM-Wargames: Trinity braucht Codex als Staerke-Model
- **Codex als "optional"** behandeln: Sunk-Cost-Abo → MUSS maximal genutzt werden

## SAE-Isomorphie

Codex ist im Trinity-Pattern = **Contrarian** (diverse Perspektiven, Adversarial-Reviews).
Claude = Conservative, Copilot = Aggressive, Codex = Contrarian, Grok = Provocator, Gemini = Authority/Sources.

## Falsifikations-Bedingung

- Codex-Output-Qualitaet < 80% Claude-Opus bei delegierbaren Tasks
- Pro-Rate-Limit chronisch ueberschritten
- Subscription-Wechsel / Service-Disruption
- gpt-5.4 entfernt ohne Ersatz

## Cross-LLM-Audit 2026-04-19 (PATCH-Log)

**Audit-Datum:** 2026-04-19T16:10+02:00
**Cross-LLM-Reviewers:** Codex gpt-5.4 + Grok 4.20-reasoning (via MCP, 0 EUR marginal via Sunk-Cost-Abos)
**Verdict:** CONDITIONAL (nicht HARDENED, gemaess `rules/cross-llm-pflicht-e3-plus.md`)
**Audit-File:** `branch-hub/cross-llm/2026-04-19-Multi-Provider-Rule-chatgpt-pro.md`
**Priority:** MITTEL
**Key-Weakness:** Break-Even '1 Monat' ohne Konfidenzintervall; Pre-Commit-Hook kann Workflow blocken

### PATCH-Liste (Pending Implementation)
- **P1 Break-Even mit Konfidenzintervall: Monte-Carlo-Berechnung statt Punkt-Schaetzer. Realistisch: [0.7-1.8 Monate] 95%-KI bei Lambda 5-20 Calls/Tag.**
- **P2 Pre-Commit-Hook OPTIONAL: Fallback-Mode = WARNING statt BLOCK. Explizit opt-in per .git/hooks/pre-commit-ENABLE Flag. Entwickler-frust vermeiden.**
- **P3 Canary-Struktur: 5% Random-Sample-Ausgabe fuer Manual-Review durch Martin (Codex-Output-Sanity-Check).**
- **P4 Clarify Sunk-Cost: 200 EUR/Monat ist Sunk Cost (Psychologie), nicht Economics. Echte Basis: Qualitaets-Volumen bei Flat-Abos.**
- **P5 Model-Tier-Routing: Matrix praezisieren: gpt-5.4 fuer Meta-Reasoning, gpt-5.3-codex fuer Code-Gen, gpt-5.1-codex-mini fuer Batch-Routine. Dokumentieren wann was.**

### Status
- Rule bleibt AKTIV (keine Rollback erforderlich).
- Patches sind Backlog-Items, umzusetzen wenn Baseline-Daten vorliegen.
- Verdict-Promotion auf CROSS-LLM-2OF3-HARDENED moeglich nach P1-P3 Umsetzung.
- Empirische Bestaetigung: Pentagon-Live-Run 2026-04-19 validierte Kern-Schwaechen (siehe `branch-hub/findings/PENTAGON-AUDIT-LIVE-2026-04-19.md`).



[CRUX-MK]
