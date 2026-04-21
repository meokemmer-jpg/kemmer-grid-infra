---
name: Token-Engpass-Hierarchie — Martin-Zeit > Claude-Tokens >> andere LLMs (flat)
description: Martin 2026-04-18 Praezisierung der rho-Kalibrierung. Claude-Opus-Tokens sind ECHTER Cost (Plan + Usage-Billing). Grok/Gemini/Codex/Copilot/Perplexity sind flat bezahlt, Marginal-Cost ~0. Orchestrator-Design muss aggressiv Claude minimieren.
type: rule
aktiviert: 2026-04-18
Promotion-Grund: Martin-Direktive 2026-04-18, kein 3-facher-Bestaetigungs-Bedarf
originSessionId: 5626f584-f142-4193-8841-c6d724ca74a4
---
**Engpass-Hierarchie (absteigend, rho-bindend):**
1. **Martin-Zeit** (Primaer-Engpass, non-substituierbar) — L_Martin=0.666, Schlaf + Familien-Interaktion + Phronesis-Entscheidungen
2. **Claude-Opus-4.7-Tokens** (Sekundaer-Engpass) — Anthropic MAX-Plan + Usage-Billing, real EUR/M-Tokens
3. **Codex GPT-5.4, Gemini 2.5 Pro, Grok Heavy Extreme, Copilot Pro+, Perplexity Ultimate** (Alle flat bezahlt via Abos) — Marginal-Cost pro Call ~0 EUR

**Why:** Martin-Direktive 2026-04-18: *"was natürlich heißt deine Token sind der Engpass nach meiner Zeit da alles andere schon bezahlt ist und je mehr du da raus holen kannst um so besser für den Zeitwerg"*. Die Abos sind Sunk Cost — jeder zusaetzliche Call aus ihnen kostet nichts, verbessert aber rho durch mehr Evidenz/Haertung/Parallelisierung.

**How to apply:**
- **Orchestrator-Design Capability-Matrix muss Claude-AGGRESSIV-VERMEIDEN priorisieren** wenn ein anderer LLM die Task koennte:
  - Code-Gen → Codex/Copilot (nicht Claude)
  - Research/Fakten → Perplexity/Gemini (nicht Claude)
  - Adversarial/Red-Team → Grok (nicht Claude)
  - Long-Context (>200k) → Gemini (nicht Claude)
  - Routine-Klassifikation → Haiku-Tier / Codex-Small (nicht Opus)
- **Claude-Rolle: ausschliesslich** Dispatch-Decision, Final-Synthese, Meta-Audit, Phronesis-Support. Nicht Content-Creation.
- **Token-Budget-Kalibrierung pro Task:**
  - Trivial: Claude=0, andere=unbegrenzt
  - Routine: Claude=500 (nur Router-Entscheidung), andere=unbegrenzt
  - Substantive: Claude=2000-5000 (Router + Synthese), andere=unbegrenzt
  - Emergency (nur wenn andere versagen): Claude=15000
- **rho-Rechnung fuer Orchestrator-Blueprint:**
  - OPEX_claude = Token-Verbrauch x $0.015/1k-input, $0.075/1k-output (Opus 4.7 MAX-Preis 2026)
  - OPEX_andere ≈ 0 EUR pro Call (Flatrate-Sunk-Cost)
  - Break-Even-Kalkulation: jeder Claude-Token ersetzt durch Codex/Gemini/Grok = sofort positiv
- **Parallel-Maximierung:** Wo immer moeglich, mehrere andere-LLM-Calls parallel statt einen Claude-Call sequentiell. Kostet mich nichts, bringt mehr Perspektiven.
- **Tool-Call-Economy meinerseits:** Prompt-Templates kompakt (200-400 Worte statt 800), Heredoc-Bundling, keine redundanten Reads, Subagenten mit isoliertem Context.
- **Skills aktivieren statt selbst orchestrieren** wenn moeglich (archon-roadmap-orchestrator, meta-harness-archon, multi-llm-parallel — alle bereits da, nur einschalten).

