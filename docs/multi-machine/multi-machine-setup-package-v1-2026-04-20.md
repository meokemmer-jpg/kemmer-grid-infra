---
type: setup-package
version: v1.0
date: 2026-04-20
from: Opus47-Work-D2 (PC 1 Master)
to: Neue PC-Instanz (Worker) — VOR Bootstrap zu lesen
depends-on: session_bootstrap_multi_machine_2026-04-20.md
crux-mk: true
---

# Multi-Machine Setup-Paket v1.0 [CRUX-MK]

**Warum dieses File:** Ohne Python, CLIs, API-Keys und Zugaenge ist die Claude-Instanz auf dem neuen PC **eingeschraenkt**. Bootstrap laeuft, aber Dark-Factories/Cross-LLM/NLM-Spiegel-Lesen alles tot. Dieses File deckt **ALLE Abhaengigkeiten** die vor Bootstrap installiert sein muessen.

**Reihenfolge:** Dieses File → `session_bootstrap_multi_machine_2026-04-20.md` → normal Bootstrap.

---

## 1. Betriebssystem + Privileges

| Item | Was | Warum |
|------|-----|-------|
| OS | Windows 10/11 (Build 22000+) | Primary-Target. Linux/Mac Version spaeter. |
| User-Rechte | Lokaler Admin | Fuer winget/npm global/Scheduled-Tasks-Pruefung |
| PowerShell | v7.4+ empfohlen (v5.1 geht auch) | Fuer Env-Var-Setting + Hook-Scripts |
| Disk-Space | min 50 GB frei | Claude Code + Models + NLM-Spiegel + Git-Repo |
| RAM | min 16 GB, 32 GB empfohlen | fuer sentence-transformers + playwright + Claude Code |

## 2. Core-Installs (Pflicht vor Claude Code)

**Via winget (Admin-PowerShell):**
```powershell
winget install Python.Python.3.12           # 3.12+ Pflicht (fuer nlm-meta-harness-archon + DF-Scripts)
winget install OpenJS.NodeJS.LTS             # Node v24 LTS (fuer MCP-Servers, CLIs)
winget install Git.Git                       # Git
winget install GitHub.cli                    # gh CLI (Auth + PR)
winget install Microsoft.VisualStudioCode    # optional, aber praktisch
```

**Via Chocolatey (Alternative):**
```powershell
choco install python311 nodejs-lts git gh -y
```

**Validate:**
```powershell
python --version   # MUSS 3.12+
node --version     # MUSS v20+
git --version      # MUSS 2.40+
gh --version       # MUSS 2.40+
```

## 3. Claude Code Installation

```powershell
# Via npm
npm install -g @anthropic-ai/claude-code

# Oder via Anthropic Install-Script (wenn verfuegbar)
# curl -fsSL https://claude.com/install.sh | sh

# Validate
claude --version   # MUSS v2.0+
```

**Login:**
```powershell
claude  # startet, verlangt Login via Browser
```

Nach Login: `~/.claude/` Ordner existiert. **Der bekommt dann Seed-Import — siehe §7.**

## 4. CLI-Toolchain (flat-LLM-Delegation)

**Pflicht (alle):**
```powershell
# GitHub Copilot CLI (braucht Copilot Pro+ Subscription)
gh extension install github/copilot-cli
# Dann: gh copilot explain | gh copilot suggest
# Alt: copilot -p "prompt" (separater CLI falls gh-copilot-cli reicht nicht)

# Codex CLI (ChatGPT Pro)
npm install -g @openai/codex
# Dann: codex login (Browser-OAuth)
# Test: codex exec --skip-git-repo-check "hello"

# Gemini CLI (Google AI Studio / Gemini Ultra)
npm install -g @google/gemini-cli
# Setzt GEMINI_API_KEY env-var voraus
# Test: gemini --version → 0.38.2+
# Dann: gemini -p "hello"

# uv (fuer grok-mcp via Python)
winget install astral-sh.uv
# Test: uv --version
```

**Validate aller CLIs:**
```powershell
foreach ($cmd in 'python','node','npm','git','gh','claude','codex','gemini','uv') {
    $found = (Get-Command $cmd -ErrorAction SilentlyContinue)
    if ($found) { Write-Host "OK: $cmd" } else { Write-Host "MISSING: $cmd" -ForegroundColor Red }
}
```

## 5. Python-Packages (Master + Worker)

