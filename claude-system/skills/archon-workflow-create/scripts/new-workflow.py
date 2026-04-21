#!/usr/bin/env python3
"""
new-workflow.py [CRUX-MK]
Interaktiver Archon-Workflow-Scaffolder.

Usage:
  python new-workflow.py [--non-interactive --name X --template Y --domain Z]

Schritte:
1. Fragt Martin nach Workflow-Metadaten (Name, Template, Domain, Budget, Triggers)
2. Liest passende Template-Datei
3. Platzhalter ersetzen ({{...}})
4. YAML schreiben nach learning-archon/.archon/workflows/<name>.yaml
5. Archon validate ausfuehren
6. Commit-Vorschlag ausgeben
"""
import argparse, os, re, subprocess, sys
from pathlib import Path
from datetime import datetime


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

SKILL_DIR = Path.home() / ".claude" / "skills" / "archon-workflow-create"
TEMPLATES_DIR = SKILL_DIR / "templates"
LEARNING_ARCHON = Path("C:/Users/marti/Projects/learning-archon")
BRANCH_HUB_MIRROR = Path("G:/Meine Ablage/Claude-Knowledge-System/branch-hub/.archon/workflows")

TEMPLATES = {
    "1": ("wargame", "wargame.yaml.template"),
    "2": ("knowledge-diff", "knowledge-diff.yaml.template"),
    "3": ("nlm-factory", "nlm-factory.yaml.template"),
    "4": ("custom", "custom.yaml.template"),
}


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"  {prompt}{suffix}: ").strip()
    return val if val else default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--non-interactive", action="store_true")
    ap.add_argument("--name")
    ap.add_argument("--template", choices=["wargame", "knowledge-diff", "nlm-factory", "custom"])
    ap.add_argument("--domain")
    ap.add_argument("--triggers")
    ap.add_argument("--budget-tokens", type=int, default=50000)
    ap.add_argument("--budget-eur", type=float, default=2.0)
    args = ap.parse_args()

    print("=== Archon Workflow Scaffolder [CRUX-MK] ===")
    print()

    if not args.non_interactive:
        print("Phase 1: PLAN")
        print()
        name = args.name or ask("Workflow-Name (kebab-case, z.B. learning-review)")
        print()
        print("  Template waehlen:")
        for k, (label, _) in TEMPLATES.items():
            print(f"    {k}. {label}")
        choice = ask("Welches Template? (1-4)", "4")
        template_label, template_file = TEMPLATES.get(choice, TEMPLATES["4"])
        print()
        domain = args.domain or ask("Domain (sae/9os/heylou/kpm/graphity/cape-coral/pmo/meta)", "meta")
        triggers = args.triggers or ask(
            'Triggers (komma-separiert, z.B. "review, wochen-review")',
            f"{name.replace('-', ' ')}"
        )
        budget_tokens = int(ask("Budget Tokens", str(args.budget_tokens)))
        budget_eur = float(ask("Budget EUR", str(args.budget_eur)))
    else:
        name = args.name
        template_label = args.template
        template_file = f"{args.template}.yaml.template"
        domain = args.domain or "meta"
        triggers = args.triggers or name.replace("-", " ")
        budget_tokens = args.budget_tokens
        budget_eur = args.budget_eur

    if not name:
        print("ERROR: --name required", file=sys.stderr)
        sys.exit(1)

    # Load template
    tmpl_path = TEMPLATES_DIR / template_file
    if not tmpl_path.exists():
        print(f"ERROR: Template {tmpl_path} not found", file=sys.stderr)
        sys.exit(1)
    content = tmpl_path.read_text(encoding="utf-8")

    # Substitute placeholders
    substitutions = {
        "{{WORKFLOW_NAME}}": name,
        "{{WORKFLOW_NAME_UPPER}}": name.upper().replace("-", "_"),
        "{{DOMAIN}}": domain,
        "{{DOMAIN_UPPER}}": domain.upper().replace("-", "_"),
        "{{DOMAIN_CONTEXT}}": f"Domain {domain}. Context aus MOC-{domain}.md lesen.",
        "{{TRIGGERS}}": triggers,
        "{{BUDGET_TOKENS}}": str(budget_tokens),
        "{{BUDGET_EUR}}": str(budget_eur),
        "{{WHEN_TO_USE}}": f"User wants to invoke {name}",
        "{{WHAT_IT_DOES}}": f"Structured process for {name} in domain {domain}",
        "{{OUTPUT_TARGET}}": f"branch-hub/findings/{name.upper()}-<slug>-<date>.md",
        "{{NOT_FOR}}": "Trivial one-off tasks. Use bash directly.",
        "{{MAIN_PROMPT_OR_COMMAND_FILE_REFERENCE}}": f"Load command: commands/{name}-main.md",
        "{{TASK_DESCRIPTION}}": f"Main task for {name}",
    }
    for k, v in substitutions.items():
        content = content.replace(k, v)

    # Write YAML
    out_path = LEARNING_ARCHON / ".archon" / "workflows" / f"{name}.yaml"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        ans = ask(f"\n  {out_path} existiert bereits. Ueberschreiben? (y/N)", "N")
        if ans.lower() != "y":
            print("Abgebrochen.")
            sys.exit(0)
    out_path.write_text(content, encoding="utf-8")
    print()
    print(f"[OK] Workflow geschrieben: {out_path}")

    # Mirror into branch-hub
    if BRANCH_HUB_MIRROR.exists():
        mirror_path = BRANCH_HUB_MIRROR / f"{name}.yaml"
        mirror_path.write_text(content, encoding="utf-8")
        print(f"[OK] Mirror in branch-hub: {mirror_path}")

    # Validate
    print()
    print("Phase 4: TEST - archon validate")
    try:
        result = subprocess.run(
            ["archon", "validate", "workflows", name],
            cwd=LEARNING_ARCHON,
            capture_output=True, text=True, timeout=60
        )
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        if result.returncode != 0:
            print("[WARN] Validation failed. See output above.", file=sys.stderr)
            print(result.stderr[-500:], file=sys.stderr)
    except FileNotFoundError:
        print("[WARN] archon CLI not found. Run manually:", file=sys.stderr)
        print(f"  cd {LEARNING_ARCHON} && archon validate workflows {name}", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("[WARN] archon validate timeout", file=sys.stderr)

    # Next-steps hint
    print()
    print("Phase 5: REFINE")
    print(f"  cd {LEARNING_ARCHON}")
    print(f"  git add .archon/workflows/{name}.yaml")
    print(f"  git commit -m 'Add workflow: {name} [CRUX-MK]'")
    print(f"  git push origin master")
    print()
    print(f"  Smoke-Test:")
    print(f"  archon workflow run {name} --branch test/smoke-{name} \"Test-Input\"")
    print()
    print("[CRUX-MK] Pentagon abgeschlossen.")


if __name__ == "__main__":
    main()
