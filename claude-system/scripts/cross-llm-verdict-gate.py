#!/usr/bin/env python3
"""
Cross-LLM-Verdict-Gate Pre-Write-Hook [CRUX-MK] v8

Prueft dass Canon-Dateien mit verdict: HARDENED (und meta-ebene: E3|E4|E5) echte Cross-LLM-Belegung haben,
nicht nur Single-Model-Simulation. v8 erweitert um PROVISIONAL-Tier (G3.4) + R4 Divergenz-Proxy-Check.

Hintergrund: rules/cross-llm-simulation.md + rules/meta-governance-framework.md G3.4 definieren Hierarchie:
  REJECTED < CONDITIONAL < PROVISIONAL < CROSS-LLM-SIMULATION-HARDENED < CROSS-LLM-2OF3-HARDENED < HARDENED < HARDENED-PRODUCTION < FIXPUNKT-HARDENED

PROVISIONAL (NEU v8): zwischen CONDITIONAL und SIM-HARDENED. Tritt auf wenn LLM-Konsens vorliegt
aber G3.2 Divergenz-Proxies (3 von 7) unvollstaendig. Max-Verdict fuer Cross-LLM ohne Proxy-Belegung.

M4-Regel: Single-Instance max CONDITIONAL. Simulation max CROSS-LLM-SIMULATION-HARDENED.
Echte HARDENED verlangt >= 3 unabhaengige Modelle. Auf E3+ zusaetzlich externe Ankerung (FIXPUNKT-1).

Author: Opus 4.7 METAOPS, 2026-04-18 (v1)
Hardened: Opus 4.7 METAD2, 2026-04-18 (v2 — Negation-Pre-Filter Mission-1a)
v8: Opus 4.7 METAD2 Continuation-3, 2026-04-19T15:10 (IL-10 PROVISIONAL-Tier + R4 Divergenz-Proxy-Check)

Changelog v2:
- strip_negation_clauses() entfernt Saetze/Klauseln mit Negations-Markern (ohne, kein\\w*, fehlt, ...)
  bevor has_external_anchor()/has_cross_llm_reference() den Pattern-Match laufen lassen.
  Behebt FP wo "HARDENED-PRODUCTION ohne Benchmark" als "mit Benchmark" gewertet wurde.
- Path-Patterns (cross-llm-URLs) bleiben robust gegen Negation (URL ist URL).
- Trade-off: doppelte Verneinung wird konservativ gedroppt (False-Negative-Bias akzeptiert).

Mission-1, Hook-4 von 4
Rules: cross-llm-simulation.md, meta-stack-fixpunkte.md FIXPUNKT-1

Scope (Pflicht):
- Claude-Vault/docs/decision-cards/
- branch-hub/findings/FINDING-
- branch-hub/cross-llm/

Check-Regeln:
R1: verdict: HARDENED + meta-ebene: E3|E4|E5 → MUSS Body-Link zu branch-hub/cross-llm/ haben
R2: verdict: HARDENED-PRODUCTION + alle Ebenen → MUSS Cross-LLM UND externen Benchmark nennen
R3: verdict: STATISTICAL-STABLE → WARN wenn keine externe Ankerung genannt
R4 (v8): verdict: CROSS-LLM-2OF3-HARDENED + meta-ebene E3|E4|E5 → MUSS >=3 von 7 G3.2-Divergenz-Proxies dokumentieren, sonst WARN-Downgrade-Empfehlung auf PROVISIONAL
R5 (v8): verdict: PROVISIONAL → OK (akzeptierte neue Tier-Stufe, keine Zusatz-Pflicht)

Exit-Codes:
    0 = OK
    1 = WARN (Downgrade empfohlen)
    2 = BLOCK (ENFORCE-mode)

Usage:
    python cross-llm-verdict-gate.py <file-path> [--content-stdin] [--mode=CHECK|ENFORCE|AUDIT]
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime
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

SCOPE_PATTERNS = [
    r"Claude-Vault[/\\]docs[/\\]decision-cards[/\\]",
    r"branch-hub[/\\]findings[/\\]FINDING-",
    r"branch-hub[/\\]cross-llm[/\\]",
]

CROSS_LLM_REFERENCE_PATTERNS = [
    r"branch-hub[/\\]cross-llm[/\\]",
    r"cross-llm[/\\]\d{4}-\d{2}-\d{2}",
    r"Cross-LLM[- ]Run",
    r"Codex[- ]GPT",
    r"Gemini[- ]2\.5",
]

EXTERNAL_ANCHOR_PATTERNS = [
    # v4 METAD2 (2026-04-18 Codex-Cross-LLM-Review): Wortgrenzen + Erweiterungen
    r"\bBenchmark\w*\b",                                # \b verhindert "Benchmark-Platzhalter" pseudo-match
    r"\bexternal[- ]?anchor\b",
    r"\bexterne[r]?\s+(Ankerung|Verankerung|Anker)\b",
    r"\bextern\s+validiert\b",
    r"\bpublished[- ]?(data|dataset)\b",
    r"\bpeer[- ]?review(ed)?\b",                        # peer-review ODER peer-reviewed
    r"\bproduction[- ]?metric\w*\b",                    # production-metric, production-metriken (mixed)
    r"\bProduktions[- ]?metrik\w*\b",                   # Deutsch
    r"\bProduction[- ]?Metrik\w*\b",                    # Mixed Title-Case
]

# v8 METAD2 IL-10 (2026-04-19): G3.2 Divergenz-Proxies (7 Stueck), min 3 fuer NICHT-PROVISIONAL.
# Quelle: ~/.claude/rules/meta-governance-framework.md G3.2 Cross-LLM-2OF3-HARDENED-Pflicht.
DIVERGENCE_PROXY_PATTERNS = [
    # P1: Fehlerkorrelation < 0.5 auf adversarialer Holdout-Batterie
    r"\bFehlerkorrelation\b",
    r"\berror\s+correlation\b",
    r"\bholdout[- ]?batterie\b",
    r"\badversarial\s+holdout\b",
    # P2: Lineage-Distanz (unterschiedliche Base-Family/Tokenizer/Provider)
    r"\bLineage[- ]?Distanz\b",
    r"\blineage\s+distance\b",
    r"\bunterschiedliche?\s+(Provider|Base[- ]?Family|Tokenizer)\b",
    r"\bdifferent\s+(provider|base[- ]?family|tokenizer)\b",
    r"\bCross[- ]?Provider\b",
    # P3: RLHF/Policy-Overlap-Analyse
    r"\bRLHF[- ]?Overlap\b",
    r"\bpolicy\s+overlap\b",
    r"\bPolicy[- ]?Overlap[- ]?Analyse\b",
    # P4: Rationale/Quellen-Overlap < 0.5
    r"\bRationale[- ]?Overlap\b",
    r"\bQuellen[- ]?Overlap\b",
    r"\brationale\s+overlap\b",
    r"\bsource\s+overlap\b",
    r"\bsemantische\s+Aehnlichkeit\b",
    # P5: Token-Prob-Dist-Variance > Schwelle
    r"\bToken[- ]?Prob[- ]?(Dist[- ]?)?Variance\b",
    r"\btoken\s+probability\s+(distribution\s+)?variance\b",
    # P6: Counter-Prompt-Invarianz-Test
    r"\bCounter[- ]?Prompt[- ]?Invarianz\b",
    r"\bcounter[- ]?prompt\s+invariance\b",
    # P7: Disjunkte Argumentations-Trajektorien
    r"\bdisjunkte?\s+Argumentations[- ]?Trajektorien?\b",
    r"\bdisjoint\s+argumentation\s+trajector(y|ies)\b",
    r"\bdivergent\s+reasoning\s+paths?\b",
]

# v2 (METAD2 Mission-1a Hook-4-FP-Fix 2026-04-18):
# Negation-Pre-Filter. Saetze die das Anchor/Cross-LLM-Konzept aktiv VERNEINEN
# duerfen nicht als positiver Match zaehlen.
# Pragmatischer Ansatz: drop ganzer Saetze mit Negation-Markers, dann Pattern-Match.
# Trade-off: doppelte Verneinungen ("Benchmark fehlt nicht") werden ebenfalls gedroppt ->
#   konservativer Bias (False-Negative besser als False-Positive bei Hardening-Hooks).
NEGATION_PATTERNS = [
    r"\bohne\b",
    r"\bkein\w*\b",          # kein, keine, keinen, keinem, keiner, keines
    r"\bnicht\b",
    r"\bfehlt\b",
    r"\bfehlen\b",
    r"\bfehlend\w*\b",       # fehlend, fehlende, fehlendem, ...
    r"\bno\b",
    r"\bnot\b",
    r"\bwithout\b",
    r"\bmissing\b",
    r"\bunavailable\b",
    r"\bnicht\s+verf\u00fcgbar\b",
    r"\bnicht\s+vorhanden\b",
    # v3 METAD2 Mission-1d M2 (2026-04-18): Wunsch-/TBD-/Komposition-Patterns
    r"\bw\u00fcnschenswert\b",
    r"\bwuenschenswert\b",
    r"\boffen\b",
    r"\bTBD\b",
    r"\bTODO\b",
    r"\bw\u00e4re\b",          # konditional
    r"\bwaere\b",
    r"\bw\u00fcrde\b",         # konditional
    r"\bwuerde\b",
    r"\bnoch\s+nicht\b",       # "noch nicht recherchiert"
    r"\bn\.A\.\b",             # nicht-anwendbar Abkuerzung
    r"\bn\.a\.\b",
    r"-frei\b",                # Komposition: "Benchmark-frei"
    r"-los\b",                 # Komposition: "Anchor-los"
    # v4 METAD2 (Codex-Cross-LLM-Review 2026-04-18):
    r"\bnie\b",
    r"\bniemals\b",
    r"\bweder\b",
    r"\bausstehend\w*\b",
    r"\bpending\b",
    r"\bfraglich\b",
    r"\bPlatzhalter\b",
    r"\bFehlanzeige\b",
    r"\b(unbekannt|unklar)\b",
    r"\bnot\s+yet\b",
    r"\bgeplant\b",                                        # "Benchmarking ist geplant"
    r"\bin\s+(Planung|Vorbereitung|Arbeit|Bearbeitung)\b",
    r"\bvorgesehen\b",
    r"\bin\s+Aussicht\b",
]

AUDIT_LOG = Path("G:/Meine Ablage/Claude-Knowledge-System/branch-hub/audit/cross-llm-verdict-gate.jsonl")


def is_in_scope(file_path: str) -> bool:
    norm = file_path.replace("\\", "/")
    for pattern in SCOPE_PATTERNS:
        if re.search(pattern, norm, re.IGNORECASE):
            return True
    return False


def extract_frontmatter(content: str) -> dict | None:
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 4)
    if end == -1:
        return None
    fm_text = content[4:end]
    fm = {}
    for line in fm_text.split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip().strip("\"'")
    return fm


def strip_negation_clauses(content: str) -> str:
    """Entferne Saetze und Komma-getrennte Klauseln die Negations-Marker enthalten.
    Pre-Filter fuer has_external_anchor() und has_cross_llm_reference().

    Heuristik: Splitten an Satz- und Komma-Grenzen. Wenn ein Fragment Negations-Marker
    hat -> drop (auch wenn doppelte Negation; konservativ).
    """
    fragments = re.split(r'(?<=[.!?\n])\s+|,\s+', content)
    kept = []
    for frag in fragments:
        if not frag.strip():
            continue
        is_negated = False
        for neg_p in NEGATION_PATTERNS:
            if re.search(neg_p, frag, re.IGNORECASE):
                is_negated = True
                break
        if not is_negated:
            kept.append(frag)
    return " ".join(kept)


def _fragments(content: str) -> list[str]:
    """Sentence/Klausel-Split fuer Anti-Laundering-Pruefung."""
    return [f for f in re.split(r'(?<=[.!?\n])\s+|,\s+', content) if f.strip()]


def _fragment_has_negation(frag: str) -> bool:
    return any(re.search(p, frag, re.IGNORECASE) for p in NEGATION_PATTERNS)


def _negation_in_window(frag: str, anchor_start: int, anchor_end: int, window_words: int = 3) -> bool:
    """v7 METAD2 (Codex-FN-Mitigation 2026-04-18):
    Negation in 3-Wort-Window VOR ODER NACH Anchor-Token.
    Verbessert ueber Whole-Fragment-Drop (v5/v6) bei Idiom-aehnlichen Faellen.
    """
    before = frag[:anchor_start]
    after = frag[anchor_end:]
    before_words = re.findall(r'\b\w+\b', before)[-window_words:]
    after_words = re.findall(r'\b\w+\b', after)[:window_words]
    near_text = " ".join(before_words + after_words)
    return any(re.search(p, near_text, re.IGNORECASE) for p in NEGATION_PATTERNS)


def _check_pattern_with_anti_laundering(content: str, patterns: list[str], min_words: int = 3) -> bool:
    """v7 METAD2 (Codex-FN-Mitigation): Window-Negation statt Whole-Fragment-Drop.

    Schutz-Schichten:
    1. Negation in 3-Wort-Window um Anchor-Token (v7 NLP-naehe Heuristik)
    2. Min_words im Fragment (Anti-Token-Laundering, v5 BIAS-027)
    3. Backwards-Scan nur bei kurzen Fragmenten (<4 Worte = Listing-Indiz)
    """
    fragments = _fragments(content)
    for i, frag in enumerate(fragments):
        # Iteriere alle Pattern-Hits (statt nur ersten Match-Test)
        any_hit = False
        for pattern in patterns:
            for m in re.finditer(pattern, frag, re.IGNORECASE):
                # v7: Window-Negations-Check direkt am Anchor
                if _negation_in_window(frag, m.start(), m.end()):
                    continue
                any_hit = True
                break
            if any_hit:
                break
        if not any_hit:
            continue
        # Min-Word-Count Check (Anti-Token-Laundering, v5)
        words = re.findall(r'\b\w+\b', frag)
        if len(words) < min_words:
            continue
        # Backwards-Scan nur bei sehr kurzen Fragmenten (<4 Worte = Listing-Indiz).
        # 4+ Worte = eigenstaendiger Satz, Sandwich-Faelle bleiben akzeptiert.
        if len(words) < 4 and i > 0 and _fragment_has_negation(fragments[i-1]):
            continue
        return True
    return False


def has_cross_llm_reference(content: str) -> bool:
    # Path-Patterns sind robust gegen Negation (URL ist URL) -> Sonder-Check
    for pattern in [r"branch-hub[/\\]cross-llm[/\\]", r"cross-llm[/\\]\d{4}-\d{2}-\d{2}"]:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    # Andere Patterns mit Anti-Laundering
    return _check_pattern_with_anti_laundering(content, CROSS_LLM_REFERENCE_PATTERNS, min_words=3)


def has_external_anchor(content: str) -> bool:
    return _check_pattern_with_anti_laundering(content, EXTERNAL_ANCHOR_PATTERNS, min_words=3)


def count_divergence_proxies(content: str) -> int:
    """v8 METAD2 IL-10: Zaehlt Anzahl der G3.2-Divergenz-Proxy-Pattern-Hits.
    Anti-Laundering wie has_external_anchor (negation-window + min_words).
    Returns: int 0-7 (max 7 verschiedene Proxies).
    """
    fragments = _fragments(content)
    hit_proxies = set()  # set of pattern indices um Doppel-Zaehlung zu vermeiden
    for i, frag in enumerate(fragments):
        words = re.findall(r'\b\w+\b', frag)
        if len(words) < 3:
            continue
        if len(words) < 4 and i > 0 and _fragment_has_negation(fragments[i-1]):
            continue
        for idx, pattern in enumerate(DIVERGENCE_PROXY_PATTERNS):
            if idx in hit_proxies:
                continue
            for m in re.finditer(pattern, frag, re.IGNORECASE):
                if not _negation_in_window(frag, m.start(), m.end()):
                    hit_proxies.add(idx)
                    break
    return len(hit_proxies)


def validate_verdict(fm: dict, content: str) -> tuple[str, str]:
    verdict = fm.get("verdict", "").upper().replace("-", "_")
    ebene = fm.get("meta-ebene", "").strip()
    has_cross = has_cross_llm_reference(content)
    has_anchor = has_external_anchor(content)

    if not verdict:
        return "OK", "kein Verdict gesetzt (kein Gate anwendbar)"

    if verdict == "HARDENED_PRODUCTION":
        if not has_cross:
            return "BLOCK", "HARDENED-PRODUCTION ohne Cross-LLM-Referenz — downgrade oder Cross-LLM-Run dokumentieren"
        if not has_anchor:
            return "WARN", "HARDENED-PRODUCTION ohne externen Benchmark/Anchor — Produktions-Stichprobe nennen"
        return "OK", "HARDENED-PRODUCTION mit Cross-LLM + Anchor"

    if verdict == "HARDENED":
        if ebene in {"E3", "E4", "E5"} and not has_cross:
            return "BLOCK", f"HARDENED auf {ebene} ohne Cross-LLM-Referenz — max CROSS-LLM-SIMULATION-HARDENED (rules/cross-llm-simulation.md M4)"
        if not has_cross:
            return "WARN", f"HARDENED ohne Cross-LLM-Referenz — pruefe Downgrade auf CROSS-LLM-SIMULATION-HARDENED"
        return "OK", "HARDENED mit Cross-LLM-Referenz"

    if verdict == "STATISTICAL_STABLE":
        if not has_anchor:
            return "WARN", "STATISTICAL-STABLE ohne externen Anchor — Koehler-Korrelations-Risiko, Anchor-Dokumentation empfohlen"
        return "OK", "STATISTICAL-STABLE mit Anchor"

    # v8 METAD2 IL-10: R4 Divergenz-Proxy-Pruefung fuer CROSS-LLM-2OF3-HARDENED auf E3+
    if verdict == "CROSS_LLM_2OF3_HARDENED":
        if ebene in {"E3", "E4", "E5"}:
            proxy_count = count_divergence_proxies(content)
            if proxy_count < 3:
                return "WARN", f"CROSS-LLM-2OF3-HARDENED auf {ebene} mit nur {proxy_count}/7 G3.2-Divergenz-Proxies — Downgrade-Empfehlung auf PROVISIONAL (G3.4)"
            return "OK", f"CROSS-LLM-2OF3-HARDENED mit {proxy_count}/7 G3.2-Divergenz-Proxies (ausreichend)"
        return "OK", "CROSS-LLM-2OF3-HARDENED auf E1/E2 — keine G3.2-Proxy-Pflicht"

    if verdict == "PROVISIONAL":
        return "OK", "PROVISIONAL — neue G3.4-Tier zwischen CONDITIONAL und SIM-HARDENED, akzeptiert"

    if verdict in {"CROSS_LLM_SIMULATION_HARDENED", "CONDITIONAL", "REJECTED", "FIXPUNKT_HARDENED"}:
        return "OK", f"Verdict {verdict} — keine zusaetzliche Gate-Pruefung"

    return "WARN", f"Unbekannter Verdict-Wert '{fm.get('verdict')}' — in rules/cross-llm-simulation.md Hierarchie erfassen"


def log_audit(entry: dict):
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        sys.stderr.write(f"[cross-llm-gate] Audit-Log failed: {e}\n")


def main():
    parser = argparse.ArgumentParser(description="Cross-LLM Verdict Gate [CRUX-MK]")
    parser.add_argument("file_path")
    parser.add_argument("--content-stdin", action="store_true")
    parser.add_argument("--mode", default="CHECK", choices=["CHECK", "ENFORCE", "AUDIT"])
    args = parser.parse_args()

    timestamp = datetime.now().isoformat()
    entry = {
        "ts": timestamp,
        "tool": "cross-llm-verdict-gate",
        "file": args.file_path,
        "mode": args.mode,
    }

    try:
        if not is_in_scope(args.file_path):
            entry["status"] = "OUT-OF-SCOPE"
            log_audit(entry)
            if args.mode != "AUDIT":
                print(f"[cross-llm-gate] OUT-OF-SCOPE: {args.file_path}")
            return 0

        if args.content_stdin:
            content = sys.stdin.read()
        elif os.path.exists(args.file_path):
            with open(args.file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        else:
            entry["status"] = "FILE_MISSING_PRE_WRITE"
            log_audit(entry)
            return 0

        fm = extract_frontmatter(content) or {}
        status, message = validate_verdict(fm, content)
        entry["status"] = status
        entry["message"] = message
        entry["verdict"] = fm.get("verdict", "")
        entry["meta_ebene"] = fm.get("meta-ebene", "")
        log_audit(entry)

        if status == "OK":
            if args.mode != "AUDIT":
                print(f"[cross-llm-gate] OK: {message}")
            return 0
        elif status == "WARN":
            sys.stderr.write(f"[cross-llm-gate] WARN {args.file_path}: {message}\n")
            return 1 if args.mode == "ENFORCE" else 0
        else:
            sys.stderr.write(f"[cross-llm-gate] BLOCK {args.file_path}: {message}\n")
            return 2 if args.mode == "ENFORCE" else 1

    except Exception as e:
        entry["status"] = "ERROR"
        entry["error"] = str(e)
        log_audit(entry)
        sys.stderr.write(f"[cross-llm-gate] ERROR: {e}\n")
        return 3


if __name__ == "__main__":
    sys.exit(main())
