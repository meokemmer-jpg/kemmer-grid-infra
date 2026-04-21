# SUPERSEDED — Lies stattdessen: rules/parallel-session.md [CRUX-MK]
# WARNUNG: Dieses Dokument ist veraltet seit 2026-04-18 (METAOPS Mission-2).
# Aktuelle Version: ~/.claude/rules/parallel-session.md §§1-5, §7 und Anti-Muster (unveraendert subsumiert).

# Parallel-Session-Koordination [CRUX-MK] (ARCHIV)

**Zweck:** Verhindert Eigenfehler EF-2 (Parallel-Session nicht erkannt). Mehrere Claude-Instanzen arbeiten parallel am Kemmer-System — ohne Koordination: Duplikat-Arbeit, Map-Konflikte, widersprueechliche Rules.

## Pflicht bei jedem Session-Start UND bei jedem "warum wartest/stoppst du"-Signal

Vollstaendig lesen, nicht nur Zeile 1:

1. `G:/Meine Ablage/Claude-Knowledge-System/branch-hub/BEACON.md` (komplett, 1-3 Zeilen)
2. `~/.claude/projects/G--Meine-Ablage/memory/MEMORY.md` (Index komplett)
3. Neueste 2 `session_handoff_*.md` (nach Datum sortiert, komplett)
4. `branch-hub/REGISTRY.md` falls existent (wer macht was parallel)

**Regel:** Wenn BEACON ein Thema nennt das meine Session auch betrifft — erstmal die referenzierte Handoff-Datei komplett lesen, nicht eigenstaendig arbeiten.

## Bei Namespace-Kollisionen (z.B. Fragment-Nummern)

Wenn zwei Sessions parallel F76 belegen:
1. Kollision sofort anerkennen (keine stillschweigende Uebernahme)
2. Session-Namespace einfuehren (F-PAR-76, F-SB-76, F-WG-76)
3. Spaetere Konsolidierung durch expliziten Merge-Subagent
4. Eintrag in `branch-hub/meta-learning/namespace-conflicts.md`

## Vor Subagent-Start — BEACON-Check

Bevor du einen Subagent startest fuer ein Thema:
1. BEACON pruefen: Hat eine andere Session dieses Thema schon bearbeitet?
2. Wenn JA: Handoff lesen, pruefen was konkret fehlt
3. Nur dann Subagent mit **gezieltem** Auftrag ("ergaenze X", nicht "baue Y")

Das verhindert den Fehler: Subagent baut X redundant zu bestehendem Y.

## Bei /compact oder Session-Ende

1. BEACON aktualisieren mit 1-Zeilen-Status meiner Session (Skill `beacon-update`)
2. Handoff-Datei schreiben nach Muster `memory/session_handoff_<datum>_<thema>.md`
3. Action-Log-Eintraege pro Write (rules/action-logging.md)
4. MEMORY-Index um Eintrag zu meinem Handoff ergaenzen
5. Fragment-Map-Aenderungen in Session-Namespace dokumentieren

## Anti-Muster

- **Single-Instance-Annahme:** Planen als ob ich die einzige Claude-Instanz bin. VERBOTEN bei Kemmer-Multi-Branch-System.
- **BEACON-Skim:** Nur Zeile 1 lesen. VERBOTEN — der ganze String ist Payload.
- **Stilles Namespace-Ueberschreiben:** Wenn meine F-Nummer die einer anderen Session ueberschreibt = verfassungswidrig.

## §7 Session-Heartbeat (aktiviert 2026-04-18 via Instanz-B-Vorschlag + Martin-Approval #14)

**Zweck:** Verhindert Zeit-Race zwischen parallelen Sessions, die BEACON fast gleichzeitig ueberschreiben (siehe Kollisions-Incident 2026-04-18T~13:00 Instanz-A vs Instanz-B).

**Regel:**
- Jede aktive Session schreibt alle 5 Min einen Touch in ihre `status/<branch-name>-status.md` (Timestamp-Update)
- Vor BEACON-Write: Pruefe alle anderen Status-Dateien auf letztes Update < 5 Min → wenn JA, 5 Min warten oder alternative Publikation (Inbox statt BEACON)
- Mechanische Umsetzung: Scheduled-Task `session-heartbeat` oder Manual-Ritual (alle 5 Min wenn aktiv schreibend)

**SAE-Isomorphie:** Trinity-Voting-Heartbeat (`state.py` Atomic-Heartbeat-Pattern).

## §8 Namespace-Prefix (optional bei Hoch-Frequenz-Parallel)

**Zweck:** Verhindert F-/B-Nummer-Kollisionen wenn zwei Sessions zeitgleich schreiben.

**Regel:**
- Default: Counter-Range-Reservierung (Work-C1 F206-F250, Work-C2 F251-F299, Meta-C1 F300-F399)
- Alternativ bei Crunch: Prefix
  - Work-C1: `F-WC1-<n>` oder `F-A-<n>` (historisch)
  - Work-C2: `F-WC2-<n>` oder `F-B-<n>`
  - Meta-C1: `F-M-<n>`
- Nach Session-Ende: Merge-Subagent vereinheitlicht Prefix-Fragmente in Haupt-Counter-Space

**SAE-Isomorphie:** Trinity-Slot-ID-Namespace (agent-instance-uuid prefix).

## SAE-Isomorphie (allgemein)

Dies ist MYZ-30 (Event-Router) + MYZ-32 (Dispatcher) auf Session-Ebene. Jede Session ist eine Agent-Instanz, die gegen denselben Event-Bus (BEACON) arbeitet.

## Bezug zu rules/session-handoff.md

`session-handoff.md` regelt WAS geschrieben wird (lossless machen).
`parallel-session-coordination.md` regelt WIE andere Sessions gelesen werden (Kollisions-Schutz) + wie sie sich zeitlich koordinieren (§7+§8).
Beide zusammen = vollstaendige Multi-Instance-Governance.

[CRUX-MK]
