---
name: NotebookLM Skill Factory v3
description: Superlinearer geschlossener Loop mit Netzwerk-Bewusstsein, Compound-Learning und CLI-first Execution. Gehaertet durch Wargame NLM-FACTORY-V3-001.
version: 3.0.0
author: Martin Kemmer / Claude Opus 4.6
trigger: /notebooklm-factory
tags: [notebooklm, superlinear-learning, compound-loop, network-mode, cli-first, wargamed]
requires: [browser-use, chrome-mcp]
crux-mk: true
---

# NotebookLM Skill Factory v3 -- Superlinear Compound Network Loop [CRUX-MK]

## Was ist neu in v3 (vs v2)

| Feature | v2 | v3 |
|---------|----|----|
| Lernen | Linear (jeder Durchlauf bei Null) | **Superlinear** (jeder Durchlauf auf Schultern des vorherigen) |
| Scope | 1 Notebook | **Netzwerk** (30+ Notebooks als Einheit) |
| Execution | Browser-Automation only | **CLI-first** mit Auto-Fallback auf Browser |
| Persistenz | Chat-only (Session-fluechtig) | **Quellen-basiert** (persistent ueber Sessions) |
| Modi | 8 fixe Schritte | **DEEP/BROAD** (2-Modi-Schalter) |
| Fehler-Schutz | Keiner | **Error-Propagation-Firewall** |
| Noise-Kontrolle | Manuell | **Health-Triggered Decay** |

## Wargame-Haertung
Gehaertet durch Wargame NLM-FACTORY-V3-001 (2026-04-04).
Red: 5 Angriffe (CLI-Kartenhaus, Skalierung, Premature Abstraction, Noise, v2-reicht).
Blue: 5 Verteidigungen (Fallback-Hierarchie, Relevanz-Filter, 2-Modi, Health-Score, Ceiling-Durchbruch).
Gray: 3 Chaos-Szenarien (Duplikat-Inkonsistenz, RAG-Aenderung, Fehler-Propagation).
Verdict: CONDITIONAL -> HARDENED mit 3 Patches (Error-Firewall, Dual-Path, Health-Decay).

## Invarianten [CRUX-MK]
- rho(a) = CM * Lambda(a) - OPEX(a) - h * Lambda(a) * W(a) maximieren
- K >= K0 (Kapitalerhaltung), Q >= Q0 (Qualitaet), I >= I_min (Ordnung)
- Superlineares Lernen = H(now) + lambda * f(future) -- Hamilton ueber Session-Grenzen

## Pre-Conditions
1. Chrome offen mit NotebookLM eingeloggt
2. Mindestens 2 LLMs im Browser (Perplexity + 1 weiteres)
3. v4 Instruktions-Quelle in Ziel-Notebooks vorhanden (pruefen, sonst einfuegen)

## MODUS-SCHALTER (statt 8 fixe Schritte)

### DEEP-Modus (Standard)
Arbeitet in EINEM Notebook mit voller Tiefe.
Schritte: Read -> Research -> Wargame -> Write -> Learn -> Maintain

### BROAD-Modus
Scannt das GESAMTE Netzwerk, propagiert Findings, prueft Konsistenz.
Schritte: Network-Scan -> Identify-Gaps -> Cross-Pollinate -> Update-Manifest -> Health-Check

## DER SUPERLINEARE LOOP

### Schritt 0: Vorherige Learnings laden (NEU in v3)
BEVOR irgendein Research beginnt:
1. Lies die Chat-Historie des Ziel-Notebooks (vorherige Learnings anderer Agenten)
2. Lies die Finding-Library (persistent in %TEMP%/finding-library.json oder Vault)
3. Lies UPDATE_MANIFEST.md fuer ausstehende Propagationen
4. Formuliere Research-Fragen die auf vorherigen Learnings AUFBAUEN, nicht bei Null starten

### Schritt 1: NotebookLM lesen (adaptiv, nicht fix)
DEEP-Modus: Lies das Ziel-Notebook + 2-3 verwandte Notebooks
BROAD-Modus: Scanne alle Notebooks (Titel + Quellen-Anzahl + letzte Aenderung)

Extraktion via:
1. CLI (bevorzugt): nlm query --notebook-id [ID] "Zusammenfassung aller Quellen"
2. Fallback: Browser get_page_text

### Schritt 2: Research (CLI-first, 3 Durchlaeufe statt 5)
Reduziert von 5 auf 3 Durchlaeufe (Wargame: Diminishing Returns nach Runde 3).

