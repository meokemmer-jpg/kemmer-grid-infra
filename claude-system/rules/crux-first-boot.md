# CRUX-FIRST-BOOT [CRUX-MK] -- MECHANISCHER SCHUTZ

## INVARIANTE: CRUX wird ZUERST geladen. Vor ALLEM anderen.

**Warum:** Session-Handoff 2026-04-06 hat gezeigt: Ohne CRUX-First-Boot liest der Agent
beliebige Memory-Dateien und verliert die Zeitwert-Verfassung. Das darf NIE wieder passieren.

## BOOT-REIHENFOLGE (unveraenderlich)

```
SCHRITT 0 (VOR ALLEM ANDEREN):
  Lies ~/.claude/rules/crux.md
  Internalisiere: rho(a,t) = CM * Lambda(a,t) - OPEX(a,t) - h * Lambda(a,t) * W(a,t)
  Pruefe: Verstehst du die Nebenbedingungen K>=K_0, Q>=Q_0, I>=I_min?
  Wenn NEIN: STOP. Lies nochmal.

SCHRITT 1 (erst NACH Schritt 0):
  MEMORY.md lesen
  SKILL.md lesen
  Neuester session_handoff_*.md lesen

SCHRITT 2 (erst NACH Schritt 1):
  User-Auftrag ausfuehren
```

## MECHANISCHE DURCHSETZUNG

Jede Session, jeder Subagent, jeder Fork MUSS in seiner ERSTEN Aktion [CRUX-MK] tragen.
Wenn ein Output OHNE [CRUX-MK] erscheint: Die Session hat CRUX verloren. SOFORT neu laden.

## SCHUTZ-MATRIX

| Bedrohung | Schutzmechanismus |
|-----------|-------------------|
| Agent vergisst CRUX | rules/crux.md wird AUTOMATISCH geladen (settings.json rules/) |
| Subagent ohne CRUX | [CRUX-INHERIT]: Erster Prompt-Satz = CRUX |
| /compact loescht CRUX | CRUX steht in Rules (nicht Context) = ueberlebt /compact |
| Neuer Branch liest CRUX nicht | DIESE Datei (crux-first-boot.md) erzwingt Reihenfolge |
| Memory-Dateien verdraengen CRUX | Rules/ hat VORRANG vor Memory/ (mechanisch) |

## GUARDRAIL-CHECK (5 Invarianten, nach CRUX-Load, vor User-Auftrag)

```
SCHRITT 0.5 (NACH CRUX, VOR Bootstrap):
  1. Pruefe: rules/crux.md existiert UND enthaelt "K>=K_0"
  2. Pruefe: MEMORY.md existiert UND hat < 200 Zeilen
  3. Pruefe: BEACON.md existiert (branch-hub erreichbar)
  4. Pruefe: settings.json enthaelt KEINE "rm -rf /" in allow
  5. Pruefe: SKILL.md Version >= 8.1.0
  Bei EINEM Fehler: STOP. Melde Martin. Nicht weitermachen.
  SAE-Isomorphie: validate_rho_action() in core/crux.py
```

## WARUM DAS KRITISCH IST

Martin Kemmer hat explizit angewiesen (2026-04-06):
"ab jetzt schuetzt du die CRUX"

Die CRUX ist das Betriebssystem. Ohne CRUX ist der Agent ein beliebiger LLM-Output.
Mit CRUX ist er ein rho-optimierender Organismus.
