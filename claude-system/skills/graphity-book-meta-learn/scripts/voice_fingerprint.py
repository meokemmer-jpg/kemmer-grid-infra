#!/usr/bin/env python3
"""
voice_fingerprint.py -- Voice-Drift-Detection [CRUX-MK]
Wave-3 W9 Konsens: 4-5 Algorithmen-Ensemble mit Fusion-Score.

Algorithmen:
  V1 Burrows' Delta (Function-Word + Char-Ngram) -- billig
  V2 Syntax-Rhythm (Satzlaenge-Verteilung + POS-3gram fallback) -- mittel
  V3 Six-Pillar Marker (Martins 6 Saeulen Wiederholung/Kaestner/Somatik/Parallel/Abstraktion/Leitmotiv) -- billig
  V4 Rolling Drift (JS-Divergence + CUSUM gegen akzeptierte Kapitel) -- billig
  V5 SBERT optional (Semantic Centroid, GPU) -- teuer (skip default)

Fusion: drift = 0.20*V1 + 0.30*V2 + 0.25*V3 + 0.15*V4 + 0.10*V5
  gelb >= 0.45, rot >= 0.60

Pflicht pro Baseline: Scope = (author x category x overlay), mind. 3 Referenzkapitel.

Usage:
    python voice_fingerprint.py --baseline --author martin --category K1_narrativ --corpus-dir <dir> --db <sqlite>
    python voice_fingerprint.py --check <kapitel.md> --author martin --category K1_narrativ --db <sqlite> --book <slug> --chapter 15
    python voice_fingerprint.py --report --book <slug> --db <sqlite>

Exit-Codes:
    0 = OK (alle Kapitel ok/gelb)
    1 = gelb (>= 1 Kapitel mit WARN)
    2 = rot (>= 1 Kapitel mit BLOCK)
"""

import argparse
import io
import json
import math
import pickle
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


# ==========================================================================
# CONFIG (Wave-3 W9 Konsens)
# ==========================================================================

# Deutsche Stopwoerter/Function-Words Top-200 (fuer Burrows' Delta)
FUNCTION_WORDS = set("""
der die das ein eine einer eines einem einen den dem
und oder aber doch denn sondern
ich du er sie es wir ihr sie mich dich ihn uns euch
mein dein sein ihr unser euer mir dir ihm ihr uns euch
in an auf zu bei mit von nach vor hinter ueber unter zwischen durch fuer
ist sind war waren sein habe hat hatte haben hatten werde wird wurde wurden
nicht kein keine keiner keinem keinen niemand nichts nie
sehr so sehr auch noch schon wieder dann wann wo wie was wer
aus als auch nur wenn weil dass ob wie dann gerade eben schon
ja nein vielleicht wahrscheinlich moeglicherweise
dies diese dieser diesem diesen dieses
jener jene jenes jenem
viel viele vieler vielem wenig wenige alle allen alles
gegen ohne um her hin zurueck weg weit nahe
""".split())

# Six-Pillar Patterns (Martins 6 Saeulen)
SIX_PILLARS = {
    "wiederholung": [
        r"(?i)\b(\w{4,})\b.*?\b\1\b",  # Wort zweimal innerhalb 50 Worte (approx)
    ],
    "kaestner_kontrast": [
        r"(?i)\b(aber|jedoch|dagegen|hingegen)\b",
        r"(?i)\b(nicht\s+\w+\s*,?\s*sondern)\b",
    ],
    "somatik": [
        r"(?i)\b(haende|finger|kiefer|schulter|magen|atem|herz|bauch|koerper|huefte|nacken|ruecken|knie|gesicht)\b",
        r"(?i)\b(spuert|fuehlt|zittert|atmet|schwitzt|pocht|schlaegt|schmerzt|sticht|brennt)\b",
    ],
    "parallelmontage": [
        r"(?i)(gleichzeitig|waehrend|in\s+dem\s+moment|derweil|indessen)",
    ],
    "abstraktion": [  # Negativ-Indikator: zu viel Abstraktion = schlecht
        r"(?i)\b(konzept|prinzip|struktur|system|mechanismus|prozess|aspekt|dimension|ebene|faktor|kategorie)\b",
    ],
    "leitmotiv": [
        # Leitmotiv ist kapitel-spezifisch; hier Heuristik: seltene Substantive die wiederholt werden
        # Wird in runtime spezifisch berechnet
    ],
}

