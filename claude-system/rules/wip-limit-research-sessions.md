---
name: wip-limit-research-sessions
description: Max 3 gleichzeitige Research-Sessions pro Domain pro Woche zum Schutz der Martin-Bandbreite
type: rule
meta-ebene: E3
status: ACTIVE-MODIFY-v2-PENDING (C1-Wargame 2/3 MODIFY 2026-04-19)
modify-v2-schaerfungen: [Last-basiert statt Session-Count, rolling max 4 mit Carry-over, Auto-Review nach 8 Wochen, Burnout-Failure-Sensitivity]
c1-wargame-finding: branch-hub/findings/FINDING-C1-PROPOSAL-RULES-WARGAME-2026-04-19.md
c1-wargame-detail: branch-hub/cross-llm/2026-04-19-WARGAME-C1-wip-limit-research-sessions.md
created: 2026-04-18
aktiviert: 2026-04-19
cross-llm-reference: branch-hub/cross-llm/2026-04-18-work-d-decision-framework-scale-7-to-30-sessions.md
claim-type: empirical (WIP=3-Limit ist durch L_Martin-Degradation messbar falsifizierbar)
---

# WIP-Limit-Research-Sessions [CRUX-MK] -- PROPOSAL

> STATUS: PROPOSAL. Wird erst zu `wip-limit-research-sessions.md` (ohne `.PROPOSAL`) wenn Martin approve.

## Zweck

Verhindert Options-Flut die Martin-Bandbreite sprengt. Bei Skalierung 7 → 30 Sessions entstehen bei unbegrenzter Research-Parallelisierung pro Domain 10+ gleichzeitige Options-Explorationen. Martin muss alle durchlesen, gewichten, entscheiden. Resultat: L_Martin faellt, Lebensqualitaets-Faktor sinkt, rho-Bindung wird verletzt.

Aus Cross-LLM-Konsens (Codex): **"WIP-Limit ist notwendig fuer Skalierung, ohne explizites Limit wird Research-Output quantitativ aber nicht qualitativ skaliert."**

## Regel

1. **Max 3 gleichzeitige Research-Sessions pro Domain pro Woche**.
2. **Domain-Matrix** (initial, Martin-erweiterbar):
   - Hotel-Tech (MEWS, Workday, RMS, PMS)
   - Medizin/Gesundheit (Labor, Blutpanel, MBSR, Ernaehrung)
   - Steuer/Legal (Wegzugsbesteuerung, E-2, VG Wort, LexVance)
   - Familie (Peak-Season-Protokoll, K4-Skizze, Brueder)
   - Meta-Lern (Cross-LLM, Wargames, Rules, Fixpunkte)
   - Code/SAE (v8, Trinity, Governance, Adapters)
   - Finanzen (KPM, Kapital-Allokation, Kryptographie)
3. **WIP-Counter pro Domain**: REGISTRY.md-Feld `wip_count_by_domain` mit 7-Tages-Rolling-Window.
4. **Pre-Spawn-Check**: Vor Start einer neuen Research-Session:
   - Domain identifizieren
   - WIP-Count pruefen
   - Bei < 3: spawnen erlaubt
   - Bei = 3: EINE alte Session muss promoviert (zu Decision) oder pausiert werden
   - Bei > 3: STOP mit Martin-Alert
5. **Promotion-Pfad**: Research-Session → Decision-Card → WIP-Count sinkt um 1
6. **Pausieren**: Research-Session wird auf `branch-hub/parked/<name>-<date>.md` verschoben, WIP-Count sinkt um 1

## Mechanik

### REGISTRY.md-Erweiterung

```markdown
## WIP-Matrix

| Domain | Aktive Research-Sessions | Count | Schwelle | Status |
|--------|-------------------------|-------|----------|--------|
| hotel-tech | <session1>, <session2> | 2/3 | 3 | OK |
| medizin | <session1>, <session2>, <session3> | 3/3 | 3 | FULL |
| steuer-legal | <session1> | 1/3 | 3 | OK |
...
```

### Pre-Spawn-Skript

```pseudo
def can_spawn_research(domain: str) -> bool:
    wip_count = read_registry_wip(domain)
    if wip_count < 3:
        return True
    elif wip_count == 3:
        candidates = find_promotable_or_pausable(domain)
        if candidates:
            return False  # warten auf Promotion/Pause
        else:
            alert_martin(f"WIP full in {domain}, kein Kandidat")
            return False
    else:
        alert_martin(f"WIP overflow in {domain}: {wip_count}")
        return False
```

### Eskalations-Matrix

- 3/3 in kritischer Domain (K_0/Q_0) ueber 14 Tage: Martin-Alert fuer Domain-Rebalancing
- Chronisch-FULL Domain (>4 Wochen): Domain-Scope ueberpruefen, ggf. aufspalten
- Martin-Override: Bei spezifischem Go-Ahead kann 4. Session gespawnt werden (mit Limit-Ausnahme-Log)

## Anti-Patterns

- **Silent-Overflow**: Session spawnen ohne WIP-Check → verletzt Limit
- **Domain-Creep**: Session beansprucht mehrere Domains um Limit zu umgehen → Scope-Gaming
- **Research-ohne-Promotion-Path**: Session startet als Research, wird nie Decision-Card → blockiert Slot permanent
- **Parkplatz-Flooding**: Massives Pausieren um neue Sessions zu ermoeglichen → verlagert Problem

## SAE-Isomorphie

**200-Slot-Begrenzung**: SAE hat genau 200 Slots, nicht mehr. Hier: 3 Research-Slots pro Domain.

**T_CAP = 50000 Tokens**: Harte Obergrenze pro Agent. Hier: Harte Obergrenze pro Domain-Research-Count.

**Trinity-Promotion**: Challenger → Active → Relegated. Hier: Research → Decision-Card → Archive.

## CRUX-Bindung

- **K_0**: geschuetzt (keine Ueberlast-bedingten Fehl-Entscheidungen durch Martin-Erschoepfung)
- **Q_0**: geschuetzt (Qualitaet der Martin-Reviews erhaelt sich)
- **W_0**: direkt optimiert (Martin-Bandbreite = Primaer-Engpass nach token-engpass-hierarchie.md)
- **L_Martin**: stabilisiert (keine Schlafverlust durch Research-Ueberflutung)
- **rho-Gain**: geschaetzt +80-200k EUR/J durch erhaltene Martin-Review-Qualitaet bei 30-Sessions-Skala

## Falsifikations-Bedingung

Regel ist falsifiziert wenn:
- Ueber 6 Monate Research-Output-Rate niedriger ist als ohne Limit (trotz Qualitaets-Gewinn nicht rentabel)
- Martin meldet dass 3 zu streng ist und 5 funktionieren wuerde
- Domain-Grenzen unschaerfer werden sodass Matrix unbrauchbar wird

**Replacement-Trigger**: Falls Falsifikation → Dynamisches Limit basierend auf gemessener Martin-Bandbreite (adaptive WIP).

**Claim-Type**: `empirical` (per G6)

[CRUX-MK]
