---
type: cross-llm-audit
subject: Self-Healing-Dark-Factories-v1 (Worker0001-PC3 Proposal)
reviewers: [Codex GPT-5, Gemini 2.5 Pro]
date: 2026-04-21
verdict: MODIFY (2/2 Konsens, keine REJECT)
crux-mk: true
---

# Cross-LLM-Haertung: Self-Healing-Dark-Factories v1 [CRUX-MK]

## Setup

**Proposal:** `branch-hub/proposals/Self-Healing-Dark-Factories-v1-2026-04-20.md` (Worker0001@PC3, 134 Zeilen)
**Reviewer:** Codex GPT-5 (via `codex exec`) + Gemini 2.5 Pro (via `gemini -p`) parallel
**Prompt:** Adversarial, 5 Angriffs-Fragen, max 400 Worte, strukturierter Output
**Master-Review:** Opus 4.7 Work-D2 (Synthese + Patch-Katalog)

## Verdict-Matrix

| # | Frage | Codex | Gemini | Konsens |
|---|-------|-------|--------|---------|
| 1 | Skalierungs-Bottleneck | Schicht 4 O(N²)→O(N) | Schicht 4 O(N*M) Pull→Push | **HOCH: Schicht 4 umbauen** |
| 2 | Watchdog-Rekursion | 2-Layer falsch, Dead-Man-Switch ausserhalb | 2-Layer falsch, Reciprocal Worker→Master | **HOCH: externer Watchdog, NICHT self-referential** |
| 3 | Alert-Fatigue | State-Change + Blast-Radius + Digest, 160→<5 | Exception-only + Digest, 160→0 | **HOCH: Notification-by-Exception** |
| 4 | Race-Auth | Signiertes Release-Tag | Git Branch main | **TEIL: beide Git-based, Codex staerker** |
| 5 | Nicht-Adressiert | Split-Brain-Doubled-Execution (Lease-Modell) | Zombie-Empty-Output (Schema/Size) | **BEIDE VALIDE: 2 separate Failure-Modes** |

**Verdict:** 2/2 **MODIFY**. Keine REJECT. Proposal-Kern (5-Schichten-Modell) bleibt, 5 Patches noetig.

## Patch-Katalog (5 konsolidierte Patches)

### P1 Schicht-4-Architektur: Pull → Push + Manifest-Delta (HOCH)

**Problem:** Aktuelle Schicht 4 liest Worker-Git-Branches + Status-Files zentral → O(N²) bei N=10.

**Fix (Konsens):**
- Jeder Worker schreibt **autoritatives Zyklus-Manifest**: `worker_id`, `branch_head`, `rules_version`, `last_df_run`, `lease_owner`
- Master-Cross-Validator macht nur **Delta-Check gegen Manifest** → O(N)
- Pfad: `branch-hub/state/worker-manifests/<worker-id>-manifest.json`
- Atomic-Write mit compare-and-swap beim Update

**Implementierungs-Aufwand:** +2h zusaetzlich zu Schicht-4 Basis (Pull-Code durch Manifest-Reader ersetzen)

### P2 Watchdog in anderer Failure-Domain (KRITISCH)

**Problem:** 2-Layer-Watchdog auf demselben Master = gemeinsame Failure-Domain (Scheduler kaputt → beide tot).

**Fix (Konsens, leichte Varianz):**
- **Option A (Codex):** Dead-Man-Switch auf Mac (LAN-Gestuetzt) — Master schreibt Lease/Heartbeat in append-only Sink; Mac prueft Lease-Expiry + fehlende Ack-Kette
- **Option B (Gemini):** Reciprocal — Worker PC2 ueberwacht Master-Heartbeat-Timestamp; bei Ausbleiben triggert PC2 Notfall-Alarm

**Entscheidung:** **Beide kombinieren**. Mac = Primary-External-Watchdog. Worker PC2 = Secondary-Reciprocal. Sekundaer-Watchdog steht erst wenn Mac online (Phase 3). Bis dahin: PC2-reciprocal ausreichend.

### P3 Notification-by-Exception + Digest (HOCH)

**Problem:** 4 Worker × 10 DFs × 15-Min-Heartbeats = 160 Heartbeats/h → Alert-Flood.

**Fix (Konsens):**
- Heartbeats sind **Rohsignale**, keine Human-Alerts
- Alert nur bei **Zustandswechsel** (State-Change-Detection, nicht pro-Heartbeat)
- `warn` erst nach 2 verpassten Intervallen UND >45 Min ohne Erfolg
- `critical` nur bei Blast-Radius >1 DF oder Ownership-Verlust
- **Cooldown 2h** + Flap-Suppression
- **Taeglicher Digest** fuer Resolved/Flapping/OK
- Root-Cause-Korrelation: "PC2 stale" = 1 Incident statt 10 DF-Alerts

**Ziel:** 160 Rohsignale/h → **<5 menschliche Incidents/Tag**

### P4 Authoritative = Signiertes Release-Tag (KRITISCH)

