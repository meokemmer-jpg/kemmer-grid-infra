---
name: strategic-wargame-dark-factory
description: Dark-Factory (Level-5 Autonomie) die strategische Plaene durch 5 Ordnungen (Existenz/Konsistenz/Adversarial/Spieltheorie/Systemtheorie) autonom haertet. Nutzt NotebookLM-Dissent-Loop (0 Token) + Multi-LLM-Adversarial (Codex+Gemini+Grok+Copilot flat) + Korpus-Backfill-Learning. Ersetzt manuelle Wargame-Runden durch Martin. Triggers "wargame plan", "strategic wargame", "aswdf", "haerte plan auf O5", automatisch bei neuem Blueprint-File.
type: skill-dark-factory
meta-ebene: E3+E4
crux-mk: true
version: 0.1.0-SKELETON
created: 2026-04-19
tier: 2 (Dark-Factory, Level-5-Autonomie)
status: SKELETON (Build-Phase-A-B, nicht production-ready)
depends-on:
  - nlm-meta-harness-archon (DF-06, NLM-Infrastructure)
  - multi-llm-parallel
  - 4-team-wargame
  - gemini-isolated-retry
  - ordnung-3-audit-template
  - cross-llm-real
token-budget:
  per-iteration: 6500
  per-plan-max: 52000
  daily-cap: 5 EUR
---

# Skill: strategic-wargame-dark-factory (ASWDF) [CRUX-MK]

## Zweck

ASWDF ist die Meta-Dark-Factory die strategische Plaene autonom durch 5 Ordnungen
(Existenz/Konsistenz/Adversarial/Spieltheorie/Systemtheorie) haertet, bis O_total >= 80%
erreicht ist. **Martin-Zeit als Engpass eliminiert** — statt Martin kommt die Factory
zwischen jeder Planungs-Iteration.

**Martin-Diagnose 2026-04-19**: "Plan ist nicht mal 3% reif, bricht in der 1. Ordnung,
die zweite ist nur noch Chaos." ASWDF ersetzt manuelle Wargame-Runden durch autonome
8-Phasen-Iterations-Engine mit NLM-Loop (0 Token) + Multi-LLM-Adversarial (flat) +
Korpus-Backfill-Learning (~250 historische Prompts).

**rho-Gain Jahr 1**: 250-550k EUR (Martin-Zeit + Plan-Qualitaets-Amplifikation).
**Kumulativ 5J**: 3-8M EUR.

## 8-Phasen-Engine

### Phase 1: Ordnungs-Audit (5-10 min, 500 Claude-Token)
- **Input**: Plan-Markdown + Frontmatter
- **Tool**: Python-Script (mechanisches Frontmatter+Header-Audit)
- **Output**: O1-O5 Matrix mit Scores, Gaps-Liste
- **Token-Budget**: 500

### Phase 2: Multi-LLM-Adversarial (15-30 min, 2000 Claude-Token)
- **Input**: Gaps-Liste aus Phase 1
- **Tool**: Bash-Script parallel (Codex+Gemini+Grok+Copilot)
- **Output**: 4-Block-Pattern-Results, Konvergenz-Analyse
- **Token-Budget**: 2000
- **Konvergenz-Regeln**: 4/4 ADOPT → HARDENED, 3/4 → CROSS-LLM-SIM-HARDENED, 2/4 SPLIT, 1-0/4 → Revision

### Phase 3: NotebookLM-Dissent-Loop (20-40 min, 0 Claude-Token!)
- **Input**: Plan-Iteration
- **Tool**: DF-06-Infrastructure (nlm-meta-harness-archon), Codex+Gemini fuer Antworten
- **Output**: Dissent-Aussagen (3-5 pro NLM-Output, 8 Outputs, Loop 3x)
- **Token-Budget**: 0 (der Kern-Innovations-Hebel)
- **NLM-Outputs**: Audio-Overview, Study-Guide, Mindmap, FAQ, Timeline, Briefing, Report, Infografik

### Phase 4: Spieltheorie (15 min, 1500 Claude-Token)
- **Input**: Plan + Dissent-Aussagen
- **Tool**: Codex (formal Nash-Solver) + Claude (Synthese)
- **Output**: Strategien-Matrix mit Stabilitaets-Bewertung, Nash-Gleichgewichte, Dominanz-Pruning
- **Token-Budget**: 1500
- **Checks**: Nash, Dominanz, Bayesian-Spiele, Signaling, Zero-Sum vs Positive-Sum, Prisoner-Dilemma

