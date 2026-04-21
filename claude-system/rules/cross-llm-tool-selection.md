---
name: cross-llm-tool-selection
description: Pre-Flight-Pflicht Tool-Wahl fuer Cross-LLM-Research. Vermeidet wiederholte Codex-Sandbox-Hangs auf JS-Docs, Firecrawl-No-API-Fehler, Gemini-File-Contamination. Basiert auf F416 empirische Hierarchie.
type: rule
meta-ebene: E3
status: ACTIVE-MODIFY-v2-PENDING (C1-Wargame 2/3 MODIFY 2026-04-19)
modify-v2-schaerfungen: [Prinzipienbasierter Decision-Tree statt Tool-Whitelist, 90d-Auto-Revaluierung, Timeout+Fallback-Klausel, Lambda>=10-Schwelle als Aktivierungs-Trigger, Obsoleszenz-Check bei CLI-Version-Updates]
c1-wargame-finding: branch-hub/findings/FINDING-C1-PROPOSAL-RULES-WARGAME-2026-04-19.md
c1-wargame-detail: branch-hub/cross-llm/2026-04-19-WARGAME-C1-cross-llm-tool-selection.md
created: 2026-04-19
aktiviert: 2026-04-19
cross-llm-reference: F416 aus Subnautica-Fragment-Map-Ergaenzung-T
claim-type: empirical (falsifizierbar durch >2 Faelle wo Hierarchie versagt)
---

# Cross-LLM-Tool-Selection [CRUX-MK] — PROPOSAL

## Zweck
Pre-Flight-Tool-Wahl-Checklist fuer Cross-LLM-Research. Verhindert 5+ Min Codex-Hangs auf JS-Docs durch strukturierte Tool-Zuordnung.

## Regel

### R1 Ziel-URL-Klassifikation vor Tool-Wahl
Pro Research-Task: Klassifiziere Ziel in 4 Kategorien:
1. **Training-only** (allgemeines Wissen, keine URL): Codex + Gemini-isolated parallel
2. **Statische Docs** (einfaches HTML, Markdown, PDFs): WebFetch zuerst, dann Firecrawl-scrape
3. **JS-rendered Docs** (SPAs, React-Docs, MEWS-help): **Firecrawl-scrape mit JS-Mode** zuerst, NICHT Codex
4. **Auth-gated** (Login-Pflicht): Chrome-MCP oder Firecrawl-Instruct

### R2 Empirisch belegte Inkompatibilitaets-Liste
- Codex CLI + MEWS-JS-Docs: 2x gehangen (Welle-3+4), verbotene Kombi
- WebFetch + help.mews.com: 401-Fehler (auth-gated)
- Native WebSearch + MEWS-partners-page: ok

### R3 API-Key-Pflicht-Setup
Vor Cross-LLM-Research-Session:
- FIRECRAWL_API_KEY (User-Env) pruefen
- GEMINI_API_KEY (User-Env) pruefen
- Wenn fehlt: STOP + Setup-Anweisung

### R4 Pre-Flight-Checklist
Subagent-Prompt muss enthalten:
- Ziel-URL-Klassifikation (Training/Static/JS/Auth)
- Tool-Wahl-Begruendung (1 Satz)
- Fallback-Plan wenn Primary-Tool versagt

### R5 Post-Call-Verdict
Wenn Tool versagt (timeout, 0-Byte-Output, Auth-Fehler):
- LOG in `branch-hub/learnings/tool-compatibility.jsonl`
- Markiere Tool+Ziel-URL-Domain als "inkompatibel"
- Fallback-Tool aktivieren

## Mechanik
- Pre-Spawn-Check via Skill `cross-llm-tool-selection`
- Post-Call-Audit in tool-compatibility.jsonl
- Monatlicher Review: Patterns ersichtlich?

## Anti-Patterns
- Codex als Default fuer JS-Docs
- "Vielleicht geht's dieses Mal" ohne Pattern-Check
- API-Keys zur Laufzeit setzen statt Pre-Flight

## SAE-Isomorphie
MYZ-36 Meta-Prompting-Router: Jedes Tool hat Expertise-Profil, Router waehlt nach Use-Case.

## CRUX-Bindung
- K_0: Opus-Token-Schutz (5+ min Codex-Hang = verschwendete Tokens)
- W_0: Research-Velocity (min Time-to-Insight)
- I_min: strukturierte Tool-Zuordnung

## rho-Impact
5-15k EUR/J (verhindert wiederholte Codex-Sandbox-Loops).

## Falsifikations-Bedingung
- Wenn 3+ Faelle Codex erfolgreich auf JS-Docs → R2 revidieren
- Wenn Firecrawl-JS-Mode bei MEWS ebenfalls versagt → Alt-Tool-Liste anpassen

## Selbst-Anwendung
G1 ok (Rule beschreibt Tool-Wahl, ist selbst nicht-Tool). G6 falsifizierbar.

[CRUX-MK]
