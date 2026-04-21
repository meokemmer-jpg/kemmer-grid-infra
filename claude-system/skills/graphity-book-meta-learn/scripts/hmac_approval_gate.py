#!/usr/bin/env python3
"""
hmac_approval_gate.py -- P0-1 HMAC/Ed25519 Approval-Gate [CRUX-MK]
Status: STUB (not runnable, typsicher)
Design-Doc: branch-hub/findings/DESIGN-P0-1-HMAC-APPROVAL-GATE-2026-04-19.md
Verdict: CROSS-LLM-2OF3-HARDENED-MODIFY (Grok ADOPT, Codex REJECT mit 5 Fixes integriert)

Loest P0-1 Approval-Gate TOCTOU-Bypass:
- Gewaltenteilung: Ed25519 asymmetrisch, private key nur Martin
- Scope: Promotion-Manifest (write_set + schema + code_sha) statt nur bundle_hash
- Replay-Schutz: token_id + realm_id in Signatur-Payload
- Single-use: consumed_at + Kryptografische Bindung via token_id
- Direct-SQL-Bypass: OS-Account-Trennung (siehe Design-Doc §4.4)

Pflicht-Abhaengigkeiten (nicht in Stub implementiert):
- cryptography (Ed25519)
- sqlite3 (WAL-Mode Pflicht!)
- json (kanonisiert: sort_keys=True, separators=(',', ':'))
- hmac.compare_digest (constant-time)

WICHTIG: Dieser Stub definiert API + Signaturen. Keine echte Validation-Logik.
Vor Ausfuehrung: Kapitel 2-8 im Design-Doc implementieren.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sqlite3
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any



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

# ==========================================================================
# CONFIG
# ==========================================================================

REALM_ID = "DF-07-graphity-prod"  # Cross-Env-Replay-Schutz
DEFAULT_TOKEN_TTL_HOURS = 24
DEFAULT_KEY_GRACE_DAYS = 30

DARK_FACTORY_ROOT = Path("G:/Meine Ablage/Claude-Knowledge-System/dark-factory/DF-07-graphity-book-writer")
VAULT_INBOX = DARK_FACTORY_ROOT / "approval-inbox"
TOKEN_IMPORT_DIR = DARK_FACTORY_ROOT / "approval-imported"
AUDIT_LOG = DARK_FACTORY_ROOT / "approval-audit.jsonl"


# ==========================================================================
# EXCEPTIONS (fail-enumerated fuer Audit)
# ==========================================================================

class ApprovalGateError(Exception):
    """Raised on any validation failure. Enumerated error-codes."""
    ERROR_CODES = {
        "NO_VALID_TOKEN",
        "TOKEN_EXPIRED",
        "INTENT_MISMATCH",
        "REALM_MISMATCH",
        "UNKNOWN_KEY",
        "KEY_REVOKED",
        "KEY_GRACE_EXPIRED",
        "INVALID_SIGNATURE",
        "BUNDLE_HASH_CHANGED",
        "SCHEMA_VERSION_CHANGED",
        "CANONIZER_VERSION_CHANGED",
        "CAS_MISMATCH",
        "PARENT_REVISION_ROLLED_BACK",
        "WRITE_SET_INVALID",
    }


# ==========================================================================
# DATA-CLASSES
# ==========================================================================

@dataclass(frozen=True)
class PromotionManifest:
    """Was genau promotet wird. Codex-Einwand #3: Scope zu schmal."""
    bundle_hash: str              # SHA256 ueber Artefakte + Inputs
    write_set: list[dict]         # [{"table": "book_revisions", "row_key": "...", "row_value": "..."}]
    schema_version: str           # DB-Schema-Hash zum Approval-Zeitpunkt
    canonizer_version: str        # z.B. "sha256-v1"
    promotion_code_sha: str       # Git-Commit-SHA der Promotion-Logik


