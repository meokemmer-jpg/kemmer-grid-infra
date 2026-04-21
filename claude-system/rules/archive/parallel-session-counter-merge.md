# SUPERSEDED — Lies stattdessen: rules/parallel-session.md [CRUX-MK]
# WARNUNG: Dieses Dokument ist veraltet seit 2026-04-18 (METAOPS Mission-2).
# Aktuelle Version: ~/.claude/rules/parallel-session.md §6 Counter-Merge-Protokoll (unveraendert subsumiert).

# Parallel-Session-Counter-Merge [CRUX-MK] (ARCHIV)

**Zweck:** Verhindert Eigenfehler EF-04 (Fragment-/Blueprint-Counter divergieren zwischen Parallel-Sessions).

## Problem

Mehrere Claude-Instanzen arbeiten parallel (Alpha, Beta, Gamma, Opus-Varianten). Jede aktualisiert Counter (Fragment-Map, Blueprints, L-Werte, rho-Schaetzungen). Beim naechsten Session-Bootstrap treffen divergente Zustaende aufeinander.

Beispiel 2026-04-18: BEACON sagt "Fragment-Map 75->77", eigene Detail-Maps haben 75+32+18 = 125 Fragments.

## Regel

1. **Authoritative Quelle bei Zahlen-Konflikt:**
   - Haupt-Datei (z.B. `Subnautica-Fragment-Map.md`) definiert den Basis-Count
   - `<Datei>-Ergaenzung-X.md` Dateien sind ADDITIV (nie SUPERSEDIEREN)
   - BEACON ist 1-Zeilen-Kurzsicht, nie maßgebend bei Detail-Zahlen

2. **Merge-Protokoll bei Bootstrap:**
   - Lies Haupt-Datei
   - Glob alle `<datei>-Ergaenzung-*.md`
   - Summiere additive Counter
   - Bei Konflikt (selber Fragment-Name, unterschiedlicher Inhalt): **neuerer timestamp gewinnt, Konflikt dokumentieren**

3. **Neue Counter-Eintraege:**
   - Nummerierung fortsetzt nach hoechstem vorhandenen Eintrag (aus Haupt + alle Ergaenzungen)
   - Nie neue Nummer vergeben ohne Blick auf Ergaenzungs-Dateien

4. **BEACON-Disziplin:**
   - BEACON darf Counter nennen, aber mit Quellen-Verweis
   - Bei Divergenz zwischen BEACON und Detail-Datei: Detail-Datei gewinnt, BEACON wird im naechsten Turn korrigiert

## Mechanisch

Bei jedem Lese-Bootstrap mit Counter-Interesse:
```
main_file = Subnautica-Fragment-Map.md (oder Aequivalent)
ergaenzungen = glob("<same-stem>-Ergaenzung-*.md")
total_count = sum(count(main_file), count(ergaenzungen))
```

Bei Divergenz zwischen BEACON und berechnetem total_count: in der ersten Antwort des Turns darauf hinweisen, BEACON als naechste Aktion updaten.

## SAE-Isomorphie

Dies ist Myzel-Layer-Event-Reconciliation zwischen Branches. Bei SAE wird das durch Trinity-Voting + Relegation geloest (3 Varianten, bester gewinnt). Bei Claude-Sessions ist Authoritative-Hauptdatei + additive Ergaenzungen der pragmatische Mechanismus.

## Konsequenz bei Verletzung

- Falsche Zahlen in Reports an Martin (z.B. "wir haben 77 Fragments" obwohl 125)
- Doppelte Nummern-Vergabe bei neuen Fragments (F77a vs F77b)
- BEACON-Vertrauensverlust

[CRUX-MK]