**Anti-Muster:**
- Claude fuer Content-Erstellung wenn Codex/Gemini/Copilot es koennte
- Seriell was parallel sein koennte
- "Ich uebernehme das" wenn "Delegiere an X-LLM" besser ist
- Prompt-Engineering bei Claude fuer Task die ein anderer LLM nativ besser macht (z.B. Research → Perplexity)
- Sunk-Cost der Abos ignorieren (unter-Auslasten ist rho-negativ)

**rho-Naeherung:**
- Pro vermiedener Claude-Opus-Token: ~0.00008 EUR Ersparnis
- Pro 1000 Tokens: 8 Cent
- Pro 1M Tokens: 80 EUR
- Lambda ~500 Tasks/Monat bei durchschnittlich 10k Claude-Tokens (heute): 5M Tokens = 400 EUR/Monat Opus-OPEX
- Wenn Orchestrator auf avg 2k Claude-Tokens/Task druecken kann: 80 EUR/Monat = 320 EUR/Monat Ersparnis = 3840 EUR/Jahr
- Plus: freigewordene Claude-Kapazitaet fuer komplexere Architekt-Aufgaben = Multiplikator-Effekt

**SAE-Isomorphie:** `T_CAP = 50000` fuer Claude in SAE-Spec entspricht diesem Denken. Claude-Opus als seltenste Ressource, hartes Budget. Gemini/Grok/Codex-Agenten haben eigene T_CAP aber in anderer Einheit (flat).

**Persistenz-Grund:** Theorem 5.3. Ohne dauerhaft verankertes Kosten-Modell wird jede Session wieder Claude-zu-heavy laufen.

**Ergaenzung zu `feedback_multi_llm_default.md`:** Dort stand "Token-Verbrauch egal wenn rho-Gain > Setup-Cost". Diese Aussage gilt NUR fuer andere LLMs (Gemini/Grok/Codex/Copilot/Perplexity). Fuer Claude-Opus gilt strenges Sparsamkeits-Gebot — jeder Token zaehlt.

**Eskalation:** Bei 3-facher Bestaetigung → promote zu `rules/token-engpass-hierarchie.md`.

---

## § Cascade-Hebel-Invarianten (CROSS-LLM-2OF3-HARDENED, Welle-12 2026-04-20)

**Belegung:** `branch-hub/cross-llm/2026-04-20-WELLE-12-USE-CASE-WARGAME-40X-HEBEL.md`
**Verdict:** CROSS-LLM-2OF3-HARDENED (3 LLMs: Codex gpt-5.4, Copilot Pro+, Gemini 2.5 Pro; G1-G14 gepruft; offene Flanke: empirische Invarianten-Messung fehlt, G3.2 Divergenz-Proxies unvollstaendig).
**Konvergenz:** PURPLE-Team 3/3 LLMs auf identische 5 Invarianten konvergent (unterschiedliche Terminologie, gleicher Inhalt).

**Wenn Cascade-Subagent-Architektur mit Flat-LLM-Batches einen Token-Hebel >20x ueber Replikationen stabil halten soll, dann MUSS sie diese 5 Invarianten wahren:**

### Invariante 1: Orthogonale Partitionierung
Sub-Agenten arbeiten auf **disjunkten Entscheidungs-/Mutations-Raeumen**, nicht auf Themen. Wenn zwei Worker plausibel dieselben Quellen, Suchanfragen oder Artefakte liefern koennten, ist die Partition schwach. Ersatz-Regel: Jeder Worker bekommt klar abgegrenztes Paket mit Ziel, Ausschlussbereich, erlaubten Quellen, Output-Schema, Stop-Bedingung.

