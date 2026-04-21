# kemmer-grid-infra

**Control-Plane fuer Kemmer Multi-LLM-Multi-Machine-Grid** [CRUX-MK]

Versionierte Infrastruktur-Definition fuer 3 Windows-PCs + 1 Mac M5 Max (spaeter). Single Source of Truth fuer Manifeste, Bootstrap-Scripts, Kill-Switch, Golden Task Suite, LLM-Router-Config, Rules-System.

## Schnellstart

### Mac M5 Max (Local-Inference-Node)
```bash
cd ~ && git clone https://github.com/meokemmer-jpg/kemmer-grid-infra.git kemmer-grid
cd kemmer-grid
cat docs/MAC-QUICKSTART.md    # lies das zuerst!
sh scripts/pre-bootstrap-check.sh
sh scripts/grid-bootstrap.sh --role local-inference
```

### Windows-Worker (PC2/PC3)
```powershell
cd C:\Users\$env:UserName
git clone https://github.com/meokemmer-jpg/kemmer-grid-infra.git kemmer-grid
cd kemmer-grid
pwsh scripts\pre-bootstrap-check.ps1
pwsh scripts\grid-bootstrap.ps1 -Role worker
```

### Windows-Master (PC1)
```powershell
# Analog, aber mit -Role primary
# ACHTUNG: nur EIN Master im Grid zulaessig (MR-1 Master-Singleton)
pwsh scripts\grid-bootstrap.ps1 -Role primary
```

## Repo-Struktur

```
kemmer-grid-infra/
├── README.md                              # Dieses File
├── scripts/
│   ├── kill-switch.sh / .ps1              # Deterministischer Stop (ohne LLM)
│   ├── pre-bootstrap-check.sh / .ps1      # 30-Sek-Diagnose
│   └── grid-bootstrap.sh / .ps1           # Idempotenter Resume-Installer
├── manifests/
│   ├── manifest-primary.json              # Master-Rollen-Spec
│   ├── manifest-worker.json               # Worker-Rollen-Spec
│   └── manifest-mac-local-inference.json  # Mac-Rollen-Spec
├── golden-tasks/
│   └── golden-task-suite.json             # 12 Capability-Tests fuer Admission
├── router/
│   └── litellm-router-config.yaml         # 4-Tier LLM-Routing
├── docs/
│   ├── MAC-QUICKSTART.md
│   ├── session_bootstrap_mac_2026-04-20.md
│   ├── claude-md-mac-patch.md
│   └── grid-endpoints-schema.md
└── claude-system/
    ├── CLAUDE.md                          # Verfassung (alle Machines)
    ├── rules/                             # 40 aktive Rules
    ├── scripts/                           # 12 Python-Hooks
    └── skills/                            # Kemmer-eigene Skills
```

## Hard-Stops (Burnout-Protection, v2-Addendum)

Diese Trigger sind **ueber allem anderen** (keine Verhandlung):

| Trigger | Aktion |
|---------|--------|
| Martin-h/Woche steigt >30% vs 3-Wochen-Baseline | HALT + BEACON-Alert |
| Schlaf-Qualitaet Martin sinkt >15% | HALT + Review |
| API-Cost >50 EUR/h pro Node | AUTO-KILL via kill-switch |
| >100 Auto-Repair-Versuche in 24h | AUTO-KILL |
| Rho-Netto nach Woche 8 <+180 EUR | SHUTDOWN-Empfehlung an Martin |

## Referenz-Dokumente

- Masterplan v2: `Claude-Knowledge-System/branch-hub/findings/MASTERPLAN-v2-MULTI-LLM-MULTI-MACHINE-GRID-2026-04-20.md`
- Loopback-Audits: `Claude-Knowledge-System/branch-hub/wargames/multi-llm-grid-masterplan-2026-04-20/`
- CRUX-Framework: `claude-system/CLAUDE.md` §0 "CRUX"

## rho-Bindung

- **K_0 (Kapital):** geschuetzt via physischer Kill-Switch + Cost-Cap
- **Q_0 (Familie/Qualitaet):** geschuetzt via Hard-Stops auf Martin-Zeit + Schlaf
- **I_min (Ordnung):** erhoeht via Single-Source-of-Truth GitHub + Versioning
- **W_0 (Martin-Bandbreite):** direkt optimiert via Delegation + lokale Inferenz (Mac Phase 3)

## Lizenz

Privater Gebrauch Familie Kemmer. Public fuer Cross-Machine-Git-Sync via GitHub. Keine Secrets in diesem Repo.

## Status

v0.1 Initial-Commit 2026-04-20. Masterplan v2 integriert. Loopback-Auditoren-Patches beachtet (3/3 REJECT/MODIFY-fundamental des v1-Plans adressiert).

[CRUX-MK]
