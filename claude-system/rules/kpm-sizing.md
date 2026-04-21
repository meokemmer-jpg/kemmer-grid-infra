---
name: kpm-sizing
description: KPM-Trading Position-Sizing + Drawdown-Governance. Ersetzt Half-Kelly v1.0/v1.1 durch Variante-D-Hybrid (Kelly-Fraction kontext-adaptiv, realistischer Drawdown-Cap, HIVE als Governance-Gate).
type: rule
meta-ebene: E3 (Anwendungs-Methodik) mit E1-Fundament (Kelly-Mathematik)
status: ACTIVE-CONDITIONAL (2026-04-19 via C2+C3-Wargame 2/2 MODIFY, Martin-Switch auf Variante D)
created: 2026-04-19
aktiviert: 2026-04-19
supersedes: "Half-Kelly Kristall v1.0/v1.1 (METAOPS Mission-5 2026-04-18, Cross-LLM 3/3 Lehrbuch-Echokammer)"
cross-llm-reference: branch-hub/cross-llm/2026-04-19-WARGAME-C2C3-C3a-Half-Kelly-v1.1.md
parent-finding: branch-hub/findings/FINDING-C2-C3-METASTACK-WARGAME-2026-04-19.md
claim-type: empirical (Drawdown-Caps + Kelly-Fraction sind durch Backtesting falsifizierbar)
k0-relevance: HIGH (20M+ Family-Portfolio, Substanzverzehr-Risiko)
q0-relevance: MEDIUM (Familien-Vermoegens-Stabilitaet)
---

# KPM-Sizing Rule [CRUX-MK]

**Zweck:** Position-Sizing + Drawdown-Governance fuer KPM (Kemmer-Portfolio-Management) Familien-Trading.
**Ersetzt:** Half-Kelly Kristall v1.0/v1.1 (rejected als "Lehrbuch-Echokammer" im C2+C3-Wargame 2026-04-19).

## Martin-Entscheidung 2026-04-19

Option **Variante D-Hybrid** nach Cross-LLM-Wargame (Codex GPT-5.4 + Grok-4.20-reasoning 2/2 MODIFY-radikal). Ablage **hier in `rules/kpm-sizing.md`** — NICHT CLAUDE.md-Verfassungsrang (Finanzheuristik != Betriebsrecht).

## Kern-Parameter (Variante D)

### 1. Kelly-Fraction: 0.25-0.40 kontext-adaptiv (NICHT fix 0.5 Half-Kelly)

| Kontext | Kelly-Fraction | Begruendung |
|---------|----------------|-------------|
| Normalregime + hoher Edge-Confidence | 0.40 | Naeher am Kelly-Optimum bei gutem Signal |
| Normalregime + durchschnittliche Confidence | 0.30 | Default |
| Erhoehte Vola / Regime-Unsicherheit | 0.25 | Konservativ bei Modellfehler-Risk |
| Entnahme-Phase / Liquiditaetsbedarf hoch | 0.20 | Familien-Mental-Load |
| Regimebruch detektiert | 0 (pausieren) | Kein Auto-Rebalance |

**Begruendung:** Half-Kelly (0.5) ist Lehrbuch-Default, aber fuer Family-Office mit **endlicher Horizon + Entnahmebedarf + Mental-Load** zu aggressiv. 0.25-0.40 gibt Puffer fuer Parameterschaetzfehler + psychologische Limits.

### 2. Drawdown-Caps (zweistufig)

- **Soft-Brake:** 15% akkumulierter Drawdown → Position-Reduktion um 50%, Review-Pflicht
- **Hard-Cap:** 20% akkumulierter Drawdown → Trading-Pause, Martin-Phronesis-Gate
- **Absolute-No-Go:** 25% akkumulierter Drawdown → harter Stop, Familien-Notfall-Protokoll

**Begruendung:** Original Half-Kelly v1.0 hatte 30% Drawdown-Cap. Zu locker fuer Family-Office (Substanzverzehr-Risiko -100k bis -500k EUR/J bei Regimebruch).

### 3. HIVE nur als Governance-Gate

**Vorher (Half-Kelly v1.1 REJECTED):** HIVE>0.7 triggert Rebalance. Falsch gekoppelt — Shannon-Team-Score hat nichts mit Markt-Signal zu tun.

**Jetzt (Variante D):** HIVE als Governance-Gate fuer Leverage-Erhoehung:
- HIVE < 0.7: keine Leverage-Erhoehung (auch wenn Markt-Signal positiv)
- HIVE >= 0.7: Leverage-Erhoehung moeglich innerhalb Kelly-Fraction-Limits
- HIVE < 0.5: auto-Deleverage

Rebalance-Trigger ist **marktbasiert** (Vola, Korrelation, Forecast-Dispersion, Edge-Decay, Leverage-Drift), NICHT HIVE.

### 4. Nicht-Cross-LLM-HARDENED (wichtig)

