#!/usr/bin/env bash
# [CRUX-MK] Layer 0 — Script traegt CRUX-Marker (siehe CRUX-MK.md)
# Deterministischer Kill-Switch fuer Mac/Linux.
set -euo pipefail

ROOT="${HOME}/.kemmer-grid"; FLAG="${ROOT}/killed.flag"; LOG="${ROOT}/kill-log.jsonl"
mkdir -p "$ROOT"
[[ -f "$FLAG" ]] && exit 0

arg="${1:-}"; reason=""
cost_log=""
for f in "$ROOT/api-usage.jsonl" "$ROOT/api-log.jsonl" "$ROOT/cost-log.jsonl"; do [[ -f "$f" ]] && cost_log="$f" && break; done
cost_rate="$(
python3 - "$cost_log" <<'PY'
import json,sys
p=sys.argv[1]; best=0.0
if p:
  with open(p,'r',encoding='utf-8',errors='ignore') as fh:
    for line in fh:
      try:
        o=json.loads(line); v=o.get("eur_per_hour",o.get("cost_eur_per_hour",o.get("hourly_eur",0)))
        best=max(best,float(v or 0))
      except Exception: pass
print(best)
PY
)"

[[ "$arg" == "panic" ]] && reason="panic"
[[ -z "$reason" && "$arg" == "cost" ]] && reason="cost"
[[ -z "$reason" && "$arg" == "manual" ]] && reason="manual"
[[ -z "$reason" && "${CLAUDE_KILL:-0}" == "1" ]] && reason="env"
awk "BEGIN{exit !($cost_rate > 50)}" && [[ -z "$reason" ]] && reason="cost>50"

[[ -z "$reason" ]] && exit 0
ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
printf '%s\t%s\n' "$ts" "$reason" > "$FLAG"

while IFS='=' read -r k _; do unset "$k" || true; done < <(env | awk -F= '/(_API_KEY|TOKEN)=/{print $1}')
for k in GEMINI_API_KEY XAI_API_KEY ANTHROPIC_API_KEY OPENAI_API_KEY GH_TOKEN GITHUB_TOKEN; do unset "$k" || true; done

if command -v launchctl >/dev/null 2>&1; then
  launchctl list 2>/dev/null | awk 'NR>1{print $3}' | grep -E '^kemmer-' | while read -r label; do
    launchctl disable "gui/${UID}/${label}" >/dev/null 2>&1 || true
    launchctl disable "system/${label}" >/dev/null 2>&1 || true
    launchctl bootout "gui/${UID}/${label}" >/dev/null 2>&1 || true
    launchctl bootout "system/${label}" >/dev/null 2>&1 || true
  done
fi
if command -v systemctl >/dev/null 2>&1; then
  systemctl list-unit-files 'kemmer-*' --no-legend 2>/dev/null | awk '{print $1}' | while read -r unit; do
    [[ -n "$unit" ]] && systemctl --user disable --now "$unit" >/dev/null 2>&1 || true
  done
fi

python3 - "$LOG" "$ts" "$reason" "$cost_rate" <<'PY'
import json,sys
with open(sys.argv[1],"a",encoding="utf-8") as fh:
  fh.write(json.dumps({
    "ts":sys.argv[2],"reason":sys.argv[3],"cost_eur_per_hour":float(sys.argv[4] or 0),"host":"local"
  },ensure_ascii=True)+"\n")
PY