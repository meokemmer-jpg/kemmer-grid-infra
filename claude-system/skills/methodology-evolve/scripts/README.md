# methodology-evolve Scripts [CRUX-MK]

**Status:** SKELETON v1.0.0 (produktions-ready erst nach 3-Monats-Shadow ab 2026-05-01)

## 7 Script-Platzhalter

| Script | Zweck | Executor | Status |
|--------|-------|----------|--------|
| `s1_outcome_sampling.py` | Blueprints+Findings+Feedback sammeln | Python | PLATZHALTER |
| `s2_methodology_inventory.py` | Aktive Methoden + Metriken indexieren | Python | PLATZHALTER |
| `s3_gap_analysis.py` | Pattern-Mining (Wrapper um Claude-Call) | Python | PLATZHALTER |
| `s4_patch_generation.py` | Patch-Vorschlaege generieren (Wrapper) | Python | PLATZHALTER |
| `s5_cross_llm_audit.sh` | multi-llm-parallel invoken | Bash | PLATZHALTER |
| `s6_shadow_deployment.sh` | A/B-Shadow aufsetzen + Metriken sammeln | Bash | PLATZHALTER |
| `s7_promote_decision.py` | Statistische Tests + Decision-Card | Python | PLATZHALTER |

## Dependencies

- Python 3.12+ (via `winget install Python.Python.3.12`)
- Shell: Bash (Unix-Syntax via Git-Bash oder WSL)
- LLM-Clients: `codex exec`, `copilot -p`, `gemini -p`, Grok-MCP
- Python-Packages: `pyyaml`, `scipy` (fuer t-test), `pandas` (Daten-Aggregation)

## Deploy-Status

**v1.0.0 SKELETON (2026-04-19):** Scripts als Platzhalter. Shadow-Run ab 2026-05-01 fuehrt
nur S1+S2 (Sampling) aus, S3-S7 als Dry-Run-Simulation fuer Metriken-Kalibrierung.

**v1.1.0 (geplant 2026-06-01):** S1-S4 live, S5-S7 noch Shadow.

**v2.0.0 (geplant 2026-08-01):** Alle 7 Nodes live, Auto-Promote nach Martin-Approval.

## Invocation

```bash
# Manuell (Test-Run):
cd ~/.claude/skills/methodology-evolve
bash scripts/s1_outcome_sampling.py --dry-run

# Via Archon-Workflow:
archon workflow run methodology-evolve

# Via Scheduled-Task (automatisch):
# Konfiguriert in archon-workflow.yaml schedule: "0 4 1 * *"
```

## Referenz

- Parent-Skill: `../SKILL.md`
- Workflow-YAML: `../archon-workflow.yaml`
- CRUX-Rules: `~/.claude/rules/meta-governance-framework.md`, `~/.claude/rules/meta-methodological-pragmatism.md`

[CRUX-MK]
