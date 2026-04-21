---
name: research-value-score
description: "Scored Research-Output auf 5-Dim-rho-Skala (Decision-Delta/Predictive-Gain/Compression/Transfer/Robustness). Adressiert Welle-12 Gray-Killer. Triggers 'rho score', 'value score', 'gray-killer check', automatisch nach Subagent-Reports und DF-Runs."
version: 0.1.0
status: SKELETON
meta-ebene: E3
crux-mk: true
aktiviert: 2026-04-20
---

# Research-Value-Score [CRUX-MK]

## Zweck

Adressiert den **Welle-12 Gray-Killer**: *"Tokens sind Kosten, nicht Nutzen."*

Bisherige Metriken (Token-Output, Anzahl Subagent-Reports, Anzahl Knowledge-Diffs) messen **Aufwand**, nicht **Entscheidungs-Wert**. Goodhart-Falle: Dark-Factories und Cascade-Subagenten optimieren auf Messbares (Token-Volumen) statt auf rho-Beitrag (Decision-Delta).

Dieser Skill trennt **Token-Aufwand** von **Research-Wert** via 5-Dimensionen-Scoring. Jede Dimension 0-3 Punkte, Summe 0-15, Zonen-Klassifikation LOW/MID/HIGH.

**Nicht-Ziele:**
- Kein Ersatz fuer Cross-LLM-Haertung (E3/E4-Verdicts).
- Keine automatische Promotion (Scorer ist Empfehlung, nicht Entscheidung).
- Keine Qualitaets-Messung isolierter Token-Stuecke (Scorer arbeitet auf Research-Output-Ebene, nicht Satz-Ebene).

## Wann aktivieren

Automatisch:
- **Nach jedem Subagent-Report** (ueber DF-10 Post-Run-Hook, Skill `parallel-subagent-dispatch` als Quality-Gate).
- **Nach jedem DF-Run** (DF-06, DF-07, DF-08, DF-10) als Post-Processing.
- **Vor Rule-Promotion** (wenn Skill/Rule/Decision-Card aus Research entsteht).

Manuell:
- "rho score this finding"
- "value score WELLE-12-*"
- "gray-killer check"
- Bei Zweifel ob Research-Output Token-Inflation oder Substanz war.

## Input-Vertrag

```python
score_research_output(
    output_text: str,          # Voller Research-Output (Finding, Knowledge-Diff, Subagent-Report)
    thema: str,                # Kemmer-Thema (z.B. "KPM-Sizing", "DF-06-Optimization", "Cape-Coral")
    kemmer_kontext: dict | None = None,  # Optional: {decision_pending: [...], invariants: [...], domain: ...}
) -> ResearchValueScore
```

Alternativ CLI:
```bash
python scorer.py <file_path> <thema>
```

## Output-Vertrag

```json
{
  "decision_delta": 2,
  "predictive_gain": 1,
  "compression": 3,
  "transfer": 2,
  "robustness": 2,
  "total": 10,
  "zone": "MID",
  "justifications": {
    "decision_delta": "Modifiziert KPM-Kelly-Fraction von 0.5 auf 0.25-0.40 kontextadaptiv.",
    "predictive_gain": "Backward-Erklaerung Half-Kelly-Lehrbuch, keine neue Prognose.",
    "compression": "Formel + Drawdown-Caps + Tabelle verdichten 50+ Seiten Literatur.",
    "transfer": "Drawdown-Governance anwendbar auf Trading UND Hotel-RMS.",
    "robustness": "2/2 Cross-LLM MODIFY-radikal, haelt Adversarial-Test."
  },
  "timestamp": "2026-04-20T...",
  "thema": "...",
  "output_length_chars": 12345
}
```

## 5 Dimensionen (Mess-Leitlinien)

### D1: Decision-Delta (0-3)

**Frage:** Aendert dieser Output eine konkrete Kemmer-Entscheidung?

- **0** = keine Entscheidungs-Relevanz erkennbar (reine Beschreibung / Doku / historischer Bericht)
- **1** = bestaetigt bestehende Entscheidung (liefert zusaetzliche Evidenz fuer bekannten Pfad)
- **2** = modifiziert bestehende Entscheidung (neue Parameter, Timing, Scope)
- **3** = zwingt Entscheidungs-Umkehr oder neue Entscheidungs-Klasse

**Heuristik-Signale (im Code):**
- Enthaelt Decision-Card-Format? (Pro/Contra, rho-Rechnung, Go/No-Go)
- Enthaelt konkrete Parameter-Werte (Zahlen, Thresholds, Timings)?
- Benennt konkrete Kemmer-Themen (Cape-Coral, KPM, HeyLou, 9dots)?
- Enthaelt "SUPERSEDED", "REPLACE", "MODIFY" fuer bestehenden Pfad?

### D2: Predictive-Gain (0-3)

**Frage:** Erlaubt der Output bessere Vorhersagen ueber K_0, Q_0, Systemdynamik?

- **0** = keine Prognose-Staerkung (Beschreibung des Bestehenden)
- **1** = bessere Backward-Erklaerung existierender Phaenomene
- **2** = falsifizierbare Vorhersage ueber konkrete Zukunftssituation
- **3** = Vorhersage mit definierter Mess-Prozedur + Falsifikations-Bedingung

