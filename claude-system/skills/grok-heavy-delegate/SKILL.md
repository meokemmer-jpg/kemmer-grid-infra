---
name: grok-heavy-delegate
description: Delegiert Adversarial-Reviews, Multi-Agent-Research, X-Live-Search, Real-time-Web an Grok via MCP (mcp__grok-mcp__*). Triggers "ask grok", "grok challenge", "x search", "multi-agent research", automatisch bei Adversarial-Tasks + Real-time-Web-Bedarf. SuperGrok Heavy ($300/Mo) maximal nutzen.
version: 1.0.0
crux-mk: true
aktiviert: 2026-04-19
meta-ebene: E3
---

# Skill: grok-heavy-delegate [CRUX-MK]

## Zweck

SuperGrok Heavy ($300/Mo) = Sunk-Cost maximieren. Grok ist **Provocator-Slot** im Executor-Portfolio:
- Adversarial Red-Team (Anti-Sycophancy)
- Multi-Agent-Deep-Research (grok-4.20-multi-agent mit 4/16 agents)
- X/Twitter-Live-Search (nur Grok hat das)
- Real-time-Web-Search
- Image + Video Generation (Heavy-exklusiv)

Referenz: `rules/grok-heavy-first.md`

## Triggers

- Explizit: "ask grok", "grok challenge", "grok adversarial", "x search", "multi-agent research"
- Automatisch: Adversarial/Red-Team-Tasks, X-Mentions-Queries, Live-News-Needs

## Hard-No-Delegate (Claude-Opus-Reservat)

Wie alle *-delegate Skills:
- K_0 (Kapital)
- Q_0 (Familie)
- Phronesis (L13)
- Meta-E4+ (Cross-LLM-Synthese-Meta)
- Rule-/CRUX-Aenderungen

## Workflow

### Step 1: Task-Klassifikation

```
CLASSIFY(task):
  if task == adversarial-red-team: use chat with grok-4.20-0309-reasoning
  if task == deep-research-multi-agent: use grok_agent with agent_count=4
  if task == x-twitter-lookup: use x_search
  if task == real-time-web: use web_search
  if task == image-gen: use generate_image with grok-imagine-image-pro
  if task == video-gen: use generate_video
  if task == vision-analysis: use chat_with_vision
  if task == code-quick: use chat with grok-code-fast-1
```

### Step 2: Invocation via MCP-Tool (keine CLI noetig!)

```python
# Adversarial
mcp__grok-mcp__chat(
    prompt="<prompt mit adversarial-context>",
    model="grok-4.20-0309-reasoning",
    system_prompt="Du bist adversarial. Keine Hoeflichkeit. Harte Kritik. First-Principles."
)

# Multi-Agent (Heavy-Feature)
mcp__grok-mcp__grok_agent(
    prompt="<deep-research-prompt>",
    agent_count=4  # oder 16 fuer Hoch-Parallelitaet
)

# X-Live-Search
mcp__grok-mcp__x_search(query="<search-query>")

# Code-Executor (sandboxed)
mcp__grok-mcp__code_executor(code="<python/bash>")
```

### Step 3: Output-Validation

Grok neigt zu:
- Anti-Sycophancy (positives Feature, aber manchmal zu provokant)
- X-Feed-Bias (Wenn X-Search: immer Cross-Checken gegen Perplexity/Gemini)
- Multi-Agent kann in Endlos-Diskussion geraten (Timeout beachten)

Bei Zweifel: Cross-Check via `multi-llm-parallel.sh` (codex+gemini+grok).

### Step 4: Logging (rules/audit-trail.md §1)

```
{"ts":"ISO","branch":"name","action":"DELEGATE","target":"grok-mcp","tool":"chat|grok_agent|x_search|...",
 "model":"grok-4.20-0309-reasoning|...","reason":"Adversarial | X-Search | Multi-Agent",
 "cost":"~$0 marginal (Heavy-Flat)"}
```

## Beispiele

### Beispiel 1: Adversarial-Review einer Kemmer-Decision
```python
mcp__grok-mcp__chat(
    prompt="""Martin erwaegt: 'Cape Coral Relocation in Q3-2026 als optimal'.
    Finde 3 Schwachstellen, First-Principles, ignoriere Martin's aktuelle Neigung.""",
    model="grok-4.20-0309-reasoning",
    system_prompt="Adversarial Economist. Keine Emotionen, nur Zahlen + Logik."
)
```

### Beispiel 2: Multi-Agent-Konkurrenz-Research
```python
mcp__grok-mcp__grok_agent(
    prompt="""Analysiere 4 Konkurrenten von HeyLou Hotels (AI-first, EU-Markt):
    (1) Funktionalitaet, (2) Pricing, (3) Tech-Stack, (4) Lucken-in-Markt.
    Parallel je 1 Agent pro Aspekt. Output: Strukturiert.""",
    agent_count=4
)
```

### Beispiel 3: X-Live-Search fuer Kemmer-Brand-Monitoring
```python
mcp__grok-mcp__x_search(query="HeyLou OR 9dots mentions last 30d")
```

### Beispiel 4: Real-time-Web Fact-Check
```python
mcp__grok-mcp__web_search(query="MWSt Gastronomie Deutschland 2026 Gesetz")
# Gut fuer K_0-Alert-Verifikation (aus Pentagon-POC MWSt-Konflikt)
```

## rho-Impact

SuperGrok Heavy = $300/Mo Sunk-Cost:
- **Break-Even:** ~15 Adversarial-Calls/Monat (@ Claude-Opus-Equivalent ~$20/Call)
- **Realistisch:** Lambda 30+ = **+€300-800/Monat** reine Token-Ersparnis
- **Plus:** Anti-Sycophancy-Gain (weniger Fehl-Decisions) = indirekt substanziell
- **Exklusive Features:** X-Search, Multi-Agent = nicht substituierbar

## Integration in Meta-Harness

- **DF-07 Pentagon-Wargame:** Grok ist Default-Provider (`PENTAGON_PROVIDERS` in config.py)
- **multi-llm-parallel.sh:** Grok nutzt CLI (`grok -p`) fuer Parallel-Runs
- **DF-03 v2.2 geplant:** Grok als 4. Provider fuer Adversarial-Triangulation (nach Codex-Synth + Gemini-Cross-Check + Copilot-Triangulate)

## Falsifikations-Bedingung

- Grok-Adversarial-Qualitaet < 70% Claude-Opus (Brier-Score, 20 Samples monatlich via DF-07)
- Anti-Sycophancy-Effekt nicht reproduzierbar → Downgrade Grok-Rolle
- Heavy-Rate-Limit chronisch ueberschritten → zurueckdrehen
- MCP-Server down / merterbak/Grok-MCP nicht mehr gepflegt → alternativer MCP-Server suchen

Monthly-Review via `monthly-model-audit` Pentagon-P5 (Adversarial-Prompt).

[CRUX-MK]
