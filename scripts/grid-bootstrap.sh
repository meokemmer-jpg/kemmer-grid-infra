#!/usr/bin/env bash
# [CRUX-MK] Layer 0
# rho-Impact: +5-30k EUR/J je nach Rolle
# K_0/Q_0/I_min: geschuetzt via Admission-Gate + Capability-Suite
# Wargame-Status: alignment_passed (Masterplan v2)
# Pre-Check: crux-check.sh wird als erste Aktion invoked

# === LAYER 0: CRUX-MK-Gate ===
SCRIPT_DIR="$(dirname "$0")"
if [ -x "$SCRIPT_DIR/crux-check.sh" ]; then
  sh "$SCRIPT_DIR/crux-check.sh"     --action "grid-bootstrap start"     --estimated-rho "+5000-30000 EUR/J (role-dependent infrastructure deploy)"     --k0-risk low --q0-risk low --i-min positive --l-martin positive     --wargame alignment_passed --stage "bootstrap-entry" || {
    echo "[grid-bootstrap] CRUX-Gate verweigert Bootstrap. Abbruch."
    exit 1
  }
else
  echo "[grid-bootstrap] WARN: crux-check.sh nicht gefunden. CRUX-Layer-0 inactive." >&2
fi
# === END LAYER 0 ===
# Idempotenter Grid-Bootstrap fuer Mac/Linux.
set -euo pipefail

ROLE=""; RESUME=0; DRY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --role) ROLE="${2:-}"; shift 2;;
    --resume) RESUME=1; shift;;
    --dry-run) DRY=1; shift;;
    *) echo "usage: $0 --role {worker|primary|validator|local-inference} [--resume] [--dry-run]" >&2; exit 2;;
  esac
done
[[ "$ROLE" =~ ^(worker|primary|validator|local-inference)$ ]] || exit 2

HOST="$(hostname -s 2>/dev/null || hostname)"; TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
ROOT="${HOME}/.kemmer-grid"; mkdir -p "$ROOT"
ATTEST="${ROOT}/state-attestation.json"; REPO="${ROOT}/kemmer-grid-infra"; STATUS_FILE="${ROOT}/${HOST}.status.json"
BRANCH_HUB=""
for p in "${BRANCH_HUB:-}" "/Volumes/GoogleDrive/branch-hub" "/Volumes/GoogleDrive/Meine Ablage/Claude-Knowledge-System/branch-hub"; do
  [[ -n "${p:-}" && -f "$p/BEACON.md" ]] && BRANCH_HUB="$p" && break
done

attest(){ python3 - "$ATTEST" "$1" "$2" "$3" "$TS" <<'PY'
import json,os,sys
p,step,verdict,detail,ts=sys.argv[1:6]
data=[]
if os.path.exists(p):
  try: data=json.load(open(p,'r',encoding='utf-8'))
  except Exception: data=[]
data.append({"ts":ts,"step":step,"verdict":verdict,"detail":detail})
json.dump(data,open(p,'w',encoding='utf-8'),indent=2)
PY
}
hash_of(){ python3 - "$1" <<'PY'
import hashlib,shutil,sys; p=shutil.which(sys.argv[1]); 
print(hashlib.sha256(open(p,'rb').read()).hexdigest() if p else "")
PY
}
ver_of(){ "$1" --version 2>/dev/null | head -n1 || true; }
need_item(){ python3 - "$1" "$2" "$3" "$4" <<'PY'
import sys
cmd,have,need,sha=sys.argv[1:5]
ok=bool(have)
if need and need not in have: ok=False
if sha and sha!=cmd: ok=False
print("0" if ok else "1")
PY
}
update_status(){
  local score="$1"
  python3 - "$STATUS_FILE" "$HOST" "$ROLE" "$TS" "$score" <<'PY'
import json,sys
out,host,role,ts,score=sys.argv[1:6]
json.dump({"host":host,"role":role,"ts":ts,"grid_doctor_score":float(score)},open(out,'w',encoding='utf-8'),indent=2)
PY
  if [[ -n "$BRANCH_HUB" ]]; then mkdir -p "$BRANCH_HUB/status"; cp "$STATUS_FILE" "$BRANCH_HUB/status/${HOST}.json"; fi
  if [[ -d "$REPO/.git" ]]; then
    mkdir -p "$REPO/status"; cp "$STATUS_FILE" "$REPO/status/${HOST}.json"
    git -C "$REPO" add "status/${HOST}.json" >/dev/null 2>&1 || true
    git -C "$REPO" commit -m "status(${HOST}): ${ROLE} @ ${TS}" >/dev/null 2>&1 || true
    git -C "$REPO" push >/dev/null 2>&1 || true
  fi
}

