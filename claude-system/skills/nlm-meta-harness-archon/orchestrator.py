#!/usr/bin/env python3
"""
NLM-Meta-Harness-Archon Orchestrator v1.1.0 (2026-04-19 API-Fix fuer notebooklm-py 0.3.4)
Dark-Factory DF-06: NotebookLM -> Vault Sync + Shannon-Surprise-Messung
Nahezu zero Claude-Tokens.

Usage:
    python orchestrator.py                          # voller Run alle 5 Priority-Notebooks
    python orchestrator.py --notebook NAME          # einzelnes Notebook
    python orchestrator.py --domains business       # Komma-sep: business,ai,learning,wisdom
    python orchestrator.py --limit-reports 2        # nur N Berichtstypen (fuer Test)
    python orchestrator.py --dry-run                # keine Writes, nur Simulation

Setup (einmalig):
    pip install "notebooklm-py[browser]" sentence-transformers pyyaml
    python -m playwright install chromium           # PATH-fix: nutzt python -m
    python -m notebooklm login                      # Google-Auth Browser-Flow
"""

import argparse
import asyncio
import datetime
import hashlib
import json
import math
import re
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
    "The Kemmer Index: Systems, Variables, and Architectural Logic",
    "WISSEN-1-Bibliothek-Wargame-930",
    "Wisdom, Wealth, and Wonder: A Knowledge Compendium",
]

# Map friendly name -> API method (available in notebooklm-py 0.3.4)
REPORT_TYPES = {
    "briefing": "generate_report",           # Briefing Doc
    "study_guide": "generate_study_guide",
    "mind_map": "generate_mind_map",
    "audio": "generate_audio",
    "slide_deck": "generate_slide_deck",       # Presentation
    "infographic": "generate_infographic",
    "quiz": "generate_quiz",
    "flashcards": "generate_flashcards",
}

# --- State ---

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}

def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")

# --- Shannon Measurement (local, zero-LLM) ---

def n_grams(text: str, n: int = 5) -> set:
    tokens = re.findall(r"\w+", text.lower())
    return {" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}

def overlap_jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def shannon_measure(new_text: str, baseline_dir: Path) -> tuple[float, float]:
    """Bit-depth estimate: -log2(P(new|baseline)) via n-gram Jaccard."""
    if not new_text or len(new_text) < 50:
        return 0.0, 1.0
    new_grams = n_grams(new_text)
    max_overlap = 0.0
    if baseline_dir.exists():
        for f in baseline_dir.rglob("*.md"):
            try:
                baseline_grams = n_grams(f.read_text(encoding="utf-8", errors="ignore"))
                overlap = overlap_jaccard(new_grams, baseline_grams)
                max_overlap = max(max_overlap, overlap)
            except Exception:
                continue
    p = max(max_overlap, 1e-6)
    bit_depth = -math.log2(p)
    return min(bit_depth, 20.0), max_overlap

# --- Sync + Audit ---

def safe_name(name: str) -> str:
    return re.sub(r"[^\w\-_]", "_", name)[:80]

def write_output(target_dir: Path, name: str, content) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    if content is None:
        return
    if isinstance(content, bytes):
        (target_dir / f"{name}.bin").write_bytes(content)
    else:
        (target_dir / f"{name}.md").write_text(str(content), encoding="utf-8")

def audit_log(notebook_name: str, target_dir: Path, report_count: int, avg_bit: float) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "branch": "DF-06-nlm-archon",
        "action": "NLM-SYNC",
        "target": str(target_dir).replace("\\", "/"),
        "reason": f"notebook={notebook_name}, reports={report_count}, avg_shannon_bit={avg_bit:.2f}",
        "source": "nlm-meta-harness-archon v1.1.0",
    }
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

# --- Prompt Loader ---

def load_prompts() -> dict:
    if not PROMPTS_FILE.exists():
        return {"domains": {}}
    try:
        import yaml
        return yaml.safe_load(PROMPTS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"domains": {}}

# --- Main async pipeline ---