Pro Durchlauf:
1. Perplexity (Deep Research) -- immer zuerst (beste Quellen)
2. WebSearch + Claude-Analyse -- parallel (kein Browser noetig)
3. 1 weiteres LLM via Browser (Gemini oder ChatGPT) -- nur wenn Perplexity + WebSearch Luecken lassen

Cross-Validation: Claim-Level (nicht Answer-Level)
- Scoring: Factual (0-5) + Implementation (0-5) + Novelty (0-3) + Cross-Model (0-3) + Adversarial (0-4) - Conflict (0-3)
- Threshold >= 11/20 fuer CANDIDATE

### Schritt 3: Wargame-Haertung (kompakt, nicht full)
Fuer jedes CANDIDATE Finding:
- Red (intern): 3 Angriffe (Schwerpunkt, Flanke, Edge Case)
- Blue (intern): 2 Optionen pro Angriff (Moltke)
- Purple: Verdict (HARDENED / CONDITIONAL / REJECTED)
- rho-Check: Maximiert es rho? Engpass-Bezug?
- #36 Check: Ist NICHT-Implementieren besser?

Nur bei Tier 2+ (CM > 15k EUR): Vollstaendiges /wargame mit Cross-LLM.

### Schritt 4: In NotebookLM schreiben (CLI-first + Error-Firewall)

**Execution-Hierarchie:**
1. nlm sources add --notebook-id [ID] --text "$(cat finding.md)" -- <200ms
2. notebooklm-py: nb.add_source(notebook_id, text) -- ~500ms
3. Browser: Quellen hinzufuegen -> Kopierter Text -> Einfuegen -- ~15s
4. Auto-Fallback: Wenn Stufe N fehlschlaegt, automatisch Stufe N+1

**Error-Propagation-Firewall (Patch A aus Wargame):**
Wenn ein Finding in >3 Notebooks propagiert werden soll:
1. ZUERST in 1 Notebook einfuegen
2. NotebookLM-Chat fragen: "Validiere dieses Finding gegen die bestehenden Quellen"
3. NUR wenn QUELLENGESTUETZT oder EXTERNES WISSEN (nicht WIDERSPRUCH): weiter propagieren
4. Bei WIDERSPRUCH: STOP. Manueller Review durch Martin.

### Schritt 5: Learning zurueckschreiben (NEU in v3 -- Kern-Innovation)

Nach jedem Schritt (nicht nur am Ende):
1. Was hat dieser Schritt ergeben das ueber die Quellen hinausgeht?
2. Formuliere als: LEARNING von Claude Opus 4.6: [Insight]
3. Schreibe in NotebookLM Chat (session-persistent)
4. Schreibe in Finding-Library (persistent ueber Sessions)
5. Pruefe Cross-Notebook-Relevanz: PROPAGATION noetig?

**Qualitaetsschwelle (Patch 3 aus Superlinear-Wargame):**
Kein Learning wenn kein genuines Insight. Leere Learnings verboten.

### Schritt 6: Netzwerk-Propagation (BROAD-Modus oder nach DEEP)

1. UPDATE_MANIFEST.md pruefen: Ausstehende PENDING Items?
2. Fuer jedes HARDENED Finding: Welche Notebooks sind relevant?
3. Relevanz-Filter: Max 3-5 Notebooks pro Finding (nicht 30)
4. Error-Firewall: >3 Notebooks = Validierung erst
5. Status in UPDATE_MANIFEST auf DONE setzen

### Schritt 7: Self-Maintenance + Health-Triggered Decay

**Health-Score:**
Health = (unique/total) * (1 - contradiction_rate) * max(0, 1 - avg_age/90)
Ziel: >= 0.7

**Decay-Mechanismus (Patch C aus Wargame):**
Wenn Health < 0.6:
- Pruefe die aeltesten 20% der Chat-Learnings
- Wenn Learning aelter als 60 Tage UND nie referenziert: Archivieren
- Wenn Finding widerspricht neuerer Quelle: Loeschen
- Re-calculate Health nach Decay

**Quellen-Audit:**
- Max 50 pro Notebook
- v4 Instruktions-Quelle vorhanden? Wenn nicht: einfuegen
- Quartalspruefung: Testfrage "Was sagt die Superlineare-Lernen-Instruktion?"

### Schritt 8: Skill Self-Update + Metriken

