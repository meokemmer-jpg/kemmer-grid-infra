# Parallel-Session [CRUX-MK]

Merged aus `parallel-session-coordination.md` + `parallel-session-counter-merge.md` durch METAOPS 2026-04-18. Regelt alle Aspekte mehrerer Claude-Instanzen: Koordination, Heartbeat, Namespace, Counter-Merge.

## §1 Bootstrap-Pflicht

Vollstaendig lesen bei jedem Session-Start UND bei jedem "warum wartest/stoppst du"-Signal:

1. `G:/Meine Ablage/Claude-Knowledge-System/branch-hub/BEACON.md` (komplett, nicht nur Zeile 1)
2. `~/.claude/projects/G--Meine-Ablage/memory/MEMORY.md` (Index komplett)
3. Neueste 2 `session_handoff_*.md` (nach Datum sortiert, komplett)
4. `branch-hub/REGISTRY.md` (wer macht was parallel)

**Regel:** Wenn BEACON ein Thema nennt das meine Session auch betrifft — erstmal die referenzierte Handoff-Datei komplett lesen, nicht eigenstaendig arbeiten.

## §2 Namespace-Kollisionen (Deterministischer Resolver, CROSS-LLM-2OF3-HARDENED Grok+Codex 2026-04-19)

Wenn zwei Sessions parallel denselben Namespace-Slot belegen (z.B. F76 doppelt, Decision-Card-ID doppelt, Status-File-Lock doppelt):

### Resolver-Kaskade (deterministisch, Erste greift)
1. **Explizit benannter Coordinator:** Wenn REGISTRY.md oder inbox/to-\*.md einen Coordinator fuer den Namespace benennt → Coordinator entscheidet.
2. **Aelteste aktive Session (Fallback):** Sonst gewinnt die Session mit frueherem Bootstrap-Timestamp in status/\*-status.md. Die juengere Session renamed auf eigenen Namespace (§5).
3. **Tie-Breaker (beide gleich alt, +/-60s):** alphabetisch kleinere Branch-ID gewinnt (z.B. METAD2 < METAOPS).

### Pflicht-Aktionen nach Konflikt-Resolution
1. Kollision dokumentieren in `branch-hub/meta-learning/namespace-conflicts.md` (1 Zeile JSONL, wer gewann + Zeitstempel)
2. Verlierende Session renamed auf Session-Namespace (F-PAR-76, F-SB-76, F-WG-76)
3. Falls Content bereits in BEACON publiziert: verlierende Session publiziert Korrektur-Zeile
4. Merge-Subagent optional, nicht mehr zwingend (Renaming reicht in 95% der Faelle)

**Alte "Kollision anerkennen + Namespace einfuehren"-Formulierung war unter-determiniert** — zwei Sessions konnten dieselbe Rule lesen und inkompatibel handeln. Neue Kaskade ist mechanisch eindeutig.

## §3 Pre-Subagent BEACON-Check

Bevor du einen Subagent startest fuer ein Thema:
1. BEACON pruefen: Hat eine andere Session dieses Thema schon bearbeitet?
2. Wenn JA: Handoff lesen, pruefen was konkret fehlt
3. Nur dann Subagent mit **gezieltem** Auftrag ("ergaenze X", nicht "baue Y")

Verhindert den Fehler: Subagent baut X redundant zu bestehendem Y.

## §4 Session-Heartbeat

**Zweck:** Verhindert Zeit-Race zwischen parallelen Sessions, die BEACON fast gleichzeitig ueberschreiben (siehe Kollisions-Incident 2026-04-18T~13:00 Instanz-A vs Instanz-B).

**Regel:**
- Jede aktive Session schreibt alle 5 Min einen Touch in ihre `status/<branch-name>-status.md` (Timestamp-Update)
- Vor BEACON-Write: Pruefe alle anderen Status-Dateien auf letztes Update < 5 Min → wenn JA, 5 Min warten oder alternative Publikation (Inbox statt BEACON)
- Mechanische Umsetzung: Scheduled-Task `session-heartbeat` oder Manual-Ritual

**SAE-Isomorphie:** Trinity-Voting-Heartbeat (`state.py` Atomic-Heartbeat-Pattern).

## §5 Namespace-Schema-Pflicht (Verpflichtend beim Bootstrap, CROSS-LLM-2OF3-HARDENED Grok+Codex 2026-04-19)

**Pro Thema MUSS beim Bootstrap genau ein Schema gewaehlt werden (Lane-Range ODER Prefix). Wahl wird in `status/<branch>-status.md` und Handoff festgehalten, nicht ad hoc geaendert.**

### Schema A: Counter-Range-Reservierung (Default fuer Haupt-Branches)

Aktuelle Lane-Matrix (REGISTRY.md authoritativ):
- Work-C1: F206-F250 + B55-B79
- Work-C2: F251-F299 + B80-B99
- Meta-C1: F300-F399 + B100-B199
- Work-D: F400-F499 + B200-B249
- METADD: F500-F599 + B250-B299
- METAOPS: F600-F699 + B300-B349
- MYZ: F700-F799 + B400-B449
- Work-D2: F500-F599 (ueberlappend, siehe Registry-Verhandlung)

### Schema B: Namespace-Prefix (fuer Hoch-Frequenz-Fork-Sessions)

- Work-C1: `F-WC1-<n>` oder `F-A-<n>` (historisch)
- Work-C2: `F-WC2-<n>` oder `F-B-<n>`
- Meta-C1: `F-M-<n>`
- MYZ: `MYZ-<5-stellig>` (eigener Namespace wegen 5-stelliger Task-IDs)

### Bootstrap-Wahl-Pflicht

