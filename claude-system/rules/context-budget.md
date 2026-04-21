# Context-Budget [CRUX-MK]

Merged aus `context-fill-messung.md` + `meta-calibration.md` + `token-budget.md` durch METAOPS 2026-04-18.
Zusammengefuehrt weil alle drei Regeln Claude's **eigenes Arbeitsfenster** regeln: Context, Token, Messung, Kulminationspunkt, Pre-Flight.

## §1 Context-Fuellung nur gemessen, nie geschaetzt

**Problem (belegt 2026-04-17):** Ich schaetzte 95-96%, tatsaechlich 41%. Faktor 2 zu hoch. Ursache: Subagent-Reports als Haupt-Context gezaehlt, obwohl sie destilliert zurueckkamen.

**Regel:**
- KEINE Aussagen wie "Context bei X%" ohne externe Messung (UI-Anzeige, `/context`, System-Reminder, Martin-Feedback)
- Wenn keine Messung verfuegbar: Heuristik explizit markieren ("geschaetzt ~X%, nicht gemessen")
- Bei Verdacht auf Kulminations-Naehe: erst messen, dann entscheiden
- Externe Messung schlaegt interne Heuristik IMMER

**Hintergrund (Bias-Catalog):** Reads von Subagent-Reports bleiben in deren isoliertem Context, nur Destillate kommen zu mir. Ich ueberschaetze meinen echten Fill um 30-40%.

## §2 Kulminationspunkt-Schutz ist mechanisch, nicht gefuehlt

- Max 3 Subagenten gleichzeitig (nicht "ca. 3")
- Max 3 Factories in Shadow
- Bei Unsicherheit: aktiv zaehlen, nicht schaetzen

## §3 Heartbeat + Budget-Planung (1M Token Window)

### PFLICHT bei JEDER Session: Heartbeat starten

Bei Session-Start (nach Bootstrap): CronCreate Heartbeat alle 15 Minuten.

**Heartbeat prueft:**
1. **Schaetze Context-Fill** (basierend auf Gespraechslaenge, gelesene Dateien, Tool-Nutzung) — als **Heuristik** markieren (§1)
2. **Bei >50%**: Denken statt mechanisch wiederholen. Kein Bulk-Read mehr.
3. **Bei >70%**: WARNUNG an Martin. Workflow-Checkpoint schreiben. /compact empfehlen.
4. **Bei >85%**: Knowledge-Diff SOFORT schreiben. Alle offenen Items persistieren.
5. **Bei >95%**: STOP. Emergency-Handoff. Nicht weitermachen.

### Budget-Planung

- **Bootstrap:** ~50K Token (MEMORY + SKILL + Handoff + Feedback + Findings)
- **User-Auftrag:** ~200-400K
- **NLM/Browser:** ~100-200K (Screenshots = 5K pro Bild!)
- **Sicherung:** ~50K (Memory-Updates, Handoff)
- **Reserve:** ~200K

**Mechanische Zwangs-Kompakt-Schwelle (Cross-LLM-Audit 2026-04-19 P4, Gemini-M3):**
Bei externer Messung Context-Budget >900k: Zwangs-Kompaktierung VOR naechstem Subagent-Call. Grund: Summe der Budget-Posten kann ~500-900k erreichen, ohne Kompakt-Schwelle droht 1M-Hit mitten in aktiver Session.

## §4 Handoff-Schreiben ist IMMER billig

Theorem 5.3 (Session-Handoffs lossy) sagt: Schreibe lieber einmal zu viel als einmal zu wenig.
- Kosten Handoff: ~20 Min Schreibzeit, ~5k Token
- Kosten kein Handoff + Session-Bruch: potenziell gesamte Session-Erkenntnisse verloren
- **Regel:** Jede Session mit >3 Subagenten-Reports bekommt Handoff, unabhaengig vom Context-Stand

## §5 Lambda-Honesty als Prinzip

Bei jeder quantitativen Aussage:
- Ist das gemessen oder geschaetzt?
- Wenn geschaetzt: mit welchem Fehler-Balken?
- Gibt es Indikatoren dass meine Schaetzung systematisch daneben liegt?

