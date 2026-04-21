---
name: github-bauplan-publish
description: Archon-Workflow der Bauplaene/Findings/Cross-LLM-Files aus branch-hub/ und Claude-Vault/canon/ nach meokemmer-jpg/kemmer-knowledge-system GitHub pusht. Triggers "publish bauplan", "github push blueprint", "share finding on git", automatisch nach CROSS-LLM-2OF3-HARDENED-Verdict.
type: skill-archon-workflow
tier: 1
meta-ebene: E3 (Methoden-Audit ueber Wissens-Publikation)
crux-mk: true
version: 1.0.0
created: 2026-04-19
depends-on:
  - gh CLI (GitHub)
  - git
  - powershell (Windows)
---

# Skill: github-bauplan-publish [CRUX-MK]

## Zweck
Ein-Kommando-Publikation von Bauplaenen, Findings, Cross-LLM-Outputs nach GitHub-Repo `meokemmer-jpg/kemmer-knowledge-system`. Branch-uebergreifende Sichtbarkeit, externe Zusammenarbeit, Archiv-Qualitaet.

## 5-Phasen-Workflow

### Phase 1: Classify
Input: File-Pfad
Output: Target-Pfad im Repo
- `Claude-Vault/canon/blueprints/B*.md` -> `blueprints/`
- `branch-hub/findings/*.md` -> `findings/`
- `branch-hub/cross-llm/*.md` -> `cross-llm/`
- Code-Files (z.B. KPM-Patches) -> `code/<domain>/`
- Skills/Rules (bei Martin-Approval) -> `skills/` oder `rules/`

### Phase 2: Pre-Flight
- gh auth status pruefen
- Repo-Clone lokal aktuell (cd /tmp/kks-repo && git pull)
- Target-Verzeichnis existiert? (mkdir -p falls nicht)
- File-Size-Cap (>500KB Warnung)
- Secrets-Scan (keine API-Keys/Tokens in File)

### Phase 3: Stage
- Copy File(s) in lokalen Clone
- Frontmatter auf `status: PUBLISHED-TO-GITHUB` updaten (optional)
- git add <target>

### Phase 4: Commit+Push
- Commit-Message-Template: `[<branch>] <type>: <short-title> (<date>)`
- Body: auto-generierte 3-Zeilen-Zusammenfassung aus File-Frontmatter
- git push mit Rebase-Protection (nicht force)

### Phase 5: Report
- Commit-Hash an Caller zurueckgeben
- BEACON-Eintrag-Draft mit URL
- Optional: GitHub-Issue zum Diskussions-Anlass

## Invocation-Patterns

### Single-File
```
# Via Skill-Tool mit Arg: Pfad
github-bauplan-publish "G:/Meine Ablage/Claude-Vault/canon/blueprints/B200-...md"
```

### Batch
```
# Mehrere Files, gemeinsamer Commit
github-bauplan-publish "B200-*.md" "cross-llm/2026-04-19-work-d-heylou-*.md"
```

### Auto-Publish-Trigger (bei HARDENED)
```yaml
# settings.json Hook:
PostWrite:
  pattern: branch-hub/cross-llm/*.md
  condition: frontmatter.verdict contains "HARDENED"
  action: skill:github-bauplan-publish
```

## Tool-Dependencies
- `gh` CLI (GitHub auth via `gh auth login`)
- `git` (rebase-Protection)
- `powershell.exe` (Windows Env-Vars)
- Python-optional fuer Frontmatter-Parsing

## Anti-Patterns
- Push von PRIVATE/CONFIDENTIAL-markierten Files ohne Martin-Approval
- Secrets in Files (.env, credentials, API-Keys)
- Force-Push auf main
- Commit ohne Frontmatter-Validierung

## rho-Impact
- **Cross-Branch-Visibilitaet**: +10-30k EUR/J (Doppelarbeit verhindert)
- **Externe Zusammenarbeit** (bei Business-Partner-Einbindung spaeter): +50-200k/J Option-Wert
- **Archiv-Qualitaet**: Git-History dokumentiert Evolution

## Falsifikations-Bedingung
- Wenn nach 30 Tagen 0 Bauplaene gepusht: Skill nicht gebraucht -> archivieren
- Wenn Secret-Leak passiert: Skill-Revision Pflicht + Hook-Enforcement

## CRUX-Bindung
- K_0: geschuetzt durch Secrets-Scan
- Q_0: Branch-uebergreifende Konsistenz
- I_min: strukturierte Publikation
- W_0: Martin-Zeit gespart (kein manuelles git push)

## SAE-Isomorphie
MYZ-30 Event-Router: Files werden nach Frontmatter-Typ und Pfad-Pattern nach Domain geroutet (blueprints/findings/cross-llm/code/skills/rules). Trinity-Pattern auf Publikations-Ebene: Conservative (dry-run), Aggressive (direct-push), Contrarian (PR-based Review).

[CRUX-MK]
