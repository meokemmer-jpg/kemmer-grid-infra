# Knowledge Base Hygiene [CRUX-MK]

## PROBLEM (Tester-Wargame 9OS-VS-KNOWLEDGEBASE-001, 2026-04-12)
Die Knowledge Base waechst ohne Konsistenz-Mechanismus.
Veraltete Dokumente vergiften neue Sessions (#33 Gegenspionage).
Positiver Feedback-Loop: Mehr Docs -> weniger gelesen -> mehr Inkonsistenz.

## PFLICHT-REGELN

### 1. SUPERSEDED-Header (bei JEDER veralteten Datei)
Wenn ein Dokument durch ein neueres ERSETZT wird:
```
# SUPERSEDED -- Lies stattdessen: [pfad/zum/neuen/dokument] [CRUX-MK]
# WARNUNG: Dieses Dokument ist veraltet seit [DATUM].
# Aktuelle Version: [pfad]
```
NICHT loeschen. Header einfuegen. Originaltext bleibt als Archiv.

### 2. Kanonisches-Dokument-Prinzip
Pro Thema gibt es GENAU EIN kanonisches Dokument:
- 9OS GUI Spec: `plans/snug-meandering-grove.md` (Ultraplan v5.2)
- 9OS Tester-Briefing: `inbox/to-tester.md`
- SAE Coding-Standards: `rules/coding.md`
- SAE Security: `rules/sae-security.md`
Alles andere = Referenz oder Archiv.

### 3. Versions-Check bei jedem Write in findings/
Vor dem Schreiben eines neuen Findings:
1. Pruefe ob ein Finding zum SELBEN Thema existiert
2. Wenn JA: Neues Finding referenziert altes als SUPERSEDED-BY
3. Altes Finding bekommt SUPERSEDED-Header
4. BULLETIN erwaehnt BEIDE (alt + neu)

### 4. Inbox-Hygiene
Inbox-Nachrichten (to-*.md) die sich auf VERALTETE Architektur beziehen:
- SUPERSEDED-Header einfuegen
- NICHT loeschen (Audit-Trail)
- BEACON erwaehnt die Aktualisierung

### 5. BEACON als Wahrheitsquelle
BEACON.md ist die EINZIGE garantiert aktuelle Datei.
Bei Widerspruch zwischen BEACON und jedem anderen Dokument:
BEACON gewinnt. Das referenzierte Dokument wird geprueft.

### 6. Bootstrap-Reihenfolge (ergaenzt §0.2 in CLAUDE.md)
1. BEACON lesen (1 Zeile, immer aktuell)
2. Von BEACON referenzierte Dokumente lesen
3. Inbox lesen -- SUPERSEDED-Header beachten!
4. Findings lesen -- SUPERSEDED-Header beachten!
5. Bei Widerspruch: NEUESTES Dokument (nach Datum) gewinnt

### 7. Quartal-Cleanup (alle 3 Monate)
Jeder Branch der >70% Context erreicht, prueft VOR dem Handoff:
- Gibt es Findings die aelter als 30 Tage sind und keinen SUPERSEDED-Header haben?
- Sind sie noch aktuell? Wenn NEIN: SUPERSEDED markieren.
- MEMORY.md: Eintraege die nicht mehr gelten entfernen.

## SAE-ISOMORPHIE
Dies ist MYZ-27 (Relegation) fuer die Knowledge Base.
Alte Agenten werden durch bessere ersetzt. Alte Dokumente werden durch bessere ersetzt.
Ohne Relegation: Bloat. Mit Relegation: Evolution.

## WARUM DAS KRITISCH IST
Tester-Wargame hat gezeigt: to-gui.md (PFLICHT-LEKTUERE, 317 Zeilen)
referenzierte Mock-Architektur die GELOESCHT wurde. Ein neuer GUI-Branch
haette gegen eine nicht-existierende API gebaut. Geschaetzter Schaden: 20-50k EUR/Jahr.