Die Antwort "ich weiss nicht" ist besser als ein falscher Wert.

## §6 Meta-Learning nach jedem Fehler

- Wenn ich einen Fehler mache (Context-Fehlschaetzung, Subagent-Abbruch, Chrome-MCP-Limit):
  1. Was war die konkrete Fehl-Annahme?
  2. Was ist der generalisierbare Lernsatz?
  3. Wo wird er mechanisch verankert? (Rule, Skill, Doc)
- Ohne mechanische Verankerung: vergessen bis zum naechsten Auftreten

## §7 Infrastructure-Pre-Flight (aus BIAS-011 + BIAS-013)

Bevor ein Subagent mit unsicherer Infrastruktur startet (Chrome-MCP mit Screenshots, externes API mit Rate-Limit, neue Integration):
- Pre-Flight-Test durchfuehren (1-2 Min): passt das Tool zur geplanten Skala?
- Wenn N > 10 (Notebooks, API-Calls, Screenshots): Pilot mit N=1 zuerst
- Erst nach Pilot-Erfolg volle Batch
- Rate-Limit + Image-Dimension + Token-Cap vorab dokumentieren

## §8 Parallel-Branch-Awareness

**Verschoben** → siehe `parallel-session.md §1` (Bootstrap-Pflicht) + `§3` (Pre-Subagent BEACON-Check).

**Rationale (Cross-LLM-Audit 2026-04-19, P4):** Gemini + Codex unabhaengig festgestellt dass §8 Duplikat zu parallel-session §1+§3 ist. Single-Point-of-Truth-Prinzip: Koordinationslogik lebt in parallel-session.md.

Single-Line-Requirement hier: Subagent-Prompt bekommt Standard-Zeile *"Check paralleler Branch-Fortschritt in BEACON/REGISTRY/knowledge-diffs vor Start"*. (Das bleibt context-budget-relevant, da es Token-Budget-Implikationen hat.)

## §9 Deployment-Pflicht

**Verschoben** → siehe `deployment-governance.md` (ausgelagert 2026-04-19, Cross-LLM-2OF3-HARDENED Grok+Codex: Scope-Cut fuer Sauberkeit).

Originalinhalt (BIAS-014 CRIT, 2026-04-17) ist in `deployment-governance.md §1-§4` erweitert dokumentiert: Frontmatter-Status-Pflicht, automatische Supersession-Pruefung, Aktivierungs-Trigger, Deployment-Gap-Monitoring.

## Bezug zu anderen Rules

- `self-discipline.md` §1 (Rule-Ausnahme vs Rule-Aenderung) — parallele Disziplin-Regel. Konsolidierung von self-discipline und context-budget ausstehend.
- `parallel-session.md` §4 — Branch-Sync-Heartbeat (5 Min, status-Touch fuer Parallel-Branches). Dieser Rule §3 regelt Context-Fill-Heartbeat (15 Min, intern). **Zwei verschiedene Mechanismen, nicht konfligierend** (Cross-LLM-Audit 2026-04-19 P4, Gemini missdeutete als Widerspruch, Opus-Gegenanalyse gezeigt).
- `parallel-session.md` §1 + §3 — authoritativ fuer Multi-Branch-Koordination (Parallel-Branch-Awareness, frueher §8 hier, seit Cross-LLM-Audit 2026-04-19 verlagert).

## SAE-Isomorphie

- **§1** entspricht q-Normalisierung (nicht-kalibrierte Werte werden markiert)
- **§2** entspricht T_CAP (mechanische Grenze, nicht gefuehlte)
- **§3** entspricht tau_remaining + EOC-Kulmination (3 sinkende Throughput-Ticks)
- **§5** entspricht Lambda-Honesty (core/crux.py)

## SUPERSEDED Predecessors (2026-04-18)

Diese Datei ersetzt:
- `context-fill-messung.md` (subsumiert in §1)
- `meta-calibration.md` (subsumiert in §1, §2, §4, §5, §6, §7, §8, §9)
- `token-budget.md` (subsumiert in §3)

Die Predecessors werden mit SUPERSEDED-Header markiert, nicht geloescht (Audit-Trail).

[CRUX-MK]
