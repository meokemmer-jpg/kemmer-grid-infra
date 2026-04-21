---
name: codex-delegate
description: Delegiert Code-Review, Research-Synthesis, Adversarial-Cross-Check an Codex CLI (`codex exec`, `codex review`). Triggers "delegate to codex", "codex review", "gpt-5.4 check", automatisch bei Code-Review-Tasks und Cross-LLM-Haertung.
version: 1.0.0
crux-mk: true
aktiviert: 2026-04-19
meta-ebene: E3
---

# Skill: codex-delegate [CRUX-MK]

## Zweck

ChatGPT-Pro-Sunk-Cost ($200/Mo) maximal nutzen. Codex CLI als Default-Executor fuer:
- Code-Review (`codex review`)
- Adversarial-Cross-Check (gpt-5.4)
- Research-Synthesis (Deep Research Pro-Tier)
- Routine-Code-Gen (gpt-5.3-codex)

Referenz: `~/.claude/rules/chatgpt-pro-first.md`

## Triggers

- Explizit: "delegate to codex", "codex review", "gpt-5.4 check", "codex-delegate"
- Automatisch bei: Code-Review-Tasks, Pre-Commit-Validierung, Cross-LLM-Haertung

## Hard-No-Delegate

Wie alle -delegate Skills: K_0, Q_0, Phronesis, Meta-E4+, Cross-LLM-Synthese, Rule-Aenderungen → Claude Opus.

## Workflow

### Pre-Call: Model-Auswahl

```
CLASSIFY(task):
  if task_type == "code-review": use codex review (no -m needed)
  if task_type == "adversarial-cross-check": use `-m gpt-5.4`
  if task_type == "routine-code-gen": use `-m gpt-5.3-codex`
  if task_type == "quick-classification": use `-m gpt-5.4-mini`
  if task_type == "long-context-legacy": use `-m gpt-5.1-codex-max`
```

### Invocation-Patterns

```bash
# 1. Non-interactive exec (bereits in DF-03 und multi-llm-parallel genutzt):
codex exec --skip-git-repo-check "<prompt>"

# 2. Explicit Pro-Model:
codex exec -m gpt-5.4 "<adversarial-review-prompt>"

# 3. Code-Review (neu erschlossen):
codex review                    # aktueller Branch vs main
codex review --uncommitted      # staged/unstaged/untracked changes
codex review "focus: n+1 queries, injection risks"

# 4. Mit config override:
codex exec -c model=\"gpt-5.4\" -c sandbox_permissions=[\"disk-full-read-access\"] "<prompt>"

# 5. Via MCP (nach Claude-Restart):
# automatisch als mcp__codex-mcp__* Tools verfuegbar
```

### Capture-Output

```bash
codex exec --skip-git-repo-check "<prompt>" > /tmp/codex-$(date +%s).out 2>&1
```

### Output-Validation (Claude, minimaler Token)

- Output-Format check (erfuellt Prompt-Kriterium?)
- Bei Zweifel: Cross-Check mit Gemini (`multi-llm-parallel.sh` Option C)
- Bei Pass: integrate / commit / apply

## Beispiele

### Beispiel 1: Pre-Commit Code-Review
```bash
# In .git/hooks/pre-commit oder ad-hoc:
cd /path/to/repo
codex review --uncommitted || { echo "REVIEW FAILED — fix issues before commit"; exit 1; }
```

### Beispiel 2: Adversarial-Cross-Check fuer wichtige Decision
```bash
PROMPT="Adversarial review: Meine Hypothese ist X weil Y. Wo sind Schwachstellen?"
codex exec -m gpt-5.4 "$PROMPT" > /tmp/cross-check-$(date +%s).md
# Claude-Opus liest Output + entscheidet Go/Modify/Reject
```

### Beispiel 3: Routine Code-Gen delegiert
```bash
codex exec -m gpt-5.3-codex "Generate SQL migration for adding created_at timestamp to users table. PostgreSQL."
```

### Beispiel 4: Research-Synthesis (Pro-Deep-Research)
```bash
codex exec -m gpt-5.4 "Summarize last 30 days xAI API changes. Sources: changelog, blog posts, community discussions. Max 300 words."
```

## rho-Impact

Pro + max-genutzt:
- Lambda 20 Calls/Tag @ avg 20k tokens = 400k tokens/Tag
- Claude-Opus-Aequivalent: ~$30/Tag = $900/Mo OPEX
- Codex-Cost: flat $200/Mo (Pro-Abo)
- **Netto-Ersparnis: $700/Mo = €8400/Jahr**

Break-Even: 10 Calls/Tag (= 1 Pro-Monat amortisiert)

## Meta-Harness-Anbindung

- **DF-03 v2.x** nutzt bereits `codex exec` — Haupt-Use-Case ist Abstract-Synthesis
- **multi-llm-parallel Skill v1.1.0** Option C ruft `codex exec` parallel
- **Neu:** `codex review` als Pre-Commit-Hook-Kandidat (rules/chatgpt-pro-first.md)
- **Neu:** `codex-mcp` als Claude-Code-MCP-Tool nach Restart

## Falsifikations-Bedingung

- Codex-Output-Qualitaet vs Claude-Opus: Brier-Score-Drop > 20% bei delegierten Tasks
- Pro-Rate-Limit chronisch ueberschritten (Lambda > 50 Calls/Tag)
- gpt-5.4 entfernt ohne equivalenten Ersatz

Monatliches Review via `monthly-model-audit` Skill (siehe dort).

[CRUX-MK]
