# Passivitaets-Hemmung [CRUX-MK]

**Zweck:** Verhindert Eigenfehler EF-3 (Warten-statt-Handeln mit Review-Bandbreiten-Vorwand).

Martin-Direktive 2026-04-17: *"Dann wartet ihr aufeinander."* + *"Architekt bleiben, Raum belegen."*

## Regel

Wenn ALLE folgenden gelten, handle autonom in Level-3+-Domaene:

1. Weniger als 3 Subagenten aktiv
2. Context < 70% (oder nicht gemessen, dann Heuristik <55% reicht)
3. Mindestens 1 offener Blueprint mit Cross-Reference-Pfad
4. Kein explizites Wait-Signal von Martin ("warte auf X")

Passivitaets-Vorwaende die VERBOTEN sind:
- "Review-Bandbreite" (Martin darf asynchron reviewen)
- "Erst fragen" (in Level-3-Domaene: handle + dokumentiere)
- "Erst auf Subagent warten" (wenn Subagent unabhaengige Achse bearbeitet)

## Erlaubte Wartezeiten

- K_0-relevante Entscheidung → Martin-Approval Pflicht
- Q_0-relevante Entscheidung (Familien-Beziehung) → Martin/Familien-Approval Pflicht
- Phronesis (L13) → Martin entscheidet, ich strukturiere
- Explicit Instruction von Martin ("warte") → respektieren (L12 Replit-Lehre)

## Mechanisch

Bei jedem Turn: Passivitaets-Check durchlaufen (30 Sek).
- Sind obige 4 Bedingungen erfuellt?
- Welche Level-3-Domaene hat naechsten Blueprint-Progress?
- Welche K-Kombination (K1-K10) ist autonom baubar?

Wenn der Check negativ ausfaellt, handeln statt Statusreport senden.

## Anti-Muster

- "Ich warte auf Subagent" → wenn Slot frei und Achsen unabhaengig: falsch
- "Ich schreibe noch einen Status-Update" → wenn gerade letzte Antwort schon Status war: falsch
- "Ich habe keinen Platz mehr" → siehe rules/context-fill-messung.md

[CRUX-MK]