### Phase 5: Systemtheorie (15 min, 1500 Claude-Token)
- **Input**: Plan + Spieltheorie-Analyse
- **Tool**: Gemini (Feedback-Loops) + Copilot (Benchmarks) + Claude (Emergenz)
- **Output**: System-Diagramm + Instabilitaets-Hotspots, Feedback-Loop-Karte
- **Token-Budget**: 1500
- **Checks**: Feedback-Loops, Lyapunov, Daempfungs-Puffer, Emergenz, Kaskaden, Beobachter-Paradox

### Phase 6: Iteration-Gate (5 min, 500 Claude-Token)
- **Input**: O-Scores + Kontext
- **Tool**: Python-Script (Decision-Logic)
- **Output**: STOP_SUCCESS / CONTINUE / STOP_DIVERGE / STOP_K0 / STOP_Q0 / STOP_COST
- **Token-Budget**: 500

### Phase 7: Dual-Persistence (5 min, 0-500 Claude-Token)
- **Input**: Finaler Plan oder Eskalation
- **Tool**: NLM-Upload + KB-File-Write + Fragment-Map + Rule/Skill-Update
- **Output**: 4 Persistenz-Targets
- **Token-Budget**: 500

### Phase 8: Self-Improvement-Loop (async, 0 Claude-Token Live)
- **Input**: Pattern aus abgeschlossenen Iterationen
- **Tool**: Python-Script (Pattern-Extraction, dark-factory-evolve weekly)
- **Output**: Config-Adjustments, neue Rule-PROPOSALs, LLM-Routing-Gewichte
- **Token-Budget**: 0 (async)

## 5-Ordnungs-Stack

### O1 Existenz (Pflicht-Struktur)
- Plan hat: Vision, Architektur, Risiken, rho-Schaetzung, Phronesis-Entscheidungen, Falsifikations-Bedingung?
- Metrik: 6/6 Pflicht-Sektionen, Schwellen 100%
- Tool: mechanisches Frontmatter+Header-Audit via Python

### O2 Konsistenz
- Self-Contradiction-Check, Scope-Konsistenz, rho-Arithmetik, Claim-Type-Alignment
- Metrik: 0 Widersprueche = 100%, 1 pro 100 Zeilen = 80%, >3 = 0%
- Tool: Codex + Gemini Parallel-Check

### O3 Adversarial-Resilienz (Red-Team)
- Poisoning, 4-Perspektiven (Angreifer/Konkurrent/Skeptiker/Ignorant), Silent-Killer-Hunt
- Metrik: Anteil Angriffe die Plan uebersteht
- Tool: Grok + 4-team-wargame + Gemini

### O4 Spieltheorie-Stabilitaet
- Nash-Gleichgewicht, Dominanz-Analyse, Bayesian-Spiele, Signaling, Prisoner-Dilemma
- Metrik: Anzahl Gleichgewichts-Strategien, Dominanz-Tiefe
- Tool: Codex (formal) + Claude (Synthese)

### O5 System-Robustheit (Systemtheorie)
- Feedback-Loops, Stabilitaets-Analyse, Daempfungs-Puffer, Emergenz, Kaskaden, Beobachter-Paradox
- Metrik: Anzahl robuster Feedback-Loops + Puffer + Kaskaden-Pruefungen
- Tool: Gemini + Copilot + Claude

### Progression-Scoring
```
O_total = 0.1*O1 + 0.15*O2 + 0.25*O3 + 0.25*O4 + 0.25*O5
Stop: O_total >= 0.80 ODER 10 Iterationen ohne Verbesserung
```

## Token-Oekonomie

### Pro-Iteration-Budget
| Phase | Claude-Token | EUR-Marginal |
|-------|-------------:|-------------:|
| 1 Ordnungs-Audit | 500 | 0.04 |
| 2 Multi-LLM-Adversarial | 2000 | 0.15 |
| 3 NLM-Dissent-Loop | 0 | 0 |
| 4 Spieltheorie | 1500 | 0.11 |
| 5 Systemtheorie | 1500 | 0.11 |
| 6 Iteration-Gate | 500 | 0.04 |
| 7 Dual-Persistence | 500 | 0.04 |
| 8 Self-Improvement | 0 (async) | 0 |
| **Total** | **6500** | **~0.50 EUR** |

### Pro-Plan (bis O5 >= 80%)
- Durchschnitt: 5-8 Iterationen
- Claude-Token-Range: 32-52k
- EUR-Range: 2.50-4.00 EUR
- Martin-Zeit gespart: 3-8h pro Plan

