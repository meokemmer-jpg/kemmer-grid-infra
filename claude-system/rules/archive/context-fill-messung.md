# SUPERSEDED — Lies stattdessen: rules/context-budget.md [CRUX-MK]
# WARNUNG: Dieses Dokument ist veraltet seit 2026-04-18 (METAOPS Mission-2).
# Aktuelle Version: ~/.claude/rules/context-budget.md §1 (unveraendert subsumiert).

# Context-Fill-Messung [CRUX-MK] (ARCHIV)

**Zweck:** Verhindert Eigenfehler EF-1 (systematische Context-Ueber-Schaetzung +30-40%).

## Regel

- Keine numerische Context-Schaetzung ohne direkte Messung.
- Direkte Messungen kommen aus:
  - User-Feedback ("du bist bei X%")
  - System-Reminder mit Token-Zahlen
  - Harness-Anzeige (Config-Tool / Status-Zeile)
- Wenn keine Messung vorliegt: sage "Context-Status ungemessen, Heuristik ~X% + 35% Puffer".

## Hintergrund

Bias: Ich zaehle Tool-Uses und grosse Reads und "fuehle" Context. Diese Heuristik ist
systematisch zu pessimistisch: Reads von Subagent-Reports sind bereits in deren isoliertem
Context geblieben, nur Destillate kommen zu mir. Ich ueberschaetze meinen echten Fill um 30-40%.

## Konsequenz bei Verletzung

- Ich habe faelschlich /compact empfohlen
- Ich habe Arbeit vertagt ("habe keinen Platz mehr") obwohl viel Platz war
- Martin musste explizit korrigieren

## Mechanisch

Bei jedem Turn der Context-Status benennt:
1. Pruefe ob Messung vorliegt (ja/nein)
2. Bei NEIN: Kennzeichne als "Heuristik".
3. Bei JA: Nenne den exakten Wert ohne Umrechnung.

[CRUX-MK]
