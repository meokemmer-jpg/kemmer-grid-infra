#!/usr/bin/env bash
# [CRUX-MK] Layer 0 — Git pre-commit hook
# Installiert via: cp scripts/crux-pre-commit.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
# Oder symlink: ln -s ../../scripts/crux-pre-commit.sh .git/hooks/pre-commit

set -uo pipefail

WARN_COUNT=0
TOTAL_FILES=0
NON_CRUX_FILES=()

# Commit-Message-Check (wenn COMMIT_MSG_FILE verfuegbar via prepare-commit-msg Kontext)
COMMIT_MSG_FILE=".git/COMMIT_EDITMSG"
if [[ -f "$COMMIT_MSG_FILE" ]]; then
  MSG=$(cat "$COMMIT_MSG_FILE")
  if ! echo "$MSG" | grep -q "\[CRUX-MK\]"; then
    echo "[CRUX-MK] WARN: Commit-Message ohne [CRUX-MK]-Marker."
    echo "  Empfehlung: '[CRUX-MK]' im Body-Ende ergaenzen."
    echo "  Plus: 'rho-impact: +/- X EUR/J' Footer-Zeile."
    WARN_COUNT=$((WARN_COUNT + 1))
  fi
fi

# File-Check
for file in $(git diff --cached --name-only --diff-filter=ACM); do
  TOTAL_FILES=$((TOTAL_FILES + 1))
  case "$file" in
    *.sh|*.py)
      if ! head -20 "$file" 2>/dev/null | grep -qi "crux-mk\|CRUX-MK"; then
        NON_CRUX_FILES+=("$file")
      fi
      ;;
    *.ps1)
      if ! Select-String -Path "$file" -Pattern "CRUX-MK" -SimpleMatch -Quiet 2>/dev/null; then
        # Fallback falls Select-String nicht verfuegbar (non-Windows)
        if ! head -20 "$file" 2>/dev/null | grep -qi "crux-mk"; then
          NON_CRUX_FILES+=("$file")
        fi
      fi
      ;;
    *.json)
      if ! grep -q '"crux_mk"' "$file" 2>/dev/null; then
        NON_CRUX_FILES+=("$file")
      fi
      ;;
    *.yaml|*.yml)
      if ! head -20 "$file" 2>/dev/null | grep -qi "crux-mk"; then
        NON_CRUX_FILES+=("$file")
      fi
      ;;
    *.md)
      # Markdown: Nur warn wenn Manifest-, Canon- oder Finding-Doc
      case "$file" in
        *manifest*|*canon*|*finding*|CRUX-MK.md|MASTERPLAN*|README*)
          if ! head -10 "$file" 2>/dev/null | grep -qi "crux-mk"; then
            NON_CRUX_FILES+=("$file")
          fi
          ;;
      esac
      ;;
  esac
done

# Report
if [[ ${#NON_CRUX_FILES[@]} -gt 0 ]]; then
  NON_CRUX_COUNT=${#NON_CRUX_FILES[@]}
  if [[ $TOTAL_FILES -gt 0 ]]; then
    PCT=$((NON_CRUX_COUNT * 100 / TOTAL_FILES))
  else
    PCT=0
  fi
  echo "[CRUX-MK] WARN: $NON_CRUX_COUNT/$TOTAL_FILES Files ohne CRUX-Marker (${PCT}%)"
  if [[ ${#NON_CRUX_FILES[@]} -le 10 ]]; then
    for f in "${NON_CRUX_FILES[@]}"; do echo "    - $f"; done
  else
    for i in 0 1 2 3 4; do echo "    - ${NON_CRUX_FILES[$i]}"; done
    echo "    ... und $((NON_CRUX_COUNT - 5)) weitere"
  fi
  WARN_COUNT=$((WARN_COUNT + NON_CRUX_COUNT))
fi

# TODO: Hier spaeter crux-check.sh invoken fuer Commit-Impact-Estimation:
# sh scripts/crux-check.sh --action "commit <hash>" --estimated-rho "<from message>" ...

if [[ $WARN_COUNT -gt 0 ]]; then
  echo "[CRUX-MK] $WARN_COUNT Warnings. Commit nicht blockiert, aber bitte adressieren."
fi

exit 0
