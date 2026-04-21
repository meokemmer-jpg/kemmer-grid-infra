# FALLBACK-Routinen [CRUX-MK]

**Zweck:** Alle Fallback-Routinen zentralisiert + klar markiert + loeschbar wenn nicht mehr gebraucht.

## Policy

Jeder Fallback:
- hat `FALLBACK-` Prefix im Dateinamen
- ist in `fallback/` Verzeichnis
- hat Eintrag in `FALLBACK-manifest.json` mit:
  - `type`: bug-workaround / provider-fallback / compatibility-shim / config-default
  - `reason`: warum ist der Fallback noetig
  - `triggered_count`: wie oft wurde er aktiviert
  - `success_count_without_this_fallback`: wie oft lief das System ohne ihn
  - `to_delete_when`: Bedingung fuer Loeschung
  - `deletion_command`: wie wird geloescht

## Deletion-Policy

Ein Fallback ist **Deletion-Kandidat** wenn:
- `triggered_count == 0` (hat nie feuern muessen)
- `success_count_without_this_fallback >= 30` (System lief 30x ohne ihn erfolgreich)
- `age_days >= 30` (mindestens 30 Tage aktiv)

**Martin-Approval ist Pflicht fuer jede Loeschung** (policy.require_martin_approval_for_deletion = true).

## Sweep

Das Script `FALLBACK-retention-sweep.py` prueft monatlich und schreibt:
- Report auf stdout
- BULLETIN-Alert (mit `--auto-notify`)
- Audit-Entry in `branch-hub/audit/fallback-sweep.jsonl`

Geplant: Monatlicher Scheduled Task (siehe DF-06 Deep-Pass der 1x/Tag laeuft, sweep kann dort integriert werden).

## Aktueller Bestand (2026-04-18)

| Name | Typ | Trigger | Erfolge-ohne-Fallback |
|------|-----|---------|----------------------|
| FALLBACK-pwsh-to-powershell | compatibility-shim | 1x | 0 |
| FALLBACK-detect-empty-title-skip | bug-workaround | 0x | 0 |
| FALLBACK-codex-to-gemini-router | provider-fallback | 2x | 0 |
| FALLBACK-global-optima-defaults | config-default | 0x | 0 |

Alle aktiv. Keiner noch Deletion-Kandidat (alle < 30 Tage alt).

## Loeschungs-Workflow

1. `python FALLBACK-retention-sweep.py` zeigt Kandidaten
2. Martin reviewed
3. Bei Approval: `python FALLBACK-retention-sweep.py --delete <name>`
4. Audit-Eintrag automatisch

## Warum das wichtig ist

Nach Martin-Direktive (2026-04-18):
> "bennene diese auch das diese nur Fallback ist damit wenn wir platz brauchen diese dann geloescht wird denn dann sollte das System ja x mal schon ohne Fallback notwendig gelaufen sein"

Fallbacks sind Safety-Nets, nicht permanent Features. Durch klares Naming + Manifest-Tracking + Retention-Sweep koennen sie sicher entfernt werden wenn das System bewiesen robust ist.

[CRUX-MK]
