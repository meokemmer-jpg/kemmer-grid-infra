# Beispiel HIGH (erwartet ~13/15)

## Input (Kemmer-Research-Output-Passage, synthetisch aus KPM-Variante-D verdichtet)

---

## KPM-Sizing v0.1.0 -- Variante D (SUPERSEDED Half-Kelly)

**Belegung:** Cross-LLM-Wargame 2026-04-19 Codex gpt-5.4 + Grok-4.20-reasoning (2/2 MODIFY-radikal).
**Verdict:** CROSS-LLM-2OF3-HARDENED.

### Kern (Kelly-Fraction kontext-adaptiv)

Half-Kelly fix 0.5 REJECTED (3/3 LLMs: "Lehrbuch-Echokammer"). Stattdessen:

| Kontext | Kelly-Fraction | Begruendung |
|---------|----------------|-------------|
| Normalregime + hoher Edge | 0.40 | Naeher am Kelly-Optimum |
| Normalregime + avg Confidence | 0.30 | Default |
| Erhoehte Vola / Regime-Unsicherheit | 0.25 | Parameter-Schaetzfehler-Puffer |
| Entnahme-Phase | 0.20 | Familien-Mental-Load |
| Regimebruch detektiert | 0 (pausieren) | Kein Auto-Rebalance |

### Drawdown-Caps (zweistufig, ersetzt 30%)

- **Soft-Brake:** 15% akkumuliert -> Position-Reduktion 50%, Review-Pflicht
- **Hard-Cap:** 20% akkumuliert -> Trading-Pause, Martin-Phronesis-Gate
- **Absolute-No-Go:** 25% -> Familien-Notfall-Protokoll

### HIVE nur als Governance-Gate (nicht Trading-Trigger)

- HIVE < 0.7: keine Leverage-Erhoehung (unabhaengig vom Markt-Signal)
- HIVE < 0.5: auto-Deleverage

### Falsifikations-Bedingung

Regel ist falsifiziert wenn:
- Realer Drawdown > 20% trotz Soft-Brake-Trigger -> Soft-Brake greift nicht
- Kelly-Fraction 0.40 fuehrt zu negativer Sharpe ueber 12 Monate -> Fraction zu aggressiv
- Family-Office-Backtest schlechter als Benchmark -> Grundkonzept falsch

### SAE-Isomorphie

Drawdown-Cap analog zu T_CAP = 50000 in SAE-Governance (mechanische Obergrenze). Kelly-Fraction
kontext-adaptiv analog zu klassenspezifischer Strategie (10 AgentClasses unterschiedliche
Parameter). HIVE-Gate analog zu BoundedVeto (COSMOS).

### CRUX-Bindung

K_0 direkt geschuetzt (Substanzverzehr verhindert). Q_0 erhoeht. Anwendbar auf KPM UND
Hotel-RMS-Pricing (Drawdown-Governance ist Domain-uebergreifend).

---

## Erwartete Bewertung (manuelle Nachvollziehung)

- **D1 Decision-Delta = 3**: SUPERSEDED Half-Kelly (Umkehr-Marker), konkrete Parameter, rho-relevant.
- **D2 Predictive-Gain = 3**: Falsifikations-Bedingung mit Mess-Prozedur (12 Monate, Benchmark).
- **D3 Compression = 3**: Kernregel + Tabelle + Klare Abgrenzung + Formel-Struktur.
- **D4 Transfer = 2-3**: KPM + Hotel + SAE = 3 Domaenen, explizite SAE-Isomorphie.
- **D5 Robustness = 2-3**: Cross-LLM-Verdict (2/3) + Modell-Nennungen + Wargame-Durchfuehrung.

**Erwartetes Total: 13-15 (HIGH)**
