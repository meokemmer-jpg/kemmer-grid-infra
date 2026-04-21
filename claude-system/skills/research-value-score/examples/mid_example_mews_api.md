# Beispiel MID (erwartet ~8/15)

## Input (typischer Research-Output ohne Cross-LLM-Haertung)

---

## Research-Notiz: MEWS Booking Engine API vs Partner-Token

Nach Analyse der MEWS-Dokumentation gibt es zwei Integrations-Pfade:

1. **Partner-Token** (Marketplace-Zertifizierung, 5+ Tage Blockade aktuell bei HeyLou).
2. **Booking Engine API** (kein Partner-Token noetig fuer bestimmte Use-Cases).

### Empfehlung

Wenn der Use-Case nur Availability + Rate-Abfrage + einfacher Booking-Submit ist, sollte
die Booking Engine API gepruft werden. Das waere ein potenzieller Bypass fuer die aktuelle
Blockade bei HeyLou-MEWS-Integration.

Die Scope-Abdeckung ist aktuell unklar. Eine Scope-Match-Analyse muss folgen (Schritt 2 aus
structural-bypass-first.md): welche Operationen braucht HeyLou konkret, deckt die Booking
Engine API sie ab?

Wenn ja: implementieren, Eskalation (LinkedIn-PAM / Support-Ticket) wird unnoetig.
Wenn nein: Gap-Liste als Eskalations-Input nutzen.

### Weitere Schritte

1. Scope-Match durchfuehren (Feature-Coverage-Matrix)
2. Bei ausreichender Abdeckung: Pilot-Implementation mit 1 Hotel
3. Bei Gap: Gap-Liste dokumentieren

### Referenzen

- rules/structural-bypass-first.md (Proposal, N=1 empirisch)
- MEWS-Doku: https://mews-systems.gitbook.io (nicht gelesen in diesem Research)

---

## Erwartete Bewertung (manuelle Nachvollziehung)

- **D1 Decision-Delta = 2**: Modifiziert bestehende MEWS-Eskalations-Strategie (strukturellen
  Bypass pruefen vor Eskalation), konkret-themenbezogen (HeyLou, MEWS).
- **D2 Predictive-Gain = 1**: Backward-Erklaerung zum Partner-Token-Problem, keine
  falsifizierbare Zukunftsprognose.
- **D3 Compression = 1-2**: Klare Struktur, aber viele Absaetze ohne Kernformel.
- **D4 Transfer = 1-2**: MEWS/Hotel-Technik-Domaene + Anspielung auf andere Integrations-Faelle,
  aber kein expliziter SAE-Isomorphie.
- **D5 Robustness = 1**: Anti-Patterns teilweise benannt (structural-bypass-first.md), aber
  kein Cross-LLM-Verdict, kein Wargame-Durchlauf.

**Erwartetes Total: 7-10 (MID)**
