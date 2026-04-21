# Model-Portfolio-Optimization [CRUX-MK]

**Aktiviert:** 2026-04-19 durch Martin-Direktive "sorge dafuer dass wir wirklich das maximale herausholen".
**Meta-Ebene:** E3 (Methoden-Audit ueber Model-Routing)
**Bezug:** rules/token-engpass-hierarchie.md, rules/copilot-cli-first.md, rules/chatgpt-pro-first.md

## Kernthese

Kemmer-System zahlt Flat-Sunk-Costs fuer 5+ LLM-Abos (~€600-1000/Monat):
- Claude Pro/Max (Usage-based bei Opus)
- Copilot Pro+ ($39/Mo)
- ChatGPT Pro ($200/Mo)
- Grok SuperGrok Heavy (~$300/Mo)
- Gemini Ultra (bundle)
- Perplexity Ultimate (~$40/Mo)

**Jeder nicht-genutzte Call auf einem Flat-Abo = rho-negativ** (Sunk-Cost ohne Nutzen).
**Jeder Claude-Opus-Call wo ein Flat-LLM reicht = rho-negativ** (Token-Verbrennung).

Optimales Portfolio = **jeder Task geht an den guenstigsten LLM der die Qualitaets-Schwelle erreicht.**

## Executor-Role-Matrix (Stand 2026-04-19)

| Rolle | Primary | Reason | Cost-Profil |
|-------|---------|--------|-------------|
| **Conservative (Strategie, K_0, Q_0, Phronesis)** | Claude Opus 4.7 (1M) | Tiefes Denken, Risk-Aware | Premium, non-delegate |
| **Aggressive (Code-Gen, Docs, GitHub-API)** | Copilot CLI Pro+ | flat, fast, GitHub-MCP eingebaut | Flat (Pro+) |
| **Contrarian (Code-Review, Cross-Check, Research-Synthesis)** | Codex (gpt-5.4 / gpt-5.3-codex) | `codex review`, Pro-Tier 6x Plus | Flat (Pro) |
| **Authority (Faktencheck, Citations, Papers)** | Gemini 2.5 Pro | Breite Wissensbasis, Quellen | Flat (Ultra) |
| **Provocator (Adversarial, Red-Team, First-Principles)** | Grok 4 (via grok-mcp) | Anti-Sycophancy, X/Twitter-Live | Flat (Heavy) |
| **Source-Finder (Real-time Web, News, X-Feed)** | Grok-MCP (X-Search) oder Perplexity | Live-Web, aktuelle Events | Flat |
| **Emergency-Fallback** | Claude Sonnet 4.6 | Wenn Flat-LLMs down | Mid-Cost |

## Routing-Regel (vor jedem Task)

```
DECIDE_EXECUTOR(task):
  1. if K_0/Q_0/Phronesis/Meta-E4+/Cross-LLM-Synthese-Meta: return CLAUDE_OPUS
  2. elif task_type == code-review: return CODEX review
  3. elif task_type == code-gen AND no K_0: return COPILOT
  4. elif task_type == research-synthesis: return CODEX gpt-5.4 (Pro-Deep)
  5. elif task_type == adversarial-check: return GROK (if mcp) OR CODEX gpt-5.4
  6. elif task_type == real-time-web: return GROK-MCP X-Search OR PERPLEXITY
  7. elif task_type == quick-fact: return GEMINI
  8. elif task_type == meta-hardening (multi-LLM): return PARALLEL(codex+gemini+copilot+grok)
  9. else: return CLAUDE_OPUS (sichere Default bei Unklarheit)
```

## Monthly-Audit-Pflicht

Jeden Monat (1. des Monats, via Archon-Workflow `model-portfolio-audit.yaml`):

1. **Inventar-Snapshot**: verfuegbare Modelle pro LLM (Codex liefert Liste via `exec "list models"`)
2. **Preis-Update**: aktuelle USD/1M-Tokens-Preise (Anthropic, OpenAI, xAI, Google, Perplexity)
3. **Subscription-Check**: Verlaengerung / Cancellation-Datum / Rate-Limits
4. **Token-Preis-Leistungs-Wargame**: identischer Prompt (Pentagon-Test: Fakt + Reasoning + Code + Research + Adversarial) auf allen Modellen
5. **rho-Analyse pro Model**: Delta-rho = Qualitaets-Score × Lambda / (Kosten × Zeit × h)
6. **Delta zu letztem Monat**: neue Modelle, neue Caps, veraltete Routes
7. **Role-Reassignment**: welcher Model-Slot bekommt welche Rolle fuer naechsten Monat?
8. **Self-Improvement**: Rules + Skills + DFs automatisch patchen (Decision-Card fuer Martin)
9. **Findings nach Canon**: HARDENED-Claims → `branch-hub/findings/MONTHLY-AUDIT-<YYYYMM>.md`