### Skalierung
- 10 Plaene/Jahr: ~25-40 EUR OPEX, ~30-80h Martin-Zeit gespart
- 50 Plaene/Jahr: ~200-400 EUR OPEX, ~150-400h Martin-Zeit gespart
- Lambda-Faktor 10-20x gegen manuelle Wargame-Praxis

## Martin-Phronesis-Gates (L13, 11 Fragen)

1. **Build-JA/NEIN**: Commit zur 7-Wochen-Build-Phase?
2. **Budget-Commitment**: 40-80 Arbeitstage Claude + 14h Martin-Phronesis akzeptabel?
3. **Korpus-Scope**: alle ~250 Prompts oder selektiv (Top-50 K_0-nah)?
4. **Shadow-Mode-Dauer**: 1 Woche / 1 Monat / 3 Monate?
5. **Phronesis-Gate-Schwelle**: K_0/Q_0-Risiko-Schwelle?
6. **Cost-Cap**: 5 EUR/Tag default akzeptabel?
7. **NLM-Notebook-Allocation**: dedizierte "ASWDF-*"-Notebooks oder integrieren?
8. **Skill-Namens-Konvention**: `strategic-wargame-dark-factory` / `aswdf` / `meta-wargame-factory-v2`?
9. **First-Real-Target**: B200 / B33 / KPM-Phase-0?
10. **Abloesung `meta-harness-archon`**: komplett oder coexist?
11. **Self-Improvement-Autonomie**: Rules-PROPOSAL autonom oder nur vorschlagen?

## Integration mit existierenden Skills

| Asset | Rolle in ASWDF |
|-------|---------------|
| `meta-harness-archon` | **Abgeloest** durch ASWDF (Weiterentwicklung mit NLM+Spieltheorie+Systemtheorie) |
| `nlm-meta-harness-archon` (DF-06) | Phase 3 Infrastructure (NLM-Upload, Output-Extraktion) |
| `4-team-wargame` | Phase 2 Component (Red/Blue/Purple/Gray bleibt) |
| `multi-llm-parallel` | Phase 2 Executor (Codex+Gemini+Grok+Copilot) |
| `dark-factory-create` | Build-Template fuer ASWDF-Skill |
| `dark-factory-evolve` | Phase 8 (weekly Self-Improvement) |
| `gemini-isolated-retry` | Phase 3+4 Gemini-Calls (Anti-Kontamination) |
| `ordnung-3-audit-template` | Phase 1 Pattern |
| `cross-llm-real` | Phase 2 Verdict-Logik |

## Trainings-Korpus

### Historische Prompts-Liste (ca. 250 Iterationen)
| Domain | Count | Primaerquelle |
|--------|------:|---------------|
| SAE v8 | ~100 | CRUX.md + architecture decisions + 6 Wargames |
| 9OS GUI | ~50 | snug-meandering-grove Ultraplan v5.1 + Unified-Rewrite |
| KPM | ~30 | Strategie v1 + 20M+ Portfolio + Thomas-First |
| HeyLou | ~20 | B13+B23+B24+B250+B200 + 7 Hotels |
| Meta-Lern-Kristall | ~30 | E1-E5 + G1-G14 + Half-Kelly-HARDENED |
| Cape-Coral | ~15 | B33 Relocation + E-2 Visa |

### Backfill-Strategie
- **Tag 1-7**: Factory durchlaeuft Korpus nach **Risikoklasse** (K_0-naechst zuerst)
- **Pro Korpus-Prompt**: 1 Iteration mit aktuellem Plan-Stand
- **Lerneffekt**: welche Wargame-Config welche Ordnung am besten aufbaut
- **Konfig-Matrix**: Domain × Ordnung × LLM-Routing-Gewicht (3D-Tensor)

### Leerlauf-Training
- **Scheduled Cron**: alle 4h, 1 Korpus-Iteration
- **Training-Signal**: rho_delta (Plan-Qualitaet nach Iteration vs vor) als Reward

## Anti-Patterns

- Plan-Input ohne Frontmatter (Phase 1 versagt)
- Factory-Auto-Approval von Rule-PROPOSALs (nur Vorschlag, nie Approval ohne Martin)
- Martin-Phronesis-Gate-Umgehung bei K_0/Q_0
- NLM-Upload ohne claude-isolated-retry bei File-Access-Risk
- Korpus-Backfill ohne Lern-Reward-Metrik (blindes Training)
- Selbst-Referenz-Loop ohne Bootstrap-Gate (B201 muss EXTERN gewargamed werden vor Self-Use)
- Cost-Cap-Override ohne Martin-Approval
- Cross-LLM-Single-Family-Simulation als HARDENED ausgeben (FIXPUNKT-1 Verletzung)

