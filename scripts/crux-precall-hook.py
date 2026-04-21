#!/usr/bin/env python3
# [CRUX-MK] Layer 0 — LiteLLM Pre-Call-Hook
# rho-Impact:       Live-Tracking aller LLM-Calls, CRUX-Gate gegen Fehl-Routing
# K_0/Q_0/I_min:    K_0/Q_0-Tasks erzwingen Claude-Opus-Arbitration, nicht Routine-LLM
# Wargame-Status:   alignment_passed (Masterplan v2 Patch P6 Criticality-Budgeting)

"""
LiteLLM Pre-Call-Hook fuer CRUX-MK Layer-0-Verankerung.

Integration in litellm-router-config.yaml:
  callbacks:
    - type: pre_call
      path: scripts/crux-precall-hook.py:crux_pre_call

Verhalten:
- Classify task via metadata-Tags -> criticality_score (0-1)
- criticality >= 0.7 + model != claude-opus-4.7 -> Exception "CRUX-Gate: Premium-Route required"
- criticality >= 0.4 + model == gemma2-27b-local -> Exception "CRUX-Gate: Local-Only insufficient"
- Log jeden Call in ~/.kemmer-grid/rho-tracking.jsonl
"""

import json
import pathlib
import datetime
from typing import Any, Dict

CRUX_LOG_DIR = pathlib.Path.home() / ".kemmer-grid"
CRUX_LOG_DIR.mkdir(exist_ok=True)
RHO_TRACKING_FILE = CRUX_LOG_DIR / "rho-tracking.jsonl"
KILL_FLAG = CRUX_LOG_DIR / "killed.flag"

# Criticality-Tag-Gewichte aus Masterplan v2 Patch P6
TAG_WEIGHTS = {
    # K_0 (Kapital-Relevant)
    "capital": 0.4, "finance": 0.4, "trading": 0.4, "kpm": 0.4,
    "wegzugssteuer": 0.4, "vermoegen": 0.4, "investment": 0.4,
    # Q_0 (Familie)
    "family": 0.4, "gerdi": 0.4, "brueder": 0.4, "marriage": 0.4,
    "familie": 0.4, "martin-gerdi": 0.4, "gesundheit": 0.35,
    # Phronesis (L13, nicht delegierbar)
    "rule-design": 0.4, "crux": 0.4, "l13": 0.5, "phronesis": 0.5,
    "martin-only": 0.5, "strategic": 0.3,
    # Irreversible
    "delete": 0.3, "push-main": 0.3, "publish": 0.3, "force": 0.3,
    # Cross-LLM-Synthese (Meta-E4+)
    "meta-audit": 0.4, "e4-claim": 0.4, "fixpunkt": 0.4,
}


def compute_criticality(metadata: Dict[str, Any]) -> float:
    """Berechnet criticality_score aus Tags in metadata."""
    score = 0.0
    tags = metadata.get("tags", []) or []
    if isinstance(tags, str):
        tags = [tags]
    for tag in tags:
        tag_lower = str(tag).lower()
        score += TAG_WEIGHTS.get(tag_lower, 0.0)
    # Cap bei 1.0
    return min(score, 1.0)


def crux_pre_call(data: Dict[str, Any]) -> bool:
    """
    Pre-call hook fuer LiteLLM.

    Args:
        data: LiteLLM-Call-Data mit model, messages, metadata.

    Returns:
        True wenn Call erlaubt.

    Raises:
        Exception wenn CRUX-Gate verletzt (Premium-Route required oder Local-Only insufficient).
    """
    # Kill-Switch-Check zuerst
    if KILL_FLAG.exists():
        raise Exception(f"[CRUX-MK] Kill-Switch aktiv ({KILL_FLAG}). LLM-Call verweigert.")

    model = data.get("model", "")
    metadata = data.get("metadata", {}) or {}

    # Criticality berechnen
    criticality = compute_criticality(metadata)
    task_family = metadata.get("task_family", "unknown")

    # Gate-Checks (Premium-Escalation)
    if criticality >= 0.7 and "claude-opus" not in model.lower():
        log_call(model, criticality, task_family, metadata, verdict="REJECT",
                 reason=f"criticality={criticality:.2f} requires claude-opus-4.7")
        raise Exception(
            f"[CRUX-MK] Gate: criticality={criticality:.2f} erfordert Premium-Route "
            f"(claude-opus-4.7). Aktuelles Model: {model}. "
            f"Tags: {metadata.get('tags', [])}"
        )

    if criticality >= 0.4 and "gemma" in model.lower() and "local" in model.lower():
        log_call(model, criticality, task_family, metadata, verdict="REJECT",
                 reason=f"criticality={criticality:.2f} exceeds local-only threshold")
        raise Exception(
            f"[CRUX-MK] Gate: criticality={criticality:.2f} zu hoch fuer local-only. "
            f"Nutze Cloud-Tier (claude-sonnet/gemini/codex). Model: {model}"
        )

    # Pass: Log und return
    log_call(model, criticality, task_family, metadata, verdict="PASS", reason=None)
    return True


def log_call(model: str, criticality: float, task_family: str,
             metadata: Dict[str, Any], verdict: str, reason: Any) -> None:
    """Schreibt Call-Eintrag in rho-tracking.jsonl."""
    entry = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "model": model,
        "criticality_score": criticality,
        "task_family": task_family,
        "metadata_tags": metadata.get("tags", []),
        "estimated_rho_eur": metadata.get("estimated_rho", "not_provided"),
        "verdict": verdict,
        "reason": reason,
    }
    try:
        with open(RHO_TRACKING_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # Logging darf Call nicht blockieren bei File-Fail


if __name__ == "__main__":
    # Standalone-Test
    import sys
    test_data = {
        "model": sys.argv[1] if len(sys.argv) > 1 else "gemma2:27b-local",
        "metadata": {
            "tags": sys.argv[2].split(",") if len(sys.argv) > 2 else ["test"],
            "task_family": "test",
        },
    }
    try:
        result = crux_pre_call(test_data)
        print(f"CRUX-Gate: PASS (criticality={compute_criticality(test_data['metadata']):.2f})")
    except Exception as e:
        print(f"CRUX-Gate: REJECT - {e}")
        sys.exit(1)