```powershell
# Worker MUSS:
pip install sentence-transformers   # 5.4+ (DF-06 v2.4 Embedding-Shannon)
pip install playwright              # 1.58+ (Chrome-MCP)
python -m playwright install chromium  # Browser herunterladen

# Master ZUSATZLICH:
pip install notebooklm-py           # 0.3.4 (nur Master wegen NLM-Single-Login, KR-5)
```

## 6. MCP-Server-Konfiguration

`~/.claude/settings.json` MUSS diese MCP-Servers haben (kopiert aus Master-Seed):
- **context7** (npx @context7/mcp)
- **playwright** (npx @playwright/mcp)
- **firecrawl** (@firecrawl/mcp, braucht FIRECRAWL_API_KEY)
- **codex-mcp** (`codex mcp-server` stdio, braucht codex-Login)
- **grok-mcp** (via uv, braucht XAI_API_KEY)

**Pruefen nach Seed-Import:**
```powershell
python -c "import json; print('\n'.join(json.load(open('C:/Users/marti/.claude/settings.json')).get('mcpServers',{}).keys()))"
```

## 7. Seed-Import — ~/.claude/ Populaten

**WICHTIG:** GitHub-Repo `/rules/` ist OUTDATED (9 Files statt 40 — siehe CR-Warnung unten). Verlaesslicher Weg:

### Option A (empfohlen, schnell): USB/Netzwerk-Share vom Master

Auf PC 1 (Master):
```powershell
### PATCH 2026-04-21: Korrigierter Seed-Sync-Pfad (ersetzt alte Optionen)

**Problem identifiziert durch Worker0001@PC3 (L1):** `G:/Seed-Exports/` existierte nicht, nur 9 outdated Rules auf G: sichtbar. Behoben durch zwei echte Quellen.

**Jede neue Machine hat 2 redundante Pfade — waehle einen:**

### Option A (PRIMARY): GitHub-Clone (empfohlen, immer frisch)

```powershell
# Einmalig: Repo clonen (auf User-Home)
mkdir $env:USERPROFILE\Projects -ErrorAction SilentlyContinue
cd $env:USERPROFILE\Projects
git clone https://github.com/meokemmer-jpg/kemmer-grid-infra.git
cd kemmer-grid-infra

# Claude-System installieren (40+ Rules, CLAUDE.md, Skills, Scripts)
# Windows:
robocopy "claude-system\rules" "$env:USERPROFILE\.claude\rules" /E /XO
robocopy "claude-system\skills" "$env:USERPROFILE\.claude\skills" /E /XO
robocopy "claude-system\scripts" "$env:USERPROFILE\.claude\scripts" /E /XO
Copy-Item "claude-system\CLAUDE.md" "$env:USERPROFILE\.claude\CLAUDE.md" -Force

# Settings-Template (PC-spezifische Keys danach manuell editieren):
Copy-Item "docs\settings.json.template" "$env:USERPROFILE\.claude\settings.json" -Force
```

**Update-Pfad (immer wenn neue Rules dazu kommen):**
```powershell
cd $env:USERPROFILE\Projects\kemmer-grid-infra
git pull
robocopy "claude-system\rules" "$env:USERPROFILE\.claude\rules" /E /XO
```

### Option B (FALLBACK): ZIP-Extract von Drive-G

Nutze wenn: kein GitHub-Auth, offline-Setup, Mac ohne git-tooling.

```powershell
# ZIP ist LIVE auf: G:\Meine Ablage\Seed-Exports\kemmer-seed-export-YYYY-MM-DD.zip
# Erzeugt durch PC 1 Master via: powershell scripts/build-seed-zip.ps1
Expand-Archive -Path "G:\Meine Ablage\Seed-Exports\kemmer-seed-export-2026-04-21.zip" `
               -DestinationPath "$env:USERPROFILE\.claude" -Force
```

**Mac (bash):**
```bash
unzip -o "/Volumes/GoogleDrive/My Drive/Seed-Exports/kemmer-seed-export-2026-04-21.zip" \
      -d "$HOME/.claude/"
```

**Drive-Sync-Hinweis:** Bei File-Stream-Google-Drive muss der ZIP vor Extract lokal gecached sein (Rechtsklick → "Offline verfuegbar").

### Option C (minimal, als Notfall): Rules-only-Copy

Nur die 40+ Rules reichen fuer CRUX-Grundbetrieb. Skills on-demand.

