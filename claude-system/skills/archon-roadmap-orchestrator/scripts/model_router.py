#!/usr/bin/env python3
"""
model_router.py - Capability-aware Modell-Routing mit Backoff-statt-Downgrade

Usage:
  python model_router.py --task-type priorization --context-tokens 50000
  python model_router.py --route-all roadmap-priorization-batch.json

Returns: JSON {"model": "claude-sonnet-4-6", "fallback_chain": [...], "reason": "..."}
"""
import argparse, json, os, sys
from datetime import datetime, timezone


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

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(SKILL_DIR, "capability-registry.json")

def load_registry():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def score_model(model_spec: dict, task_type: str, context_tokens: int,
                rate_state: dict) -> float:
    """Higher = better fit."""
    caps = model_spec.get("capabilities", [])
    typical = model_spec.get("typical_use", [])
    score = 0.0
    # Bonus fuer explicit task-type-match
    if task_type in typical:
        score += 3.0
    # Context-fit
    window = model_spec.get("context_window", 0)
    if context_tokens > 0 and window < context_tokens:
        return -1e9  # impossible
    if window >= context_tokens * 1.5:  # comfortable fit
        score += 1.0
    # Rate-limit-Reserve (weniger verbraucht = besser)
    calls_today = rate_state.get("calls_today", 0)
    rate_per_min = model_spec.get("rate_limit_per_min", 999)
    if rate_per_min > 0:
        score += min(2.0, (rate_per_min - calls_today * 0.1) / rate_per_min * 2)
    # Cost-Penalty (hoehere Kosten = weniger Score bei gleicher Capability)
    cost_in = model_spec.get("cost_per_1k_input", 0)
    if cost_in > 0:
        score -= min(1.0, cost_in * 100)  # 0.015 → -0.15
    # Browser-Requirement-Penalty (braucht separaten Web-Worker)
    if model_spec.get("requires_browser", False):
        score -= 2.0
    return score

def route(task_type: str, context_tokens: int = 10000,
          exclude_models: list = None) -> dict:
    registry = load_registry()
    exclude_models = exclude_models or []
    routing = registry.get("task_type_routing", {}).get(task_type, {})
    primary = routing.get("primary")
    never = routing.get("never", [])
    models = registry.get("models", {})

    # Candidates sind alle, die nicht in never sind + not excluded + task-type-compatible
    candidates = []
    for name, spec in models.items():
        if name in never or name in exclude_models:
            continue
        rate_state = {"calls_today": 0}  # TODO: track via state/rate-tracker.json
        s = score_model(spec, task_type, context_tokens, rate_state)
        if s > -1e8:
            candidates.append((name, s, spec))

    if not candidates:
        return {"model": None, "fallback_chain": [], "reason": "no-capable-model",
                "escalate_to_martin": True}

    # Sortieren: primary kommt zuerst wenn capable
    candidates.sort(key=lambda x: (0 if x[0] == primary else 1, -x[1]))
    chosen = candidates[0]
    fallback_chain = [c[0] for c in candidates[1:4]]

    return {
        "model": chosen[0],
        "fallback_chain": fallback_chain,
        "reason": f"task-type={task_type}, score={chosen[1]:.2f}",
        "escalate_to_martin": routing.get("escalate_to_martin", False),
        "context_window": chosen[2].get("context_window"),
        "requires_browser": chosen[2].get("requires_browser", False)
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task-type", required=True)
    p.add_argument("--context-tokens", type=int, default=10000)
    p.add_argument("--exclude", default="", help="comma-separated models to exclude")
    args = p.parse_args()
    exclude = args.exclude.split(",") if args.exclude else []
    result = route(args.task_type, args.context_tokens, exclude)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
