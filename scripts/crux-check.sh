#!/usr/bin/env bash
# [CRUX-MK] Layer 0
# Kern-Script fuer CRUX-MK-Verankerung im Kemmer-Grid.
# Wird aufgerufen als: pre-bootstrap, pre-commit, pre-LLM-call, pre-tool-use.
# rho-Impact:         Infrastruktur-Erhalt, verhindert Grid-Drift
# K_0/Q_0/I_min:      Aktive Durchsetzung aller drei Nebenbedingungen
# Wargame-Status:     alignment_passed (Martin-Direktive 2026-04-21 "CRUX Layer 0")

set -euo pipefail

# -----------------------------------------------------------------------------
# Konstanten
# -----------------------------------------------------------------------------
CRUX_LOG_DIR="${HOME}/.kemmer-grid"
CRUX_LOG_FILE="${CRUX_LOG_DIR}/crux-events.jsonl"
CRUX_VERSION="v1.0"
mkdir -p "$CRUX_LOG_DIR"

# -----------------------------------------------------------------------------
# Argument-Parsing
# -----------------------------------------------------------------------------
ACTION=""
ESTIMATED_RHO=""
K0_RISK="unknown"
Q0_RISK="unknown"
I_MIN_IMPACT="unknown"
L_MARTIN_IMPACT="unknown"
WARGAME_STATUS="none"
STAGE=""
DRY_RUN=0
VERBOSE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --action)         ACTION="${2:-}"; shift 2;;
    --estimated-rho)  ESTIMATED_RHO="${2:-}"; shift 2;;
    --k0-risk)        K0_RISK="${2:-}"; shift 2;;
    --q0-risk)        Q0_RISK="${2:-}"; shift 2;;
    --i-min)          I_MIN_IMPACT="${2:-}"; shift 2;;
    --l-martin)       L_MARTIN_IMPACT="${2:-}"; shift 2;;
    --wargame)        WARGAME_STATUS="${2:-}"; shift 2;;
    --stage)          STAGE="${2:-}"; shift 2;;
    --dry-run)        DRY_RUN=1; shift;;
    --verbose|-v)     VERBOSE=1; shift;;
    --help|-h)
      cat << 'EOF'
crux-check.sh [CRUX-MK] Layer 0
Prueft ob eine Aktion CRUX-MK konform ist.

Usage:
  crux-check.sh --action "install ollama" \
    --estimated-rho "+10-30 EUR/M" \
    --k0-risk low --q0-risk none \
    --i-min positive --l-martin positive \
    --wargame adversarial_passed

Optionen:
  --action             Kurz-Beschreibung der Aktion (required)
  --estimated-rho      rho-Schaetzung in EUR/Zeit (required)
  --k0-risk            none|low|medium|high (default: unknown)
  --q0-risk            none|low|medium|high (default: unknown)
  --i-min              positive|neutral|negative (default: unknown)
  --l-martin           positive|neutral|negative (default: unknown)
  --wargame            none|adversarial_passed|alignment_passed|both_passed (default: none)
  --stage              Optional Bootstrap-Stage
  --dry-run            Kein Write, nur Report
  --verbose            Detail-Output

Exit-Codes:
  0 = PASS (proceed)
  1 = REJECT (Nebenbedingung verletzt)
  2 = WARN (rho unklar, Martin-Review)
EOF
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

# -----------------------------------------------------------------------------
# Validierung Pflicht-Felder
# -----------------------------------------------------------------------------
if [[ -z "$ACTION" ]]; then
  echo "[CRUX-MK] ERROR: --action ist Pflicht" >&2
  exit 2
fi
if [[ -z "$ESTIMATED_RHO" ]]; then
  echo "[CRUX-MK] ERROR: --estimated-rho ist Pflicht (keine Aktion ohne rho-Schaetzung)" >&2
  exit 2
fi

# -----------------------------------------------------------------------------
# Kill-Switch-Check (immer zuerst)
# -----------------------------------------------------------------------------
if [[ -f "${CRUX_LOG_DIR}/killed.flag" ]]; then
  echo "[CRUX-MK] Kill-Switch aktiv (${CRUX_LOG_DIR}/killed.flag). Alle Aktionen gestoppt."
  exit 1