## Token-Preis-Leistungs-Wargame (Pre-Audit-Pflicht)

Vor jedem Monthly-Audit (also monatlich 1x):

```
PENTAGON_PROMPT:
  P1_FACT: "Was ist die korrekte MWSt-Rate in Bayern 2026 fuer Gastronomie (Speisen, Inhouse)?"
  P2_REASONING: "Sensitivitaets-Analyse: wenn rho_a faellt um 10%, wie reagiert Hamilton H?"
  P3_CODE: "Python-Funktion: atomic file-write mit Backup + Rollback. 20 Zeilen max."
  P4_RESEARCH: "3 aktuelle Papers (2025-2026) zu Multi-Agent-LLM-Coordination. Kurz."
  P5_ADVERSARIAL: "Finde 3 Schwachstellen in: 'rho(a) = CM*Lambda - OPEX - h*Lambda*W ist zeitlos gueltig'."

METRICS pro Model:
  - Brier-Score gegen HARDENED-Referenz (P1)
  - Reasoning-Depth-Score (P2, Cross-LLM-peer-review)
  - Code-Exec-Test-Pass (P3)
  - Citation-Quality (P4)
  - Adversarial-Coverage (P5, wie viele echte Schwachstellen vs Strohmaenner)

SCORE = (Quality × Lambda) / (Cost_eur × Time_s × h)

WINNER pro P1-P5 = bekommt die Rolle im naechsten Monat.
```

## Self-Improvement-Pflicht

Nach jedem Monthly-Audit:

1. **Rules aktualisieren**: Matrix oben + rules/copilot-cli-first.md + rules/chatgpt-pro-first.md
2. **Skills aktualisieren**: Version-Bump bei relevanten delegate-Skills
3. **DF-Config aktualisieren**: neue LLM_PROVIDERS Listen, neue Tier-Zuordnung
4. **CLAUDE.md §18 updaten**: neue Skills/Rules/Archons eingetragen
5. **BIAS-Catalog reviewen**: haben sich Patterns wiederholt? → neue Hooks?
6. **rho-Impact messen**: realer Gain vs erwarteter Gain (Lambda-Honesty)

## Hard-Invarianten (auch nach Audit UNVERAENDERLICH)

1. **K_0-Tasks** bleiben Claude Opus (nie delegiert)
2. **Q_0-Tasks** bleiben Claude Opus (Familie nicht delegieren)
3. **Phronesis (L13)** bleibt Claude Opus
4. **Rule-/CRUX-Aenderungen** bleiben Claude Opus (Meta-Harness §8c)
5. **FIXPUNKT-1 bis 4** nicht ueberstimmbar durch Audit (E5, axiomatisch)

## Anti-Patterns

- **"alle LLMs pruefen" ohne Pentagon-Prompt**: Ad-hoc-Tests = Bias, nicht messbar
- **Model-Drift ignorieren**: wenn gpt-5.4 entfernt wird, muss Rule sofort aktualisiert
- **Kosten-Fehleinschaetzung**: Flat ≠ free. Rate-Limit-Exhaustion kostet Zeit
- **Audit ohne Self-Improvement-Step**: dann lernt das System nicht
- **Claude-Opus-Favoritismus**: "Claude kann's besser" ohne Benchmark = Opus-Gluecksritter-Bias

## rho-Quantifizierung

Pre-Audit: ~€600-1000/Mo Flat-Sunk-Cost
- Nicht-Nutzung = 100% Verlust = rho_negativ voll
- Halbe-Nutzung = 50% Verlust
- Optimale Routing = fast 0 Verlust

Zusaetzlich:
- Vermiedene Claude-Opus-Tokens: €500-2400/Jahr bei konsequenter Delegation
- Lambda-skaliert: bei hohem Workflow-Volumen > €10k/Jahr moeglich

## Falsifikations-Bedingung

- Pentagon-Test reicht nicht (bei >30% False-Negatives) → neue Metrik-Pentagon
- Audit-Overhead > Gain → Audit-Frequenz reduzieren (quartalsweise)
- Self-Improvement fuehrt zu Regressionen → mehr Martin-Approval-Gates

## SAE-Isomorphie

