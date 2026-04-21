---
type: proposal
title: Self-Healing fuer Dark Factories (Konsistenz-Validator + Heartbeat + Auto-Retry)
author: Worker0001 @ RazorBuero (PC 3)
date: 2026-04-20
ref: Martin-Direktive "Dark Factories ohne Selbstheilung geht nicht oder"
status: PROPOSAL (Martin-Approval + Master-Review pending)
cross-llm: PENDING (CLIs fehlen auf PC3, Cross-LLM-Haertung durch Master ausstehend)
crux-mk: true
---

# Self-Healing fuer Dark Factories v1 [CRUX-MK]

## Anlass: 4 DF-Versagen in einer Session ohne Alarm

| # | Versagen | Symptom | Wirkung |
|---|----------|---------|---------|
| 1 | Master-Bootstrap-Paket nie auf G: | `memory/session_bootstrap_multi_machine_2026-04-20.md` PC-lokal | Worker-Onboarding blockiert |
| 2 | PC2-Arbeit komplett unsichtbar | keine Status/Inbox/Commits auf G:/GitHub | Koordination unmoeglich |
| 3 | GitHub-Repo `/rules/` outdated (9 statt 40) | Seed-Import Option C aus Setup-Paket §7 kaputt | CRUX-Drift-Risiko |
| 4 | Seed-Export-ZIP nicht generiert | `G:/Seed-Exports/kemmer-seed-export-2026-04-20.zip` existiert nicht | §7-Option-A kaputt |

**Gemeinsame Root-Cause:** DF schreibt, kein Validator pruef ob Ergebnis dort angekommen ist wo versprochen. Kein Heartbeat. Kein Auto-Retry. Kein Alert.

## Self-Healing-Schichten-Modell

### Schicht 1: Assertion-After-Write (jedes DF)
Jedes DF schreibt Outcome, ANSCHLIESSEND Assert-Check gegen Versprechen.

**Pseudo-Code:**
```python
def df_write(path, content, promise):
    write(path, content)
    log_write(path, content)
    # NEU: Self-Assert
    if not assert_reachable(promise.sync_target, path):
        log_alert("DF-ASSERT-FAIL", df=df_name, path=path, target=promise.sync_target)
        trigger_retry(df_name, path, attempt=1)
```

**Konkret:** DF-06 verspricht `session_bootstrap_multi_machine_2026-04-20.md` in `memory/`. Assert: `test -f G:/Meine Ablage/.../memory/...` direkt danach. Wenn nicht da → Alert + Retry.

### Schicht 2: Heartbeat-Monitor (zentraler Scheduled-Task auf Master)
1 Master-Task (`DF-11-heartbeat-watchdog.py`) checkt ALLE 15 Min:
- Alle Worker-Status-Files <15 Min alt? Sonst: Alert + Pruef ob PC reachable
- Alle DF-Last-Run-Timestamps im erwarteten Fenster? Sonst: Alert + Auto-Retry
- Rules-Hash aller PCs identisch? Sonst: Divergence-Alert + Force-Sync

**Output:** `branch-hub/state/heartbeat-<YYYY-MM-DD>.jsonl` + Alerts in `branch-hub/alerts/`

### Schicht 3: Consistency-Check (nach Merges + Handoffs)
Jedes Handoff-Write triggert Checker:
```python
def check_handoff_consistency(handoff_path):
    handoff = read(handoff_path)
    for referenced_artifact in handoff.get_references():
        assert exists(referenced_artifact), f"Broken reference: {referenced_artifact}"
    return True  # oder raise
```

**Konkret:** Blueprint `multi-machine-coordination-v1-2026-04-20.md` verweist Zeile 122 auf Bootstrap-Paket. Checker haette gefangen dass Bootstrap nicht existiert.

### Schicht 4: Cross-Machine-Sync-Validator (fuer PC-uebergreifende Konsistenz)
Neuer DF `DF-12-cross-machine-sync-validator` (Master-exklusiv):
- Liest alle Worker-PC-Git-Branches + Status-Files
- Vergleicht: `git log --since=24h --all | diff g:/pulled-state`
- Detected: Worker hat commits die nicht in main sind? Worker-Status >15 Min alt? Worker hat DF-* Scheduled-Task (MR-1-Verletzung)?
- **Alert** + Auto-PR-Request bei Divergenz

### Schicht 5: Rules-Hash-Enforcement (hart)
Bootstrap-Zeit-Check:
```python
def bootstrap_rules_verify():
    local_hash = sha256_dir("~/.claude/rules/")
    github_hash = sha256_github_branch("main", "rules/")
    drive_snapshot_hash = sha256_dir("G:/Meine Ablage/claude-seeds/latest/rules/")
    if not (local_hash == github_hash == drive_snapshot_hash):
        halt_bootstrap("Rules-Divergenz, Master-Reconciliation noetig")
```

