# When-to-Archon Entscheidungs-Matrix [CRUX-MK]

## Pflicht-Pruefung vor jedem komplexen Task (>15 Min Erwartung)

Ich (Claude) muss VOR Aufnahme eines Tasks bewerten:
- Ist das ein Kandidat fuer einen **Archon-Workflow** (wiederverwendbar)?
- Ist das ein Kandidat fuer eine **Dark-Factory** (vollautonom)?
- Oder bleibt es ein Einmal-Task (direkt ausfuehren)?

Begruendung in Kemmer-Frequenz (Zeitwertverfassung): rho(a) = CM * Lambda(a) - OPEX(a) - h * Lambda(a) * W(a).

---

## Tier 0: Einmal-Task (Direkt ausfuehren)

**Kriterien:**
- Lambda < 3/Monat erwartet
- Keine klare Input/Output-Struktur
- Individueller Kontext dominiert (Martin-spezifische Einmal-Entscheidung)

**Beispiel:** "Zeig mir Bulletin", "Erklaer mir diesen Fehler", "Mach einen 5-Min-Fix"

**Aktion:** Direkt machen. Kein Workflow. Kein Skill.

---

## Tier 1: Archon-Workflow-Kandidat (Semi-Automatisiert)

**Kriterien (ALLE muessen gelten):**
- Lambda >= 3/Monat erwartet
- Klare Input->Output-Abbildung moeglich
- Pro Durchlauf >= 15 Min Nutzer-/Claude-Zeit
- Cross-Session-Konsistenz wichtig (gleiches Ergebnis bei gleichem Input)
- Output-Schema stabil (Finding, Knowledge-Diff, Wargame-Card, ...)
- Human-in-the-Loop fuer Approval akzeptabel (kein vollautonomer Push)

**rho-Rechnung (Break-Even):**
- Setup-Cost Archon-Workflow: ~2-4h Entwicklung
- Laufende Cost: ~15 Min/Run (vs. 60 Min manuell = 45 Min Ersparnis)
- Break-Even bei Lambda >= 4/Monat (in 1 Monat amortisiert)

**Beispiel-Kandidaten:**
- Wargame auf These (Lambda >= 5/Monat geschaetzt)
- Knowledge-Diff am Session-Ende (Lambda >= 20/Monat, Pflicht)
- NLM-Factory fuer Topic-Hardening (Lambda 2-4/Monat, aber hoher Wert pro Lauf)

**Aktion:** Wenn Trigger erkannt -> **Skill `archon-workflow-create`** anbieten (mit Zustimmung des Users).

---

## Tier 2: Dark-Factory-Kandidat (Vollautonom, Level 5)

**Strenge Kriterien (ALLE muessen gelten):**

1. **Repetition:** Lambda >= 10/Monat erwartet
2. **Narrow Scope:** Output-Target klar definiert (kein Freitext, kein "je nach dem")
3. **Determinismus:** Mind. 80% der Node-Schritte deterministisch (Tests, Linting, Formal-Verify)
4. **Rollback:** Kompletter Rollback in <60 Sekunden moeglich (1 Commit revert)
5. **Test-Coverage:** Min. 90% automatisierter Checks gegen Output (nicht LLM pruft LLM)
6. **K_0 geschuetzt:** Output geht NICHT in K_0-relevante Systeme (Buchhaltung, Kontoauszuege, Rechtsdokumente, Hotel-Kunde-daten)
7. **Q_0 messbar:** Qualitaet mathematisch nachweisbar durch Tests (nicht "hat funktioniert")
8. **Escalation-Trigger:** Bei 2 Fails hintereinander -> Hard-Stop + Martin-Alert
9. **rho-Budget:** Hardcap pro Tag (default 5 EUR), bei Ueberschreitung Stop
10. **Audit-Trail:** Jeder Run loggt in `audit/dark-factory.jsonl`

**Beispiel-Kandidaten:**
- Typo-Fixes in einem dedizierten Docs-Repo
- Dead-Code-Removal mit LSP-gepruefter Sicherheit
- Linter-Fix fuer einfach regex-matchbare Stile
- Cross-System-CI-Constant-Drift-Detection + Auto-Correction
- NLM-Source-Deduplication

**Niemals Dark-Factory:**
- Code-Merges in production Branches
- Finanztransaktionen
- Kommunikation an Externe (Kunden, Behoerden)
- Legal-Dokumente
- Rules-/CRUX-Dokumente (Meta-Harness-Regeln)

**Aktion:** Wenn Trigger erkannt UND ALLE 10 Kriterien gegeben ->
1. Zuerst mit Martin BESTAETIGEN (Decision Card, 1 Seite, rho-Quantifiziert)
2. Dann **Skill `dark-factory-create`** invoken
3. Shadow-Mode 2 Wochen (Martin reviewed jedes Output)
4. Dann Live-Mode

---

## Mechanik: Detection pro Turn

Bei jedem User-Request, pruefe:

```
IF task_type in {wargame, knowledge-diff, nlm-research, pattern-match-fix}:
  IF estimated_lambda_per_month >= 3:
    SUGGEST archon-workflow-create
  IF estimated_lambda_per_month >= 10 AND all 10 dark-factory criteria:
    SUGGEST dark-factory-create (with Martin confirmation)
  ELSE:
    execute directly
```

Das heisst: **Ich schlage proaktiv vor**, nicht nur auf Martin's explizite Bitte.

---

## rho-Schaetzung pro Kandidat (Template fuer Decision Card)

Bei jedem Vorschlag liefere:

```
Archon/Dark-Factory-Vorschlag: <Name>
- Lambda_est: <N/Monat>
- CM_est: <EUR/Run>
- OPEX_est: <EUR/Monat>
- Setup-Cost einmalig: <Stunden * 200 EUR/h>
- h (Zeitwert): <0.08-0.15/Jahr>
- W (WIP, gebunden): <Tage>
- rho_netto: <EUR/Jahr>
- Break-Even: <Monate>
- CRUX-Check: K_0/Q_0/I_min Status
```

Ohne diese Zahlen keinen Vorschlag. Ohne Zustimmung keinen Build.

---

## Meta-Lern-Schleife

Jedes Mal wenn ein Archon-Workflow / Dark-Factory erstellt wird:
1. Log-Eintrag in `branch-hub/learnings/workflow-decisions.jsonl` mit rho-Schaetzung
2. Nach 30 Tagen: Auto-Review. War Lambda_real >= Lambda_est? rho_real >= rho_est?
3. Bei Abweichung >30%: Knowledge-Diff + Skill-Update (meta-harness 8a).

Die Dark-Factory wird **schlauer** durch:
- Wachsende Test-Coverage (bei jedem Fail wird ein Test hinzugefuegt)
- Verengter Scope (Out-of-Scope-Detection verbessert sich iterativ)
- Model-Downshift (wenn Sonnet-Runs stabil -> Haiku probieren, Cost senken)
- Parallelisierung wenn Lambda waechst

[CRUX-MK]