```powershell
cd $env:USERPROFILE\Projects\kemmer-grid-infra
Copy-Item "claude-system\rules\*.md" -Destination "$env:USERPROFILE\.claude\rules\" -Force
```

### Hash-Verify (optional, nach Sync)

```powershell
# Sicherheit: Pruefe dass lokale Rules-Count matcht
$local = (Get-ChildItem "$env:USERPROFILE\.claude\rules\*.md").Count
$repo = (Get-ChildItem "$env:USERPROFILE\Projects\kemmer-grid-infra\claude-system\rules\*.md").Count
Write-Host "Local: $local | Repo: $repo | Match: $($local -eq $repo)"
```

## 8. Environment Variables (User-Scope, Pflicht)

**Setup via PowerShell (mit User-Scope, persistent):**
```powershell
# Pflicht
[Environment]::SetEnvironmentVariable('GEMINI_API_KEY', '<key>', 'User')
[Environment]::SetEnvironmentVariable('ENABLE_PROMPT_CACHING_1H', 'true', 'User')  # rules/token-orchestration.md §1.2

# Optional aber empfohlen (Cross-LLM-Haertung)
[Environment]::SetEnvironmentVariable('XAI_API_KEY', '<key>', 'User')               # Grok
[Environment]::SetEnvironmentVariable('OPENAI_API_KEY', '<key>', 'User')           # ChatGPT (Codex nutzt OAuth, aber Env hilft)
[Environment]::SetEnvironmentVariable('PERPLEXITY_API_KEY', '<key>', 'User')       # Perplexity
[Environment]::SetEnvironmentVariable('FIRECRAWL_API_KEY', '<key>', 'User')        # Firecrawl

# MACHINE_ROLE (fuer multi-machine-coordination.md.PROPOSAL)
[Environment]::SetEnvironmentVariable('MACHINE_ROLE', 'WORKER-E', 'User')          # oder MASTER/WORKER-F/WORKER-G

# Neu-Laden (neue Session oder reboot)
```

**Sicherheits-Hinweis:** Keys NIEMALS in PowerShell-Command-Line (Readline-History). Nutze `Read-Host -AsSecureString` oder manuell in User-Env-Var-GUI setzen.

## 9. GitHub-Zugang

```powershell
gh auth login  # Browser-Flow, waehle Account mit kemmer-knowledge-system-Access
gh auth status # verify

# Repo-Clone (fuer Seed + Updates):
gh repo clone meokemmer-jpg/kemmer-knowledge-system "$env:USERPROFILE/kks-mirror"
```

**Rechte benoetigt:** Read + Feature-Branch-Push + PR-Create auf `meokemmer-jpg/kemmer-knowledge-system`.

## 10. Google Drive File Stream

- Mit **Martin's Google-Account** angemeldet
- Drive-Buchstabe muss **G:** sein (hardcoded in vielen Skills/Rules)
- Offline-Kopie fuer kritische Files aktivieren (Right-Click → "Fuer Offline-Zugriff verfuegbar")

**Validate:**
```powershell
Test-Path "G:/Meine Ablage/Claude-Knowledge-System/branch-hub/BEACON.md"  # MUSS True
Test-Path "G:/Meine Ablage/Claude-Vault/00-moc"                           # MUSS True
```

## 11. Subscriptions (was Martin bereits bezahlt, Workerer brauchen Login)

| Subscription | Zweck | Login-Weg | Rate-Limit |
|--------------|-------|-----------|------------|
| **Anthropic Console/Max** | Claude Opus 4.7 + Haiku/Sonnet | `claude` CLI → Browser-OAuth | per-account (KRITISCH, siehe Wargame 1) |
| **GitHub Copilot Pro+** ($39/Mo) | Copilot CLI, 1500 Premium-Requests/Mo | `gh auth login` mit Copilot-Account | flat bis 1500, dann $0.04/req |
| **ChatGPT Pro** ($200/Mo) | Codex CLI, alle gpt-5.x, 6x Rate vs Plus | `codex login` Browser | Pro-Tier |
| **SuperGrok Heavy** ($300/Mo) | grok-4.20-multi-agent, X-Live-Search | XAI_API_KEY Env-Var | pro-account |
| **Gemini Ultra** (bundle Google One) | Gemini 2.5 Pro CLI, 1M context | GEMINI_API_KEY | pro-account |
| **Perplexity Ultimate** ($40/Mo) | WebSearch primary | PERPLEXITY_API_KEY | pro-account |

