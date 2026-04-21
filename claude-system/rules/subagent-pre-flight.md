# Subagent Pre-Flight Check [CRUX-MK]

**Zweck:** Verhindert Eigenfehler EF-5 (Chrome-MCP-Optimismus ohne Pilot-Test).
Jeder Subagent der Browser-MCP oder externe APIs nutzt, durchlaeuft vor Start einen Pre-Flight.

## Regel

Vor Subagent-Start mit folgenden Tools-Kategorien:

### Browser-MCP (Claude_in_Chrome, Claude_Preview, firecrawl-instruct)

Pflicht-Checks:
1. **Screenshot-Limit:** Wenn Flow Screenshots benoetigt → max 5 Screenshots pro Session, danach Text-Extraktion
2. **Bevorzugt:** `get_page_text` / `read_page` statt `preview_screenshot` fuer Daten-Extraktion
3. **Login-Status:** Wenn Login benoetigt → Test-Flag im Prompt ("bei Login-Bedarf STOP")
4. **Rate-Limit:** Wenn externe Seite (NotebookLM, Gmail, etc.) → 2-5s Pause zwischen Actions
5. **Pilot vor Batch:** Ein Notebook / eine Seite / ein Flow testen, bevor 5+ parallel

### Externe APIs (Firecrawl, MCP-Server mit Kosten)

Pflicht-Checks:
1. **Cost-Cap:** Max 5 EUR pro Subagent-Run hardcoded
2. **Fallback:** Bei API-Fehler → Drive-Cache / lokale Dateien als Plan B
3. **Idempotenz:** Wenn Run abbricht, nicht von vorne beginnen

## Historischer Eigenfehler (Quelle der Regel)

Session 2026-04-17, Meta-Lern-Pilot-Subagent:
- Chrome-MCP-basierter NLM-Chat gestartet ohne Screenshot-Limit-Check
- Nach 16 Min / 98 Tool-Uses Abbruch: "image exceeds dimension limit (2000px)"
- 0 produktiver Output, verlorener Subagent-Slot
- Learning: Edge Cases vor Batch-Start pilot-testen

## Mechanisch

Bei jedem Subagent-Prompt mit Browser-MCP oder externen APIs:

```
VOR Mission:
  Pre-Flight-Checkliste pruefen:
  [ ] Screenshot-Limit beachtet?
  [ ] Text-Extraktion bevorzugt?
  [ ] Login-Bedarf gecheckt (STOP-Flag)?
  [ ] Rate-Limit-Pause eingebaut?
  [ ] Pilot-Modus fuer erste Action?
```

Wenn eine Box nicht erfuellt: Prompt verbessern, NICHT Subagent starten.

## CRUX-Bindung

- K_0: Schutz vor Budget-Verschwendung (API-Kosten)
- Q_0: Schutz vor Martin-Zeit-Verschwendung durch failed Subagenten
- I_min: Strukturierter Pre-Flight statt Ad-hoc-Start
- MHC: Martin kann jederzeit STOP senden

[CRUX-MK]
