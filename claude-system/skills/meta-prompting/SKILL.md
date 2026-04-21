---
name: meta-prompting
description: |
  Systematische Anwendung von Conductor-Pattern (Suzgun+Kalai 2024, F160) und
  OPRO-Loop (Google DeepMind 2023, F161) auf Multi-Step-Aufgaben.
  Spezialisierte LLMs + iterative Prompt-Optimierung > ein grosses General-LLM.
  Empirisch bis zu 1567x guenstiger bei +15-17% Quality-Lift auf Multi-Step-Tasks.
status: PROPOSAL
triggers:
  - "meta-prompting anwenden"
  - "conductor pattern"
  - "opro loop"
  - "prompt iterativ optimieren"
  - "multi-step prompt"
  - "prompt optimization"
  - "sae-agent-prompt verbessern"
  - "hotel-agent-prompt verbessern"
crux-mk: true
version: 0.1.0-PROPOSAL
created: 2026-04-18
author: Opus 4.7 (1M) Blueprint-Formalisierungs-Subagent (Architekt-2)
blueprint: B52
parent-decision-card: G:/Meine Ablage/Claude-Vault/docs/decision-cards/B52-Meta-Prompting-Skill.md
approval: martin-kemmer-pending
review-pflicht: true
tier: 1 (Archon-Workflow-Kandidat, NICHT Dark-Factory)
---

# Meta-Prompting Skill [CRUX-MK] -- PROPOSAL

**Status:** PROPOSAL. Datei endet auf `.PROPOSAL`. Wird erst zu `SKILL.md` (in `~/.claude/skills/meta-prompting/`) wenn Martin approved.

**Referenz:** [Decision Card B52](G:/Meine Ablage/Claude-Vault/docs/decision-cards/B52-Meta-Prompting-Skill.md)

---

## 1. Wann triggern (Selektivitaets-Regel, P-B52-1)

Skill triggert NUR wenn mindestens eines gilt:

| Bedingung | Beschreibung |
|---|---|
| (a) Multi-Step >= 3 | Task zerlegbar in >= 3 unabhaengige Sub-Schritte |
| (b) Prompt-Laenge >= 500 Woerter | Komplexer System-Prompt fuer Agent-Klasse |
| (c) Martin explizit invoked | `/meta-prompting` Slash-Command oder "meta-prompting anwenden" |
| (d) Build-Time-Optimierung | Periodische Optimierung eines Agent-Prompts (1x/Quartal) |

**NICHT triggern bei:**
- Triviale Einzel-Frage ("wie spaet ist es?", "gib mir die Datei")
- Lookups in Vault/branch-hub
- Reine Uebersetzungen
- Formale Deduktionen die direkt loesbar sind

**Warum selektiv:** Sonst wird Skill zur Luftnummer (Red-Team-Einwand, siehe Wargame 1 in B52).

## 2. 3-Phase-Anwendung (Pentagon-Verfahren)

### Phase 1 -- Conductor (F160)

Conductor-LLM (Haiku oder Sonnet, nicht Opus) analysiert:

```
Input: Aufgabe A + Kontext K
Output:
  - Sub-Schritte S_1, ..., S_n (DAG, mit Dependencies)
  - Pro Sub-Schritt: empfohlenes Tier (0=Cache, 1=Haiku, 2=Opus)
  - Pro Sub-Schritt: initialer Prompt P_i
  - Aggregations-Strategie (wie S_1...S_n zusammengesetzt wird)
```

**Meta-Prompt fuer Conductor (Template):**
```
Du bist ein Meta-Prompting-Conductor. Analysiere folgende Aufgabe:
[AUFGABE]
Kontext:
[KONTEXT]

Zerlege in unabhaengige Sub-Schritte (max 7). Fuer jeden Sub-Schritt gib an:
- Ziel
- Eingaben
- Ausgabe-Format
- Empfohlenes LLM-Tier (0/1/2, begruende)
- Initial-Prompt (max 200 Woerter)

Liefere auch Aggregations-Strategie (wie Sub-Ergebnisse zusammengesetzt werden).
Output als JSON.
```

### Phase 2 -- OPRO-Loop (F161)

Fuer jeden Sub-Schritt S_i:

