#!/usr/bin/env python3
"""
NLM-Meta-Harness-Archon Orchestrator v2.0.0 (2026-04-19, Global-Max + Agil)

Aenderungen gegenueber v1.1:
- ALLE 5 Priority-Notebooks pro Run (parallel via asyncio.gather)
- Multi-LLM-Prompt-Crafting: Gemini + Codex (flat via Abos, ~50 Token/Call)
- 12-Themen-Katalog (rho-gewichtet, agil erweiterbar ueber state.json)
- 2 Cooldown-Ebenen: Ultra-Abo 24h (1 Run/Tag) + Per-Notebook-Saturation 8 Tage
- Auto-Rekrutierung: saturated Notebooks raus, neue aus 58 rein
- Theme-Priority rho-lebendig: shannon * rho_estimate * (1 + lambda_anchor)
- Claude-Tokens: nahezu 0 (nur Orchestrator-Python)

Usage:
    python orchestrator_v2.py                        # voller Run alle Priority-Notebooks parallel
    python orchestrator_v2.py --max-notebooks 3      # Limit
    python orchestrator_v2.py --theme coding         # erzwingt Tages-Thema
    python orchestrator_v2.py --dry-run              # keine Writes, nur Plan
    python orchestrator_v2.py --pilot NAME           # einzelnes Notebook voll durch
"""

import argparse
import asyncio
import datetime
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
PROMPTS_FILE = SCRIPT_DIR / "prompts_v2.yaml"

PRIORITY_NOTEBOOKS = [
    "00_MASTER_CONTROL_TOWER",
    "Martin-Kemmer-Business-Plan-Master",
    "The Kemmer Index: Systems, Variables, and Architectural Logic",
    "WISSEN-1-Bibliothek-Wargame-930",
    "Wisdom, Wealth, and Wonder: A Knowledge Compendium",
]

REPORT_TYPES = {
    "briefing":    "generate_report",
    "study_guide": "generate_study_guide",
    "mind_map":    "generate_mind_map",
    "audio":       "generate_audio",
    "slide_deck":  "generate_slide_deck",
    "infographic": "generate_infographic",
    "quiz":        "generate_quiz",
    "flashcards":  "generate_flashcards",
}

# Initial 12-Themen (rho-weighted, agil erweitert via weekly meta-loop)
INITIAL_THEMES = {
    "coding":                  {"rho": 0.85, "lambda": 5.0, "label": "Coding & Software-Architektur"},
    "ai_engineering":          {"rho": 0.95, "lambda": 5.0, "label": "KI & LLM-Engineering"},
    "documentation":           {"rho": 0.50, "lambda": 3.0, "label": "Dokumentation & Technical Writing"},
    "mathematics":             {"rho": 0.80, "lambda": 3.0, "label": "Mathematik, Formeln, Beweise"},
    "game_theory":             {"rho": 0.75, "lambda": 2.0, "label": "Spieltheorie & Strategische Interaktion"},
    "bwl_finance":             {"rho": 0.90, "lambda": 5.0, "label": "BWL & Finance"},
    "vwl_makro":               {"rho": 0.70, "lambda": 2.0, "label": "VWL & Makrooekonomie"},
    "knowledge_management":    {"rho": 0.80, "lambda": 5.0, "label": "Wissensmanagement & Lernen"},
    "meta_learning":           {"rho": 0.90, "lambda": 5.0, "label": "Meta-Lernen & Selbst-Lernen"},
    "biological_learning":     {"rho": 0.60, "lambda": 2.0, "label": "Biologisches Lernen & Neuroplastizitaet"},
    "civilizational_learning": {"rho": 0.70, "lambda": 2.0, "label": "Zivilisatorisches Lernen & Governance"},
    "autonomous_organizations":{"rho": 0.95, "lambda": 5.0, "label": "Dark Factories & Autonome Organisationen"},
}

# --- State ---

