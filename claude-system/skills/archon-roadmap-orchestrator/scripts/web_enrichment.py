#!/usr/bin/env python3
"""
web_enrichment.py - Browser-LLM-Worker (Perplexity + Firecrawl-Fallback)

Usage:
  python web_enrichment.py --single-query "What is X?"
  python web_enrichment.py --queries-json path/to/queries.json
"""
import argparse, json, subprocess, sys, time
from typing import List, Dict, Any



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

class WebEnricher:
    def __init__(self, rate_limit_per_min: int = 20):
        self.delay = 60.0 / rate_limit_per_min
        self.last_call = 0.0

    def _wait_rate_limit(self):
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_call = time.time()

    def _exec(self, cmd: List[str]) -> str:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            return r.stdout.strip()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return ""

    def search_perplexity(self, query: str) -> Dict[str, Any]:
        out = self._exec(["perplexity", "search", query, "--json"])
        if out:
            try:
                data = json.loads(out)
                return {"query": query, "results": data.get("results", []), "provider": "perplexity"}
            except json.JSONDecodeError:
                pass
        return {}

    def search_firecrawl(self, query: str) -> Dict[str, Any]:
        out = self._exec(["firecrawl", "search", query, "--limit", "3"])
        if out:
            try:
                data = json.loads(out)
                results = [
                    {"url": i.get("url"), "title": (i.get("metadata") or {}).get("title"),
                     "excerpt": (i.get("markdown") or "")[:300], "confidence": 0.7}
                    for i in data.get("data", [])
                ]
                return {"query": query, "results": results, "provider": "firecrawl"}
            except json.JSONDecodeError:
                pass
        return {}

    def enrich(self, query: str) -> Dict[str, Any]:
        t0 = time.time()
        self._wait_rate_limit()
        res = self.search_perplexity(query)
        if not res or not res.get("results"):
            res = self.search_firecrawl(query)
        if not res or not res.get("results"):
            res = {"query": query, "results": [], "provider": "NOT_IMPLEMENTED_YET",
                   "error": "No providers available"}
        res["latency_ms"] = int((time.time() - t0) * 1000)
        return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--queries-json")
    p.add_argument("--single-query")
    args = p.parse_args()

    queries = []
    if args.single_query:
        queries = [args.single_query]
    elif args.queries_json:
        try:
            with open(args.queries_json, "r", encoding="utf-8") as f:
                queries = json.load(f)
        except Exception as e:
            print(json.dumps({"error": f"Failed to read queries: {e}"}))
            sys.exit(1)
    else:
        p.print_help()
        sys.exit(1)

    e = WebEnricher()
    for q in queries:
        print(json.dumps(e.enrich(q), ensure_ascii=False))


if __name__ == "__main__":
    main()
