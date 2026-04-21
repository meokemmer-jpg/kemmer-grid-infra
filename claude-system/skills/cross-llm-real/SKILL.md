---
name: cross-llm-real
description: Echte Cross-LLM-Validation mit Claude + Gemini Ultra + ChatGPT Pro (Codex). Upgrade zu HARDENED-Verdict statt CROSS-LLM-SIMULATION-HARDENED. Triggers bei K_0-relevanten Entscheidungen, Blueprint-Formalisierung, Verfassungs-Rang-Aenderungen, Cross-Validation-Pflicht.
triggers:
  - "cross-llm validieren"
  - "echtes cross-llm"
  - "bei K_0 alle drei fragen"
  - "consensus check claude gemini gpt"
  - auto-triggered bei Blueprint-Verdict >= K_0-Naehe
crux-mk: true
status: PROPOSAL
author: Opus 4.7 (1M) Architekt-2
created: 2026-04-18
---

# Cross-LLM-Real Skill [CRUX-MK]

## Zweck

**Upgrade rule cross-llm-simulation.md §5 zu echtem HARDENED:**
- Single-Modell-Simulation (4 Perspektiven im selben LLM) = CROSS-LLM-SIMULATION-HARDENED (praxistaugliche Zwischenstufe)
- **Echtes** 3-Modell-Cross-LLM (Claude + Gemini Ultra + ChatGPT Pro) = voll HARDENED

Condorcet-Jury-Theorem (F70): 3 unabhaengige Modelle > 1 Modell x 3 Perspektiven (Korrelation 1.0 vs Korrelation <1).

## Trigger-Schwellen

### PFLICHT (automatisch bei folgenden Kontexten)
1. **K_0-Relevanz**: Empfehlungen die Kapital-Allokation, Wegzugssteuer, Konten-Struktur betreffen
2. **Blueprint-Formalisierung**: B-Nummer wird von INBOX/CANDIDATE → HARDENED gepromoted
3. **Rule-Aenderung**: Neue Rule in `~/.claude/rules/` oder Rule-Edit
4. **Verfassungs-Rang**: CLAUDE.md-Aenderung oder rules/crux.md-Aenderung
5. **Cape-Coral-Timing-Entscheidungen**: P1-P4-Pfade
6. **SAE-/KPM-/9OS-Architektur-Entscheidungen** mit Reichweite >6 Monate

### KANN (Martin-Discretion)
- Wissenschafts-/Mathematik-Beweise (Formel-Sweep-Gegenpruefung)
- Buchprojekt-Kapitel-Haertung (Mathematik der Macht, Symbiotic Minds)
- Strategische Szenarien (Sensitivity-Analyse)

### SKIP (kein Cross-LLM)
- Tool-Aufrufe / Code-Refactoring / Typo-Fixes
- Routinemaessige Welle-NLM-Extraktion (ausser K_0-beruehrt)
- Persoenliche Chat-Konversation

## Ausfuehrung

### Phase 1: Prompt-Vorbereitung
```
PROMPT_KERN = "<die konkrete Frage oder der zu haertende Claim>"
PROMPT_KONTEXT = "<relevante CRUX-Nebenbedingungen, Vor-Arbeit, Datenlage>"
```

### Phase 2: Parallel-Anfrage (3 CLIs in Parallel)
```bash
# Claude (ich, direkt)
CLAUDE_ANSWER = "<meine strukturierte Antwort mit 4 Bloecken: Pattern/What-Doesnt-Fit/Frage/Empfehlung>"

# Gemini Ultra
echo "$PROMPT_KERN $PROMPT_KONTEXT" | gemini -p "Adversarial Haertung als unabhaengiger Experte. CRUX = max Integral(rho*L) ueber T_life. Nebenbedingungen K_0, Q_0, I_min, W_0. Antworte in 4 Bloecken: Pattern/What-Doesnt-Fit/Frage/Empfehlung. Sei hart."

# ChatGPT Pro (via Codex)
codex exec --model gpt-5 "Adversarial Haertung als unabhaengiger Experte. CRUX = max Integral(rho*L) ueber T_life. Nebenbedingungen K_0, Q_0, I_min, W_0. Antworte in 4 Bloecken. Sei hart. Prompt: $PROMPT_KERN"
```

