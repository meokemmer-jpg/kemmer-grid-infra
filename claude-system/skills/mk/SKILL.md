---
name: MK Factory v9
description: Lernen, Pflegen, Anlegen via NotebookLM. 3 Modi. Kompakt und ausfuehrbar.
version: 9.0.1
trigger: /mk
requires: [chrome-mcp OR notebooklm-py]
crux-mk: true
previous: v9.0.0 (umbenannt von /nlm zu /mk)
---

# /mk -- MK Factory v9 [CRUX-MK]

3 Modi: `/mk lernen {thema}` | `/mk pflegen` | `/mk anlegen`

---

## /mk lernen {thema}

Nutze NotebookLM als Wissensbasis. Lerne, haerte durch Wargame, speichere.

**Schritt 1: Notebook waehlen**
- Pruefe `branch-hub/tool-registry.json` → welche Notebooks existieren
- Waehle das passende Notebook fuer {thema}
- Kein passendes? Erstelle neues in NotebookLM

**Schritt 2: NLM zuerst fragen**
- Chrome MCP → notebooklm.google.com → Notebook oeffnen
- Chat: "{thema}" -- NLM antwortet aus bestehenden Quellen
- Antwort LESEN. Reicht sie? → Springe zu Schritt 6
- Wenn nicht: weiter zu Schritt 3

**Schritt 3: Research**
- WebSearch + WebFetch fuer aktuelle Daten
- Optional: Andere LLMs (Grok, Gemini, Perplexity) fuer Cross-Validation
- Quellen sammeln, strukturieren, auf max 3000 Zeichen kondensieren

**Schritt 4: /wargame auf das Gelernte (PFLICHT)**
- Nutze `/wargame` Skill auf das neue Wissen:
  - RED: Was ist falsch, uebertrieben, veraltet?
  - BLUE: Was haelt, was ist die Verteidigung?
  - PURPLE: Was ist die gehaertete Version?
- Tier 1 (Quick) reicht fuer die meisten Themen (30 Min)
- Nur bei CM > 15K: Tier 2+ (Multi-LLM)
- Verdict: HARDENED → weiter. CONDITIONAL → Patches einarbeiten, nochmal. REJECTED → verwerfen.

**Schritt 5: Gehaertetes Wissen als Datei auf Google Drive speichern**
- Schreibe das gehaertete Ergebnis als .md Datei:
  - `G:/Meine Ablage/Claude-Knowledge-System/nlm-library/learnings/{thema}.md`
- NUR GEHAERTETES Wissen speichern. Nie ungepruefte Research.

**Schritt 6: In NotebookLM als Drive-Quelle verlinken**
- Chrome MCP → Notebook oeffnen → "Quellen hinzufuegen" → "Drive"
- "Meine Ablage" → "Claude-Knowledge-System" → "nlm-library" → "learnings" → Datei waehlen
- HINWEIS: NLM findet nur Docs/PDF/TXT ueber Drive-Picker. Wenn .md nicht gefunden:
  Fallback auf "Kopierter Text" mit JavaScript-Injection (bewaehrte Methode)

**Schritt 7: VERIFIZIEREN (5-Punkte-Chat-Check, PFLICHT)**
- Im NLM-Chat 5 Fragen stellen die NUR aus der neuen Quelle beantwortbar sind:
  1. Eine Faktenfrage ("Was ist der rho-Wert von X?")
  2. Eine Zusammenfassungsfrage ("Fasse die Kernaussage zusammen")
  3. Eine Verknuepfungsfrage ("Wie haengt X mit Y zusammen?" -- Y aus anderer Quelle)
  4. Eine Kritikfrage ("Was ist die groesste Schwaeche von X?")
  5. Eine Anwendungsfrage ("Wie wuerde man X auf Szenario Z anwenden?")
- Wenn NLM alle 5 korrekt beantwortet mit Quellenverweisen → Quelle ist eingebunden.
- Wenn NLM die Quelle NICHT kennt → Quelle wurde nicht korrekt verlinkt. Nochmal pruefen.

**Schritt 8: Speichern + Verankern**
- Finding-Library (JSON append):
  `{"id":"THEMA-001","status":"HARDENED","content":"...","rho":"...","nlm_verified":true}`
- Memory-Datei wenn langfristig relevant
- BEACON aktualisieren

---

## /mk pflegen

Notebooks pflegen. Pending Findings hochladen. Health pruefen.

**Schritt 1: Pending Findings identifizieren**
- Lies `branch-hub/findings/` → welche Dateien sind neuer als letzter NLM-Upload?
- Lies Finding-Library → HARDENED Findings ohne NLM-Eintrag?

**Schritt 2: Pro Finding → richtiges Notebook → hochladen**
- Nutze Schritt 4 aus `/mk lernen` (JavaScript-Injection)
- Max 3 Notebooks pro Finding (nicht ALLE -- fokussiert bleiben)

**Schritt 3: Health-Check melden**
- Pro Notebook: Quellenzahl, letzte Aktualisierung
- Warnung wenn > 50 Quellen (NLM-Qualitaet sinkt)
- Warnung wenn letzte Quelle > 30 Tage alt
- 00_MASTER_CONTROL_TOWER: 600-Quellen-Limit bekannt, NICHT mehr hinzufuegen

---

## /mk anlegen

Neues Geraet oder neuer Branch: NLM-Zugang einrichten.

**Schritt 1: Zugang pruefen**
- Chrome MCP verfuegbar? → notebooklm.google.com oeffnen
- Login ok? Notebooks sichtbar?