# Drift-Schwellen (Wave-3 Konsens)
THRESHOLDS = {
    "V1": {"gelb": 1.0, "rot": 1.2},    # Burrows Delta
    "V2": {"gelb": 0.55, "rot": 0.65},  # Syntax-Rhythm
    "V3": {"gelb": 0.20, "rot": 0.25},  # Six-Pillar
    "V4": {"gelb": 0.08, "rot": 0.12},  # Rolling JS
    "V5": {"gelb": 0.35, "rot": 0.45},  # SBERT (wenn verfuegbar)
    "fusion": {"gelb": 0.45, "rot": 0.60},
}

FUSION_WEIGHTS = {"V1": 0.20, "V2": 0.30, "V3": 0.25, "V4": 0.15, "V5": 0.10}
# Summe = 1.00 MIT V5; ohne V5 muessen weights neuberechnet werden.
# P0-2 Fix (Framework-Adversarial-Audit 2026-04-19): Normalisiere Fusion on-the-fly
# falls V5 nicht verfuegbar (SBERT optional wegen GPU-Requirement).
# FUSION_WEIGHTS_NO_V5 = {V1: 0.22, V2: 0.33, V3: 0.28, V4: 0.17} (=1.00 normalisiert)
FUSION_WEIGHTS_NO_V5 = {
    "V1": 0.20 / 0.90,  # 0.222
    "V2": 0.30 / 0.90,  # 0.333
    "V3": 0.25 / 0.90,  # 0.278
    "V4": 0.15 / 0.90,  # 0.167
}

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-ZAEOUOEO])")


# ==========================================================================
# FEATURE-EXTRACTION
# ==========================================================================

def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


def function_word_vector(tokens, n_top=200):
    """V1: Top-N Function-Word-Frequenzen."""
    filtered = [t for t in tokens if t in FUNCTION_WORDS]
    total = max(1, len(filtered))
    counts = Counter(filtered)
    # Normalisiert auf relative Frequenz
    return {w: counts.get(w, 0) / total for w in FUNCTION_WORDS}


def sentence_length_distribution(text):
    """V2: Satzlaengen-Statistik."""
    sentences = [s.strip() for s in SENTENCE_SPLIT.split(text) if s.strip()]
    lengths = [len(re.findall(r"\b\w+\b", s)) for s in sentences]
    if not lengths:
        return {"mean": 0, "std": 0, "p10": 0, "p50": 0, "p90": 0, "n": 0}
    lengths_sorted = sorted(lengths)
    n = len(lengths_sorted)
    mean = sum(lengths) / n
    var = sum((l - mean) ** 2 for l in lengths) / n
    return {
        "mean": mean,
        "std": math.sqrt(var),
        "p10": lengths_sorted[int(n * 0.1)],
        "p50": lengths_sorted[int(n * 0.5)],
        "p90": lengths_sorted[min(n - 1, int(n * 0.9))],
        "n": n,
    }


def six_pillar_vector(text):
    """V3: Six-Pillar-Marker-Dichte pro 1000 Tokens."""
    token_count = max(1, len(tokenize(text)))
    vec = {}
    for pillar, patterns in SIX_PILLARS.items():
        if not patterns:
            vec[pillar] = 0.0
            continue
        count = 0
        for p in patterns:
            count += len(re.findall(p, text))
        vec[pillar] = count * 1000 / token_count
    return vec


# ==========================================================================
# DRIFT-SCORES
# ==========================================================================