### Phase 3: Consensus-Analyse
Pro Kern-Claim:
- **ADOPT** (>=2 von 3 stimmen zu) → HARDENED
- **SPLIT** (1 von 3 stimmt zu oder Auto-Widerspruch) → CONDITIONAL + Diff-Dokumentation
- **REJECT** (0 von 3 stimmen zu) → REJECTED + Begruendung

### Phase 4: Ergebnis-Persistenz
Pro Cross-LLM-Run:
```
G:/Meine Ablage/Claude-Knowledge-System/branch-hub/cross-llm/YYYY-MM-DD-<topic>.md
```
Inhalt:
- Prompt-Kern + Kontext
- Claude-Antwort (strukturiert)
- Gemini-Antwort (strukturiert)
- Codex-Antwort (strukturiert)
- Consensus-Tabelle pro Kern-Claim
- HARDENED/CONDITIONAL/REJECTED-Verdict
- Divergenz-Analyse (bei SPLIT: wer hat was gesagt und warum)

## Invarianten

### I1: Modell-Anonymitaet
Weder Gemini noch Codex erfahren was Claude gesagt hat (sonst Anchoring). Parallel-Anfrage ohne Quer-Kontamination.

### I2: Identischer Prompt-Kern
Exakt derselbe Prompt-Kern an alle 3. Unterschiede nur im Modell-spezifischen Role-Wrap (z.B. Gemini ist "Gemini als unabhaengiger Experte").

### I3: Temperatur-Konsistenz
Default Temperatur 0.7 fuer alle 3 (Standard-Reasoning). Bei Determinismus-Bedarf 0.0.

### I4: Lambda-Honesty
Wenn ein Modell "ich weiss nicht" sagt: das zaehlt als SKIP fuer diesen Claim, nicht als ADOPT/REJECT.

### I5: Kosten-Cap
Max 5 USD pro Cross-LLM-Run (Token-Estimate vorab). Bei >100k Token Context: Kostenwarnung an Martin, Approval-Pflicht.

## Kosten-Nutzen (rho-Analyse)

### Opex pro Run
- Claude (eingebettet, Fix-Kosten)
- Gemini Ultra: ~0.50 USD pro mittleren Prompt
- ChatGPT Pro (GPT-5 via Codex): ~2.00 USD pro mittleren Prompt
- **~2.50 USD pro Run**

### Lambda (erwartete Frequenz)
- K_0-Entscheidungen: ~2-4/Monat
- Blueprint-Formalisierungen: ~5-10/Monat
- Rule-Aenderungen: ~1-2/Monat
- **~10-16 Runs/Monat = 25-40 USD/Monat = 300-480 USD/Jahr**

### Value
- Pro vermiedener Fehlentscheidung mit K_0-Relevanz: 10k-1M EUR
- Break-Even bei 1 vermiedener Fehlentscheidung / Jahr
- Bei Martins K_0-Volumen (20M+ Familien-Vermoegen): einzelne richtige Entscheidung lohnt 100x-1000x

**CRUX-GATE-Verdict:** HARDENED. rho >>0 unter allen realistischen Szenarien.

## Fallback-Regeln

### Bei Modell-Ausfall
- **1 Modell down**: 2-Modell-Run als "CROSS-LLM-2OF3-HARDENED" markieren (unter voll-HARDENED, ueber Simulation)
- **2 Modelle down**: abbrechen, CROSS-LLM-SIMULATION-HARDENED faellt zurueck
- **3 Modelle down**: Martin-Eskalation, keine HARDENED-Faehigkeit

