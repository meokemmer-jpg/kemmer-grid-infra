#!/usr/bin/env python3
# [CRUX-MK] Self-Healing Schicht 3: Handoff-Consistency-Check + P5a Schema-Validator
# Cross-LLM-HARDENED 2/2 MODIFY (Codex + Gemini adversarial 2026-04-21).
#
# Aufruf:
#   python scripts/self-healing/consistency-check.py --file <path>
#   python scripts/self-healing/consistency-check.py --dir <dir> [--strict]
#
# Pruefungen:
#   1. Frontmatter-Schema (P5a): Pflicht-Felder type/from/to/date/crux-mk
#   2. Min-Size-Check (P5a): > 200 bytes (Zombie-Empty-Fix)
#   3. Reference-Check (Schicht 3): alle Markdown-Links + wikilinks erreichbar
#
# Exit-Codes:
#   0 = alle Checks passed
#   1 = Frontmatter-Schema fail
#   2 = Min-Size fail
#   3 = Broken reference(s)
#   4 = File not found / unreadable
#
# Integration:
#   - pre-handoff-write Hook (Schicht 3)
#   - CI/CD Lint-Step auf branch-hub/inbox/*.md + handoffs/*.md + proposals/*.md
#
# CRUX-Impact:
#   Q_0: Consistency-Check verhindert broken references → Folgen-Bugs bei neuen Sessions.
#   I_min: Strukturelle Validierung aller Handoffs.
#   rho_estimate_eur_per_year: "+25-70k (verhindert Wissensverlust durch broken Refs)"

from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
import hashlib
from datetime import datetime, timezone

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # handled at runtime

# ---- Config ----
MIN_BYTES = 200  # P5a Zombie-Empty-Fix
MARKDOWN_LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
WIKILINK_RE = re.compile(r'\[\[([^\]]+)\]\]')
FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
AUDIT_LOG = Path.home() / ".kemmer-grid" / "self-healing-audit.jsonl"

# Paths that we skip in reference-check (external URLs, known-no-file targets)
SKIP_REF_PREFIXES = (
    "http://", "https://", "mailto:",
    "#",  # anchors
)


