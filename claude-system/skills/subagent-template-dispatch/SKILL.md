---
name: subagent-template-dispatch
description: |
  Parametrischer Subagent-Dispatcher mit Template-Registry. Reduziert Boilerplate-Tokens bei
  Subagent-Prompts um ~70% durch lokales Rendering. Integriert mit DF-10 fuer Feedback-Loop
  (Template-ROI-Messung = Delta-rho pro Template ueber Zeit).
  Triggers: "dispatch template", "subagent mit template", "template X fuer Kategorie Y",
    automatisch wenn ein wiederkehrendes Prompt-Muster (3+ Uses) detektiert wird.
  Capability: Template-Render lokal + Subagent-Spawn mit minimalem Prompt + Post-Dispatch-Logging.
  NICHT: fuer Einmal-Prompts oder K_0/Q_0-Phronesis (Opus direkt).
crux-mk: true
version: 0.2.0
meta-ebene: E3
origin: rules/token-orchestration.md §4
status: SCAFFOLD (Martin-Approval Gap-4 2026-04-19)
depends-on:
  - rules/token-orchestration.md §4
  - rules/parallel-subagent-dispatch.md
  - DF-10 token-intelligence (Feedback-Loop)
---

# subagent-template-dispatch [CRUX-MK]

## Zweck

Wiederkehrende Subagent-Prompts werden nicht mehr jedes Mal als 2000-Token-Boilerplate neu geschrieben, sondern aus Template-Registry parametrisch gerendert.

**Effekt:**
- ~70% Token-Ersparnis pro Dispatch (nur parametrische Diff geht an Claude)
- Template-Versionierung + A/B-Test moeglich
- Feedback-Loop via DF-10 misst Template-ROI (rho-Gain pro Dispatch)

## Wann nutzen

- Repetitives Pattern mit 3+ historischen Uses
- Task-Typ klar klassifizierbar
- Output-Struktur deterministisch erwartbar

**NICHT fuer:**
- K_0/Q_0/Phronesis (Opus direkt)
- Einmal-Prompts ohne Zukunftsnutzung
- Templates die noch unter Entwicklung sind (v<1.0)

## Template-Registry (Initial-Set)

