---
name: archon-workflow-create
description: |
  Erzeugt einen neuen Archon-Workflow fuer Learning-Archon. CRUX-MK-aligned.
  Triggers (create): "archon workflow bauen", "neuen workflow erstellen", "scaffold archon workflow",
      "learning-archon neuer workflow", "create archon workflow for", "baue mir einen archon workflow",
      "archon skill bauen".
  Triggers (adapt): "archon workflow anpassen", "workflow erweitern", "workflow klonen".
  Capability: Schritt-fuer-Schritt Scaffolding von YAML-Workflows + Commands + Scripts
      mit CRUX-Gate, Budget-Hard-Stop, Cross-LLM-Mandate, Write-to-Hub.
crux-mk: true
version: 1.0.0
origin: opus-4.7-2026-04-17
---

# /archon-workflow-create [CRUX-MK]

## Wann nutzen

Du willst einen neuen Archon-Workflow fuer `C:/Users/marti/Projects/learning-archon/` bauen.
Beispiele:
- Neue These systematisch wargamen (Adaption von `learning-wargame`)
- Lern-Ziel strukturiert verfolgen (Adaption von `learning-knowledge-diff`)
- NLM-Factory-Pipeline (Multi-LLM-Research + Wargame + Synthese)
- Komplett eigenen Prozess als DAG

NICHT fuer: triviale Einmal-Aufgaben. Bash-Oneliner reichen.

## Pentagon-Ablauf

### Phase 1: PLAN - These klaeren

Frage Martin:
1. **Zweck**: Was soll der Workflow liefern? (1 Satz)
2. **Trigger**: Auf welchen Natural-Language-Phrase soll er reagieren?
3. **Input**: Was gibt Martin beim Aufruf mit (String, Pfad, GitHub-Issue)?
4. **Output**: Wo soll das Ergebnis landen? (Default: `branch-hub/findings/<SLUG>.md`)
5. **Budget**: Wie viel Token/EUR maximal? (Default: 50k Token / 2 EUR)
6. **CRUX-Alignment**: Welcher rho-Beitrag? K_0/Q_0/I_min-Bezug?
7. **Basis-Template**: wargame / knowledge-diff / nlm-factory / custom?

Wenn CRUX-Alignment unklar ist -> rejectiere + bitte Martin um Ueberarbeitung.

### Phase 2: SPEC - Nodes entwerfen

Fuer jeden Node klaeren:
- `id` (kebab-case, sprechend)
- `type` - bash / claude / external_llm
- `model` - sonnet / haiku / opus (Default sonnet)
- `depends_on` - Liste vorheriger Nodes
- `session: fresh` oder `continue` (fresh = Bias-Reduktion)
- Was genau wird getan? (Prompt oder Bash-Command)
- Welches Output-File wird erzeugt? ($ARTIFACTS_DIR/...)

**Pflicht-Nodes (in jedem Learning-Workflow):**
- Node 0: `crux-gate` (Bash -> `scripts/crux-validate.py`)
- Node 1: `budget-init` (initialisiert Budget)
- Letzter Node: `write-finding` (Bash -> `branch-hub/findings/` + audit-log)

**Cross-LLM-Mandate (aus WARGAME-ARCHON-FOR-LEARNING):**
Mindestens 2 Non-Claude-Nodes bei Wargames. Bei reinen Knowledge-Diffs optional.

### Phase 3: IMPLEMENT - Scaffolding

Nutze `scripts/new-workflow.py` (interaktiv) ODER erstelle manuell:

1. Waehle Template aus `templates/`:
   - `wargame.yaml.template` - 9-Node Red/Blue/Purple/Gray
   - `knowledge-diff.yaml.template` - 4-Node Session-Reflexion
   - `nlm-factory.yaml.template` - 8-Schritt NLM-Loop
   - `custom.yaml.template` - Minimal-Skelett