**Entscheidung pending (Wargame 1):** Ob Claude/andere Subscriptions per-account oder per-machine rate-limited sind. Das ist fundamental fuer ob Multi-Machine-Hebel funktioniert.

## 12. Scheduled-Tasks Policy (KRITISCH — MR-1 Verletzung = Disaster)

**Auf Worker-PC MUSS leer sein:**
```powershell
schtasks /query /fo LIST | Select-String -Pattern "DF-|NLM-|Claude-|Vault-|Archon-"
# Wenn Output: Liste ausgeben, Martin fragen, einzeln deleten
schtasks /delete /tn "DF-05-auto-commit-push" /f  # Beispiel
```

**Nur Master hat:**
- DF-05-auto-commit-push (30min)
- DF-06 NLM-Meta-Harness-Archon (daily 02:00)
- DF-07-model-audit-monthly (1. d. Monats 03:00)
- DF-08-Weekly-Scan (SUN 04:00)
- DF-08-Hourly-Idle (stuendlich)
- DF-10-token-intelligence-weekly (SAT 03:03)
- NLM-Archon-Weekly-Meta-Loop (SUN 03:00)
- Claude-Vault-Activity-Stats-Hourly
- vault-hub-sync-daily (07:00)
- Claude-Warm-Boot (daily 05:00)
- DF-drive-sync-dedup (daily 06:45)

## 13. Firewall + Netzwerk (fuer Multi-Machine + Gemma4-Grid)

**Outbound (alle PCs):**
- api.anthropic.com:443
- api.openai.com:443
- generativelanguage.googleapis.com:443
- api.x.ai:443
- api.perplexity.ai:443
- api.firecrawl.dev:443
- github.com:443
- drive.google.com:443 + notebooklm.google.com:443

**Inbound (falls PC als LLM-Server):**
- 11434 (Ollama)
- 1234 (LM Studio)
- 8080 (llama.cpp)
- 4000 (LiteLLM Proxy, spaeter)

**LAN-Discovery (fuer Grid):**
- mDNS/Bonjour aktiv (Windows: iTunes oder Bonjour-Service)
- oder statische LAN-IPs dokumentiert in `~/.claude/grid-endpoints.json`

## 14. Pre-Bootstrap-Check-Script

Vor dem ersten Bootstrap auf neuer PC (nach §§1-13 abgeschlossen):

```powershell
# Speichern als C:/temp/pre-bootstrap-check.ps1
$checks = @{
    'Drive-G' = (Test-Path "G:/Meine Ablage/Claude-Knowledge-System/branch-hub/BEACON.md")
    'Python'  = ($null -ne (Get-Command python -ErrorAction SilentlyContinue))
    'Node'    = ($null -ne (Get-Command node -ErrorAction SilentlyContinue))
    'Git'     = ($null -ne (Get-Command git -ErrorAction SilentlyContinue))
    'GH'      = ($null -ne (Get-Command gh -ErrorAction SilentlyContinue))
    'Claude'  = ($null -ne (Get-Command claude -ErrorAction SilentlyContinue))
    'Codex'   = ($null -ne (Get-Command codex -ErrorAction SilentlyContinue))
    'Gemini'  = ($null -ne (Get-Command gemini -ErrorAction SilentlyContinue))
    'UV'      = ($null -ne (Get-Command uv -ErrorAction SilentlyContinue))
    'GH-Auth' = (gh auth status 2>&1 | Select-String "Logged in").Count -gt 0
    'GEMINI_API_KEY' = $null -ne [Environment]::GetEnvironmentVariable('GEMINI_API_KEY','User')
    'MACHINE_ROLE'   = $null -ne [Environment]::GetEnvironmentVariable('MACHINE_ROLE','User')
    'Rules-Count'    = (Get-ChildItem "$env:USERPROFILE/.claude/rules/*.md" -ErrorAction SilentlyContinue).Count
    'Scheduled-Tasks-Clean' = -not (schtasks /query /fo LIST 2>$null | Select-String -Pattern "DF-|NLM-|Claude-|Vault-")
}
$checks.GetEnumerator() | ForEach-Object {
    $color = if ($_.Value -eq $true -or ($_.Value -is [int] -and $_.Value -ge 30)) { "Green" } else { "Red" }
    Write-Host ("{0,-24} {1}" -f $_.Key, $_.Value) -ForegroundColor $color
}
```