async def run_notebook(client, nb, prompts: dict, domains: list[str], limit_reports: int | None, dry_run: bool) -> dict:
    """Process one notebook: generate reports + drill domains."""
    print(f"[{nb.title}] starting")
    safe = safe_name(nb.title)
    today = datetime.date.today().isoformat()
    target_dir = FROM_NLM / today / safe
    outputs = {}

    # 1. Generate reports
    report_items = list(REPORT_TYPES.items())
    if limit_reports:
        report_items = report_items[:limit_reports]

    for friendly, method_name in report_items:
        try:
            method = getattr(client.artifacts, method_name)
            result = await method(nb.id)
            outputs[friendly] = result
            print(f"  [{friendly}] generated (task={getattr(result, 'task_id', '-')})")

            # Optional: wait_for_completion where available
            wait_method = getattr(client.artifacts, "wait_for_completion", None)
            task_id = getattr(result, "task_id", None)
            if wait_method and task_id and not dry_run:
                try:
                    await wait_method(nb.id, task_id, timeout=120.0)
                except Exception as exc_wait:
                    print(f"  [{friendly}] wait failed: {exc_wait}")
        except Exception as exc:
            outputs[friendly] = {"error": str(exc)}
            print(f"  [{friendly}] error: {exc}")

    if dry_run:
        return {"notebook": nb.title, "dry_run": True, "would_generate": list(outputs.keys())}

    # 2. Write outputs (summary/metadata only - actual artifact download is separate)
    for friendly, content in outputs.items():
        if isinstance(content, dict) and "error" in content:
            write_output(target_dir, friendly, f"ERROR: {content['error']}")
        else:
            write_output(target_dir, friendly, str(content))

    # 3. Domain-Permutation-Drill via chat
    domain_cfg = prompts.get("domains", {})
    drill_results = {}
    for domain in domains:
        cfg = domain_cfg.get(domain, {})
        stop_bit = cfg.get("stop_bit", 0.7)
        queries = cfg.get("queries", [])[:cfg.get("max_permutations", 5)]
        domain_summary = []
        for idx, query in enumerate(queries):
            try:
                result = await client.chat.ask(nb.id, query)
                response_text = str(result)
                bit, overlap = shannon_measure(response_text, FROM_NLM)
                domain_summary.append({
                    "idx": idx,
                    "query_head": query[:80],
                    "resp_len": len(response_text),
                    "bit": round(bit, 2),
                    "overlap": round(overlap, 3),
                })
                # Write the chat response
                chat_file = target_dir / f"chat_{domain}_{idx}.md"
                chat_file.write_text(
                    f"# {query}\n\n{response_text}\n\n---\n\nbit_depth={bit:.2f} overlap={overlap:.3f}",
                    encoding="utf-8",
                )
                if bit < stop_bit:
                    print(f"  [chat/{domain}] saturation at idx={idx} (bit={bit:.2f})")
                    break
            except Exception as exc:
                domain_summary.append({"idx": idx, "error": str(exc)})
                print(f"  [chat/{domain}] error: {exc}")
                break
        drill_results[domain] = domain_summary

    # 4. Audit log
    bits = [q.get("bit", 0.0) for d in drill_results.values() for q in d if "bit" in q]
    avg_bit = sum(bits) / len(bits) if bits else 0.0
    report_count = sum(1 for v in outputs.values() if not (isinstance(v, dict) and "error" in v))
    audit_log(nb.title, target_dir, report_count, avg_bit)

    return {
        "notebook": nb.title,
        "reports_ok": report_count,
        "avg_bit": round(avg_bit, 2),
        "drill": drill_results,
    }

async def run(args) -> dict:
    try:
        from notebooklm import NotebookLMClient
    except ImportError:
        return {"error": "notebooklm-py not installed. Run: pip install 'notebooklm-py[browser]'"}

    prompts = load_prompts()
    domains = args.domains.split(",") if args.domains else ["business", "ai", "learning", "wisdom"]

    try:
        # NOTE: from_storage() is a coroutine returning a client, THEN use async with
        client = await NotebookLMClient.from_storage()
        async with client:
            all_notebooks = await client.notebooks.list()

            # Target selection
            if args.notebook:
                targets = [nb for nb in all_notebooks if nb.title == args.notebook]
                if not targets:
                    return {"error": f"Notebook '{args.notebook}' not found. Available: {[nb.title for nb in all_notebooks[:10]]}"}
            else:
                state = load_state()
                drift = [nb for nb in all_notebooks
                         if nb.title in PRIORITY_NOTEBOOKS
                         and state.get(str(nb.id), {}).get("last_sync", "") < datetime.date.today().isoformat()]
                targets = drift if drift else [nb for nb in all_notebooks if nb.title in PRIORITY_NOTEBOOKS][:3]

            summary = []
            for nb in targets:
                res = await run_notebook(client, nb, prompts, domains, args.limit_reports, args.dry_run)
                summary.append(res)

            # Update state
            if not args.dry_run:
                state = load_state()
                for nb in all_notebooks:
                    state[str(nb.id)] = {
                        "title": nb.title,
                        "last_sync": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    }
                save_state(state)

            return {"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(), "summary": summary}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}

def main():
    parser = argparse.ArgumentParser(description="NLM-Meta-Harness-Archon Orchestrator v1.1")
    parser.add_argument("--notebook", help="Single notebook title")
    parser.add_argument("--domains", help="Comma-separated: business,ai,learning,wisdom")
    parser.add_argument("--limit-reports", type=int, help="Limit number of report types")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without writes")
    args = parser.parse_args()

    result = asyncio.run(run(args))
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

if __name__ == "__main__":
    main()