@dataclass(frozen=True)
class ApprovalPayload:
    """Kanonisiert signiertes Payload. Codex-Einwand #4: token_id + realm_id."""
    version: int
    token_id: str                 # UUID-v4
    realm_id: str
    book_id: str
    revision_id: str
    promotion_manifest: PromotionManifest
    approval_timestamp: str       # ISO8601
    expires_at: str               # ISO8601
    key_id: str
    martin_intent: str            # "promote_to_canon" | "approve_draft" | "approve_template_update"
    state_version_expected: int


# ==========================================================================
# CANONICALIZATION
# ==========================================================================

def canonicalize(payload: dict) -> bytes:
    """Deterministic bytes fuer Signatur. MUSS reproduzierbar sein."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


# ==========================================================================
# BUNDLE-HASH COMPUTATION
# ==========================================================================

def build_promotion_manifest(conn: sqlite3.Connection, book_id: str, revision_id: str) -> PromotionManifest:
    """Berechne aktuelles Promotion-Manifest. Wird bei Approval UND bei Verify aufgerufen.

    STUB: echte Implementierung muss:
    1. output_artifacts_sha: SHA256 ueber alle Files die promoted werden
    2. template_versions: {tpl_id: version} aus template_registry
    3. voice_baseline_id: aktuelle voice_baselines-ID
    4. vector_capsule_hash: aus context_capsules.namespace_hash
    5. base_canon_sha: git_head_sha("canon")
    6. change_set_chain: alle change_set_jsons in revision_chain
    7. write_set: aus change_propagator.stage2_invalidate resolved
    8. schema_version: sha256 der schema-DDL
    9. canonizer_version: Konstante im Code
    10. promotion_code_sha: git blob sha dieses Files + change_propagator.py
    """
    raise NotImplementedError("STUB: siehe Design-Doc §2 bundle_hash Komponenten")


def compute_bundle_hash(components: dict) -> str:
    """SHA256 ueber kanonisierte Components."""
    canon = canonicalize(components)
    return hashlib.sha256(canon).hexdigest()


# ==========================================================================
# KEY-MANAGEMENT
# ==========================================================================

def load_active_signing_key_id(conn: sqlite3.Connection) -> str:
    """Lies aktive key_id aus signing_keys. Codex-Einwand #2: state-separated."""
    row = conn.execute(
        "SELECT key_id FROM signing_keys WHERE state = 'active' LIMIT 1"
    ).fetchone()
    if not row:
        raise ApprovalGateError("UNKNOWN_KEY: no active key in signing_keys table")
    return row[0]


def load_public_key_pem(conn: sqlite3.Connection, key_id: str) -> dict:
    """Returnt dict mit public_key_pem + state + retired_at + revoked_at."""
    row = conn.execute("""
        SELECT public_key_pem, state, retired_at, revoked_at, algorithm
        FROM signing_keys WHERE key_id = ?
    """, (key_id,)).fetchone()
    if not row:
        raise ApprovalGateError(f"UNKNOWN_KEY: {key_id}")
    return dict(row)


def check_key_usable(key_row: dict, signing_timestamp: str) -> None:
    """Raised wenn key revoked oder grace expired.

    Codex-Einwand #2: Revoked hat keine Grace-Period. Retired: 30 Tage.
    """
    if key_row['state'] == 'revoked':
        raise ApprovalGateError("KEY_REVOKED")
    if key_row['state'] == 'retired':
        retired_at = datetime.fromisoformat(key_row['retired_at'])
        signing_at = datetime.fromisoformat(signing_timestamp)
        grace_days = (signing_at - retired_at).days
        if grace_days > DEFAULT_KEY_GRACE_DAYS:
            raise ApprovalGateError("KEY_GRACE_EXPIRED")
        # Pre-retirement-signatur: auch ok (grace_days <=0)


# ==========================================================================
# SIGNATURE-VERIFY (STUB)
# ==========================================================================

