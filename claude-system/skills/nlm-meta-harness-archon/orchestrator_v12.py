#!/usr/bin/env python3
"""
NLM-Meta-Harness-Archon Orchestrator v1.2 (2026-04-19)
Pure CLI-subprocess implementation — maximal robust, minimal code.

Alle NLM-Operationen via `python -m notebooklm <cmd>`. Kein async-Python.
Shannon-Messung via n-gram-Jaccard (local, zero-LLM).

Usage:
    python orchestrator_v12.py                          # alle Priority-Notebooks
    python orchestrator_v12.py --notebook NAME          # einzelnes Notebook
    python orchestrator_v12.py --domain business        # nur 1 Domain
    python orchestrator_v12.py --limit-reports 2        # nur N Berichte
    python orchestrator_v12.py --skip-reports           # nur Chat-Queries, keine Artefakte
    python orchestrator_v12.py --dry-run                # keine NLM-Calls, nur Plan ausgeben

Setup:
    # Einmalig:
    python login_workaround.py                          # Session speichern
"""

import argparse
import datetime
import hashlib
import json
import math
import re
import subprocess
import sys
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

SCRIPT_DIR = Path(__file__).parent
VAULT = Path("G:/Meine Ablage/Claude-Vault")
HUB = Path("G:/Meine Ablage/Claude-Knowledge-System/branch-hub")
FROM_NLM = VAULT / "resources" / "_from-nlm"
STATE_FILE = VAULT / "areas" / "family" / "instance-d2" / "nlm-archon-state.json"
AUDIT_LOG = HUB / "audit" / "action-log.jsonl"
PROMPTS_FILE = SCRIPT_DIR / "prompts.yaml"

PRIORITY_NOTEBOOKS = [
    "00_MASTER_CONTROL_TOWER",
    "Martin-Kemmer-Business-Plan-Master",
    "The Kemmer Index",  # substring-match
    "WISSEN-1",
    "Wisdom, Wealth",
]

# Pro Notebook: bis zu 8 Berichtstypen (CLI-Namen aus `notebooklm generate`)
REPORT_TYPES_CLI = [
    "report",           # Briefing Doc
    "mind-map",
    "audio",
    "slide-deck",
    "infographic",
    "quiz",
    "flashcards",
    # "video",          # lang-laufend, nur bei --all
    # "data-table",
]

# --- CLI-Wrapper ---

def run_nlm(*args, capture=True, timeout=120, check=False):
    """subprocess-wrapper fuer `python -m notebooklm <args>`. Returns (stdout, stderr, rc)."""
    cmd = [sys.executable, "-m", "notebooklm"] + list(args)
    try:
        result = subprocess.run(
            cmd, capture_output=capture, text=True,
            timeout=timeout, encoding="utf-8", errors="replace",
        )
        if check and result.returncode != 0:
            raise RuntimeError(f"{' '.join(cmd)} rc={result.returncode} stderr={result.stderr[:500]}")
        return result.stdout or "", result.stderr or "", result.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", 124

def list_notebooks() -> list[dict]:
    """Return list of {id, title} via `notebooklm list`."""
    out, err, rc = run_nlm("list", "--format", "json", timeout=30)
    if rc != 0:
        # Fallback: parse plain text output
        out, err, rc = run_nlm("list", timeout=30)
        if rc != 0:
            return []
        notebooks = []
        for line in out.splitlines():
            m = re.search(r"([a-f0-9-]{20,})\s+(.+)", line)
            if m:
                notebooks.append({"id": m.group(1), "title": m.group(2).strip()})
        return notebooks
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return []

def use_notebook(nb_id: str) -> bool:
    """Select a notebook as current context. Returns True on success."""
    _out, _err, rc = run_nlm("use", nb_id, timeout=20)
    return rc == 0

def ask_chat(question: str, timeout: int = 120) -> str:
    """Ask a question on the currently-selected notebook."""
    out, err, rc = run_nlm("ask", question, timeout=timeout)
    return out if rc == 0 else f"ERROR: {err[:300]}"

def generate_artifact(artifact_type: str) -> str | None:
    """Trigger artifact generation. Returns task/artifact id or None."""
    out, err, rc = run_nlm("generate", artifact_type, timeout=60)
    if rc != 0:
        return None
    # Try to extract artifact-id from output
    m = re.search(r"(artifact[_-]?id|task[_-]?id)[:=\s]+([a-zA-Z0-9_-]+)", out)
    return m.group(2) if m else out.strip()[:100]

def wait_artifact(artifact_id: str, timeout: int = 300) -> bool:
    """Wait for artifact generation to complete."""
    _out, _err, rc = run_nlm("artifact", "wait", artifact_id, timeout=timeout)
    return rc == 0