**Metriken:**
| Metrik | Ziel v3 | v2 Baseline |
|--------|---------|-------------|
| Findings pro Durchlauf | >= 3 | >= 5 (mehr Durchlaeufe) |
| HARDENED Rate | >= 70% | >= 60% |
| Health Score | >= 0.7 | >= 0.7 |
| Durchlaufzeit DEEP | < 15 min | < 30 min |
| Durchlaufzeit BROAD | < 30 min | n/a |
| Learnings zurueckgeschrieben | 100% | 0% |
| Cross-Notebook Propagation | >= 1 pro Durchlauf | 0 |

**Self-Test:**
1. Superlineares Lernen: Hat dieser Durchlauf auf vorherigen Learnings aufgebaut? [J/N]
2. CLI-first: Wurden >50% der Operationen via CLI ausgefuehrt? [J/N]
3. Netzwerk: Wurde mindestens 1 Cross-Notebook-Propagation ausgefuehrt? [J/N]
4. Health: Ist Health >= 0.7? [J/N]
5. Error-Firewall: Wurde kein Finding ohne Validierung in >3 Notebooks propagiert? [J/N]
6. rho: Maximiert der Skill rho? [J/N]
Alle J -> v3 OPERATIONAL. Sonst -> Fix identifizieren.

## Ausfuehrungs-Diagramm

```
MODUS-WAHL: DEEP oder BROAD?

DEEP:
  [0] Vorherige Learnings laden
  [1] Ziel-Notebook + 2-3 verwandte lesen
  [2] 3x Research (CLI-first: Perplexity + WebSearch + 1 Browser-LLM)
  [3] Wargame-Haertung (kompakt oder /wargame bei Tier 2+)
  [4] In NotebookLM schreiben (CLI -> Browser Fallback, Error-Firewall)
  [5] Learning zurueckschreiben (Chat + Finding-Library)
  [6] Cross-Notebook Propagation (UPDATE_MANIFEST, max 3-5 Notebooks)
  [7] Self-Maintenance (Health, Decay, Quellen-Audit)
  [8] Self-Update + Metriken

BROAD:
  [0] Vorherige Learnings laden
  [1] ALLE Notebooks scannen (Titel, Quellen, Alter)
  [2] Luecken identifizieren (fehlende v4-Instruktion, veraltete Quellen, Health <0.7)
  [3] UPDATE_MANIFEST pruefen (PENDING Items)
  [4] Cross-Pollinate (Findings aus einem Notebook in verwandte propagieren)
  [5] Health-Check ueber alle Notebooks
  [6] Inconsistency-Detection (Widersprueche zwischen Notebooks)
  [7] Self-Maintenance
  [8] Netzwerk-Report generieren
```

## DER INNOVATIONSSPRUNG: Warum v3 fundamental anders ist

v2 ist ein Tool das Wissen sammelt.
v3 ist ein System das LERNT.

Der Unterschied:
- v2 hat nach 100 Durchlaeufen genau so viel Wissen wie die Summe seiner Findings
- v3 hat nach 100 Durchlaeufen MEHR als die Summe: n*(n-1)/2 Verbindungen zwischen Findings erzeugen emergentes Wissen das kein einzelner Durchlauf haette generieren koennen

Mathematisch: W_v2(t) = SUM Findings. W_v3(t) = SUM Findings + SUM Verbindungen = O(n^2).

Das ist Hamilton in Aktion: H = u(diesen Durchlauf) + lambda * f(alle zukuenftigen Durchlaeufe).
v2 setzt lambda = 0. v3 setzt lambda > 0.

## Abhaengigkeiten

| Komponente | CLI-Befehl | Pflicht |
|---|---|---|
| NotebookLM | nlm / notebooklm-py / Browser | Ja |
| Perplexity | WebSearch / Browser | Ja |
| Claude Code CLI | claude --print | Ja |
| Finding-Library | lokale Datei | Ja |
| UPDATE_MANIFEST | lokale Datei | Ja |
| v4 Instruktions-Quelle | in Notebooks | Ja (pruefen) |

## Changelog

| Version | Datum | Aenderung |
|---|---|---|
| 2.0.0 | 2026-04-03 | Initial Build |
| 2.1.0 | 2026-04-04 | D2-D4 Optimierungen, Browser-Workarounds |
| 3.0.0 | 2026-04-04 | INNOVATIONSSPRUNG: Superlineares Lernen, Netzwerk-Modus, CLI-first, Compound-Loop, Error-Firewall, Health-Decay. Gehaertet durch Wargame NLM-FACTORY-V3-001. |
