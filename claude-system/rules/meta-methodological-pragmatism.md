---
aktiviert: 2026-04-18
---

# Meta-Methodological-Pragmatism (E3) [CRUX-MK]

**Ebene:** E3 (Wissen ueber Validierungs-Methoden = Methoden-Audit)
**Referenz:** `Claude-Vault/areas/family/META-LERN-KRISTALL-5-ORDNUNGEN-SUPER-SYSTEM.md` §E3

## Kern-These

**E3-Aussagen sind pragmatisch gueltig (funktioniert), nicht ontologisch wahr.**

Aus dem Kristall-Wargame E3 (Purple-Team): *"E3 ist ein Meta-Methoden-Audit-Framework, nicht eine Einzel-Methode. Seine Gueltigkeit ist nicht 'Aussage-Wahr/Falsch' sondern 'Framework-nuetzlich'. Pragmatismus (James, Peirce, Rorty) ist legitime Erkenntnis-Theorie fuer Handlungs-Systeme."*

## rho-Gain-Messung (Pflicht, Revised 2026-04-18 via Cross-LLM-2OF3-HARDENED)

**Belegung:** `branch-hub/cross-llm/2026-04-18-Mission-2-3-4-Konsolidiert.md` §Mission-3 (3/3 MODIFY, 1.5x als ad-hoc entlarvt)

### Robustheits-Formel (ersetzt naive (post-pre)/Setup)

```
rho_gain_adj = (median(rho_post) - median(rho_pre)) / full_cost
full_cost = setup + training + maintenance + allocated_shared_infra
```

### HARDENED-Promotion-Bedingungen (alle Pflicht)

1. `n_pre >= 5` Sessions UND `n_post >= 5` Sessions (statt N=3)
2. `P(rho_gain_adj > tau_domain,horizon) >= 0.8` (Bayesianisch, nicht Punktschaetzung)
3. Kein negativer Schadens- / Tail-Risk-Trigger
4. Setup-Kosten < 50% des Zeitfensters (Sunk-Cost-Amortisation)

### Gestaffelte Domain-Matrix (ersetzt universelle 1.5x-Schwelle)

| Domain | Schwelle @ 1 Monat | Schwelle @ 3 Monate | Schwelle @ 6 Monate | Konfidenz-Anforderung |
|--------|---------------------|----------------------|---------------------|------------------------|
| **Default / E3** | 2.0x | 1.5x | 1.25x | sigma(rho) < 0.2 |
| **K_0 (Kapital)** | 2.5x | 2.0x | 1.5x | Bayes-Faktor > 10 (Jeffreys "stark") |
| **Code (Fast)** | 1.6x | 1.3x | 1.2x | Trend-Stabilitaet p < 0.05 |
| **Q_0 (Familie)** | — | 1.4x | 1.2x | + L-Gate: keine Verschlechterung Harm-Indikatoren |
| **Exploration** | > 1.0x | 1.2x | — | CONDITIONAL-Status, nie HARDENED |

### Goodhart-Schutz (Anti-Kosten-Shifting)

- `full_cost` muss ALLE Kosten enthalten: Setup + Training + Maintenance + anteilige Shared-Infra
- Verbot "Auslagern auf allgemeines Maintenance" um Nenner zu druecken
- `rho_pre` aus mindestens 5 Vor-Sessions Median (keine Cherry-Picking-Basis)
- Vorab definiertes Messfenster (keine Post-hoc-Anpassung)

### Statistische Begruendung

N=3 Sessions sind **unzureichend** fuer HARDENED-Inferenz. Bei hoher Session-Varianz kann 1.5x-Durchschnitt 40% Wahrscheinlichkeit fuer real < 1.0 haben. Bayes-Faktor 1.5 gilt nach Jeffreys-Skala als "anecdotal" — HARDENED braucht BF > 10.

### Anti-Pattern (zusaetzlich)

