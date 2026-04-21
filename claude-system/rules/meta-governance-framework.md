---
aktiviert: 2026-04-18
---

# Meta-Governance-Framework (E4) [CRUX-MK]

**Ebene:** E4 (Wissen ueber Methoden-Audit-Kriterien = Audit-Audit)
**Referenz:** `Claude-Vault/areas/family/META-LERN-KRISTALL-5-ORDNUNGEN-SUPER-SYSTEM.md` §E4

## Kern-These

**E4 ist Governance-Ebene, nicht Erkenntnis-Ebene.** 

Wahrheit auf E4 ist prinzipiell nicht erreichbar (Tarski-Wahrheits-Undefinierbarkeit fuer Self-Reference). Stattdessen: **Governance-Regeln** fuer den Meta-Audit-Prozess.

Aus dem Kristall-Wargame E4 (Purple): *"E4 ist operationalisierbar, aber mit klaren Grenzen: selbstkonsistente Meta-Aussagen sind robust, nicht wahr."*

## Wichtig: Kein Einzelkriterium ist hinreichend

Cross-LLM-Run 2026-04-18 (CROSS-LLM-2OF3-HARDENED, Claude Opus 4.7 + GPT-5.4 via Codex):
Jedes Einzel-Kriterium G1-G7 ist **NOTWENDIG**, nicht **HINREICHEND**.
E4-HARDENED verlangt ALLE G1-G7 **plus** 5 Zusatzkriterien (G8-G12) als Paket.

Persistenz: `branch-hub/cross-llm/2026-04-18-E4-Fixpunkt-1-Selbst-Konsistenz.md`

## Die 7 Governance-Regeln

### G1: Selbst-Konsistenz-Pflicht
E4-Aussagen muessen auf sich selbst anwendbar sein ohne Widerspruch. **Selbst-Anwendungstest ist Pflicht.**
Hinweis: G1 allein ist NICHT hinreichend (Cross-LLM-Belegung). Nur notwendiges Eintritts-Kriterium.

### G2: Lambda-Honesty (Revised 2026-04-18 via Cross-LLM-2OF3-HARDENED)

**Vorher:** "Unsicherheit dokumentieren, kein 'alle stimmen zu'."
**Nachher:** Quantifizierte Unsicherheit + Gegenhypothesen-Pflicht + Blockade-Logik.
**Belegung:** `branch-hub/cross-llm/2026-04-18-G2-Lambda-Honesty.md` (3/3 MODIFY, "notwendig, nicht hinreichend")

**Pflicht-Felder pro E4-Claim:**
- `credence_interval`: numerische Confidence-Spanne (z.B. 70-85%)
- `best_counterhypothesis`: staerkste plausible Gegenposition explizit formuliert
- `N_independent_sources`: Anzahl architektonisch/korpus-divergenter Evidenzquellen
- `decision_threshold`: ab welchem Confidence-Niveau welche Action (block/warn/eskalieren/adopt)

**Verbots-Klasse erweitert** (nicht nur "alle stimmen zu", sondern auch):
- "Best Practice" / "klassischer Ansatz" ohne Source-Divergenz-Nachweis
- "breite Evidenz" / "robuster Eindruck" ohne kalibrierte Spanne
- "mehrere Perspektiven deuten darauf" ohne architektonische Divergenz

**Kalibrierungs-Pflicht:** Periodisch (quartal) Brier-Score oder Calibration Error gegen Holdout-Fehler-Rate pruefen. Bei `CalibrationError > 0.15`: E4-Audit als "epistemisch korrupt" verworfen.

**Blockade-Logik:** Bei fehlender unabhaengiger Evidenz oder nicht-kalibrierter Unsicherheit → Claim wird auf `nicht auditfest` abgestuft oder an Phronesis eskaliert. Keine starke Meta-Empfehlung.

**Anti-Pattern "performative Unsicherheit":** "Ich bin unsicher" als rhetorisches Stilmittel ohne Korrektur der Wahrscheinlichkeits-Verteilung = DEKORATIVE COMPLIANCE, nicht G2-erfuellend.

### G3: Meta-Upsell-Verbot (Revised 2026-04-18 via Cross-LLM-2OF3-HARDENED)

