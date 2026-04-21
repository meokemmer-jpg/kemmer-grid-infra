---
name: SAE GUI Excellence
description: 9OS MEGA Interface -- 25 Best Practices + Design System + SAE-Only + Text-Frei + Rechte + Workday
version: 2.0.0
crux-mk: true
triggers:
  - /gui-excellence
  - /gui-best-practices
  - /sae-gui
  - /9os
---

# SAE GUI Excellence Skill v2.0.0 [CRUX-MK]

## Kontext
7 HeyLou Hotels, 600 AI-Agenten (SAE v8.0), ~49 Human-Agenten (GSAs), 7 FTE/Hotel.
**SAE ist das MVP. GUI ist der USP. GSA nutzt NUR die SAE (kein MEWS/PMS-Zugang).**
2 Wargames gehaertet: GUI-NEXTGEN-001 (psychologische Architektur) + GUI-EXCELLENCE-002 (World-Class Standards).
Findings: `branch-hub/findings/GUI-NEXTGEN-001-WARGAME-2026-04-11.md` + `GUI-EXCELLENCE-002-WARGAME-2026-04-11.md`

## Die 5 Ebenen der GUI-Excellence

```
Ebene 5: FREUDE     -- Joy of Use ("ich WILL die App oeffnen")
Ebene 4: PRAEZISION -- IBCS, Gestalt, i18n (professionelle Darstellung)
Ebene 3: KOMPETENZ  -- Progressive Disclosure, Nielsen, Undo (GUI waechst mit Nutzer)
Ebene 2: ZUGANG     -- Voice, Smartwatch, Ambient (GUI findet den GSA)
Ebene 1: VERSTAENDNIS -- Semantic Data Layer (Zahlen die sofort Sinn machen)
```

Jede Ebene baut auf der vorherigen auf. Ohne Verstaendnis kein Zugang. Ohne Zugang keine Kompetenz.

## Kern-Architektur