**Heuristik-Signale:**
- Enthaelt "wenn X dann Y"-Klauseln mit messbaren Bedingungen?
- Enthaelt Falsifikations-Bedingung explizit?
- Enthaelt Zeitfenster fuer Messung ("nach 4 Wochen", "bei Lambda > 10")?
- Unterscheidet er zwischen retrospektiver Erklaerung und prospektiver Prognose?

### D3: Compression (0-3)

**Frage:** Wird komplexes Terrain auf wenige Kern-Klauseln verdichtet?

- **0** = aufgeblaht, hoher Token-Count ohne Verdichtung (Prosa ohne Kernsatz)
- **1** = moderate Verdichtung (klare Struktur, aber viele redundante Absaetze)
- **2** = dichter Kern + klare Abgrenzung (Kernsatz/Formel + Scope-Begrenzung)
- **3** = extrem dichter Satz/Formel der komplexes Terrain zusammenfasst

**Heuristik-Signale:**
- Verhaeltnis "Kernsatz : Prosa" (hoch = besser)
- Enthaelt einzelne Formel oder strukturierte Tabelle die Kern ersetzt?
- Laenge des Outputs im Vergleich zur Komplexitaet des Themas (kurz + Kernaussage = gut)
- Vermeidet Filler-Phrases ("es ist wichtig zu beachten", "in diesem Zusammenhang")

### D4: Transfer (0-3)

**Frage:** Ist Insight jenseits des aktuellen Themas anwendbar?

- **0** = nur fuer aktuelles Micro-Thema (stark kontextgebunden)
- **1** = anwendbar auf verwandte Themen derselben Kategorie (z.B. KPM-Trading → KPM-Risiko)
- **2** = anwendbar auf andere Kategorien (z.B. Hotel → Trading, SAE → Familien-System)
- **3** = strukturelle Invariante, anwendbar auf Meta-Ebene (Prinzip, nicht Rezept)

**Heuristik-Signale:**
- Enthaelt "SAE-Isomorphie" oder andere explizite Uebertragung?
- Nennt mehrere Domaenen in denen Pattern gilt?
- Formuliert auf abstrakter Ebene (Invariante, Regel, Prinzip) statt konkret (Parameter, Zahl)?
- Verweist auf bestehende Muster (Trinity-Pattern, MYZ-*, Hamilton)?

### D5: Robustness (0-3)

**Frage:** Haelt der Output gegen adversariale Perturbation?

- **0** = kippt bei Cross-LLM-Challenge sofort (keine Verteidigung)
- **1** = haelt einfache Gegenfragen (1-Level-Adversarial)
- **2** = haelt adversariale Perturbation mit Stresstest (mehrere Angriffs-Vektoren ausgehalten)
- **3** = konvergent-stabil ueber 3+ Modell-Familien + Szenario-Shift

**Heuristik-Signale:**
- Enthaelt Cross-LLM-Verdict (CONDITIONAL/HARDENED/CROSS-LLM-2OF3)?
- Benennt Anti-Patterns / Falsifikations-Bedingungen?
- Wurde durch Wargame (Red/Blue/Purple/Gray) getestet?
- Enthaelt "Belegung durch"-Verweise auf Cross-LLM-Files?

## Zone-Klassifikation

```
Total = D1 + D2 + D3 + D4 + D5  (Range: 0-15)

0-5   = LOW    -> Token-Inflation-Verdacht, Review-Pflicht vor Canon-Aufnahme
6-10  = MID    -> akzeptabel, normal weiter
11-15 = HIGH   -> substanziell, Promotion-Kandidat (Rule, Skill, Decision-Card)
```

**LOW-Konsequenz:**
- Eintrag in `branch-hub/audit/low-value-research-log.jsonl`
- Bei Subagent-Output: dispatching Skill kalibriert Prompt-Template (weniger Tokens zulassen)
- Bei DF-Run: DF-Frequency-Review (ggf. halbieren via dark-factory-evolve)
- Keine automatische Loeschung (Audit-Trail bleibt, siehe kb-hygiene.md)

**HIGH-Konsequenz:**
- Kandidat fuer Promotion zu Rule / Skill / Canon-Artefakt
- Kein Auto-Promote: Entscheidung bleibt bei Claude + Martin (Phronesis-L13)
- Eintrag in `branch-hub/audit/high-value-research-log.jsonl` fuer Pattern-Analyse

## Integration

### 1. DF-10 Post-Run-Hook

`token-intelligence` (DF-10) ruft nach jedem Run den Scorer auf allen produzierten Artefakten:

```python
# in DF-10 Post-Run-Logic (Pseudocode)
from research_value_score.scorer import score_from_file
for artifact in run_output_files:
    score = score_from_file(artifact, thema=run_thema)
    df10_metrics.log_score(artifact, score)
```

Resultat geht in `~/.claude/data/research-value-scores.jsonl` fuer Weekly-Learner.

### 2. Subagent-Wrapup (parallel-subagent-dispatch Skill)

