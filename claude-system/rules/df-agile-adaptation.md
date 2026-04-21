# Dark-Factory Agile Adaptation [CRUX-MK]

**Aktiviert:** 2026-04-18 durch Martin-Direktive "Aufraeumen wöchentlich + agil nach Notwendigkeit anpassen"

## Prinzip

Dark-Factories duerfen/sollen sich selbst an die beobachtete Drift-Rate anpassen.
Starrer Cron-Schedule ist suboptimal bei variablem Workload.

## Regel 1: Drift-basierte Frequenz-Anpassung

Jede DF hat eine gemessene **Primaer-Metrik** (z.B. DF-04: duplicates_deleted/run).

Anpassungs-Logik (monatlich via `dark-factory-evolve`):

```
if primary_metric_avg < low_threshold and errors == 0:
    → Frequenz halbieren (taeglich -> 2-taegig, 2-taegig -> woechentlich)
    → spart OPEX
elif primary_metric_avg > high_threshold or errors > 0:
    → Frequenz verdoppeln (woechentlich -> 2-taegig, 2-taegig -> taeglich)
    → schuetzt Q_0
else:
    → bleibt
```

Pro DF definiert:
- `low_threshold` (unter dem: Verkleinerung macht Sinn)
- `high_threshold` (ueber dem: Vergroesserung noetig)
- `stability_window` (min. 4 Wochen Beobachtung vor Aenderung)

## Regel 2: Deputy-Pattern bei Martin-Ausfall

Bei Martin-Ausfall > 4 Wochen (kein Approval moeglich):
- Niedrig-Risiko-DFs (DF-04 Drive-Sync) laufen autonom weiter
- Hoch-Risiko-DFs (K_0-nah, Q_0-nah) pausieren mit STOP.flag
- Deputy-Instanz (sekundaere Claude-Session) uebernimmt Monitoring

## Regel 3: Kill-Switch-Latenz

Jede DF hat Kill-Switch (STOP.flag in audit/). 
Bei 2 consecutive fails: automatische Pause + Martin-Alert.
Bei 5 consecutive fails: harte Deaktivierung + Decision-Card-Pflicht.

## Regel 4: Evolve-Review Cadence

- **Monatlich**: `dark-factory-evolve` auf alle aktiven DFs
- **Quartal**: Reality-Check mit Cross-LLM (Claude + GPT + Grok) ob DF-Set noch optimal
- **Halbjaehrlich**: Full-Retro mit Martin: welche DFs aktivieren, welche pausieren, welche neu

## Regel 5: Transparenz-Pflicht

Jede automatische Frequenz-Aenderung:
1. BEACON-Eintrag mit Begruendung
2. Decision-Card Update in `docs/decision-cards/DF-XX-Frequency-History.md`
3. Rollback-Moeglichkeit fuer 30 Tage

## SAE-Isomorphie

Dies ist **MYZ-27 (Relegation)** fuer DFs: underperformende DFs werden relegiert 
(reduziert), hochperformende befoerdert (Frequenz erhoeht). Trinity-Pattern: 
Conservative (keine Aenderung), Aggressive (Verdopplung), Contrarian 
(Halbierung) — Pick via Evolve-Logik.

## CRUX-Bindung

- K_0: Hoch-Risiko-DFs pausieren bei Martin-Ausfall (Pattern Deputy §2)
- Q_0: Drift-Rate steuert Qualitaets-Erhalt (§1)
- I_min: DF-Set bleibt konsistent durch Evolve-Cadence (§4)
- W_0: OPEX wird durch agile Anpassung minimiert (§1)

[CRUX-MK]
