---
name: dark-factory-evolve
description: |
  Macht bestehende Dark-Factories schlauer durch Self-Improvement-Loop.
  Triggers: "dark factory schlauer", "dark factory evolve", "auto-improve dark factory <name>",
      "retrospective <factory-name>", automatisch monatlich via scheduled task.
  Capability: Liest Fail-Logs + Reviews + Metrics aus .archon/dark-factory/<name>/
      und generiert Patches: neue Tests, verengter Scope, Model-Downshift, Parallelisierung.
crux-mk: true
version: 1.0.0
origin: opus-4.7-2026-04-17
---

# /dark-factory-evolve [CRUX-MK]

## Was dieser Skill macht

Eine Dark-Factory ohne Evolution veraltert. Failure-Modes haeufen sich, Scope driftet, Kosten steigen. Dieser Skill **haertet** sie monatlich.

## Evolutions-Dimensionen

| Dimension | Signal | Aktion |
|---|---|---|
| **Tests-Coverage** | Fail-Log >0 | Neue Tests aus Fails generieren |
| **Scope-Tightening** | Martin-Rejects im Shadow-Mode >5% | Input-Validation verschaerfen |
| **Model-Downshift** | Stabile Runs mit Sonnet | Testen ob Haiku reicht (75% Cost-Saving) |
| **Parallelisierung** | Queue > 5 items | Workflow-Splits mit worktree-isolation |
| **Budget-Optimierung** | OPEX-Trend steigend | Prompt-Caching + Token-Limits |
| **Deterministic-Lift** | AI-Node konvergiert stabil | AI -> Python-Script (ersetzen) |

## Pentagon-Ablauf

### Phase 1: PLAN - Datensammlung

Pro Dark-Factory `<name>` lese:
```
C:/Users/marti/Projects/learning-archon/.archon/dark-factory/<name>/
├── fail-counter (historische Timeline aus git log)
├── review-log.jsonl (Martin-Approvals/Rejects)
├── audit-entries aus audit/dark-factory.jsonl (letzte 30 Tage)
└── git log (was wurde wie oft reverted)
```

Metriken berechnen:
- Success-Rate (runs ohne Fail / runs total)
- Rollback-Rate (runs mit revert / runs total)
- Cost-per-Run (EUR)
- Lambda_real (runs/Monat) vs Lambda_est
- rho_real vs rho_est
- Martin-Approval-Rate (im Shadow) vs Auto-Approval (im Live)
- Average Runtime (Sekunden)
- Tokens-per-Run Median + P95

### Phase 2: SPEC - Evolution-Kandidaten

Pro Metrik Gegenmassnahme:

**A. Fails > 10% der Runs:**
- Fail-Patterns clustern (per Error-Typ)
- Top-3 Patterns als Test-Cases formulieren
- Add to `tests/` directory
- Add corresponding validation node in workflow

**B. Martin-Rejects > 5%:**
- Reject-Reasons clustern (per free-text-Analyse)
- Scope verengen: Out-of-Scope-Patterns als Hard-Stop-Conditions

**C. Sonnet-Runs stabil (>98% Success bei 30+ Runs):**
- Fork workflow `<name>-haiku` mit model: haiku
- Shadow-Mode 1 Woche
- Wenn >95% Success, replace main workflow
- Cost-Saving dokumentieren

**D. Lambda_real > Lambda_est * 1.5 UND Queue-Delays > 10 Min:**
- Split in parallel-worktree-workflows
- Max-concurrency = 3

**E. OPEX > Budget-Plan:**
- Prompt-Caching einbauen (system prompt separate)
- Context-Reduction: Output-Size-Limit pro Node
- Alternative: Weniger Nodes, mehr Bash-Logik

**F. AI-Node liefert >95% identischen Output-Patterns:**
- Python-Ersatz prototypen
- Shadow-Vergleich 2 Wochen
- Wenn Python-Version >=95% deckungsgleich: AI-Node ersetzen

### Phase 3: IMPLEMENT - Patch-Generierung

Pro Dark-Factory erzeugt der Skill einen Patch-Vorschlag:

```
# Evolution-Patch: <factory-name> v<n+1>
## Baseline
- Success-Rate: X%
- Cost/Run: Y EUR
- Martin-Approval-Rate: Z%

## Proposed Changes
1. [NEW TEST] test_case_fail_pattern_<hash>.py (verhindert Fail Typ A)
2. [SCOPE] input-validation: Reject wenn <regex>
3. [MODEL] Downshift Sonnet->Haiku fuer Node X (Grund: <metric>)
4. [PARALLEL] Split in 3 concurrent worktrees

## Erwarteter Effekt
- Success-Rate: X% -> X+3%
- Cost/Run: Y -> 0.7Y EUR
- Setup-Cost Patch: 2h

## Martin-Approval erforderlich: [JA/NEIN]
(Ja wenn: scope change, Modellwechsel; Nein wenn: nur neue Tests added)
```

### Phase 4: TEST - A/B-Run 7 Tage

Nach Approval:
1. Fork workflow als `<name>-v<n+1>`
2. Beide laufen parallel fuer 7 Tage (random-split 50/50)
3. Metriken vergleichen: Success, Cost, Runtime, Martin-Approval
4. Statistischer Test (t-test) ob Verbesserung signifikant

### Phase 5: REFINE - Release

Bei signifikanter Verbesserung:
- `<name>-v<n+1>` wird neues `<name>`
- Altes `<name>` archiviert in `archive/dark-factory/<name>-v<n>`
- Knowledge-Diff schreiben
- BULLETIN-Eintrag

Bei keiner Verbesserung:
- Patch verworfen
- Aber: Learning dokumentiert in `branch-hub/learnings/dark-factory-evolution.jsonl`

## Automatisierter Monatlicher Run

Scheduled Task (Windows Task Scheduler):
```
Name: DarkFactory-Evolve-Monthly
Trigger: 1. des Monats, 02:00
Action: archon workflow run dark-factory-evolve --branch auto/evolve-$(date +%Y%m) "all"
```

Pro Dark-Factory wird eine Retrospective geschrieben, Patches vorgeschlagen,
approval-required ones als BULLETIN-Eintrag markiert.

## Self-Modifying-Guard

**WICHTIG:** Dieser Skill darf sich NICHT selbst modifizieren.
- Evolution-Targets = nur die Factories in `.archon/dark-factory/*/`
- NICHT: `~/.claude/skills/dark-factory-*/`
- NICHT: rules/
- NICHT: CLAUDE.md

Begruendung: Rekursive Selbst-Aenderung = nicht auditierbar. Bleibt Martin-Pflege.

## Rollback fuer Evolutions-Patches

```bash
cd C:/Users/marti/Projects/learning-archon
git log --oneline .archon/dark-factory/<name>/
git revert <evolution-commit>
```

Plus: `<name>-v<n-1>` aus `archive/dark-factory/` wiederherstellen wenn noetig.

## Smoke-Test

```
Input: "evolve orphan-marker-darkfactory"
Erwartet:
1. Liest .archon/dark-factory/orphan-marker/ metrics
2. Findet Success-Rate 92%, 3 Fail-Patterns
3. Schlaegt 3 neue Tests vor
4. rho-Check: Setup 2h, Nutzen 15 EUR/Monat -> NET POSITIV
5. Decision-Card an Martin, keine Auto-Applikation
```

[CRUX-MK]
