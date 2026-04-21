---
name: multi-llm-parallel
description: Orchestriert parallele LLM-Queries ueber Claude + Copilot-Pro+ + ChatGPT-Codex + Grok-Ultra + Perplexity-Ultimate fuer maximale Research-Velocity. Martin-Direktive 2026-04-18. Claude generiert Prompts, Martin faehrt parallel durch 4-5 Browser-Tabs, Claude konsolidiert Antworten via Cross-LLM-4/7-Regel.
crux-mk: true
version: 1.1.0
aktiviert: 2026-04-18
updated: 2026-04-19 (Option C CLI-automatisiert, Copilot CLI integriert)
triggers:
  - "multi llm research"
  - "parallel llm"
  - "cross llm"
  - "cross-llm sprint"
  - "frag alle llms"
  - "grok perplexity gpt"
---

# Multi-LLM Parallel Orchestrator [CRUX-MK]

**Martin-Direktive 2026-04-18:** *"natuerlich so viel wie moeglich an GitHub Copilot auslagern, ChatGPT Codex, Grok Ultra Pro, Perplexity Ultimate, so viel mehr untersucht werden, deutlich mehr parallel"*

## Zweck

Bei Research-Fragen, Architektur-Entscheidungen, Cross-Validations maximal parallel
durch alle verfuegbaren LLM-Ressourcen — **nicht** seriell.

## Verfuegbare LLMs (Stand 2026-04-18)

| LLM | Zugang | Scope | Staerke |
|-----|--------|-------|---------|
| Claude Opus 4.7 (1M) | diese Session | Analyse, Reasoning, Architektur | Tiefes Denken, 1M Context |
| GitHub Copilot Pro+ | IDE / Web | Code, Docs, Commit-Msgs | Code-Generation, IDE-Integration |
| ChatGPT Codex (GPT-5) | Web/App | Research, Code, Multimodal | Breitestes Wissen, Codex-Kern |
| Grok Ultra Pro (xAI) | Web | Provokante Sichten, Real-time Web | Anti-Bias-Angriff, "First Principles" |
| Perplexity Ultimate Pro | Web | Quellen, Research, Zitate | Multi-Source-Recherche, Citations |

## Workflow (5 Schritte)

### Schritt 1: Frage formulieren (Claude)

Claude analysiert die Frage und erstellt:
- **Master-Prompt** (neutral, ohne Leading)
- **Perspektiv-Prompts** pro LLM (auf Staerken angepasst)

Output: JSON mit 4-5 Prompts fuer parallele Ausfuehrung.

### Schritt 2: Parallel-Dispatch (Martin oder automatisiert)

Option A — Martin-manuell (sofort moeglich):
- Martin oeffnet 4-5 Browser-Tabs
- Claude-Prompt → copilot.github.com
- GPT-Prompt → chatgpt.com
- Grok-Prompt → grok.com
- Perplexity-Prompt → perplexity.ai
- Parallel laufen lassen (1-3 Min each)

Option B — API-basiert (wenn Keys vorhanden):
- Claude ruft andere APIs via MCP auf
- Aktuell: nicht automatisch (API-Keys muessen Martin bereitstellen)

Option C — **CLI-automatisiert (NEU 2026-04-19, Default seit v1.1.0):**
- Alle CLIs lokal installiert und geprueft via `which`:
  - `copilot -p "<prompt>" --allow-all-tools` (GitHub Copilot Pro+, 1 Premium/Request flat)
  - `codex exec --skip-git-repo-check "<prompt>"` (ChatGPT Pro via Codex-CLI, flat)
  - `echo "<prompt>" | GEMINI_API_KEY=$KEY gemini -p "..."` (Gemini Ultra, flat)
  - `grok -p "<prompt>"` (xAI Grok, flat)
  - Perplexity: kein natives CLI — bleibt Browser-Option in Option A
- **Parallel-Dispatch via Bash-Background** (`&` + `wait`), kein Martin-Manual noetig
- Helper-Script: `~/.claude/scripts/multi-llm-parallel.sh` (POC, nutzt /tmp/ gegen Windows-UNC-Bugs)
- Output-Capture: pro LLM in `/tmp/mllm-<llm>-<ts>.out`
- Aggregation: Claude liest alle Outputs, wendet 4/5-Regel an

**Beispiel Option C — 4 LLMs parallel fuer eine Frage:**
```bash
PROMPT="Deine Frage hier (kompakt, 200-400 Worte)"
TS=$(date +%s)

cd /tmp  # UNC-Path-Safety
copilot -p "$PROMPT" --allow-all-tools > "mllm-copilot-$TS.out" 2>&1 &
codex exec --skip-git-repo-check "$PROMPT" > "mllm-codex-$TS.out" 2>&1 &
echo "$PROMPT" | GEMINI_API_KEY="$GEMINI_KEY" gemini -p "Antworte adversarial kompakt Deutsch." > "mllm-gemini-$TS.out" 2>&1 &
grok -p "$PROMPT" > "mllm-grok-$TS.out" 2>&1 &
wait

# Alle 4 Outputs verfuegbar. Claude liest sie + synthesiert.
```

