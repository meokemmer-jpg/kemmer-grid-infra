#!/usr/bin/env bash
# [CRUX-MK] Layer 0 — Kemmer-Grid Heartbeat (Master-Infrastructure PC 1)
# Martin-Direktive 2026-04-21 (Handoff Prio 4): "Master-Infrastruktur kemmer-heartbeat"
#
# Aufruf (via Scheduled-Task/cron alle 15 Min):
#   kemmer-heartbeat.sh
#
# Schreibt:
#   ~/.kemmer-grid/heartbeat.jsonl (letzte 1000 Ticks)
#   ~/.kemmer-grid/grid-health.json (aktueller Snapshot)
#
# Checkt:
#   - Kill-Switch Status
#   - Pre-Tool-Hook letzter Event (Drift?)
#   - PreCommit-Hook in Ziel-Repos
#   - LiteLLM-Router port 4000 erreichbar?
#   - Dark-Factories heute gelaufen? (df-runs.jsonl tail)
#   - Disk-Space ~/.kemmer-grid/ (<1GB warning)
#
# CRUX-Impact: verhindert Grid-Drift, stellt Master-Infra-Kontinuitaet sicher
# K_0-Protection: Kill-Switch-Watchdog-Redundanz
# Q_0-Protection: Log-Integritaet + Health-Snapshot
# I_min: strukturierter 15-Min-Takt

set -uo pipefail

CRUX_DIR="${HOME}/.kemmer-grid"
mkdir -p "$CRUX_DIR"
HEARTBEAT_LOG="$CRUX_DIR/heartbeat.jsonl"
HEALTH_JSON="$CRUX_DIR/grid-health.json"
KILL_FLAG="$CRUX_DIR/killed.flag"
TOOL_EVENTS="$CRUX_DIR/tool-events.jsonl"
DF_RUNS="$CRUX_DIR/df-runs.jsonl"

TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
HOSTNAME=$(hostname)

# --- Status-Checks ---

# 1. Kill-Switch
KILL_STATUS="inactive"
[[ -f "$KILL_FLAG" ]] && KILL_STATUS="active"

# 2. PreToolUse-Hook Live-Check (last event in 1h?)
HOOK_STATUS="unknown"
if [[ -f "$TOOL_EVENTS" ]]; then
  # Extract "ts" value via sed (works on all POSIX awk/sed, no -P required)
  LAST_EVENT_TS=$(tail -1 "$TOOL_EVENTS" 2>/dev/null | sed -n 's/.*"ts":[[:space:]]*"\([^"]*\)".*/\1/p')
  if [[ -n "$LAST_EVENT_TS" ]]; then
    LAST_EPOCH=$(date -d "$LAST_EVENT_TS" +%s 2>/dev/null || echo 0)
    NOW_EPOCH=$(date +%s)
    AGE=$((NOW_EPOCH - LAST_EPOCH))
    if [[ $AGE -lt 3600 ]]; then
      HOOK_STATUS="fresh"
    elif [[ $AGE -lt 86400 ]]; then
      HOOK_STATUS="stale-day"
    else
      HOOK_STATUS="cold"
    fi
  else
    HOOK_STATUS="empty"
  fi
else
  HOOK_STATUS="missing"
fi

# 3. PreCommit-Hook in 5 Repos
PRECOMMIT_COUNT=0
for repo in "/c/Users/marti/Projects/kemmer-grid-infra" "/c/Users/marti/Projects/learning-archon" "/c/Users/marti/Projects/archon" "/g/Meine Ablage/Claude-Knowledge-System" "/g/Meine Ablage/Claude-Vault"; do
  if [[ -x "$repo/.git/hooks/pre-commit" ]]; then
    PRECOMMIT_COUNT=$((PRECOMMIT_COUNT + 1))
  fi
done

# 4. LiteLLM-Router port-check
LITELLM_STATUS="not-checked"
if command -v curl &>/dev/null; then
  if curl -sf --max-time 2 http://127.0.0.1:4000/health >/dev/null 2>&1; then
    LITELLM_STATUS="up"
  else
    LITELLM_STATUS="down"
  fi
fi

# 5. DFs heute gelaufen?
DF_RUNS_TODAY=0
if [[ -f "$DF_RUNS" ]]; then
  TODAY=$(date -u +%Y-%m-%d)
  DF_RUNS_TODAY=$(grep -c "\"ts\":\"${TODAY}" "$DF_RUNS" 2>/dev/null || echo 0)
fi

# 6. Disk-Space ~/.kemmer-grid
KG_SIZE_KB=$(du -sk "$CRUX_DIR" 2>/dev/null | awk '{print $1}' || echo 0)
KG_WARN="ok"
[[ $KG_SIZE_KB -gt 1048576 ]] && KG_WARN="warn-1gb-plus"

# --- Heartbeat-Log ---
HEARTBEAT_ENTRY=$(cat <<EOF
{"ts":"$TS","host":"$HOSTNAME","kill_switch":"$KILL_STATUS","hook_status":"$HOOK_STATUS","precommit_repos":$PRECOMMIT_COUNT,"litellm":"$LITELLM_STATUS","df_runs_today":$DF_RUNS_TODAY,"kg_size_kb":$KG_SIZE_KB,"kg_warn":"$KG_WARN"}
EOF
)
echo "$HEARTBEAT_ENTRY" >> "$HEARTBEAT_LOG"

# Rotate log to last 1000 entries
if [[ -f "$HEARTBEAT_LOG" ]]; then
  LINE_COUNT=$(wc -l < "$HEARTBEAT_LOG")
  if [[ $LINE_COUNT -gt 1500 ]]; then
    tail -1000 "$HEARTBEAT_LOG" > "$HEARTBEAT_LOG.tmp"
    mv "$HEARTBEAT_LOG.tmp" "$HEARTBEAT_LOG"
  fi
fi

# --- Health-Snapshot (overwrite) ---
cat > "$HEALTH_JSON" <<EOF
{
  "crux_mk": true,
  "last_heartbeat": "$TS",
  "host": "$HOSTNAME",
  "kill_switch": "$KILL_STATUS",
  "pretooluse_hook": "$HOOK_STATUS",
  "precommit_repos_ok": $PRECOMMIT_COUNT,
  "precommit_repos_expected": 5,
  "litellm_router": "$LITELLM_STATUS",
  "df_runs_today": $DF_RUNS_TODAY,
  "kemmer_grid_size_kb": $KG_SIZE_KB,
  "size_warning": "$KG_WARN"
}
EOF

# --- Alerts ---
WARNINGS=0
if [[ "$KILL_STATUS" == "active" ]]; then
  echo "[CRUX-MK] ALERT: Kill-Switch aktiv!" >&2
  WARNINGS=$((WARNINGS + 1))
fi
if [[ "$HOOK_STATUS" == "cold" || "$HOOK_STATUS" == "missing" ]]; then
  echo "[CRUX-MK] WARN: PreToolUse-Hook status=$HOOK_STATUS" >&2
  WARNINGS=$((WARNINGS + 1))
fi
if [[ $PRECOMMIT_COUNT -lt 5 ]]; then
  echo "[CRUX-MK] WARN: Only $PRECOMMIT_COUNT/5 Repos haben pre-commit-Hook" >&2
  WARNINGS=$((WARNINGS + 1))
fi

exit 0
