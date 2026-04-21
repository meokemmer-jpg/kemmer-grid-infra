#!/usr/bin/env python3
# [CRUX-MK] Layer 0 — PreToolUse-Hook fuer Claude Code
# Martin-Direktive 2026-04-21 "Option A" (aggressive Durchsetzung, jeder Tool-Call)
#
# Verhalten:
# - Liest Claude-Code Tool-Event von stdin (JSON)
# - Classified Tool-Call nach Risiko
# - Ruft crux-check.sh/.ps1 mit passenden Args
# - Exit-Code zurueck an Claude:
#   0 = allow tool
#   1 = block tool (Martin-Review)
#   2 = warn (tool proceedsaber geloggt)
#
# Performance-kritisch: muss <200ms laufen, sonst bremst Session-Latenz.
# Default = FAST-PASS fuer unkritische Patterns.

import json
import sys
import os
import pathlib
import time
import re

CRUX_LOG_DIR = pathlib.Path.home() / ".kemmer-grid"
CRUX_LOG_DIR.mkdir(exist_ok=True)
TOOL_TRACK = CRUX_LOG_DIR / "tool-events.jsonl"
KILL_FLAG = CRUX_LOG_DIR / "killed.flag"

# Fast-Pass-Patterns (unkritische Tools, sofort PASS)
FAST_PASS_TOOLS = {"Read", "Glob", "Grep", "LS", "ToolSearch", "mcp__ccd_session__mark_chapter"}

# Bedenkliche Pfad-Patterns (WARN-Level)
WARN_PATTERNS = [
    r"git\s+push\s+.*\s+(-f|--force|main|master)",
    r"rm\s+-rf",
    r"DROP\s+(TABLE|DATABASE)",
    r"schtasks\s+/delete",
    r"launchctl\s+bootout",
    r"del\s+/[sSqQ]",
    r"Remove-Item.*-Recurse.*-Force",
]

# K_0-Kritische Patterns (REJECT, nur mit Martin-Override)
REJECT_PATTERNS = [
    r"git\s+push\s+--force.*\s+(main|master)",
    r"rm\s+-rf\s+[/~].*",  # rm -rf / oder ~
    r"format\s+[cC]:",
    r"schtasks\s+/delete.*/tn\s+\*",
]


def read_tool_event():
    """Liest Tool-Event-JSON von stdin."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except Exception:
        return {}


def classify_risk(tool_name, tool_input):
    """Returns (verdict, reason) — PASS/WARN/REJECT."""
    # Kill-Switch
    if KILL_FLAG.exists():
        return "REJECT", "kill-switch active"

    # Fast-Pass
    if tool_name in FAST_PASS_TOOLS:
        return "PASS", "fast-pass-tool"

    # Bash-/Shell-Command-Analyse
    if tool_name == "Bash":
        cmd = str(tool_input.get("command", ""))
        for pat in REJECT_PATTERNS:
            if re.search(pat, cmd, re.IGNORECASE):
                return "REJECT", f"destructive pattern: {pat[:40]}"
        for pat in WARN_PATTERNS:
            if re.search(pat, cmd, re.IGNORECASE):
                return "WARN", f"sensitive pattern: {pat[:40]}"
        return "PASS", "bash-no-risk-pattern"

    # Write/Edit auf kritische Pfade
    if tool_name in {"Write", "Edit"}:
        file_path = str(tool_input.get("file_path", ""))
        # Kritische Pfade = Rules, Settings, CRUX-Files
        if re.search(r"\.claude[/\\]rules[/\\]", file_path):
            return "WARN", "rules-write (Verfassungs-Rang)"
        if re.search(r"CLAUDE\.md$", file_path):
            return "WARN", "CLAUDE.md-edit (Verfassungs-Rang)"
        if re.search(r"CRUX-MK\.md$", file_path):
            return "WARN", "CRUX-MK-edit (Layer 0)"
        if re.search(r"settings\.json$", file_path):
            return "WARN", "settings.json-edit"
        return "PASS", "write-standard"

    # Agent-Spawn (Subagent-Call)
    if tool_name == "Agent":
        desc = str(tool_input.get("description", "")).lower()
        if any(t in desc for t in ["delete", "force", "destroy"]):
            return "WARN", "agent-destructive-intent"
        return "PASS", "agent-standard"

    # PowerShell
    if tool_name == "PowerShell":
        cmd = str(tool_input.get("command", ""))
        for pat in REJECT_PATTERNS:
            if re.search(pat, cmd, re.IGNORECASE):
                return "REJECT", f"destructive: {pat[:40]}"
        for pat in WARN_PATTERNS:
            if re.search(pat, cmd, re.IGNORECASE):
                return "WARN", f"sensitive: {pat[:40]}"
        return "PASS", "powershell-no-risk"

    # Default: PASS fuer alles andere
    return "PASS", "default-pass"


def log_event(tool_name, verdict, reason, duration_ms):
    """Append-Log fuer alle Tool-Events."""
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tool": tool_name,
        "verdict": verdict,
        "reason": reason,
        "duration_ms": duration_ms,
    }
    try:
        with open(TOOL_TRACK, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def main():
    t_start = time.time()
    event = read_tool_event()
    tool_name = event.get("tool_name", "unknown")
    tool_input = event.get("tool_input", {})

    verdict, reason = classify_risk(tool_name, tool_input)
    duration_ms = int((time.time() - t_start) * 1000)

    log_event(tool_name, verdict, reason, duration_ms)

    # Output fuer Claude (optional, bei WARN/REJECT sichtbar)
    if verdict == "REJECT":
        print(f"[CRUX-MK] REJECT {tool_name}: {reason}", file=sys.stderr)
        sys.exit(1)
    elif verdict == "WARN":
        print(f"[CRUX-MK] WARN {tool_name}: {reason}", file=sys.stderr)
        # WARN proceeded (Exit 0), nur geloggt
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