**Status: CONDITIONAL**, NICHT HARDENED. Grund:
- Claude+Codex+Gemini Konsens auf Kelly/Thorp/Lehrbuch ist **Echokammer** (gemeinsam trainiert auf gleichen Finance-Textbooks)
- Ohne G3.2-Divergenz-Proxies keine echte Cross-Model-Divergenz
- Empfehlung Cross-LLM: max PROVISIONAL (G3.4)

**Hardening-Pfad:**
- Adversarial-Prompts zu Tail-/Regimebruch-Szenarien durchspielen
- Blindtests mit fehlerhaften Edge-Schaetzungen
- Mindestens 1 non-LLM-Check (Backtest historische Family-Office-Krisen 2008/2020/2022)
- Dann moeglicherweise Upgrade zu CROSS-LLM-SIM-HARDENED

### 5. Phase-1 Pilotierung (beibehalten aus v1.1)

- **Thomas-First:** Pilot mit Thomas-Allokation (konservative Startgroesse)
- **Shadow-Mode:** 3+ Monate Paper-Trading bevor Real-Capital
- **Review-Cadence:** monatlich Claude + Martin, quartalsweise Steuerberater + externe Referenz

## Implementation-Checks (Pflicht vor Live)

1. **Backtest** ueber historische Krisen (2008 Finanzkrise, 2020 COVID-Crash, 2022 Bear-Market)
2. **Regimebruch-Stress-Test** mit 40% Drawdown-Szenario
3. **Forecast-Dispersion-Monitor** (wenn LLM-Forecast-Varianz steigt → auto-Deleverage)
4. **Edge-Decay-Alert** (wenn realized-return < forecast-return fuer 3 consecutive Monate → Strategy-Review)

## Falsifikations-Bedingungen

Regel ist falsifiziert wenn:
- Realer Drawdown > 20% trotz Soft-Brake-Trigger → Soft-Brake greift nicht
- Kelly-Fraction 0.40 fuehrt zu negativer Sharpe-Ratio ueber 12 Monate → Fraction zu aggressiv
- HIVE-Gate blockiert profitable Trades chronisch → Gate zu restriktiv
- Family-Office-Backtest zeigt schlechter als Benchmark → Grundkonzept falsch

## Anti-Patterns (aus C2+C3-Wargame belegt)

1. **Half-Kelly fix 0.5** als Default ohne Kontext-Adaption (Codex: "Full-Kelly ist asymptotisches Optimum, Half-Kelly ist Praxis-Heuristik, nicht kanonischer Default")
2. **Drawdown-Cap 30%** ohne Soft/Hard-Staffelung (Grok: "Zu locker fuer Family-Office-Governance")
3. **HIVE direkt als Trading-Trigger** (fachlich schief gekoppelt)
4. **Cross-LLM als HARDENED-Beleg** auf Finanz-Mathematik (Echokammer-Risiko)
5. **Ablage in CLAUDE.md-Verfassungsrang** (vermischt Finanzheuristik mit Betriebsrecht)

## Promotion-Pfad

- **v0.1.0 (jetzt, 2026-04-19):** CONDITIONAL via Martin-Switch Variante D
- **v0.2.0 (nach Backtest + Regimebruch-Test):** CROSS-LLM-SIM-HARDENED moeglich
- **v1.0.0 (nach 3 Monate Shadow-Mode + realen Trade-Ergebnissen):** HARDENED-PRODUCTION
- **NIE CLAUDE.md-Promotion** — bleibt in rules/ als Finanz-Spezial-Regel

## CRUX-Bindung

- **K_0:** DIREKT GESCHUETZT — Drawdown-Caps + Kelly-Fraction-Kontext-Adaption verhindern Substanzverzehr
- **Q_0:** erhoeht — Familien-Vermoegens-Stabilitaet durch HIVE-Gate + Review-Cadence
- **I_min:** strukturiert (Implementation-Checks + Falsif-Bedingungen explizit)
- **W_0:** Martin-Review-Zeit geschuetzt durch klare Trigger + Automatisierung

## Historischer Kontext

- **v1.0 (METAOPS Mission-5, 2026-04-18):** Half-Kelly 0.5 + Drawdown 30% + HIVE>0.7 Trigger. 3-LLM-Konsens (Claude+Codex+Gemini 3/3 ADOPT/MODIFY) als "HARDENED" proklamiert.
- **v1.1 (METAD2 Continuation, 2026-04-19):** CLAUDE.md-Eintrag-Vorschlag.
- **Wargame C3a (2026-04-19):** 2/2 MODIFY (Codex + Grok unabhaengig). Befund: "Lehrbuch-Echokammer", K_0-Risiko, nicht HARDENED.
- **Martin-Switch 2026-04-19:** Variante D-Hybrid, Ablage `rules/kpm-sizing.md`.

[CRUX-MK]
