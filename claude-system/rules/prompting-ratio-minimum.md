---
type: rule-proposal
name: prompting-ratio-minimum
meta-ebene: E3
claim-type: empirical
branch: Work-D
status: PROPOSAL
created: 2026-04-20
aktiviert-in: 2026-05-20
cross-llm-reference: branch-hub/cross-llm/2026-04-20-WELLE-11-PROMPTING-RATIO-WARGAME.md
belegung: branch-hub/findings/WELLE-10-USE-CASE-BEST-PRACTICE-2026-04-20.md
crux-mk: true
---

# Prompting-Ratio-Minimum [CRUX-MK] — PROPOSAL

> STATUS: PROPOSAL. Wird erst zu `prompting-ratio-minimum.md` (ohne `.PROPOSAL`), wenn Martin approve.
> Belegt durch 9 Cross-LLM-Messpunkte Welle 11 + 650 Messpunkte Welle 10 (Input-Tokens geschaetzt).

## Zweck

Prompts sollen so verdichtet werden, dass das Modell echten Hebel liefert. Martin-Direktive 2026-04-20:
> "Input:Output-Ratio sollte bei 1:30 oder besser 1:50 liegen. Unter 1:5 sind die Fragen zu schwach und das Modell muss gar nicht arbeiten."

Empirisch belegt: Kompakte Prompts (30-60 Input-Tokens) mit Output-Vertrag (Wortziel + Form) erreichen reproduzierbar 1:45 bis 1:90 ueber alle drei getesteten Modelle (Codex gpt-5.4, Gemini 2.5 Pro, Copilot gpt-5.x).

Diese Regel verankert die Ratio als messbare Qualitaets-Metrik im PreToolUse/PostToolUse-Pfad.

## Definition (klarer Begriff)

**Martin-Ratio** = output_tokens / input_tokens (also 1:50 heisst: Output ist 50x so lang wie Input).

Nicht zu verwechseln mit der umgekehrten Input:Output-Ratio der Kosten-Literatur (dort ist kleiner besser). Diese Regel nutzt durchgaengig Martin-Ratio (groesser ist besser).

## Schwellenwerte

| Zone | Martin-Ratio | Reaktion |
|------|--------------|----------|
| HARD-FLOOR | < 1:5 | BLOCK + Prompt-Refactor-Alert (Ausnahme: Trivial-Response- und Kompressionsklassen, siehe §Ausnahmen) |
| SUB-TARGET | 1:5 bis 1:30 | WARN ueber 5-Call-Fenster; Template-Review-Empfehlung |
| TARGET | 1:30 bis 1:50 | OK, log-only |
| OPTIMAL | 1:50+ | OK, als Architekt-Benchmark markieren |

## Messung

- **input_tokens:** via `tiktoken.get_encoding("cl100k_base").encode(prompt)`, Fallback `len(prompt)//4`.
- **output_tokens:** analog auf Response.
- **martin_ratio:** `output_tokens / max(input_tokens, 1)`.
- **Logging:** JSONL-Zeile pro Call nach `~/.claude/data/token-usage-log.jsonl`, Format:
  ```json
  {"ts":"ISO","agent":"<name>","task_class":"<klasse>","in":<int>,"out":<int>,"ratio":<float>,"stop_reason":"<str>"}
  ```
- **Integration:** PreToolUse-Hook (Budget-Enforcer) + PostToolUse-Hook (Logger). DF-10 Weekly-Learner fasst auf Task-Klasse-Ebene zusammen und aktualisiert `~/.claude/data/output-budget-scores.json`.

## Ausnahmen (keine Ratio-Pflicht)

1. **Trivial-Response-Klasse** (max_tokens 200): Binaere Entscheidungen, Statusbestaetigungen. Ratio-Check irrelevant.
2. **Kompressionsklassen:** Zusammenfassung, Extraktion, Klassifikation. Hier ist <1:5 Ziel, nicht Fehler. Task-Class-Classifier muss das erkennen (Haiku-basiert, Pre-Hook).
3. **Tool-Call-Sequenzen** ohne Free-Text-Output: Nur Tool-Calls, kein Content. Ratio-Metrik greift nicht.
4. **Interaktive Martin-Sessions:** Martin-Turns sind keine Orchestrations-Dispatches. Keine Enforcement-Hooks auf Martin-Input.

## Mechanische Durchsetzung

**Phase 1 (Shadow, 2026-04-20 bis 2026-05-20):**
- Nur Logging, keine Blocks, keine Warns-an-User.
- DF-10 sammelt Baseline-Daten fuer die 5 gaengigen Task-Klassen.