2. Kopiere nach `learning-archon/.archon/workflows/<name>.yaml`
3. Ersetze Platzhalter: `{{WORKFLOW_NAME}}`, `{{DOMAIN}}`, `{{BUDGET_TOKENS}}`, `{{THESIS_HELP}}`
4. Commands in `learning-archon/.archon/commands/<name>-*.md` ausfuehrlich ausformulieren
5. Bei Bedarf: Helper-Script in `.archon/scripts/`

### Phase 4: TEST - Validate + Smoke

```powershell
# Struktur pruefen
cd C:\Users\marti\Projects\learning-archon
archon validate workflows <name>

# Smoke-Test in isoliertem Worktree
archon workflow run <name> --branch test/smoke-<name> "Test-Input"

# Logs monitoren
archon workflow status
```

Erwartetes Ergebnis: Alle Nodes durchlaufen, Output in `branch-hub/findings/` oder definiertem Target.

### Phase 5: REFINE - Commit + Mirror

```bash
# Commit im Learning-Archon-Repo
cd C:/Users/marti/Projects/learning-archon
git add .archon/ && git commit -m "Add workflow: <name> [CRUX-MK]"
git push origin master

# Mirror in branch-hub
cp .archon/workflows/<name>.yaml "G:/Meine Ablage/Claude-Knowledge-System/branch-hub/.archon/workflows/"

# Audit-Log
echo '{"ts":"ISO","branch":"claude","action":"WRITE","target":".archon/workflows/<name>.yaml","reason":"new archon workflow","source":"archon-workflow-create"}' \
  >> "G:/Meine Ablage/Claude-Knowledge-System/branch-hub/audit/action-log.jsonl"

# BULLETIN Eintrag appenden + Finding schreiben
```

## Templates-Uebersicht

| Template | Nodes | Use-Case |
|---|---|---|
| `wargame.yaml.template` | 9 | Red/Blue/Purple/Gray/CRUX auf eine These |
| `knowledge-diff.yaml.template` | 4 | 5+1-Pruef-Fragen am Session-Ende |
| `nlm-factory.yaml.template` | 8 | NLM-Research + Wargame + Synthese + Skill |
| `custom.yaml.template` | 3 | Minimales Skelett (crux-gate + main + write) |

## CRUX-Check bei jedem neuen Workflow

- [ ] rho-Beitrag in Finding geschaetzt
- [ ] mind. 1 Bash/Python-Node (deterministisch) gegen LLM-Bias
- [ ] Budget hart limitiert (`budget_tokens` + `budget_eur`)
- [ ] Output geht in `branch-hub/findings/` oder `knowledge-diffs/`
- [ ] Audit-Log-Entry wird geschrieben
- [ ] `session: fresh` zwischen inhaltlich unabhaengigen Nodes
- [ ] Bei Wargames: Cross-LLM-Mandate (mind. 2 Non-Claude)
- [ ] Kein Auto-Merge (Bounded Autonomy, Level 4)

## Antipatterns

1. **Workflow-in-Workflow-in-Workflow** - YAML-Bloat >1000 Zeilen, unwartbar
2. **Nur Claude-Nodes** bei Wargames - Sycophancy-Risiko
3. **Missing crux-gate** - Workflow laeuft bei CRUX-Verletzung trotzdem
4. **Missing budget-init** - Token-Explosion moeglich
5. **Inline-Prompts >50 Zeilen** - lies `commands/` nach, extrahiere
6. **Kein Write-Finding-Node** - Output verschwindet im Artifacts-Dir

## Referenz

- Basis-Workflows: `learning-archon/.archon/workflows/learning-wargame.yaml`
- Helper-Scripts: `learning-archon/.archon/scripts/`
- Wargame-Ziel: `findings/WARGAME-ARCHON-FOR-LEARNING-2026-04-17.md`
- Tutorial: `findings/TUTORIAL-LEARNING-ARCHON-2026-04-17.md`
- Archon-Docs: https://github.com/coleam00/archon

[CRUX-MK]
