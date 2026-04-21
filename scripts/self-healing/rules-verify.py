#!/usr/bin/env python3
# [CRUX-MK] Self-Healing Schicht 5 + P4: Rules-Integritaet via Signed Git-Tag
# Cross-LLM-HARDENED 2/2 MODIFY (Codex + Gemini adversarial 2026-04-21).
#
# Aufruf:
#   python scripts/self-healing/rules-verify.py [--halt-on-fail] [--grace-sec 300]
#
# Prinzip (Codex-Patch P4):
#   - Authoritative = signierter immutable Git-Tag (z.B. seed-v2026-04-21-a)
#   - NICHT main-Branch, NICHT Drive-Snapshot, NICHT Quorum
#   - Race-Condition-Feste Version-ID
#   - 5-Min-Grace-Period fuer Drive-Sync-Verzoegerungen (Gemini-Ergaenzung)
#
# Ablauf:
#   1. Lese ~/.claude/rules/.version (SEED_VERSION string)
#   2. `git rev-parse refs/tags/<version>` in kemmer-grid-infra repo
#   3. Vergleiche Local-Rules-Hash gegen Tag-Content (aus git archive)
#   4. Optional: `git verify-tag` fuer Signatur-Check
#   5. Bei Fehler: 5-Min-Grace-Sleep, dann Retry
#   6. Bei Bootstrap-Mode + halt-on-fail: Exit 1
#
# CRUX-Impact:
#   K_0: CRUX-Drift-Schutz (verhindert inkonsistente Rules auf Multi-Machine-Grid)
#   I_min: strukturierter Hash-Check statt 3-Way-Quorum
#   rho_estimate_eur_per_year: "+10-30k (verhindert Rules-Drift-Kosten)"

from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

GRID_REPO = Path.home() / "Projects" / "kemmer-grid-infra"
LOCAL_RULES_DIR = Path.home() / ".claude" / "rules"
VERSION_FILE = LOCAL_RULES_DIR / ".version"
AUDIT_LOG = Path.home() / ".kemmer-grid" / "self-healing-audit.jsonl"


