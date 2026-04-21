---
name: parallel-subagent-dispatch
description: |
  Orchestriert 2-3 parallele Subagenten + Flat-LLM-Dispatches fuer substantielle Projekte (>1h Claude-Zeit).
  Hebelt Faktor 5-8 Token-Ersparnis durch 1:13 Coordinator:Worker-Ratio (empirisch MYZ 2026-04-19).
  Triggers: "parallel dispatch", "3 subagenten", "faktor 5-8 token", "multi-subagent-coordinator",
    automatisch bei Projekten die in 2-4 unabhaengige Sub-Tasks zerlegbar sind (Template-Extraktion,
    Cross-LLM-Audit, DF-Scaffold, E2E-Pilot).
  Capability: Token-sparsamer Multi-Subagent-Workflow mit ECONNRESET-Handling + Summary-Return-Pattern.
  NICHT: fuer K_0/Q_0/Phronesis-Tasks (Claude-Opus only) oder wenn Tasks stark dependent sind.
crux-mk: true
version: 0.1.0-scaffold
meta-ebene: E3
origin: FINDING-TOKEN-EFFICIENCY-PATTERN-MYZ-2026-04-19
status: SCAFFOLD (Martin-Approval via F09 erhalten 2026-04-19)
depends-on:
  - rules/token-engpass-hierarchie.md
  - rules/context-budget.md §2 (Max 3 Subagenten)
  - rules/copilot-cli-first.md + chatgpt-pro-first.md + grok-heavy-first.md
---

# parallel-subagent-dispatch [CRUX-MK]

## Wann nutzen

- Substantielle Projekte >1h Claude-Zeit
- Task zerlegbar in 2-4 unabhaengige Sub-Tasks
- Flat-LLMs (Codex/Gemini/Copilot/Grok) koennen Heavy-Lifting uebernehmen
- Claude-Opus bleibt Coordinator + Final-Synthesizer

**NICHT fuer:** K_0/Q_0/Phronesis-Tasks (Claude-Opus only), stark dependent Tasks (A blockt B blockt C).

## 7 Kern-Prinzipien (empirisch MYZ 2026-04-19)

1. **P1 Claude-Opus = Coordinator, nicht Writer** (max 10% Tokens)
2. **P2 Parallel-Dispatch > Sequentiell** (3 Subagenten gleichzeitig, Kulminationspunkt aus context-budget.md §2)
3. **P3 Subagent-Summary-Return** (~15k statt 200k+ Full-Transcript)
4. **P4 Flat-LLM-Abo maximal nutzen** (Sunk-Cost-Amortisation)
5. **P5 ECONNRESET != Task-Fail** (File-System-Check vor Retry)
6. **P6 Subagent-Prompt-Kompakt-Muster** (siehe Template unten)
7. **P7 Anti-Pattern Sequentielle-Subagent-Kette** vermeiden

## Prompt-Template (fuer Subagent-Dispatch)

```
<ROLLE>: Subagent fuer [Task-Typ] [CRUX-MK].

<KONTEXT>: 1-2 Saetze Framework-Status, wichtige Artefakt-Pfade.

<BASELINE-PFLICHT-LEKTUERE>: 1-2 Finding-Pfade als Format-Vorlage.

<AUFTRAG>: Konkrete Deliverables (T1/T2/T3 Struktur, Zeilen-Range, Frontmatter-Pflichten).

<PFLICHT-FELDER>: genaue YAML-Keys die erwartet werden.

<BUDGET>: max Xh, max Y Reads, Kaestner-Ton.

<MELDE AM ENDE>: Pfad + Zeilen + Kern-Metriken.
```

## rho-Quantifizierung

**Ohne Pattern (Claude-only):**
- ~500-800k Opus-Tokens fuer substantiellen Output
- ~12-20h real time

**Mit Pattern (Multi-Subagent):**
- ~80-100k Opus-Coordinator-Tokens
- ~6h real time

**Faktor 5-8 Token-Ersparnis + Faktor 2-3 Zeit-Ersparnis.** Bei Lambda 10-20 Sessions/Monat = **+200-400 EUR/Monat** Claude-Ersparnis.

## CLI-Commands (Template)

```bash
# 3 Subagenten parallel in Background
Agent(description="Task A", ..., run_in_background=true)
Agent(description="Task B", ..., run_in_background=true)
Agent(description="Task C", ..., run_in_background=true)

# ODER: Codex+Gemini parallel-Dispatch via Shell
cd /tmp
echo "" | codex exec --skip-git-repo-check "$PROMPT" > codex.out 2> codex.err &
echo "$PROMPT" | gemini -p "kompakt Deutsch" > gemini.out 2> gemini.err &
wait
```

## ECONNRESET-Handler (P5)

Bei Subagent-ECONNRESET:
1. **Erst pruefen:** `ls <expected-output-path>` + `wc -l <file>`
2. Wenn Datei mit erwarteter Groesse existiert: Task erfolgreich, **kein Retry**
3. Nur wenn Datei fehlt/leer: Retry dispatch

**Belegt durch:** MYZ00011 Subagent 747s ECONNRESET, File war trotzdem 757 Zeilen vollstaendig.

## Anti-Patterns

1. **Sequentielle Kette** bei unabhaengigen Tasks — Kapazitaet liegt brach
2. **Full-Transcript-Return** statt Summary — Coordinator-Context explodiert
3. **Retry ohne File-Check** bei ECONNRESET — doppelte Token-Kosten
4. **Claude-Opus schreibt lange Code-Blocks** wenn Codex/Copilot koennen
5. **Subagent fuer K_0-Decisions** — NIEMALS delegieren
6. **Mehr als 3 Subagenten gleichzeitig** — Kulminationspunkt (context-budget.md §2)

## Empirische Belegung

Session MYZ-Graphity-Framework 2026-04-19:
- 4 Subagenten dispatched (MYZ00008/00009/00010/00011 C1-C5-Templates)
- 3 parallele Wave-3-Subagenten (E2E-Pilot + Framework-Audit + DF-09-Scaffold)
- 20-25 Codex+Gemini+Grok-Flat-LLM-Dispatches
- **Claude-Opus ~170k Tokens** (Coordinator)
- **Flat-LLMs ~2M+ Tokens** (Worker)
- **Ratio 1:13 Coordinator:Worker empirisch**
- **45+ Artefakte produziert** in ~9-10h

## Promotion-Pfad

- v0.1.0-scaffold (jetzt, 2026-04-19, Martin F09 JA)
- Nach 3 erfolgreichen Branch-Adoptionen: promote zu **rules/parallel-subagent-dispatch.md** als Pflicht-Pattern (F11 JA)
- Parallel: Archon-Workflow `multi-subagent-coordinator` (F10 JA, pending)

## CRUX-Bindung

- **K_0:** geschuetzt (keine Delegation von K_0-Decisions)
- **Q_0:** erhoeht (Cross-LLM-Konsens via parallele Flat-LLMs)
- **I_min:** strukturiert (Pattern reproduzierbar)
- **W_0:** direkt **faktor 5-8 optimiert** — Martin's Primaer-Engpass

## Referenz

- Vollstaendige Herleitung: `branch-hub/findings/FINDING-TOKEN-EFFICIENCY-PATTERN-MYZ-2026-04-19.md`
- Memory-File: `feedback_token_efficient_multi_subagent.md`
- Inbox-Broadcast: `branch-hub/inbox/to-all-branches-token-efficiency-2026-04-19.md`

[CRUX-MK]
