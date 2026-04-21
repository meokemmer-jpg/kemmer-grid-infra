#!/usr/bin/env python3
"""
NLM-Meta-Harness-Archon Weekly Meta-Loop (2026-04-19)
Laeuft woechentlich Sonntag 03:00, nach 7 taeglichen Runs.
Gemini-Heavy-Lifting: analysiert Shannon-History + schlaegt Theme-Updates vor.
Claude-Tokens = 0.
"""

import asyncio
import datetime
import json
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
STATE_FILE = VAULT / "areas" / "family" / "instance-d2" / "nlm-archon-state.json"
HUB = Path("G:/Meine Ablage/Claude-Knowledge-System/branch-hub")
AUDIT_LOG = HUB / "audit" / "action-log.jsonl"
WEEKLY_REPORTS = VAULT / "resources" / "_from-nlm" / "_weekly-meta"

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}

def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str, ensure_ascii=False), encoding="utf-8")

async def gemini_call(prompt: str, timeout: int = 120) -> str:
    try:
        proc = await asyncio.create_subprocess_exec(
            "gemini", "-p", prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return out.decode("utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

async def analyze_week(state: dict) -> dict:
    """Gemini analysiert letzte 7 Runs, schlaegt Theme-Updates vor."""
    runs = state.get("runs", [])
    last_week = [r for r in runs if r.get("ts", "") > (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)).isoformat()]
    if not last_week:
        return {"error": "Keine Runs der letzten 7 Tage"}

    themes = state.get("themes", {})
    themes_summary = [
        f"{key}: shannon_history={t.get('shannon_history', [])}, rho={t.get('rho')}, lambda={t.get('lambda')}"
        for key, t in themes.items()
    ]

    prompt = (
        f"Du bist Gemini als Meta-Analyst fuer Martin Kemmer's NLM-Dark-Factory DF-06. "
        f"CRUX: max rho*L ueber T_life. 12-Themen-Katalog rho-gewichtet.\n\n"
        f"=== Letzte 7 Tage Runs ===\n{json.dumps(last_week, indent=2, default=str)[:2500]}\n\n"
        f"=== Themen-Status (shannon_history, rho, lambda) ===\n" + "\n".join(themes_summary) + "\n\n"
        f"AUFGABE: Analysiere rho-gesteuert:\n"
        f"1. Welches Thema hat hoechste Lern-Rate (avg Shannon-Bit * rho * lambda)? → verstaerken\n"
        f"2. Welches Thema ist saturiert (<0.7 bit avg)? → fade oder cooldown\n"
        f"3. Schlage 2 NEUE Sub-Themen vor, die aus bisherigen Reports emergent erscheinen und rho-relevant sind "
        f"(Kemmer-Context: 9dots/HeyLou/KPM, AI-Doktrin, Familie)\n"
        f"4. Schlage 1 Thema vor zum Pausieren (niedrig rho_gain)\n\n"
        f"Output als JSON: {{\"boost\":[keys], \"fade\":[keys], \"new_themes\":[{{\"key\":\"...\",\"label\":\"...\",\"rho\":0.7,\"lambda\":3.0,\"rationale\":\"...\"}}], \"retire\":[keys], \"summary\":\"1 Satz\"}}"
    )
    response = await gemini_call(prompt, timeout=120)
    return _extract_json_lenient(response) or {"raw": response[:2000], "parse_error": True}


def _extract_json_lenient(text: str) -> dict | None:
    """IL-12 v2.2-M3 Patch (2026-04-19): Robuster JSON-Parser.

    Gemini liefert oft:
    - Markdown-Code-Block: ```json\n{...}\n```
    - Deutsche Dezimal-Kommata statt Punkte (zu Zahlen)
    - Extra-Text vor/nach dem JSON-Block
    - Unicode-Smart-Quotes
    Alter Parser (find{ rfind}) scheiterte in diesen Faellen.

    Reihenfolge: (1) fenced code-block ```json, (2) generischer fenced, (3) first-{ last-}.
    """
    import re as _re
    if not text:
        return None

    # (1) Markdown-Fenced-Block ```json ... ```
    for pattern in [
        r"```json\s*\n(.+?)\n```",
        r"```\s*\n(\{.+?\})\s*\n```",
    ]:
        m = _re.search(pattern, text, _re.DOTALL | _re.IGNORECASE)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                continue

    # (2) Smart-Quote-Normalisierung + Retry
    normalized = text.replace("\u201c", '"').replace("\u201d", '"').replace("\u2018", "'").replace("\u2019", "'")
    start = normalized.find("{")
    end = normalized.rfind("}")
    if start >= 0 and end > start:
        candidate = normalized[start:end+1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # (3) Letzter Versuch: Komma-vor-Schliess-Bracket entfernen (trailing comma)
            cleaned = _re.sub(r",(\s*[}\]])", r"\1", candidate)
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass
    return None

def apply_theme_updates(state: dict, updates: dict) -> dict:
    """Wendet Gemini-Vorschlaege auf state an (konservativ, mit Audit-Trail)."""
    themes = state.setdefault("themes", {})
    applied = {"boosted": [], "faded": [], "added": [], "retired": []}

    # Boost: rho *= 1.1 (max 1.0)
    for key in updates.get("boost", [])[:3]:  # max 3
        if key in themes:
            themes[key]["rho"] = min(1.0, themes[key].get("rho", 0.5) * 1.1)
            applied["boosted"].append(key)

    # Fade: lambda *= 0.8
    for key in updates.get("fade", [])[:3]:
        if key in themes:
            themes[key]["lambda"] = max(0.5, themes[key].get("lambda", 1.0) * 0.8)
            applied["faded"].append(key)

    # New themes (max 2 pro Woche)
    for new_theme in updates.get("new_themes", [])[:2]:
        key = new_theme.get("key")
        if key and key not in themes:
            themes[key] = {
                "label": new_theme.get("label", key),
                "rho": new_theme.get("rho", 0.6),
                "lambda": new_theme.get("lambda", 2.0),
                "stop_bit": 0.5,
                "added_ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "added_rationale": new_theme.get("rationale", ""),
            }
            applied["added"].append(key)

    # Retire (max 1 pro Woche, kein Loeschen, nur lambda=0)
    for key in updates.get("retire", [])[:1]:
        if key in themes:
            themes[key]["lambda"] = 0.0
            themes[key]["retired_ts"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            applied["retired"].append(key)

    return applied

async def main():
    """IL-13 Flag-Scheduling (2026-04-19): Pre-Flight-Checks gegen Daily/Weekly-Race.

    Problem (Gemini-Finding M4): Weekly-Scheduled-Task laeuft starr SUN 03:00,
    waehrend Daily 02:00 laeuft und bis >60 Min dauern kann. Race-Condition
    wenn weekly_meta_loop state.json liest waehrend Daily schreibt.

    Fix: (1) Check dass Daily-Run von heute bereits erfolgreich (state.runs
    hat Eintrag mit ts startet mit heute). (2) Active-Lock via .ACTIVE-Flag,
    max 60 Min alt tolerieren (stale lock cleanup).
    """
    import time
    print(f"[{datetime.datetime.now().isoformat()}] Weekly Meta-Loop start")

    # Pre-Flight 1: Active-Lock (verhindert Parallel-Starts)
    active_flag = STATE_FILE.parent / "weekly-meta-loop.ACTIVE"
    if active_flag.exists():
        age = time.time() - active_flag.stat().st_mtime
        if age < 3600:  # < 60 Min
            print(f"[weekly_meta_loop] Aktive Lock {age:.0f}s alt — Parallel-Start verhindert, skip.")
            return
        else:
            print(f"[weekly_meta_loop] Stale Lock {age:.0f}s alt — uebernehme.")
    active_flag.touch()

    try:
        state = load_state()
        if not state.get("runs"):
            print("Keine Run-Daten, nichts zu tun")
            return

        # Pre-Flight 2: Daily-Run von heute muss done sein
        today_iso = datetime.date.today().isoformat()
        todays_runs = [r for r in state["runs"] if r.get("ts", "").startswith(today_iso)]
        if not todays_runs:
            print(f"[weekly_meta_loop] Daily-Run von {today_iso} noch nicht erfolgt — skip.")
            print(f"[weekly_meta_loop] Letzte 3 Runs: {[r.get('ts', '?')[:19] for r in state['runs'][-3:]]}")
            print(f"[weekly_meta_loop] Weekly-Loop benoetigt Daily-Run als Vorbedingung (M4 Flag-Scheduling).")
            return
        print(f"[weekly_meta_loop] Pre-Flight OK: {len(todays_runs)} Daily-Runs heute, letzter {todays_runs[-1].get('ts', '?')[:19]}.")

        await _main_body(state)
    finally:
        # Active-Lock immer freigeben (auch bei Exception)
        active_flag.unlink(missing_ok=True)

async def _main_body(state: dict):
    """Eigentliche Meta-Loop-Logik (extrahiert fuer Lock-Kapselung)."""

    updates = await analyze_week(state)
    print(f"[gemini-analysis] {json.dumps(updates, ensure_ascii=False)[:500]}")

    if updates.get("parse_error"):
        # Speicher rohe Analyse, fail-soft
        WEEKLY_REPORTS.mkdir(parents=True, exist_ok=True)
        (WEEKLY_REPORTS / f"weekly_{datetime.date.today().isoformat()}_raw.md").write_text(
            updates.get("raw", ""), encoding="utf-8"
        )
        print("Parse-error, raw gespeichert, keine State-Aenderungen")
        return

    applied = apply_theme_updates(state, updates)
    save_state(state)

    # Weekly-Report schreiben
    WEEKLY_REPORTS.mkdir(parents=True, exist_ok=True)
    report = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "gemini_suggestions": updates,
        "applied": applied,
        "summary": updates.get("summary", ""),
    }
    (WEEKLY_REPORTS / f"weekly_{datetime.date.today().isoformat()}.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Audit-Log
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "branch": "DF-06-nlm-archon-v2",
            "action": "WEEKLY-META-LOOP",
            "boosted": applied["boosted"],
            "faded": applied["faded"],
            "added": applied["added"],
            "retired": applied["retired"],
        }, ensure_ascii=False) + "\n")

    print(f"[applied] {applied}")
    print(f"[state] {len(state['themes'])} themes aktiv")

if __name__ == "__main__":
    asyncio.run(main())
