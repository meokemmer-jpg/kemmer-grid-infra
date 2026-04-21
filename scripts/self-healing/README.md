# Self-Healing Phase 1 (MVP) [CRUX-MK]

Cross-LLM-HARDENED 2/2 MODIFY (Codex + Gemini adversarial 2026-04-21).
Ref: `docs/proposals/Self-Healing-Dark-Factories-v2-2026-04-21.md`

## Was Phase 1 deckt

| Schicht | Script | Was es faengt |
|---------|--------|---------------|
| **3** Consistency-Check | `consistency-check.py` | Broken Markdown-References in Handoffs / Inbox / Proposals |
| **P5a** Zombie-Empty-Fix | `consistency-check.py` (Min-Size + Schema) | 0-Byte-Outputs, fehlende Frontmatter-Felder |
| **5** Rules-Verify | `rules-verify.py` | Rules-Drift gegen Master-Seed |
| **P4** Signed-Git-Tag | `rules-verify.py` | Race-Condition-Feste Version-ID |
| **Grace 5 Min** | `rules-verify.py` | Drive-Sync-Verzoegerungen werden nicht als Bootstrap-Halt missinterpretiert |

**Deckung der 4 v1-Versagen:** 3 von 4 (L1 Bootstrap-Paket + L3 outdated-Rules + L4 Seed-ZIP).
L2 (PC2 unsichtbar) braucht Phase 2 Schicht 4.

## Nutzung

### Consistency-Check auf einzelne Datei
```bash
python scripts/self-healing/consistency-check.py \
  --file "G:/Meine Ablage/Claude-Knowledge-System/branch-hub/inbox/to-yogamobil-from-work-d2-seed-fixed-2026-04-21.md"
```

**Exit-Codes:** 0=OK, 1=Schema-Fail, 2=Size-Fail, 3=Broken-Refs, 4=File-Error.

### Consistency-Check auf Verzeichnis
```bash
python scripts/self-healing/consistency-check.py \
  --dir "G:/Meine Ablage/Claude-Knowledge-System/branch-hub/inbox" \
  --strict
```

### Rules-Verify (Bootstrap-Mode)
```bash
python scripts/self-healing/rules-verify.py --halt-on-fail --grace-sec 300
```

### Rules-Verify (Monitor-Mode, warn-only)
```bash
python scripts/self-healing/rules-verify.py
```

## Audit-Trail

Alle Checks loggen JSONL nach `~/.kemmer-grid/self-healing-audit.jsonl`.
Jede Zeile enthaelt: `ts`, `event`, `target`, Ergebnis-Felder.

## Integration (Hook-Punkte)

### Hook 1: Pre-Handoff-Write
Vor `Write` auf `branch-hub/inbox/*.md` oder `handoffs/*.md`:
- Run `consistency-check.py --file <path> --strict`
- Bei rc != 0: Block + Alert

### Hook 2: Pre-Bootstrap
In `scripts/grid-bootstrap.{sh,ps1}` als erste Aktion:
- Run `rules-verify.py --halt-on-fail --grace-sec 300`
- Bei rc != 0: Halt Bootstrap

### Hook 3: CI/CD Lint
GitHub-Actions-Workflow `.github/workflows/consistency-check.yml` (noch nicht eingerichtet):
- Auf jeden Push: `consistency-check.py --dir docs/ --strict`

## Release-Tag-Workflow (neu)

Bei jedem Seed-Release:
1. `powershell scripts/build-seed-zip.ps1`  (erstellt ZIP)
2. `git tag -a seed-v<YYYY-MM-DD>-a -m "Seed-Release <datum>"`  (optional: `-s` fuer Signatur)
3. `git push origin seed-v<YYYY-MM-DD>-a`
4. Updaten `~/.claude/rules/.version` auf allen PCs: `echo "seed-v<YYYY-MM-DD>-a" > ~/.claude/rules/.version`

## Signatur (optional aber empfohlen)

Fuer `-s` (signed tag) ist GPG-Key + `user.signingkey` in git-config noetig:
```bash
git config --global user.signingkey <KEY-ID>
git config --global commit.gpgsign false  # Tags nur
```

Wenn kein GPG-Setup: annotated tag (`-a`) reicht fuer Content-Hash.

## Phase 2 kommt danach

- Schicht 1 Assertion-After-Write retroaktiv auf DF-05/06/07/08/10
- Schicht 2 Heartbeat-Monitor mit P3 Notification-by-Exception
- P2 Secondary PC2-Reciprocal-Watchdog

## Phase 3

- Schicht 4 Cross-Machine-Sync + P1 Manifest-Delta (Pull→Push)
- Schicht 6 Execution-Lease (P5b)
- P2 Primary Mac-External-Watchdog

## CRUX

- **K_0:** direkt geschuetzt (Rules-Drift-Erkennung)
- **Q_0:** direkt erhoeht (Consistency-Check fuer alle Handoffs)
- **I_min:** strukturell verankert (2 neue Scripts, 1 neuer Audit-Log-Stream)
- **L_Martin:** positiv (weniger Debug-Schleifen wenn Rules driften)
- **rho:** +25-70k EUR/J Phase-1 allein

[CRUX-MK]