**Konkret:** Wenn GitHub-`/rules/` 9 Files und Drive-Snapshot 40 Files und Lokal 40 hat → **Alarm**. Nicht stumm weiterarbeiten.

## Kosten-Nutzen-Abschaetzung

| Schicht | Implementierungs-Aufwand | Laufzeit-Overhead | rho-Schutz |
|---------|---------------------------|-------------------|------------|
| 1 Assertion-After-Write | 20 Min/DF × 10 DFs = ~3h | <1% | +30-80k EUR/J (verhindert stille Verluste) |
| 2 Heartbeat-Monitor | 1 neuer Task, ~4h | 15 Min × 4/h = 1h Compute/Tag | +20-50k EUR/J |
| 3 Consistency-Check | Handoff-Hook, ~2h | <5 Sek/Write | +15-40k EUR/J |
| 4 Cross-Machine-Sync-Validator | 1 neuer Task, ~6h | 30 Min/Tag | +25-60k EUR/J |
| 5 Rules-Hash-Enforcement | Bootstrap-Pre-Check, ~1h | <3 Sek/Boot | +10-30k EUR/J |
| **Gesamt** | **~16h + 4 neue Tasks** | **~3-5% Compute** | **+100-260k EUR/J** |

## Implementierungs-Reihenfolge (nach Prio)

### Phase 1 (SOFORT, <1 Tag)
- **Schicht 3 Consistency-Check** fuer Handoffs (haette aktuelles Problem gefangen)
- **Schicht 5 Rules-Hash-Enforcement** fuer Bootstrap (verhindert CRUX-Drift)

### Phase 2 (1-2 Tage)
- **Schicht 1 Assertion-After-Write** retroaktiv auf DF-05/06/07/08/10 aufsetzen
- **Schicht 2 Heartbeat-Monitor** als Master-Task neu

### Phase 3 (3-5 Tage, nach Shadow-Mode-Validierung)
- **Schicht 4 Cross-Machine-Sync-Validator** (braucht Multi-Machine aktiv)

## Anti-Patterns (was NICHT tun)

- **AP-1:** Silent-Failure. "Schreibt irgendwas, pruef nicht." → aktueller Zustand, 4 Versagen.
- **AP-2:** Alert-Fatigue. Jede Kleinigkeit als CRIT → Ignoriert werden. Nur Pflicht-Versprechens-Verletzungen escalaten.
- **AP-3:** Self-Referential Self-Heal. Ein Self-Healer der sich selbst NICHT monitored = Single-Point-of-Failure. Watchdog muss selbst watchdog haben (2-Layer).
- **AP-4:** Auto-Fix ohne Audit. Auto-Retry OK, aber JEDER Fix muss in `audit/self-heal.jsonl` protokolliert sein (Nachvollziehbarkeit).
- **AP-5:** Hartes Auto-Merge bei Konflikten. Self-Heal darf NICHT Martin-Phronesis-Entscheidungen treffen. Bei Konflikt → Alert + Halt.

## Relation zu bestehenden Findings/Rules

- `FINDING-DRIVE-SYNC-CHAOS-2026-04-18` — Drive ist unzuverlaessig → Self-Heal muss Drive-agnostisch sein (Schicht 5 hilft)
- `FINDING-DRIVE-SYNC-FORENSIK-2026-04-18` — Forensik ist reaktiv → Self-Heal waere proaktiv
- `CR-2026-04-19-001` Crash-Report — Pre-Compact-Write-Zwang ist bereits partielle Self-Heal → erweitert durch Schicht 1
- `rules/antifragile-crash-structure-v1.0` (M9) — Pflicht-Artefakte pre-compact → Consistency-Check waere Assertion dafuer
- `rules/meta-harness.md` — Cross-LLM-Verdict braucht Consistency-Check (Schicht 3)

## Offen fuer Cross-LLM-Haertung (wenn Master/PC2 validieren koennen)
- Codex-Review: Skalierbarkeit bei 4+ PCs
- Gemini-Review: Adversarial (was bricht den Self-Healer?)
- Grok-Review: Failure-Mode-Katalog

## Fazit
Martin-Direktive ist korrekt: **Ohne Self-Healing sind Dark Factories fragil.** Bei 4 unentdeckten Versagen in EINER Session ist der Zustand nicht tragbar fuer Multi-Machine-Skalierung. Phase-1 sollte sofort gestartet werden, bevor ein 2. oder 3. Worker-PC dazukommt.

## Naechster Schritt
Master-Review. Cross-LLM-Haertung. Dann Phase-1-Implementation (Handoff-Consistency-Check + Rules-Hash-Enforcement, ~3h Arbeit).

[CRUX-MK]
