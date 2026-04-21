---
type: proposal
title: Self-Healing fuer Dark Factories v2 (Cross-LLM-HARDENED)
author_v1: Worker0001 @ RazorBuero (PC 3)
reviewer: Opus 4.7 Work-D2 @ PC 1 Master (Synthese nach Cross-LLM)
date: 2026-04-21
ref: Martin-Direktive "Dark Factories ohne Selbstheilung geht nicht" + "a und b" 2026-04-21T12
status: PROPOSAL v2 (Martin-Approval pending, Phase-1-ready)
supersedes: Self-Healing-Dark-Factories-v1-2026-04-20.md
cross-llm: branch-hub/cross-llm/2026-04-21-Self-Healing-Dark-Factories-Adversarial.md
verdict: CROSS-LLM-SIMULATION-HARDENED (Codex + Gemini 2/2 MODIFY)
crux-mk: true
---

# Self-Healing Dark-Factories v2 (Cross-LLM-HARDENED) [CRUX-MK]

## Aenderung ggue v1

v1 (Worker0001) hat 4 DF-Versagen korrekt diagnostiziert und ein 5-Schichten-Modell vorgeschlagen. Cross-LLM-Haertung (Codex + Gemini adversarial) ergab **5 Patches P1-P5**, alle integriert.

v2 = v1-Kern + 5 Patches + NEUE Schicht 6 (Execution-Lease).

## Die 6 Schichten v2

### Schicht 1: Assertion-After-Write + Schema-Check (P5a NEU)

**v1:** Jedes DF schreibt Outcome + Assert-Check gegen Versprechen.
**v2-Patch P5a (Gemini):** Zusaetzlich Mandatory Schema + Min-Size-Check.

```python
def df_write(path, content, promise):
    write(path, content)
    log_write(path, content)
    # Assert: File existiert UND non-zero
    if not assert_reachable(promise.sync_target, path):
        log_alert("DF-ASSERT-FAIL", df=df_name, path=path)
        trigger_retry(df_name, path, attempt=1)
    # NEU P5a: Content-Integritaet
    if path.endswith('.json'):
        if not validate_schema(path, promise.schema_ref):
            log_alert("DF-SCHEMA-FAIL", df=df_name, path=path)
            trigger_retry(df_name, path, attempt=1)
    if os.path.getsize(path) < promise.min_bytes:
        log_alert("DF-ZOMBIE-EMPTY", df=df_name, path=path, size=os.path.getsize(path))
        trigger_retry(df_name, path, attempt=1)
```

**Pro DF:** `schema_ref` + `min_bytes` in Manifest.

### Schicht 2: Heartbeat-Monitor mit Notification-by-Exception (P3 NEU)

**v1:** Master-Scheduled-Task alle 15 Min checkt Worker-Status, DF-Timestamps, Rules-Hashes.

**v2-Patch P3 (beide Reviewer):** 
- Heartbeats = Rohsignale, NICHT Human-Alerts
- Alert nur bei **Zustandswechsel** (State-Change-Detection, nicht pro-Heartbeat)
- `warn` erst nach 2 verpassten Intervallen UND >45 Min ohne Erfolg
- `critical` nur bei Blast-Radius >1 DF oder Ownership-Verlust
- **Cooldown 2h** + Flap-Suppression zwischen Alerts
- **Taeglicher Digest** (07:00) fuer Resolved/Flapping/OK → 1 Email/Tag, kein Trickle
- Root-Cause-Korrelation: "PC2 stale" = **1 Incident**, nicht 10 DF-Alerts

**Ziel quantifiziert:** 160 Heartbeats/h → **<5 menschliche Incidents/Tag** (Martin-Ruhe).

### Schicht 3: Consistency-Check mit Schema-Validation (P5a NEU)

**v1:** Handoff-Writes triggern Checker gegen `get_references()`.

**v2-Patch P5a:** Checker prueft nicht nur `exists(ref)`, sondern auch **Schema + Min-Size** (analog Schicht 1).

### Schicht 4: Cross-Machine-Sync mit Manifest-Delta (P1 KRITISCH)

**v1-Problem:** Pull-Model O(N*D*R) → kollabiert bei N=10 Workers.