def _log(entry: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry["ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _git(args: List[str], cwd: Path = GRID_REPO) -> Tuple[int, str, str]:
    try:
        r = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=30,
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except FileNotFoundError:
        return 127, "", "git not found"
    except subprocess.TimeoutExpired:
        return 124, "", "git timeout"


def read_local_version() -> Optional[str]:
    if not VERSION_FILE.exists():
        return None
    v = VERSION_FILE.read_text(encoding="utf-8", errors="replace").strip()
    return v or None


def tag_exists(tag: str) -> bool:
    rc, out, _ = _git(["rev-parse", f"refs/tags/{tag}"])
    return rc == 0 and len(out) >= 7


def verify_tag_signature(tag: str) -> Tuple[bool, str]:
    """Returns (signature_valid, detail). Unsigned tags return (False, 'unsigned')."""
    rc, _, err = _git(["verify-tag", tag])
    if rc == 0:
        return True, "signed-valid"
    if "no signature found" in err.lower() or "unsigned" in err.lower():
        return False, "unsigned"
    return False, f"invalid: {err[:100]}"


def _normalize_content(raw: bytes) -> bytes:
    """CRLF/CR → LF normalize to match git-show output on Windows."""
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def hash_dir(d: Path, pattern: str = "*.md") -> str:
    """Deterministic SHA-256 of directory (sorted relative paths + LF-normalized content)."""
    h = hashlib.sha256()
    files = sorted(d.rglob(pattern))
    for f in files:
        if f.is_file():
            rel = f.relative_to(d).as_posix()
            h.update(rel.encode("utf-8"))
            h.update(b"\0")
            h.update(_normalize_content(f.read_bytes()))
            h.update(b"\0")
    return h.hexdigest()


def tag_rules_hash(tag: str) -> Optional[str]:
    """Compute hash of claude-system/rules/ content at tag using git show.

    Strategy: Enumerate files via `git ls-tree` (text-safe), then read each
    via `git show <tag>:<path>` (binary-safe). Avoids Windows-Thread-Read bug
    with `git archive | tarfile`.
    """
    # List files in tag
    rc, out, err = _git(["ls-tree", "-r", "--name-only", tag, "claude-system/rules"])
    if rc != 0:
        return None
    paths = [p for p in out.splitlines() if p.endswith(".md")]
    paths.sort()
    h = hashlib.sha256()
    for p in paths:
        # Use binary-safe git show
        try:
            r = subprocess.run(
                ["git", "show", f"{tag}:{p}"],
                cwd=str(GRID_REPO),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                check=False,
            )
            if r.returncode != 0:
                continue
            rel = p[len("claude-system/rules/"):] if p.startswith("claude-system/rules/") else p
            h.update(rel.encode("utf-8"))
            h.update(b"\0")
            h.update(_normalize_content(r.stdout))
            h.update(b"\0")
        except Exception:
            continue
    return h.hexdigest()


def verify(halt_on_fail: bool, grace_sec: int) -> int:
    version = read_local_version()
    if not version:
        _log({"event": "rules-verify", "result": "no-version-file", "path": str(VERSION_FILE)})
        msg = f"[WARN] No version file: {VERSION_FILE}"
        print(msg, file=sys.stderr)
        if halt_on_fail:
            return 2
        # No version file = cold-start or bootstrap init — not fatal for now
        return 0

    if not GRID_REPO.exists():
        _log({"event": "rules-verify", "result": "no-repo", "path": str(GRID_REPO)})
        print(f"[FAIL] Grid-Repo missing: {GRID_REPO}", file=sys.stderr)
        return 3 if halt_on_fail else 0

    if not tag_exists(version):
        _log({"event": "rules-verify", "result": "tag-missing", "version": version})
        print(f"[FAIL] Tag {version} not in repo", file=sys.stderr)
        if halt_on_fail:
            print(f"  Grace sleep {grace_sec}s, then retry...", file=sys.stderr)
            time.sleep(grace_sec)
            if not tag_exists(version):
                print(f"[FAIL] Tag {version} STILL missing after grace", file=sys.stderr)
                return 4
        else:
            return 0

    sig_ok, sig_detail = verify_tag_signature(version)

    # Hash-Compare
    local_hash = hash_dir(LOCAL_RULES_DIR, "*.md")
    tag_hash = tag_rules_hash(version)

    match = local_hash == tag_hash if tag_hash else False

    result = {
        "event": "rules-verify",
        "version": version,
        "signature": sig_detail,
        "signed_valid": sig_ok,
        "local_hash": local_hash[:16],
        "tag_hash": (tag_hash or "")[:16] if tag_hash else None,
        "match": match,
    }
    _log(result)

    if match:
        print(f"[OK] Rules match tag {version} | sig={sig_detail}")
        return 0

    print(f"[FAIL] Rules-Hash-Mismatch: local={local_hash[:16]} vs tag={tag_hash[:16] if tag_hash else 'NULL'}", file=sys.stderr)
    if halt_on_fail:
        print(f"  Grace sleep {grace_sec}s, then retry...", file=sys.stderr)
        time.sleep(grace_sec)
        local_hash2 = hash_dir(LOCAL_RULES_DIR, "*.md")
        tag_hash2 = tag_rules_hash(version)
        if local_hash2 == tag_hash2:
            print(f"[OK-after-grace] Rules match after grace-period")
            return 0
        print(f"[HALT] Rules-Divergenz persists → halt_bootstrap", file=sys.stderr)
        return 5
    return 0  # non-halt: warn-only


def main() -> int:
    p = argparse.ArgumentParser(description="Self-Healing Schicht-5 + P4 Rules-Verify")
    p.add_argument("--halt-on-fail", action="store_true", help="Exit non-zero on divergence (Bootstrap-Mode)")
    p.add_argument("--grace-sec", type=int, default=300, help="Grace period for Drive-Sync (default 300s)")
    args = p.parse_args()
    return verify(halt_on_fail=args.halt_on_fail, grace_sec=args.grace_sec)


if __name__ == "__main__":
    sys.exit(main())
