---
name: archon-trigger-detect
description: |
  Proaktive Erkennung wann ein Task als Archon-Workflow oder Dark-Factory sinnvoll ist.
  Triggers: Automatisch vor jedem Task mit geschaetzter Dauer >= 15 Min.
      Auch: "lohnt sich archon hier", "sollte das ein workflow werden",
      "rho-check archon", "task-analyse".
  Capability: Schaetzt Lambda, rho, CRUX-Alignment und schlaegt Tier vor (0=einmal,
      1=archon-workflow, 2=dark-factory).
crux-mk: true
version: 1.0.0
origin: opus-4.7-2026-04-17
---

# /archon-trigger-detect [CRUX-MK]

## Wann nutzen

**Claude soll diesen Skill automatisch invoken** bevor ein Task angefangen wird der:
- Geschaetzt >=15 Min dauert
- Oder: wiederkehrend aussieht (Trigger-Signal)
- Oder: Martin explizit fragt "lohnt sich archon fuer X"

Referenz-Entscheidungs-Matrix: `~/.claude/rules/when-to-archon.md`.

## Prozess

### Schritt 1: Task-Klassifikation

Kategorie waehlen:
- `wargame` - Red/Blue/Purple auf These
- `knowledge-diff` - Session-Reflexion
- `nlm-research` - Multi-LLM-Topic-Hardening
- `pattern-fix` - Typos / Linter / Regex-Pattern
- `code-analysis` - Review / Audit / Diff
- `content-generation` - Doku / Blog / Marketing
- `data-extraction` - Copilot/Research-Reports
- `other` - keine klare Passform

### Schritt 2: Lambda-Schaetzung (pro Monat)

Quellen:
- Frueheres `audit/action-log.jsonl` lesen (wie oft trat aehnlicher Task auf?)
- `branch-hub/learnings/workflow-decisions.jsonl` fuer historische Lambda_real
- Martin-Kontext: bekannte Projekte (SAE/9OS/KPM) haben typische Frequenzen

Kategorisierung:
- Lambda < 3/Monat -> Tier 0 (Einmal-Task)
- Lambda 3-10/Monat -> Tier 1 (Archon-Workflow-Kandidat)
- Lambda >= 10/Monat UND deterministisch -> Tier 2 (Dark-Factory-Kandidat)

### Schritt 3: rho-Rechnung

```
CM_pro_Run    = manuell_min - archon_min) * Martin_h_rate
OPEX_mtl      = archon_runs_mtl * cost_per_run_eur
Setup_Cost    = entwicklungs_h * 200 EUR/h
rho_netto_jhr = (CM_pro_Run * Lambda_mtl * 12) - (OPEX_mtl * 12) - Setup_Cost
Break_Even    = Setup_Cost / (CM_pro_Run * Lambda_mtl)
```

Typische Martin-Rate: 200 EUR/h (konservativ).
Typische Sonnet-Kosten: ~0.30 EUR/Run (15k Token).
Typische Setup-Cost Archon-Workflow: 2-4h.
Typische Setup-Cost Dark-Factory: 8-16h.

### Schritt 4: CRUX-Check

Pflicht-Gates fuer Tier 1 (Archon-Workflow):
- [ ] rho_netto_jhr > 5k EUR
- [ ] Break-Even < 3 Monate
- [ ] Keine K_0-relevanten Outputs
- [ ] Q_0-Check moeglich (Tests, Assertions, Schema)

Zusaetzlich Pflicht-Gates fuer Tier 2 (Dark-Factory):
- [ ] Lambda_est >= 10/Monat
- [ ] 100% automatisierter Output-Check
- [ ] Rollback in < 60s
- [ ] Escalation-Trigger bei 2 Fails
- [ ] Budget-Hardcap 5 EUR/Tag
- [ ] Kein Merge in Production ohne Shadow-Mode-Phase

### Schritt 5: Empfehlung

Output-Format (Markdown-Block in Chat):

```
## Archon-Trigger-Analyse [CRUX-MK]

**Task**: <Beschreibung>
**Kategorie**: <wargame|knowledge-diff|...>
**Lambda**: <N/Monat> (Quelle: <audit-log|projektion|martin-input>)
**CM pro Run**: <EUR>
**rho netto/Jahr**: <EUR>
**Break-Even**: <Monate>

**Empfehlung**: Tier <0|1|2>
- [ ] Tier 0 (direkt ausfuehren)
- [ ] Tier 1 (Archon-Workflow) -> invoke /archon-workflow-create
- [ ] Tier 2 (Dark-Factory) -> invoke /dark-factory-create (nach Martin-Approval)

**CRUX**:
- rho: <+/0/->
- L: <+/0/->
- K_0: <geschuetzt|Risiko>
- Q_0: <messbar|unmessbar>
- I_min: <OK|Verletzt>

**Martin-Frage**: Baue ich den Workflow jetzt oder spaeter?
```

### Schritt 6: Log + Meta-Learning

Nach jeder Empfehlung (egal ob umgesetzt oder nicht):

```bash
echo '{"ts":"'$(date -Iseconds)'","task":"<kurz>","tier_suggested":<0|1|2>,
       "lambda_est":<N>,"rho_est_eur_yr":<EUR>,"accepted":<null|true|false>}' \
  >> "G:/Meine Ablage/Claude-Knowledge-System/branch-hub/learnings/workflow-decisions.jsonl"
```

Nach 30 Tagen: `/workflow-decision-review` (Skill, noch zu bauen) prueft:
- Lambda_real vs Lambda_est
- rho_real vs rho_est
- False-Positive-Rate (empfohlen aber nicht wertvoll)
- False-Negative-Rate (haette empfehlen sollen)

## Anti-Patterns

1. **Alles vorschlagen** - Tier-0-Tasks sind 80% der Interaktion. Kein Workflow-Overkill.
2. **Setup-Cost unterschaetzen** - Archon-Workflows brauchen 2-4h zum Bauen + Testen + Dokumentieren
3. **Lambda ueberschaetzen** - Fantasie-Zahlen. Nur aus audit-log + Martin-Input.
4. **Tier 2 ohne ALLE 10 Kriterien** - Dark-Factory ist gefaehrlich. Kein Shortcut.
5. **Rekursion** - archon-trigger-detect nicht fuer sich selbst invoken. Base-Case!

## Smoke-Test

```
Task: "Schreib mir ein Knowledge-Diff fuer diese Session"
Erwartet: Tier 1 (Lambda ~20/Monat, Break-Even <1 Monat), Empfehlung archon-workflow-create
```

```
Task: "Fix 3 Typos in meinem README"
Erwartet: Tier 0 (Einmal-Task, Lambda <3/Monat)
```

```
Task: "Entferne alle unused imports in meinem Python-Code automatisch bei jedem Push"
Erwartet: Tier 2 (Lambda >=15, deterministisch via pyflakes, Rollback trivial)
```

[CRUX-MK]