**v2-Patch P1 (beide Reviewer):**
- Jeder Worker schreibt **autoritatives Zyklus-Manifest** 
  - `branch-hub/state/worker-manifests/<worker-id>-manifest.json`
  - Felder: `worker_id`, `branch_head`, `rules_version`, `last_df_run`, `lease_owner`, `status_ts`
  - Atomic-Write via compare-and-swap
- Master-Cross-Validator: **Delta-Check gegen Manifest** → O(N)
- Pull → Push: Worker schreiben proaktiv, Master aggregiert nur

**Skalierung:** bei N=10 kein quadratischer Blowup.

### Schicht 5: Rules-Auth via Signed-Release-Tag (P4 KRITISCH)

**v1-Problem:** 3-Way-Hash-Compare zwischen `main`-Branch, Drive-Snapshot, lokalen Rules → Race-Conditions unloesbar.

**v2-Patch P4 (Codex-staerker, Gemini-Ergaenzung):**
- Authoritative = **signierter immutable Git-Tag** (z.B. `seed-v2026-04-21-a`)
- Bootstrap liest `~/.claude/rules/.version`, verifiziert Tag-Signatur gegen Release-Entry
- **Grace-Period 5 Min** fuer Drive-Sync-Verzoegerungen bevor Bootstrap-Halt (Gemini-Ergaenzung)
- Release-Kadenz: Bei jedem neuen Seed-ZIP → neuer Git-Tag (via `build-seed-zip.ps1` erweitern)

```python
def bootstrap_rules_verify():
    local_version = read_text("~/.claude/rules/.version")
    github_tag_sha = git_rev_parse(f"refs/tags/{local_version}")
    signature_ok = git_verify_tag(local_version)
    if not (signature_ok and github_tag_sha):
        # 5-Min-Grace
        time.sleep(300)
        # Retry
        if not (signature_ok and github_tag_sha):
            halt_bootstrap(f"Rules-Tag {local_version} not verifiable")
```

### Schicht 6: Execution-Lease (P5b NEU)

**v1-Verfehlt:** Split-Brain-Doubled-Execution — DF-07 laeuft auf PC2 + PC3 gleichzeitig wegen Status-Race.

**v2-Patch P5b (Codex):**
- **Monotone `run_id`** pro DF-Run
- **TTL-Lease** pro DF-Run mit compare-and-swap beim Start
  - Datei: `branch-hub/state/leases/<df-name>.lease` JSON
  - Fields: `lease_owner`, `run_id`, `expires_at`, `content_sha`
- **Retry nur nach Lease-Expiry** (verhindert Doppel-Trigger)
- **Artefakte content-addressed** (SHA-suffixed Filenames) → last-writer-wins NICHT destruktiv

## External-Watchdog statt Self-Referential (P2 KRITISCH)

**v1-Verfehlt:** 2-Layer-Watchdog auf demselben Master = gemeinsame Failure-Domain.

**v2-Patch P2 (Konsens):**
- **Primary-Watchdog:** Mac (Phase 3) — Master schreibt Lease/Heartbeat in LAN-Sink auf Mac; Mac prueft Lease-Expiry + fehlende Ack-Kette (Codex-Variante)
- **Secondary-Watchdog:** PC2 Reciprocal — ueberwacht Master-Heartbeat-Timestamp (Gemini-Variante)
- **Bis Mac online:** nur PC2-Reciprocal (Phase 2 genug)
- Kein rekursiver Watchdog-Turm auf PC1.

## Implementierungs-Reihenfolge v2

### Phase 1 — SOFORT (4h)
- **Schicht 3** Consistency-Check + **P5a** Schema/Size-Check
- **Schicht 5** Rules-Verify + **P4** Signed-Git-Tag + Grace-Period

**Haette gefangen (aus 4 v1-Versagen):**
- ✅ L1 Master-Bootstrap-Paket nicht auf G: (Schicht 3 Consistency)
- ✅ L3 GitHub /rules/ outdated 9 statt 40 (Schicht 5 Rules-Tag)
- ✅ L4 Seed-Export-ZIP fehlt (Schicht 3 Consistency)
- ✗ L2 PC2 unsichtbar (braucht Phase 2 Schicht 4)