### Shelf + Stage (aus psychologischer Forschung)
- **Shelf (obere 40%):** Immer sichtbar, nie scrollbar, max 7 Items (Millers Law)
- **Stage (untere 60%):** Scrollbar, vollstaendiger Kontext
- **KRITISCH:** Shelf ist TAB-UEBERGREIFEND (Best Practice #1). Shelf wechselt NIE bei Tab-Wechsel.

### 3-Tab-Struktur (psychologische Zugehoerigkeit)
- Heart: Deine Gaeste (Empathie-Modus)
- Circle: Dein Tag (Aufgaben-Modus)
- Gear: Dein Haus (Analyse-Modus)

### Kern-Formeln
```
GUI_Value = Information / CognitiveLoad
Motivation = (Klarheit x Sichtbarer_Erfolg) / Komplexitaet
Hick's Law: RT = a + b * log2(n+1)
```

## 25 Gehaertete Best Practices

### Ebene 0: Fundament (aus WG-001)

| # | Best Practice | Wargame-Haertung |
|---|---|---|
| 1 | **Shelf ist tab-uebergreifend** -- obere 40% wechseln NIE bei Tab-Wechsel | R3: Tab-Wechsel-Kosten. Shelf = globaler Anker |
| 2 | **Confidence-Score auf jedem Shelf-Item** (visueller Balken 0-100%) | R1: Shelf-Kontamination. Transparenz = Vertrauen |
| 3 | **1-Tap Feedback** ("stimmt"/"stimmt nicht") auf Shelf-Items | R1: GSA wird Co-Kalibrierer des Agents |
| 4 | **Timer kontextadaptiv** -- Front Desk: 10s/kein Timer, Back Office: 30s | R2: Sozialer Druck am Counter. Kontext > Universalregel |
| 5 | **Next Play zeigt 3 Optionen ab Level L2** -- L1 bekommt 1 Empfehlung | R5: Learned Helplessness. Kompetenz waechst mit Autonomie |
| 6 | **Shape-Coding neben Farb-Coding** (Kreis/Dreieck/X + Gruen/Orange/Rot) | R4: 8% Farbblindheit. WCAG ist Minimum nicht Maximum |
| 7 | **Offline-Cache fuer Shelf** (letzte 15 Min Daten lokal) | Gray: Schichtwechsel + API-Timeout = App ignoriert |
| 8 | **Progressive Notification-Reduktion** (weniger Toasts mit steigendem Level) | Gray: Peak-End kippt zu Noise nach Woche 12 |
| 9 | **Outcome-Tracking statt Activity-Tracking** fuer Next Play Metriken | Gray: Goodhart's Law -- GSAs gamen Activities |
| 10 | **Ambient-GUI** -- Lobby-Screen + Smartwatch + Audio-Cue | Ku: Physische Verfuegbarkeit. GUI findet den GSA |
| 11 | **Monatlicher Autonomy Day** ohne Next Play (Kompetenz-Test) | Bismarck: Rueckzugsweg offen halten |
| 12 | **Empirische Kalibrierung vor Rollout** (2 Wochen Pilot, Eye-Tracking) | Chi: Alle Formeln sind unkalibriert. Theorie != Praxis |

### Ebene 1: VERSTAENDNIS (aus WG-002)

| # | Best Practice | eta-Rang |
|---|---|---|
| 13 | **Semantic Data Layer:** Jede Zahl = Wert + Richtung + Vergleich + Handlungsimpuls. Nie eine nackte Zahl. Beispiel: "78% Belegung -- +12% vs. gestern -- Upsell-Fenster offen" | 2 |

### Ebene 2: ZUGANG (aus WG-002)

| # | Best Practice | eta-Rang |
|---|---|---|
| 14 | **"Hey Lou" Voice Layer:** Wake-Word, Task-Completion via Voice, Proactive Alerts via Earbud. Backend: Whisper STT → SAE Router → TTS | 1 |
| 15 | **Smartwatch als Output-Kanal:** Vibration + 1-Zeile Text fuer Housekeeping/Maintenance. Kein Smartphone noetig fuer 80% der Tasks | 1 |
| 16 | **Voice-Confirmation:** Jedes Voice-Command bekommt visuelle Bestaetigung auf Smartwatch (verhindert Fehlinterpretation) | 1 |
| 17 | **Privacy-Zonen fuer Voice:** Voice nur in Staff-Bereichen oder via Earbud-Whispering. Nie in Gaeste-Naehe ohne Earbud | 1 |

### Ebene 3: KOMPETENZ (aus WG-002)

| # | Best Practice | eta-Rang |
|---|---|---|
| 18 | **Progressive Disclosure mit Gradient:** L1 sieht 5 Items, L2 sieht 7, L3 sieht alles. Level-Up = 1 neues Element pro Woche (kein Cliff-Edge) | 3 |
| 19 | **Nielsen Compliance Matrix:** Undo-Stack (5 Aktionen), Error Recovery Flows, Contextual Tooltips (Long-Press), Labels unter ALLEN Icons, Shortcuts fuer L3-Power-User | 4 |

### Ebene 4: PRAEZISION (aus WG-002)

| # | Best Practice | eta-Rang |
|---|---|---|
| 20 | **Motion Token System:** 3 Durations (100ms/250ms/400ms), 3 Easings (enter/exit/standard), 3 Haptics (success/warning/error). 60fps Animationen | 5 |
| 21 | **Swipe-Gesten:** Rechts = Erledigt (gruen), Links = Spaeter (grau), Runter = Details | 5 |
| 22 | **IBCS-Light (5 Regeln):** Einheitliche Achsen, Plan=Linie/Ist=Balken, Abweichungen als Wasserfall, keine 3D/Pie, Sparklines inline | 6 |
| 23 | **ICU MessageFormat + CLDR:** Echte Lokalisierung (Plurale, Zahlen, Datum, Waehrung). UI-Grid mit minmax() fuer Text-Expansion | 7 |
| 24 | **Gestalt Design Tokens:** Proximity (8px/24px), Similarity (einheitliche Card-Radius), Continuity (vertikaler Flow), Figure/Ground (Shelf vs Stage Hintergrund), Common Fate (synchrone Animationen) | 8 |

### Ebene 5: FREUDE (aus WG-002 -- NUR nach Pilotbetrieb)

| # | Best Practice | Gray-Haertung |
|---|---|---|
| 25 | **Persoenliche Achievements:** NUR eigener Fortschritt vs. eigene Vergangenheit. NIEMALS Kollegenvergleich. "Du bist schneller als letzte Woche" statt "schneller als Durchschnitt". + Persoenliche Begruessung + Saisonale Farbvariation | Gray Reflexiv: Toxischer Wettbewerb wenn Vergleich |

## Implementation-Sequenz (Moltke: Sequential nach eta)

```
SPRINT 1 (Woche 1-2):   #13 Semantic Data Layer          [eta=15.0, LOW RISK]
SPRINT 2 (Woche 3-10):  #14-17 Voice Layer komplett       [eta=25.0, MEDIUM RISK]
SPRINT 3 (Woche 11-13): #18-19 Disclosure + Nielsen       [eta=5.0-8.3, LOW RISK]
SPRINT 4 (Woche 14-17): #20-21 Micro-Interactions         [eta=3.8, LOW RISK]
SPRINT 5 (Woche 18-20): #22 IBCS-Light                    [eta=3.3, LOW RISK]
SPRINT 6 (Woche 21-26): #23-24 i18n + Gestalt             [eta=1.7-2.0, LOW RISK]
SPRINT 7 (Woche 27+):   #25 Joy of Use (NUR nach Pilot)   [eta=?, HIGH RISK ohne Research]
```

## Design System Referenz

### Farben
```
--color-primary: #006c73 (Teal -- Vertrauen)
--color-accent: #e95d0f (Orange -- Handlungsbedarf)
--color-text: #707070 (nicht Schwarz -- weniger Ermuedung)
--color-bg: #ECEBE8 (Warm Cream -- Premium-Gefuehl)
--color-success: #2E7D32 (Gruen + Kreis-Shape)
--color-warning: #E65100 (Orange + Dreieck-Shape)
--color-error: #C62828 (Rot + X-Shape)
--color-disabled: #9E9E9E (Grau)
```

### Typografie
- Headers: Georgia (elegant, professionell)
- Body: Calibri (lesbar, accessible)
- Monospace: Fuer KPIs/Zahlen (tabellarische Ausrichtung)
- Mindestgroesse: 16px Body, 14px Labels (WCAG)

### Breakpoints
- Mobile: 320-640px (single column, touch-friendly, 48px min touch target)
- Tablet: 640-1024px (two-column)
- Desktop: 1024px+ (full dashboard)

## Psychologische Mechanismen (14, UI-relevant)

| # | Mechanismus | UI-Pattern |
|---|---|---|
| 4 | Mere Exposure | Konsistente Shelf-Struktur ueber alle Tabs |
| 5 | Peak-End Rule | Erfolgs-Feedback bei Task-Completion (gruener Haken + Haptic) |
| 8 | Anchoring | Shelf zeigt Ist-Wert VOR Vergleichswert |
| 11 | Generation Effect | Szenarien-Fragen ("Was wenn 2 Walk-ins?") statt Anweisungen |
| 14 | Contrast Effect | KPI-Boxen immer "Aktuell vs. Vergleich" |

## Wargame-Verdicts
- GUI-NEXTGEN-001: CONDITIONAL (wird HARDENED nach Pilot + Offline-Cache + Shape-Coding)
- GUI-EXCELLENCE-002: CONDITIONAL (wird HARDENED nach Voice-Pilot + Semantic A/B + Gradient-Validierung)

## rho-Estimate
```
Voice: +80k/Jahr (primaerer Kanal, auch fuer Illiterate)
Text Semantik: +30k/Jahr (weniger Interpretationsfehler)
Progressive Disclosure: +25k/Jahr (44% schnellere Entscheidungen)
Nielsen: +20k/Jahr (weniger Support-Anfragen)
Micro-Interactions: +15k/Jahr (Adoption +20%)
i18n: +12k/Jahr (weniger Sprachfehler)
IBCS: +10k/Jahr (bessere Management-Entscheidungen)
Gestalt: +8k/Jahr (schnelleres Lernen)
PMS-Lizenzen: +50k/Jahr (kein User-MEWS-Zugang mehr)
Schulung: +30k/Jahr (1 System statt 5)
Single-Source: +20k/Jahr (keine Daten-Diskrepanzen)
GESAMT: ~300k EUR/Jahr kumuliert
```

## 9OS MEGA Design System
**Code:** `SAE-v8/9os-design-system/tokens.ts` + `animations.ts`

Kern: iPhone-Feeling durch Physik, Weissraum, Praezision, Ueberraschung, Ruhe.
- Teal-Universe (5-stufig: Deep→Core→Bright→Glow→Ghost) + Glassmorphism Shelf
- Inter Display + Tabular Nums (nicht Georgia/Calibri)
- 8px-Raster. Touch: 48-64px. Spring-Animationen (nicht duration-basiert)
- Checkbox: Press→Overshoot→Settle→Haken→Konfetti(letzter)
- Swipe: Friction(0.8)→Threshold(30%)→Snap→Wegfliegen
- Voice-Button: 3 Puls-Ringe→Processing-Arc→Morph-to-Check
- Dark Mode: redesigned (nicht invertiert), Auto-Switch Nachtschicht
- White-Label: Primaerfarbe + Font ueberschreibbar, Status/Spacing/Motion nicht

## SAE-Only Paradigma
GSA nutzt NUR die SAE. Kein MEWS/PMS-Zugang. 1 SAE-Call = N Backend-Calls.
11 neue Endpoints (Check-in, Check-out, Minibar, Wartung, Team-Komm, etc.)
Text-freier DIREKT-Modus: 12 Piktogramme + Voice als primaerer Kanal.
Graceful Degradation 4 Levels + Papier-Notfallplan.

## Rechte-Architektur
5 Rollen (GSA/Manager/Hotel-Owner/Admin/System). 2 GUIs (Hotel-App + Admin-GUI).
User aus Workday (SSO, kein eigenes User-Management).
D4 Mitarbeiter-Performance: Manager NIE individuell, NUR Team-Aggregate (Min. 3 Anwesende).
Voice-Audio: nach STT sofort geloescht. Feedback: anonym.

## Findings (7)
- GUI-NEXTGEN-001-WARGAME-2026-04-11.md
- GUI-EXCELLENCE-002-WARGAME-2026-04-11.md
- GUI-RECHTE-ARCHITEKTUR-2026-04-11.md
- GUI-SAE-VOLLSTAENDIGKEIT-2026-04-11.md
- GUI-RETEST-2O-3O-WORKDAY-2026-04-11.md
- GUI-SAE-ONLY-PARADIGMA-2026-04-11.md
- 9OS-MEGA-DESIGN-SYSTEM-2026-04-11.md

## Changelog
- v2.0.0 (2026-04-11): SAE-Only + Text-Frei + 9OS Design System + Workday + Rechte + 95% SAE-Abdeckung
- v1.0.0 (2026-04-11): Initial aus 2 Wargames (GUI-NEXTGEN-001 + GUI-EXCELLENCE-002)