def download_artifact(artifact_type: str, out_path: Path) -> bool:
    """Download an artifact to a local path."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _out, _err, rc = run_nlm("download", artifact_type, "--out", str(out_path), timeout=180)
    return rc == 0 and out_path.exists()

# --- Shannon ---

def n_grams(text: str, n: int = 5) -> set:
    tokens = re.findall(r"\w+", text.lower())
    return {" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}

def shannon_bit(new_text: str, baseline_dir: Path) -> float:
    if not new_text or len(new_text) < 50:
        return 0.0
    new_grams = n_grams(new_text)
    max_overlap = 0.0
    if baseline_dir.exists():
        for f in baseline_dir.rglob("*.md"):
            try:
                b = n_grams(f.read_text(encoding="utf-8", errors="ignore"))
                if b:
                    overlap = len(new_grams & b) / len(new_grams | b)
                    max_overlap = max(max_overlap, overlap)
            except Exception:
                continue
    return min(-math.log2(max(max_overlap, 1e-6)), 20.0)

# --- Prompts ---

def load_prompts() -> dict:
    if not PROMPTS_FILE.exists():
        return {"domains": {}}
    try:
        import yaml
        return yaml.safe_load(PROMPTS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"domains": {}}

# --- Pipeline ---

def match_notebook(all_notebooks: list[dict], query: str) -> dict | None:
    for nb in all_notebooks:
        if nb["title"] == query:
            return nb
    for nb in all_notebooks:
        if query.lower() in nb["title"].lower():
            return nb
    return None

def process_notebook(nb: dict, prompts: dict, domains: list[str],
                     limit_reports: int | None, skip_reports: bool,
                     dry_run: bool) -> dict:
    today = datetime.date.today().isoformat()
    safe = re.sub(r"[^\w\-_]", "_", nb["title"])[:80]
    target_dir = FROM_NLM / today / safe
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n== {nb['title']} (id={nb['id']})")

    if dry_run:
        return {"notebook": nb["title"], "dry_run": True}

    # Use this notebook
    if not use_notebook(nb["id"]):
        return {"notebook": nb["title"], "error": "use failed"}

    results = {"notebook": nb["title"], "reports": {}, "chats": {}}

    # 1. Artifacts
    if not skip_reports:
        types = REPORT_TYPES_CLI[:limit_reports] if limit_reports else REPORT_TYPES_CLI
        for at in types:
            print(f"  generate {at}...", end=" ", flush=True)
            aid = generate_artifact(at)
            if not aid:
                print("FAIL")
                results["reports"][at] = "generate_failed"
                continue
            if wait_artifact(aid, timeout=300):
                out_path = target_dir / f"{at}.out"
                if download_artifact(at, out_path):
                    print(f"OK ({out_path.stat().st_size} B)")
                    results["reports"][at] = "ok"
                else:
                    print("download_fail")
                    results["reports"][at] = "download_failed"
            else:
                print("timeout/wait_fail")
                results["reports"][at] = "wait_failed"

    # 2. Chat-Permutations pro Domain
    for domain in domains:
        cfg = prompts.get("domains", {}).get(domain, {})
        stop_bit = cfg.get("stop_bit", 0.7)
        queries = cfg.get("queries", [])[:cfg.get("max_permutations", 5)]
        if not queries:
            continue
        domain_rows = []
        for idx, q in enumerate(queries):
            print(f"  chat/{domain}[{idx}]...", end=" ", flush=True)
            resp = ask_chat(q, timeout=120)
            bit = shannon_bit(resp, FROM_NLM)
            domain_rows.append({"idx": idx, "bit": round(bit, 2)})
            (target_dir / f"chat_{domain}_{idx}.md").write_text(
                f"# {q}\n\n{resp}\n\n---\nbit={bit:.2f}", encoding="utf-8"
            )
            print(f"bit={bit:.2f}")
            if bit < stop_bit:
                print(f"    saturation reached (< {stop_bit})")
                break
        results["chats"][domain] = domain_rows

    # 3. Audit log
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    avg_bit = 0.0
    all_bits = [r["bit"] for d in results["chats"].values() for r in d if "bit" in r]
    if all_bits:
        avg_bit = sum(all_bits) / len(all_bits)
    results["avg_bit"] = round(avg_bit, 2)

    entry = {
        "ts": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "branch": "DF-06-nlm-archon",
        "action": "NLM-SYNC",
        "target": str(target_dir).replace("\\", "/"),
        "reason": f"notebook={nb['title']}, reports={len(results['reports'])}, avg_bit={avg_bit:.2f}",
        "source": "nlm-meta-harness-archon v1.2",
    }
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return results

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--notebook", help="Notebook title (substring-match)")
    ap.add_argument("--domain", help="Single domain: business/ai/learning/wisdom")
    ap.add_argument("--limit-reports", type=int)
    ap.add_argument("--skip-reports", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    prompts = load_prompts()
    domains = [args.domain] if args.domain else ["business", "ai", "learning", "wisdom"]

    print("Fetching notebook list...")
    all_notebooks = list_notebooks()
    if not all_notebooks:
        print(json.dumps({"error": "list_notebooks failed - run login_workaround.py first"}))
        return
    print(f"Found {len(all_notebooks)} notebooks")

    if args.notebook:
        nb = match_notebook(all_notebooks, args.notebook)
        if not nb:
            print(json.dumps({"error": f"Notebook '{args.notebook}' not found",
                              "available": [n["title"] for n in all_notebooks[:10]]}))
            return
        targets = [nb]
    else:
        targets = [nb for p in PRIORITY_NOTEBOOKS for nb in all_notebooks
                   if p.lower() in nb["title"].lower()][:5]

    summary = []
    for nb in targets:
        try:
            summary.append(process_notebook(
                nb, prompts, domains, args.limit_reports, args.skip_reports, args.dry_run
            ))
        except KeyboardInterrupt:
            print("\n[interrupted]")
            break
        except Exception as exc:
            summary.append({"notebook": nb["title"], "error": f"{type(exc).__name__}: {exc}"})

    print("\n" + json.dumps({"summary": summary}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