### Bei Budget-Ueberschreitung
- 5 USD-Cap erreicht: STOP + Prompt-Kuerzung vorschlagen
- Wenn Martin explizit mehr genehmigt: OK + rho-Dokumentation

### Bei Divergenz (SPLIT-Verdict)
- Kein automatischer 4. Tiebreaker
- Martin-Phronesis-Eintrag: Entscheidung bei Martin (L13)
- Divergenz-Analyse ist wertvoller als ein erzwungener "Gewinner"

## Integration in bestehende Architektur

### Hook-Punkte
- **Vor Blueprint-HARDENED-Promotion** (Pre-Hook): cross-llm-real automatisch triggern
- **Vor Rule-Write in `~/.claude/rules/`** (Pre-Hook): cross-llm-real triggern
- **Nach Subagent-Verdict mit K_0-Flag**: cross-llm-real als Confirm

### MCP-Server-Setup (separat)
Codex + Gemini als MCP-Server in `~/.claude/settings.json` registrieren:
```json
{
  "mcpServers": {
    "codex": { "command": "codex", "args": ["mcp-server"] },
    "gemini": { "command": "gemini", "args": ["mcp", "serve"] }
  }
}
```
(Syntax ggf. anpassen je nach CLI-Spezifikation)

Dann sind Codex- und Gemini-Tools direkt als Claude-Tools verfuegbar.

## 4-Layer-Task-Verteilung (Martin-Direktive 2026-04-18, Zeitwertverfassung)

Copilot Pro+ mit 13+ Top-Modellen (Opus 4.7, GPT-5.4, Gemini 3.1 Pro, Codex-Varianten) ist bezahlt — Nicht-Nutzung = rho < 0. Distributed-Motors-Prinzip (F15) + Engpass-Primat (TOC).

### Layer 1: Strategisch
- **Tool:** Claude-Code Opus 4.7 1M (dieses Fenster)
- **Task:** Phronesis-Strukturierung, CRUX-Gate-Judgment, Architekt-Entscheidungen, Martin-Sensemaking (L11/L13)
- **Token-Schutz:** Reserviert fuer K_0/Q_0-relevante Entscheidungen
- **Niemals:** Code-Implementation, Canon-Routine-Extraktion

### Layer 2: Orchestrierung
- **Tool:** Claude-Code general-purpose Subagents
- **Task:** Canon-Arbeit, NLM-Welle-Scans, Dedup-Reviews, Blueprint-Formalisierung, MOC-Updates
- **Kosten-Effizienz:** Interne Sonnet/Opus-Wahl, Prompt-Cache geteilt
- **Max 3 gleichzeitig** (rules/meta-calibration §2)

### Layer 3: Code-Execution (NEU, via Copilot-Agent-Mode)
- **Tool:** Copilot-CLI (`copilot` command) oder GitHub.com Agent-Mode
- **Max-Modell-Wahl nach Task:**
  - **Opus 4.7**: Komplexe Logik, SAE-Core, Architektur-Refactoring, BV/COSMOS-Patches
  - **GPT-5.4**: Mathematische Beweise, Formel-Sweep-Deep-Dive, KPM-Backtesting
  - **Gemini 3.1 Pro**: Multimodale Tasks, Diagramme, grosse Codebase-Deep-Research
  - **Codex (GPT-5.2/5.3-Codex)**: Spezialisierte Code-Implementation, Kurzfristig-Refactors
- **Triggers:**
  - Scheduled-Task `sae-v8-adapter-implementation` (schon existent, auf Copilot-Agent umstellen)
  - 9OS Feature-Development
  - SAE v8 Adapter-Implementation (14 Systeme)
  - Deep-Research auf externen Repos (Architektur-Scans)
- **Bridge zu Claude-Code:**
  - Martin startet Copilot-Agent-Task via Webseite ODER
  - Ich rufe `copilot` CLI aus Bash auf (nach Shell-Restart + Auth)