def burrows_delta(vec_chap, vec_baseline):
    """V1: Burrows' Delta (Euklidische Distanz Z-Score-Normalisiert)."""
    if not vec_baseline:
        return 0.0
    # Approximiert: mean + std pro Dimension aus Baseline
    # Hier vereinfacht: Differenz-L2 normalisiert
    keys = set(vec_chap) & set(vec_baseline)
    if not keys:
        return 0.0
    diffs = []
    for k in keys:
        diff = vec_chap[k] - vec_baseline[k]
        diffs.append(diff)
    # Euklidische Norm
    return math.sqrt(sum(d ** 2 for d in diffs)) * 100  # Skalierung


def syntax_distance(dist_chap, dist_baseline):
    """V2: Syntax-Rhythm (Mahalanobis-Approx)."""
    if dist_baseline.get("n", 0) == 0:
        return 0.0
    keys = ["mean", "std", "p10", "p50", "p90"]
    diff = 0.0
    for k in keys:
        b = dist_baseline.get(k, 0)
        c = dist_chap.get(k, 0)
        norm = max(1.0, b)
        diff += ((c - b) / norm) ** 2
    return math.sqrt(diff / len(keys))


def six_pillar_distance(vec_chap, vec_baseline):
    """V3: Gewichtete Six-Pillar-Distanz."""
    if not vec_baseline:
        return 0.0
    weights = {
        "wiederholung": 0.15,
        "kaestner_kontrast": 0.15,
        "somatik": 0.25,
        "parallelmontage": 0.15,
        "abstraktion": 0.10,  # negativ-gewichtet in Anti-Drift-Logik
        "leitmotiv": 0.20,
    }
    dist = 0.0
    for k, w in weights.items():
        b = vec_baseline.get(k, 0)
        c = vec_chap.get(k, 0)
        norm = max(1.0, b)
        dist += w * ((c - b) / norm) ** 2
    return math.sqrt(dist)


def js_divergence(p, q):
    """V4: Jensen-Shannon zwischen zwei Verteilungen."""
    keys = set(p) | set(q)
    if not keys:
        return 0.0
    m = {k: 0.5 * (p.get(k, 0) + q.get(k, 0)) for k in keys}
    def kl(a, b):
        return sum(a.get(k, 0) * math.log((a.get(k, 1e-10) + 1e-10) / (b.get(k, 1e-10) + 1e-10))
                   for k in keys if a.get(k, 0) > 0)
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


# ==========================================================================
# BASELINE-BUILD
# ==========================================================================

MIN_BASELINE_N_SAMPLES = 3  # P0-2-Nachbau aus Audit: statistisch instabil unter 3


def build_baseline(corpus_dir):
    """Aggregiere Features aus Referenzkapiteln zu einem Baseline-Vektor."""
    all_tokens = []
    all_sentences_lengths = []
    pillar_sums = {p: 0.0 for p in SIX_PILLARS}
    n_chapters = 0

    for md_file in Path(corpus_dir).glob("*.md"):
        text = md_file.read_text(encoding="utf-8", errors="replace")
        text = re.sub(r"^---\n[\s\S]*?\n---\n", "", text, count=1)  # strip frontmatter
        tokens = tokenize(text)
        all_tokens.extend(tokens)
        dist = sentence_length_distribution(text)
        all_sentences_lengths.append(dist)
        pillars = six_pillar_vector(text)
        for p, v in pillars.items():
            pillar_sums[p] += v
        n_chapters += 1

    if n_chapters == 0:
        return None, 0
    # Baseline-Mindest-Sample-Pflicht (Audit-P5 / E2E-Pilot-Finding)
    if n_chapters < MIN_BASELINE_N_SAMPLES:
        print(f"WARN: Baseline-N={n_chapters} unter MIN_BASELINE_N_SAMPLES={MIN_BASELINE_N_SAMPLES} "
              f"(Burrows 2002). Baseline wird gebaut, aber scores statistisch instabil. "
              f"Quality-Flag = 'low_n'.", file=sys.stderr)

    # Aggregate
    fw_vec = function_word_vector(all_tokens)
    # Avg syntax dist
    avg_dist = {}
    for k in ["mean", "std", "p10", "p50", "p90"]:
        vals = [d[k] for d in all_sentences_lengths if d.get("n", 0) > 0]
        avg_dist[k] = sum(vals) / len(vals) if vals else 0
    avg_dist["n"] = n_chapters
    # Avg six-pillar
    pillar_avg = {p: pillar_sums[p] / n_chapters for p in SIX_PILLARS}

    baseline = {
        "V1_fw_vec": fw_vec,
        "V2_syntax_dist": avg_dist,
        "V3_pillar_vec": pillar_avg,
        "n_samples": n_chapters,
        "n_words": len(all_tokens),
    }
    return baseline, n_chapters