**Problem:** `main` und Drive-`latest` und lokales Hash sind bewegliche Ziele. Race-Conditions bei 3-Way-Sync-Check nicht loesbar.

**Fix (Codex-staerker, Gemini-Basis):**
- **Schicht 5 umbauen**: Authoritative = **signierter immutable Git-Tag** (z.B. `seed-v2026-04-21-a`)
- Nicht `main`-Branch, nicht Drive-Snapshot, kein Quorum
- Version wird aus `~/.claude/rules/.version` gelesen, Tag-Signatur verifiziert
- **5-Minuten Grace-Period fuer Drive-Sync-Verzoegerungen** vor Bootstrap-Halt (Gemini-Ergaenzung)
- Release-Kadenz: Bei jedem neuen Seed-ZIP wird ein Git-Tag erzeugt

### P5 NEUE Schicht 6: Execution-Lease + Schema/Size-Check (KRITISCH)

**Problem:** 2 separate Failure-Modes die Proposal verfehlt:

**P5a (Gemini) — Zombie-Empty-Output:**
- DF crasht waehrend Write oder produziert 0-Byte / semantisch leeren JSON
- Schicht 3 `exists()` ist True, aber Inhalt ist Muell
- Fix: **Mandatory Schema-Validation + Min-Size-Check** in Schicht 1/3
- Pro DF: definierte JSON-Schema + min_bytes in Manifest

**P5b (Codex) — Split-Brain-Doubled-Execution:**
- Master haelt DF-07 auf PC2 fuer stale, retriggert auf PC3
- PC2 lief aber weiter, nur Status-Write hing
- Resultat: doppelte Commits, last-writer-wins, nondeterministische Outputs
- Fix: **NEUE Schicht 6 Execution-Lease**
  - Monotone `run_id` pro DF-Run
  - TTL-Lease mit compare-and-swap beim Start
  - Retry nur nach Lease-Expiry
  - Artefakte content-addressed (SHA-suffixed)

**Beide sind komplementaer — P5a fixt Content-Integritaet, P5b fixt Execution-Ownership.**

## Implementierungs-Reihenfolge v2 (Patches integriert)

### Phase 1 (SOFORT, <1 Tag, 4h)
- Schicht 3 Consistency-Check **+ P5a Schema/Size-Check**
- Schicht 5 Rules-Hash-Enforcement **+ P4 Signed-Git-Tag + Grace-Period**

### Phase 2 (1-2 Tage, 6h)
- Schicht 1 Assertion-After-Write retroaktiv DF-05/06/07/08/10 **+ P5a Schema**
- Schicht 2 Heartbeat-Monitor **+ P3 Notification-by-Exception**

### Phase 3 (3-5 Tage, 10h nach Mac-Phase-3)
- Schicht 4 Cross-Machine-Sync-Validator **+ P1 Manifest-Delta + Pull→Push**
- Schicht 6 Execution-Lease (NEU, **P5b**)
- **P2 External-Watchdog** (Mac + PC2-Reciprocal)

## Kosten-Nutzen v2

| Phase | Aufwand | rho-Schutz (v1-Basis + Patches) |
|-------|---------|--------------------------------|
| Phase 1 mit P4+P5a | 4h (+1h) | +25-70k EUR/J + Integritaet |
| Phase 2 mit P3+P5a | 6h (+1h) | +50-130k EUR/J + weniger Alert-Fatigue |
| Phase 3 mit P1+P2+P5b | 10h (+4h) | +25-60k EUR/J + Skalierung valide bei N=10 |
| **Gesamt v2** | **~22h (+6h)** | **+100-260k EUR/J (gleich wie v1 Basis, aber skaliert valide)** |

## Konsens-Staerke

- **2/2 MODIFY**, keine REJECT
- **4/5 Fragen voller Konsens**
- **Frage 5**: 2 verschiedene Failure-Modes identifiziert → beide valide, ergaenzen sich
- **G3.2 Divergenz-Proxies** (rules/meta-governance-framework.md): Codex (OpenAI-family) + Gemini (Google-family) sind genug lineage-distant, keine Bias-Korrelation erwartbar
- **Verdict-Tier:** CROSS-LLM-SIMULATION-HARDENED (2/2, beide externe Modelle, keine Claude-Self-Validation)

## Status

- **Phase-1 darf starten** (4h Arbeit, P4+P5a integriert)
- **Martin-Approval** fuer v2 pending
- **Worker0001 wird informiert** via inbox

## Cross-LLM-Meta

- **Runtime Codex:** ~45s fuer 29 Zeilen Output
- **Runtime Gemini:** ~35s fuer 27 Zeilen Output
- **Parallel-Run:** beide gleichzeitig gestartet (background-job)
- **Token-Kosten:** €0 (beide via Flat-Abos: Pro-Tier Codex + Gemini Ultra)
- **Claude-Opus Token:** ~400 fuer Prompt-Craft + ~800 fuer Synthese = ~1200 Tokens
- **rho-Ratio:** Cross-LLM kostet €0 marginal, Master-Synthese ~€0.05 → Netto-positive rho bei P-Umsetzung

[CRUX-MK]