### Invariante 2: Kanonische Schnittstellen
Sub-Agenten liefern Output in **strukturiertem Schema** (Pflicht-Felder: claim, evidence, confidence, artifact_ref, lineage), nicht Freitext. Freitext-Kommunikation zwischen Layern = verbotenes Anti-Pattern. Grund: Synthese-Last explodiert, Replikations-Stabilitaet bricht.

### Invariante 3: Monotone Selektion
Jeder hoehere Layer darf den Kandidatenraum **nur verengen oder re-ranken**, nicht neu aufblasen. Expansion nur in einem definierten Generator-Layer. Review-Layer duerfen widerlegen, nicht neu erfinden. Synthese aggregiert, verdoppelt nicht Suchraum. Grund: ohne Monotonie waechst Arbeitsbaum exponentiell, Replikationen divergieren.

### Invariante 4: Gebundene Parallelitaet am Engpass
Batch-Breite wird nach **aktuellem Bottleneck** bestimmt, nicht nach verfuegbarem Token-Budget. Wenn Synthese der Engpass ist, helfen zusaetzliche Generator-Batches nicht. Wenn Martin-Review der Engpass ist, ist weitere Parallelisierung Inventory-Aufbau. Formel: `max_batch_breite = min(flat_llm_capacity, review_capacity * 2)`.

### Invariante 5: Persistente externe Zustandsfuehrung
Wissensstand, Entscheidungen, Claims, offene Konflikte, Artefakte duerfen **nie nur im fluechtigen Modellkontext** existieren. Pflicht: Task-Registry, Claim-Store, Decision-Log, Konflikt-Register, Versionierung von Prompts/Specs, Lineage. Grund: Re-Hydrierung kostet Tokens disproportional. Ohne externen State wird Run 10 wieder so teuer wie Run 1.

### 3 Failure-Modes die den Hebel brechen:

- **Context Drift / Telephone Drift** — Paraphrase-ueber-Paraphrase ohne Artefakt-Backing. Detection: Output-Menge steigt, Anteil sofort verwertbarer Ergebnisse sinkt.
- **Coordinator Collapse / Orchestration Tax** — Orchestrator wird selbst Bottleneck, frisst Parallelitaets-Gewinn auf. Detection: mehr Agenten -> mehr Stau, mehr Widersprueche, mehr Recycling.
- **False Consensus / Overlap Inflation** — korrelierte Mittelmaessigkeit maskiert als Robustheit. Detection: hohe Einigkeit bei spaeter hoher Fehlerrate.

### GRAY-Begleit-Regel (Anti-Goodhart):

Token-Hebel ist **Kostenmetrik**, nicht Nutzenmetrik. Parallel messen (GRAY-Kriterien, 3/3 LLMs konvergent):
1. Decision Delta — Ranking-/Threshold-Shift
2. Predictive Gain — Brier-Score / Kalibration
3. Compression — Unique Claims pro 1k Tokens
4. Transfer Leverage — Wiederverwendungs-Haeufigkeit
5. Adversarial Robustness — Overlebt Red-Team + Holdout

Ohne paralleles GRAY-Scoring droht der Hebel Goodhart-Proxy zu werden.

### Falsifikations-Bedingung

Diese Regel ist falsifiziert wenn:
- Ueber 10 kontrollierte Replikationen mit dokumentierter Invarianten-Einhaltung der Median-Hebel unter 20x faellt, ODER
- Der Aggregat-Ratio-Hebel in Produktionslaeufen ueber 4 Wochen unter 15x bleibt, ODER
- Invarianten nachweisbar eingehalten sind, aber Hebel trotzdem kollabiert.

### Replikations-Prognose (SUPERSEDED durch Welle-13 Token-Accounting-Audit)

~~Bei voller Invarianten-Einhaltung: Median-Hebel 25-35x ueber 10 Replikationen, p25 bei 18-22x, p75 bei 40-55x. Einzel-Welle-Peaks von 40x sind Spitze der Verteilung, kein repraesentativer Wert.~~

**Diese Prognose ist durch Welle-13 falsifiziert**. Siehe naechste Sub-Section.