```
iterations = 0
current_prompt = P_i
best_score = 0
while iterations < MAX_ITER (Default 3):
    output = LLM(current_prompt)
    score = evaluate(output)  # Self-Check oder externe Metrik
    if score > best_score:
        best_score = score
        best_prompt = current_prompt
    if score >= QUALITY_THRESHOLD (Default 0.8):
        break
    current_prompt = OPRO_improve(current_prompt, output, score)
    iterations += 1

if best_score < MIN_QUALITY (Default 0.5):
    flag_warning("OPRO nicht konvergiert")
    return initial_prompt_result  # Fallback P-B52-4
return best_prompt, output
```

**OPRO-Improve-Meta-Prompt:**
```
Du bist ein Prompt-Optimierer. Aktueller Prompt:
[CURRENT_PROMPT]

Output des Prompts:
[OUTPUT]

Bewertung (0-1): [SCORE]
Probleme: [IDENTIFIED_ISSUES]

Generiere eine verbesserte Version. Max 3 Patches. Output als JSON
mit Feldern: new_prompt, changed_sections, expected_improvement.
```

### Phase 3 -- Compile

Conductor aggregiert:

```
Input: Sub-Ergebnisse R_1, ..., R_n + Aggregations-Strategie
Check:
  - Konsistenz (keine Widersprueche zwischen R_i und R_j)
  - Vollstaendigkeit (alle Sub-Schritte haben Output)
  - Format-Konformitaet (Output-Schema erfuellt)
Output: finaler Output + Meta-Stats
```

**Meta-Stats (Pflicht-Artefakt, P-B52-3):**
```json
{
  "task": "...",
  "sub_steps_count": N,
  "tokens_total": T,
  "tokens_per_tier": {"0": t0, "1": t1, "2": t2},
  "opro_iterations": [i1, i2, ..., iN],
  "quality_before": 0.0,
  "quality_after": 0.85,
  "cost_eur": 0.23,
  "runtime_sec": 47,
  "warnings": ["OPRO S_3 nicht konvergiert"]
}
```

## 3. Limits und Fallback (Cost-Cap P-B52-2 + Fallback P-B52-4)

| Limit | Default | Verhalten bei Verletzung |
|---|---|---|
| MAX_ITER pro Sub-Schritt | 3 | Abbrechen, best_score zurueck |
| MAX_SUB_STEPS | 7 | Re-Conduct mit engerer Zerlegung |
| COST_CAP (EUR) | 2 | Abbrechen + Report |
| RUNTIME_CAP (Sek) | 600 (10 Min) | Abbrechen + Report |
| MIN_QUALITY | 0.5 | Warn-Flag + Fallback zu initial |
| QUALITY_THRESHOLD | 0.8 | Early-Exit wenn erreicht |

**Fallback-Kette:**
1. Wenn OPRO-Loop nicht konvergiert: Initial-Prompt-Resultat zurueck + Warnung.
2. Wenn Cost-Cap erreicht: Letzter bester Stand + Warnung.
3. Wenn Conductor Fehler: Direkter Einzel-Prompt (ohne Meta-Prompting) + Warnung.

## 4. Measurement (Pflicht, P-B52-3)

Jeder Run logged in `~/.claude/skills/meta-prompting/runs.jsonl`:

```json
{"ts":"2026-04-18T14:22:00Z","task_hash":"abc123","tokens_total":15420,"tokens_saved_vs_opus":42000,"cost_eur":0.23,"quality_before":0.55,"quality_after":0.85,"opro_iterations":2,"warnings":[]}
```

**Nach 10 Runs:** Martin-Review via inbox/to-architekt.md. Falls Quality-Lift < 0.1 median: Skill deaktivieren (PROPOSAL bleibt stehen, aber Trigger disabled).

## 5. Anti-Meta-Meta-Regel (P-B52-5)

Der Skill darf:
- Object-Level-Prompts optimieren (Hotel-Agent, SAE-Agent, Research-Query, etc.)
- Eigene Zwischen-Prompts fuer Conductor/OPRO generieren

Der Skill darf NICHT:
- Prompts generieren die selbst Prompting-Regeln erzeugen (Meta-Meta-Level)
- CLAUDE.md, `rules/*.md`, `skills/*/SKILL.md` modifizieren
- Rules ueber Prompting ableiten und persistieren