**Phase 2 (Live mit WARN, ab 2026-05-20):**
- WARN-Zone aktiviert. PostToolUse-Hook schreibt Alert ins BEACON bei 3+ Sub-Target-Calls in Folge pro Agent.
- BLOCK noch nicht aktiv.

**Phase 3 (Live mit BLOCK, ab 2026-06-20):**
- Pre-Dispatch-Hook in `subagent-template-dispatch` rechnet erwartete Ratio aus Template-Historie aus. Bei Erwartung < 1:5: BLOCK + Martin-Alert.
- Ausnahmeliste (siehe oben) wird geprueft.

## Anti-Patterns

1. **"Beschreibe ausfuehrlich" ohne Wortziel** → Default-Verbositaet greift, Ratio kippt unter 1:10.
2. **Tool-Trigger-Woerter ohne Tool-Bedarf** ("checke", "verifiziere", "lies") bei Codex-CLI → Tool-First-Failover frisst Output-Slot.
3. **Context-Bloat bei Multi-Agent-Cascade** → Vollhistorie wird weitergereicht, jeder Agent liest 20k und antwortet 200.
4. **Ping-Pong-Critic-Loops** → Validator und Generator tauschen Vollkontexte fuer Stilfixes.
5. **Vage Ziel-Definition** → "Mach das besser" ohne Qualitaets-Kriterium.
6. **Ratio-Gaming via Bulk-Padding** → Modell kuenstlich lang reden lassen ohne Inhaltshebel. Darum pairing mit Quality-Score (DF-10 Feedback-Loop) notwendig.

## Integration mit anderen Rules

- `rules/token-orchestration.md §3` (Output-Token-Budget) — diese Rule macht den qualitativen Gegenpol zur quantitativen Budget-Obergrenze. Zusammen: "nicht zu lang, nicht zu kurz, dicht genug".
- `rules/token-engpass-hierarchie.md` — Ratio-Optimierung reduziert Claude-Opus-Token-Bedarf pro Informations-Einheit.
- `rules/context-budget.md §5` (Lambda-Honesty) — Ratio-Schaetzungen werden explizit als geschaetzt markiert, wenn tiktoken nicht verfuegbar.
- `rules/meta-governance-framework.md §G4` (Predictive-Power) — Ratio als E3-Predictive-Metrik fuer Prompt-Qualitaet.

## SAE-Isomorphie

Martin-Ratio ist isomorph zu Agent-Throughput-Metrik in SAE v8 (`mu_b` pro Slot). Niedrige Ratio bei gegebenem Input = `mu_b` unter erwartetem Niveau = Relegations-Kandidat.

## CRUX-Bindung

- **K_0:** indirekt geschuetzt (weniger Opus-Overpayment durch dichte Prompts).
- **Q_0:** direkt erhoeht (dichte Prompts liefern dichtere Antworten; Default-Verbositaet vermieden).
- **I_min:** erhoeht (mechanische Metrik in PreToolUse-Hook).
- **W_0:** direkt optimiert (Coordinator-Worker-Hebel wird messbar und lernbar).

## rho-Abschaetzung

- Verdraengter Opus-Aufwand bei Wechsel auf Flat-LLMs mit Ratio-Optimierung: **~1.140 EUR/Monat** (30 Wellen * 38 EUR, siehe Finding §4 und §8.2).
- Setup-Cost: 2h Hook + DF-10-Integration (bereits geplant, Shadow-Mode laeuft).
- **Break-Even:** < 1 Woche bei Lambda 1 Welle/Tag.

## Falsifikations-Bedingung

Regel ist falsifiziert, wenn:

1. Ueber 30 Tage DF-10-Sampling Median-Ratio auf vergleichbaren Prompt-Klassen < 1:20 bleibt.
2. Hard-Floor-Block-Rate > 5% der Dispatches (zu strikt — legitime Trivial-Klassen werden nicht korrekt ausgenommen).
3. Ein alternatives Qualitaets-Metrik-System mit nachgewiesen besserer Vorhersagekraft ueber 6 Monate besser ist (siehe G5 Sparsamkeit).

**Replacement-Trigger:** Bei Falsifikation → Task-Klassen-spezifische Ratio-Zielwerte statt pauschal 1:30.

## Selbst-Anwendung

Diese Rule ist selbst ein Prompt an Claude. Eigene Ratio beim Lesen dieser Datei: Irrelevant, denn das ist kein Dispatch-Kontext. Die Regel zielt auf Dispatch-Pfade, nicht auf Rule-Consumption.

Claim-Type: `empirical`. Scope (G7): lokal/artefaktbezogen (konkrete Ratio-Messung an konkreten Dispatch-Calls, keine globale Meta-Aussage ueber E3 als Klasse).

[CRUX-MK]
