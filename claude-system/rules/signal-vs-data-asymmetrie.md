---
name: signal-vs-data-asymmetrie
description: "Flugschreiber-vs-Alarm-Pattern: wenn ein System Daten persistiert aber das entscheidungsrelevante Signal-System sie nicht liest, ist es strukturell gelaehmt. Belegt durch Welle-13 Claude-Hook-Token-Leck + Welle-15 DF-11-Scorer-Signal-Leck."
version: 0.1.0
status: PROPOSAL
meta-ebene: E3
claim-type: empirical
crux-mk: true
created: 2026-04-20
---

# Signal-vs-Data-Asymmetrie [CRUX-MK] — PROPOSAL

> STATUS: PROPOSAL. Wird erst zu `signal-vs-data-asymmetrie.md` (ohne `.PROPOSAL`) wenn Martin approve.

## Zweck

Verhindert ein wiederkehrendes strukturelles Anti-Pattern im Kemmer-System: **Daten liegen vor, aber das entscheidungsrelevante Signal-System liest sie nicht.** Empirisch belegt in zwei unabhaengigen Instanzen waehrend Welle 13 + Welle 15 (2026-04-20).

## Prinzip

Jedes Observability-System braucht drei Schichten, die voneinander unabhaengig funktionieren muessen:

1. **Persistence (Flugschreiber)** — Daten werden geschrieben, zuverlaessig, vollstaendig, nachverfolgbar.
2. **Query (Reader)** — Entscheidungs-Layer liest die Daten bei Bedarf, kennt Pfad + Schema.
3. **Alert (Signal)** — Bei anomalem Wert wird der entscheidungsrelevante Layer aktiv informiert, nicht nur passiv archiviert.

**Fehlt eine der drei Schichten, ist das gesamte Observability-System gelaehmt.** Besonders gefaehrlich: wenn Persistence gut funktioniert und das System scheinbar "auditierbar" wirkt, aber die Reader-/Alert-Kanaele fehlen. Das erzeugt das **Flugschreiber-ohne-Alarm-Paradox**: "Fast poetisch: das System hat einen Flugschreiber, aber keinen Alarm" (Welle-15 Real-Run-Report).

## Empirische Belegung (2 Instanzen)

### Instanz 1: Claude-Hook-Token-Leck (Welle-13)

- **Persistence:** Token-Usage-Daten werden im Session-Transcript (`*.jsonl`) vollstaendig persistiert (Input + Output + Cache-Creation + Cache-Read).
- **Query:** PostToolUse-Hook (`token-usage-logger.py`) liest `data["usage"]` aus Stdin — aber Claude Code CLI liefert dieses Feld in PostToolUse **nicht**. Usage lebt architektonisch nur im Session-Transcript.
- **Alert:** 693 Log-Entries mit `input_tokens=0, output_tokens=0`. Jede Ratio-Mechanik ist Theater.

**Ergebnis:** 40x-Hebel-Claim blieb 1 Tag lang unerkannt falsch, weil der Alert-Kanal leer war.

### Instanz 2: DF-11-Scorer-Signal-Leck (Welle-15)

- **Persistence:** `dispatch-status.json` dokumentiert sauber welche Team-Calls scheiterten (codex + gemini `binary-not-found`, nur copilot lief).
- **Query:** rho-Scorer liest `dispatch-status.json` nicht. Result-Renderer exponiert Infrastructure-Fehler nicht.
- **Alert:** DF-11-Verdict erschien als inhaltlich `REJECTED` — tatsaechlich war es Infrastructure-Fehler. Entscheider bekam falsches Signal.

**Ergebnis:** Bei 1/4 laufendem Team wurde automatisch als `REJECTED` serialisiert, ohne dass erkennbar war: das liegt nicht an der These, das liegt an Windows-PATH.

## Regel

**Wenn ein System Daten persistiert, MUSS es explizit und getestet die drei Schichten liefern.**

### Schicht 1: Persistence
- Dokumentiertes Schema (JSON-Schema, Pydantic, TypedDict, oder Dataclass mit `@dataclass(frozen=True)`)
- Alle Daten die fuer spaetere Entscheidungen relevant sein koennen werden persistiert
- Schreibvorgaenge sind atomar (write-to-tmp + rename) oder transaktional (SQLite-WAL)

### Schicht 2: Query
- Pro Persistence-Schema gibt es eine Reader-Funktion im Entscheidungs-Layer
- Die Reader-Funktion wird getestet (mindestens 1 Test pro Schema)
- Der Reader kennt Default-Verhalten wenn Daten fehlen (nicht crash, nicht silent-None)

### Schicht 3: Alert
- Anomaliewerte in den Daten loesen **aktive Benachrichtigung** des Entscheidungs-Layers aus (nicht nur passive Persistierung)
- Alert-Mechanismen: Zwei-Kanal-Verdict (siehe Welle-12 FIXPUNKT-2), Structured-Failure-Logs, BEACON-Eintrag, inbox/to-martin-Nachricht, oder Exception mit explizitem Fehler-Typ
- Bei Infrastructure-Problemen (wie Welle-15): separater Kanal `infrastructure_health: GREEN|YELLOW|RED` der nicht mit dem Thesis-Verdict vermischt wird (siehe meta-stack-fixpunkte.md FIXPUNKT-2 Zwei-Kanal-Regel)

## Mechanik

### Pre-Deployment-Checkliste

