---
name: token-orchestration
meta-ebene: E3
status: AKTIV
aktiviert: 2026-04-19
version: 0.1.0-scaffold
crux-mk: true
depends-on:
  - rules/token-engpass-hierarchie.md
  - rules/context-budget.md §3
  - rules/copilot-cli-first.md
  - rules/chatgpt-pro-first.md
  - rules/grok-heavy-first.md
  - rules/parallel-subagent-dispatch.md (skills/)
origin: FINDING-TOKEN-ORCHESTRATION-SYSTEM-MYZ-2026-04-19
---

# Token-Orchestration [CRUX-MK]

**Konsolidiert 4 Gaps (Gap-1 bis Gap-4) in ein integriertes Token-Optimierungs-System.**
Belegt durch Anthropic-Docs 2026 + Issue #46829 (silent 1h→5m TTL regression) + DF-06-Praxis.

## §1 Prompt-Caching mit expliziter 1h-TTL (Gap-1)

### §1.1 Claude-Code-Status (2026-04-19)
- **Automatisch:** Claude Code CLI nutzt prompt_caching defaultmaessig (System-Prompt, Tools, Messages)
- **Regression:** Anthropic hat zwischen 2026-03-06 und 2026-03-08 silent die Default-TTL von **1h auf 5m** reduziert (Issue #46829, bestaetigt bei 119866 API-Calls mit 17-32% Overpayment)
- **Fix:** Env-Var `ENABLE_PROMPT_CACHING_1H=true` stellt 1h-TTL wieder her. Gegenpol: `FORCE_PROMPT_CACHING_5M=true`
- **Anthropic-Status:** Issue #46829 "not planned" → wir sind selbst verantwortlich

### §1.2 Mechanische Durchsetzung 1h-TTL
1. User-Env: `ENABLE_PROMPT_CACHING_1H=true` in Windows Env-Vars setzen (Machine oder User Scope)
2. Session-Start-Hook prueft env-var und warnt wenn nicht gesetzt
3. Monitoring: `cache_read_input_tokens` vs `cache_creation_input_tokens` in postlog ueberwachen

### §1.3 Cache-Ordering-Regel (zwingend)
Stable-Prefix VOR Dynamic-Suffix:

```
Position 1: System-Prompt (Tools + Personality) — CACHE-MARKED
Position 2: CLAUDE.md (~50k Tokens, Kemmer-Verfassung) — CACHE-MARKED
Position 3: rules/*.md (35 Files, ~30k Tokens) — CACHE-MARKED
Position 4: MEMORY.md (~2k Tokens, semi-stabil) — CACHE-MARKED (4. Breakpoint)
Position 5: Dynamic Context (Session-spezifisch) — NICHT cached
Position 6: User-Query — NICHT cached
```

**Max 4 cache_control Breakpoints pro Request** (Anthropic-Limit).

### §1.4 TTL-Wahl-Regel
- Session-erwartete Dauer > 5min → **1h-TTL** (Write 2.0x Base, aber Read 0.1x)
- Session < 5min ODER Bootstrap wird nur einmal benutzt → **5m-TTL** (Write 1.25x Base)
- Kemmer-Sessions typisch 30min-9h → Default **1h-TTL**

### §1.5 Opus 4.7 Preise (Anthropic-Docs 2026)
| Kategorie | USD/MTok | Faktor |
|-----------|----------|--------|
| Base Input | $5.00 | 1.0x |
| 5m Cache Write | $6.25 | 1.25x |
| 1h Cache Write | $10.00 | 2.0x |
| Cache Read | $0.50 | 0.1x |
| Output | $25.00 | — |

Min-Cacheable fuer Opus 4.7: **4096 Tokens** (unser 50k-Bootstrap liegt drueber).

### §1.6 Subagent-Cache-Isolation (WICHTIG)
Seit 2026-02-05: **Workspace-Level-Isolation**. Subagenten haben eigenen Cache-Keyspace, teilen NICHT mit Parent.
**Konsequenz:** Subagent-Dispatches muessen Mini-Prefix haben (nicht volle 50k Bootstrap), sonst 5x Cache-Write-Cost.

### §1.7 Periodischer Cache-Order-Audit (Gap-7, Martin-Direktive 2026-04-19)
**Problem:** Cache-Ordering driftet. Wenn Dynamic Content (Timestamps, Session-IDs) sich in Stable-Prefix einschleicht → Cache-Miss, TTL-Loop, Overpayment.

**Mechanischer Audit:**
1. DF-10 token-intelligence (siehe §5.2) prueft **woechentlich** (Sa 03:00):
   - Lesen von 7-Tage-PostToolUse-Logs
   - Berechnet Cache-Hit-Rate (cache_read / (cache_read + cache_creation))
   - Bei Hit-Rate < 60%: ALERT in BEACON + Decision-Card
   - Detektiert Drift-Ursache (welche Content-Block hat sich geaendert?)
2. **Monthly-Audit (DF-07 Extension):** Orchestrations-Brief enthaelt Cache-Health-Score
3. **Ad-hoc-Check:** Session-Start-Hook prueft `cache_read_input_tokens` nach 3. Call; wenn 0 → Warnung

**Dirty-Prefix-Kandidaten (zu pruefen):**
- Timestamps in CLAUDE.md Frontmatter/Today
- Session-IDs in MEMORY.md Index
- Dynamic Feedback-Regeln die vor Stable-Rules geladen werden

---

## §2 Batch-API fuer non-urgent Processing (Gap-2)

### §2.1 Anthropic Message-Batches API (Kernfakten)
- **Rabatt:** 50% auf Input+Output vs Regular-API
- **Turnaround:** typisch <1h, SLA max 24h
- **Compatible mit:** cache_control (Rabatte stapeln)
- **Use-Case:** Non-urgent Batch-Processing (DF-Runs, Monthly-Audits, Log-Analysen)

### §2.2 Migration-Policy pro Dark-Factory
| DF | Batch-API? | Grund |
|----|------------|-------|
| **DF-06 NLM-Meta-Harness (daily)** | **JA** | Non-urgent, tolerates <1h-24h Delay |
| **DF-07 model-audit (monthly)** | **JA** | Batch-ideal, keine User-Wartezeit |
| **DF-08 docs-generator** | **JA** | Batch-ideal |
| **DF-01 graphity-book (geplant)** | **JA** | Chapter-Generation ist Batch-taskable |
| **DF-02 kpm-shadow** | **CASE-BY-CASE** | Wenn Rebalance < 4h-SLA: NEIN |
| **DF-03 longevity-research** | **JA** | Non-urgent |
| **DF-04 bias-calibration** | **JA** | Non-urgent |
| **DF-05 auto-commit-push** | **NEIN** | Sub-Sekunden-Latenz noetig |
| **Interactive Claude-Sessions** | **NEIN** | User wartet |

### §2.3 Implementation-Pattern
DFs bekommen neuen Config-Key `batch_mode: true|false` und `batch_max_wait_hours`.
Orchestrator-Code prueft bei Task-Dispatch:
- `if config.batch_mode and estimated_tokens > 10k`: submit via Message-Batches-API
- `else`: regular API

### §2.4 rho-Kalkulation
Beispiel DF-06 daily, 5 NBs parallel, ~50k Tokens/Run:
- Regular: 50k * $5.00/MTok * 30 Tage = $7.50/Monat OPEX
- Batch (50% Rabatt): $3.75/Monat = **-$3.75/Monat pro DF**
- Bei 5 DFs migrated: ~**-$18/Monat OPEX** direkt + Rate-Limit-Budget-Ersparnis (bei MAX-Plan indirekt rho-positiv)

---

## §3 Output-Token-Budget + Lernendes Scoring-System (Gap-3)

### §3.1 Task-Class-Matrix (Initial-Budgets)
| Task-Klasse | max_tokens Initial | Beispiele |
|-------------|-------------------|-----------|
| Trivial-Response | 200 | Ja/Nein, kurze Bestaetigung |
| Routine-Classification | 500 | Label-Vergabe, Parse-Ergebnis |
| Quick-Answer | 1000 | Erklaerung 1 Absatz |
| Substantive-Analysis | 3000 | Wargame-Analyse, Design-Doc-Absatz |
| Long-Synthesis | 8000 | Finding, Decision-Card, Rule |
| Full-Artifact | 15000 | Komplettes Dokument, SKILL.md |
| Emergency | 64000 | Nur wenn Task es wirklich braucht |

### §3.2 Lernendes Scoring-Modell (DF-10)
Static-Budgets sind Startpunkt. Echte Optimierung via Dark-Factory DF-10 `token-intelligence`:
1. **PostToolUse-Hook** loggt jeden API-Call: input_tokens, output_tokens, task_class, stop_reason
2. **Log-Format:** JSONL in `~/.claude/data/token-usage-log.jsonl`
3. **Weekly-Learner:** DF-10 laeuft Sa 03:00 via CronCreate, analysiert 7-Tage-Log:
   - Median + P90 + P99 pro Task-Klasse
   - Truncation-Rate (wenn stop_reason == "max_tokens")
   - Waste-Rate (output_tokens << max_tokens)
4. **Output:** `~/.claude/data/output-budget-scores.json`:
   ```json
   {
     "substantive-analysis": {
       "n_samples": 42,
       "median": 2100,
       "p90": 3800,
       "p99": 5200,
       "truncation_rate": 0.02,
       "waste_rate": 0.34,
       "recommended_max_tokens": 4200
     },
     ...
   }
   ```
5. **PreToolUse-Hook** liest scores.json und setzt dynamisch max_tokens = `p90 * 1.1` pro Task-Klasse.

### §3.3 Besser-als-Scoring-Alternativen (pruefen)
Das obige ist **Phase-1 Static-Statistik**. Fortgeschrittene Moeglichkeiten fuer spaetere Phasen:
- **Phase-2 Thompson-Sampling:** Bayes-Posterior pro Task-Klasse, Exploration/Exploitation
- **Phase-3 Reward-Shaping:** Delta-rho pro Output-Token messen, Budget so setzen dass rho maximiert (nicht nur Token-Sparnis)
- **Phase-4 Adaptive-Sampling:** Start mit niedrigem Budget, bei Truncation schrittweise erhoehen (Session-interne Loop)
- **Phase-5 LLM-as-Judge:** Haiku-Zweitrangig bewertet Output-Verbosity "war das zu lang?"

### §3.4 Mechanische Durchsetzung
Pre-TaskHook setzt max_tokens basierend auf:
1. Task-Class-Classifier (Haiku-basiert, sub-Sekunde) → class_id
2. Lookup in `output-budget-scores.json` → max_tokens
3. Fallback: Static-Matrix §3.1 wenn DF-10 scores.json nicht existiert

---

## §4 Skill-Delegation fuer Repeat-Patterns (Gap-4)

### §4.1 Problem
Subagent-Dispatches haben oft ~2000 Token Boilerplate (CRUX-Preamble, Pflicht-Lektuere-Liste, Pflicht-Felder, Format-Template). Bei Lambda 10 Dispatches/Session * 2000 = 20k Token nur fuer Boilerplate.

### §4.2 Loesung: Parametrischer Template-Dispatcher
Skill `subagent-template-dispatch` mit Template-Registry:

```yaml
# ~/.claude/skills/subagent-template-dispatch/templates/category-template-extraction.yaml
id: category-template-extraction
version: 1.0
required_params:
  - category_id            # z.B. "C6"
  - category_name          # z.B. "Tech-Manual"
  - baseline_finding_path  # z.B. "MYZ00011-Templates-Cat-5-Referenziell.md"
  - line_range             # z.B. "500-700"
prompt_skeleton: |
  <ROLLE>: Subagent fuer Kategorie-{category_id} {category_name} Template-Extraktion [CRUX-MK].
  <KONTEXT>: Graphity-Book-Framework v1.1.0-live, Template-Catalog-Erweiterung.
  <BASELINE>: Lies {baseline_finding_path} als Format-Vorlage.
  <AUFTRAG>: T1+T2+T3-Struktur, {line_range} Zeilen, Frontmatter wie Baseline.
  <PFLICHT-FELDER>: template_category, t1_name, t2_name, t3_name, cross_ref_patterns, invariants.
  <BUDGET>: max 3h, max 50 Reads, Kaestner-Ton.
  <MELDE AM ENDE>: Pfad + Zeilen + 5 Kern-Metriken.
```

Dispatcher-Aufruf:
```python
from token_orchestrator import dispatch_template
dispatch_template(
  template_id="category-template-extraction",
  params={
    "category_id": "C6",
    "category_name": "Tech-Manual",
    "baseline_finding_path": "MYZ00011-Templates-Cat-5-Referenziell.md",
    "line_range": "500-700"
  }
)
```

**Effekt:** Boilerplate wird aus Template gerendert (lokal, kein Claude-Token). Nur die parametrische Diff geht in den Prompt → **~70% Token-Ersparnis pro Dispatch**.

### §4.3 Feedback-/Auswertungs-System (Gap-4 Martin-Anforderung)
Wichtig: *"mit Feedback und auswertungssystem so dass du deutlich die Wertvollen Token zur voll Informierten Orchestrations nutzt"*

Integration mit DF-10:
1. Template-Dispatcher loggt pro Dispatch:
   - `template_id`, `rendered_tokens`, `subagent_output_tokens`, `subagent_quality_score` (rho-Gain)
   - Wenn Quality-Score niedrig: Template-Version-Bump erforderlich
2. **Orchestrations-Dashboard** (`llm_usage_dashboard.py` erweitern):
   - Pro Template: Avg rho-Gain, Avg Token-Cost, Template-ROI (rho/Token)
   - Pro Task-Klasse: Welches Template/Skill/Delegate hat hoechstes ROI?
   - **Claude (ich) sieht das bei Session-Start** → voll-informierte Orchestrierungs-Entscheidung
3. **Claude-Orchestrator-Brief** bei Bootstrap: `~/.claude/data/orchestration-brief.md` mit Top-10-Template-ROIs, Top-5 Skill-Delegations, Top-3 LLM-Routes der letzten 30 Tage.

---

## §5 Integration: Hook-Trinity + DF-10 + Skill

### §5.1 Hook-Registration in settings.json
```json
"PreToolUse": [
  {
    "matcher": "Agent|Task|Bash",
    "hooks": [
      { "type": "command", "command": "python C:/Users/marti/.claude/scripts/token-budget-enforcer.py" }
    ]
  }
],
"PostToolUse": [
  {
    "matcher": "*",
    "hooks": [
      { "type": "command", "command": "python C:/Users/marti/.claude/scripts/token-usage-logger.py" }
    ]
  }
],
"Notification": [
  {
    "matcher": "session_start",
    "hooks": [
      { "type": "command", "command": "python C:/Users/marti/.claude/scripts/session-start-cache-check.py" }
    ]
  }
]
```

### §5.2 DF-10 token-intelligence (Scheduled-Task)
- **Frequenz:** woechentlich Sa 03:00 (stabil, kein Konflikt mit DF-06 02:00 + DF-07 monatlich)
- **Shadow-Mode:** 2 Wochen ohne Budget-Enforcement (nur Logging) vor Live
- **Kill-Switch:** STOP.flag in `~/.claude/data/`
- **Audit:** `audit/token-intelligence-runs.jsonl`

### §5.3 Skill subagent-template-dispatch
- Template-Registry: `~/.claude/skills/subagent-template-dispatch/templates/*.yaml`
- Dispatcher-Script: `~/.claude/skills/subagent-template-dispatch/dispatch.py`
- Initial-Templates: category-template-extraction, cross-llm-adversarial, finding-writer, decision-card-writer

### §5.4 Haiku-Fallback-Policy (Gap-5, Martin-Direktive 2026-04-19)
**Martin-Kalibrierung:** Haiku ist **NICHT Primary** fuer Trivialitaeten. Reihenfolge:
1. **Primary (Flat-LLMs mit Sunk-Cost-Abo):** Copilot CLI → Codex → Gemini → Grok (je nach Task-Typ)
2. **Sekundaer (Claude-Opus):** wenn Task K_0/Q_0/Phronesis/Meta-E4+
3. **Fallback (Haiku):** nur wenn ALLE Flat-LLMs erschoepft (Rate-Limit, Service-Disruption, Auth-Expired)

**Grund:** Flat-Abos sind Sunk-Cost (Pro+ $39, Pro $200, Heavy $300, Ultra bundle). Jeder Call via Flat-LLM = €0 marginal. Haiku kostet Opus-Rate ($1/MTok input), also NICHT gratis.

**Trigger-Kaskade fuer Haiku-Fallback (Martin-Kalibrierung 2026-04-19 "erst wenn Flat 100% erschoepft"):**
```python
def route_trivial_task(task):
    # Priority 1: ALLE Flat-LLMs nacheinander versuchen (Exhaustion-Modell)
    for llm in [copilot, codex, gemini, grok, perplexity]:
        if llm.available and not llm.rate_limited and not llm.auth_expired:
            try:
                return llm.execute(task)
            except (RateLimitError, AuthError, ServiceDisruptionError) as e:
                log_exhaustion(llm=llm.name, reason=type(e).__name__)
                continue  # next flat-LLM in chain
    # Priority 2: Claude-Opus wenn Task Opus-relevant (K_0/Q_0/Phronesis/Meta-E4+)
    if task.needs_opus():
        return claude_opus.execute(task)
    # Priority 3: Haiku-Fallback - NUR wenn ALLE Flat-LLMs wirklich erschoepft
    # ODER Task-Timeout-Deadline bedroht
    log_fallback_trigger(reason="all_flat_llms_exhausted_or_time_critical",
                          flat_llms_tried=["copilot","codex","gemini","grok","perplexity"],
                          time_critical=task.has_deadline())
    return claude_haiku.execute(task)
```

**Monitoring (Martin-Kalibrierung 2026-04-19):** `~/.claude/data/haiku-fallback-log.jsonl` loggt jeden Fallback-Trigger mit:
- `flat_llms_tried` (Exhaustion-Chain)
- `last_flat_llm_error` (warum es nicht ging)
- `time_critical` (war deadline-bedroht?)

**Alert-Policy:** "Nach Zeit nachjustieren" statt festem Schwellenwert. DF-10 Weekly-Learner analysiert Trend ueber 4 Wochen:
- Bei steigendem Fallback-Trend: Decision-Card (Rate-Limit-Upgrade? Abo-Wechsel?)
- Bei stabil-niedrigem Trend (< 3/Woche): OK, keine Alert
- Bei Cluster-Trigger (5+ in 1 Tag): sofortige BEACON-Notiz

**Wichtig:** Haiku ist **NICHT Ersatz** fuer Flat-LLMs, sondern **Safety-Net** wenn ALLE Flat-Kanaele versagen. Grund: Haiku ist anthropic-Opus-Rate-Limit-teilend (nicht Sunk-Cost-Abo). Jeder Haiku-Call belastet Opus-Kontingent indirekt.

---

## §6 rho-Quantifizierung (konsolidiert)

| Gap | Mechanismus | OPEX-Ersparnis | W_0 Gewinn | Setup-h |
|-----|-------------|----------------|------------|---------|
| 1 | 1h-TTL + Cache-Ordering | ~€80-180/Monat (Opus) | Rate-Limit-Budget | 1h |
| 2 | Batch-API DF-Migration | ~€20-60/Monat | 50%-Durchsatz-Plus | 4h |
| 3 | Output-Budget-Scoring | ~€40-80/Monat | Iterations-Schaerfe | 6h |
| 4 | Template-Dispatch | ~€30-60/Monat | Orchestrations-Info | 4h |
| 5 | Haiku-Fallback (nur Fallback, nicht Primary) | ~€5-15/Monat indirekt (Service-Kontinuitaet) | Ausfallsicherheit | 2h |
| 7 | Periodischer Cache-Audit | 0 direkt (praeventiv) | Drift-Erkennung | 1h (in DF-10 integriert) |
| **Summe** | | **~€175-395/Monat** | **~€2100-4740/Jahr** | **18h** |

**Break-Even: <1 Monat** bei Lambda 10+ Sessions/Tag.

---

## §7 CRUX-Bindung

- **K_0:** geschuetzt (keine K_0-Decisions an DF-10-Learner; Budget-Enforcement reversibel via STOP.flag)
- **Q_0:** erhoeht (weniger Truncation = vollstaendigere Outputs; bessere Orchestrierungs-Entscheidungen)
- **I_min:** strukturiert (Hook-Trinity + DF-10 + Skill + Rule = 4 Ebenen durchsetzend)
- **W_0:** direkt optimiert — **~€2000-4500/Jahr + Rate-Limit-Entlastung**

## §8 Anti-Patterns

1. **Manueller Cache_control in Prompt-Strings:** Claude Code abstrahiert; explicit nur wenn API-Call direkt
2. **Subagent mit Full-Bootstrap-Prompt:** Subagent-Prompt MUSS minimal sein (kein Re-Include von CLAUDE.md)
3. **Batch-API fuer interactive Sessions:** User wartet, 1h-Latenz ist UX-Verletzung
4. **Output-Budget ohne Lernen:** Statische Caps ignorieren Task-Variabilitaet
5. **Template-Dispatch ohne Quality-Feedback:** Dispatch-Frequency steigt, Qualitaet faellt unbemerkt
6. **ENABLE_PROMPT_CACHING_1H nicht gesetzt:** 1.6-2x Overpayment bei 5m-Default

## §9 Falsifikations-Bedingung

- Wenn ueber 4 Wochen realer OPEX-Gain < €50/Monat (Brier gegen €170-380 vermutet): Setup revidieren
- Wenn DF-10 Learner Qualitaets-Drop > 10% (Truncation-Rate steigt): statische Matrix zurueck
- Wenn Anthropic Batch-API-Discount aendert: §2 Policy re-kalibrieren
- Wenn Claude Code CLI automatisches 1h-TTL-Fix deployed (Issue #46829 reopened): §1.2 vereinfachen

## §10 Promotion-Pfad

- v0.1.0-scaffold (2026-04-19, diese Datei): **AKTIV** in rules/
- Nach 4 Wochen Shadow-Mode DF-10: Evidenz sammeln (rho-Gain real vs estimated)
- Nach 3 erfolgreichen Adoptionen in anderen Branches: promote zu rules/crux.md §10 (Token-Verfassung als CRUX-Invariante)

[CRUX-MK]