### Phase 2 (6h, 1-2 Tage)
- **Schicht 1** Assertion-After-Write retroaktiv auf DF-05/06/07/08/10 + **P5a** Schema
- **Schicht 2** Heartbeat-Monitor + **P3** Notification-by-Exception + Digest
- **P2 Secondary** PC2-Reciprocal-Watchdog

### Phase 3 (10h, 3-5 Tage nach Mac-Phase-3)
- **Schicht 4** Cross-Machine-Sync + **P1** Manifest-Delta (Pull→Push)
- **Schicht 6** Execution-Lease (**P5b** NEU)
- **P2 Primary** Mac-External-Watchdog

## Kosten-Nutzen v2

| Phase | Aufwand | rho-Schutz |
|-------|---------|-----------|
| Phase 1 (P4+P5a) | 4h | +25-70k EUR/J (Integritaet) |
| Phase 2 (P3+P5a) | 6h | +50-130k EUR/J (weniger Alert-Fatigue) |
| Phase 3 (P1+P2+P5b) | 10h | +25-60k EUR/J (valide Skalierung bei N=10) |
| **Gesamt v2** | **~22h (+6h)** | **+100-260k EUR/J** |

**Break-Even:** Phase 1 bereits <1 Tag Arbeit → amortisiert sich beim ersten verhinderten DF-Versagen.

## Anti-Patterns (erweitert)

v1-Anti-Patterns (AP-1 bis AP-5) gelten weiter. Neu in v2:

- **AP-6 (v2):** Self-Referential-Monitoring auf gleicher Failure-Domain. Watchdog der sich selbst watcht ist Single-Point-of-Failure-Falle (P2).
- **AP-7 (v2):** Pull-basierter Cross-Machine-Check bei N>4. Skaliert nicht (P1).
- **AP-8 (v2):** 3-Way-Hash-Consensus auf bewegliche Ziele. Git-Branches + Drive + Lokal = Race-Condition-Playground. Nur signed Tag (P4).
- **AP-9 (v2):** `exists()` als einzige Existenz-Pruefung. 0-Byte / Muell-JSON ist unsichtbar (P5a).
- **AP-10 (v2):** Kein Lease-Modell → Split-Brain-Doubled-Execution (P5b).

## Cross-LLM-Meta

- **Verdict:** 2/2 MODIFY, 0 REJECT
- **Reviewer:** Codex GPT-5 + Gemini 2.5 Pro (verschiedene Families, G3.2-kompatibel)
- **Tier:** CROSS-LLM-SIMULATION-HARDENED (noch nicht echt-HARDENED, da nur 2 LLMs, kein 3. Model)
- **Konsens-Rate:** 4/5 Fragen full, 1/5 komplementaer (2 valide Failure-Modes)
- **Cross-LLM-Kosten:** €0 (beide Flat-Abos)
- **Master-Synthese-Kosten:** ~€0.05 Claude-Opus

## Offen fuer v3-HARDENED (optional)

Falls v2 einsetzt und Martin 3. Review will:
- Grok-4 adversarial (via grok-mcp, wartet auf Claude-Code-Restart)
- Oder: Perplexity Ultimate fuer Failure-Mode-Research Zeitfenster

v2 ist bereits deploybar fuer Phase 1 — kein Warten auf v3 noetig.

## Phase-1-Start-Entscheidung

**Empfehlung Master-Review:** 
- Schicht 3 + P5a + Schicht 5 + P4 sofort umsetzen (4h)
- Das faengt 3 von 4 ursaechlichen Versagen
- Token-Kosten gering (Flat-LLMs fuer Code-Gen + Claude-Opus nur fuer Review)
- Martin-Approval: **ja/nein** in Inbox

## CRUX

- **K_0:** geschuetzt (Schicht 5 + P4 verhindert CRUX-Drift durch Rules-Divergenz)
- **Q_0:** erhoeht (Integritaet via P5a, weniger Cognitive-Load durch P3)
- **I_min:** strukturell erhoeht (6 Schichten statt 5, explizite Lease-Model)
- **W_0:** Martin-Bandbreite geschuetzt durch P3 Notification-by-Exception
- **rho:** +100-260k EUR/J bei Vollausbau

[CRUX-MK]
