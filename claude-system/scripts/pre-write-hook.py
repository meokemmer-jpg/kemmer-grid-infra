#!/usr/bin/env python3
"""
Pre-Write-Hook Orchestrator [CRUX-MK]

Claude-Code-Hook-Target fuer PreToolUse-Event auf Write/Edit.

Liest stdin-JSON (Claude-Code-Hook-Input), extrahiert file_path + content,
orchestriert die 4 Validator-Scripts und aggregiert die Ergebnisse.

Author: Opus 4.7 METAOPS, 2026-04-18
Mission-1 Hook-Orchestrator

Input-Format (stdin JSON, vom Claude-Code-Harness):
{
  "session_id": "...",
  "transcript_path": "...",
  "hook_event_name": "PreToolUse",
  "tool_name": "Write" | "Edit" | "MultiEdit",
  "tool_input": {
    "file_path": "...",
    "content": "..."  // Write
    // oder old_string/new_string fuer Edit
  }
}

Exit-Codes (Claude-Code-Hook-Semantik):
    0 = allow (OK)
    2 = blocking error, stderr shown to Claude as reason-to-stop

Default-Mode: CHECK (warnt, blockiert nicht) — Deploy-Sicherheit fuer erste Tage.
Per ENV var CLAUDE_HOOK_MODE=ENFORCE zur Haertung.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent

VALIDATORS = [
    ("frontmatter-validator.py", "Hook-1 Frontmatter meta-ebene"),
    ("two-channel-validator.py", "Hook-2 Zwei-Kanal-Regel"),
    ("e6-plus-rule-blocker.py", "Hook-3 E6+-Rule-Blocker"),
    ("cross-llm-verdict-gate.py", "Hook-4 Cross-LLM-Verdict-Gate"),
]

# Hook-5 Backlink-Validator uses a different invocation-contract (JSON-stdin, not CLI-args).
# Registered separately so run_validator() keeps its Hook-1..4 contract unchanged.
# Shadow-Mode: own ENV CLAUDE_BACKLINK_HOOK_MODE (default CHECK) — so global ENFORCE
# cannot accidentally block writes before the 7-day review window closes.
BACKLINK_VALIDATOR = ("backlink-requirement-validator.py", "Hook-5 Backlink-Requirement (Shadow)")

AUDIT_LOG = Path("G:/Meine Ablage/Claude-Knowledge-System/branch-hub/audit/pre-write-hook.jsonl")


def log_audit(entry: dict):
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # Audit-Log failure darf Hook nicht blockieren


def run_validator(script_name: str, file_path: str, content: str, mode: str) -> tuple[int, str, str]:
    """Returns (exit_code, stdout, stderr)"""
    script_path = SCRIPT_DIR / script_name
    if not script_path.exists():
        return 3, "", f"Script nicht gefunden: {script_path}"

    try:
        proc = subprocess.run(
            ["python", str(script_path), file_path, "--content-stdin", f"--mode={mode}"],
            input=content,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        return proc.returncode, proc.stdout or "", proc.stderr or ""
    except subprocess.TimeoutExpired:
        return 3, "", f"Validator {script_name} timeout (30s)"
    except Exception as e:
        return 3, "", f"Validator {script_name} error: {e}"


def run_backlink_validator(tool_name: str, file_path: str, content: str, backlink_mode: str) -> tuple[int, str, str]:
    """Hook-5: invokes backlink-requirement-validator.py via JSON-stdin (native contract).

    Uses its OWN mode (CLAUDE_BACKLINK_HOOK_MODE) — not the global CLAUDE_HOOK_MODE.
    This preserves Shadow-Mode for 7-day observation even when Hook-1..4 run ENFORCE.
    Returns (exit_code, stdout, stderr)."""
    script_path = SCRIPT_DIR / BACKLINK_VALIDATOR[0]
    if not script_path.exists():
        return 3, "", f"Script nicht gefunden: {script_path}"

    payload = {
        "tool_name": tool_name,
        "tool_input": {"file_path": file_path, "content": content or ""},
    }
    stdin_data = json.dumps(payload, ensure_ascii=False)

    # Child-Env: override CLAUDE_HOOK_MODE with per-hook Shadow-Mode var.
    # The validator itself reads CLAUDE_HOOK_MODE internally — so we pass the
    # Shadow-Mode value under that name only for this subprocess.
    env = dict(os.environ)
    env["CLAUDE_HOOK_MODE"] = backlink_mode
    # Also keep original global mode under a different var for potential future use.
    env["CLAUDE_BACKLINK_HOOK_MODE"] = backlink_mode

    try:
        proc = subprocess.run(
            ["python", str(script_path)],
            input=stdin_data,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            env=env,
        )
        # Parse JSON-stdout of backlink-validator -> normalize to stderr-message for orchestrator.
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        status = ""
        reason = ""
        try:
            result = json.loads(stdout.strip().splitlines()[-1]) if stdout.strip() else {}
            status = result.get("status", "")
            reason = result.get("reason", "")
        except Exception:
            pass

        msg_parts = []
        if status in {"WARN", "BLOCK"}:
            msg_parts.append(f"Backlink-Validator [{status}] reason={reason} file={file_path}")
        if stderr.strip():
            msg_parts.append(stderr.strip())
        combined_stderr = " | ".join(msg_parts) if msg_parts else ""
        return proc.returncode, stdout, combined_stderr
    except subprocess.TimeoutExpired:
        return 3, "", f"Backlink-Validator timeout (30s)"
    except Exception as e:
        return 3, "", f"Backlink-Validator error: {e}"


def extract_write_content(tool_input: dict, tool_name: str) -> str | None:
    """Extract the effective new content from tool_input."""
    if tool_name == "Write":
        return tool_input.get("content", "")
    elif tool_name == "Edit":
        # Fuer Edit: nur new_string, nicht der volle File-Content. Partial-Check.
        # Ein voller Content-Check wuerde file_path-Existenz voraussetzen. Skip fuer jetzt.
        return None  # Edit -> skip content-checks, nur path-based Pruefung
    elif tool_name == "MultiEdit":
        return None  # Gleich wie Edit
    else:
        return None


def main():
    timestamp = datetime.now().isoformat()
    mode = os.environ.get("CLAUDE_HOOK_MODE", "CHECK").upper()
    if mode not in {"CHECK", "ENFORCE", "AUDIT"}:
        mode = "CHECK"

    # Hook-5 Backlink-Validator runs in its own Shadow-Mode until 7-day review closes.
    # Default CHECK — only flips to ENFORCE via explicit ENV (not by the global flag).
    backlink_mode = os.environ.get("CLAUDE_BACKLINK_HOOK_MODE", "CHECK").upper()
    if backlink_mode not in {"CHECK", "ENFORCE", "AUDIT"}:
        backlink_mode = "CHECK"

    entry = {
        "ts": timestamp,
        "tool": "pre-write-hook",
        "mode": mode,
        "backlink_mode": backlink_mode,
    }

    try:
        raw = sys.stdin.read()
        if not raw.strip():
            entry["status"] = "NO_INPUT"
            log_audit(entry)
            return 0
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        entry["status"] = "BAD_JSON"
        entry["error"] = str(e)
        log_audit(entry)
        sys.stderr.write(f"[pre-write-hook] Ignoring bad JSON input: {e}\n")
        return 0  # Nicht blockieren bei Hook-Infrastruktur-Fehlern

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path") or tool_input.get("path") or ""
    entry["tool_name"] = tool_name
    entry["file_path"] = file_path

    if tool_name not in {"Write", "Edit", "MultiEdit"}:
        entry["status"] = "WRONG_TOOL"
        log_audit(entry)
        return 0

    if not file_path:
        entry["status"] = "NO_FILE_PATH"
        log_audit(entry)
        return 0

    content = extract_write_content(tool_input, tool_name)
    if content is None:
        # Edit/MultiEdit: nur Pfad-basierte Pruefung (Hook-3: E6+-Blocker checkt nur Pfad)
        # Hook-1/2/4 brauchen Content — skip fuer Edit.
        content = ""

    # Run all validators (Edit/MultiEdit: nur path-basierte Validators)
    results = []
    max_exit = 0
    stderrs = []

    # METAD2 Mission-1e Fix (2026-04-18):
    # Im CHECK-Mode geben Validators Exit 0 fuer WARN zurueck (rules/cross-llm-simulation.md M4 Konvention).
    # Vorher wurde stderr nur bei exit_code > 0 aggregiert -> CHECK-Mode-WARNs waren komplett unsichtbar.
    # Fix: Aggregiere ALLE non-empty stderr-Strings aus den Validators, unabhaengig vom exit_code.
    # Block-Decision bleibt mode-basiert.
    for script_name, hook_label in VALIDATORS:
        if tool_name in {"Edit", "MultiEdit"} and script_name != "e6-plus-rule-blocker.py":
            continue
        exit_code, stdout, stderr = run_validator(script_name, file_path, content, mode)
        results.append({
            "hook": hook_label,
            "exit": exit_code,
            "stderr": stderr.strip()[:500] if stderr else "",
        })
        max_exit = max(max_exit, exit_code)
        # v2: stderr immer aggregieren, nicht nur bei exit > 0
        if stderr and stderr.strip():
            stderrs.append(f"[{hook_label}] {stderr.strip()}")

    # Hook-5 Backlink-Validator (runs after Hook-1..4, uses native JSON-stdin contract + own Shadow-Mode)
    # Only Write events carry content; Edit/MultiEdit skipped (same as Hook-1/2/4).
    if tool_name == "Write" and content is not None:
        h5_exit, h5_stdout, h5_stderr = run_backlink_validator(tool_name, file_path, content, backlink_mode)
        results.append({
            "hook": BACKLINK_VALIDATOR[1],
            "exit": h5_exit,
            "stderr": h5_stderr.strip()[:500] if h5_stderr else "",
        })
        # Hook-5 cannot escalate max_exit beyond Shadow-Mode limit:
        # only count its exit-code toward blocking when backlink_mode == ENFORCE.
        if backlink_mode == "ENFORCE":
            max_exit = max(max_exit, h5_exit)
        if h5_stderr and h5_stderr.strip():
            stderrs.append(f"[{BACKLINK_VALIDATOR[1]}] {h5_stderr.strip()}")

    entry["results"] = results
    entry["max_exit"] = max_exit
    log_audit(entry)

    # Aggregate stderr for Claude — auch im CHECK-Mode sichtbar
    if stderrs:
        for msg in stderrs:
            sys.stderr.write(msg + "\n")
        # Header zur Klarstellung in welchem Modus wir laufen
        if mode == "CHECK":
            sys.stderr.write(f"[pre-write-hook] CHECK-Mode active (no block) — set CLAUDE_HOOK_MODE=ENFORCE to harden\n")

    # Final exit decision
    if mode == "ENFORCE" and max_exit >= 2:
        return 2
    elif mode == "ENFORCE" and max_exit == 1:
        # WARN im ENFORCE: nicht blockieren, aber stderr wird angezeigt
        return 0
    else:
        # CHECK / AUDIT: nie blockieren
        return 0


if __name__ == "__main__":
    sys.exit(main())