Bei **Rot** (ausser "Scheduled-Tasks-Clean" auf Master, das MUSS False sein): **STOP**, Item fixen, erneut laufen.

## 15. Warnungen (aus CR-2026-04-19-001 + Drive-Sync-Finding gelernt)

- **GitHub-Repo `/rules/` ist veraltet** (9 Files statt 40). Nutze Seed-Export oder Drive-G-Snapshot, NICHT `git clone` als Rules-Quelle.
- **Drive-Sync hat KEINE Merge-Auflösung.** Zwei PCs schreiben parallel dieselbe Datei = Duplikat-Kaskade. Mitigation: Instanz-Workspaces + BEACON-Heartbeat-Lock.
- **Pre-Compact-Write-Zwang (Antifragile M9)** gilt auch auf Workern. Bei "kompakt"-Trigger ZUERST 6 Pflicht-Artefakte persistieren, dann Summary.
- **Anthropic Rate-Limit-Policy** (per-account vs per-machine) ist **derzeit unklar**. Siehe Wargame 1. Bei per-account: Claude-Hebel-Effekt = 0 fuer Opus-Tasks, aber >0 fuer Delegate.

## 16. Minimum Working Setup (falls Zeit knapp)

Wenn du nicht alles installieren kannst, MUSS zumindest:
- Drive-G + Python + Node + Git + GitHub-CLI + **Claude Code + Gemini CLI** installiert
- GEMINI_API_KEY + MACHINE_ROLE Env-Vars gesetzt
- Rules-Kopie (Option C in §7)
- KEINE Scheduled-Tasks

Das erlaubt: 60-70% der Worker-Tasks. Voll-Funktionalitaet braucht §§1-14 komplett.

## 17. Nach-Setup-Validation

Nach Setup, VOR Bootstrap:

```powershell
C:/temp/pre-bootstrap-check.ps1
```

Wenn alles Gruen (ausser "Scheduled-Tasks-Clean" = True):

```powershell
# Erster Claude-Code-Start
cd "G:/Meine Ablage"
claude  # oder claude -p "prompt"
```

Und als ersten Prompt:

> "Ich bin Claude-Instanz auf PC 2. Lies `C:/Users/marti/.claude/projects/G--Meine-Ablage/memory/session_bootstrap_multi_machine_2026-04-20.md` + dieses Setup-Paket-File und fuehre Bootstrap aus."

---

## Abhaengigkeits-Matrix (wenn etwas fehlt, was ist kaputt)

| Fehlend | Was funktioniert nicht |
|---------|------------------------|
| Python 3.12+ | DF-Scripts, nlm-meta-harness-archon, Hook-Scripts |
| Node.js | npx-based CLIs (context7, playwright, firecrawl, codex-mcp) |
| sentence-transformers | DF-06 v2.4 Embedding-Shannon (fallback auf v2.3 lex-only) |
| playwright + chromium | Chrome-MCP, Claude_Preview |
| gh CLI | PR-Erstellung, Issue-Tracking |
| gemini CLI | Cross-LLM-Runs (Gemini-Leg) |
| codex CLI | ChatGPT-Pro-Tier-Nutzung, codex-mcp |
| uv | grok-mcp startet nicht |
| GEMINI_API_KEY | Cross-LLM-Verdict-Runs unvollstaendig |
| MACHINE_ROLE | Multi-Machine-Coordination-Rule greift nicht |
| Rules-Kopie | Bootstrap-Regeln nicht geladen (CRUX-Drift-Gefahr) |
| Drive-G | alles tot (Vault + Branch-Hub unerreichbar) |

---

## rho-Impact des Setup-Pakets

- **Ohne Setup:** PC 2 Claude-Session = nur 20-30% funktional, Netto rho **negativ** (Martin-Rescue-Zeit > Worker-Gewinn)
- **Mit Setup (§§1-14):** PC 2 voll funktional = rho-Prognose `multi-machine-coordination-v1-2026-04-20.md` Vollausbau gilt (+18k-54k EUR/J)
- **Setup-Zeit:** 45-90 Min (inkl. Subscriptions-Login + Seed-Import)
- **Break-Even:** 2-4 Sessions nach Setup-Abschluss

## Versionierung

Dieses File ist v1.0. Nach PC-2-Erst-Boot wird es basierend auf realen Problemen evolved.
Skill `seed-export` wird Setup-Paket in Zip mit einbauen (TODO: skill-update).

[CRUX-MK]
