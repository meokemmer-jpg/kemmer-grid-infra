#!/bin/bash
# gemini-isolated.sh — Isolated Gemini Call with Post-Call Audit
# Usage: ./gemini-isolated.sh <claim-name> <prompt-file>
#
# CRUX-MK

set -e

CLAIM=$1
PROMPT_FILE=$2
WORKSPACE_MARKERS=("/Meine Ablage" "Claude-Knowledge-System" "branch-hub" "Work-D" "Work-C")

if [ -z "$CLAIM" ] || [ -z "$PROMPT_FILE" ]; then
    echo "Usage: $0 <claim-name> <prompt-file>"
    exit 1
fi

# Step 1: CWD-Wechsel
cd /tmp

# Step 2: Prompt mit Anti-Kontaminations-Klausel
PROMPT=$(cat "$PROMPT_FILE")
HARDENED_PROMPT="$PROMPT

WICHTIG: Antworte NUR aus deinem Wissensstand. KEINE Dateien im Workspace lesen. Keine Suche nach bestehenden Files. Cross-LLM-Unabhaengigkeit ist kritisch. Lambda-Honesty bei Unsicherheit."

# Step 3: API-Key
KEY=$(powershell.exe -Command "[Environment]::GetEnvironmentVariable('GEMINI_API_KEY', 'User')" 2>/dev/null | tr -d '\r\n')
if [ -z "$KEY" ]; then
    echo "ERROR: GEMINI_API_KEY not set in user env"
    exit 2
fi

# Step 4: Call
OUT_FILE="/tmp/${CLAIM}-gemini.out"
ERR_FILE="/tmp/${CLAIM}-gemini.err"
echo "$HARDENED_PROMPT" | GEMINI_API_KEY="$KEY" gemini -p "Adversarial kompakt DE." > "$OUT_FILE" 2> "$ERR_FILE"

# Step 5: Post-Call-Audit
CONTAMINATED=0
for marker in "${WORKSPACE_MARKERS[@]}"; do
    if grep -q "$marker" "$OUT_FILE" 2>/dev/null; then
        echo "CONTAMINATION DETECTED: marker '$marker' in output"
        CONTAMINATED=1
    fi
done

if [ "$CONTAMINATED" = "0" ]; then
    echo "CLEAN: 0 workspace markers detected. Output saved to $OUT_FILE"
else
    echo "DIRTY: Contamination detected. Retry recommended."
    exit 3
fi

# Report output-size
wc -c "$OUT_FILE" "$ERR_FILE"