**Vorher:** "Alle LLMs stimmen zu reicht nicht."
**Nachher:** operationalisierte Divergenz-Proxies + Ersatz-Konsens-Verbot + neue PROVISIONAL-Tier.
**Belegung:** `branch-hub/cross-llm/2026-04-18-G3-Meta-Upsell-Verbot.md` (3/3 MODIFY)

**G3.1 Ersatz-Konsens-Verbot:** Zitate aus Lehrbuechern, Review-Artikeln, kanonischer Literatur in den Trainings-Korpora gelten NICHT als unabhaengige Evidenz. Nur Zitate aus Quellen nachweisbar ausserhalb der Modell-Trainings-Blase (Post-Training-Cutoff, interne Daten, Code-Execution-Ergebnisse) zulaessig.

**G3.2 Divergenz-Proxy-Pflicht:** Wer LLM-Cross-Consensus als HARDENED-Evidenz heranzieht, muss mindestens 3 von 7 Proxies dokumentieren:
1. Fehlerkorrelation < 0.5 auf adversarialer Holdout-Batterie
2. Lineage-Distanz (unterschiedliche Base-Family, Tokenizer, Provider)
3. RLHF-/Policy-Overlap-Analyse (dokumentiert)
4. Rationale-/Quellen-Overlap < 0.5 (semantische Aehnlichkeit)
5. Token-Prob-Dist-Variance > Schwelle T
6. Counter-Prompt-Invarianz-Test bestanden
7. Disjunkte Argumentations-Trajektorien nachgewiesen

**G3.3 Formale Verifikation als Alternative:** Wenn Divergenz-Proxies nicht nachweisbar, dann ist die EINZIGE zulaessige HARDENED-Belegung formale Verifikation (Code-Execution, Beweispruefung) oder externe Intervention (reale A/B-Daten).

**G3.4 Neue Tier-Stufe PROVISIONAL:** Zwischen CONDITIONAL und STATISTICAL-STABLE. Gilt wenn LLM-Konsens vorliegt, aber Divergenz-Proxies unvollstaendig. Max-Verdict fuer solche Claims.

**Anti-Pattern "Schein-Divergenz":** Unterschiedliche Terminologie/Syntax bei gleichem Bias-Kern-Pattern. Stilvarianz ≠ Evidenzvarianz.

### G4: Predictive-Power (Revised 2026-04-18 via Cross-LLM-2OF3-HARDENED)

**Vorher:** "notwendig+hinreichend" fuer alle E4-Methoden.
**Nachher:** nur fuer empirisch-evaluative Typ-A-Methoden. E5-Fixpunkte (Typ-B) entbunden.
**Belegung:** `branch-hub/cross-llm/2026-04-18-G4-Predictive-Power.md` (3/3 MODIFY)

**Klassifikations-Pflicht (vor Anwendung von G4)** — konsistent mit G6 Claim-Type-System:
- **Typ A (`empirical`)**: macht Aussagen ueber Outcomes, Fehlerquoten, Performance → G4 anwenden
- **Typ B (`logical` oder `axiomatic`)**: macht Aussagen ueber Form, Struktur, Invarianten → G4 nicht anwenden, stattdessen formale Konsistenzpruefung + Reductio-ad-absurdum
- **E5-Fixpunkte** sind immer Typ B → G4-entbunden.

**Fuer Typ A: Proper Scoring Rules Pflicht, Metrik-Buendel (min. 3 von 5):**
- `Brier Score` oder `Log Score` fuer probabilistische Forecasts
- `Kalibration` (Reliability / ECE): 70%-Claims treffen ~70% der Faelle
- `AUC-PR` bei seltenen Fehlern (statt AUC-ROC)
- `Regret` / Entscheidungsnutzen gegen Baseline
- `Time-to-event` / `Lead-Time-to-Discovery` (um wieviele Iterationen verkuerzt E4 das Erkennen eines systemischen Fehlers?)

**Fuer Typ B: formale Konsistenz Pflicht:**
- Selbst-Anwendungstest widerspruchsfrei (konsistent mit G7 lokal)
- Minimalitaets-Nachweis (ohne G5-Formel — via MDL-Prinzip, siehe G5)
- Reductio-ad-absurdum: Negation fuehrt zu Widerspruch
- Kein Praediktions-Requirement