mkdir -p "$REPO"
if [[ ! -d "$REPO/.git" ]]; then
  [[ $DRY -eq 1 ]] && echo "DRY git clone kemmer-grid-infra" || git clone "https://github.com/meokemmer-jpg/kemmer-grid-infra.git" "$REPO"
else
  [[ $DRY -eq 1 ]] && echo "DRY git pull" || git -C "$REPO" pull --ff-only
fi

MANIFEST=""
[[ -n "$BRANCH_HUB" && -f "$BRANCH_HUB/handoffs/manifest-${ROLE}.json" ]] && MANIFEST="$BRANCH_HUB/handoffs/manifest-${ROLE}.json"
[[ -z "$MANIFEST" && -f "$REPO/manifests/manifest-${ROLE}.json" ]] && MANIFEST="$REPO/manifests/manifest-${ROLE}.json"
[[ -f "$MANIFEST" ]] || { attest manifest FAIL "manifest-${ROLE}.json fehlt"; exit 1; }

OS="$(uname -s)"
PKG=""
if [[ "$OS" == "Darwin" ]]; then PKG="brew"
elif command -v apt-get >/dev/null 2>&1; then PKG="apt"
elif command -v snap >/dev/null 2>&1; then PKG="snap"
else attest package FAIL "Kein Paketmanager"; exit 1; fi
if [[ $DRY -eq 0 && "$PKG" != "brew" ]]; then sudo -v; fi
attest bootstrap OK "role=${ROLE};resume=${RESUME};dry=${DRY};pkg=${PKG}"

mapfile -t ITEMS < <(python3 - "$MANIFEST" <<'PY'
import json,sys
d=json.load(open(sys.argv[1],'r',encoding='utf-8'))
items=d.get("tools",d.get("modules",d if isinstance(d,list) else []))
for x in items:
  print("\t".join(str(x.get(k,"")) for k in ("name","command","version","sha256","brew","apt","snap")))
PY
)

total=0; ok=0
install_item(){
  local pkg="$1"
  [[ $DRY -eq 1 ]] && { echo "DRY install $pkg via $PKG"; return 0; }
  case "$PKG" in
    brew) brew list "$pkg" >/dev/null 2>&1 && brew upgrade "$pkg" || brew install "$pkg" ;;
    apt) sudo apt-get update -y >/dev/null && sudo apt-get install -y "$pkg" ;;
    snap) sudo snap install "$pkg" --classic ;;
  esac
}

for line in "${ITEMS[@]}"; do
  IFS=$'\t' read -r name cmd want_ver want_sha brew_pkg apt_pkg snap_pkg <<<"$line"
  ((total+=1))
  have_ver="$(command -v "$cmd" >/dev/null 2>&1 && ver_of "$cmd" || true)"
  have_sha="$(hash_of "$cmd")"
  need="$(need_item "$have_sha" "$have_ver" "$want_ver" "$want_sha")"
  if [[ "$need" == "0" ]]; then
    ((ok+=1)); attest "$name" OK "bereits vorhanden"
  else
    pkg_ref="$brew_pkg"; [[ "$PKG" == "apt" ]] && pkg_ref="$apt_pkg"; [[ "$PKG" == "snap" ]] && pkg_ref="$snap_pkg"
    [[ -n "$pkg_ref" ]] || { attest "$name" FAIL "kein Paket fuer $PKG"; update_status "$(awk "BEGIN{print ($ok/$total)*100}")"; exit 1; }
    attest "$name" APPLY "installiere $pkg_ref"
    install_item "$pkg_ref"
    have_ver="$(command -v "$cmd" >/dev/null 2>&1 && ver_of "$cmd" || true)"
    have_sha="$(hash_of "$cmd")"
    if [[ "$(need_item "$have_sha" "$have_ver" "$want_ver" "$want_sha")" == "0" ]]; then
      ((ok+=1)); attest "$name" OK "assert-after-write erfolgreich"
    else
      attest "$name" FAIL "assert-after-write fehlgeschlagen"; update_status "$(awk "BEGIN{print ($ok/$total)*100}")"; exit 1
    fi
  fi
  score="$(awk "BEGIN{printf \"%.2f\", ($ok/$total)*100}")"; update_status "$score"
done

golden=""
for p in "$REPO/scripts/golden-task-suite.sh" "$BRANCH_HUB/scripts/golden-task-suite.sh" "./golden-task-suite.sh"; do
  [[ -n "${p:-}" && -x "$p" ]] && golden="$p" && break
done
if [[ -n "$golden" ]]; then
  [[ $DRY -eq 1 ]] && attest capability SKIP "dry-run: $golden" || { "$golden"; attest capability OK "$golden"; }
else
  attest capability FAIL "golden-task-suite.sh fehlt"; exit 1
fi

score="$(awk "BEGIN{printf \"%.2f\", ($ok/$total)*100}")"; update_status "$score"; attest grid-doctor OK "$score"