## Falsifikations-Bedingung

Der Skill ist falsifiziert wenn:

1. **Shadow-Mode-Qualitaets-Gap**: nach 3 Monaten Factory-Output <50% Qualitaet manueller Wargames
2. **O5-Plateau**: bei realen Plaenen erreicht Factory nie O5 >60% → Architektur-Revision
3. **Martin-Phronesis-Gate-Rate >70%**: Factory eskaliert zu haeufig, nicht autonom genug
4. **Cost-Exceed**: Claude-Token-Budget uebersteigt 500 EUR/Monat → rho-negativ
5. **Korpus-Backfill-Ineffektivitaet**: nach 3 Monaten keine messbare Config-Verbesserung

**Revision-Trigger**: nach Phase-F (Integration-Test mit B200) empirische Daten vs Hypothesen vergleichen.

## SAE-Isomorphie

- **MYZ-36 Meta-Prompting-Router** fuer LLM-Routing pro Phase (Tier 0/1/2 Haiku-Filter vor Premium-LLMs)
- **Trinity-Pattern**: 3-LLM-Konsens bei Phase 2+4+5 (Conservative/Aggressive/Contrarian)
- **COSMOS-Compliance-Matrix** fuer Phronesis-Gates (Phase 6 Escalation-Logic)
- **Myzel-Layer MYZ-27 Relegation**: schlechte Phase-Configs werden durch bessere ersetzt (Phase 8)
- **Bounded Veto (myz33)**: K_0/Q_0-Verletzung → hartes Stop, kein Auto-Continue

## CRUX-Bindung

- **K_0 Kapitalerhaltung**: Factory schuetzt K_0 durch Phronesis-Gate bei K_0-relevanten Plaenen
- **Q_0 Qualitaetsinvarianz**: direkt zentrales Ziel (Plan-Qualitaet 3% → 80%)
- **I_min Ordnungsminimum**: 8-Phasen-Architektur + 5-Ordnungs-Stack = strukturiertes OS
- **W_0 Working-Capital**: Martin-Zeit-Engpass massiv entlastet
- **rho**: Lambda-skalierend durch Korpus-Training-Effekt
- **L_Martin**: direkt erhoeht (Stress-Reduktion bei strategischer Planung)
- **MHC (Meaningful Human Control)**: Martin-Phronesis-Gate eingebaut, nicht umgehbar bei K_0/Q_0

## rho-Schaetzung (kompakt)

- **Investment**: 70 Arbeitstage Claude + 14h Martin = ~200-400 EUR OPEX + 14k EUR Opportunity-Cost
- **Direkt (Martin-Zeit)**: 50-150k EUR/J
- **Systemisch (Plan-Qualitaet)**: 200-500k EUR/J
- **Kumulativ (Lerneffekte)**: Jahr 2 +80%, Jahr 3+ +100-150%
- **Jahr 1 Total**: 250-550k EUR
- **5J-Total**: 3-8M EUR
- **Break-Even**: Monat 3-6

## SKELETON-Status

Version 0.1.0 ist SKELETON. Build-Phase-B-G noetig vor Production:
- **Phase-B (Week 2)**: Phase-1+2-Scripts bauen, Konvergenz-Analyzer
- **Phase-C (Week 3)**: NLM-Integration (Phase 3 + 7)
- **Phase-D (Week 4)**: Spieltheorie + Systemtheorie (Phase 4 + 5)
- **Phase-E (Week 5)**: Self-Improvement + Korpus-Backfill (Phase 8)
- **Phase-F (Week 6)**: Integration-Test mit B200 als erster Real-Input
- **Phase-G (Week 7+)**: Production mit Scheduled Cron + Monthly Evolve

**Shadow-Mode 3 Monate** nach Build. Falsifikations-Gate pruefen.

**Cross-References**:
- Master-Blueprint: `G:/Meine Ablage/Claude-Vault/canon/blueprints/B201-Archon-Strategic-Wargame-Dark-Factory-ASWDF.md`
- `~/.claude/rules/meta-governance-framework.md` (G1-G14)
- `~/.claude/rules/meta-stack-fixpunkte.md` (FIXPUNKT-1-4)
- `~/.claude/rules/when-to-archon.md` (Tier-Klassifikation)
- `~/.claude/rules/token-engpass-hierarchie.md` (Token-Budget-Regel)

[CRUX-MK]
