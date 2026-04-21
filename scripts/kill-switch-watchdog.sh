#!/usr/bin/env bash
# [CRUX-MK] Layer 0 — Kill-Switch-Watchdog (Master-Infrastructure PC 1)
# Martin-Direktive 2026-04-21 (Handoff Prio 4)
#
# Aufruf: als Scheduled-Task alle 5 Min (oder als Background-Loop)
#
# Zweck:
#   1. Prueft ob killed.flag existiert
#   2. Wenn JA: terminiert alle laufenden DF-Orchestrator + LiteLLM-Router + Heartbeat
#   3. Schreibt Audit-Event in kill-audit.jsonl
#   4. Benachrichtigt Martin (Console-Print, optional Desktop-Notification)
#
# CRUX-Impact: K_0-Max-Protection (verhindert rho-negative Cascades)
# Q_0: Audit-Trail
# I_min: strukturierte Kill-Ketten-Durchsetzung

set -uo pipefail

CRUX_DIR="${HOME}/.kemmer-grid"
mkdir -p "$CRUX_DIR"
KILL_FLAG="$CRUX_DIR/killed.flag"
KILL_AUDIT="$CRUX_DIR/kill-audit.jsonl"
LITELLM_PID_FILE="$CRUX_DIR/litellm-router.pid"

TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Kein Kill-Flag = kein Alarm
if [[ ! -f "$KILL_FLAG" ]]; then
  exit 0
fi

# --- Kill-Flag ist aktiv ---
FLAG_AGE_SEC=$(( $(date +%s) - $(stat -c %Y "$KILL_FLAG" 2>/dev/null || echo 0) ))

# Audit-Event
cat >> "$KILL_AUDIT" <<EOF
{"ts":"$TS","event":"kill-detected","flag_age_sec":$FLAG_AGE_SEC,"action":"terminate-all"}
EOF

echo "[CRUX-MK] KILL-SWITCH ACTIVE (age=${FLAG_AGE_SEC}s). Terminating grid..." >&2

# --- Terminate LiteLLM-Router ---
if [[ -f "$LITELLM_PID_FILE" ]]; then
  PID=$(cat "$LITELLM_PID_FILE")
  if [[ -n "$PID" ]] && kill -0 "$PID" 2>/dev/null; then
    kill "$PID" 2>/dev/null || true
    sleep 2
    kill -9 "$PID" 2>/dev/null || true
    echo "{\"ts\":\"$TS\",\"event\":\"terminated\",\"target\":\"litellm-router\",\"pid\":$PID}" >> "$KILL_AUDIT"
  fi
  rm -f "$LITELLM_PID_FILE"
fi

# --- Terminate aktive DF-Orchestrators (Python-Prozesse in Projects/dark-factories) ---
if command -v pgrep &>/dev/null; then
  DF_PIDS=$(pgrep -f "python.*dark-factories.*orchestrator\.py" 2>/dev/null || echo "")
  DF_PIDS_RUN=$(pgrep -f "python.*dark-factories.*run\.py" 2>/dev/null || echo "")
  for P in $DF_PIDS $DF_PIDS_RUN; do
    kill "$P" 2>/dev/null || true
    echo "{\"ts\":\"$TS\",\"event\":\"terminated\",\"target\":\"df-orchestrator\",\"pid\":$P}" >> "$KILL_AUDIT"
  done
fi

# --- Report-End ---
echo "[CRUX-MK] Kill-Switch-Watchdog: termination complete. Audit: $KILL_AUDIT" >&2
echo "  To re-enable grid: rm $KILL_FLAG  &&  verify kill-audit.jsonl" >&2

exit 0
