#!/bin/bash
# github-bauplan-publish.sh [CRUX-MK]
# Version: 1.0.0
# Usage: publish.sh <source-file> [<source-file-2> ...]
# Publiziert Bauplaene/Findings/Cross-LLM-Files nach meokemmer-jpg/kemmer-knowledge-system

set -euo pipefail

# ====== CONFIG ======
REPO_LOCAL="${REPO_LOCAL:-/tmp/kks-repo}"
REPO_REMOTE="${GITHUB_REPO:-meokemmer-jpg/kemmer-knowledge-system}"
AUDIT_LOG="G:/Meine Ablage/Claude-Knowledge-System/branch-hub/audit/github-publish.jsonl"
BRANCH="${BRANCH_NAME:-main}"

# ====== HELPERS ======
log_audit() {
    local action="$1" target="$2" status="$3" hash="${4:-}"
    local ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "{\"ts\":\"$ts\",\"branch\":\"$BRANCH\",\"action\":\"$action\",\"target\":\"$target\",\"status\":\"$status\",\"commit\":\"$hash\"}" >> "$AUDIT_LOG"
}

fail() {
    echo "ERROR: $1" >&2
    log_audit "FAIL" "${2:-unknown}" "error"
    exit 1
}

# ====== PHASE 1: CLASSIFY ======
classify() {
    local src="$1"
    case "$src" in
        *Claude-Vault/canon/blueprints/B*.md) echo "blueprints/" ;;
        *branch-hub/findings/*.md)            echo "findings/" ;;
        *branch-hub/cross-llm/*.md)           echo "cross-llm/" ;;
        *.py|*.ts|*.js|*.sh)                  echo "code/" ;;
        *.claude/skills/*)                    echo "skills/" ;;
        *.claude/rules/*)                     echo "rules/" ;;
        *)                                    fail "Unknown file type: $src" "$src" ;;
    esac
}

# ====== PHASE 2: PRE-FLIGHT ======
preflight() {
    local src="$1"
    # gh auth
    gh auth status >/dev/null 2>&1 || fail "gh auth failed -- run: gh auth login" "$src"
    # repo clone
    if [ ! -d "$REPO_LOCAL/.git" ]; then
        git clone "https://github.com/$REPO_REMOTE.git" "$REPO_LOCAL" || fail "Clone failed" "$src"
    fi
    (cd "$REPO_LOCAL" && git pull --rebase origin "$BRANCH" >/dev/null) || fail "Pull failed" "$src"
    # file-size cap
    local size=$(stat -c%s "$src" 2>/dev/null || wc -c < "$src")
    [ "$size" -gt 524288 ] && echo "WARN: File >500KB ($size bytes)" >&2
    # secrets scan
    if grep -qE 'API_KEY|SECRET|TOKEN=|PASSWORD|PRIVATE_KEY|BEGIN RSA' "$src"; then
        fail "Secrets detected in $src -- ABORT" "$src"
    fi
}

# ====== PHASE 3: STAGE ======
stage() {
    local src="$1" target_dir="$2"
    mkdir -p "$REPO_LOCAL/$target_dir"
    cp "$src" "$REPO_LOCAL/$target_dir/" || fail "Copy failed" "$src"
    (cd "$REPO_LOCAL" && git add "$target_dir") || fail "git add failed" "$src"
}

# ====== PHASE 4: COMMIT+PUSH ======
commit_push() {
    local src="$1" target_dir="$2"
    local title=$(basename "$src" .md)
    local type="publish"
    case "$target_dir" in
        blueprints/) type="blueprint" ;;
        findings/)   type="finding" ;;
        cross-llm/)  type="cross-llm" ;;
        code/)       type="code" ;;
    esac
    local date=$(date +%Y-%m-%d)
    local msg="[$BRANCH] $type: $title ($date)"

    cd "$REPO_LOCAL"
    # Guard against force push
    [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ] && {
        git config push.default current
    }
    git commit -m "$msg" -m "Auto-published via github-bauplan-publish v1.0.0" \
               -m "Source: $src" \
               -m "[CRUX-MK]" \
        || fail "Commit failed" "$src"
    git push origin "$BRANCH" || fail "Push failed -- check remote state" "$src"
    git rev-parse HEAD
}

# ====== PHASE 5: REPORT ======
report() {
    local src="$1" hash="$2" target_dir="$3"
    local url="https://github.com/$REPO_REMOTE/commit/$hash"
    echo "PUBLISHED: $src"
    echo "  target : $target_dir"
    echo "  commit : $hash"
    echo "  url    : $url"
    log_audit "PUBLISH" "$src" "success" "$hash"
}

# ====== MAIN ======
[ "$#" -eq 0 ] && fail "No source files given. Usage: publish.sh <file> [...]" "stdin"

for src in "$@"; do
    [ -f "$src" ] || fail "File not found: $src" "$src"
    echo "=== Publishing: $src ==="
    target_dir=$(classify "$src")
    preflight "$src"
    stage "$src" "$target_dir"
    hash=$(commit_push "$src" "$target_dir")
    report "$src" "$hash" "$target_dir"
done

echo "Done. All files published to $REPO_REMOTE."
# [CRUX-MK]