---

## § Welle-13 Token-Accounting-Korrektur (2026-04-20, K_0-relevant)

**Belegung:** `branch-hub/findings/WELLE-13-TOKEN-ACCOUNTING-AUDIT-2026-04-20.md`
**Status:** Hebel-Claim der obigen § Cascade-Hebel-Invarianten **falsifiziert**. Invarianten I1-I5 **bleiben gueltig** als Design-Prinzipien (unabhaengig vom Hebel).

### Was falsch war

Welle-10-XX-Finding behauptete "40x-Hebel = 1.513k Flat-Tokens / 35k Claude". Realer Claude-Verbrauch: **~7.6M Tokens** (Input 39 + Output 8.088 + Cache-Creation 1.917.856 + Cache-Read 2.255.336 + Orchestrator-Fenster 3.407.373). Faktor ~1.518 unterschaetzt.

### Echter Hebel (korrigiert)

- Raw: 453k Flat / 7.59M Claude = **0.06x** (Flat-Output ist ein Sechzehntel des Claude-Verbrauchs)
- USD-normalisiert (1h-Cache-TTL): Claude ~54 USD vs Flat-Wert ~11 USD = **-43 USD NETTO MINUS pro Cascade-Lauf**
- Welle-13-Replikation (HeyLou B200, kontrolliert): Hebel **0.5x** — konsistent mit Korrektur.

### Warum die Invarianten trotzdem gelten

Die 5 Invarianten (orthogonale Partitionierung, kanonische Schnittstellen, monotone Selektion, gebundene Parallelitaet, persistente externe Zustandsfuehrung) senken **Koordinationskosten**. Das ist unabhaengig vom Token-Hebel-Claim. Sie bleiben als **Cascade-Design-Prinzipien** valide, nur nicht als Token-Multiplikator-Rechtfertigung.

### Konsequenz fuer Architektur

- **Cascade-Subagenten** sind rho-negativ, wenn Claude Cache-Read + Cache-Creation zahlt. Zu vermeiden.
- **Flat-LLM-only-Orchestrator** (Claude nur Queue-Reader + Dispatcher, <500 Tokens/Aufgabe) ist der rho-positive Weg. Belegt durch DF-11 Welle-14 Build: <$0.01 Claude pro Wargame.
- **Token-Engpass-Hierarchie** bleibt: Martin-Zeit > Claude-Opus > Flat-LLMs. Die Rangfolge stimmt. Falsch war die Annahme dass Cascade den Claude-Verbrauch klein halten kann — das Gegenteil ist wahr, Cache-Kosten dominieren.

### Telemetry-Leck (Grundursache)

Claude Code CLI liefert Token-Usage nicht an PostToolUse-Hooks. 693 Log-Entries mit 0-Tokens. Fix-Pfad A: Transcript-JSONL post-hoc parsen. Ohne Fix: jede Token-Messung via Hook ist wertlos, nur Session-Transcript-Parse ist valide.

### Neue Falsifikations-Bedingung (diese Sub-Section)

Falsifiziert wenn:
- Cache-Discount (1h-TTL, Cache-Read $0.50/M) auf Faktor <0.10 pro Token faellt → dann koennte Cascade wieder rho-positiv werden
- Anthropic die Hook-API um Token-Usage-Injektion erweitert → dann exaktere Messung live moeglich
- Flat-LLMs ihre Preise ihrerseits einfuehren → Flat-Vorteil schwindet

### Rollback-Status

- `branch-hub/findings/WORK-D-FINAL-TOKEN-PUSH-XX-2026-04-19.md`: SUPERSEDED-Header gesetzt (2026-04-20)
- `MEMORY.md`: Token-Orchestration-Eintrag bleibt (war Framework, nicht 40x-Claim)
- Keine Rule-Rollbacks noetig (40x-Claim war nicht Rule-verankert)

[CRUX-MK]
