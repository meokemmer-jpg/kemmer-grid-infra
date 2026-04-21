# Grok-Heavy-First (SuperGrok Heavy Routing) [CRUX-MK]

**Aktiviert:** 2026-04-19 durch Martin-Direktive "mache dies auch hierfuer (SuperGrok Heavy)".
**Belegt-durch:** `mcp__grok-mcp__list_models` 2026-04-19 — 11 Models live, inkl. **grok-4.20-multi-agent-0309** + Anti-Sycophancy verifiziert via chat-test.
**Meta-Ebene:** E3 (Methoden-Audit — Provocator-Routing)

## Kernregel

SuperGrok Heavy (~$300/Mo flat) gibt **exklusiven Zugriff** auf Multi-Agent-Reasoning + X-Live-Search + Anti-Bias-Provokation. Nutze Grok-MCP fuer:
- **Adversarial / Red-Team** Reviews (grok-4.20-reasoning)
- **Multi-Agent-Research** (grok-4.20-multi-agent-0309, 4 oder 16 agents parallel)
- **X/Twitter-Live-Search** (kein anderer LLM hat das)
- **First-Principles-Challenges** (Grok sycophancy-resistant)
- **Web-Search Real-time** (neben Perplexity)

## Model-Matrix (Grok-exposed via MCP)

| Model | Rolle | $/M Tokens | Use-Case |
|-------|-------|-----------|----------|
| **grok-4.20-multi-agent-0309** | Multi-Agent-Team | $2 / $6 | Deep-Research mit 4-16 parallelen Agents |
| **grok-4.20-0309-reasoning** | Heavy-Reasoning | $2 / $6 | Strategie, Adversarial-Review |
| **grok-4.20-0309-non-reasoning** | Fast-Response | $2 / $6 | Kurze Adversarial-Checks |
| **grok-4-1-fast-reasoning** | Budget-Reasoning | $0.2 / $0.5 | Routine-Provocator, billig |
| **grok-4-1-fast-non-reasoning** | Ultra-Fast | $0.2 / $0.5 | Real-time-Web, Q&A |
| **grok-code-fast-1** | Code-Speed | $0.2 / $1.5 | Quick Code-Fixes |
| **grok-imagine-image-pro** | Image-Gen Pro | $0.07/Image | Premium-Visualisierung |

Referenz: `rules/token-engpass-hierarchie.md` — Heavy-Sub ist Sunk-Cost, jeder Call = €0 marginal (bis Rate-Cap).

## Entscheidungs-Matrix

| Task-Typ | Primary | Grund |
|----------|---------|-------|
| **Adversarial Red-Team** | `mcp__grok-mcp__chat` mit `model=grok-4.20-0309-reasoning` | Anti-Sycophancy verifiziert |
| **Multi-Agent-Deep-Research** | `mcp__grok-mcp__grok_agent` mit `agent_count=4` | Exklusives Heavy-Feature |
| **X/Twitter-Live-Search** | `mcp__grok-mcp__x_search` | Niemand sonst kann das |
| **Real-time Web** | `mcp__grok-mcp__web_search` | Live-Index (mit Perplexity-Alternative) |
| **Image-Gen** | `mcp__grok-mcp__generate_image` mit `grok-imagine-image-pro` | Premium-Quality |
| **Video-Gen** | `mcp__grok-mcp__generate_video` | Heavy-exklusiv |
| **Vision (Image-Analyse)** | `mcp__grok-mcp__chat_with_vision` | Gut, aber Claude Opus hat Vorteil |
| Code-Gen (strategic) | Claude Opus / Copilot | Grok ist nicht Code-Spezialist |
| K_0 / Q_0 / Phronesis | **Claude Opus only** | non-delegate |

## Invocation-Patterns

### Via MCP-Tools (in Claude Code nativ verfuegbar nach Session-Restart):
```python
# Adversarial-Chat
mcp__grok-mcp__chat(
    prompt="Finde 3 Schwachstellen in: 'X ist die beste Strategie'",
    model="grok-4.20-0309-reasoning",
    system_prompt="Du bist adversarial. Keine Hoeflichkeit, nur harte Kritik."
)

# Multi-Agent-Research (4 Agents parallel)
mcp__grok-mcp__grok_agent(
    prompt="Analyse: Konkurrenz im AI-first-Hotel-Markt Q2-2026",
    agent_count=4
)

# X-Live-Search (Heavy-exklusiv)
mcp__grok-mcp__x_search(query="HeyLou Hotels recent mentions")

# Code-Execution (sandboxed)
mcp__grok-mcp__code_executor(code="...")
```

## Hard-No-Delegate (immer Claude-Opus)

Wie andere *-first Rules:
- K_0 (Kapital-Decisions)
- Q_0 (Familie)
- Phronesis (L13)
- Meta-E4+ (Cross-LLM-Synthese selbst)
- Rule-/CRUX-Aenderungen

