# CRUX-MK — Layer 0 der Kemmer-Grid-Architektur

**Status:** OBERSTE INVARIANTE. Nicht verhandelbar. Wird in jedem Bootstrap, jedem Script, jedem Commit, jedem LLM-Call geprueft UND aktiv optimiert.

---

## Die Zielfunktion

```
max  INTEGRAL_{t=0}^{T_life}  [ rho(a,t) * L(t) ]  dt

=  Vermoegen der Familie Kemmer * Lebensqualitaet ueber Lebenszeit
```

### Variablen

- **rho(a,t)** = CM * Lambda(a,t) - OPEX(a,t) - h * Lambda(a,t) * W(a,t)
  - CM = Deckungsbeitragsmarge
  - Lambda(a,t) = Engpass-Durchsatz (TOC: min{D, mu_b(a)})
  - OPEX(a,t) = operative Kosten
  - W(a,t) = gebundenes Working Capital
  - h = Zeitwert-/Kapitalkostensatz
- **L(t)** = Lebensqualitaets-Faktor [0,1] (Gesundheit, Familie, Freiheit)
- **T_life** = Lebenserwartung (zu MAXIMIEREN, nicht fixiert)

### Harte Nebenbedingungen (invariant)

1. **K >= K_0** (Kapitalerhaltung) — kein Substanzverzehr
2. **Q >= Q_0** (Qualitaetsinvarianz) — keine Degradation von Familie/Marke/Prozess/Info
3. **I >= I_min** (Ordnungsminimum) — IT, Prozesse, Doku, Governance

Verletzung einer Nebenbedingung = **automatisches No-Go**, unabhaengig von rho.

---

## Layer-0-Status: Was das fuer das Grid bedeutet

### Prinzip 1: Jede Aktion wird CRUX-gepruef

Jede Aktion dieses Grids (Bootstrap, LLM-Call, Commit, Install, Delete, Migrate) muss CRUX passieren:

1. Erhoet dies rho? (Vermoegen)
2. Erhoet dies L? (Lebensqualitaet)
3. Haelt es K_0, Q_0, I_min?
4. Wurde es durch 2 Wargames gehaertet? ([CRUX-GATE])
5. Wenn NEIN bei 1-3: **REJECT.** Sofort.

### Prinzip 2: Jeder Sub-Agent/Sub-Skill vererbt CRUX

[CRUX-INHERIT]: Keine Ausnahme. Kein Skill ohne CRUX-Marker, kein Agent-Prompt ohne CRUX-Header, kein Script ohne CRUX-Check.

### Prinzip 3: Aktives Zuarbeiten, nicht nur Nicht-Verletzen

CRUX ist kein Negativ-Filter. CRUX ist **Ziel-Funktion**. Jede Bootstrap-Phase fragt aktiv:
- Welches rho-Delta liefert diese Aktion?
- Welches L-Delta?
- Welches T_life-Delta (langfristig)?

Wenn Antworten nicht quantifiziert werden koennen: Aktion ist unbegruendet.

---

## Implementierung im Grid-Repo

### 1. `scripts/crux-check.sh` / `.ps1`

Kern-Script. Wird aufgerufen:
- Als erste Aktion in `grid-bootstrap.sh/.ps1`
- Als pre-commit-Hook
- Als pre-LLM-call-Hook in LiteLLM-Router
- Als PreToolUse-Hook in `~/.claude/settings.json`

Output: `crux-events.jsonl` in `~/.kemmer-grid/`

Exit-Codes:
- 0 = passed (rho positiv, K_0/Q_0/I_min erhalten)
- 1 = REJECT (Nebenbedingung verletzt)
- 2 = WARN (rho unklar, Martin-Review)

### 2. Manifest-Pflichtfelder

Jedes Manifest hat:

```json
{
  "crux_mk": true,
  "crux_version": "v1.0",
  "crux_impact": {
    "rho_estimate_eur_per_year": "...",
    "k0_risk": "none|low|medium|high",
    "q0_risk": "none|low|medium|high",
    "i_min_contribution": "positive|neutral|negative",
    "l_martin_impact": "positive|neutral|negative",
    "t_life_impact_days": 0,
    "wargame_status": "none|adversarial_passed|alignment_passed|both_passed"
  }
}
```

### 3. Script-Header-Pflicht

Jedes Script (ps1/sh/py) beginnt mit:

```bash
# [CRUX-MK] Layer 0
# rho-Impact:         <estimation>
# K_0/Q_0/I_min:      <erhalten|verletzt>
# Wargame-Status:     <none|adversarial|alignment|both>
# Referenz:           CRUX-MK.md
source "$(dirname $0)/crux-check.sh" || exit 1
```

### 4. Commit-Pflicht

Jede Commit-Message hat:
- `[CRUX-MK]` im Body (nicht Titel)
- `rho-impact: <estimate>` in Footer
- `wargame: <status>` in Footer