- **Pseudo-Praezision** durch Fixe 1.5x ohne Varianz-Modell
- **Quarterly-Bias** — Lagging Indicators (Architektur-Frameworks) brauchen 6+ Monate
- **Ausreisser-Monate** kippen 3-Monats-Inferenz → rolling median statt Einzelwerte

## Zirkularitaets-Audit (Pflicht bei Meta-Meta)

Pro E3-Aussage, vor Canon-Aufnahme, beantworten:

1. **Gilt die Aussage fuer sich selbst?** (Selbst-Anwendungstest)
2. **Wenn ja: fuehrt Selbst-Anwendung zu Widerspruch oder Fixpunkt?**
3. **Wenn Fixpunkt: ist er stabil unter Iteration?**

Nicht-beantwortbare oder widerspruechliche E3-Aussagen werden als CONDITIONAL-mit-Zirkularitaets-Warnung markiert.

## Pragmatismus-Rahmen (Kurz-Referenz)

- **William James** (1907): "Wahrheit ist, was funktioniert" — Handlungs-Ertrag als Wahrheitskriterium
- **C.S. Peirce** (1878): Pragmatische Maxime — Bedeutung einer Aussage = praktische Konsequenzen
- **Richard Rorty** (1979): Anti-Repraesentationismus — Wissen nicht als Spiegel der Realitaet, sondern als Handlungs-Werkzeug

## Operationalisierung

**Vor Aufnahme einer E3-Aussage in Canon:**

1. Quantifiziere erwarteten rho-Gain (Hypothese)
2. Definiere Messgroessen (Zeit / Fehler / Kontext-Effizienz)
3. Shadow-Mode fuer 3 Sessions (ohne Canon-Status)
4. Nach 3 Sessions: Gain-Messung gegen Hypothese
5. Wenn Gain >= 1.5x erwartet: HARDENED-pragmatisch
6. Wenn Gain < 1.0x: Aussage wird **archiviert** (kein Canon)
7. Wenn Gain 1.0-1.5x: Iteration 2 mit verfeinerter Hypothese

## Anti-Patterns

- **Ontologische Wahrheits-Behauptung auf E3**: "Das ist so, weil Logik das verlangt" — auf E3 nicht erlaubt, nur auf E5-Fixpunkten
- **Nicht-gemessene Claims**: "funktioniert in Praxis" ohne 3-Messungs-Beleg
- **Zirkularitaets-Ignoranz**: Meta-Aussage nicht auf Selbst-Anwendung getestet
- **Meta-Upsell**: E3-Aussage wird auf E4-Niveau gehoben ohne zusaetzlichen Pragmatismus-Test

## Beziehung zu anderen Rules

- Input von: `meta-validation-portfolio.md` (E2, liefert Methoden-Matrix)
- Eskaliert zu: `meta-governance-framework.md` (E4, wenn Audit-Audit noetig)
- Beschraenkt durch: `meta-stack-fixpunkte.md` (E5, Fixpunkt-3 "pragmatisch > ontologisch")

## SAE-Isomorphie

**Shadow-Mode-Periode** entspricht SAE Phase-0 (Learning ohne Governance-Impact). 
**rho-Gain-Messung** entspricht `core/crux.py::validate_rho_action` — nicht-gehaertete Methoden laufen im Shadow, gehaertete im Production-Pfad.

## CRUX-Bindung

- **K_0**: geschuetzt (keine Meta-Methoden-Empfehlungen ohne gemessenen Gain)
- **Q_0**: verbessert (Pragmatismus stoppt Meta-Over-Engineering)
- **W_0**: effizienter Write (nur bewiesen-nuetzliche E3-Claims werden Canon)

## Falsifikations-Bedingung

Wenn eine E3-Aussage Canon wird, aber nach 6 Monaten rho_gain < 1.0x: **SUPERSEDED-Header**, Archiv, kein Revert.

[CRUX-MK]
