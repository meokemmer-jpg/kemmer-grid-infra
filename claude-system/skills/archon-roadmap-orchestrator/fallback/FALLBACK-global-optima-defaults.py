#!/usr/bin/env python3
"""
FALLBACK-global-optima-defaults.py

=== FALLBACK-ROUTINE (NUR FALLBACK, NACH N SUCCESSFUL RUNS LOESCHBAR) ===

Type: config-default
Reason: Wenn global-optima.json fehlt oder JSON-korrupt, liefert dieses Script
die Default-Werte. Verhindert Orchestrator-Crash bei Config-Problem.

To-Delete-When: global-optima.json hat Backup-Strategie (git + Snapshots)
                UND 30 Runs ohne Config-Loss gemessen
                UND Schema-Validation etabliert

Usage:
  python FALLBACK-global-optima-defaults.py [--write-if-missing]

Output: JSON auf stdout (Default-Optima)
Mit --write-if-missing: schreibt Defaults in global-optima.json falls fehlt
"""
import argparse, json, os, sys
from datetime import datetime, timezone

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPTIMA_PATH = os.path.join(SKILL_DIR, "global-optima.json")

DEFAULT_OPTIMA = {
    "schema_version": "1.0",
    "last_update": None,  # set at runtime
    "_fallback_source": "FALLBACK-global-optima-defaults.py",
    "_notice": "THIS IS A FALLBACK. Primary source is global-optima.json.",
    "zeitwertverfassung": {
        "CM_base_eur_per_action": {
            "meta-audit": 25.0,
            "classification": 2.0,
            "priorization": 15.0,
            "code-analysis": 20.0,
            "cross-llm-wargame": 50.0,
            "live-research": 10.0,
            "conflict-resolution": 30.0
        },
        "h_opportunity_per_year": 0.08,
        "Lambda_typical_per_day": {
            "meta-audit": 2, "classification": 20, "priorization": 6,
            "code-analysis": 10, "cross-llm-wargame": 3, "live-research": 4
        },
        "K_0_base_eur": 5000000,
        "Q_0_min": 0.9,
        "I_min_threshold": 0.85
    },
    "token_budgets": {
        "per_workflow_default_eur": 2.0,
        "per_session_warn_pct": 0.7,
        "per_session_block_pct": 0.95,
        "daily_global_cap_eur": 50.0,
        "per_action_ceiling_eur": 5.0
    },
    "rho_thresholds": {
        "HARDENED_promo_min": 2.0,
        "CONDITIONAL_min": 1.2,
        "Exploration_min": 1.0,
        "domain_overrides": {"K_0": 2.5, "Q_0": 1.4, "code": 1.3},
        "n_min_sessions_for_hardened": 5,
        "bayes_factor_min_k0": 10
    },
    "models": {
        "claude-opus-4-7-1m": {"cost_per_1k_input": 0.015, "cost_per_1k_output": 0.075},
        "claude-sonnet-4-6": {"cost_per_1k_input": 0.003, "cost_per_1k_output": 0.015},
        "claude-haiku-4-5": {"cost_per_1k_input": 0.0008, "cost_per_1k_output": 0.004},
        "gpt-5-4-codex": {"cost_per_1k_input": 0.005, "cost_per_1k_output": 0.020},
        "gemini-2-5-pro": {"cost_per_1k_input": 0.00125, "cost_per_1k_output": 0.005},
        "grok-ultra": {"cost_per_1k_input": 0.005, "cost_per_1k_output": 0.015}
    },
    "dark_factory_defaults": {
        "shadow_mode_decision_volume": 150,
        "max_cost_per_run_eur": 2.0,
        "max_fails_before_stop": 2,
        "hardcap_daily_eur": 12.0,
        "debounce_min": 30,
        "reconciliation_sweep_hours": [6, 24]
    },
    "hooks": {
        "on_optima_change": "python C:/Users/marti/.claude/skills/archon-roadmap-orchestrator/scripts/propagate_optima.py",
        "on_budget_breach": "python C:/Users/marti/.claude/skills/archon-roadmap-orchestrator/scripts/alert_martin.py --reason budget",
        "on_rho_negative": "python C:/Users/marti/.claude/skills/archon-roadmap-orchestrator/scripts/alert_martin.py --reason rho_negative"
    },
    "cross_llm_config": {
        "providers": ["gpt-5-4-codex", "gemini-2-5-pro"],
        "tie_break_provider": "grok-ultra",
        "require_external_anchoring_for_hardened": True,
        "max_retries_per_provider": 2,
        "backoff_strategy": "exponential"
    }
}


def get_defaults():
    d = dict(DEFAULT_OPTIMA)
    d["last_update"] = datetime.now(timezone.utc).astimezone().isoformat()
    return d


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--write-if-missing", action="store_true")
    args = p.parse_args()

    defaults = get_defaults()

    if args.write_if_missing and not os.path.exists(OPTIMA_PATH):
        with open(OPTIMA_PATH, "w", encoding="utf-8") as f:
            json.dump(defaults, f, indent=2, ensure_ascii=False)
        print(f"FALLBACK-OPTIMA written to {OPTIMA_PATH}", file=sys.stderr)

    print(json.dumps(defaults, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