Git-Pre-Commit-Hook erzwingt das.

### 5. PR-Template

Pull-Requests haben in Description:

```
## CRUX-Impact
- rho-Delta: +X EUR/J
- K_0: geschuetzt / betroffen: ...
- Q_0: geschuetzt / betroffen: ...
- I_min: erhoeht / neutral / reduziert
- L_Martin: erhoeht / neutral
- T_life: +X Tage / neutral
- Wargame: none / adversarial / alignment / both

## CRUX-Gate-Entscheidung
- [ ] rho positiv
- [ ] Nebenbedingungen erhalten
- [ ] 2-Wargame (wenn substantiell)
- [ ] Martin-Phronesis (wenn K_0/Q_0)
```

### 6. Rho-Live-Tracking

Jeder LLM-Call in LiteLLM-Router wird mit:
- `criticality_score` (0-1)
- `rho_estimate_eur` vor Call
- `rho_realized_eur` nach Call (durch MED-Tripel + Outcome)
- Delta wird in `~/.kemmer-grid/rho-tracking.jsonl` geloggt

Weekly: Aggregation in Martin-rho-Dashboard.

---

## Relation zu bestehenden Rules (Drive-G)

Die CRUX-Layer-0-Verankerung im Grid-Repo ergaenzt (superseded NICHT) folgende Rules:

- `claude-system/rules/crux.md` — Kern-Invariante
- `claude-system/rules/crux-first-boot.md` — Boot-Protokoll mit CRUX-First
- `claude-system/rules/crux-gate-grenzen.md` — Meta-Grenzen fuer CRUX-Anwendung
- `claude-system/CLAUDE.md §0` — CRUX-MK Definition

**Bei Konflikt:** Diese CRUX-MK.md gewinnt im Grid-Context, die Rules gewinnen im Claude-Session-Context. Keine Divergenz zulaessig — bei Divergenz-Detect: Martin-Alert.

---

## Live-Beispiel: Wie crux-check.sh arbeitet

```bash
$ ./scripts/crux-check.sh --action "install ollama" --estimated-rho "+10-30 EUR/M (local-inference cost savings)"

[CRUX-MK] Layer-0-Check
  Action:           install ollama
  rho-Estimate:     +10-30 EUR/M
  K_0-Risk:         low (Cash-Out ca €0, brew)
  Q_0-Risk:         none
  I_min-Impact:     positive (lokale Inferenz = mehr Souveraenitaet)
  L_Martin-Impact:  positive (weniger Cloud-Abhaengigkeit = mentale Last reduziert)
  Wargame-Status:   adversarial_passed (Loopback-Audit Masterplan v2)

VERDICT: PASS
Logged: ~/.kemmer-grid/crux-events.jsonl
Proceed with action.
```

Bei Verletzung:

```bash
$ ./scripts/crux-check.sh --action "push directly to main" --estimated-rho "unclear"

[CRUX-MK] Layer-0-Check
  Action:           push directly to main
  rho-Estimate:     unclear - REJECT
  K_0-Risk:         high (240+ commits ahead, potential destructive)
  I_min-Impact:     negative (umgeht GitHub-Primaer-Fixpunkt-Rule MR-5)

VERDICT: REJECT - Nebenbedingung verletzt
Action: HALT. Martin-Phronesis erforderlich.
Exit-Code: 1
```

---

## Bootstrap-Reihenfolge mit CRUX-Layer-0

```
Stage 0: CRUX-INHERIT-CHECK
  └─ crux-check.sh --stage 0 --assertion "Bootstrap-Absicht CRUX-aligned?"
     Wenn FAIL: HALT.

Stage 1: Pre-Flight
  └─ pre-bootstrap-check.sh (enthaelt CRUX-Header-Scan aller Grid-Files)

Stage 2: Capability-Gate
  └─ golden-task-suite.json Test T00 = CRUX-Check-Pass auf allen bisherigen Aktionen

Stage 3: Install-Konvergenz
  └─ Jede Install-Aktion: crux-check.sh VORHER
     Wenn rho-negativ oder K_0-Risk: HALT.

Stage 4: Attestation
  └─ state-attestation.json enthaelt crux_impact-Block pro Installations-Schritt

Stage 5: Master-Handshake
  └─ Inbox-Message an Master enthaelt CRUX-Bilanz
```

---

## Naechste Schritte (Phase A Woche 1 Start)

1. `scripts/crux-check.sh` + `.ps1` schreiben (Kern-Logik)
2. Alle bestehenden Scripts/Manifeste mit CRUX-Header patchen
3. Git-Hook: pre-commit-crux-validator installieren
4. LiteLLM-Router-Pre-Call-Hook fuer CRUX-Check erweitern
5. Golden-Task-T00 zur Suite hinzufuegen
6. README patchen: CRUX als Sektion 0
7. Pre-Bootstrap-Check scannt CRUX-Compliance aller Grid-Files

[CRUX-MK]