def _log(entry: Dict[str, Any]) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry["ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _extract_frontmatter(content: str) -> Dict[str, Any]:
    m = FRONTMATTER_RE.match(content)
    if not m:
        return {}
    fm_text = m.group(1)
    if yaml:
        try:
            return yaml.safe_load(fm_text) or {}
        except Exception:
            return {}
    # Minimal fallback parser (key: value only)
    out: Dict[str, Any] = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            v = v.strip()
            if v.lower() == "true":
                out[k.strip()] = True
            elif v.lower() == "false":
                out[k.strip()] = False
            else:
                out[k.strip()] = v.strip('"\'')
    return out


def check_schema(fm: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Check min frontmatter fields."""
    required = ["type", "from", "to", "date", "crux-mk"]
    errors = []
    for field in required:
        if field not in fm:
            errors.append(f"Missing field: {field}")
    if fm.get("crux-mk") is not True:
        errors.append("crux-mk must be true (not string 'true')")
    return len(errors) == 0, errors


def check_size(path: Path) -> Tuple[bool, int]:
    size = path.stat().st_size
    return size >= MIN_BYTES, size


def extract_references(content: str) -> List[str]:
    """Extract all markdown links + wikilinks that are likely file references."""
    refs: List[str] = []
    for _, url in MARKDOWN_LINK_RE.findall(content):
        u = url.strip()
        if u.startswith(SKIP_REF_PREFIXES):
            continue
        # Strip anchors
        if "#" in u:
            u = u.split("#", 1)[0]
        if u:
            refs.append(u)
    for wiki in WIKILINK_RE.findall(content):
        # [[target|alias]] → target
        tgt = wiki.split("|", 1)[0].strip()
        if tgt:
            refs.append(tgt)
    return refs


def resolve_ref(ref: str, base_dir: Path) -> List[Path]:
    """Resolve a reference to candidate paths. Returns list of path candidates."""
    candidates: List[Path] = []
    # Absolute path
    if ref.startswith(("/", "C:", "G:", "~")):
        candidates.append(Path(ref).expanduser())
        return candidates
    # Relative to file
    candidates.append(base_dir / ref)
    # Some common roots
    candidates.append(Path.home() / ".claude" / ref)
    # Vault + branch-hub if mentioned without prefix
    gdrive = Path("G:/Meine Ablage")
    if (gdrive).exists():
        candidates.append(gdrive / "Claude-Knowledge-System" / ref)
        candidates.append(gdrive / "Claude-Vault" / ref)
    return candidates


def check_references(content: str, base_dir: Path) -> Tuple[bool, List[str]]:
    refs = extract_references(content)
    broken: List[str] = []
    for ref in refs:
        # Skip refs that look like fragments only
        if not ref or ref.startswith("#"):
            continue
        # Skip .git, node_modules, etc.
        if any(seg in ref for seg in ("node_modules", ".git/")):
            continue
        candidates = resolve_ref(ref, base_dir)
        if not any(c.exists() for c in candidates):
            # One more heuristic: glob-matching if pattern
            found = False
            for c in candidates:
                if "*" in str(c):
                    if list(c.parent.glob(c.name)):
                        found = True
                        break
            if not found:
                broken.append(ref)
    return len(broken) == 0, broken


def check_file(path: Path, strict: bool = False) -> int:
    if not path.exists() or not path.is_file():
        _log({"event": "file-not-found", "target": str(path)})
        print(f"[FAIL] File not found: {path}", file=sys.stderr)
        return 4

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        _log({"event": "read-error", "target": str(path), "err": str(e)})
        print(f"[FAIL] Read error: {e}", file=sys.stderr)
        return 4

    # Schema
    fm = _extract_frontmatter(content)
    ok_schema, schema_errs = check_schema(fm)

    # Size (P5a)
    ok_size, size = check_size(path)

    # References (Schicht 3)
    ok_refs, broken = check_references(content, path.parent)

    result = {
        "event": "consistency-check",
        "target": str(path),
        "size_bytes": size,
        "schema_ok": ok_schema,
        "schema_errors": schema_errs,
        "size_ok": ok_size,
        "min_bytes": MIN_BYTES,
        "refs_ok": ok_refs,
        "broken_refs": broken[:10],  # cap
    }
    _log(result)

    # Console output
    status_line = f"[{'OK' if (ok_schema and ok_size and ok_refs) else 'FAIL'}] {path.name}"
    print(status_line)
    if not ok_schema:
        print(f"  Schema: {', '.join(schema_errs)}", file=sys.stderr)
    if not ok_size:
        print(f"  Size: {size} bytes (min {MIN_BYTES})", file=sys.stderr)
    if not ok_refs:
        print(f"  Broken refs ({len(broken)}):", file=sys.stderr)
        for b in broken[:10]:
            print(f"    - {b}", file=sys.stderr)

    # Exit code priority: size → schema → refs
    if not ok_size:
        return 2
    if strict and not ok_schema:
        return 1
    if strict and not ok_refs:
        return 3
    if not ok_schema or not ok_refs:
        return 1 if not ok_schema else 3
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Self-Healing Schicht-3 Consistency-Check + P5a")
    p.add_argument("--file", type=Path, help="Single file to check")
    p.add_argument("--dir", type=Path, help="Directory to scan recursively for *.md")
    p.add_argument("--strict", action="store_true", help="Exit non-zero on any issue (schema + refs)")
    p.add_argument("--pattern", default="*.md", help="Glob pattern for --dir mode")
    args = p.parse_args()

    if args.file:
        return check_file(args.file, strict=args.strict)

    if args.dir:
        files = sorted(args.dir.rglob(args.pattern))
        worst = 0
        for f in files:
            rc = check_file(f, strict=args.strict)
            worst = max(worst, rc)
        print(f"\nChecked {len(files)} files. Worst exit code: {worst}")
        return worst

    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