**Anti-Patterns Option C:**
- **Alle 5 CLIs bei Trivialfrage** → Overhead > Nutzen
- **Kein Timeout** → CLIs haengen, Script haengt. Verwende `timeout 60 copilot -p ...`
- **Output nicht validieren** → mache IMMER quick-scan ob Output `.out` nicht leer / error-ridden ist

**Pflicht bei Option C:**
- Jeder parallele CLI-Call kriegt `timeout N` (60-180s)
- Outputs werden VOR Aggregation auf Mindest-Laenge (>= 100 Chars) geprueft
- Bei Timeout → retry **einmal** mit halbiertem Prompt, danach markiere LLM als unavailable fuer diese Runde

### Schritt 3: Antworten einsammeln (Martin)

Martin kopiert alle 4-5 Antworten in Chat an Claude (oder speichert als Dateien).

### Schritt 4: Cross-LLM-Konsolidierung (Claude)

Claude wendet 4/7-Regel an (CLAUDE.md §15):
- 4/5 stimmen zu → **VALIDATED** (HARDENED)
- 3/5 stimmen zu → **NEEDS_REVIEW** (CONDITIONAL)
- <3/5 → **DISPUTED** (Rueckfrage an Martin)

Claim-Level-Analyse (nicht Answer-Level):
- Extrahiere einzelne Claims aus jeder Antwort
- Cross-ref via semantischer Similarity
- Score >= 11/20 → Canon-Kandidat

### Schritt 5: Synthese + Persistenz

- Synthese-Report in `branch-hub/findings/MULTI-LLM-<thema>-<datum>.md`
- Kern-Claims in Subnautica-Fragment-Map-Ergaenzung
- Wenn K_0-relevant: Decision-Card in `docs/decision-cards/`

## Wann nutzen

| Scenario | Multi-LLM-Gebrauch |
|----------|-------------------|
| Code-Writing | Copilot + ChatGPT Codex parallel |
| Research-Frage | Perplexity (Quellen) + Grok (Provokation) + Claude (Synthese) + GPT (Breite) |
| Architektur-Entscheidung | Alle 5 (max Breadth) |
| Quick Fact-Check | Perplexity allein |
| Deep Debug | Claude + Copilot (2 Augen) |

## Claim-Kalibrierung (pro LLM)

Empirisch (2026-04-18, Startwerte — werden via BIAS-Catalog justiert):

| LLM | Konfidenz bei Fakten | Konfidenz bei Meta | Konfidenz bei Code |
|-----|---------------------|--------------------|--------------------|
| Claude Opus 4.7 | 0.85 | 0.75 | 0.80 |
| GPT-5 (Codex) | 0.80 | 0.70 | 0.85 |
| Grok Ultra Pro | 0.70 | 0.75 | 0.70 |
| Perplexity | 0.90 (mit Quellen) | 0.60 | 0.60 |
| Copilot Pro+ | 0.75 | 0.55 | 0.90 |

Gewichtete Konfidenz-Berechnung bei Cross-LLM-Synthese:
`confidence_final = Sum(w_i * c_i * agreement_i) / Sum(w_i)`

## Kosten-Bewusstsein

Martin zahlt bereits:
- Claude (diese Session)
- GitHub Copilot Pro+ (~$19/Mo)
- ChatGPT Pro (~$20/Mo)
- Grok Ultra Pro (~$30/Mo)
- Perplexity Ultimate Pro (~$40/Mo)

**Gesamt ~$110/Mo** (1.3k/J). Bereits bezahlt = marginal cost fuer zusaetzliche Queries = 0.
**Nicht-Nutzung = Zeitwert-Verstoss**: Idle-Kosten ohne Nutzen.

## CRUX-Bindung

- **rho**: Multi-LLM + Synthese = 2-3x schnellere Research vs. single-LLM. rho-Gain 50-150k/J.
- **Q_0**: Cross-LLM-Validation verbessert Antwort-Qualitaet (4/7-Regel).
- **W_0**: Direkt erhoeht (Wissens-Assimilation beschleunigt).
- **K_0**: geschuetzt durch Gray-Team-Pattern (Grok als Provokateur findet blinde Flecken).

## Anti-Patterns

- **Nur Claude fragen** wenn Frage breiter ist als Claude's Trainings-Cutoff.
- **Antworten nicht cross-checken** — dann kein Added-Value vs. Single-LLM.
- **Alle 5 LLMs fragen bei Quick-Fact** — Overhead > Nutzen, Perplexity allein reicht.

## Meta-Lern-Hinweis

Dieser Skill ist **Ordnung 3** (Meta-Methoden) aus dem Meta-Lern-Kristall
(`areas/family/META-LERN-KRISTALL-5-ORDNUNGEN-SUPER-SYSTEM.md`). Validierung:
pragmatisch (funktioniert oder nicht, gemessen an rho-Gain).

[CRUX-MK]