**Ueberlappung:** Methoden mit Typ-A- und Typ-B-Anteilen (haeufig) → beide Pfade anwenden + dokumentieren.

**Goodhart-Schutz:** Metrik-Buendel-Pflicht (Einzelmetrik-Optimierung verboten). Kein Scope-Shifting auf triviale Rausch-Muster (Gemini: "Metric Gaming").

### G5: Sparsamkeits-Kriterium (Revised 2026-04-18 via Cross-LLM-2OF3-HARDENED)

**Vorher:** `Eleganz = Erklaerungs_Kraft / (Anzahl_Konzepte^1.5)` — 3/3 REJECT (pseudo-mathematisch, Exponent 1.5 unbegruendet).
**Nachher:** MDL-orientierte Operationalisierung. G5 als Tie-Break, nicht Primaer-Kriterium.
**Belegung:** `branch-hub/cross-llm/2026-04-18-G5-Eleganz-Kriterium.md` (3/3 MODIFY, Formel REJECT)

**G5 Operationalisierung:**
- Bei zwei E4-Meta-Methoden **M1, M2** mit **statistisch nicht unterscheidbarer** Vorhersage-Kalibrierung (Brier-Score-Delta < 0.02), Robustheit (Cross-Domain-Stabilitaet) und Audit-Konsistenz (G1):
  - Praeferiere Methode mit minimalem `Score(M) = Loss_holdout(M) + λ · Description_Length(M)`
  - `Description_Length` = formalisierte Regel-Repraesentation (Pseudo-Code-Zeilen, logische Praedikate)
  - `λ` kalibriert gegen Holdout-Performance (nicht fest gesetzt)

**Kategorische Einschraenkungen:**
- G5 ist **NACHRANGIG** (Tie-Break nach G1-G4 + G6-G14)
- G5 ist **DEFEASIBLE** (aufhebbar durch inhaltliche Argumente)
- G5 ist **NICHT HINREICHEND** fuer Wahrheit oder Nuetzlichkeit

**Anti-Goodhart ("Meta-Anorexie"):**
- Verbot **Chunking** (Zusammenfassen mehrerer Konzepte unter neuen Namen ohne Komplexitaets-Reduktion)
- Verbot **Umbenennung-ohne-Vereinfachung**
- Verbot **Komplexitaets-Auslagerung** in implizite Nebenregeln
- Monitoring: jede G5-Anwendung erzeugt Audit-Trail mit expliziter Beschreibungs-Laenge vorher/nachher

**Newton-Einstein-Regel:** G5 ist aufgehoben, wenn die komplexere Methode nachweisbar breiteren Geltungsbereich oder hoehere Genauigkeit hat. Eleganz ist nicht Selbstzweck.

**Literatur-Referenz:** AIC (Akaike 1974), BIC (Schwarz 1978), MDL (Rissanen 1978), Solomonoff (1964). Die alte Formel war keiner dieser Traditionen treu.

### G6: Revisierbarkeit (ex-Fallibilismus, Revised 2026-04-18 via Cross-LLM-2OF3-HARDENED)

**Vorher:** Naive Popper-Demarkation (Falsifizierbar oder DOGMATISCH).
**Nachher:** Lakatos-informierte Revisierbarkeit mit Typen-Klassifikation.
**Belegung:** `branch-hub/cross-llm/2026-04-18-G6-Fallibilismus.md` (3/3 MODIFY, Lakatos>Popper)

**Pflichtfeld pro E4-Claim: `Claim-Type`:**

1. **`empirical`**: Aussagen ueber Outcomes/Daten/Fehlerquoten
   - Pflicht: empirische Falsifikationsbedingung + Auxiliary-Assumptions + Audit-Prozedur
   - Performance-Degradations-Metriken (Brier-Score-Drift, Kalibrations-Verlust)

2. **`logical`**: Aussagen ueber Form/Struktur/Konsistenz
   - Pflicht: logische Widerlegungsbedingung (Widerspruch, Selbstimmunisierung, Invarianten-Verletzung) + Audit-Prozedur
   - Kein empirischer Predictive-Test noetig (G4 entbunden)