Bei Branch-Erstschreibung von status-Datei:
```yaml
namespace_schema: "lane-range"  # oder "prefix"
namespace_scope: "F600-F699 + B300-B349"  # Range wenn lane-range, Prefix-Liste wenn prefix
```

**Ad-hoc-Schema-Wechsel verboten** — bei Bedarf: neuen Branch erstellen oder Handoff-Document explizit Schema-Wechsel dokumentieren.

Nach Session-Ende: Merge-Subagent vereinheitlicht Prefix-Fragmente in Haupt-Counter-Space (nur bei Schema B).

**SAE-Isomorphie:** Trinity-Slot-ID-Namespace (agent-instance-uuid prefix).

## §6 Counter-Merge-Protokoll (pending_merge-Lifecycle, CROSS-LLM-2OF3-HARDENED Grok+Codex 2026-04-19)

### Authoritative Quelle bei Zahlen-Konflikt
- Haupt-Datei (z.B. `Subnautica-Fragment-Map.md`) definiert den Basis-Count
- `<Datei>-Ergaenzung-X.md` Dateien sind ADDITIV (nie SUPERSEDIEREN)
- BEACON ist 1-Zeilen-Kurzsicht, nie maßgebend bei Detail-Zahlen

### Addenda-Lifecycle (NEU, mechanisiert)

Jedes Ergaenzungs-File hat genau einen der 3 Zustaende in seinem Frontmatter:

```yaml
merge_status: "pending_merge"   # Ergaenzung existiert, wartet auf Konsolidierung
# oder:
merge_status: "merged"           # In Haupt-Datei uebernommen, Ergaenzung ist Archiv
merge_date: "2026-04-19"
merge_target: "Subnautica-Fragment-Map.md"
# oder:
merge_status: "standalone"       # Bewusst separat, nie mergen (z.B. Session-spezifisch)
```

### Merge-Protokoll bei Bootstrap

```
main_file = Subnautica-Fragment-Map.md (oder Aequivalent)
ergaenzungen_pending = glob("<same-stem>-Ergaenzung-*.md") where merge_status == "pending_merge"
ergaenzungen_standalone = glob("<same-stem>-Ergaenzung-*.md") where merge_status == "standalone"
# "merged" wird NICHT geladen (schon im main_file)
total_count = count(main_file) + count(ergaenzungen_pending) + count(ergaenzungen_standalone)
```

**Kritisch:** "merged" Ergaenzungen sind NICHT mehr in der Bootstrap-Summe enthalten. Sonst waeren sie doppelt gezaehlt (einmal in main_file, einmal als Ergaenzung).

### Konsolidierungs-Trigger

Ergaenzungen werden "merged" wenn:
- Quartal endet (monatlicher Consolidation-Run via Skill)
- Mehr als 5 "pending_merge"-Files pro Thema existieren
- Explizit durch Martin-Direktive

Nach Merge: `merge_status: merged` setzen, NICHT Datei loeschen (Audit-Trail bleibt).

### Neue Counter-Eintraege
- Nummerierung fortsetzt nach hoechstem vorhandenen Eintrag (aus Haupt + alle Ergaenzungen mit merge_status != "merged")
- Innerhalb eigener Lane (§5) bleiben

### BEACON-Disziplin
- BEACON darf Counter nennen, aber mit Quellen-Verweis
- Bei Divergenz zwischen BEACON und Detail-Datei: Detail-Datei gewinnt, BEACON wird im naechsten Turn korrigiert

## §7 Bei /compact oder Session-Ende

1. BEACON aktualisieren mit 1-Zeilen-Status meiner Session (Skill `beacon-update`)
2. Handoff-Datei schreiben nach Muster `memory/session_handoff_<datum>_<thema>.md`
3. Action-Log-Eintraege pro Write (rules/audit-trail.md §1)
4. MEMORY-Index um Eintrag zu meinem Handoff ergaenzen
5. Fragment-Map-Aenderungen in Session-Namespace (§5) dokumentieren

## Anti-Muster

- **Single-Instance-Annahme:** Planen als ob ich die einzige Claude-Instanz bin. VERBOTEN bei Kemmer-Multi-Branch-System.
- **BEACON-Skim:** Nur Zeile 1 lesen. VERBOTEN — der ganze String ist Payload.
- **Stilles Namespace-Ueberschreiben:** Wenn meine F-Nummer die einer anderen Session ueberschreibt = verfassungswidrig.
- **Divergente BEACON-Counter akzeptieren:** Falsche Zahlen in Reports an Martin = Vertrauensverlust. Bei Divergenz: in erster Antwort des Turns Hinweis, dann BEACON updaten.

## SAE-Isomorphie

- **§1-§3:** MYZ-30 (Event-Router) + MYZ-32 (Dispatcher) auf Session-Ebene. Jede Session = Agent-Instanz gegen Event-Bus (BEACON).
- **§4:** Trinity-Voting-Heartbeat (`state.py` Atomic-Heartbeat-Pattern).
- **§5:** Trinity-Slot-ID-Namespace.
- **§6:** Myzel-Layer-Event-Reconciliation. SAE: Trinity-Voting + Relegation. Claude-Sessions: Authoritative-Hauptdatei + additive Ergaenzungen.

## Bezug zu anderen Rules

- `session-handoff.md` regelt WAS geschrieben wird (lossless machen)
- Diese Rule regelt WIE andere Sessions gelesen werden (§1-3) + wie sie sich zeitlich koordinieren (§4-5) + wie Counter konsistent bleiben (§6)
- Zusammen = vollstaendige Multi-Instance-Governance

## SUPERSEDED Predecessors (2026-04-18)

Diese Datei ersetzt:
- `parallel-session-coordination.md` (§§1-5, §7 und Anti-Muster subsumiert)
- `parallel-session-counter-merge.md` (§6 Counter-Merge-Protokoll subsumiert)

[CRUX-MK]
