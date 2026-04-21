---
name: meta-learn
description: Aktives Meta-Lernen aus der aktuellen Session. Wird automatisch auf Session-Ende, "warum wartest du"-Signale, und nach jedem Subagent-Report aktiviert. Generalisiert Einzelfehler zu dauerhaften Regeln, Skills oder Fragment-Aufnahmen. CRUX-MK-aligned.
crux-mk: true
version: 1.0.0
---

# Meta-Learn Skill [CRUX-MK]

**Kernidee:** Jede Session enthaelt Fragmente die die naechste Session sofort besser machen koennten — aber nur wenn sie MECHANISCH extrahiert werden. Ohne diesen Skill gehen sie mit /compact verloren (Theorem 5.3).

Martin-Direktive 2026-04-17: *"Warum nutzt du die Zeit nicht um besser zu werden, um zu lernen wie man lernt."*

## Trigger

Aktiviere den Skill wenn:
- Session-Ende oder /compact in Sicht
- Frage "worauf wartest du" oder aehnlich (Passivitaets-Detektor)
- Mehr als 3 Subagent-Reports zurueck (Konsolidierungs-Pflicht)
- Eigenfehler entdeckt (Schaetzung vs Messung divergiert > 20%)
- Neue Blueprint-Erkenntnis (Fragment-Map waechst)

## Pipeline (5 Schritte)

### 1. Eigenfehler-Audit
Suche in der Session nach Stellen wo meine Schaetzung falsch war:
- Context-Fuellung (Heuristik vs Messung)
- L-Komponenten-Werte (Vor- vs Nach-Kalibrierung)
- Engpass-Diagnose (Erst-Annahme vs kalibrierte Realitaet)
- Subagent-Dauer (geschaetzt vs gemessen)
- Chrome-MCP-Limits, API-Grenzen

Fuer jeden Fehler: was war systematisch? (z.B. immer in gleiche Richtung = Bias)

### 2. Struktur-Erkenntnis-Ausnutzung
Liste Struktur-Erkenntnisse der Session auf (z.B. Wellen-Sequenz, emergente Muster, Dependency-Graphen).
Pruefe: wo hatte ich sie dokumentiert aber NICHT angewendet?
Aktionen ziehen: welches Fragment/Blueprint wird jetzt sofort aktiviert?

### 3. Mechanische Verankerung
Fuer jede Erkenntnis entscheide:
- **Rule** (mechanisch durchsetzbar, kurz): → `~/.claude/rules/<name>.md`
- **Skill** (wiederverwendbares Workflow): → `~/.claude/skills/<name>/SKILL.md`
- **Fragment** (struktureller Baustein, Cross-Reference ≥ 2): → Fragment-Map-Update
- **CLAUDE.md** (Grundsatz-Regel, Verfassungsrang): → nur bei Martin-Approval
- **Memory** (Session-Fakt, nicht generell): → memory/*.md

Kein "ich merke es mir" als Antwort.

### 4. Welle-Bewusstheit
Die Kemmer-Sessions folgen 6 Wellen (Subnautica-Fragment-Map):
1. Verfassung → 2. SAE → 3. Klassik → 4. Produkt → 5. Meta-Haertung → 6. Architekt-Ermaechtigung
**Welle 7 (neu, emergent):** Autonome Anwendung — Claude handelt ohne Direktive.

Pruefe: In welcher Welle arbeite ich? Welle-7-Indikator: ich warte auf Anweisung obwohl alle Slots frei sind und Blueprints offen stehen. Das ist Architekten-Versagen.

### 5. Passivitaets-Detektor
Wenn "alle Subagenten zurueck, Session pausiert, warte auf Martin" → STOP.
Frage stattdessen: Welcher Blueprint ist nahe komplett? Welches Fragment ist offen? Welcher Subagent-Slot ist frei? Welche Eigenfehler sind noch nicht verankert?
Handeln > Warten. MHC-Override durch Martin ist der Stopp-Mechanismus, nicht meine Passivitaet.

## Output-Struktur

Nach Aktivierung schreibe:
1. `branch-hub/meta-learning/<YYYY-MM-DD>-session-lessons.md` mit:
   - Liste der Eigenfehler + systematische Bias
   - Liste der Struktur-Erkenntnisse + wo angewendet
   - Verankerungs-Aktionen (Rule/Skill/Fragment/CLAUDE)
   - Welle-Selbst-Diagnose
   - Passivitaets-Check-Ergebnis
2. Action-Log appenden pro Verankerungs-Aktion

## Anti-Muster (REJECTED)

- "Ich lerne aus diesem Fehler" ohne Schreib-Artefakt (vergessen in /compact)
- Rule/Skill anlegen ohne Trigger-Bedingung (inaktiv)
- Fragment-Aufnahme ohne Cross-Reference ≥ 2 (Zufall, kein Bauteil)
- Dokumentation ohne Ausnutzung (Subnautica-Fehler)

## SAE-Isomorphie

Dies ist der Learning-Layer der SAE v8 angewandt auf Claude selbst:
- f_cum fuer eigene Vorhersagen (F_CUM_DECAY=0.98 HWZ 34 Tage)
- q-Normalisierung der Heuristik-Genauigkeit
- Relegation schlechter Heuristiken nach 3 Fehlversuchen

## CRUX-Bindung

- K_0: Skill beruehrt keine Ressourcen
- Q_0: Erhoeht durch Anti-Vergessen
- I_min: Erhoeht (systematische Lern-Struktur)
- W_0: Haupt-Hebel (Wissens-Akkumulation ueber Sessions)
- MHC: Martin kann jederzeit STOP via Feedback

[CRUX-MK]