def load_state() -> dict:
    base = {"notebooks": {}, "themes": dict(INITIAL_THEMES), "runs": []}
    if STATE_FILE.exists():
        existing = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        # Merge: erhalte existing, aber ergaenze fehlende Keys
        for k, v in base.items():
            if k not in existing:
                existing[k] = v
        # Themes: merge initial mit existing (existing gewinnt)
        if "themes" in existing:
            merged_themes = dict(INITIAL_THEMES)
            merged_themes.update(existing["themes"])
            existing["themes"] = merged_themes
        return existing
    return base

def save_state(state: dict) -> None:
    """Atomic save: write to .tmp, then os.replace (POSIX+Windows atomic).
    Patch v2.1 (Gemini-Adversarial-Finding H1): Prevent state corruption on
    process crash or parallel runs. Previously a crash mid-write could leave
    empty/truncated state.json, bricking all future runs."""
    import os
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2, default=str, ensure_ascii=False), encoding="utf-8")
    os.replace(str(tmp), str(STATE_FILE))

# --- Shannon (zero-LLM) ---

def n_grams(text: str, n: int = 5) -> set:
    tokens = re.findall(r"\w+", text.lower())
    return {" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}

def shannon_bit(new_text: str, baseline_dir: Path) -> tuple[float, float]:
    if not new_text or len(new_text) < 50:
        return 0.0, 1.0
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
    return min(-math.log2(max(max_overlap, 1e-6)), 20.0), max_overlap


# --- IL-14 v2.2-M5 Semantic Shannon (Embedding-based, opt-in) ---
# Loest Gemini-Adversarial-Finding M5: n-gram misst nur lexikalische Neuheit.
# Paraphrasierter Content taeuscht hohes bit vor. Semantic-Embedding-Distanz erkennt das.

_EMBEDDING_MODEL = None  # Lazy-Init

def _get_embedding_model():
    """Lazy-load MiniLM-L6-v2 (80MB, schnell, mehrsprachig-kompatibel)."""
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            _EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
            print("[embedding] MiniLM-L6-v2 loaded")
        except Exception as exc:
            print(f"[embedding] Load failed: {type(exc).__name__}: {exc}")
            _EMBEDDING_MODEL = False  # Sentinel fuer Fehlschlag
    return _EMBEDDING_MODEL if _EMBEDDING_MODEL else None


def semantic_shannon_bit(new_text: str, baseline_dir: Path, max_baselines: int = 30) -> tuple[float, float]:
    """IL-14 v2.2-M5 Patch: Cosine-Similarity-basierte semantische Shannon-Bit-Messung.

    Ergaenzt n-gram Jaccard (lexikalisch) um semantische Distanz. Erkennt
    Paraphrasierung/Umformulierung korrekt als niedrig-bit (wo n-gram hohes bit
    durch andere Tokens sieht, obwohl der Inhalt identisch ist).

    Returns: (bit_depth, max_cosine_similarity). bit = -log2(1 - max_cos).
    Bei unavailable Model: return (0.0, 0.0) — Caller faellt auf shannon_bit zurueck.
    """
    if not new_text or len(new_text) < 50:
        return 0.0, 1.0
    model = _get_embedding_model()
    if model is None:
        return 0.0, 0.0

    try:
        import numpy as np
        new_emb = model.encode([new_text[:5000]], convert_to_numpy=True, show_progress_bar=False)[0]
        max_sim = 0.0

        if baseline_dir.exists():
            baselines = list(baseline_dir.rglob("*.md"))[:max_baselines]
            bl_texts = []
            for f in baselines:
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")[:5000]
                    if len(content) > 50:
                        bl_texts.append(content)
                except Exception:
                    continue

            if bl_texts:
                bl_embs = model.encode(bl_texts, convert_to_numpy=True, show_progress_bar=False)
                dots = np.dot(bl_embs, new_emb)
                norms_bl = np.linalg.norm(bl_embs, axis=1)
                norm_new = np.linalg.norm(new_emb)
                sims = dots / (norms_bl * norm_new + 1e-8)
                max_sim = float(sims.max())

        # bit = -log2(1 - cosine), weil hohe Similarity = niedrige Neuheit
        bit = min(-math.log2(max(1 - max_sim, 1e-6)), 20.0)
        return bit, max_sim
    except Exception as exc:
        print(f"[semantic-bit] error: {type(exc).__name__}: {exc}")
        return 0.0, 0.0


def combined_shannon_bit(new_text: str, baseline_dir: Path, use_semantic: bool = False) -> tuple[float, dict]:
    """Kombiniere lexikalisch + semantisch (wenn aktiviert): 0.4*lex + 0.6*sem.

    Returns: (combined_bit, metadata={lex_bit, lex_overlap, sem_bit, sem_sim}).
    """
    lex_bit, lex_overlap = shannon_bit(new_text, baseline_dir)
    meta = {"lex_bit": round(lex_bit, 2), "lex_overlap": round(lex_overlap, 3)}

    if not use_semantic:
        return lex_bit, meta

    sem_bit, sem_sim = semantic_shannon_bit(new_text, baseline_dir)
    meta["sem_bit"] = round(sem_bit, 2)
    meta["sem_sim"] = round(sem_sim, 3)

    if sem_bit > 0:  # Semantic verfuegbar
        combined = 0.4 * lex_bit + 0.6 * sem_bit
        meta["combined_formula"] = "0.4*lex + 0.6*sem"
        return combined, meta
    # Fallback auf lexikalisch
    return lex_bit, meta

# --- Rate-Limiting (IL-11 v2.2-H2 Patch 2026-04-19) ---
# Schutz gegen Burst-Exhaustion bei Multi-Notebook-Parallel + Gemini 5 RPM + Codex rate-limited.

import time as _time

class _RateLimiter:
    """Einfacher Token-Bucket: max N Calls pro 60s-Fenster, async-safe."""
    def __init__(self, calls_per_min: int, name: str = "llm"):
        self.interval = 60.0 / max(1, calls_per_min)
        self.name = name
        self.last = 0.0
        self.lock = asyncio.Lock()

    async def wait(self):
        async with self.lock:
            now = _time.monotonic()
            delta = now - self.last
            if delta < self.interval:
                sleep_s = self.interval - delta
                print(f"[rate-limit/{self.name}] throttle {sleep_s:.1f}s")
                await asyncio.sleep(sleep_s)
            self.last = _time.monotonic()

# Gemini Ultra laut META-ROADMAP: 5 Calls/min. Mit Sicherheits-Puffer: 4 RPM.
# Codex: rate-limited (unspezifiziert), konservativ 6 RPM.
_GEMINI_LIMITER = _RateLimiter(calls_per_min=4, name="gemini")
_CODEX_LIMITER = _RateLimiter(calls_per_min=6, name="codex")

# --- Multi-LLM Prompt-Crafting (flat via Abos, ~0 Claude-Tokens) ---

async def craft_prompt_gemini(notebook_title: str, report_type: str, theme_key: str, theme_label: str) -> str:
    """Gemini 2.5 Pro crafted NotebookLM-Prompt. ~50 Tokens pro Call, flat ueber Ultra-Abo.

    IL-11 v2.2-H2 Patch: Rate-Limit via _GEMINI_LIMITER (4 RPM sicher unter 5-RPM-Cap).
    """
    await _GEMINI_LIMITER.wait()
    sys_prompt = (
        f"Craft ONE compact NotebookLM prompt (max 150 words, German) for report type "
        f"'{report_type}' on notebook titled '{notebook_title}', emphasizing theme "
        f"'{theme_label}'. Martin Kemmer context: 9dots/HeyLou/Graphity/KPM, CRUX=max rho*L. "
        f"Output ONLY the prompt text, no explanation, no markdown."
    )
    try:
        proc = await asyncio.create_subprocess_exec(
            "gemini", "-p", sys_prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await asyncio.wait_for(proc.communicate(), timeout=45)
        text = out.decode("utf-8", errors="replace").strip()
        return text if text else _fallback_prompt(notebook_title, report_type, theme_label)
    except Exception as exc:
        return _fallback_prompt(notebook_title, report_type, theme_label)

async def craft_prompt_codex(notebook_title: str, report_type: str, theme_key: str, theme_label: str) -> str:
    """Codex GPT-5.4 crafted NotebookLM-Prompt. Flat via Abo.

    IL-11 v2.2-H2 Patch: Rate-Limit via _CODEX_LIMITER (6 RPM konservativ).
    """
    await _CODEX_LIMITER.wait()
    sys_prompt = (
        f"Craft ONE compact NotebookLM prompt (max 150 words, German) for report type "
        f"'{report_type}' on notebook '{notebook_title}', emphasizing theme '{theme_label}'. "
        f"Kemmer-Kontext: rho-optimierend, 9dots/HeyLou/KPM. Only the prompt, nothing else."
    )
    try:
        proc = await asyncio.create_subprocess_exec(
            "codex", "exec", "--skip-git-repo-check", sys_prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await asyncio.wait_for(proc.communicate(), timeout=60)
        text = out.decode("utf-8", errors="replace").strip()
        # Codex outputs extra formatting sometimes — take last paragraph
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if paragraphs:
            return paragraphs[-1]
        return _fallback_prompt(notebook_title, report_type, theme_label)
    except Exception:
        return _fallback_prompt(notebook_title, report_type, theme_label)

def _fallback_prompt(notebook_title: str, report_type: str, theme_label: str) -> str:
    return (
        f"Erstelle einen {report_type}-Bericht aus dem Notebook '{notebook_title}' mit "
        f"Fokus auf {theme_label}. Konkrete Zahlen, Kemmer-Kontext (9dots/HeyLou/KPM), "
        f"rho-Quantifizierung wo moeglich."
    )

async def craft_prompts_multi_llm(notebook_title: str, theme_key: str, theme_label: str, n_prompts: int = 10) -> list[str]:
    """
    Multi-LLM-Parallel Prompt-Crafting: Gemini + Codex je ~n/2 Prompts.
    Ergebnis: n unique NLM-Prompts, alle flat-LLM-generiert (~0 Claude-Tokens).
    """
    tasks = []
    report_list = list(REPORT_TYPES.keys())
    for i in range(n_prompts):
        rt = report_list[i % len(report_list)]
        if i % 2 == 0:
            tasks.append(craft_prompt_gemini(notebook_title, rt, theme_key, theme_label))
        else:
            tasks.append(craft_prompt_codex(notebook_title, rt, theme_key, theme_label))
    return await asyncio.gather(*tasks, return_exceptions=False)

# --- Gemini Heavy-Lifting (Shannon-Synthese, rho-Schaetzung, Meta-Audit) ---

async def gemini_synthesize_notebook(notebook_title: str, theme_label: str, chat_summaries: list[str], report_summaries: list[str]) -> str:
    """
    Post-Run Gemini-Synthese: fasst alle NLM-Outputs eines Notebooks zusammen,
    schaetzt rho-Impact (EUR/J), listet die 3 wichtigsten neuen Erkenntnisse.
    1 Call pro Notebook pro Tag. Gemini-Token flat. Claude-Token = 0.
    """
    joined_chats = "\n\n---\n\n".join(chat_summaries[:5])
    joined_reports = "\n\n---\n\n".join(report_summaries[:5])
    prompt = (
        f"Du bist Gemini als Analyse-Agent fuer Martin Kemmer (CRUX: max rho*L ueber T_life, "
        f"Entities: 9dots/HeyLou/Graphity/LexVance/KPM). Analysiere NotebookLM-Outputs zu "
        f"'{notebook_title}' mit Fokus-Thema '{theme_label}'. "
        f"\n\n=== Chat-Outputs (Auszug) ===\n{joined_chats[:3000]}"
        f"\n\n=== Report-Metadata ===\n{joined_reports[:2000]}"
        f"\n\nLiefere DEUTSCH in Markdown:"
        f"\n1. Die 3 wichtigsten NEUEN Erkenntnisse (nicht: was schon bekannt ist)"
        f"\n2. rho-Impact-Schaetzung in EUR/Jahr (min-max-Spanne, Begruendung)"
        f"\n3. Cross-References zu Kemmer-Doktrin (SAE/Trinity/HIVE/Myzel/CRUX)"
        f"\n4. Shannon-Bit-Schaetzung: wie hoch ist die semantische Neuheit (0-20)?"
        f"\n5. Child-Theme-Vorschlag: welches Sub-Thema waere als Folge-Audit sinnvoll?"
        f"\nKompakt, keine Einleitung, keine Floskeln."
    )
    try:
        proc = await asyncio.create_subprocess_exec(
            "gemini", "-p", prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await asyncio.wait_for(proc.communicate(), timeout=90)
        return out.decode("utf-8", errors="replace").strip()
    except Exception as exc:
        return f"# Gemini-Synthese-ERROR\n{type(exc).__name__}: {exc}"

async def gemini_extract_bit_and_rho(synthesis_text: str) -> tuple[float, tuple[float, float]]:
    """Parst Gemini-Synthese fuer bit-Schaetzung + rho-EUR-Spanne."""
    bit_match = re.search(r"(?:Shannon|Bit|semantisch)[^0-9]*(\d+(?:[.,]\d+)?)", synthesis_text, re.IGNORECASE)
    bit_gem = float(bit_match.group(1).replace(",", ".")) if bit_match else 0.0
    rho_match = re.search(r"(\d+[.,]?\d*)\s*[-–]\s*(\d+[.,]?\d*)\s*(?:k|K|Tsd|EUR|€|euro)", synthesis_text, re.IGNORECASE)
    if rho_match:
        low = float(rho_match.group(1).replace(",", "."))
        high = float(rho_match.group(2).replace(",", "."))
        # Skalieren: "50-100k" → 50000-100000
        if "k" in synthesis_text.lower()[rho_match.start():rho_match.end()].lower():
            low *= 1000
            high *= 1000
        return bit_gem, (low, high)
    return bit_gem, (0.0, 0.0)

# --- Notebook Selection (Agil, rho-gewichtet, cooldown-aware) ---

def select_active_notebooks(state: dict, all_priority: list[str], max_notebooks: int = 5) -> list[str]:
    """Gibt aktive Priority-Notebooks zurueck, rotiert saturated raus."""
    today = datetime.date.today().isoformat()
    active = []
    nbs_state = state.get("notebooks", {})
    for title in all_priority:
        nb = nbs_state.get(title, {})
        # Cooldown-Check (8-Tage per-Notebook)
        cooldown_until = nb.get("cooldown_until")
        if cooldown_until and cooldown_until > today:
            continue
        # Reactivate wenn Cooldown abgelaufen
        if nb.get("status") == "cooldown" and cooldown_until and cooldown_until <= today:
            nb["status"] = "active"
        # Skip wenn heute schon gelaufen (24h Ultra-Cooldown)
        if nb.get("last_run") == today:
            continue
        active.append(title)
        if len(active) >= max_notebooks:
            break
    return active

def pick_theme_of_day(themes_state: dict) -> tuple[str, str]:
    """rho-lebendig: theme_priority = rho * (1 + lambda_anchor/10). Top-1 wird Tages-Thema."""
    scored = []
    for key, cfg in themes_state.items():
        rho = cfg.get("rho", 0.5)
        lam = cfg.get("lambda", 1.0)
        hist = cfg.get("shannon_history", [])
        shannon_avg = (sum(hist) / len(hist)) if hist else 5.0  # unbekannt = mittel
        priority = shannon_avg * rho * (1 + lam / 10)
        scored.append((priority, key, cfg.get("label", key)))
    # Rotiere durch: pro Tag ein anderes Top-Thema (via day_of_year mod)
    scored.sort(reverse=True)
    doy = datetime.date.today().timetuple().tm_yday
    idx = doy % len(scored)
    return scored[idx][1], scored[idx][2]

# --- Run pipeline ---

def safe_name(name: str) -> str:
    """Strict allow-list + path-traversal defense.
    Patch v2.1 (Gemini-Adversarial-Finding L7): Notebook-Names koennten
    '../../../' enthalten (via Auto-Rekrutierung aus externer Quelle).
    Sanitize auf [a-zA-Z0-9_-] und Laenge-Cap 80."""
    cleaned = re.sub(r"[^a-zA-Z0-9_\-]", "_", name)[:80]
    # Extra defense: entferne alle Dots (kein ../ oder ./)
    cleaned = cleaned.replace(".", "_")
    return cleaned if cleaned else "unnamed"

def write_output(target_dir: Path, name: str, content) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    if content is None:
        return
    if isinstance(content, bytes):
        (target_dir / f"{name}.bin").write_bytes(content)
    else:
        (target_dir / f"{name}.md").write_text(str(content), encoding="utf-8")

async def run_notebook(client, nb, prompts: list[str], theme_key: str, theme_label: str, dry_run: bool, use_semantic: bool = False) -> dict:
    """1 Notebook, sequentiell 8 Reports + n Chat-Queries, Shannon-Messung."""
    print(f"[{nb.title}] START (theme={theme_key})")
    safe = safe_name(nb.title)
    today = datetime.date.today().isoformat()
    target_dir = FROM_NLM / today / safe

    results = {"notebook": nb.title, "theme": theme_key, "reports": {}, "chats": []}
    all_bits = []

    # 1. Sequentielle native reports
    for friendly, method_name in REPORT_TYPES.items():
        try:
            method = getattr(client.artifacts, method_name)
            result = await method(nb.id)
            results["reports"][friendly] = "ok"
            print(f"  [report/{friendly}] generated task={getattr(result, 'task_id', '-')}")
            if dry_run:
                continue
            write_output(target_dir, f"report_{friendly}", str(result))
            wait_method = getattr(client.artifacts, "wait_for_completion", None)
            tid = getattr(result, "task_id", None)
            if wait_method and tid:
                try:
                    await wait_method(nb.id, tid, timeout=120.0)
                except Exception:
                    pass
        except Exception as exc:
            results["reports"][friendly] = f"error: {str(exc)[:100]}"
            print(f"  [report/{friendly}] ERROR: {exc}")

    # 2. Chat-Queries mit Multi-LLM-crafted Prompts
    if dry_run:
        return results

    for idx, prompt in enumerate(prompts):
        try:
            resp = await client.chat.ask(nb.id, prompt)
            resp_text = str(resp)
            # IL-14 v2.2-M5: kombiniert lexikalisch + semantisch wenn use_semantic=True
            bit, meta = combined_shannon_bit(resp_text, FROM_NLM, use_semantic=use_semantic)
            overlap = meta.get("lex_overlap", 0.0)
            all_bits.append(bit)
            chat_file = target_dir / f"chat_{theme_key}_{idx}.md"
            bit_detail = f"bit={bit:.2f} lex={meta.get('lex_bit', 0):.2f} overlap={overlap:.3f}"
            if "sem_bit" in meta:
                bit_detail += f" sem={meta['sem_bit']:.2f} cos-sim={meta.get('sem_sim', 0):.3f}"
            chat_file.write_text(
                f"# {prompt[:120]}\n\n## Theme: {theme_label}\n\n{resp_text}\n\n---\n{bit_detail}",
                encoding="utf-8",
            )
            print(f"  [chat/{idx}] bit={bit:.2f} overlap={overlap:.3f}")
            results["chats"].append({"idx": idx, "bit": round(bit, 2), "overlap": round(overlap, 3), "prompt_head": prompt[:80]})
            # Early saturation bei sehr niedrig bit
            if bit < 0.3 and idx >= 2:
                print(f"  [chat/{idx}] early saturation, stop")
                break
        except Exception as exc:
            results["chats"].append({"idx": idx, "error": str(exc)[:100]})
            print(f"  [chat/{idx}] ERROR: {exc}")
            # Rate-limit-Abbruch: stop notebook
            if "quota" in str(exc).lower() or "rate" in str(exc).lower():
                results["quota_exceeded"] = True
                break

    results["avg_bit"] = round(sum(all_bits) / len(all_bits), 2) if all_bits else 0.0

    # 3. Gemini Heavy-Lifting: Post-Run Synthese pro Notebook (1 Call, flat Gemini-Token)
    chat_texts = []
    for f in sorted(target_dir.glob(f"chat_{theme_key}_*.md"))[:5]:
        try:
            chat_texts.append(f.read_text(encoding="utf-8", errors="ignore")[:600])
        except Exception:
            pass
    report_texts = [f"{k}={v}" for k, v in results["reports"].items()]
    synthesis = await gemini_synthesize_notebook(nb.title, theme_label, chat_texts, report_texts)
    (target_dir / "_SYNTHESIS.md").write_text(
        f"# Gemini-Synthese: {nb.title}\n\n## Theme: {theme_label}\n\n{synthesis}",
        encoding="utf-8",
    )
    gemini_bit, rho_range = await gemini_extract_bit_and_rho(synthesis)
    results["gemini_bit"] = gemini_bit
    results["gemini_rho_eur_year"] = list(rho_range)
    print(f"  [gemini-synthesis] bit={gemini_bit} rho={rho_range[0]:.0f}-{rho_range[1]:.0f} EUR/J")

    return results

def audit_log(results: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "branch": "DF-06-nlm-archon-v2",
        "action": "NLM-SYNC-V2",
        "notebook": results.get("notebook", "?"),
        "theme": results.get("theme", "?"),
        "reports_ok": sum(1 for v in results.get("reports", {}).values() if v == "ok"),
        "avg_bit": results.get("avg_bit", 0.0),
        "chats": len(results.get("chats", [])),
    }
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

def update_state_post_run(state: dict, results: list[dict], theme_key: str) -> None:
    today = datetime.date.today().isoformat()
    nbs = state.setdefault("notebooks", {})
    themes = state.setdefault("themes", {})
    bits_per_theme = []

    for res in results:
        title = res["notebook"]
        nb = nbs.setdefault(title, {})
        nb["last_run"] = today
        avg_bit = res.get("avg_bit", 0.0)
        hist = nb.setdefault("bit_history", [])
        hist.append(avg_bit)
        hist[:] = hist[-20:]  # keep last 20
        # Patch v2.1 (Gemini-Adversarial L6): Unterscheide Hard-Error vs Low-Quality
        # Silent-Failures (exceptions, quota_exceeded) NICHT als Saturation werten
        has_hard_error = (
            res.get("quota_exceeded", False)
            or not res.get("chats", [])  # keine Chats = Error
            or all(c.get("error") for c in res.get("chats", []))  # alle Chats fehlerhaft
        )
        if has_hard_error:
            nb["status"] = "error"
            nb["last_error"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            nb.pop("cooldown_until", None)
            print(f"[state] {title} HARD-ERROR (quota/network), kein Cooldown - retry morgen")
        elif avg_bit < 0.5:
            cooldown_until = (datetime.date.today() + datetime.timedelta(days=8)).isoformat()
            nb["status"] = "cooldown"
            nb["cooldown_until"] = cooldown_until
            print(f"[state] {title} SATURATED (bit={avg_bit}), cooldown until {cooldown_until}")
        else:
            nb["status"] = "active"
            nb.pop("cooldown_until", None)
        bits_per_theme.append(avg_bit)

    # Theme-History update
    theme = themes.setdefault(theme_key, {})
    theme_hist = theme.setdefault("shannon_history", [])
    if bits_per_theme:
        theme_hist.append(round(sum(bits_per_theme) / len(bits_per_theme), 2))
        theme_hist[:] = theme_hist[-20:]

    # Run-Log
    state.setdefault("runs", []).append({
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "theme": theme_key,
        "notebooks_run": len(results),
        "avg_bit": round(sum(bits_per_theme) / len(bits_per_theme), 2) if bits_per_theme else 0.0,
    })
    state["runs"] = state["runs"][-100:]  # keep last 100

async def run(args) -> dict:
    try:
        from notebooklm import NotebookLMClient
    except ImportError:
        return {"error": "notebooklm-py not installed"}

    state = load_state()
    theme_key, theme_label = (args.theme, state["themes"].get(args.theme, {}).get("label", args.theme)) \
        if args.theme else pick_theme_of_day(state["themes"])
    print(f"[theme-of-day] {theme_key} — {theme_label}")

    try:
        client = await NotebookLMClient.from_storage()
        async with client:
            # Patch v2.2 Auth-Health-Check (AKUT-Decision-Card 2026-04-19):
            # Pre-Flight-Check, verhindert Silent-Failure bei expired Session.
            try:
                all_notebooks = await client.notebooks.list()
            except Exception as auth_exc:
                msg = str(auth_exc).lower()
                if "auth" in msg or "signin" in msg or "expired" in msg:
                    # Write alert-file fuer Scheduled-Task-Monitoring
                    alert = VAULT / "areas" / "family" / "instance-d2" / "AUTH-EXPIRED.flag"
                    alert.parent.mkdir(parents=True, exist_ok=True)
                    alert.write_text(
                        f"DF-06 Auth expired at {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n"
                        f"Run: python {SCRIPT_DIR / 'login_workaround.py'}\n"
                        f"Error: {auth_exc}\n",
                        encoding="utf-8",
                    )
                    return {"error": "AUTH_EXPIRED", "fix": "login_workaround.py", "alert_file": str(alert)}
                raise
            by_title = {nb.title: nb for nb in all_notebooks}

            if args.pilot:
                candidates = [nb for nb in all_notebooks if args.pilot in nb.title]
                if not candidates:
                    return {"error": f"Pilot notebook '{args.pilot}' not found"}
                targets = [candidates[0]]
            else:
                active_titles = select_active_notebooks(state, PRIORITY_NOTEBOOKS, args.max_notebooks)
                targets = [by_title[t] for t in active_titles if t in by_title]
                # Auto-Rekrutierung wenn alle Priority saturated: pick aus 58
                if not targets and len(all_notebooks) > len(PRIORITY_NOTEBOOKS):
                    pool = [nb for nb in all_notebooks if nb.title not in state.get("notebooks", {})]
                    targets = pool[:args.max_notebooks]
                    print(f"[auto-recruit] Alle Priority saturated, rekrutiere {len(targets)} aus 58-Pool")

            if not targets:
                return {"msg": "Nichts zu tun — alle Notebooks heute schon gelaufen oder saturated"}

            # Multi-LLM Prompts parallel crafted (alle Targets teilen sich Theme-of-Day)
            print(f"[prompt-crafting] Multi-LLM fuer {len(targets)} Notebooks...")
            prompt_lists = await asyncio.gather(*[
                craft_prompts_multi_llm(nb.title, theme_key, theme_label, n_prompts=args.prompts_per_notebook)
                for nb in targets
            ])

            # Run notebooks parallel (limited concurrency fuer NLM-Rate-Limit)
            sem = asyncio.Semaphore(args.concurrency)

            async def run_one(nb, prompts):
                async with sem:
                    return await run_notebook(client, nb, prompts, theme_key, theme_label, args.dry_run, args.semantic_shannon)

            results = await asyncio.gather(*[run_one(nb, pr) for nb, pr in zip(targets, prompt_lists)])

            # Audit + State
            for r in results:
                audit_log(r)
            if not args.dry_run:
                update_state_post_run(state, results, theme_key)
                save_state(state)

            return {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "theme": theme_key,
                "notebooks_run": len(results),
                "summary": [{"nb": r["notebook"], "avg_bit": r.get("avg_bit", 0)} for r in results],
            }
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}

def main():
    parser = argparse.ArgumentParser(description="NLM-Meta-Harness-Archon Orchestrator v2.0")
    parser.add_argument("--theme", help="Force theme key (else auto from rho-weighted rotation)")
    parser.add_argument("--pilot", help="Pilot mode: single notebook by title substring")
    parser.add_argument("--max-notebooks", type=int, default=5)
    parser.add_argument("--concurrency", type=int, default=2, help="Parallel notebook runs")
    parser.add_argument("--prompts-per-notebook", type=int, default=10)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--semantic-shannon", action="store_true",
                        help="IL-14 v2.2-M5: Ergaenze n-gram Jaccard um Embedding-Cosine (MiniLM-L6-v2). "
                             "Erkennt Paraphrasierung korrekt. +~300MB RAM + ~2s/Chat Overhead.")
    args = parser.parse_args()

    result = asyncio.run(run(args))
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

if __name__ == "__main__":
    main()
