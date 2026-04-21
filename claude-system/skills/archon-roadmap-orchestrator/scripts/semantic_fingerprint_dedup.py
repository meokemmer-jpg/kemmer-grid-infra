#!/usr/bin/env python3
"""semantic_fingerprint_dedup.py - Jaccard-based Duplikat-Kandidaten-Suche."""
import sys, os, json, argparse, re

HUB = os.environ.get("BRANCH_HUB", "G:/Meine Ablage/Claude-Knowledge-System/branch-hub")
ROADMAP = os.path.join(HUB, "state", "roadmap-materialized.json")

STOPWORDS = {"der","die","das","ein","eine","the","a","an","and","or","for","mit","zum",
             "zur","von","ist","of","to","in","at","on","fuer","vom","bei","auf"}
SUFFIXES = ("ung", "ing", "en", "er", "s")

def tokenize(text):
    if not text: return set()
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = []
    for t in text.split():
        if t in STOPWORDS or len(t) < 2:
            continue
        for s in SUFFIXES:
            if t.endswith(s) and len(t) > len(s) + 2:
                t = t[:-len(s)]
                break
        tokens.append(t)
    return set(tokens)

def jaccard(a, b):
    if not a and not b: return 1.0
    u = a | b
    return len(a & b) / len(u) if u else 0.0

def action_for(sim):
    if sim >= 0.9: return "merge"
    if sim >= 0.7: return "review"
    return "ignore"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--threshold", type=float, default=0.7)
    p.add_argument("--compare")
    p.add_argument("--against")
    args = p.parse_args()

    if args.compare and args.against:
        s1, s2 = tokenize(args.compare), tokenize(args.against)
        sim = jaccard(s1, s2)
        print(json.dumps({"similarity": round(sim, 3), "recommend_action": action_for(sim)},
                         ensure_ascii=False))
        return

    try:
        with open(ROADMAP, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(json.dumps({"error": f"roadmap-read: {e}"}))
        return

    tasks = data.get("tasks", {})
    tids = list(tasks.keys())
    tok = {tid: tokenize(tasks[tid].get("title", "")) for tid in tids}

    pairs = []
    for i in range(len(tids)):
        for j in range(i+1, len(tids)):
            a, b = tids[i], tids[j]
            sim = jaccard(tok[a], tok[b])
            if sim >= args.threshold:
                pairs.append({"task_a": a, "task_b": b,
                              "similarity": round(sim, 3),
                              "recommend_action": action_for(sim)})

    print(json.dumps({"pairs": pairs}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
