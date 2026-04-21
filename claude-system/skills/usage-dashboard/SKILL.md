---
name: usage-dashboard
description: Oeffnet zentrales LLM-Usage-Dashboard (alle Abos in einer Ansicht Claude/Copilot/ChatGPT/Grok/Gemini/Perplexity). Triggers "usage dashboard", "wie viel haben wir genutzt", "llm usage", "abo status", "dashboard oeffnen". Generiert HTML + oeffnet im Browser.
version: 1.0.0
crux-mk: true
aktiviert: 2026-04-19
---

# Skill: usage-dashboard [CRUX-MK]

## Zweck

Martin-Direktive 2026-04-19: *"wenn ich zu den einzelnen Sources gehen muss ist dies nicht Optimal fuer meine Zeit"*.

EIN Dashboard fuer alle 6 LLM-Abos. Aggregiert Auto-API wo moeglich + Manual-Input-Links wo nicht. One-Click auf Provider-Dashboards. Daily refresh via Scheduled-Task.

## Trigger

- "usage dashboard", "dashboard oeffnen", "llm usage"
- "wie viel haben wir genutzt"
- "abo status", "wie ausgelastet"

## Workflow

### Einfache Ausfuehrung (oeffnet Dashboard im Browser)
```bash
python C:/Users/marti/.claude/scripts/llm_usage_dashboard.py
```

### Refresh ohne Browser-Open
```bash
python C:/Users/marti/.claude/scripts/llm_usage_dashboard.py --no-open
```

### Manual State-Update (wenn API nicht verfuegbar)

State-File: `~/.claude/state/llm-usage-state.json`

Edit pro Provider:
```json
{
  "grok": {
    "usage_eur": 120.0,      // was Martin im console.x.ai gelesen hat
    "usage_percent": 40.0,   // % des Monats-Kontingents
    "calls_count": 350,       // geschaetzt
    "last_manual_update": "2026-04-19T14:00:00"
  }
}
```

Nach Edit: Skill erneut triggern → regeneriert HTML mit neuen Zahlen.

## Dashboard-Struktur

**Uebersicht oben:** Gesamt-Budget / Aktuell genutzt / Auslastung% / Aktive Provider

**Pro Provider-Karte:**
- Abo-Typ + monatliche Kosten
- Genutzt (EUR + % + farbige Statusbar)
- Status-Text: NAHE CAP (rot) / GESUND (orange) / GUT GENUTZT (gruen) / UNTERGENUTZT (grau, rho-negativ!)
- Calls-Count pro Monat
- Renewal-Countdown (Tage bis Abo-Verlaengerung)
- Rolle im Portfolio (Conservative / Aggressive / Contrarian / Authority / Provocator / Source-Finder)
- Direkt-Button zum Provider-Dashboard
- Manual-Update-Hint

## Scheduling

**Daily Refresh taeglich 06:00 lokaler Zeit:**
```powershell
schtasks /create /tn "LLM-Usage-Dashboard" ^
  /tr "python C:\Users\marti\.claude\scripts\llm_usage_dashboard.py --no-open" ^
  /sc daily /st 06:00 /f
```

## Auto-API-Quellen (Stand 2026-04-19)

| Provider | Auto | Quelle |
|----------|------|--------|
| GitHub Copilot Pro+ | ✓ | `gh api /user/settings/billing/actions` |
| Anthropic Claude | ✗ | Admin-API-Key noetig (manual) |
| OpenAI ChatGPT | ✗ | Admin-API-Key noetig (manual) |
| xAI Grok | ✗ | Keine oeffentliche API (manual via console.x.ai) |
| Google Gemini | ✗ | GCP Billing komplex (manual) |
| Perplexity | ✗ | Kein Usage-API (manual) |

**Zukuenftige Erweiterung:** wenn Martin Admin-API-Keys von Anthropic/OpenAI setzt, werden sie automatisch eingelesen.

## Dashboard-Standort

- **Primary (Desktop-shortcut):** `C:/Users/marti/Desktop/llm-usage-dashboard.html`
- **Mirror (Drive):** `G:/Meine Ablage/Claude-Knowledge-System/dashboards/llm-usage.html`
- **History (Trend-Analyse):** `G:/Meine Ablage/Claude-Knowledge-System/dashboards/llm-usage-history.jsonl`

## Browser-Homepage-Trick

Setze als Start-Tab:
1. Browser oeffnen
2. Edit Settings → Homepage → `file:///C:/Users/marti/Desktop/llm-usage-dashboard.html`
3. Jeder Browser-Start zeigt aktuelle Usage

## rho-Impact

- **Vorher:** 6 Provider x 2 Min Navigation = **12 Min/Tag** verlorene Zeit
- **Nachher:** 1 Klick = Dashboard = **10 Sek**
- **Lambda:** 1x/Tag Review = 360 Min/Jahr eingespart = **~€400/Jahr** bei Martin-Zeitwert 50 EUR/h
- **Plus:** Untergenutzte Provider (grau = rho-negativ) werden sofort sichtbar → aktionbar

## Integration mit DF-07 (monthly-model-audit)

Dashboard-state wird von DF-07 monatlich als Input genutzt:
- Usage-Metrics pro Provider → rho_model_prompt berechnung
- Untergenutzte Provider → Role-Reassignment-Kandidaten
- Cost-Drift → automatic Price-Update-Trigger

## Falsifikations-Bedingung

- Martin updatet manual nicht mehr (Dashboard veraltet) → Frequency reduzieren auf weekly
- Auto-API-Quellen aendern sich (gh api /billing/actions deprecated) → Script-Update
- Neue Provider-Abos dazu (z.B. Mistral, DeepSeek) → PROVIDERS-Liste erweitern in llm_usage_dashboard.py

[CRUX-MK]