Warum: `rules/crux-gate-grenzen.md` + `rules/cross-llm-simulation.md` - Meta-Meta-Aussagen max CONDITIONAL. Der Skill wuerde sonst seine eigenen Grenzen ueberschreiten.

## 6. Integration mit anderen Skills

### 6.1 Aufrufbar aus:

- `mk-research` -> fuer Multi-Step Research-Query-Decomposition
- `wargame` -> fuer Red/Blue/Purple-Prompt-Iterationen
- `archon-workflow-create` -> als Baustein in neuen Workflows
- Direkt via `/meta-prompting` oder Trigger-Woerter (siehe §1)

### 6.2 Nutzt:

- `when-to-archon` zur Tier-Klassifikation (Tier 1 Default)
- `meta-learn` fuer Session-Lessons

### 6.3 Nutzt NICHT:

- `dark-factory-create` (B52 ist bewusst KEIN Dark-Factory)
- `knowledge-janitor` (Meta-Prompting != KB-Hygiene)

## 7. K_0-Naehe-Regel (Sonderfall KPM)

**Bei KPM-Anwendungen (Portfolio-Prompts, Trading-Strategien):**
- Human-in-the-Loop ZWINGEND.
- Martin approved jedes OPRO-iterierte Resultat vor Deployment.
- Log in separater Datei `runs-kpm.jsonl` (strenger Audit).

Grund: KPM-Prompts beeinflussen K_0. CRUX-Gate-Grenzen sakrosankt.

## 8. Benutzungs-Beispiele

### 8.1 Hotel-Agent-System-Prompt Optimierung

```
/meta-prompting

Aufgabe: Optimiere den System-Prompt fuer REVENUE-Agent in SAE v8.
Aktueller Prompt: [PROMPT]
Kontext: 600 Agenten, Trinity-Pattern, HIVE-Score, Q_SCALE_INTEGRAL=11.11.
Ziel: +10-15% Accuracy auf MEWS-basierten Preisempfehlungen.

Erwartetes Resultat: optimierter System-Prompt + Meta-Stats.
```

### 8.2 Research-Query-Decomposition

```
/meta-prompting

Aufgabe: Erforsche "wie wirkt Zuckerkonsum auf HbA1c ueber 90 Tage?"
Mit mk-research invoked.
Conductor soll 5-7 Sub-Queries definieren (Meta-Studies, Guidelines,
Mechanismus, Dose-Response, Confounders).
```

### 8.3 Wargame-Prompt-Iteration

```
/meta-prompting

Aufgabe: Verbessere Red-Team-Prompt fuer Blueprint-Wargaming.
Aktueller Prompt faellt zu schnell auf Strohmann-Argumente.
Ziel: ehrlichere Adversarial-Analyse mit klarer Annahmen-Liste.
```

## 9. Testplan (vor Aktivierung)

| Test | Erfolgskriterium |
|---|---|
| T1 Trivial-Prompt Trigger-Check | Skill NICHT getriggert |
| T2 Multi-Step-Prompt | Skill triggert + 3+ Sub-Schritte |
| T3 OPRO-Konvergenz | Score steigt in >= 70% der Runs |
| T4 Cost-Cap | Abbruch bei 2 EUR, Fallback liefert Ergebnis |
| T5 K_0-KPM-Pfad | Human-in-Loop Dialog erscheint |
| T6 Meta-Meta-Schutz | Verweigert Modifikation von rules/ |

Alle Tests: 30-90 Min, dann Martin-Approval.

## 10. Changelog

| Version | Datum | Aenderung |
|---|---|---|
| 0.1.0-PROPOSAL | 2026-04-18 | Initial Proposal nach Wargames B52. |

## 11. Approval-Pfad (leadership.md-PROPOSAL-Pattern)

1. Martin liest Decision Card B52 (`docs/decision-cards/B52-Meta-Prompting-Skill.md`).
2. Martin beantwortet Approval-Fragen (B52 §11).
3. Datei wird umbenannt: `SKILL.md.PROPOSAL` -> `SKILL.md`.
4. Rename-Aktion trigger `~/.claude/skills/meta-prompting/runs.jsonl` Initial-Create.
5. Erste 3 Runs unter Beobachtung.
6. Nach 10 Runs: Status-Update, Version 0.2.0.
7. Nach 4 Wochen + >= 10 positive Runs: Version 1.0.0, CONDITIONAL -> HARDENED.

[CRUX-MK]
