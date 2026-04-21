"""LLM Usage Dashboard Generator [CRUX-MK]

Aggregiert Usage-Data aller Kemmer-LLM-Abos in EIN HTML-Dashboard.
Aktiviert 2026-04-19 durch Martin-Direktive "ich will EIN Dashboard".

Strategie:
- Auto-Update wo moeglich (GitHub via gh api)
- Manual-Input via state.json (Martin tippt wochentlich in ~2min)
- Direkt-Links zu jedem Provider-Dashboard
- Abo-Renewal-Countdown pro Provider
- Token-Budget-Gauge fuer Claude-Opus

Usage:
    python llm_usage_dashboard.py          # Generate + open
    python llm_usage_dashboard.py --no-open  # Just generate
    python llm_usage_dashboard.py --manual  # Force manual-input prompts
"""
from __future__ import annotations
import json
import subprocess
import sys
import os
import webbrowser
from datetime import datetime, date, timedelta
from pathlib import Path

# --- Paths ---
STATE_FILE = Path.home() / ".claude" / "state" / "llm-usage-state.json"
DASHBOARD_OUT = Path("C:/Users/marti/Desktop/llm-usage-dashboard.html")
DASHBOARD_MIRROR = Path("G:/Meine Ablage/Claude-Knowledge-System/dashboards/llm-usage.html")
HISTORY_LOG = Path("G:/Meine Ablage/Claude-Knowledge-System/dashboards/llm-usage-history.jsonl")

# --- Provider Definitions ---
# Renewal-Dates aus Martin's Screenshots
PROVIDERS = [
    {
        "id": "claude",
        "name": "Claude Pro/Max (Anthropic)",
        "subscription": "Pro/Max (1M context)",
        "cost_eur_per_month": 180.0,  # ~$200
        "renewal": "2026-05-01",  # rolling monthly, Martin kann updaten
        "dashboard_url": "https://console.anthropic.com/settings/usage",
        "role": "Conservative (Strategy, K_0, Q_0, Phronesis)",
        "auto_api": False,
        "manual_hint": "console.anthropic.com -> Settings -> Usage (monthly cost)",
    },
    {
        "id": "copilot",
        "name": "GitHub Copilot Pro+",
        "subscription": "Pro+ ($39/Mo)",
        "cost_eur_per_month": 36.0,
        "renewal": "rolling",
        "dashboard_url": "https://github.com/settings/billing/summary",
        "role": "Aggressive (Code/Docs, GitHub-MCP)",
        "auto_api": True,  # gh api
        "manual_hint": "github.com/settings/billing (premium-request count)",
    },
    {
        "id": "chatgpt",
        "name": "ChatGPT Pro (OpenAI/Codex)",
        "subscription": "Pro ($200/Mo)",
        "cost_eur_per_month": 185.0,
        "renewal": "2026-05-08",
        "dashboard_url": "https://platform.openai.com/account/usage",
        "role": "Contrarian (Code-Review, Deep-Research, gpt-5.4)",
        "auto_api": False,
        "manual_hint": "platform.openai.com -> Usage (last 30d)",
    },
    {
        "id": "grok",
        "name": "SuperGrok Heavy (xAI)",
        "subscription": "Heavy (~$300/Mo)",
        "cost_eur_per_month": 275.0,
        "renewal": "2026-05-14",
        "dashboard_url": "https://console.x.ai/team/default/billing",
        "role": "Provocator (Adversarial, X-Search, Multi-Agent)",
        "auto_api": False,
        "manual_hint": "console.x.ai -> Billing (Monthly snapshot)",
    },
    {
        "id": "gemini",
        "name": "Gemini Ultra (Google AI)",
        "subscription": "Ultra (bundle)",
        "cost_eur_per_month": 0.0,  # bundled with Google One / Workspace
        "renewal": "rolling",
        "dashboard_url": "https://ai.google.dev/gemini-api/docs/billing",
        "role": "Authority (Facts, Citations, Large-Context)",
        "auto_api": False,
        "manual_hint": "ai.google.com + cloud.google.com/billing",
    },
    {
        "id": "perplexity",
        "name": "Perplexity Pro Ultimate",
        "subscription": "Ultimate (~$40/Mo)",
        "cost_eur_per_month": 37.0,
        "renewal": "rolling",
        "dashboard_url": "https://www.perplexity.ai/settings/account",
        "role": "Source-Finder (Citations, Live-Web)",
        "auto_api": False,
        "manual_hint": "perplexity.ai -> Settings (search count)",
    },
]


