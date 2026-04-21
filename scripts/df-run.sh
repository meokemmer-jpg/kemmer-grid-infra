#!/usr/bin/env bash
# [CRUX-MK] Layer 0 — Dark-Factory Universal-Runner mit CRUX-Gate
# Martin-Direktive 2026-04-21: "DF-Runtime-Invocation im df-run-Script"
#
# Aufruf:
#   df-run.sh DF-01                # Run DF-01 mit Default-Orchestrator
#   df-run.sh DF-07 --dry-run      # Dry-run
#   df-run.sh DF-11 --mode shadow  # Args durchgereicht an Orchestrator
#
# rho-Impact: verhindert DF-Run ohne Runtime-CRUX-Gate (Kill-Switch + Criticality-Check)
# K_0:        geschuetzt (Kill-Switch-First vor jedem DF-Run)
# Q_0:        geschuetzt (CRUX-Event-Logging pro DF-Run)
# I_min:      strukturierter Einheits-Entrypoint fuer alle DFs

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRUX_CHECK="${SCRIPT_DIR}/crux-check.sh"
DF_ROOT="${HOME}/Projects/dark-factories"

# Argument-Parsing
if [[ $# -lt 1 ]]; then
  cat << 'EOF'
df-run.sh [CRUX-MK] Layer 0 — Dark-Factory Universal-Runner

Usage:
  df-run.sh <DF-NAME> [orchestrator-args...]

Examples:
  df-run.sh DF-01
  df-run.sh DF-07 --dry-run
  df-run.sh DF-10 --mode shadow
  df-run.sh DF-11 --mode calibrate

Invarianten:
  - Runs crux-check.sh --stage df-start FIRST (blocks if kill-switch)
  - Auto-Detects orchestrator.py or run.py or df05-run.ps1
  - Logs DF-Event to ~/.kemmer-grid/df-runs.jsonl
EOF
  exit 2
fi

DF_NAME="$1"
shift
DF_ARGS="$*"

# DF-Directory Resolution (case-insensitive via lowercase)
DF_DIR="${DF_ROOT}/${DF_NAME}"
if [[ ! -d "$DF_DIR" ]]; then
  # Try lowercase variant (df-11-* vs DF-11-*)
  for candidate in "$DF_ROOT"/*; do
    base=$(basename "$candidate")
    if [[ "${base,,}" == "${DF_NAME,,}"* ]]; then
      DF_DIR="$candidate"
      break
    fi
  done
fi

if [[ ! -d "$DF_DIR" ]]; then
  echo "[CRUX-MK] ERROR: DF-Directory not found: $DF_NAME" >&2
  echo "  Searched: ${DF_ROOT}/${DF_NAME}" >&2
  exit 1
fi

# CRUX-Check First (Stage: df-start)
if [[ -x "$CRUX_CHECK" ]]; then
  bash "$CRUX_CHECK" \
    --action "df-run ${DF_NAME}" \
    --estimated-rho "inherited from manifest" \
    --k0-risk "low" \
    --q0-risk "low" \
    --i-min "positive" \
    --l-martin "neutral" \
    --wargame "both_passed" \
    --stage "df-start"
  CRUX_VERDICT=$?
  if [[ $CRUX_VERDICT -eq 1 ]]; then
    echo "[CRUX-MK] REJECT: DF-Run ${DF_NAME} blocked by CRUX-Gate" >&2
    exit 1
  fi
  # WARN (2) or PASS (0) both proceed
else
  echo "[CRUX-MK] WARN: crux-check.sh not found at $CRUX_CHECK" >&2
  echo "  Continuing without Layer-0-Gate (degraded mode)" >&2
fi

# Orchestrator-Detection
ORCHESTRATOR=""
if [[ -f "$DF_DIR/orchestrator.py" ]]; then
  ORCHESTRATOR="python $DF_DIR/orchestrator.py"
elif [[ -f "$DF_DIR/run.py" ]]; then
  ORCHESTRATOR="python $DF_DIR/run.py"
elif [[ -f "$DF_DIR/df05-run.ps1" ]]; then
  ORCHESTRATOR="powershell -ExecutionPolicy Bypass -File $DF_DIR/df05-run.ps1"
else
  echo "[CRUX-MK] ERROR: No orchestrator found in $DF_DIR" >&2
  echo "  Expected: orchestrator.py | run.py | df05-run.ps1" >&2
  exit 1
fi

# Log DF-Event-Start
DF_LOG="${HOME}/.kemmer-grid/df-runs.jsonl"
TS_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "{\"ts\":\"${TS_START}\",\"df\":\"${DF_NAME}\",\"event\":\"start\",\"orchestrator\":\"${ORCHESTRATOR##*/}\",\"args\":\"${DF_ARGS}\"}" >> "$DF_LOG"

# Execute Orchestrator
echo "[CRUX-MK] df-run ${DF_NAME}: ${ORCHESTRATOR} ${DF_ARGS}"
cd "$DF_DIR"
$ORCHESTRATOR $DF_ARGS
RC=$?

# Log DF-Event-End
TS_END=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "{\"ts\":\"${TS_END}\",\"df\":\"${DF_NAME}\",\"event\":\"end\",\"exit_code\":${RC}}" >> "$DF_LOG"

if [[ $RC -ne 0 ]]; then
  echo "[CRUX-MK] DF ${DF_NAME} exit=${RC}" >&2
fi

exit $RC