| Template-ID | Version | Use-Case | Est. Token-Ersparnis |
|-------------|---------|----------|---------------------|
| `category-template-extraction` | 1.0 | MYZ00006-11-Pattern (Graphity-Book Cat-1-7) | 1500 Tokens/Dispatch |
| `cross-llm-adversarial` | 1.0 | Codex+Gemini+Grok Konvergenz-Test | 1200 Tokens/Dispatch |
| `finding-writer` | 1.0 | branch-hub/findings/*.md mit Frontmatter | 1000 Tokens/Dispatch |
| `decision-card-writer` | 1.0 | docs/decision-cards/*.md Binary-Format | 800 Tokens/Dispatch |

## Template-Format

```yaml
# ~/.claude/skills/subagent-template-dispatch/templates/<template-id>.yaml
id: category-template-extraction
version: 1.0
subagent_type: general-purpose
required_params:
  - category_id
  - category_name
  - baseline_finding_path
  - line_range
optional_params:
  - priority (default: "standard")
prompt_skeleton: |
  <ROLLE>: Subagent fuer Kategorie-{category_id} {category_name} Template-Extraktion [CRUX-MK].
  <KONTEXT>: Graphity-Book-Framework v1.1.0-live, Template-Catalog-Erweiterung.
  <BASELINE>: Lies {baseline_finding_path} als Format-Vorlage.
  <AUFTRAG>: T1+T2+T3-Struktur, {line_range} Zeilen, Frontmatter wie Baseline.
  <PFLICHT-FELDER>: template_category, t1_name, t2_name, t3_name, cross_ref_patterns, invariants.
  <BUDGET>: max 3h, max 50 Reads, Kaestner-Ton.
  <MELDE AM ENDE>: Pfad + Zeilen + 5 Kern-Metriken.
expected_output_structure:
  - "File-Pfad"
  - "Line-Count"
  - "Top-5 Metrics"
feedback_config:
  quality_score_method: "rho_gain_estimated"   # oder "martin_review" / "llm_judge"
  min_quality_threshold: 0.7
```

## Invocation-Pattern

```python
# Python-API (wenn Skill direkt aufgerufen)
from skill import dispatch_template

result = dispatch_template(
    template_id="category-template-extraction",
    params={
        "category_id": "C6",
        "category_name": "Tech-Manual",
        "baseline_finding_path": "MYZ00011-Templates-Cat-5-Referenziell.md",
        "line_range": "500-700"
    },
    run_in_background=True,
)
```

Oder: Claude-Turn-Dispatch mit Skill-Reference:
```
Skill: subagent-template-dispatch
Template: category-template-extraction
Params: {category_id: "C6", category_name: "Tech-Manual", ...}
```

## Feedback-/Auswertungs-System (Gap-4 Kern)

Jeder Dispatch wird geloggt in `~/.claude/data/template-dispatch-log.jsonl`:
```json
{
  "ts": "2026-04-19T15:30:00",
  "template_id": "category-template-extraction",
  "template_version": "1.0",
  "params_hash": "abc123...",
  "rendered_tokens": 600,
  "subagent_id": "a3644b6d...",
  "output_tokens": 3400,
  "duration_ms": 180000,
  "quality_score": 0.85,   # via rho_gain-Schaetzung
  "martin_review_pending": false,
}
```

DF-10 Weekly-Learner aggregiert:
- **Template-ROI** = avg(quality_score) / avg(rendered_tokens + output_tokens)
- **Top-Templates** in Orchestration-Brief (§4.3 Rule)
- **Low-ROI-Templates (< 0.3)** → flag fuer Version-Update
- **Neue-Pattern-Detector** → detektiert 3+ aehnliche Prompts ohne Template → schlaegt Template-Scaffold vor

## Bootstrap-Integration (Gap-4 Martin-Anforderung)

Beim Session-Start liest Claude aus `~/.claude/data/orchestration-brief.md`:
```
## Top-Templates (30-Tage-Window)
- category-template-extraction: 8 dispatches, avg ROI 0.92
- cross-llm-adversarial: 5 dispatches, avg ROI 0.78
- finding-writer: 4 dispatches, avg ROI 0.65 (⚠ Review empfohlen)
```

→ Claude sieht bei Bootstrap direkt welche Templates zuverlaessig sind und welche Aufmerksamkeit brauchen. **Vollinformierte Orchestrierungs-Entscheidung.**

## Promotion-Pfad

- v0.1.0-scaffold (jetzt, Martin-Approval via Gap-4 2026-04-19)
- v0.2.0-shadow: 10+ Dispatches in Log, erste ROI-Daten
- v1.0.0-live: 3+ Templates mit avg ROI > 0.7 ueber 4 Wochen
- v2.0.0-autodetect: Pattern-Detector schlaegt automatisch neue Templates vor

## CRUX-Bindung

- **K_0:** geschuetzt (keine Delegation von K_0-Decisions, Templates nur fuer non-Phronesis-Tasks)
- **Q_0:** erhoeht (konsistentere Subagent-Outputs durch Template-Struktur)
- **I_min:** strukturiert (Template-Registry versioniert + feedback-gemessen)
- **W_0:** direkt **~70% Token-Ersparnis** pro Dispatch + ROI-gesteuerte Optimierung

## § Ratio-Monitoring (v0.2.0, aktiviert 2026-04-20)

**Quelle:** Welle 11 Cross-LLM-Wargame (`branch-hub/cross-llm/2026-04-20-WELLE-11-PROMPTING-RATIO-WARGAME.md`), 9 Messpunkte, CROSS-LLM-2OF3-HARDENED.

### § A. Metrik-Definition

Pro Dispatch loggt der Dispatcher **Martin-Ratio** = `output_tokens / input_tokens`:
- **input_tokens** = tiktoken-Count des gerenderten Template-Prompts (nicht des Template-Skeletons, sondern des finalen Prompts mit Parametern).
- **output_tokens** = tiktoken-Count der Subagent-Response.
- **ratio** = float, groesser ist besser.

Fallback ohne tiktoken: `len(text) // 4` als Schaetzung (Lambda-Honesty-Marker im Log-Record).

### § B. Schwellen (siehe `rules/prompting-ratio-minimum.md.PROPOSAL`)

| Zone       | Martin-Ratio | Dispatcher-Reaktion |
|------------|--------------|---------------------|
| HARD-FLOOR | < 1:5        | Alert an DF-10 + Template-Review-Flag |
| SUB-TARGET | 1:5-1:30     | WARN bei 5-Call-Fenster < Target |
| TARGET     | 1:30-1:50    | OK, log-only |
| OPTIMAL    | 1:50+        | als Architekt-Benchmark markieren |

Ausnahmen: Trivial-Response-Klasse, Kompressionsklassen (Zusammenfassung/Extraktion) sind `ratio_exempt: true` im Template-Frontmatter.

### § C. Log-Format-Erweiterung

Bestehendes Dispatch-Log-Record wird um zwei Felder erweitert:
```json
{
  "template_id": "category-template-extraction",
  "rendered_tokens": 520,
  "output_tokens": 3400,
  "martin_ratio": 6.54,
  "ratio_zone": "SUB-TARGET",
  "ratio_exempt": false,
  "duration_ms": 180000,
  "quality_score": 0.85,
  "martin_review_pending": false
}
```

### § D. Template-ROI (erweitert)

Template-ROI war bisher `avg(quality_score) / avg(rendered_tokens + output_tokens)`. Erweiterung um Ratio-Komponente:

```
Template-ROI = quality_score * log10(martin_ratio) / total_tokens
```

`log10` weil Ratio-Steigerung bei sehr hohen Ratios diminishing returns hat (1:30 → 1:300 ist nicht 10x wertvoller).

### § E. Woechentlicher Ratio-Score pro Template

DF-10 Weekly-Learner (Sa 03:03) aggregiert zusaetzlich pro Template:
- `median_ratio`
- `p10_ratio` (schlechtes Zehntel)
- `p90_ratio` (bestes Zehntel)
- `hard_floor_rate` (wie oft unter 1:5)
- `target_rate` (wie oft >= 1:30)

Output in `~/.claude/data/template-ratio-scores.json`, eingespeist in Orchestration-Brief.

### § F. Template-Refactor-Trigger

Wenn ueber 5+ Dispatches eines Templates:
- `median_ratio < 1:20` UND
- `quality_score > 0.6` (also Output ist gut, aber zu ausfuehrlich fuer Input)

→ **Template zu duenn**. Alert fuer Template-Editor: Prompt ist nicht dicht genug, Parameter-Dichte erhoehen oder Kontext reduzieren.

Wenn:
- `median_ratio < 1:10` UND
- `quality_score < 0.5`

→ **Template kaputt**. Dispatch-Block, Martin-Alert, Template-Version-Rollback.

### § G. Codex-spezifische Sub-Regel

Bei Template-Dispatches an Codex-CLI:
- Kein Tool-Trigger-Wort im gerenderten Prompt ("checke", "lies", "verifiziere", "suche").
- Wenn Template-Zweck das verlangt: `codex_trigger_allowed: true` im Frontmatter setzen, dann wird Ratio-Exemption fuer diesen Dispatch aktiv.
- Alternative: Flag `--skip-git-repo-check` ist default bei allen Codex-Aufrufen.

Empirisch: Codex liefert ohne Tool-Trigger und mit Wortziel 1:45-1:73 (Welle 11), mit Tool-Trigger ohne Wortziel nur 1:3 (Welle 10).

## Version-Bump v0.1.0-scaffold → v0.2.0

Aenderungen:
- § Ratio-Monitoring neu hinzugefuegt (Abschnitte A-G)
- Frontmatter-Feld `ratio_exempt` fuer Templates eingefuehrt
- Template-ROI-Formel um Ratio-Komponente erweitert
- Codex-spezifische Sub-Regel fuer Tool-Trigger-Woerter

## Referenz

- Rule: `rules/token-orchestration.md §4`
- Rule-Proposal: `rules/prompting-ratio-minimum.md.PROPOSAL`
- Welle-11-Wargame: `branch-hub/cross-llm/2026-04-20-WELLE-11-PROMPTING-RATIO-WARGAME.md`
- Welle-10-Use-Case: `branch-hub/findings/WELLE-10-USE-CASE-BEST-PRACTICE-2026-04-20.md`
- DF-10: `C:/Users/marti/Projects/dark-factories/DF-10-token-intelligence/`
- Predecessor-Skill: `~/.claude/skills/parallel-subagent-dispatch/` (orchestriert Level ueber Einzel-Dispatch)

[CRUX-MK]