Skill `parallel-subagent-dispatch` ruft Scorer als Quality-Gate nach Subagent-Report:

```python
# Pseudocode-Integration
score = score_research_output(subagent_report, thema, kemmer_kontext)
if score.zone == "LOW":
    warn_dispatcher("Subagent-Output LOW-Score, Prompt-Template kalibrieren")
if score.zone == "HIGH":
    suggest_promotion("Kandidat fuer Rule/Skill/Canon")
```

### 3. Manual-Invocation

Via Skill-Tool:
```
Skill research-value-score "Scored G:/Meine Ablage/Claude-Vault/areas/family/WELLE-12-INVARIANTS.md mit thema='Welle-12'"
```

Oder CLI direkt:
```bash
cd C:/Users/marti/.claude/skills/research-value-score
python scorer.py "G:/Meine Ablage/Claude-Vault/areas/family/WELLE-12-USE-CASE-WARGAME-40X-HEBEL.md" "Welle-12"
```

## Falsifikations-Bedingung

Dieser Scorer selbst ist E3-Claim. Falsifiziert wenn:

- Ueber 30 Samples: Scorer-Verdict korreliert < 0.4 mit Martin-Phronesis-Verdict (Scorer danebenliegt)
- Scorer-Scores LOW fuer Outputs die spaeter zu rho-positiven Rules/Skills promoviert werden (False-Negative > 20%)
- Scorer-Scores HIGH fuer Outputs die nie integriert werden (False-Positive > 30%)
- Token-Count-Bias: Scorer gibt systematisch hoehere Scores fuer laengere Outputs (r > 0.5 Token-Count vs Total-Score)

**Revisions-Trigger:** Nach 30 Tagen Shadow-Mode Review. v0.2.0 adressiert Kalibrierungs-Ergebnisse.

## Anti-Patterns

- **Self-Serving-Scoring:** Wer den Output erzeugt hat, scored ihn selbst hoch → bias. Mitigation: Scorer laeuft getrennt vom Producer (nicht im selben Subagent).
- **Inflation-Bias:** Scorer gibt 2-3 statt 0-1, weil "schlechter Output" unhoeflich wirkt → Kalibration nur gegen objektive Heuristik-Signale, keine LLM-based-Self-Rating.
- **Tautologische Criteria:** "Decision-Delta = 3 weil wichtig" → jede Dim hat konkrete Heuristik-Signale, keine rein semantische Einschaetzung.
- **Token-Count-Korrelation:** Scorer belohnt Laenge → Heuristiken sind Signal-basiert, nicht Laenge-basiert. Compression-Dim bestraft sogar Laenge ohne Kern.
- **Scorer-Gaming:** Output wird so formatiert dass er Heuristiken triggert ohne Substanz → adversarial-test in v0.2.0.

## SAE-Isomorphie

- **Trinity-Pattern auf Bewertungs-Ebene:** 3 orthogonale Dimensionen (D1-Entscheidung, D2-Prognose, D3-Struktur) + 2 orthogonale Validierungs-Dimensionen (D4-Transfer, D5-Robustness) = 5-Dim analog zu Conservative/Aggressive/Contrarian im SAE-Slot.
- **q-Normalisierung:** Jede Dim [0-3] analog zu q ∈ [-2, +2] in SAE-Governance.
- **Goodhart-Schutz via Metrik-Buendel:** Keine Einzelmetrik-Optimierung (5 Dims verhindern 1-Achsen-Gaming) analog zu `meta-governance-framework.md` G4.

## CRUX-Bindung

- **K_0:** indirekt geschuetzt (LOW-Outputs in K_0-relevanten Themen bekommen Review-Pflicht)
- **Q_0:** direkt erhoeht (Token-Inflation wird detektiert, Qualitaet der Canon-Basis bleibt)
- **I_min:** erhoeht (strukturierte 5-Dim-Bewertung statt "fuehlt sich wertvoll an")
- **W_0:** Write-Bandwidth priorisiert HIGH-Outputs (Promotion-Kandidaten) vor LOW-Outputs (Token-Inflation)
- **rho-Gain:** geschaetzt +20-80k EUR/J durch vermiedene Token-Inflation-Canon-Aufnahme bei Lambda > 10 Research-Outputs/Monat

## Version-Historie

- **v0.1.0 (2026-04-20):** SKELETON mit Heuristik-basierter Scoring. Adressiert Welle-12 Gray-Killer. Pending Kalibrierung.

## Pending fuer v0.2.0 (nach Martin-Approval)

- Kalibrierung gegen 30 Sample-Outputs mit Martin-Phronesis-Ground-Truth
- Adversarial-Test: gezielt formatierte Outputs die Heuristiken triggern ohne Substanz
- Cross-LLM-Integration: zweites Modell (Codex / Gemini) scored parallel, Divergenz-Alert bei > 3 Punkte Diff
- Token-Count-Bias-Check: automatische Warnung wenn Total-Score-zu-Laenge-Korrelation > 0.5
- DF-10 Shadow-Mode-Integration (Scorer loggt ohne Enforcement)

[CRUX-MK]
