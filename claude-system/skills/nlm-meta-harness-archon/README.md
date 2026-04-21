# NLM-Meta-Harness-Archon — Quick Reference [CRUX-MK]

**Dark-Factory DF-06** | Level-5 Autonomie | v1.0.0 (2026-04-19)

## TL;DR

NotebookLM macht die Arbeit (Reports/Mindmaps/Audio/Presentations) — Python-Orchestrator misst Shannon-Surprise und syncht in Vault. **Nahezu zero Claude-Tokens.**

## Dateien

| File | Zweck |
|---|---|
| `SKILL.md` | Volle Architektur-Dokumentation, 7-Node-DAG, Domain-Matrix, Setup, rho-Kalkulation |
| `orchestrator.py` | Python-Runner (args: --notebook, --domains, --limit-reports, --dry-run) |
| `prompts.yaml` | 4 Domains x 5 Permutationen Martin-spezifische Query-Templates |
| `README.md` | Diese Datei |

## Setup (einmalig, 10 Min Martin-Zeit)

```bash
# 1. Dependencies
pip install "notebooklm-py[browser]" sentence-transformers pyyaml
playwright install chromium

# 2. Google-Auth (Browser-Flow)
python -c "from notebooklm import NotebookLM; NotebookLM().authenticate()"

# 3. Test-Run (1 Notebook, 2 Reports, kein Write)
python orchestrator.py --notebook "00_MASTER_CONTROL_TOWER" --limit-reports 2 --dry-run

# 4. Erster echter Run
python orchestrator.py --notebook "00_MASTER_CONTROL_TOWER" --limit-reports 2

# 5. Scheduled Task aktivieren (Windows)
schtasks /create /tn "NLM-Meta-Harness-Archon" \
    /tr "python C:\Users\marti\.claude\skills\nlm-meta-harness-archon\orchestrator.py" \
    /sc weekly /d SUN /st 02:00
```

## Manuell triggern

```bash
# Volllauf (alle 5 Priority-Notebooks, alle 8 Berichtstypen, alle 4 Domains)
python orchestrator.py

# Nur 1 Notebook
python orchestrator.py --notebook "Martin-Kemmer-Business-Plan-Master"

# Nur Business-Domain
python orchestrator.py --domains business

# Test (keine Writes)
python orchestrator.py --dry-run
```

## Output-Pfade

- **Reports:** `G:/Meine Ablage/Claude-Vault/resources/_from-nlm/YYYY-MM-DD/<Notebook-Name>/`
- **State:** `Claude-Vault/areas/family/instance-d2/nlm-archon-state.json`
- **Audit-Log:** `Claude-Knowledge-System/branch-hub/audit/action-log.jsonl`

## Kill-Switch

```bash
# Factory pausieren
touch "G:/Meine Ablage/Claude-Knowledge-System/branch-hub/audit/DF-06-STOP.flag"

# Fortsetzen
rm "G:/Meine Ablage/Claude-Knowledge-System/branch-hub/audit/DF-06-STOP.flag"
```

## rho-Bilanz

- **Initial-Setup:** ~30K Claude-Tokens (dieser Bau)
- **Pro Run (wöchentlich):** ~0-2K Claude-Tokens
- **Jahr-1 Einsparung:** ~99% Token-Reduktion vs. manueller NLM-Audit
- **rho:** +180-450k EUR/J (Decision-Support + Wisdom-Saturation)

## Integration mit bestehenden Skills

- Nutzt `mk-py` (Python-API) + `mk` v9 (Chat-Modi)
- Erweitert `archon-workflow-create`-Pattern
- Monatlicher Evolve via `dark-factory-evolve`

## Troubleshooting

| Problem | Loesung |
|---|---|
| `notebooklm-py` not installed | `pip install "notebooklm-py[browser]"` |
| Google-Auth expired | Script schreibt `DF-06-AUTH-EXPIRED.flag`. Re-run `NotebookLM().authenticate()` |
| NLM Rate-Limit (8-10 Reports/Tag) | Orchestrator staffelt automatisch, Queue in state.json |
| Shannon-Score immer 20 (cap) | Baseline-Dir noch leer → erster Run erwartet hohe Werte |

[CRUX-MK]