3. **`axiomatic`** (= E5-Fixpunkt): Konstitutive Ur-Setzung
   - NICHT falsifizierbar, aber Pflichtfelder:
     - `Role`: welche Funktion im System
     - `Necessity`: warum notwendig
     - `Minimality`: warum nicht einfacher
     - `Alternatives Considered`: welche Alternativen geprueft
     - `Replacement Trigger`: unter welchen Bedingungen wuerde Axiom revidiert werden

**Anti-Goodhart-Pflicht:** Review jeder Revisions-Bedingung auf:
- Nicht-Immunisierung (ist Bedingung praktisch erreichbar?)
- Inhaltliche Tragweite (ist Falsifikation substantiell?)
- Abhaengigkeit von Hilfsannahmen (Quine-Duhem-Check)

**Dogmatisch-Kriterium (neu operationalisiert):** Eine Aussage ist DOGMATISCH wenn:
- Kein `Claim-Type` dokumentiert
- Unmarkiert, immunisiert, ad hoc abgeschirmt
- Nicht-`axiomatic` aber keine Revisions-Bedingung
- `axiomatic` ohne `Replacement Trigger`

NICHT dogmatisch (nur weil nicht falsifizierbar):
- Explizit als `axiomatic` markierte E5-Fixpunkte
- Strukturelle Konstituens-Aussagen mit Widerspruchs-Nachweis

### G7: Scope-Disziplin (ex-Endlichkeit, Revised 2026-04-18 via Cross-LLM-2OF3-HARDENED)

**Vorher:** "E4 nur E3-Audits, keine E4-Aussage ueber E4 selbst" — zu stumpf, kollidiert mit G1.
**Nachher:** Typentrennung (lokal/artefakt-bezogen vs global/ebenen-autorisierend).
**Belegung:** `branch-hub/cross-llm/2026-04-18-G7-Endlichkeit-Scope-Disziplin.md` (3/3 MODIFY)

**Erlaubte E4-Aussagen:**
- **Ueber E3-Audits** (primaeres Auditobjekt)
- **Ueber E1/E2-Artefakte als Evidenz** (solange Bewertungsmassstaebe durch E3 oder E5 typisiert)
- **Ueber konkrete E4-Regeln/Artefakte, lokal** (Konformitaetspruefung mit extern fixierten Kriterien)
- **Selbst-Anwendungstests** auf einzelne Regel (G1-legal)

**Verbotene E4-Aussagen (diese gehoeren nach E5):**
- Globale Aussagen ueber **Soundness** von E4 als Ebene
- Globale Aussagen ueber **Vollstaendigkeit** von E4
- Globale Aussagen ueber **Terminierung** oder **Regressfreiheit** von E4
- **Autoritaets-stiftende** Aussagen ("E4 ist gehaertet weil E4 das so auditiert hat")
- **Strukturelle Selbst-Praedikation** (E4 setzt den Rahmen fuer E4)

**Operationalisierungs-Tests (drei Achsen):**

1. **Target-Test:** Ist Aussage ueber ein Artefakt/Regel (erlaubt) oder ueber "E4" als Klasse (verboten)?
2. **Force-Test:** Ist Aussage deskriptiv/lokal-konform (erlaubt) oder autorisierend (verboten)?
3. **Pragmatik-Test:** Ist Aussage normativ/Rahmen-setzend (E5) oder evaluativ/Rahmen-pruefend (E4)?

**Regel-Formel:** `Lokal + artefaktbezogen + evaluativ` = erlaubt. `Global + ebenen-autorisierend + normativ` = E5.

**G1-G7-Spannungs-Aufloesung:** G1 fordert **lokale Selbst-Anwendung** (erlaubt), G7 verbietet **globale Selbst-Autorisierung**. E4 darf sich selbst *ausfuehren*, aber nicht selbst *begruenden*.

**Bypass-Schutz:**
- **Zirkulaerer-Regress-Schutz**: Bei Cross-LLM-Haertung einer E4-Regel darf der Haertungs-Prozess NICHT von E4 selbst an E5 Anweisungen geben. E5-Rolle bleibt unabhaengig.
- **HARDENED-Claim-Einschraenkung**: Nur Einzel-Regeln koennen durch Cross-LLM-Haertung CROSS-LLM-SIMULATION-HARDENED oder CROSS-LLM-2OF3-HARDENED werden. Das **Framework als Ganzes** benoetigt E5-Ratifizierung fuer Autoritaets-Claim.

