---
name: structural-bypass-first
description: 3-Schritte-Protokoll bei externer-System-Integration-Blockade. Suche strukturellen Bypass-Pfad VOR Eskalations-Taktik. Basiert auf F417 (MEWS Booking Engine API umgeht Partner-Token-Block).
type: rule
meta-ebene: E3
status: ACTIVE-MODIFY-v2-PENDING (C1-Wargame 2/3 MODIFY-zu-Aktivierung 2026-04-19)
modify-v2-schaerfungen: [Scope+Support+Compliance+Reversibility-Check vor Bypass-Aktivierung, Security-Review-Pflicht, Empirie-Nachholen ueber 3+ Cases, N=1 MEWS-Basis zu duenn]
c1-wargame-finding: branch-hub/findings/FINDING-C1-PROPOSAL-RULES-WARGAME-2026-04-19.md
c1-wargame-detail: branch-hub/cross-llm/2026-04-19-WARGAME-C1-structural-bypass-first.md
created: 2026-04-19
aktiviert: 2026-04-19
cross-llm-reference: F417 aus Subnautica-Fragment-Map-Ergaenzung-T
claim-type: empirical
---

# Structural-Bypass-First [CRUX-MK] — PROPOSAL

## Zweck
Bei externer-System-Integration-Blockade (Credential / API-Token / Partner-Status): Suche strukturellen Bypass-Pfad VOR Eskalations-Taktik.

Beleg: MEWS-E2-Fall — Partner-Token 5+ Tage blockiert, waehrend Booking Engine API gesamte Blockade umgeht (fuer passendes Use-Case).

## Regel

### R1 3-Schritte-Protokoll bei Integration-Blockade

**Schritt 1: Struktur-Check** (MUST BEFORE Schritt 3)
- Pro externes System: welche Sub-APIs / Alt-Endpunkte existieren?
- Was koennen die OHNE die blockierte Credential-Klasse?
- Dokumentation-Scan: "do not need certification", "public API", "guest access"
- Artefakt: Sub-API-Map

**Schritt 2: Scope-Match**
- Tatsaechlicher Use-Case (nicht Wunsch-Case): welche Operationen konkret noetig?
- Deckt Sub-API den Use-Case ab? Messung via Feature-Coverage-Matrix
- Wenn JA → direkt implementieren, Eskalation unnoetig
- Wenn NEIN oder PARTIAL → Gap-Liste + Schritt 3

**Schritt 3: Eskalation** (nur nach negativen Schritt 1+2)
- LinkedIn-PAM / Support-Ticket / Phone / Fachanwalt
- Gap-Liste als Eskalations-Input

### R2 Strukturelle-Blindheit-Anti-Pattern
- "Credential blockiert = Projekt blockiert" (ohne Sub-API-Check)
- Eskalations-Pattern-First (teuer, zeitintensiv)
- Pilot-Property-Request wenn Sub-API das nicht braucht

### R3 Empirische Belege
| Fall | Blockade | Strukturelle-Bypass | Erfolg |
|------|----------|--------------------|---------|
| MEWS E2 | Partner-Token 5+ Tage | Booking Engine API | POTENTIAL (Scope-Match offen) |
| [zukuenftige Faelle hier ergaenzen] | | | |

### R4 Audit-Pflicht
Bei jeder externen-System-Integrations-Planung vor Start:
- Dokumentiere Sub-API-Check (Schritt 1)
- Dokumentiere Scope-Match (Schritt 2)
- Nur dann Architektur-Decision

## Mechanik
- Decision-Card-Template bekommt Feld "sub_api_check_done: yes/no"
- Pre-Integration-Planning-Skill optional

## Anti-Patterns
- Partner-Token als default-Annahme
- "Wir brauchen halt den Marketplace-Eintrag" (oft unnoetig)
- Skip von Schritt 1 weil "offensichtlich"

## SAE-Isomorphie
Trinity-Pattern: 3 Varianten (Direct-API / Sub-API / Workaround). Niedrigster Reibungs-Pfad waehlen.

## CRUX-Bindung
- K_0: Zeit-Ersparnis bei Integration-Starts (Wochen-Scale)
- W_0: Working Capital wird nicht auf Eskalation geparkt
- rho: direct 5-15k + systemisch 20-50k/J

## rho-Impact
25-65k EUR/J (direkt E2 + systemisch zukuenftige Integrationen HubSpot/SAP/Google/etc.)

## Falsifikations-Bedingung
- Wenn 3+ Faelle: Strukturelle-Bypass existiert NICHT und Eskalation bleibt einzig → Rule-Revision
- Wenn Bypass-Check selbst zu teuer (> 20% Integrations-Aufwand) → Cost-Benefit revidieren

## Selbst-Anwendung
G1 ok (Rule ueber Integration, ist selbst keine Integration). Empirisch belegt 1x (N=1 low, weitere Faelle pending).

[CRUX-MK]