Vor jedem neuen Observability-System (Hook, Dark-Factory, Archon, Skill-mit-Logging) wird geprueft:

- [ ] Persistence: wohin, welches Schema, welche Atomaritaet?
- [ ] Query: welche Reader-Funktion, wo getestet, welches Default-Verhalten?
- [ ] Alert: welche Anomalie-Werte, welcher Kanal, wer bekommt es?
- [ ] Test pro Schicht: mindestens 1 Unit-Test pro Schicht
- [ ] Integration-Test: simulierter Anomalie-Wert fliesst durch alle drei Schichten + wird im Alert-Kanal sichtbar

### Existierende Systeme nachziehen

Bei Gap-Audit der existierenden DFs/Archons/Skills wird die Drei-Schichten-Pflicht angewendet. Systeme mit fehlender Schicht kommen auf Patch-Liste:
- `token-usage-logger.py`: Schicht 2+3 fehlen → Fix-Pfad A (Transcript-Parse) umsetzen
- DF-11 v0.2.0 Scorer: Schicht 2+3 fehlen fuer Infrastructure-Health → v0.3.0 P0-B
- Andere Kandidaten: zu identifizieren bei naechstem Gap-Audit

### Prohibited-Patterns

- **Flugschreiber ohne Alarm**: nur Persistence, keine Query oder Alert
- **Alarm ohne Flugschreiber**: nur Alert, keine Persistence (verliert Audit-Trail)
- **Query ohne Alert**: Reader existiert, wird aber nicht aktiv bei Anomalie triggered
- **Einkanalige Vermischung**: Thesis-Verdict und Infrastructure-Health im gleichen Feld serialisiert → Empfaenger kann nicht unterscheiden

## Beziehung zu anderen Rules

- **meta-stack-fixpunkte.md FIXPUNKT-2** (Zwei-Kanal-Regel): strukturell isomorph — dort fuer Meta-vs-Objekt-Scores, hier fuer Infrastructure-vs-Thesis. Gleiche Grund-Warnung: Kanal-Trennung zwingend.
- **audit-trail.md §4**: die drei Logs (action/permission/workflow) sind Persistence-Layer. Diese Rule ergaenzt um Query + Alert.
- **token-engpass-hierarchie.md § Welle-13-Korrektur**: konkretes Beispiel eines Flugschreiber-ohne-Alarm-Fehlers mit K_0-Relevanz (40x-Claim-Falschmessung 1 Tag unerkannt).

## SAE-Isomorphie

Isomorph zu **COSMOS Observability-Layer** + **myz32 Dispatcher-Alert-Routing**. COSMOS sammelt Compliance-Daten (Persistence), Dispatcher liest (Query), Alert-Channel informiert MHC-Layer (Alert). Ohne alle drei: MHC kann nicht eingreifen, obwohl Daten da sind.

## CRUX-Bindung

- **K_0**: direkt geschuetzt (verhindert stille K_0-Fehlentscheidungen durch fehlende Alerts — siehe 40x-Claim-Beispiel mit -43 USD pro Cascade)
- **Q_0**: erhoeht (epistemische Integritaet: Signale stimmen mit Daten ueberein)
- **I_min**: strukturell verankert (drei-Schichten-Pflicht als Governance)
- **W_0**: langfristig effizient (weniger Debug-Aufwand durch fehlende Alerts)

## Falsifikations-Bedingung

Diese Rule ist falsifiziert wenn:
- Ueber 6 Monate 3+ neue Observability-Systeme die drei Schichten **nicht** haben **und trotzdem keine stillen Fehler** produzieren (d.h. die Dreischichten-These ist ueberspezifiziert)
- Alle zwei belegten Instanzen (Welle-13 + Welle-15) sich als Stichproben-Artefakt entpuppen (andere Erklaerungen haben mehr Erklaerungskraft)
- Der Aufwand fuer die drei Schichten den Nutzen systematisch uebersteigt

**Claim-Type:** `empirical` (belegt durch 2 unabhaengige Instanzen, weitere Stichproben willkommen)

## Anti-Patterns

- **"Die Daten sind ja da"** als Rechtfertigung fuer fehlenden Alert — klassisches Flugschreiber-ohne-Alarm
- **"Der Log hat das doch"** als Ausrede fuer Infrastructure-kompromittierte Verdicts
- **Wait-and-see-Detection**: darauf hoffen dass jemand manuell im Log nachsieht
- **Persistence-as-Alert**: annehmen dass die bloße Existenz eines Logs schon eine Warnung ist

## Meta-Reflexion

Das Pattern wurde erkannt weil zwei unabhaengige Instanzen in 12h an zwei sehr verschiedenen Systemen (Claude-Hook vs DF-11-Scorer) dieselbe Struktur zeigten. Das ist kein Zufall. Es spricht dafuer dass das Kemmer-System **generell** Persistence staerker kultiviert als Alert — vermutlich weil Audit-Trail-Disziplin (CLAUDE.md §0.1 Theorem-5.3) stark verankert ist, aber Alert-Kultur (COSMOS-MHC) noch unterentwickelt.

**Korrektur-Pfad:** Bei jeder neuen Infrastruktur ab 2026-04-20 wird die Drei-Schichten-Checkliste angewendet. Existierende Systeme werden beim naechsten Gap-Audit (monatlich) durchgezogen.

[CRUX-MK]