### Layer 4: Cross-Validation
- **Tool:** Codex + Gemini + Claude parallel (siehe Phase 2 oben)
- **Task:** K_0-Entscheidungen, Verfassungs-Rang, Blueprint-HARDENED-Gates
- **Verdict-Stufen:** CROSS-LLM-HARDENED (voll) > CROSS-LLM-2OF3-HARDENED > SIMULATION-HARDENED

### Kosten-Nutzen der 4-Layer-Verteilung

| Ressource | Kostenstelle | Verschwendung bei Nicht-Nutzung |
|-----------|--------------|--------------------------------|
| Claude Pro (ich) | ~200 USD/M | Engpass-Opfer wenn Code/Canon-Routinen hier laufen |
| Copilot Pro+ | ~40 USD/M | 100% Verschwendung wenn nicht fuer Code-Execution genutzt |
| ChatGPT Pro | ~200 USD/M | 100% Verschwendung wenn Codex nicht als Cross-LLM-Validator |
| Gemini Ultra | ~20 USD/M | 100% Verschwendung wenn nicht als Cross-LLM-Validator |
| **Total Opex** | **~460 USD/M = 5520 USD/J** | Bei 0% Nutzung = 5520 EUR/J rho-Verlust. Bei 80% Nutzung = voll im Plus. |

Break-Even bei 1 vermiedener K_0-Fehlentscheidung / 6 Monate = sehr niedrig bei Kemmer-Familien-Vermoegens-Volumen.

### Umstellungs-Schritte (Vorschlag)
1. Auth-Setup (siehe unten)
2. Scheduled-Task `sae-v8-adapter-implementation` umstellen auf Copilot-Agent-Mode (Martin-Pflicht, Web-UI-Setup)
3. Cross-LLM-Real-Skill aktivieren (SKILL.md.PROPOSAL → SKILL.md, nach Martin-Approval P15)
4. MCP-Registrierung (P16) fuer tiefere Integration
5. Neue Rule `rules/task-layer-verteilung.md` (aus diesem Abschnitt extrahieren)

## Rule-Impact

Dieser Skill UPGRADET:
- `~/.claude/rules/cross-llm-simulation.md §5` → neue Stufe "CROSS-LLM-HARDENED" (echtes Cross-LLM) **ueber** CROSS-LLM-SIMULATION-HARDENED. Simulation-Stufe bleibt erhalten als Zwischenstufe wenn Cross-LLM nicht verfuegbar.
- `~/.claude/rules/crux.md` [CRUX-GATE] → "2 Wargames (Adversarial + CRUX-Alignment)" erweitert zu "Adversarial + CRUX-Alignment, bei K_0-Naehe zusaetzlich cross-llm-real Pflicht"

## Martin-Approval-Checkliste (bevor Skill aktiviert)

- [ ] Auth-Setup fertig (siehe unten)
- [ ] MCP-Registrierung in settings.json (wenn gewuenscht)
- [ ] Kosten-Cap 5 USD/Run OK? Oder anders?
- [ ] Lambda-Schaetzung 10-16 Runs/Monat realistisch?
- [ ] Skill-Datei umbennen von SKILL.md.PROPOSAL zu SKILL.md

## Auth-Setup (Martin-Pflicht, einmalig)

```bash
# 1. Shell neu starten (PATH-Aktualisierung fuer copilot/gh/gemini)

# 2. OpenAI/ChatGPT Pro
codex login
# Browser oeffnet sich, OpenAI/ChatGPT-Login

# 3. Google Gemini Ultra
gemini
# Startet interaktiv, waehlt Google-Login aus

# 4. GitHub (fuer Copilot + Repo-Sync)
gh auth login
# Waehlt GitHub.com, Browser-Flow

# 5. GitHub Copilot CLI
copilot
# Loginflow durch Copilot-CLI
```

Nach Setup: Verifikation via
```bash
codex login status
gh auth status
# gemini hat keinen status-Subcommand, aber "echo test | gemini -p" als Test
```

[CRUX-MK]