def verify_signature(public_key_pem: str, canonical_bytes: bytes, signature_b64: str) -> None:
    """Verify Ed25519 signature.

    STUB: echte Implementierung via cryptography:
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
        public_key = load_pem_public_key(public_key_pem.encode())
        public_key.verify(base64.b64decode(signature_b64), canonical_bytes)
    Raises: InvalidSignature
    """
    raise NotImplementedError("STUB: implementiere Ed25519-Verify via cryptography")


# ==========================================================================
# ROLLBACK-CHAIN
# ==========================================================================

def walk_revision_chain(conn: sqlite3.Connection, book_id: str, revision_id: str) -> list[str]:
    """Returnt Liste aller Parent-Revisions (fuer Forward-Chain-Check)."""
    parents = []
    current = revision_id
    while current:
        row = conn.execute(
            "SELECT based_on FROM book_revisions WHERE revision_id = ?", (current,)
        ).fetchone()
        if not row or not row[0]:
            break
        parents.append(row[0])
        current = row[0]
    return parents


# ==========================================================================
# AUDIT-LOGGING
# ==========================================================================

def audit_log(event: str, token_id: str | None = None, details: dict | None = None) -> None:
    """Append-only JSONL-Log. Parallel in SQLite-Table approval_audit_log."""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "token_id": token_id,
        "process_id": os.getpid(),
        "os_user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "details": details or {},
    }
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ==========================================================================
# MARTIN-SIDE: CREATE-APPROVAL (wird auf Martin-Host ausgefuehrt)
# ==========================================================================

def create_approval_envelope(
    conn_readonly: sqlite3.Connection,
    book_id: str,
    revision_id: str,
    intent: str,
    private_key_path: Path,
    passphrase: bytes | None = None
) -> Path:
    """Wird NUR auf Martin-Host ausgefuehrt. Schreibt Envelope in Vault-Inbox.

    STUB: Pflicht-Steps:
    1. build_promotion_manifest(conn_readonly, book_id, revision_id)
    2. Display manifest + ask Martin [y/N/diff]
    3. Build Payload (token_id=uuid4, realm=REALM_ID, ...)
    4. canonicalize(payload)
    5. Load private_key from private_key_path (passphrase-protected PKCS#8)
    6. signature = private_key.sign(canonical_bytes)
    7. Write envelope = {payload, signature_b64, canonical_bytes_sha} to VAULT_INBOX/<token_id>.json
    8. Audit-Log-Event "APPROVAL_ISSUED"
    """
    raise NotImplementedError("STUB: siehe Design-Doc §3 Martin-Side")


# ==========================================================================
# IMPORT-ENVELOPE (wird von Promotion-Service ausgefuehrt, separater OS-Account)
# ==========================================================================

def import_approval_envelope(
    conn_write: sqlite3.Connection,
    envelope_path: Path
) -> str:
    """Importiert Envelope-JSON aus Vault-Inbox in approval_tokens-Table.

    STUB: Pflicht-Steps:
    1. Load envelope JSON
    2. Verify signature (verhindert korrupte Envelopes)
    3. BEGIN IMMEDIATE
    4. INSERT INTO approval_tokens (token_id, realm_id, book_id, revision_id,
       payload_json, signature_b64, key_id, martin_intent,
       state_version_expected, bundle_hash, created_at, expires_at)
    5. Audit-Log-Event "TOKEN_IMPORTED"
    6. Move envelope from inbox to imported-dir
    """
    raise NotImplementedError("STUB: siehe Design-Doc §4.4 Promotion-Service")


# ==========================================================================
# VERIFIER-SIDE: verify_and_consume (zentrale Gate-Logik)
# ==========================================================================

