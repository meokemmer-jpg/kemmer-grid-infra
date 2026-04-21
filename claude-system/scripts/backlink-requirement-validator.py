#!/usr/bin/env python3
"""
Backlink-Requirement-Validator [CRUX-MK]

Pre-Write-Validator: prueft dass neue Vault-Notes mindestens 1 Wikilink `[[...]]`
oder Backlink zum Canonical-MOC enthalten. Teil der Orphan-Crisis-Mitigation
(Option E.C aus DC-Vault-Orphan-Crisis-2026-04-19).

Erwartet: JSON-stdin mit { 'tool_name': 'Write'|'Edit'|..., 'file_path': ..., 'content': ... }
Ausgabe: JSON-stdout mit { 'status': 'PASS'|'WARN'|'BLOCK', 'reason': ... }

Verhalten:
- WARN-Mode (default): schreibt Warnung in audit-log, erlaubt Write
- ENFORCE-Mode (ENV CLAUDE_HOOK_MODE=ENFORCE): BLOCKed Writes ohne Backlink

Exceptions (kein Backlink-Requirement):
- MOC-Dateien (pattern `MOC-*.md`)
- Dashboard.md, MEMORY.md, CLAUDE.md (Root-Navigationsdateien)
- Daily-Notes (YYYY-MM-DD.md in daily-notes/)
- Frontmatter `type: moc | dashboard | daily-note | template`
- _merge-queue/, _archive/, attachments/

NICHT geprueft: Dateien ausserhalb Vault (branch-hub, SAE-v8 etc.)
"""
from __future__ import annotations
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


# [CRUX-MK] Runtime-Gate (Layer 0)
try:
    import sys as _crux_sys, pathlib as _crux_path
    _crux_sys.path.insert(0, str(_crux_path.Path.home() / ".claude" / "scripts"))
    import crux_runtime as _crux_rt  # auto-checks kill-switch on import
except (ImportError, SystemExit):
    import sys as _crux_sys
    _crux_kf = _crux_path.Path.home() / ".kemmer-grid" / "killed.flag" if '_crux_path' in dir() else None
    if _crux_kf and _crux_kf.exists(): _crux_sys.exit(1)
# /[CRUX-MK] Runtime-Gate

VAULT_ROOT = Path(r'G:\Meine Ablage\Claude-Vault')
EXEMPT_STEMS = {'Dashboard', 'MEMORY', 'CLAUDE', 'README'}
EXEMPT_TYPES = {'moc', 'dashboard', 'daily-note', 'template', 'index'}
EXEMPT_DIRS = {'_merge-queue', '_archive', 'attachments', '.obsidian', '.claude', '.git', '.smart-env'}
DAILY_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}\.md$')
WIKILINK_PATTERN = re.compile(r'\[\[([^\[\]|#]+?)(?:#[^\[\]|]+)?(?:\|[^\[\]]+?)?\]\]')
FRONTMATTER_TYPE = re.compile(r'^\s*type:\s*["\']?([a-z-]+)', re.MULTILINE | re.IGNORECASE)
AUDIT_LOG = Path(os.environ.get('BACKLINK_AUDIT_LOG',
                                r'G:\Meine Ablage\Claude-Knowledge-System\branch-hub\audit\backlink-validator.jsonl'))


def log(action: dict) -> None:
    action['ts'] = datetime.now(timezone.utc).isoformat()
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_LOG.open('a', encoding='utf-8') as f:
            f.write(json.dumps(action) + '\n')
    except Exception:
        pass  # never block on log-failure


def is_vault_md(file_path: str) -> bool:
    """Check if path is a .md file inside Claude-Vault."""
    try:
        p = Path(file_path).resolve()
    except Exception:
        return False
    if p.suffix.lower() != '.md':
        return False
    try:
        p.relative_to(VAULT_ROOT.resolve())
        return True
    except ValueError:
        return False


def is_exempt(file_path: str, content: str) -> tuple[bool, str]:
    """Check if file is exempt from backlink requirement."""
    p = Path(file_path)

    # Exempt stems (case-sensitive)
    if p.stem in EXEMPT_STEMS:
        return True, f'exempt-stem:{p.stem}'

    # MOC files
    if p.stem.startswith('MOC-'):
        return True, 'exempt-moc'

    # Daily notes
    if DAILY_PATTERN.match(p.name):
        return True, 'exempt-daily-note'

    # Exempt directories
    parts = set(p.parts)
    for ex in EXEMPT_DIRS:
        if ex in parts:
            return True, f'exempt-dir:{ex}'

    # Frontmatter type
    m = FRONTMATTER_TYPE.search(content[:1000])  # only first 1000 chars
    if m:
        t = m.group(1).lower()
        if t in EXEMPT_TYPES:
            return True, f'exempt-type:{t}'

    return False, ''


def count_wikilinks(content: str) -> int:
    return len(WIKILINK_PATTERN.findall(content))


def validate(tool_name: str, file_path: str, content: str) -> dict:
    # Gate 1: only Write/Edit/MultiEdit
    if tool_name not in ('Write', 'Edit', 'MultiEdit'):
        return {'status': 'PASS', 'reason': 'tool-not-gated'}

    # Gate 2: only Vault .md files
    if not is_vault_md(file_path):
        return {'status': 'PASS', 'reason': 'not-vault-md'}

    # Gate 3: exemptions
    exempt, exempt_reason = is_exempt(file_path, content)
    if exempt:
        return {'status': 'PASS', 'reason': exempt_reason}

    # Gate 4: wikilink count
    n_links = count_wikilinks(content)
    if n_links >= 1:
        return {'status': 'PASS', 'reason': f'has-{n_links}-wikilinks'}

    # No wikilinks found → WARN or BLOCK
    mode = os.environ.get('CLAUDE_HOOK_MODE', 'CHECK').upper()
    if mode == 'ENFORCE':
        return {'status': 'BLOCK', 'reason': 'no-wikilinks-enforce'}
    return {'status': 'WARN', 'reason': 'no-wikilinks-warn'}


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except Exception as e:
        print(json.dumps({'status': 'PASS', 'reason': f'parse-err:{e}'}))
        return 0

    tool_name = payload.get('tool_name', '')
    tool_input = payload.get('tool_input', {})
    file_path = tool_input.get('file_path', '')
    content = tool_input.get('content', '') or tool_input.get('new_string', '')

    result = validate(tool_name, file_path, content)
    result['file'] = file_path
    result['tool'] = tool_name

    log(result)

    # Output
    print(json.dumps(result))

    # Exit-code
    if result['status'] == 'BLOCK':
        return 2  # BLOCK per Hook-Orchestrator-Konvention
    return 0


if __name__ == '__main__':
    sys.exit(main())