**Schritt 2: Inventory vs. Soll**
- Lies `memory/reference_notebooklm_notebooks.md` → SOLL-Liste
- Zaehle tatsaechliche Notebooks → IST
- Zeige Diff: "X Notebooks fehlen / Y sind neu"

**Schritt 3: Auffuellen (wenn noetig)**
- `nlm-library/learnings/` enthaelt Klartext-Backups
- Prioritaet: SAE_KEYSTONE → WARGAMES → Claude-Code-Unpacked → Rest
- Nutze Schritt 4 aus `/mk lernen` fuer Upload

---

## Notebook-Referenz (Kurzliste)

| Notebook | Quellen | Primaer fuer |
|----------|---------|-------------|
| SAE_KEYSTONE_HIVE_SUPERIOR_v2 | 19 | SAE-Architektur, Wargames, Findings |
| WARGAMES_MULTIAGENT_LLM | 28 | Wargame-Ergebnisse, Multi-LLM |
| COWORK_MULTI_LLM_ORCHESTRATION | 16 | Orchestrierung, Learnings |
| Claude-Code-Unpacked-Master | 7 | Claude Code Skills, Architektur |
| OpenBrain | 14 | CLI Skill Factory, Research |
| WISSEN-1-Bibliothek-Wargame-930 | 11 | 930 Buecher, Isomorphien |
| 00_MASTER_CONTROL_TOWER | 600 | VOLL -- nicht mehr beschreiben! |

---

## PFLICHT bei JEDEM Modus: Praesentation erstellen lassen

Nach JEDEM `/mk lernen`, `/mk pflegen` und `/mk anlegen`:
NotebookLM "Praesentation" im Studio-Panel klicken mit folgendem Prompt:

```
NotebookLM-Prompt (Max Density)
Rolle: Lead Enterprise System Architect.
Zielgruppe: Hochrangige IT-Experten, Systemarchitekten, Ingenieure (Tiefstes technisches Niveau).

WICHTIGSTE REGELN ZUR STRUKTUR & LIMITS:

Erstelle ein exaktes Slide-Deck-Skript mit genau 30 Folien (Slide 1 bis Slide 30).

Teile die Praesentation strikt in die 5 Themenbloecke auf (1. Evolution, 2. Durchbrueche, 3. Zielbild, 4. Architektur, 5. Knackpunkte).

ZWINGENDE COCKPIT-REGEL: Die erste Folie jedes Blocks MUSS ein Daten-Cockpit mit min. 5 spezifischen, harten KPIs aus den Quellen sein.

DAS MIKRO-FRAMEWORK (Gilt fuer ALLE 30 Folien): Du musst JEDE Folie zwingend nach dem folgenden Schema aufbauen. Jede Folie muss ein Informationsfeuerwerk sein und diese drei Fragen explizit und detailliert beantworten:

Das WAS (Fakten & Scope): Was ist der exakte technische Sachverhalt, die Metrik oder die Anforderung?

Das WIE (Implementierung & Mechanik): Wie wird/wurde es technisch auf Code-/Architekturebene geloest? Welche Schnittstellen greifen? (Hier MUESSEN in Block 4 die Prozesse zur Pruefung externer Quellen und das fruehe Eingreifen des Red Teams exakt verortet werden).

Das WARUM (Rationale & Logik): Warum wurde dieser Weg gewaehlt? Was ist die architektonische Rechtfertigung oder der Business Value hinter dieser Entscheidung?

DIE 5 BLOECKE (Zusammenfassung der Schwerpunkte):

Block 1 (Historie): Nur abgeschlossene Evolution.
Block 2 (Durchbrueche): Nur validierte PoCs und harte Metriken der Vergangenheit.
Block 3 (Zielbild): Anforderungen und Scope der naechsten Phase (ohne Tech-Stack-Implementierung).
Block 4 (Architektur): Tech-Stack, Schnittstellen-Design. Zwingend: Einbindung der externen Quellenpruefung und der Checkpoints des Red Teams im fruehen Entwicklungszyklus.
Block 5 (Knackpunkte): Single Points of Failure, Security-Gaps, Flaschenhaelse und deren Mitigation.

Ausgabeformat & Speaker Notes (LOGBUCH-PFLICHT):
Liefere das Skript exakt formatiert (Slide X: Titel). Unter jeder Folie listest du die detaillierten Speaker Notes auf.
KRITISCHE ANWEISUNG FUER DIE NOTIZEN: Extrahiere alle mathematischen Formeln, Gleichungen oder logischen Axiome, die in den Dokumenten vorkommen, zwingend in die Speaker Notes der passenden Folie. Diese werden fuer das Projekt-Logbuch benoetigt, um sie im Nachgang minutioes auf logische Konsistenz, Transitivitaet und moegliche Axiom-Verletzungen zu pruefen.

Fuer die visuelle Darstellung auf den Slides: Generiere Mermaid.js-Code fuer das WIE, damit die Ingenieure die Architektur sofort als Diagramm rendern koennen.
```

---

## CRUX-Check [CRUX-MK]
Jede Quelle die hochgeladen wird muss rho-relevant sein.
Keine "nice to have" Quellen. Nur was rho * L(t) foerdert.
Wenn unklar: Nicht hochladen. NLM-Qualitaet > NLM-Quantitaet.

---

## Architektur + Historie
Fuer die theoretischen Grundlagen (10 Organe, 4 Saeulen, Hamilton, Bio-Muster, 30 Patches):
Lies `ARCHITECTURE.md` im selben Verzeichnis. Das ist v8.1 TURBOLOADER komplett.
