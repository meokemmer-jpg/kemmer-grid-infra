#!/usr/bin/env bash
# Standalone-Diagnose fuer Mac/Linux.
set -euo pipefail

HOST="$(hostname -s 2>/dev/null || hostname)"; TS="$(date -u +%Y%m%dT%H%M%SZ)"
ROLE="${MACHINE_ROLE:-worker}"; CLAUDE_DIR="${HOME}/.claude"; ROOT="${HOME}/.kemmer-grid"; KS="${PWD}/kill-switch.sh"
rows=(); overall=0

add_row() { rows+=("$1"$'\t'"$2"$'\t'"$3"); [[ "$2" != "OK" ]] && overall=1; }
hub=""
for p in "${BRANCH_HUB:-}" "/Volumes/GoogleDrive/branch-hub" "/Volumes/GoogleDrive/Meine Ablage/Claude-Knowledge-System/branch-hub"; do
  [[ -n "${p:-}" && -f "$p/BEACON.md" ]] && hub="$p" && break
done
if [[ -z "$hub" ]]; then
  found="$(find /Volumes/GoogleDrive -maxdepth 6 -path '*/branch-hub/BEACON.md' -print -quit 2>/dev/null || true)"
  [[ -n "$found" ]] && hub="$(dirname "$found")"
fi
[[ -n "$hub" ]] && add_row "Drive/Branch-Hub" "OK" "$hub" || add_row "Drive/Branch-Hub" "MISSING" "BEACON.md nicht gefunden"

check_cli() {
  local name="$1" need="$2" cmd="$3" state="MISSING" detail="nicht gefunden" ver=""
  if command -v "$cmd" >/dev/null 2>&1; then
    ver="$("$cmd" --version 2>/dev/null | head -n1 || true)"
    state="OK"; detail="${ver:-gefunden}"
    [[ "$name" == "python3" ]] && python3 - <<'PY' >/dev/null || state="PARTIAL"
import sys; raise SystemExit(0 if sys.version_info >= (3,12) else 1)
PY
    if [[ "$name" == "node" ]]; then
      major="$(node -p "process.versions.node.split('.')[0]" 2>/dev/null || echo 0)"
      [[ "$major" =~ ^[0-9]+$ && $major -ge 20 && $((major%2)) -eq 0 ]] || state="PARTIAL"
    fi
  fi
  add_row "CLI:$name" "$state" "$detail"
}
check_cli git required git; check_cli gh required gh; check_cli python3 "3.12+" python3; check_cli node LTS node
check_cli codex required codex; check_cli gemini required gemini; check_cli uv required uv; check_cli ollama required ollama

for v in GEMINI_API_KEY XAI_API_KEY ANTHROPIC_API_KEY MACHINE_ROLE; do
  [[ -n "${!v:-}" ]] && add_row "ENV:$v" "OK" "gesetzt" || add_row "ENV:$v" "MISSING" "nicht gesetzt"
done

if gh auth status >/dev/null 2>&1; then add_row "gh auth" "OK" "auth aktiv"; else add_row "gh auth" "PARTIAL" "gh nicht eingeloggt"; fi

sched="$( { command -v launchctl >/dev/null 2>&1 && launchctl list 2>/dev/null | awk 'NR>1{print $3}'; crontab -l 2>/dev/null; } | grep -E 'DF-|NLM-|Claude-' || true)"
if [[ "$ROLE" == "primary" ]]; then
  ok=0; for p in 'DF-' 'NLM-' 'Claude-'; do grep -q "$p" <<<"$sched" && ((ok+=1)) || true; done
  [[ $ok -eq 3 ]] && add_row "Scheduler[$ROLE]" "OK" "alle Master-Jobs da" || add_row "Scheduler[$ROLE]" "MISSING" "Master-Jobs unvollstaendig"
else
  [[ -z "$sched" ]] && add_row "Scheduler[$ROLE]" "OK" "keine Master-Jobs" || add_row "Scheduler[$ROLE]" "PARTIAL" "unerwartete Jobs gefunden"
fi

rules_count="$(find "$CLAUDE_DIR/rules" -maxdepth 1 -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
if [[ "$rules_count" -ge 40 ]]; then add_row "Rules" "OK" "$rules_count Dateien"
elif [[ "$rules_count" -gt 0 ]]; then add_row "Rules" "PARTIAL" "$rules_count Dateien"
else add_row "Rules" "MISSING" "0 Dateien"; fi

[[ -x "$KS" ]] && add_row "kill-switch.sh" "OK" "$KS" || add_row "kill-switch.sh" "MISSING" "nicht executable"

echo "| Check | Status | Detail |"
echo "|---|---|---|"
for r in "${rows[@]}"; do IFS=$'\t' read -r a b c <<<"$r"; echo "| $a | $b | $c |"; done

if [[ -n "$hub" ]]; then
  mkdir -p "$hub/status"
  printf '%s\n' "${rows[@]}" | python3 - "$hub/status/${HOST}-diagnose-${TS}.json" "$HOST" "$ROLE" "$TS" "$overall" <<'PY'
import json,sys
out,host,role,ts,overall=sys.argv[1:6]
rows=[]
for line in sys.stdin:
  name,status,detail=line.rstrip("\n").split("\t",2)
  rows.append({"check":name,"status":status,"detail":detail})
with open(out,"w",encoding="utf-8") as fh:
  json.dump({"host":host,"role":role,"ts":ts,"ok":overall=="0","checks":rows},fh,indent=2)
PY
fi

exit "$overall"