#!/usr/bin/env bash
# [CRUX-MK] Layer 0 — LiteLLM-Router Start mit Layer-0-Gate
# Martin-Direktive 2026-04-21 "LiteLLM-Router live schalten"
#
# Aufruf:
#   start-litellm-router.sh                # Port 4000, Config aus router/
#   start-litellm-router.sh --port 4001    # Alternative Port
#   start-litellm-router.sh --detach       # Background (nohup/&)
#
# rho-Impact:   aktiviert 4-Tier-Routing Deterministic/Commodity/Premium/Local
#               spart Opus-Tokens (27x Faktor bei Copilot-Delegate)
# K_0:          geschuetzt (Kill-Switch-Check + crux-precall-hook bei Criticality >=0.7)
# Q_0:          geschuetzt (CRUX-Event-Logging pro LLM-Call)
# I_min:        strukturierter Einheits-Router fuer alle LLM-Calls

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
CRUX_CHECK="${SCRIPT_DIR}/crux-check.sh"
ROUTER_CONFIG="${REPO_ROOT}/router/litellm-router-config.yaml"

PORT="${LITELLM_PORT:-4000}"
HOST="${LITELLM_HOST:-127.0.0.1}"
DETACH=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)    PORT="${2:-4000}"; shift 2;;
    --host)    HOST="${2:-127.0.0.1}"; shift 2;;
    --detach)  DETACH=1; shift;;
    --help|-h)
      echo "Usage: start-litellm-router.sh [--port N] [--host H] [--detach]"
      exit 0;;
    *) shift;;
  esac
done

# Config-Existenz
if [[ ! -f "$ROUTER_CONFIG" ]]; then
  echo "[CRUX-MK] ERROR: Config not found: $ROUTER_CONFIG" >&2
  exit 1
fi

# CRUX-Check (Stage: router-start)
if [[ -x "$CRUX_CHECK" ]]; then
  bash "$CRUX_CHECK" \
    --action "start litellm-router port=${PORT}" \
    --estimated-rho "+2400 EUR/J (Opus-Token-Ersparnis durch Routing)" \
    --k0-risk "low" \
    --q0-risk "low" \
    --i-min "positive" \
    --l-martin "positive (Bandbreite entlastet)" \
    --wargame "both_passed" \
    --stage "router-start"
  CRUX_VERDICT=$?
  if [[ $CRUX_VERDICT -eq 1 ]]; then
    echo "[CRUX-MK] REJECT: LiteLLM-Router start blocked" >&2
    exit 1
  fi
fi

# Python Scripts-Dir PATH hinzufuegen (Windows-spezifisch)
WIN_SCRIPTS="/c/Users/marti/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0/LocalCache/local-packages/Python313/Scripts"
if [[ -d "$WIN_SCRIPTS" ]]; then
  export PATH="$PATH:$WIN_SCRIPTS"
fi

# Verify litellm available
if ! command -v litellm &>/dev/null; then
  echo "[CRUX-MK] ERROR: litellm not on PATH" >&2
  echo "  Install: pip install litellm" >&2
  exit 1
fi

# Log Router-Start
ROUTER_LOG="${HOME}/.kemmer-grid/router-events.jsonl"
TS_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "{\"ts\":\"${TS_START}\",\"event\":\"router-start\",\"host\":\"${HOST}\",\"port\":${PORT},\"config\":\"$(basename "$ROUTER_CONFIG")\"}" >> "$ROUTER_LOG"

echo "[CRUX-MK] Starting LiteLLM-Router:"
echo "  Config: $ROUTER_CONFIG"
echo "  Host:   $HOST"
echo "  Port:   $PORT"
echo "  Logs:   $ROUTER_LOG"

# Start
if [[ $DETACH -eq 1 ]]; then
  LOG_DIR="${HOME}/.kemmer-grid"
  mkdir -p "$LOG_DIR"
  nohup litellm --config "$ROUTER_CONFIG" --host "$HOST" --port "$PORT" \
    > "${LOG_DIR}/litellm-router.log" 2>&1 &
  PID=$!
  echo "[CRUX-MK] LiteLLM-Router running in background, PID=${PID}"
  echo "$PID" > "${LOG_DIR}/litellm-router.pid"
  echo "  Stop: kill $PID  or  kill \$(cat ${LOG_DIR}/litellm-router.pid)"
else
  exec litellm --config "$ROUTER_CONFIG" --host "$HOST" --port "$PORT"
fi
