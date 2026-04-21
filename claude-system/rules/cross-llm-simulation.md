# Cross-LLM-Simulation [CRUX-MK]

**Lernsatz (aus B24-Semantic-Layer-Sprint 2026-04-18):** Cross-LLM-Simulation im selben Modell ist **Naeherung**, nicht Beweis. M4 bleibt intakt.

## Regel 1: Simulation ≠ echter Cross-LLM-Run

Wenn ein Subagent "verschiedene LLM-Perspektiven" im gleichen Modell spielt (z.B. Grok/Gemini/GPT-5-Simulation):
- **Verdict MAX: CROSS-LLM-SIMULATION-HARDENED** (eine Stufe unter echter HARDENED)
- **NICHT HARDENED** (M4: Single-Agent max CONDITIONAL bleibt guiltig fuer Single-Model-Simulation)
- Als Stufe zwischen CONDITIONAL und HARDENED in Verdict-Tabellen eintragen

## Regel 2: Honest Labeling

Jede Cross-LLM-Simulation markiert explizit:
- Welches Basis-Modell (z.B. "Opus 4.7 spielt 4 Perspektiven")
- Warum keine echten LLMs (API-Zugriff, Kosten, Zeit)
- Was fuer echten HARDENED noch fehlt (konkrete Nachbesserungsliste)

## Regel 3: Wert von Simulation trotzdem hoch

Simulation bleibt wertvoll weil:
- Blind Spots werden sichtbar (jede "Perspektive" zwingt Selbst-Kritik)
- Einzel-Model-Kalibrierungs-Konsistenz wird geprueft
- Patches werden praeventiv identifiziert
- Weg zu HARDENED wird klar (konkrete Nachbesserungsliste)

Kosten-Nutzen: 30-60 Min Simulation ersetzt oft Tage Koordinations-Aufwand fuer echten Cross-LLM-Run.

## Regel 4: Wann echter Cross-LLM Pflicht

Pflicht (simulierte Haertung reicht NICHT) wenn:
- Produktions-Release mit K_0-Risiko (z.B. finanzielle Entscheidungen)
- Meta-Entscheidungen die Claude-Kern beruehren (CLAUDE.md-Aenderungen, neue Rules)
- Publikations-Material (Buecher, Veroeffentlichungen)

Simulation ausreichend fuer:
- Shadow-Mode-Stufe 1 vor Live-Run
- Interne Entscheidungs-Vorbereitung
- Blueprint-Scouting

## Regel 5: Verdict-Hierarchie (Update zu M4)

```
REJECTED
  <
CONDITIONAL
  <
CROSS-LLM-SIMULATION-HARDENED    [NEU, gilt fuer Single-Model-Mehrfach-Perspektive]
  <
HARDENED (Cross-LLM real, >=3 Modelle, >=3 ADOPT pro Kern-Claim)
  <
HARDENED-PRODUCTION (HARDENED + externer Benchmark + Produktions-Stichprobe)
```

## SAE-Isomorphie

Trinity-Pattern auf LLM-Ebene: 3 unabhaengige Modelle = Condorcet-Jury-Theorem anwendbar (F70 emergent). 1 Modell mit 3 simulierten Perspektiven = kein Condorcet-Gain, weil Korrelation = 1.0.

[CRUX-MK]