def verify_and_consume(
    conn: sqlite3.Connection,
    book_id: str,
    revision_id: str,
    expected_intent: str = "promote_to_canon"
) -> dict:
    """Consume valid approval token. Raises ApprovalGateError on any failure.
    Returns dict with token details for audit.

    KRITISCH: BEGIN IMMEDIATE Pflicht (WAL-Mode erforderlich).
    Diese Funktion ist der einzige Pfad fuer stage5_atomic_promotion.
    """
    # BEGIN IMMEDIATE fuer Race-Condition-Schutz
    conn.isolation_level = None  # Manuell bewusst
    conn.execute("BEGIN IMMEDIATE")
    token_id = None
    try:
        # 1. Fetch active token (UNIQUE-Constraint stellt sicher: max 1 active)
        token = conn.execute("""
            SELECT * FROM approval_tokens
            WHERE book_id = ? AND revision_id = ? AND consumed_at IS NULL
            ORDER BY created_at DESC LIMIT 1
        """, (book_id, revision_id)).fetchone()
        if not token:
            raise ApprovalGateError("NO_VALID_TOKEN")
        token = dict(token)
        token_id = token['token_id']

        # 2. Expiration
        if datetime.fromisoformat(token['expires_at']) < datetime.now(timezone.utc):
            raise ApprovalGateError("TOKEN_EXPIRED")

        # 3. Intent
        if token['martin_intent'] != expected_intent:
            raise ApprovalGateError(f"INTENT_MISMATCH")

        # 4. Realm
        if token['realm_id'] != REALM_ID:
            raise ApprovalGateError("REALM_MISMATCH")

        # 5. Key-State
        key_row = load_public_key_pem(conn, token['key_id'])
        payload = json.loads(token['payload_json'])
        check_key_usable(key_row, payload['approval_timestamp'])

        # 6. Signature-Verify
        canonical_bytes = canonicalize(payload)
        verify_signature(key_row['public_key_pem'], canonical_bytes, token['signature_b64'])

        # 7. Bundle-Hash-Binding (TOCTOU)
        current_manifest = build_promotion_manifest(conn, book_id, revision_id)
        if not hmac.compare_digest(current_manifest.bundle_hash, payload['promotion_manifest']['bundle_hash']):
            raise ApprovalGateError("BUNDLE_HASH_CHANGED")

        # 8. Schema/Canonizer-Version
        if current_manifest.schema_version != payload['promotion_manifest']['schema_version']:
            raise ApprovalGateError("SCHEMA_VERSION_CHANGED")
        if current_manifest.canonizer_version != payload['promotion_manifest']['canonizer_version']:
            raise ApprovalGateError("CANONIZER_VERSION_CHANGED")

        # 9. Promotion-Code-SHA (Codex-Einwand #3)
        if current_manifest.promotion_code_sha != payload['promotion_manifest']['promotion_code_sha']:
            raise ApprovalGateError("CANONIZER_VERSION_CHANGED")  # or dedicated code_sha check

        # 10. CAS
        current_state_ver = conn.execute(
            "SELECT state_version FROM book_state WHERE book_id = ?", (book_id,)
        ).fetchone()[0]
        if current_state_ver != payload['state_version_expected']:
            raise ApprovalGateError("CAS_MISMATCH")

        # 11. Forward-Chain-Check (Rollback)
        for parent_rev in walk_revision_chain(conn, book_id, revision_id):
            parent_status = conn.execute(
                "SELECT status FROM book_revisions WHERE revision_id = ?", (parent_rev,)
            ).fetchone()[0]
            if parent_status == 'rolled_back':
                raise ApprovalGateError(f"PARENT_REVISION_ROLLED_BACK")

        # 12. Execute write_set (Single-Source-of-Truth)
        for write_op in payload['promotion_manifest']['write_set']:
            execute_write_op(conn, write_op)

        # 13. Bump state_version
        conn.execute(
            "UPDATE book_state SET state_version = state_version + 1 WHERE book_id = ?",
            (book_id,)
        )

        # 14. Mark token consumed
        conn.execute("""
            UPDATE approval_tokens
            SET consumed_at = ?, consumed_by_process_id = ?
            WHERE token_id = ?
        """, (datetime.now(timezone.utc).isoformat(), os.getpid(), token_id))

        # 15. Audit
        audit_log("CONSUMED", token_id, {"intent": expected_intent})
        conn.execute("""
            INSERT INTO approval_audit_log (token_id, event, timestamp, actor_process_id, actor_os_user)
            VALUES (?, 'CONSUMED', ?, ?, ?)
        """, (token_id, datetime.now(timezone.utc).isoformat(), os.getpid(), os.environ.get("USERNAME", "unknown")))

        conn.commit()
        return token
    except Exception as e:
        conn.rollback()
        audit_log("VERIFY_FAILED", token_id, {"error": str(e)})
        raise


