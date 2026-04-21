# SUPERSEDED — Lies stattdessen: rules/context-budget.md [CRUX-MK]
# WARNUNG: Dieses Dokument ist veraltet seit 2026-04-18 (METAOPS Mission-2).
# Aktuelle Version: ~/.claude/rules/context-budget.md §§1,2,4,5,6,7,8,9 (alle 8 Regeln subsumiert, Regel 7 cross-referred auf self-discipline.md §1).

# Meta-Calibration [CRUX-MK] (ARCHIV)

**Lernsatz (aus Session 2026-04-17):** Eigene Heuristiken systematisch gegen externe Messungen pruefen. M2 Lambda-Honesty in Aktion.

## Regel 1: Context-Fuellung NIE nach Heuristik schaetzen

**Problem 2026-04-17:** Ich schaetzte 95-96%, tatsaechlich 41%. Faktor 2 zu hoch.
**Ursache:** Ich habe Subagent-Reports als Haupt-Context gezaehlt, obwohl sie destilliert zurueckkamen. Das Volumen der *ausgehenden* Prompts hatte ich nicht gewichtet gegen das Volumen der *einkommenden* Reports.

**Regel:**
- KEINE Aussagen wie "Context bei X%" ohne externe Messung (UI-Anzeige, `/context`, etc.)
- Wenn keine Messung verfuegbar: Heuristik explizit markieren ("geschaetzt ~X%, nicht gemessen")
- Bei Verdacht auf Kulminations-Naehe: erst messen, dann entscheiden
- Externe Messung schlaegt interne Heuristik IMMER

## Regel 2: Kulminationspunkt-Schutz ist mechanisch, nicht gefuehlt

- Max 3 Subagenten gleichzeitig (nicht "ca. 3")
- Max 3 Factories in Shadow
- Bei Unsicherheit: aktiv zaehlen, nicht schaetzen

## Regel 3: Handoff-Schreiben ist IMMER billig

Theorem 5.3 (Session-Handoffs lossy) sagt: Schreibe lieber einmal zu viel als einmal zu wenig.
- Kosten Handoff: ~20 Min Schreibzeit, ~5k Token
- Kosten kein Handoff + Session-Bruch: potenziell gesamte Session-Erkenntnisse verloren
- **Regel: Jede Session mit >3 Subagenten-Reports bekommt Handoff**, unabhaengig vom Context-Stand

## Regel 4: Lambda-Honesty als Prinzip

Bei jeder quantitativen Aussage:
- Ist das gemessen oder geschaetzt?
- Wenn geschaetzt: mit welchem Fehler-Balken?
- Gibt es Indikatoren dass meine Schaetzung systematisch daneben liegt?

Die Antwort "ich weiss nicht" ist besser als ein falscher Wert.

## Regel 5: Meta-Learning nach jedem Fehler

- Wenn ich einen Fehler mache (Context-Fehlschaetzung, Subagent-Abbruch, Chrome-MCP-Limit):
  1. Was war die konkrete Fehl-Annahme?
  2. Was ist der generalisierbare Lernsatz?
  3. Wo wird er mechanisch verankert? (Rule, Skill, Doc)
- Ohne mechanische Verankerung: vergessen bis zum naechsten Auftreten

## Regel 6: Infrastructure-Pre-Flight (aus BIAS-011 + BIAS-013)

Bevor ein Subagent mit unsicherer Infrastruktur startet (Chrome-MCP mit Screenshots,
externes API mit Rate-Limit, neue Integration):
- Pre-Flight-Test durchfuehren (1-2 Min): passt das Tool zur geplanten Skala?
- Wenn N > 10 (Notebooks, API-Calls, Screenshots): Pilot mit N=1 zuerst
- Erst nach Pilot-Erfolg volle Batch
- Rate-Limit + Image-Dimension + Token-Cap vorab dokumentieren

## Regel 7: Rule-Aenderung schlaegt Rule-Ausnahme (aus BIAS-012 + BIAS-007)

Wenn Rechtfertigungs-Reflex fuer eine Rule-Ausnahme entsteht ("aber dieses Mal ist es
anders weil..."):
- STOPP. Rechtfertigung ist verdaechtig.
- Option A (zulaessig): Rule formal aendern (edit Rule-Datei, Begruendung, Version-Bump)
- Option B (nicht zulaessig): Situative Ausnahme durchziehen

Wenn Ausnahme gerechtfertigt ist → Rule war zu eng → aendern. Wenn nicht → Versagen.

*(Auch dokumentiert in rules/self-discipline.md §1 — Konsolidierung ausstehend.)*

## Regel 9: Parallel-Branch-Awareness (aus BIAS-010)

Vor jeder substantiellen Arbeit (neuer Subagent, Rule-Aenderung, Canon-Update):
- **BEACON.md** lesen (letzte Aenderung aus anderem Branch?)
- **REGISTRY.md** im branch-hub (welche Branches aktiv?)
- **inbox/to-*.md** (Nachrichten an mich?)
- **knowledge-diffs/** letzte 48h (was hat parallel-Branch gelernt?)
- **Vault-CLAUDE.md** (Stand-Anker vom Vault-Owner)

Wenn parallel-Branch dasselbe Thema bearbeitet: **abstimmen, nicht duplizieren**.
BIAS-008 (Gerdi-Rollen) + BIAS-009 (Sebastian-SUPERSEDED) waren Symptome dieses Meta-Bias.

**Mechanisch:** Subagent-Prompt bekommt Standard-Zeile "Check paralleler Branch-Fortschritt
in BEACON/REGISTRY/knowledge-diffs vor Start".

## Regel 8: Deployment-Pflicht (aus BIAS-014 CRIT)

Jedes geschriebene Artefakt (Proposal, Rule, Skill, Decision Card, Finding) bekommt
eines von drei Feldern im Frontmatter:
- `aktiviert: <datum>` — ist live, wirkt
- `aktiviert-in: <frist>` — wartet auf Trigger, max 30 Tage
- `supersession-gescheitert: <datum>` — wurde abgelehnt, archiviert

Nach 30 Tagen ohne Aktivierung: automatische Supersession-Pruefung. Ohne diesen Mechanismus
akkumuliert Deployment-Gap (BIAS-014 CRIT). Tester-Wargame-Beleg: veraltete Doku vergiftet
Branches (20-50k EUR/J Schaden-Potenzial).

## SAE-Isomorphie

Dies ist Governance-Tier-Selbstkalibrierung: q-Normalisierung fuer Claude's eigene Vorhersagen.
q_meta = (Schaetzung - Gemessen) / Schaetzung. Bei |q_meta| > 0.3: Re-Kalibrierung der Heuristik.

[CRUX-MK]