Dies ist **Trinity-Relegation auf LLM-Ebene**: 
- Underperformende Modelle werden relegiert (Role-Demotion)
- Hoch-performer werden promoted (mehr Lambda)
- Monatlicher Cadence = SAE-Relegation-Zyklus (F_CUM_DECAY=0.98 uebertragen auf LLM-Scoring)

## Beziehung zu anderen Rules

- **rules/token-engpass-hierarchie.md**: Liefert Input (Engpass-Rangfolge)
- **rules/copilot-cli-first.md**: operationalisiert fuer Copilot
- **rules/chatgpt-pro-first.md**: operationalisiert fuer Codex
- **rules/meta-harness-copilot-executor.md**: §8f Executor-Trinity wird monatlich re-kalibriert
- **rules/df-agile-adaptation.md**: Drift-basierte Frequenz-Anpassung fuer DF-07

## CRUX-Bindung

- **K_0**: geschuetzt durch Hard-Invarianten (Claude-Opus-Reservat)
- **Q_0**: epistemische Integritaet durch Pentagon-Test + Cross-LLM
- **I_min**: strukturierter Monthly-Audit-Prozess
- **W_0**: direkt optimiert (das ist das Ziel der Regel)
- **rho**: +€500-10000/Jahr skaliert mit Workflow-Volumen

## Cross-LLM-Audit 2026-04-19 (PATCH-Log)

**Audit-Datum:** 2026-04-19T16:10+02:00
**Cross-LLM-Reviewers:** Codex gpt-5.4 + Grok 4.20-reasoning (via MCP, 0 EUR marginal via Sunk-Cost-Abos)
**Verdict:** CONDITIONAL (nicht HARDENED, gemaess `rules/cross-llm-pflicht-e3-plus.md`)
**Audit-File:** `branch-hub/cross-llm/2026-04-19-Multi-Provider-Rule-model-portfolio.md`
**Priority:** HOCH
**Key-Weakness:** Pentagon-Test ZIRKULAER (Brier-Score als Ground-Truth = self-referenziell); empirisch bestaetigt (Gemini P4 fabrizierte arXiv-IDs)

### PATCH-Liste (Pending Implementation)
- **P1 CRITICAL - Pentagon-Test gegen externe Ground-Truth: P1-Fakt URL+Zitat-Pflicht, **P4-Research arXiv-ID-Validierung PFLICHT** (HTTP 200 bei arxiv.org/abs/<id>) - Gemini fabrizierte IDs 2603.xxxx am 2026-04-19. Hugging-Face-Leaderboard als externe GT fuer Code/Reasoning-Scores.**
- **P2 Audit-Overhead explizit in rho: 4h/Monat x 200 EUR/h = 800 EUR OPEX. In rho-Rechnung negativ eintragen. Bei Lambda < 3 model-switches/Monat: Audit-Frequenz quartalsweise reduzieren.**
- **P3 Pilot-Phase fuer Role-Reassignment: Shadow-Mode 2 Wochen vor Live-Switch. Kein direkter Switchover bei monatlichem Audit.**
- **P4 Hard-Invarianten revidierbar: K_0/Q_0/Phronesis/FIXPUNKT-1-4 NICHT rigid gegen empirischen Widerspruch. Revision via Martin-Phronesis (nicht automatisch).**
- **P5 Goodhart-Schutz erweitern: Hold-out-Test-Set (nicht-Trainings-Daten) fuer Generalisierung. Rotierende Prompt-Varianten gegen Metrik-Gaming.**
- **P6 EXECUTOR-ROLE-MATRIX UPDATE (empirisch Pentagon-Live 2026-04-19): Code=Codex PRIMARY + Copilot SECONDARY; Adversarial=Codex PRIMARY + Grok SECONDARY (nur X-Search+Sycophancy-Check); Reasoning=Gemini PRIMARY + Claude SECONDARY; P1-Fakt=Gemini PRIMARY + Codex SECONDARY; P4-Research=Codex PRIMARY (mit URL-Fetch!) + Copilot SECONDARY, Grok DEPRECATED fuer Research (P4-Rejection = false-negative).**

### Status
- Rule bleibt AKTIV (keine Rollback erforderlich).
- Patches sind Backlog-Items, umzusetzen wenn Baseline-Daten vorliegen.
- Verdict-Promotion auf CROSS-LLM-2OF3-HARDENED moeglich nach P1-P3 Umsetzung.
- Empirische Bestaetigung: Pentagon-Live-Run 2026-04-19 validierte Kern-Schwaechen (siehe `branch-hub/findings/PENTAGON-AUDIT-LIVE-2026-04-19.md`).



[CRUX-MK]