def execute_write_op(conn: sqlite3.Connection, write_op: dict) -> None:
    """Safe-executes a single write operation from promotion_manifest.write_set.

    STUB: Whitelist-based, KEINE beliebigen SQL-Strings!
    Nur vordefinierte Operationen:
    - {"op": "promote_revision", "revision_id": "..."}
    - {"op": "set_chapter_status", "chapter_no": N, "status": "canon"}
    """
    raise NotImplementedError("STUB: whitelist-based write_op executor")


# ==========================================================================
# PUBLIC API: Pre-Flight-Helper fuer run_control_kernel
# ==========================================================================

def has_valid_approval_token(conn: sqlite3.Connection, book_id: str, revision_id: str) -> bool:
    """Dry-run check: existiert valid token? Verbraucht NICHT."""
    token = conn.execute("""
        SELECT token_id, expires_at FROM approval_tokens
        WHERE book_id = ? AND revision_id = ? AND consumed_at IS NULL
          AND realm_id = ?
        ORDER BY created_at DESC LIMIT 1
    """, (book_id, revision_id, REALM_ID)).fetchone()
    if not token:
        return False
    if datetime.fromisoformat(token[1]) < datetime.now(timezone.utc):
        return False
    return True


# ==========================================================================
# ADMIN-TOOLS (separate CLI-Scripts in Production)
# ==========================================================================

def revoke_key(conn: sqlite3.Connection, key_id: str, reason: str) -> None:
    """Kompromittierter Key. Invalidiert ALLE Tokens dieser key_id. Keine Grace.
    STUB: Martin-CLI via `martin_key_revoke.py --key-id mk-2026-Q2 --reason "..."`
    """
    raise NotImplementedError("STUB: siehe Design-Doc §6 Compromised-Key-Scenario")


def rotate_key(conn: sqlite3.Connection, new_public_pem: str, new_key_id: str) -> None:
    """Normal-Rotation. Aktiver Key -> retired (30d Grace). Neuer Key -> active.
    STUB: Martin-CLI via `martin_key_rotate.py --new-key-file <pem>`
    """
    raise NotImplementedError("STUB: siehe Design-Doc §2 Rotation")


def rollback_revision(conn: sqlite3.Connection, revision_id: str, reason: str) -> None:
    """Markiert Revision als rolled_back. Verhindert zukuenftige Approvals auf Kindern.
    STUB: siehe Design-Doc §6 Normal-Rollback
    """
    raise NotImplementedError("STUB: siehe Design-Doc §6 Normal-Rollback")


# ==========================================================================
# MAIN (CLI-Integration fuer Admin-Tools)
# ==========================================================================

def main():
    """Entry-point. Delegiert zu Admin-Tools je nach Flag."""
    import argparse
    ap = argparse.ArgumentParser(description="HMAC Approval-Gate Admin (STUB)")
    ap.add_argument("--status", action="store_true", help="Zeige aktive Tokens + Key-State")
    ap.add_argument("--db", default=str(DARK_FACTORY_ROOT / "registry.sqlite"))
    args = ap.parse_args()

    if args.status:
        print("STUB: status-command nicht implementiert.")
        print(f"Schema-Extensions-Pfad: ~/.claude/skills/graphity-book-meta-learn/schemas/hmac-approval.schema.sql")
        print(f"Design-Doc: branch-hub/findings/DESIGN-P0-1-HMAC-APPROVAL-GATE-2026-04-19.md")
        sys.exit(0)
    ap.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()

# [CRUX-MK]
