---
name: monthly-model-audit
description: Meta-Learning Archon-Skill fuer monatlichen Model-Portfolio-Audit mit Pentagon-Wargame + Zeitwertverfassung + Self-Improvement. Triggers "model audit", "monatlicher model check", "portfolio audit", automatisch am 1. des Monats. Prueft alle LLM-Abos (Claude/Copilot/Codex/Gemini/Grok/Perplexity) auf rho-Optimum.
version: 1.0.0
crux-mk: true
aktiviert: 2026-04-19
meta-ebene: E3
---

# Skill: monthly-model-audit [CRUX-MK]

## Zweck

**Martin-Direktive 2026-04-19:** *"sorge dafuer dass wir wirklich das maximale herausholen"*

Meta-Learning-Skill der monatlich das LLM-Portfolio auditiert und self-improvet. Kernmechanik:

1. **Token-Preis-Leistungs-Max-Wargame** (Pentagon-Test auf allen Modellen)
2. **Zeitwertverfassungs-Bewertung** pro Model (rho-Score)
3. **Role-Reassignment** (welches Model welche Role)
4. **Self-Improvement** (Rules/Skills/DFs werden gepatcht)
5. **Decision-Card fuer Martin** (Approve/Modify/Reject)

Referenz: `rules/model-portfolio-optimization.md`

## Triggers

- Explizit: "model audit", "monatlicher model check", "portfolio audit", "rho check models"
- Automatisch: Scheduled-Task am 1. des Monats (via `scheduled-tasks` MCP oder DF-07)
- Manuell: nach neuem Modell-Release (z.B. gpt-5.5, claude-5.0, grok-5)

## Workflow (9 Schritte)

### Schritt 1: Inventar-Snapshot

```bash
# Models-Liste pro LLM abrufen:
codex exec --skip-git-repo-check "List available models" | tee /tmp/audit-codex-models.txt
copilot -p "What Claude/GPT models are available to you?" --allow-all-tools | tee /tmp/audit-copilot-models.txt
# Grok via MCP (wenn live), Gemini via --help
```

### Schritt 2: Preis-Update (Web-Search)

```bash
# Aktuelle Preise suchen (Anthropic/OpenAI/xAI/Google/Perplexity Changelogs)
# Persist: branch-hub/findings/PRICES-<YYYYMM>.md
```

### Schritt 3: Subscription-Check

Pruefe pro Abo:
- Verlaengerungsdatum
- Rate-Limits aktuell vs letzter Monat
- Neue Features seit letztem Audit

### Schritt 4: Pentagon-Wargame-Run

**Identische 5 Prompts** an alle aktiven Modelle parallel:

```bash
PENTAGON=$(cat <<'EOF'
P1_FACT: Was ist die korrekte MWSt-Rate in Bayern 2026 fuer Gastronomie Speisen Inhouse?
P2_REASONING: Sensitivitaets-Analyse: wenn rho_a faellt um 10%, wie reagiert Hamilton H = u + lambda*f?
P3_CODE: Python-Funktion atomic-file-write mit Backup + Rollback (20 Zeilen max).
P4_RESEARCH: 3 aktuelle Papers 2025-2026 zu Multi-Agent-LLM-Coordination (kurz).
P5_ADVERSARIAL: Finde 3 Schwachstellen in "rho = CM*Lambda - OPEX - h*Lambda*W ist zeitlos gueltig".
EOF
)

~/.claude/scripts/multi-llm-parallel.sh "$PENTAGON" codex,gemini,copilot,grok 180
```

### Schritt 5: Scoring

Pro Model pro Prompt (P1-P5):
- **Quality-Score** (0-1): via Cross-LLM-Peer-Review (jedes Model scored die anderen)
- **Time-Score** (niedriger = besser): Sekunden bis Antwort
- **Cost-Score**: USD-Aequivalent (Flat = 0 marginal, Opus = hoch)

```
rho_model_prompt = (Quality × Lambda_expected) / (Cost × Time × h)
```

Aggregation: `rho_model_total = SUM(rho_model_P1..P5)`.

### Schritt 6: Delta-Analyse

Vergleich zum letzten Monats-Audit:
- Welches Model gewann neue Role?
- Welches Model verlor Position (Relegation)?
- Neue Modelle seit letzter Runde?
- Pricing-Changes?

### Schritt 7: Role-Reassignment

Matrix aus `rules/model-portfolio-optimization.md` Executor-Role-Matrix wird aktualisiert.
Winners pro Role:
- Conservative: Claude Opus (Hard-Invariante)
- Aggressive: Winner P3 (Code)
- Contrarian: Winner P5 (Adversarial)
- Authority: Winner P1 (Facts)
- Source-Finder: Winner P4 (Research)
- Provocator: Grok (Hard-Invariante if available)