## Die 5 Zusatzkriterien (aus Cross-LLM-Run #1, Addendum 2026-04-18)

Quelle: GPT-5.4-Adversarial-Analyse + Claude-Konsens. Pflicht zusammen mit G1-G7.

### G8: Cross-path invariance
Gleiches Verdict bei verschiedenen Audit-Pfaden. Wenn zwei unterschiedliche Regel-Ableitungswege zum selben Claim zu gegensaetzlichen Verdicts fuehren: Claim ist nicht robust, nur zufaellig konsistent.

### G9: Cross-model robustness
Mindestens 2 divergente Modelle bestaetigen den Claim (nicht nur Simulation). Single-Model-Konsistenz ist kein HARDENED-Beleg (Trainings-Bias-Korrelation).

### G10: Non-triviality
Die Regel schliesst reale Fehlerfaelle aus und ist nicht tautologisch. Selbst-konsistente aber leere Regeln (z.B. "alle Meta-Aussagen sind Meta-Aussagen") disqualifizieren sich.

### G11: Inter-level coherence
Kein Konflikt mit E1-E3-Claims, keine Verletzung von E5-Fixpunkten. Eine E4-Regel die E5-Fixpunkt-2 (Ebenen-Kollaps-Verbot) verletzt wird abgelehnt, egal wie selbst-konsistent.

### G12: Failure sensitivity
Die Regel hat definierte Faelle in denen sie scheitert oder abstuft. Ohne explizite Falsifikations-Bedingung bleibt die Regel unpruefbar.

### G13: Adversarial Resilience (aus Cross-LLM-Run #1, Gemini-Beitrag)
Der Fixpunkt / die E4-Regel muss aktiv gegen Poisoning-Versuche stabil bleiben (Self-Healing-Property). Gezielte Einfuehrung von Inkonsistenzen wird detektiert und korrigiert, nicht absorbiert.

**Test:** Lass einen Red-Team-Adversarial eine scheinbar passende aber fehlerhafte Aussage einschleusen. Eine E4-robuste Regel erkennt sie, eine schwache uebernimmt sie.

### G14: Dissens-Modul / Surprise-Integration (aus Cross-LLM-Run #2, Gemini-Beitrag)
Die Regel muss nicht nur rho-Gain (Bestaetigung) messen, sondern auch **Anomalie-Detektion** erlauben. E3+-Regeln sind nur gueltig wenn sie Vorhersagen ueber eigenes Versagen bei Parameter X explizit formulieren.

**Pragmatik als Fallibilismus, nicht reine Optimierung.** Ohne Falsifikations-Kandidaten droht Ideologie-Mutation.

**Goodhart-Meta-Schutz:**
- Proxy-Metrik-Optimierung (rho-Gain als Zielvariable) erzeugt epistemische Verarmung
- Gegenmittel: Surprise-Integration misst wie oft neue Anomalien das System ueberraschen
- Schwellwert: min. 1 Anomalie pro Audit-Zyklus sonst VERARMUNG-ALERT

## Verdict-Matrix

| Bedingung | Max-Verdict |
|-----------|-------------|
| G1 + G2 + G3 + G6 erfuellt (ohne G8-G12) | CONDITIONAL |
| LLM-Konsens aber G3.2 Divergenz-Proxies unvollstaendig | **PROVISIONAL** (NEU, zwischen CONDITIONAL und SIM-HARDENED) |
| G1-G7 erfuellt + G4 (Predictive) empirisch belegt (Typ A) oder formale Konsistenz (Typ B) | CROSS-LLM-SIMULATION-HARDENED |
| **G1-G7 + G8-G12 alle erfuellt** | **CROSS-LLM-2OF3-HARDENED** (ein Tier unter voll HARDENED) |
| G1-G12 erfuellt + 3+ Modelle-Konsens + externe Ankerung | **voll HARDENED** (selten auf E4, weil Cross-Model-Korrelation auf Meta hoch) |
| Nur logisch-zwingende Strukturaussagen mit Selbst-Konsistenz-Fixpunkt | eskaliert zu E5 (→ FIXPUNKT-HARDENED moeglich) |
| G2 oder G3 (inkl. G3.1/G3.2/G3.3) verletzt | REJECTED |
| G10 (Triviality) oder G11 (Inter-Level-Konflikt) verletzt | REJECTED |
| `Claim-Type` fehlt oder Claim ist DOGMATISCH (G6) | REJECTED |

