---
name: copilot-delegate
description: Delegiert Code-/Docs-/Research-Tasks an Copilot CLI (`copilot -p`) statt Claude-Opus-Tokens zu verbrennen. Triggers "delegate to copilot", "use copilot for", "copilot-delegate", automatisch bei Code-Gen/Docs/Refactor-Tasks ohne K_0/Q_0-Relevanz.
version: 1.0.0
crux-mk: true
aktiviert: 2026-04-19
meta-ebene: E3
---

# Skill: copilot-delegate [CRUX-MK]

## Zweck

Token-Engpass-Routing: Nicht-strategische Tasks an `copilot -p` delegieren statt
Claude-Opus. Faktor 27x Token-Ersparnis pro delegierbarem Task.

Referenz-Rule: `~/.claude/rules/copilot-cli-first.md`

## Triggers

- Explizit: "delegate to copilot", "use copilot", "copilot-delegate"
- Automatisch (Claude-Self-Routing): Code-Generation, Docs-Drafting, Refactoring,
  Lint-Fixes, Boilerplate, GitHub-API-Tasks (Issues/PRs/Actions)

## Hard-No-Delegate (immer Claude-Opus)

Siehe `rules/copilot-cli-first.md` — K_0, Q_0, Phronesis, Meta-Audit, Cross-LLM,
Rule-/CRUX-Aenderungen.

## Workflow

### Step 1: Task-Klassifikation (Claude, 0 Copilot-Tokens)

```
CLASSIFY(task):
  if K_0 or Q_0 or Phronesis or Meta-E4+: return CLAUDE
  if deterministic code/docs/fix: return COPILOT
  if GitHub-API / Issues / PRs / Actions: return COPILOT_GH_MCP
  else: return CLAUDE_WITH_COPILOT_DRAFT
```

### Step 2: Prompt-Bau (kompakt, 200-400 Worte)

```
PROMPT_TEMPLATE:
  Context: <2-3 Saetze>
  Task: <klar, mit Output-Kriterien>
  Constraints: <CRUX-relevant wenn anwendbar>
  Output-Format: <Datei / Code-Block / JSON / Markdown>
```

### Step 3: Copilot-CLI-Invocation

```bash
# Basis-Call:
copilot -p "$(cat <prompt-file>)" --allow-all-tools

# Mit Code-Kontext:
copilot -p "..." --add-dir /path/to/src --add-dir /path/to/tests

# Mit GitHub-MCP (Issues/PRs):
copilot -p "..." --add-github-mcp-toolset all

# Reasoning-Effort (low=cheap, xhigh=hard-tasks):
copilot -p "..." --effort high

# Capture-Output fuer Claude-Synthese:
copilot -p "..." > /tmp/copilot-out-$(date +%s).md
```

### Step 4: Output-Validation (Claude, minimaler Token)

- Quick-Scan: erfuellt Output das Format-Kriterium?
- Bei Zweifel: Cross-Check gegen 2. LLM (gemini/codex) BEVOR Claude-Opus-Deep-Review
- Bei Pass: commit / apply / integrate

### Step 5: Logging (rules/audit-trail.md §1)

```
{"ts":"ISO","branch":"name","action":"DELEGATE","target":"copilot-cli",
 "reason":"Token-Engpass-Routing","prompt_tokens":N,"ROI":"27x vs claude-opus"}
```

## Beispiele

### Beispiel 1: README-Entwurf fuer neues Skill
```bash
copilot -p "Write a concise README.md for ~/.claude/skills/copilot-delegate/
explaining usage, invocation patterns, and rho-ROI. Tone: terse, no emojis,
German tech with English code." --add-dir ~/.claude/skills/copilot-delegate
```

### Beispiel 2: Issues-Sweep via GitHub-MCP
```bash
copilot -p "List all open issues in meokemmer-jpg/kemmer-knowledge-system
labeled 'bug', sorted by age. Output as markdown table." \
--add-github-mcp-toolset all
```

### Beispiel 3: Code-Refactor
```bash
copilot -p "Refactor SAE-v8/core/governance.py: extract all magic numbers
into named constants in constants.py. Preserve test-suite compatibility." \
--add-dir SAE-v8/core --add-dir SAE-v8/tests --effort high
```

## rho-Impact

- Lambda 10 Tasks/Tag @ Claude-Opus-Aequivalent = $7/Tag = $2100/Jahr OPEX
- Nach Delegation = $0 Marginal (Pro+-Flat) + 27x Capacity-Expansion
- **Break-Even: sofort**

## Meta-Harness-Anbindung

- **meta-harness.md §8f (NEU):** Copilot-Executor-Pattern fuer Dark-Factories
- **archon-roadmap-orchestrator:** kann `copilot -p` als Executor-Node nutzen
- **DF-03 (Multi-LLM):** Copilot als 3. Flat-LLM neben Codex+Gemini

## Falsifikations-Bedingung

- Copilot-Output-Qualitaet < 80% Claude-Opus bei delegierbaren Tasks (Brier-Score, 20 Samples)
- Pro+-Kontingent chronisch exhausted
- Subscription-Wechsel / Service-Disruption

[CRUX-MK]