### Schritt 8: Self-Improvement

Automatische Updates:
- `rules/model-portfolio-optimization.md` Executor-Matrix-Zeilen
- `rules/copilot-cli-first.md` / `chatgpt-pro-first.md` if role changed
- Skills `copilot-delegate` / `codex-delegate` Decision-Matrix
- DF-03 `LLM_PROVIDERS` Liste
- `multi-llm-parallel.sh` Default-LLMs
- CLAUDE.md §18 Installed-Skills bei neuen Skills/Rules

Alle Patches in **1 Decision-Card** fuer Martin:
`docs/decision-cards/DC-MONTHLY-AUDIT-<YYYYMM>.md`

### Schritt 9: Findings + Canon

```
branch-hub/findings/MONTHLY-AUDIT-<YYYYMM>.md
  - Pentagon-Results (P1-P5 per Model)
  - rho-Rankings
  - Role-Reassignments
  - Delta-to-last-month
  - Self-Improvement-Patches (Liste)
  - Verdict: HARDENED / CONDITIONAL / NEEDS_REVIEW
  - Cross-LLM-Konsens: 4/5 ADOPT = HARDENED
```

## Output-Schema

```yaml
monthly_audit_<YYYYMM>:
  date: <ISO>
  inventory:
    claude: [opus-4.7, sonnet-4.6, haiku-4.5]
    codex: [gpt-5.4, gpt-5.4-mini, gpt-5.3-codex, ...]
    copilot: [claude-sonnet-4.6, gpt-5, gemini-2.5-pro]
    grok: [grok-4, grok-4-reasoning, grok-code-fast-1]
    gemini: [2.5-pro, ultra]
    perplexity: [sonar-pro]
  pentagon_scores:
    p1_fact: {winner: gemini, rho: 0.85, 2nd: codex, ...}
    p2_reasoning: {winner: claude-opus, rho: 0.92, ...}
    # ...
  role_matrix:
    conservative: claude-opus (invariant)
    aggressive: copilot (p3_winner)
    # ...
  patches:
    - file: rules/model-portfolio-optimization.md
      change: "updated aggressive-executor from X to Y"
    # ...
  rho_gain_estimate: "+€600/Mo expected based on new routing"
  verdict: HARDENED (4/5 LLM-peer-review ADOPT)
  decision_card: docs/decision-cards/DC-MONTHLY-AUDIT-2026-04.md
```

## Hard-No-Improvement (Self-Editing-Limits)

Skill darf **nicht autonom** patchen:
- FIXPUNKT-1 bis 4 (meta-stack-fixpunkte.md) - nur Martin
- rules/crux.md - nur Martin
- CRUX-Nebenbedingungen K_0 Q_0 I_min - nur Martin

Patches auf diese → Decision-Card mit STOP-Flag, Martin-Phronesis-Review.

## rho-Impact (Lifecycle)

- Setup-Cost (einmalig): ~4h Entwicklung + Testing = ~€800
- Pro Monatlicher-Run: 
  - Token-Cost: ~100k Claude + ~flat Andere = ~$7 variable
  - Zeit: ~30 Min Martin-Review der Decision-Card
- Erwarteter Gain: €500-2000/Mo via besseres Routing
- **Break-Even: 1. Monat**
- Kumulativ: €6k-24k/Jahr rho-Gain

## SAE-Isomorphie

Dies ist der **Governance-q-Normalisierungs-Loop** auf LLM-Portfolio-Ebene:
- Jedes Model hat ein q-score (Pentagon-rho)
- Monatliche Relegation (F_CUM_DECAY auf Monats-Takt umgemuenzt)
- Trinity bleibt erhalten (Conservative/Aggressive/Contrarian)
- Shadow-Mode fuer neue Modelle (3-Monat-Probe)

## Scheduling

**Via `scheduled-tasks` MCP oder CronCreate:**
```bash
# Monatlich 1. um 03:00 lokaler Zeit
0 3 1 * * invoke skill "monthly-model-audit"
```

Oder Dark-Factory DF-07 (siehe `branch-hub/archon-workflows/model-portfolio-audit.yaml`).

## Falsifikations-Bedingung

Dieser Skill wird falsifiziert wenn:
- 3 aufeinanderfolgende Audits keine relevanten Routing-Aenderungen liefern (Saturation)
- Audit-Overhead > rho-Gain ueber 6 Monate
- Pentagon-Test-Metriken nicht differenzierend (>80% Ties)

**Revision-Trigger:** Jedes halbe Jahr Meta-Review der Pentagon-Prompts (aktuell sind sie Startpunkt, werden evolvieren).

[CRUX-MK]