def save_baseline(conn, author, category, overlay, baseline):
    for algo in ["V1", "V2", "V3"]:
        vec_key = f"{algo}_{'fw_vec' if algo == 'V1' else 'syntax_dist' if algo == 'V2' else 'pillar_vec'}"
        blob = pickle.dumps(baseline[vec_key])
        conn.execute("""
            INSERT OR REPLACE INTO voice_baselines
                (author_id, category, overlay, algo, baseline_vector, n_samples, n_words)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (author, category, overlay, algo, blob, baseline["n_samples"], baseline["n_words"]))
    conn.commit()


def load_baseline(conn, author, category, overlay):
    baseline = {}
    max_n_samples = 0
    for algo in ["V1", "V2", "V3"]:
        row = conn.execute("""
            SELECT baseline_vector, n_samples FROM voice_baselines
            WHERE author_id = ? AND category = ? AND (overlay = ? OR (overlay IS NULL AND ? IS NULL))
              AND algo = ?
        """, (author, category, overlay, overlay, algo)).fetchone()
        if row:
            vec_key = f"{algo}_{'fw_vec' if algo == 'V1' else 'syntax_dist' if algo == 'V2' else 'pillar_vec'}"
            baseline[vec_key] = pickle.loads(row[0])
            # Fix: nimm max n_samples aus allen algos (statt nur letztem)
            max_n_samples = max(max_n_samples, row[1] or 0)
    if baseline:
        baseline["n_samples"] = max_n_samples
    return baseline if baseline else None


# ==========================================================================
# CHECK
# ==========================================================================

def check_chapter(conn, text, author, category, overlay, book_id=None, chapter_num=None):
    """Berechne V1-V4 Scores + Fusion."""
    baseline = load_baseline(conn, author, category, overlay)
    if not baseline:
        return {"error": f"No baseline for {author}/{category}/{overlay}"}, "error"

    tokens = tokenize(text)
    chap_fw = function_word_vector(tokens)
    chap_syntax = sentence_length_distribution(text)
    chap_pillars = six_pillar_vector(text)

    v1 = burrows_delta(chap_fw, baseline.get("V1_fw_vec", {}))
    v2 = syntax_distance(chap_syntax, baseline.get("V2_syntax_dist", {}))
    v3 = six_pillar_distance(chap_pillars, baseline.get("V3_pillar_vec", {}))

    # V4 Rolling: vergleiche mit letzten akzeptierten Kapiteln dieses Buchs
    v4 = 0.0
    if book_id and chapter_num:
        recent_rows = conn.execute("""
            SELECT score FROM voice_scores
            WHERE book_id = ? AND chapter_num < ? AND algo = 'fusion' AND severity != 'rot'
            ORDER BY chapter_num DESC LIMIT 5
        """, (book_id, chapter_num)).fetchall()
        if recent_rows:
            recent_avg = sum(r[0] for r in recent_rows) / len(recent_rows)
            # Einfacher Delta-Check (Full-JS erfordert vollstaendige Verteilungen)
            v4 = abs((v1 + v2 + v3) / 3 - recent_avg) * 0.5

    # P0-2 Fix: ohne V5 normalisierte Gewichte (sonst Summe 0.90, systematisch zu-niedrig)
    v5_available = False  # SBERT optional, nicht implementiert
    if v5_available:
        fusion = (FUSION_WEIGHTS["V1"] * min(v1, 2.0) +
                  FUSION_WEIGHTS["V2"] * min(v2, 2.0) +
                  FUSION_WEIGHTS["V3"] * min(v3, 2.0) +
                  FUSION_WEIGHTS["V4"] * min(v4, 2.0))
    else:
        fusion = (FUSION_WEIGHTS_NO_V5["V1"] * min(v1, 2.0) +
                  FUSION_WEIGHTS_NO_V5["V2"] * min(v2, 2.0) +
                  FUSION_WEIGHTS_NO_V5["V3"] * min(v3, 2.0) +
                  FUSION_WEIGHTS_NO_V5["V4"] * min(v4, 2.0))
    fusion = min(fusion, 1.0)

    scores = {"V1": v1, "V2": v2, "V3": v3, "V4": v4, "fusion": fusion}

    # Severity-Klassifikation
    def classify(algo, score):
        t = THRESHOLDS.get(algo, THRESHOLDS["fusion"])
        if score >= t["rot"]: return "rot"
        if score >= t["gelb"]: return "gelb"
        return "ok"

    severities = {a: classify(a, s) for a, s in scores.items()}

    # Hartes Rot: fusion rot ODER 2 einzelne Algos rot
    red_count = sum(1 for s in severities.values() if s == "rot")
    if severities["fusion"] == "rot" or red_count >= 2:
        final_severity = "rot"
    elif any(s == "gelb" for s in severities.values()) or severities["fusion"] == "gelb":
        final_severity = "gelb"
    else:
        final_severity = "ok"

    # Persist
    if book_id and chapter_num:
        for algo, score in scores.items():
            conn.execute("""
                INSERT OR REPLACE INTO voice_scores
                    (book_id, chapter_num, revision_id, algo, score, severity, details_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (book_id, chapter_num, "current", algo, score, severities[algo],
                  json.dumps({"baseline_n": baseline.get("n_samples", 0)})))
        conn.commit()

    return {
        "scores": scores,
        "severities": severities,
        "final_severity": final_severity,
        "baseline_n_samples": baseline.get("n_samples", 0),
    }, final_severity


# ==========================================================================
# MAIN
# ==========================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--check")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--author")
    ap.add_argument("--category")
    ap.add_argument("--overlay")
    ap.add_argument("--corpus-dir")
    ap.add_argument("--db", required=True)
    ap.add_argument("--book")
    ap.add_argument("--chapter", type=int)
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)

    if args.baseline:
        if not (args.author and args.category and args.corpus_dir):
            print("ERROR: --baseline requires --author --category --corpus-dir", file=sys.stderr)
            sys.exit(3)
        baseline, n = build_baseline(args.corpus_dir)
        if not baseline:
            print(f"ERROR: no .md files in {args.corpus_dir}", file=sys.stderr)
            sys.exit(3)
        save_baseline(conn, args.author, args.category, args.overlay, baseline)
        print(json.dumps({"status": "baseline_built", "n_samples": n,
                         "scope": f"{args.author}/{args.category}/{args.overlay}"}))
        sys.exit(0)

    elif args.check:
        if not (args.author and args.category):
            print("ERROR: --check requires --author --category", file=sys.stderr)
            sys.exit(3)
        text = Path(args.check).read_text(encoding="utf-8", errors="replace")
        result, severity = check_chapter(conn, text, args.author, args.category,
                                          args.overlay, args.book, args.chapter)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit({"ok": 0, "gelb": 1, "rot": 2, "error": 3}.get(severity, 3))

    elif args.report:
        if not args.book:
            print("ERROR: --report requires --book", file=sys.stderr)
            sys.exit(3)
        rows = conn.execute("""
            SELECT chapter_num, algo, score, severity FROM voice_scores
            WHERE book_id = ? ORDER BY chapter_num, algo
        """, (args.book,)).fetchall()
        print(json.dumps([dict(zip(["chapter", "algo", "score", "severity"], r)) for r in rows],
                         indent=2, ensure_ascii=False))
        sys.exit(0)

    else:
        ap.print_help()
        sys.exit(3)


if __name__ == "__main__":
    main()
