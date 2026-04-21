# ASWDF Phases-YAML-Ordner [CRUX-MK]

**Status:** SKELETON — Per-Phase-YAML-Configs pending Build-Phase-B-G.

## Per-Phase-YAML-Inventar (alle pending)

| YAML-File | Phase | Input-Contract | Output-Contract |
|-----------|:-----:|----------------|-----------------|
| `phase1.yaml` | 1 Ordnungs-Audit | plan-markdown + frontmatter | O1-O5-Matrix (JSON) + Gaps-Liste |
| `phase2.yaml` | 2 Multi-LLM-Adversarial | Gaps-Liste | 4-Block-Results + Konvergenz-Analyse (JSON) |
| `phase3.yaml` | 3 NLM-Dissent-Loop | Plan-Iteration | Dissent-Aussagen (JSON, 3x Loop) |
| `phase4.yaml` | 4 Spieltheorie | Plan + Dissent | Strategien-Matrix + Nash-Gleichgewichte (JSON) |
| `phase5.yaml` | 5 Systemtheorie | Plan + Spieltheorie | System-Diagramm + Hotspots (JSON) |
| `phase6.yaml` | 6 Iteration-Gate | O-Scores + Kontext | Decision (STOP_*/CONTINUE) |
| `phase7.yaml` | 7 Dual-Persistence | Finaler Plan | 4 Persistence-Targets-Confirmation |
| `phase8.yaml` | 8 Self-Improvement | Pattern-History | Config-Updates + Rule-PROPOSALs (async) |

## Konvergenz-Regeln (pro Phase)

- **Phase 2 Multi-LLM**:
  - 4/4 ADOPT → HARDENED
  - 3/4 ADOPT → CROSS-LLM-SIM-HARDENED
  - 2/4 SPLIT → DISAGREEMENT-DOCUMENTED
  - 1/4 oder 0/4 → CRITICAL-REVISION-NEEDED

- **Phase 3 NLM**: Integration-Threshold = G8 Cross-path-invariance (Dissent uebersteht mindestens 2 unabhaengige Audit-Pfade)

- **Phase 4 Spieltheorie**: Nash-Gleichgewicht robust wenn es unter mindestens 2 Gegner-Strategien stabil bleibt

- **Phase 5 Systemtheorie**: Feedback-Loop-Karte vollstaendig wenn mindestens 3 positive + 3 negative Loops identifiziert

- **Phase 6 Gate**: O_total >= 0.80 ODER iteration_count >= 10 → STOP

## Phase-Dependency-Graph

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
                                                      ├── CONTINUE: back to Phase 2
                                                      └── STOP_*: Phase 7 → Phase 8 (async)
```

## Build-Notice

Diese YAMLs werden in Phase-B bis Phase-E gebaut. Aktueller Zustand: SKELETON.
Pentagon-Verfahren pro Phase: Plan → Spec → Implement → Test → Refine.

[CRUX-MK]