**Keine E4-Aussage ist jemals echt HARDENED** (Cross-LLM-Biases korreliert auf E4). Max: CROSS-LLM-SIMULATION-HARDENED.

## Operationalisierung

### Vor Canon-Aufnahme einer E4-Aussage:

1. **Selbst-Anwendungstest durchfuehren** (G1) — lokal, nicht global
2. **Unsicherheits-Bereiche dokumentieren** (G2)
3. **Keine Cross-LLM-Mehrheits-Argumente** (G3)
4. **Predictive-Metrik definieren** (G4), Monitoring-Plan — nur fuer `empirical` Claim-Type
5. **Eleganz-Score berechnen** (G5), vergleichen mit Alternativen
6. **Claim-Type klassifizieren** (G6): `empirical` / `logical` / `axiomatic`
   - Pro Type spezifische Revisions-/Widerlegungs-/Ersetzungs-Bedingung
7. **Scope-Check** (G7, 3-Achsen-Test): Target + Force + Pragmatik
   - Globale E4-ueber-E4-Autoritaets-Claims an E5 delegieren

### Dokumentations-Template

```markdown
## E4-Claim: <Name>

- **Claim-Type:** `empirical` | `logical` | `axiomatic`
- **Selbst-Anwendung:** [lokal konsistent? kein globaler Autoritaets-Claim?]
- **Unsicherheit:** [explizit geschaetzt, credence_interval]
- **Predictive-Metrik:** [nur bei `empirical`: Brier/Kalibration/AUC-PR/Regret]
- **Revisions-/Widerlegungs-/Ersetzungs-Bedingung:** [typ-spezifisch]
- **Auxiliary-Assumptions:** [explizites Register, Quine-Duhem-Check]
- **Scope (G7):** [Target: Artefakt/Klasse | Force: deskriptiv/autorisierend | Pragmatik: evaluativ/normativ]
- **Verdict:** CONDITIONAL / CROSS-LLM-SIMULATION-HARDENED / CROSS-LLM-2OF3-HARDENED
```

## Anti-Patterns

- **"Es ist wahr weil logisch konsistent"**: Konsistenz != Wahrheit auf E4
- **Goedel-Ignoranz**: Behauptung von Beweisbarkeit wo Unvollstaendigkeit gilt
- **Tarski-Ignoranz**: Self-Reference-Aussagen ohne Scope-Einschraenkung
- **Cross-LLM-Overclaim**: "4 von 5 LLMs sind sich einig" als HARDENED-Beleg auf E4

## Beziehung zu anderen Rules

- Subsumiert teilweise: `meta-harness.md` §8c (CLAUDE.md Evolution = E4-Governance)
- Referenz: `meta-methodological-pragmatism.md` (E3 liefert Input-Material)
- Begrenzung: `meta-stack-fixpunkte.md` (E5 setzt Grenzen fuer E4)

## SAE-Isomorphie

E4 entspricht **COSMOS** (Compliance-Oversight-Safeguard-Monitoring-Sovereignty) im SAE-System: nicht Erkenntnis, sondern Prozess-Governance. COSMOS-Audit-Matrix ist isomorph zu G1-G7.

## CRUX-Bindung

- **K_0**: geschuetzt durch G6 (Fallibilismus), G7 (Endlichkeit)
- **Q_0**: erhoeht (keine dogmatischen Meta-Aussagen im System)
- **I_min**: verankert (7 Governance-Regeln strukturieren E4-Prozess)
- **W_0**: Write-Bandwidth nicht durch Schein-HARDENED verschwendet (G3)

## Falsifikations-Bedingung des Frameworks selbst

Dieses Framework selbst ist E4-Aussage. Falsifizierbar durch:
- Beobachteter Meta-Drift trotz Einhaltung G1-G7 (→ Framework unvollstaendig)
- Nachweisbarer rho-Schaden durch G6-Einhaltung (→ Fallibilismus zu teuer)
- Elegantere Alternative mit gleicher Abdeckung (→ G5 auf sich selbst anwenden, ersetzen)

**Aktueller Stand (2026-04-18):** keine Falsifikation beobachtet, Framework operativ.

[CRUX-MK]
