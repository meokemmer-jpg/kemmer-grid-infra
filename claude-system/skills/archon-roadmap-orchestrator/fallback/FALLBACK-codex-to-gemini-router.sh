#!/bin/bash
# FALLBACK-codex-to-gemini-router.sh
#
# === FALLBACK-ROUTINE (NUR FALLBACK, NACH N SUCCESSFUL RUNS LOESCHBAR) ===
#
# Type: provider-fallback
# Reason: Codex (GPT-5.4) hat Windows-Sandbox-Probleme bei UNC-Pfaden
#         (CreateProcessAsUserW failed 1920). Wenn Codex fuer einen
#         Prompt crasht, routet dieses Script automatisch auf Gemini.
#
# To-Delete-When: Codex Windows-Sandbox-Bug gefixt UND
#                 30 aufeinanderfolgende Codex-Runs ohne Sandbox-Fehler
#
# Usage:
#   ./FALLBACK-codex-to-gemini-router.sh "prompt text" [output-file]
#
# Exit 0: success (entweder Codex ODER Gemini lieferte Output)
# Exit 1: beide failed

PROMPT="$1"
OUTFILE="${2:-/tmp/llm-output.txt}"
ERRFILE="${OUTFILE}.err"
LOG_PATH="G:/Meine Ablage/Claude-Knowledge-System/branch-hub/audit/fallback-routing.jsonl"

if [ -z "$PROMPT" ]; then
  echo "Usage: $0 '<prompt>' [output-file]" >&2
  exit 2
fi

# Try Codex first
cd /tmp 2>/dev/null
codex exec --skip-git-repo-check "$PROMPT" > "$OUTFILE" 2> "$ERRFILE"
CODEX_EXIT=$?
CODEX_SIZE=$(wc -c < "$OUTFILE")

# Check: if Codex failed OR output empty OR sandbox-error in stderr
SANDBOX_ERR=$(grep -c "CreateProcessAsUserW\|windows sandbox" "$ERRFILE" 2>/dev/null || echo 0)

if [ "$CODEX_EXIT" -eq 0 ] && [ "$CODEX_SIZE" -gt 100 ] && [ "$SANDBOX_ERR" -eq 0 ]; then
  # Codex success
  TS=$(date --iso-8601=seconds 2>/dev/null || date -Iseconds)
  echo "{\"ts\":\"$TS\",\"provider\":\"codex\",\"status\":\"success\",\"fallback_triggered\":false,\"size\":$CODEX_SIZE}" >> "$LOG_PATH"
  exit 0
fi

# Fallback to Gemini
KEY=$(powershell.exe -Command "[Environment]::GetEnvironmentVariable('GEMINI_API_KEY', 'User')" 2>/dev/null | tr -d '\r\n')
if [ -z "$KEY" ]; then
  TS=$(date --iso-8601=seconds 2>/dev/null || date -Iseconds)
  echo "{\"ts\":\"$TS\",\"provider\":\"none\",\"status\":\"failed\",\"reason\":\"codex-failed+gemini-key-missing\"}" >> "$LOG_PATH"
  exit 1
fi

echo "$PROMPT" | GEMINI_API_KEY="$KEY" gemini -p "Antwort strukturiert, deutsch." > "$OUTFILE" 2> "$ERRFILE"
GEMINI_EXIT=$?
GEMINI_SIZE=$(wc -c < "$OUTFILE")

TS=$(date --iso-8601=seconds 2>/dev/null || date -Iseconds)
if [ "$GEMINI_EXIT" -eq 0 ] && [ "$GEMINI_SIZE" -gt 100 ]; then
  echo "{\"ts\":\"$TS\",\"provider\":\"gemini\",\"status\":\"success\",\"fallback_triggered\":true,\"size\":$GEMINI_SIZE,\"codex_fail_reason\":\"sandbox-or-empty\"}" >> "$LOG_PATH"
  exit 0
fi

echo "{\"ts\":\"$TS\",\"provider\":\"none\",\"status\":\"failed\",\"reason\":\"both-failed\",\"codex_size\":$CODEX_SIZE,\"gemini_size\":$GEMINI_SIZE}" >> "$LOG_PATH"
exit 1
