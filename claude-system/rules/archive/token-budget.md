# SUPERSEDED — Lies stattdessen: rules/context-budget.md [CRUX-MK]
# WARNUNG: Dieses Dokument ist veraltet seit 2026-04-18 (METAOPS Mission-2).
# Aktuelle Version: ~/.claude/rules/context-budget.md §3 (Heartbeat + Budget-Planung, unveraendert subsumiert).

# Token Budget + Heartbeat [CRUX-MK] (ARCHIV)

## PFLICHT bei JEDER Session: Heartbeat starten

Bei Session-Start (nach Bootstrap): CronCreate Heartbeat alle 15 Minuten.

## Heartbeat prueft:
1. **Schaetze Context-Fill** (basierend auf Gespraechslaenge, gelesene Dateien, Tool-Nutzung)
2. **Bei >50%**: Denken statt mechanisch wiederholen. Kein Bulk-Read mehr.
3. **Bei >70%**: WARNUNG an Martin. Workflow-Checkpoint schreiben. /compact empfehlen.
4. **Bei >85%**: Knowledge-Diff SOFORT schreiben. Alle offenen Items persistieren.
5. **Bei >95%**: STOP. Emergency-Handoff. Nicht weitermachen.

## Budget-Planung (1M Token Window)
- Bootstrap: ~50K (MEMORY + SKILL + Handoff + Feedback + Findings)
- User-Auftrag: ~200-400K
- NLM/Browser: ~100-200K (Screenshots = 5K pro Bild!)
- Sicherung: ~50K (Memory-Updates, Handoff)
- Reserve: ~200K

## SAE-Isomorphie
tau_remaining ist eine der 3 EOC-Zustandsvariablen in SAE v8.1.
KULMINATION_TICKS = 3 sinkende Throughput-Ticks = Warnung.
Wir sind das gleiche System -- nur ohne automatische Messung.