fi

# -----------------------------------------------------------------------------
# Nebenbedingungs-Checks (hart)
# -----------------------------------------------------------------------------
VERDICT="PASS"
REJECT_REASONS=()

case "$K0_RISK" in
  high)
    VERDICT="REJECT"
    REJECT_REASONS+=("K_0 high risk: Kapital-Substanzverzehr moeglich")
    ;;
esac

case "$Q0_RISK" in
  high)
    VERDICT="REJECT"
    REJECT_REASONS+=("Q_0 high risk: Qualitaet/Familie-Degradation moeglich")
    ;;
esac

case "$I_MIN_IMPACT" in
  negative)
    VERDICT="REJECT"
    REJECT_REASONS+=("I_min negative: Ordnungsminimum unterschritten")
    ;;
esac

# rho-Schaetzung muss positiv oder klar begruendet sein
if echo "$ESTIMATED_RHO" | grep -qi "unclear\|unknown\|n/a" ; then
  if [[ "$VERDICT" == "PASS" ]]; then
    VERDICT="WARN"
    REJECT_REASONS+=("rho unklar - Martin-Review empfohlen")
  fi
fi

# -----------------------------------------------------------------------------
# Wargame-Check (bei substantiellen Aktionen)
# -----------------------------------------------------------------------------
if [[ "$WARGAME_STATUS" == "none" ]] && [[ "$K0_RISK" == "medium" || "$Q0_RISK" == "medium" ]]; then
  if [[ "$VERDICT" == "PASS" ]]; then
    VERDICT="WARN"
    REJECT_REASONS+=("Substantielle Aktion ohne Wargame-Haertung")
  fi
fi

# -----------------------------------------------------------------------------
# Output
# -----------------------------------------------------------------------------
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
HOST=$(hostname -s 2>/dev/null || hostname)

echo "[CRUX-MK] Layer-0-Check $CRUX_VERSION"
echo "  Action:           $ACTION"
echo "  rho-Estimate:     $ESTIMATED_RHO"
echo "  K_0-Risk:         $K0_RISK"
echo "  Q_0-Risk:         $Q0_RISK"
echo "  I_min-Impact:     $I_MIN_IMPACT"
echo "  L_Martin-Impact:  $L_MARTIN_IMPACT"
echo "  Wargame-Status:   $WARGAME_STATUS"
[[ -n "$STAGE" ]] && echo "  Stage:            $STAGE"
echo ""
echo "VERDICT: $VERDICT"

if [[ ${#REJECT_REASONS[@]} -gt 0 ]]; then
  echo "Reasons:"
  for reason in "${REJECT_REASONS[@]}"; do
    echo "  - $reason"
  done
fi

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
if [[ $DRY_RUN -eq 0 ]]; then
  python3 - "$CRUX_LOG_FILE" "$TS" "$HOST" "$ACTION" "$ESTIMATED_RHO" "$K0_RISK" "$Q0_RISK" "$I_MIN_IMPACT" "$L_MARTIN_IMPACT" "$WARGAME_STATUS" "$STAGE" "$VERDICT" "${REJECT_REASONS[*]:-}" <<'PY' || true
import json, sys
fp, ts, host, action, rho, k0, q0, i_min, l_m, wg, stage, verdict, reasons = sys.argv[1:14]
entry = {
  "ts": ts, "host": host, "version": "v1.0",
  "action": action, "rho_estimate": rho,
  "k0_risk": k0, "q0_risk": q0,
  "i_min_impact": i_min, "l_martin_impact": l_m,
  "wargame_status": wg, "stage": stage,
  "verdict": verdict, "reasons": reasons
}
with open(fp, "a", encoding="utf-8") as fh:
  fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
PY
fi

# -----------------------------------------------------------------------------
# Exit
# -----------------------------------------------------------------------------
case "$VERDICT" in
  PASS)   exit 0;;
  WARN)   exit 2;;
  REJECT) exit 1;;
  *)      exit 2;;
esac
