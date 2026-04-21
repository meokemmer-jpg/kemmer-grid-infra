# ASWDF Scripts-Inventar [CRUX-MK]

**Status:** SKELETON — Build-Phase-B-G needed before production.

## Script-Inventar (alle pending Build)

| Script | Phase | Typ | Zweck |
|--------|:-----:|-----|-------|
| `phase1_audit.py` | 1 | Python | Frontmatter-Parser + Claim-Type-Classifier + O1-O5-Matrix-Evaluator |
| `phase2_adversarial.sh` | 2 | Bash | Parallel-Executor fuer Codex+Gemini+Grok+Copilot + Konvergenz-Analyzer |
| `phase3_nlm_loop.py` | 3 | Python | DF-06-Upload + NLM-Output-Extractor + Dissent-Integration-Engine |
| `phase4_game_theory.sh` | 4 | Bash | Codex-Nash-Solver + Claude-Synthese |
| `phase5_systems.sh` | 5 | Bash | Gemini-Feedback-Loops + Copilot-Benchmarks + Claude-Emergenz |
| `phase6_gate.py` | 6 | Python | Decision-Logic (STOP_SUCCESS/CONTINUE/STOP_*) |
| `phase7_persist.py` | 7 | Python | Dual-Persistence (NLM + KB + Fragment-Map + Rule-PROPOSAL) |
| `phase8_evolve.py` | 8 | Python | Pattern-Extraction + Config-Adjustments + Rule-PROPOSAL-Generation (async) |

## Abhaengigkeiten (Tools)

- `python3` (>=3.10)
- `bash` (Unix shell syntax, Cygwin/WSL on Windows)
- `gh` (GitHub CLI, fuer MCP-Toolsets)
- `codex` (ChatGPT Codex CLI, via `codex exec`)
- `gemini` (Google Gemini CLI)
- `copilot` (GitHub Copilot CLI)
- `grok-mcp` (Grok MCP-Server, via `mcp__grok-mcp__*`)
- `jq` (JSON-Verarbeitung)

## Environment-Variablen (Pflicht)

- `GEMINI_API_KEY` (fuer Gemini-Calls, via User-Environment)
- `XAI_API_KEY` (fuer Grok-MCP-Calls)
- `ANTHROPIC_API_KEY` (Claude-Synthese-Calls, Fallback)
- `FIRECRAWL_API_KEY` (optional, fuer Research-Research)

## Build-Status

- **Phase-A (Design)**: Complete. B201-Blueprint + SKILL.md + archon-config.yaml vorhanden.
- **Phase-B (Skill-Skeleton + Phase-1+2)**: PENDING. Scripts-Placeholder noch nicht implementiert.
- **Phase-C bis Phase-G**: Siehe `archon-config.yaml > build-roadmap`.

Implementation-Pattern: jedes Script hat Input-Contract + Output-Contract + Error-Handling.
Pentagon-Verfahren: Plan → Spec → Implement → Test → Refine.

[CRUX-MK]