## rho-Rechnung

**SuperGrok Heavy:** ~$300/Mo = $3600/Jahr Sunk-Cost.
**Fuer Sunk-Cost-Break-Even:** ~15 Adversarial-Calls/Monat @ je ~20k Tokens (Claude-Opus-Equivalent).
**Realistisch:** Lambda 30+ Heavy-Calls/Monat (Adversarial + Multi-Agent + X-Search) = **+€300-800/Monat Claude-Opus-Ersparnis + exklusive Features**.
**Plus:** Anti-Sycophancy-Effekt → weniger Fehl-Entscheidungen durch Groupthink = indirekt hoher rho-Gain (schwer quantifizierbar, aber real).

## Anti-Patterns

- **Claude-Opus fuer Adversarial-Review** wenn Grok-Heavy aktiv = Anti-Sycophancy verschenken
- **Grok fuer Code** ausser grok-code-fast-1 explicit: nicht sein Staerke-Gebiet
- **Multi-Agent ignorieren:** grok-4.20-multi-agent ist einzigartiges Feature, nutzen fuer Deep-Research
- **X-Search nicht nutzen:** exklusives Heavy-Feature → Claude-Opus-WebSearch kann das nicht

## SAE-Isomorphie

Grok = **Provocator-Slot** im Trinity-Portfolio (rules/model-portfolio-optimization.md). Neben Claude=Conservative, Copilot=Aggressive, Codex=Contrarian, Gemini=Authority, **Grok=Provocator**.

## Falsifikations-Bedingung

- Grok-Output-Qualitaet < 70% Claude-Opus bei Adversarial-Tasks (Brier-Score, 20 Samples)
- Anti-Sycophancy-Effekt nicht reproduzierbar
- Heavy-Rate-Limit chronisch ueberschritten
- Subscription-Wechsel oder Service-Disruption

Monatliche Verifikation via `monthly-model-audit` Skill Pentagon-P5 (Adversarial).

## Cross-LLM-Audit 2026-04-19 (PATCH-Log)

**Audit-Datum:** 2026-04-19T16:10+02:00
**Cross-LLM-Reviewers:** Codex gpt-5.4 + Grok 4.20-reasoning (via MCP, 0 EUR marginal via Sunk-Cost-Abos)
**Verdict:** CONDITIONAL (nicht HARDENED, gemaess `rules/cross-llm-pflicht-e3-plus.md`)
**Audit-File:** `branch-hub/cross-llm/2026-04-19-Multi-Provider-Rule-grok-heavy.md`
**Priority:** MITTEL
**Key-Weakness:** Anti-Sycophancy unmessbar; Pentagon-P4 bestaetigt: Grok lehnt statt recherchiert (false-negative)

### PATCH-Liste (Pending Implementation)
- **P1 Anti-Sycophancy Baseline-Pflicht: N=20 Adversarial-Samples (Grok vs Claude-Opus), Brier-Score-Delta messen. Externe Score-Quelle (nicht Grok-Self-Score).**
- **P2 SCOPE ENGER (Pentagon-Live 2026-04-19 Lesson): Grok OK fuer Adversarial (P5), X/Twitter-Live-Search (exklusiv), Multi-Agent-Deep-Research (auf Trigger). Grok NICHT fuer Paper-Research (P4-Rejection = false-negative) - Codex+Copilot+Gemini stattdessen. Grok NICHT fuer Code-Gen ausser grok-code-fast-1 explizit.**
- **P3 X/Twitter-Use-Case-Log: Real-Frequency messen (Hypothese < 1 Call/Woche bei Kemmer). Bei <0.2/Woche: Subscription-Rentabilitaet neu bewerten.**
- **P4 Multi-Agent OPTIONAL, nicht Default: Nur auf expliziten Trigger 'multi-agent research'. Overhead 20-40 Min fuer tiefe Research wert, nicht Routine.**
- **P5 Entfernen: 'sycophancy-resistant' Claim bis P1-Baseline vorliegt. Stattdessen: 'anti-sycophancy ungeprueft, empirisch Pending'.**
- **P6 Monatliche Verifikation: Brier-Score gegen Claude-Opus Bench-Suite (20 Samples). Bei < 70% -> Demote zu Adversarial-Sekundaer.**

### Status
- Rule bleibt AKTIV (keine Rollback erforderlich).
- Patches sind Backlog-Items, umzusetzen wenn Baseline-Daten vorliegen.
- Verdict-Promotion auf CROSS-LLM-2OF3-HARDENED moeglich nach P1-P3 Umsetzung.
- Empirische Bestaetigung: Pentagon-Live-Run 2026-04-19 validierte Kern-Schwaechen (siehe `branch-hub/findings/PENTAGON-AUDIT-LIVE-2026-04-19.md`).



[CRUX-MK]