def load_state() -> dict:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    # Default-Template
    return {
        p["id"]: {"usage_eur": 0.0, "usage_percent": 0.0, "calls_count": 0, "last_manual_update": None}
        for p in PROVIDERS
    }


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def auto_fetch_github(state: dict) -> dict:
    """Auto-update GitHub Copilot metrics via gh api."""
    try:
        result = subprocess.run(
            ["gh", "api", "/user/settings/billing/actions"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            state["copilot"]["usage_eur"] = float(data.get("total_paid_minutes_used", 0)) * 0.008  # rough estimate
            state["copilot"]["calls_count"] = data.get("total_minutes_used", 0)
            state["copilot"]["last_auto_update"] = datetime.now().isoformat()
    except Exception:
        pass  # silent fail, keeps manual state
    return state


def days_until(date_str: str) -> str:
    if date_str == "rolling":
        return "rolling monthly"
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d").date()
        delta = (target - date.today()).days
        if delta < 0:
            return f"ueberfaellig (-{abs(delta)}d)"
        elif delta == 0:
            return "HEUTE"
        elif delta < 7:
            return f"{delta} Tage (!)"
        else:
            return f"{delta} Tage"
    except Exception:
        return date_str


def generate_html(state: dict) -> str:
    total_monthly = sum(p["cost_eur_per_month"] for p in PROVIDERS)
    total_used_eur = sum(state.get(p["id"], {}).get("usage_eur", 0) for p in PROVIDERS)
    utilization = (total_used_eur / total_monthly * 100) if total_monthly else 0

    cards_html = ""
    for p in PROVIDERS:
        s = state.get(p["id"], {})
        usage_eur = s.get("usage_eur", 0)
        usage_pct = s.get("usage_percent", 0)
        calls = s.get("calls_count", 0)
        last_update = s.get("last_manual_update") or s.get("last_auto_update") or "nie"
        renewal_text = days_until(p["renewal"])

        # Status-Farbe basierend auf Utilization
        if usage_pct > 90:
            color = "#ef4444"  # rot (close to cap)
            status_text = "NAHE CAP"
        elif usage_pct > 50:
            color = "#f59e0b"  # orange (healthy)
            status_text = "GESUND"
        elif usage_pct > 10:
            color = "#10b981"  # gruen (well used)
            status_text = "GUT GENUTZT"
        else:
            color = "#6b7280"  # grau (underused)
            status_text = "UNTERGENUTZT (rho-negativ!)"

        auto_badge = '<span class="badge auto">auto</span>' if p["auto_api"] else '<span class="badge manual">manual</span>'

        cards_html += f"""
        <div class="card" style="border-top: 4px solid {color};">
          <div class="card-header">
            <h2>{p["name"]}</h2>
            {auto_badge}
          </div>
          <div class="sub">{p["subscription"]}</div>
          <div class="metrics">
            <div class="metric">
              <div class="metric-label">Genutzt</div>
              <div class="metric-value">€{usage_eur:.2f} / €{p["cost_eur_per_month"]:.0f}</div>
              <div class="bar"><div class="bar-fill" style="width: {usage_pct}%; background: {color};"></div></div>
              <div class="metric-status" style="color: {color};">{status_text} ({usage_pct:.0f}%)</div>
            </div>
            <div class="metric">
              <div class="metric-label">Calls / Month</div>
              <div class="metric-value">{calls:,}</div>
            </div>
            <div class="metric">
              <div class="metric-label">Renewal</div>
              <div class="metric-value">{renewal_text}</div>
            </div>
          </div>
          <div class="role"><b>Rolle:</b> {p["role"]}</div>
          <div class="actions">
            <a href="{p["dashboard_url"]}" target="_blank" class="btn-open">Dashboard oeffnen ↗</a>
            <span class="last-update">Stand: {last_update[:16] if last_update != "nie" else "nie"}</span>
          </div>
          <details class="hint">
            <summary>Manual Update Hint</summary>
            <div>{p["manual_hint"]}</div>
          </details>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>LLM Usage Dashboard [CRUX-MK]</title>
<style>
* {{ box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
       background: #0f172a; color: #e5e7eb; margin: 0; padding: 2rem;
       max-width: 1400px; margin-left: auto; margin-right: auto; }}
h1 {{ color: #fbbf24; margin: 0 0 0.5rem 0; }}
.subtitle {{ color: #94a3b8; margin-bottom: 2rem; }}
.summary {{ background: #1e293b; padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;
           display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; }}
.summary-item {{ text-align: center; }}
.summary-label {{ color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.3rem; }}
.summary-value {{ font-size: 1.8rem; font-weight: bold; color: #fbbf24; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1.5rem; }}
.card {{ background: #1e293b; padding: 1.5rem; border-radius: 12px; }}
.card-header {{ display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.3rem; }}
.card h2 {{ margin: 0; color: #f3f4f6; font-size: 1.2rem; }}
.badge {{ padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: bold; }}
.badge.auto {{ background: #10b981; color: white; }}
.badge.manual {{ background: #6b7280; color: white; }}
.sub {{ color: #94a3b8; font-size: 0.9rem; margin-bottom: 1rem; }}
.metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem; }}
.metric-label {{ color: #94a3b8; font-size: 0.8rem; margin-bottom: 0.2rem; }}
.metric-value {{ font-size: 1.1rem; font-weight: bold; color: #f3f4f6; }}
.metric-status {{ font-size: 0.75rem; margin-top: 0.3rem; font-weight: bold; }}
.bar {{ background: #334155; height: 6px; border-radius: 3px; margin: 0.5rem 0; }}
.bar-fill {{ height: 100%; border-radius: 3px; transition: width 0.3s; }}
.role {{ color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem; padding-top: 1rem; border-top: 1px solid #334155; }}
.actions {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }}
.btn-open {{ background: #fbbf24; color: #0f172a; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 0.85rem; }}
.btn-open:hover {{ background: #f59e0b; }}
.last-update {{ color: #64748b; font-size: 0.75rem; }}
.hint {{ background: #0f172a; padding: 0.5rem; border-radius: 6px; margin-top: 0.5rem; font-size: 0.85rem; color: #94a3b8; }}
.hint summary {{ cursor: pointer; }}
.hint div {{ margin-top: 0.5rem; }}
.footer {{ text-align: center; color: #64748b; margin-top: 3rem; font-size: 0.85rem; }}
.footer code {{ background: #1e293b; padding: 0.2rem 0.5rem; border-radius: 4px; color: #fbbf24; }}
</style>
</head>
<body>
<h1>LLM Usage Dashboard [CRUX-MK]</h1>
<div class="subtitle">Stand: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Auto-Refresh via scheduled-task 06:00 | Martin Kemmer</div>

<div class="summary">
  <div class="summary-item">
    <div class="summary-label">Gesamt-Monatsbudget</div>
    <div class="summary-value">€{total_monthly:.0f}</div>
  </div>
  <div class="summary-item">
    <div class="summary-label">Aktuell genutzt</div>
    <div class="summary-value">€{total_used_eur:.0f}</div>
  </div>
  <div class="summary-item">
    <div class="summary-label">Auslastung</div>
    <div class="summary-value">{utilization:.0f}%</div>
  </div>
  <div class="summary-item">
    <div class="summary-label">Provider aktiv</div>
    <div class="summary-value">{len(PROVIDERS)}</div>
  </div>
</div>

<div class="cards">
{cards_html}
</div>

<div class="footer">
  <p>Update-Befehle:</p>
  <p>Automatisch: <code>python ~/.claude/scripts/llm_usage_dashboard.py</code> (oder via Scheduled-Task daily 06:00)</p>
  <p>Manuelle Werte: Edit <code>~/.claude/state/llm-usage-state.json</code> oder via Skill <code>usage-dashboard update</code></p>
  <p>[CRUX-MK] Zeitwertverfassung: Jeder Flat-Abo-EUR der nicht genutzt wird = rho-negativ. Untergenutzte Provider (grau) muessen re-routed werden.</p>
</div>

</body>
</html>"""
    return html


def log_history(state: dict) -> None:
    HISTORY_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "state": state,
    }
    with open(HISTORY_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> int:
    state = load_state()
    state = auto_fetch_github(state)
    save_state(state)
    log_history(state)

    html = generate_html(state)

    DASHBOARD_OUT.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_OUT.write_text(html, encoding="utf-8")
    print(f"Dashboard generated: {DASHBOARD_OUT}")

    if DASHBOARD_MIRROR.parent.exists():
        DASHBOARD_MIRROR.parent.mkdir(parents=True, exist_ok=True)
        DASHBOARD_MIRROR.write_text(html, encoding="utf-8")
        print(f"Mirror: {DASHBOARD_MIRROR}")

    if "--no-open" not in sys.argv:
        webbrowser.open(f"file:///{DASHBOARD_OUT.as_posix()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
