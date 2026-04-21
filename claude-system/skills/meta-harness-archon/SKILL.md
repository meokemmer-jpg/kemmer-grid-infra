---
name: meta-harness-archon
description: Meisterwerk-Skill fuer Claim-Haertung. Vereint Wargame-v7 + 4-Team + 5-Ordnungen + Multi-Language-30-EU + Cross-LLM + Pentagon + Archon-Workflow + Self-Improvement. Ersetzt wargame und 4-team-wargame. Triggers "meta-harness", "meta wargame", "haerte das", "archon wargame", "multi-language wargame", "cross-eu wargame".
crux-mk: true
version: 1.1.1
aktiviert: 2026-04-18
changelog: "v1.1.1 (2026-04-18 METAOPS Live-Test) 3 Patches aus METAOPS-LIVE-001 Half-Kelly-Test: P1 Phase-2 Multi-Language conditional (Default SKIP bei E1/E2), P2 Phase-0.3 Claim-Wording-Drift-Scan, P3 Phase-3 Tier-Mix-Strategien + Phase-5 Dual-Verdict-Schema (original vs revised). v1.1.0 (2026-04-18) Phase 0.5 Fork-Pattern-Check + Token-Budget-Guideline (aus METADD-Handoff-Analyse). v1.0.0 (2026-04-18) Initial 7 Phasen + Multi-Language-30-EU + Cross-LLM + Archon-Workflow."
supersedes: [wargame v7 (bleibt fuer strategische Initiativen), 4-team-wargame v1.0 (integriert)]
live-tests:
  - METAOPS-LIVE-001 (Half-Kelly, 2026-04-18): verdict REJECTED original / 2OF3-HARDENED revised, 17 Min Dauer, 4 Bugs entdeckt, alle 4 in v1.1.1 gefixt
triggers:
  - "meta-harness"
  - "meta wargame"
  - "haerte das"
  - "haerte den claim"
  - "archon wargame"
  - "multi-language wargame"
  - "cross-eu wargame"
  - "multilingual wargame"
  - "30 sprachen wargame"
  - "gold standard wargame"
  - "wargame-master"
---

# meta-harness-archon — Das Wargame-Meisterwerk [CRUX-MK]

**Martin-Direktive 2026-04-18:** *"einen neuen Wargame Archron META Harness der die Multilanguage findings ja alle 30 Europaeische Sprachen nutzen ... der Skill ... architektonisch ... ein Meta Harness Archron Meisterwerk"*

## Zweck

Genau EIN Skill fuer Claim-Haertung, der alle bisherigen Wargame-Technologien vereint und kontinuierlich lernt. Ersetzt partielles Wargaming und atomisiert den Meta-Harness-Loop.

## Genesis (was dieser Skill ersetzt/erweitert)

| Quelle | Beitrag in meta-harness-archon |
|--------|-------------------------------|
| `wargame` v7 | Clausewitz/Moltke/Shannon/Musashi/36-Strategeme |
| `4-team-wargame` v1 | Red/Blue/Purple/Gray-Struktur, E1-E5-Klassifikation |
| `cross-llm-real` | Codex-MCP + Multi-Model-Kombi |
| `multi-llm-parallel` | Web-UI-Multi-LLM (Grok, Perplexity, Copilot) |
| `meta-learn-kristall-audit` | Archon-Workflow-Pattern (Pentagon + Nodes) |
| `meta-prompting` | Suzgun-Kalai Conductor + OPRO-Loop |
| `rules/meta-validation-portfolio.md` | Methoden-Matrix pro Aussage-Typ |
| `rules/meta-methodological-pragmatism.md` | rho-Gain-Messung (3-Sessions-Shadow) |
| `rules/meta-governance-framework.md` | G1-G14 Governance-Kriterien |
| `rules/meta-stack-fixpunkte.md` | 4 E5-Fixpunkte-Check |
| `rules/crux.md` + `crux-gate-grenzen.md` | 2-Wargame-Gate, Meta-Ebenen-Asymmetrie |
| `findings/LERNEN-META-LERNEN-KONSOLIDIERUNG-2026-04-17.md` | Multi-Language-Prompting (NLM-Destillat), 15+11 Lern/Meta-Lern-Prinzipien |
| NLM-Chats `resources/nlm/chats/*/meta-lehren.md` | Cross-Domain-Lehren |

## Architektur (8-Phasen-Pentagon + Archon-DAG)

```
┌─────────────────────────────────────────────────────────┐
│  PHASE 0: CLAIM-INTAKE + KLASSIFIKATION (E1-E5)         │
│  PHASE 0.5: FORK-PATTERN-CHECK (bei neuer Instanz)      │
│  PHASE 1: 4-TEAM-WARGAME (Red/Blue/Purple/Gray)         │
│  PHASE 2: MULTI-LANGUAGE-PROMPTING (6 EU-Cluster, 30L)  │
│  PHASE 3: CROSS-LLM-VALIDATION (Codex + Fallback)       │
│  PHASE 4: VERDICT-MATRIX (G1-G14 + Fixpunkt-Check)      │
│  PHASE 5: PERSISTENZ (Decision-Card + Action-Log)       │
│  PHASE 6: SELF-IMPROVEMENT (rho-Gain-Messung, v-Bump)   │
└─────────────────────────────────────────────────────────┘
```

**Phase 0.5 NEU (seit v1.1.0):** Destillat aus METADD-Handoff-Analyse (`findings/KV-HANDOFF-ANALYSE-METADD-2026-04-18.md`). Verhindert Theorem-5.3-Verlust bei Fork-Operationen.

---

## PHASE 0 — Claim-Intake + Klassifikation

### 0.1 Input-Schema
```yaml
claim: <string>                   # die Aussage die gehaertet werden soll
context: <string>                 # Quelle, Domaene, warum wichtig
aussage_typ: <enum>               # Pflicht, siehe meta-validation-portfolio
  - empirisch_fakt
  - math_identitaet
  - theorie_modell
  - artefakt_integritaet
  - session_uebergang
  - meta_aussage
  - isomorphie_uebertragung
ziel_verdict: <enum>              # was erreicht werden soll
  - CONDITIONAL
  - STATISTICAL-STABLE
  - CROSS-LLM-SIMULATION-HARDENED
  - HARDENED
  - FIXPUNKT-HARDENED
stakeholder: <list>               # Martin, Instanz-A, ...
rho_hebel: <string>               # geschaetzter EUR-Wert pro Jahr
```

### 0.2 Ordnungs-Klassifikation (5-Ordnungs-Kristall)
- **E1** — Objekt (Welt-Fakt, Messwert, Daten)
- **E2** — Wissen ueber Wissen (Validierungs-Methode)
- **E3** — Methoden-Audit (wie pruefen wir Methoden)
- **E4** — Audit-Audit (wie bewerten wir Methoden-Pruefung)
- **E5** — Struktur-Fixpunkt (Meta-Stack-Architektur selbst)

Pflicht: `meta-ebene: E1|E2|E3|E4|E5` im Frontmatter der Output-Datei.

### 0.3 Pre-Gate (ueberspringt Wargame wenn unnoetig)
- Claim ist triviale Messung → SKIP (Verdict: HARDENED-direkt via SHA/Quelle)
- Claim bereits HARDENED in Canon → SKIP (Verweis, kein neues Wargame)
- Claim ist K_0-/Q_0-relevant → **VOLLER LAUF** (Pflicht, kein Skip)

### 0.3b Claim-Wording-Drift-Scan (NEU v1.1.1 — METAOPS-LIVE-001 Bug-2)

Vor Phase 1 pruefen ob Claim-Wording von Kristall-Version abweicht:

```bash
# Pseudo-Code
kristall_text = read("META-LERN-KRISTALL-5-ORDNUNGEN-SUPER-SYSTEM.md")
kern_tokens = extract_content_words(claim)  # Stop-Word-frei
matches = []
for token in kern_tokens:
    if token in kristall_text:
        matches.append(token)
if len(matches) >= 3:
    # Wahrscheinlich Kristall-Variante
    similar_line = find_closest_kristall_line(claim)
    if levenshtein(claim, similar_line) < 0.3:
        WARN("Claim-Shape-Drift: Wording weicht ab von Kristall-Referenz")
        # Protokolliere both: original-Kristall-Wording, Input-Claim-Wording
        # Phase 4 Verdict-Matrix behandelt beide separat
```

**Konsequenz:** Bei Drift-Detection werden **zwei** Claims gehaertet:
1. Der Input-Claim (wie gegeben)
2. Die Kristall-Referenz-Variante

Verdict-Output in Phase 5 dokumentiert beide → Meta-Learn-Signal ob Schaerfung gerechtfertigt.

---

## PHASE 0.5 — Fork-Pattern-Check (nur wenn Instanz-Fork)

**Trigger:** Neue Claude-Instanz bootet aus Boot-Paket, bevor sie Claims haertet.

**Quelle:** METADD-Handoff-Analyse 2026-04-18 (11/11 Ueber-Claim-Quote bei Predecessor-Sessions aufgedeckt).

### 0.5.1 — Boot-Paket-Validator (8 Pflicht-Elemente)

Pruefe dass das Fork-Boot-Paket diese 8 Elemente enthaelt:

| # | Element | Kriterium | Source-Validation |
|---|---------|-----------|-------------------|
| 1 | **Inertia-Ankuendigung** | "Du bootest NICHT als Wartender" oder aequivalent | Boot-Paket §ERSTE AKTION nicht leer |
| 2 | **Predecessor-Anti-Patterns** | min. 3, max. 7, im Ergebnis-Format (nicht Reasoning) | mindestens 3 x "Was X falsch gemacht hat / Was du tust" |
| 3 | **Konkrete Mission-Liste** | priorisiert mit Zeit-Schaetzung (nicht abstract) | min. 3 Missionen, jede mit Time-Budget |
| 4 | **Eskalations-Regeln** | K_0/Q_0-Liste explizit | "K_0-ESKALATIONS-PFLICHT" Sektion vorhanden |
| 5 | **Counter-Lane-Disjunktheit** | Fragment + Blueprint Ranges exklusiv | F-Range + B-Range angegeben, Kollisions-Check mit REGISTRY |
| 6 | **Phronesis-Stapel** | priorisiert fuer Idle-Zeit | min. 3 Items, sortiert nach rho/EUR |
| 7 | **Tool-First-Hierarchie** | welches Tool zuerst (Codex vs Browser etc.) | "Cross-LLM-Real first" oder aequivalent |
| 8 | **Tief-ueber-Breit-Mindset** | EINE Session, nicht 4 parallele | "Du bist EINE BREITE SESSION" oder aequivalent |

**Bei <8 Elementen erfuellt:** ABORT Fork. Boot-Paket nachbessern (Architekt ueberschreibt bzw. Predecessor-Session ergaenzt).

### 0.5.2 — Token-Budget-Analyse

Messe (oder schaetze):
- **B_total**: Context-Budget der Fork-Session (typisch 400K fuer Opus-Fork, 1M fuer Haupt-Session)
- **B_boot**: Tokens des Boot-Paket-Reads (Target: 3-5% von B_total)
- **B_rules**: Tokens aller Pflicht-Rules-Reads (Target: 3-5%)
- **B_context**: Tokens der Context-Dokumente (Target: 5-10%)
- **B_input_total = B_boot + B_rules + B_context** (Ziel: 15-20% von B_total)

**Validierung:**
- `B_input_total < 10% von B_total` → UNTER-BRIEFED. Erhoehe Context-Tiefe (fuege Rules hinzu).
- `B_input_total > 25% von B_total` → UEBER-BRIEFED. Streiche redundante Dokumente.
- `15% <= B_input_total <= 20%` → OPTIMAL (METADD-benchmarked).

### 0.5.3 — Persistenz-Pflicht-Check (Ergebnis vs. Reasoning)

Pre-Session-Ende-Checkliste fuer **aktuelle Session** (nicht Fork-Target):

- [ ] Ergebnis-Strukturen aller Arbeiten persistiert? (Decision-Cards, Cross-LLM-Files)
- [ ] Anti-Patterns dieser Session dokumentiert? (fuer naechsten Fork nutzbar)
- [ ] Action-Log-Eintraege vollstaendig?
- [ ] Phronesis-Stapel-Rest persistiert?
- [ ] Counter-Lane-Aenderungen in BEACON + REGISTRY?

**Nicht-Pflicht (optional, best-effort):**
- Reasoning-Weg-Zusammenfassung (Theorem 5.3: ~100% Verlust, akzeptiert)
- Interne Debatten zwischen Alternativen
- Parallel-Session-Koordinations-Trails

### 0.5.4 — Fork-Pattern-Verdict

| Outcome | Action |
|---------|--------|
| 8/8 Elemente + Token-Budget OPTIMAL + Persistenz-Pflicht erfuellt | PROCEED zu Phase 1 |
| 7/8 Elemente | WARN + PROCEED (dokumentiere Luecke) |
| <7 Elemente oder Token-Budget zu klein | ABORT + Boot-Paket-Revision-Pflicht |
| Persistenz-Pflicht verletzt bei Vor-Session | BLOCK Fork bis Vor-Session nachpersistiert |

### 0.5.5 — Output

- Pruef-Log in `branch-hub/audit/fork-pattern-checks.jsonl` appenden:
  ```json
  {"ts":"<iso>","fork_id":"<instanz-name>","parent":"<predecessor>","elements_ok":<n>/8,"budget_ok":<bool>,"verdict":"PROCEED|WARN|ABORT|BLOCK","notes":"..."}
  ```

### 0.5.6 — Wann Phase 0.5 skip

- Wenn die aktuelle Session KEIN Fork ist (direkter Martin-Auftrag in existierender Session): SKIP.
- Wenn Claim triviale E1-Messung: SKIP Phase 0.5 + Phase 1-3 (siehe Pre-Gate §0.3).

### 0.5.7 — SAE-Isomorphie

SAE v8 hat isomorphen Check in `learning/agent_bootstrap.py`: `validate_bootstrap_package()` prueft 8 Invarianten bevor Agent-Instanz zur Trinity promoviert wird. Meta-Harness-Archon Phase 0.5 ist dasselbe auf Session-Ebene.

---

## PHASE 1 — 4-Team-Wargame (Red/Blue/Purple/Gray)

### Team-Rollen

**Red (Falsifier) — 3-5 Angriffe:**
- Sucht Widersprueche, Edge-Cases, logische Luecken, Goedel-Grenzen
- Pattern: "Was bricht diesen Claim?" "Wo ist die schwaechste Annahme?"
- Tool-Input: Popper-Falsifikation + Quine-Holismus

**Blue (Affirmer) — 3-5 Verteidigungen:**
- Stuetzt mit Evidenz, Systematik, Math-Stringenz
- Pattern: "Welche Daten/Beweise untermauern?"
- Tool-Input: Cross-LLM-Konsens + formaler Beweis (wenn moeglich)

**Purple (Synthesizer) — 1 Synthese:**
- Integriert Red+Blue zu staerkerer Version des Claims
- Pattern: "Was ist die robuste Variante nach Integration?"
- Output: verfeinerter Claim oder PARTIAL-REJECT mit Patch

**Gray (Outsider) — 2-3 Perspektiven:**
- Paradigma-Wechsel, Querdomaenen-Sicht, Meta-Framing
- Pattern: "Wie wuerde Japanische/Buddhistische/Kybernetische Tradition denken?"
- Verhindert Zirkularitaet und Group-Think

### Wargame-Runden (3-Runden-Prinzip)
- Runde 1: je 2 Punkte pro Team, Quick-Draft
- Runde 2: je 2 Punkte pro Team, Tiefer-Angriff/Verteidigung
- Runde 3: Purple-Integration + Gray-Abschluss-Perspektive

---

## PHASE 2 — Multi-Language-Prompting (30 EU-Sprachen) [CONDITIONAL v1.1.1]

### 2.0 Activation-Gate (NEU v1.1.1 — METAOPS-LIVE-001 Bug-1)

**Default:** SKIP bei `ordnung ∈ {E1, E2}`. Phase 2 kostet ~15 Min + multiple LLM-Calls. Fuer Objekt-Ebene-Claims (E1) ist der Nutzen marginal — die Cross-LLM-Validation in Phase 3 reicht typischerweise.

**Activation-Bedingungen (mindestens eine muss erfuellt sein):**
- `ordnung ∈ {E3, E4, E5}` (Meta-Ebenen, wo linguistische Korpus-Diversitaet Bias bricht)
- Phase 1 Gray-Team hat kulturelle/traditionelle Divergenz signalisiert
- Claim hat explizite interkulturelle Dimension (z.B. Ethik, Governance, Werte)
- Ziel-Verdict ist HARDENED oder besser UND mindestens E2
- Martin fordert explizit (`multi-lang: force` Parameter)

**Wenn Phase 2 SKIP:** vermerke in Run-Log `phase_2_skipped: "reason=E1_sufficient_cross_llm"`.

### Rationale (aus NLM-Chats-Destillat)
*"Verschiedene Sprachen aktivieren unterschiedliche Trainingskorpora und kulturelle Denkmodelle. Multilinguales Prompting eliminiert blinde Flecken."*

### 6-Cluster-Architektur (30 Sprachen)

| Cluster | Sprachen | Repraesentant | Denk-Tradition |
|---------|----------|---------------|----------------|
| **Germanisch** (6) | DE, EN, NL, DA, SV, NO + IS | DE | Praezision, Analytik |
| **Romanisch** (7) | FR, ES, IT, PT, RO, CA + GA (Celtic) | FR | Klarheit, Diskurs |
| **Slawisch** (9) | PL, CZ, SK, RU, UA, BG, HR, SR, SL | PL | Kollektiv, Struktur |
| **Finno-Ugrisch** (3) | FI, HU, ET | FI | Agglutinativ, Kontextreich |
| **Baltisch** (2) | LV, LT | LV | Archaik, Prozessual |
| **Sonderfaelle** (3) | GR, TR, MT | GR | Philosophie-Tradition |

**Gesamt: 30 Sprachen** (IS, CA, GA zaehlen zu ihren Clustern, MT separat als Semitic-Indo-European-Hybrid).

### Prompting-Protokoll
1. Master-Prompt in DE formulieren
2. **Cluster-Representative-Prompt** (1 pro Cluster, 6 insgesamt): DE, FR, PL, FI, LV, GR
3. Pro Cluster-Rep: an jeweiligen LLM abschicken (mehrsprachig faehig)
4. Antworten zurueck → semantisches Clustering
5. **Konvergenz-Score**: wenn >=4/6 Cluster gleichen Kern-Claim bestaetigen → STATISTICAL-STABLE
6. Wenn zusaetzlich externe Ankerung (Daten/Beweis) → HARDENED

### Beispiel-Prompt-Template (fuer Gray-Team)
```
[DE] Pruefe folgende Aussage unter deutscher analytischer Tradition: <claim>
[FR] Examinez sous tradition francaise discursive: <claim>
[PL] Sprawdz pod slowianska perspektywa zbiorowa: <claim>
[FI] Arvioi kontekstirikkaasta nakokulmasta: <claim>
[LV] Parbaudi arhaiski-prociesalaja pieeja: <claim>
[GR] Εξετάστε υπό ελληνική φιλοσοφική παράδοση: <claim>
```

Multi-Language ist **Gray-Team-Verstaerker** — bricht Cross-LLM-Bias durch Korpus-Diversitaet.

---

## PHASE 3 — Cross-LLM-Validation

### Tier 1: Codex-MCP (primary, Auth live)
- Tool: `codex exec --skip-git-repo-check "<prompt>"`
- Rolle: zweite Perspektive (GPT-5), adversarial-Fact-Check
- Limit: ~300 Worte pro Call, ~100k Token intern, Web-Search-faehig

### Tier 2: Web-UI-Multi-LLM (Fallback + Cross-Model)
- Tool: Skill `multi-llm-parallel` (Martin-in-Loop)
- LLMs: Grok-Ultra, Perplexity-Ultimate, Copilot-Pro+, ChatGPT-Web, Claude-Opus-4.6
- Wann: bei E3+-Claims die volle HARDENED wollen

### Tier 3: Claude-Self-Fork via Agent-Tool
- Neuer Claude-Session-Fork mit nur dem Claim, ohne Kontext (Agent-Tool-Subagent)
- Verhindert Self-Confirmation-Bias im gleichen Modell
- Nicht voll-unabhaengig (gleiche Opus-Gewichte), aber fresh-context eliminiert Primary-Session-Bias

### Tier-Mix-Strategien (NEU v1.1.1 — METAOPS-LIVE-001 Bug-3)

**Empfohlene Muster nach Claim-Typ (rho-optimiert):**

| Claim-Typ | Empfohlener Mix | Dauer | Kosten | Verdict-Cap |
|-----------|----------------|-------|--------|-------------|
| E1 trivial | Tier 1 allein | 3 Min | 0.1 EUR | HARDENED |
| E1 K_0-nah | **Tier 1 + Tier 3 parallel** | 15 Min | 0.3 EUR | HARDENED |
| E2 Meta | Tier 1 + Tier 3 + Phase 2 | 30 Min | 0.8 EUR | HARDENED |
| E3 Methoden-Audit | Tier 1 + Tier 2 (Martin) | 60 Min | 2 EUR | 2OF3-HARDENED |
| E4 Audit-Audit | Tier 1 + Tier 2 + Tier 3 + Phase 2 | 90 Min | 3 EUR | SIM-HARDENED |
| E5 Fixpunkt | Tier 2 voll + Phase 2 voll + Martin-Phronesis | 2h+ | 5 EUR | FIXPUNKT-HARDENED |

**Ur-Pattern aus METAOPS-LIVE-001:** Tier 1 (Codex GPT-5) + Tier 3 (Self-Fork) parallel = **echte 3-LLM-Perspektive** ohne Browser-Kosten. Optimal fuer E1-K_0-Claims.

**Anti-Mix:** Tier 1 + Tier 3 ohne Primary = nur 2 Instanzen desselben Modells. Primary muss IMMER als dritte Stimme dabei sein (Orchestrator-Rolle).

### Cross-LLM-Konsens-Regel (aus rules/cross-llm-simulation.md)
- 4/7-Regel (4 von 7 LLMs stimmen zu → VALIDATED)
- Bei Meta-Ebene E4+: Simulation-Hardened max (korrelierter Bias)
- Cross-Path-Invariance (G8): 2 verschiedene Audit-Pfade, gleiches Verdict

---

## PHASE 4 — Verdict-Matrix (Integration G1-G14)

### Verdict-Stufen (aus rules/meta-stack-fixpunkte.md FIXPUNKT-1 Update)

| Stufe | Kriterium | Beispiel |
|-------|-----------|----------|
| **REJECTED** | G2 oder G3 oder G10 oder G11 verletzt | Dogmatisch, trivial, Ebenen-Konflikt |
| **CONDITIONAL** | G1+G2+G3+G6 erfuellt, kein Cross-LLM | Single-Model-Konsistenz |
| **STATISTICAL-STABLE** | Cross-LLM allein (ohne externe Ankerung) | Mehrheits-Beleg, aber Korrelationsrisiko |
| **CROSS-LLM-SIMULATION-HARDENED** | G1-G7 + G4 empirisch, Single-Instanz-Simulation | Einzel-Modell-Multi-Perspektive |
| **CROSS-LLM-2OF3-HARDENED** | G1-G12 + >=2 divergente Modelle | Mindest-Cross-Model |
| **HARDENED** | G1-G14 + 3+ Modelle + externe Ankerung | Volles Goldstandard |
| **FIXPUNKT-HARDENED** | Strukturell-logisch zwingend, selbst-konsistent | E5-Fixpunkt |
| **HARDENED-PRODUCTION** | HARDENED + Produktions-Stichprobe + externer Benchmark | Meta-Gold |

### Per-Ordnung Max-Verdict (Asymmetrie FIXPUNKT-1)
- E1 → HARDENED oder HARDENED-PRODUCTION
- E2 → HARDENED bei externer Ankerung + Cross-LLM
- E3 → CONDITIONAL default, HARDENED pragmatisch (3-Monats-Messung)
- E4 → max CROSS-LLM-SIMULATION-HARDENED, selten CROSS-LLM-2OF3-HARDENED
- E5 → FIXPUNKT-HARDENED nur fuer 4 strukturell zwingende Fixpunkte

### Fixpunkt-Check (Pflicht)
Vor Canon-Aufnahme: pruefe dass Claim keinen der 4 E5-Fixpunkte verletzt:
- FIXPUNKT-1: Ebenen-Asymmetrie → max-Verdict plausibel zur Ordnung
- FIXPUNKT-2: Ebenen-Kollaps-Verbot → Meta-q nicht in Objekt-q (Zwei-Kanal-Regel)
- FIXPUNKT-3: Pragmatisches Akzeptanz-Kriterium → Goodhart-Robustheit getestet
- FIXPUNKT-4: Endlichkeit-Meta-Stacks → keine E6+-Inflation (ausser begruendet)

---

## PHASE 5 — Persistenz

### Output-Artefakte (je nach Verdict)

**Bei HARDENED oder besser:**
- Decision-Card `docs/decision-cards/<claim-slug>.md` (1 Seite)
- Fragment-Map-Eintrag `areas/family/Subnautica-Fragment-Map-Ergaenzung-*.md` (F-Nummer)
- Blueprint wenn >=3 Cross-Refs (B-Nummer)

**Bei CONDITIONAL oder CROSS-LLM-SIM-HARDENED:**
- Finding `branch-hub/findings/<claim>-WARGAME-<datum>.md`
- 30-Tage-Review-Deadline (Deployment-Pflicht per meta-calibration.md §Regel 8)

**Bei REJECTED:**
- Dokumentation im Audit-Log + SUPERSEDED-Kennung
- Learning-Pattern in `branch-hub/audit/wargame-patterns.jsonl`

### Action-Log-Pflicht (alle Runs) — v1.1.1 Dual-Verdict-Schema

```jsonl
{
  "ts":"<iso>","skill":"meta-harness-archon","version":"1.1.1",
  "run_id":"<branch>-LIVE-<nnn>","claim_hash":"<sha>",
  "claim_original":"<text>",
  "claim_revised":"<text or null>",
  "ordnung":"E?",
  "verdict_original":"<verdict>",
  "verdict_revised":"<verdict or null>",
  "claim_revision_notes":"<was wurde geaendert und warum>",
  "teams":[...],"languages_used":[...],"cross_llm_tier":[1,2,3],
  "llms_used":["claude-opus-primary","gpt-5.4-via-codex",...],
  "consensus":"<n>/<m>_REJECT_original_<n>/<m>_ACCEPT_revised",
  "duration_min":<n>,
  "rho_estimate_eur_j":"<low-high>",
  "decision_card":"<path>"
}
```

**Begruendung Dual-Verdict (NEU v1.1.1 — METAOPS-LIVE-001 Bug-4):**

Ein Claim kann original REJECTED sein, aber in revidierter Form HARDENED — das ist ein wertvolles Lern-Signal ueber Claim-Sharpening. Das alte Single-Verdict-Schema hat diese Information verloren.

Beispiel aus METAOPS-LIVE-001:
- Original: "Half-Kelly ist optimal" → REJECTED (Verbietet "optimal")
- Revised: "Half-Kelly ist Heuristik, Optimum ist Merton+CPPI" → 2OF3-HARDENED

**Output-Pflicht bei Dual-Verdict:**
- Decision-Card MUSS beide Verdicts + revision-notes dokumentieren
- Fragment-Map: nur revidierte Fassung bekommt F-Nummer (nicht die abgelehnte)
- Canon-Aufnahme: nur revidierte Fassung

---

## PHASE 6 — Self-Improvement (Meta-Harness-Loop)

### Monatliche Evolution (via scheduled-task `meta-harness-archon-evolve`)
1. Scan `audit/wargame-patterns.jsonl` letzte 30 Tage
2. Extrahiere:
   - Welche Red-Angriffe haben *nie* getroffen → Anti-Pattern (aus Red-Pool entfernen)
   - Welche Gray-Perspektiven haben *oft* entscheidend beigetragen → Pattern-Bump
   - Welche Multi-Language-Cluster haben bei welchen Claim-Typen Bias-Bruch gebracht
3. Update SKILL.md **Patch-Level**: `version: 1.0.X` → `1.0.(X+1)`
4. Bei signifikanter Aenderung: **Minor-Bump** `1.X.0` → `1.(X+1).0`
5. Audit-Log in `branch-hub/audit/meta-harness-archon-evolution.log`

### rho-Gain-Messung (aus rules/meta-methodological-pragmatism.md)
- Per Claim-Typ: vorher/nachher rho vergleichen
- Wenn Gain < 1.5x nach 3 Monaten: Skill-Teil archivieren (SUPERSEDED)
- Wenn Gain > 3x: als Core-Pattern festigen

### Schwellwert fuer v2.0.0-Upgrade
- 100+ Runs erfolgt
- 3+ ehemals-REJECTED spaeter-HARDENED (oder umgekehrt)
- Multi-Language-Cluster um 3+ neue Sprachen erweitert (z.B. Asiatisch, Arabisch)
- Neue Verdict-Stufe eingefuehrt durch Community-Konsens

---

## PHASE 7 — Archon-Workflow-Persistence

### DAG-Struktur (YAML)
Workflow-Datei: `branch-hub/.archon/workflows/meta-harness-archon.yaml`

Nodes:
1. `crux-gate` — CRUX-Alignment-Check (rejected wenn gegen rho)
2. `intake-classify` — Input + E1-E5-Klassifikation
3. `pre-gate` — Skip-Logik
4. `team-red` (parallel mit team-blue)
5. `team-blue`
6. `team-purple` (depends-on: team-red, team-blue)
7. `team-gray`
8. `multi-language` (parallel mit team-gray)
9. `cross-llm-tier` (Tier-1-Default, Tier-2/3 wenn E3+)
10. `verdict-matrix`
11. `fixpunkt-check`
12. `persist-artefakte`
13. `action-log`
14. `evolve-pattern` (async, laeuft nach Persist)

### Hard-Stops
- Fixpunkt-Verletzung → Alarm + Audit + Prozess-Stop
- Budget-Ueberschreitung (>5 EUR pro Lauf) → Abbruch
- Cross-LLM-Konsens <3/7 bei E4+-Claim → FORCE-REJECTED

---

## Pentagon-Verfahren (Einbettung)

Jeder Run folgt Pentagon:
1. **Plan** — Phase 0 Intake
2. **Spec** — Phase 1 Teams-Setup
3. **Implement** — Phase 2-3 Wargame + Multi-Lang + Cross-LLM
4. **Test** — Phase 4 Verdict-Matrix + Fixpunkt-Check
5. **Refine** — Phase 6 Self-Improvement

---

## CRUX-Gate (2-Wargame-Regel)

Jede neue Methodik/Quelle muss 2 Wargames bestehen:
1. **Adversarial** (Red+Gray Phase 1)
2. **CRUX-Alignment** — foerdert der Claim rho * L ueber T_life?

Wenn 2/2 → HARDENED-Kandidat
Wenn 1/2 → CONDITIONAL
Wenn 0/2 → REJECTED

---

## Anti-Patterns (Pflicht-Check)

- **Meta-Upsell**: "Alle LLMs stimmen zu auf E4" = HARDENED → FORBIDDEN (G3)
- **Goodhart-Meta**: rho-Gain-Optimierung als Ziel → VERARMUNG-ALERT (G14)
- **Ebenen-Kollaps**: Meta-Score in Objekt-Entscheidung → FIXPUNKT-2-Verletzung
- **E6+-Inflation**: neue Meta-Ebene ohne Irreduzibilitaet → FIXPUNKT-4-Verletzung
- **Wahrheits-Overclaim auf E3-E5**: ontologische Wahrheit statt pragmatischer Gueltigkeit → FIXPUNKT-3
- **Single-Language-Blindspot**: nur DE/EN → Cluster-Diversitaet verletzt
- **Zirkulaere Self-Confirmation**: Claude-Alone im gleichen Session-State → FORBIDDEN
- **Rauschen statt Signal**: Wargame ohne klare Claim-Identifikation → ABORT

---

## Stakeholder-Regeln (aus Leadership-Rules)

- **K_0-relevant** → Martin-Phronesis-Pflicht (L13)
- **Q_0-relevant** → Familie + Martin-Pflicht
- **Meta-Meta-Aenderung (E5-Fixpunkt)** → nur Martin-Phronesis
- **Alles andere** → Architekt-autonom (Welle 7)

---

## Beispiel-Use-Cases

### Use-Case 1: Meta-Kristall-E5-Fixpunkt-Validierung
- Claim: "Pragmatische Gueltigkeit > Wahrheit auf Meta-Ebene"
- Ordnung: E5
- Teams: alle 4 (Red/Blue/Purple/Gray)
- Multi-Lang: 6 Cluster, Fokus auf Gray (Japanisch, Buddhisten-Tradition zusaetzlich)
- Cross-LLM: Tier 2 (Web-UI Martin-in-Loop)
- Ziel-Verdict: FIXPUNKT-HARDENED

### Use-Case 2: Hotel-Operation-KPI-Validierung
- Claim: "Cooperative-rho ab 85% Occupancy"
- Ordnung: E1
- Teams: nur Red+Blue (E1 braucht keine Gray/Purple-Tiefe)
- Multi-Lang: optional
- Cross-LLM: Tier 1 (Codex)
- Ziel-Verdict: HARDENED

### Use-Case 3: Kapital-Allokations-Entscheidung (K_0-nah)
- Claim: "Half-Kelly statt Full-Kelly"
- Ordnung: E1-E2-Hybrid (Modell + Evidenz)
- Teams: alle 4 + Martin-Review
- Multi-Lang: 6 Cluster (Finanz-Traditionen differenzieren)
- Cross-LLM: Tier 2 (volle Paranoia bei K_0)
- Ziel-Verdict: HARDENED-PRODUCTION

---

## Integration mit anderen Skills

- **`meta-learn-kristall-audit`** — ruft meta-harness-archon fuer jeden neuen Claim
- **`cross-llm-real`** — wird als Phase-3-Tier-1-Provider genutzt
- **`multi-llm-parallel`** — wird als Phase-3-Tier-2-Provider genutzt
- **`4-team-wargame`** (DEPRECATED, integriert in Phase 1) — Redirect-Header einfuegen
- **`wargame`** (v7, bleibt fuer strategische Initiativen, NICHT Claim-Haertung)

---

## Lambda-Honesty

Dieser Skill ist selbst ein **E3-Methoden-Audit-Framework** (Wargame-Methoden-Portfolio). Sein Verdict ist pragmatisch: **funktioniert oder nicht**, gemessen ueber 3-Monats-rho-Gain pro Claim-Typ.

Nicht-Anspruch: ontologische Wahrheits-Maschine. Ja-Anspruch: robuste Entscheidungs-Unterstuetzung unter Selbst-Referenz.

---

## Revision

Patch-Level: kann Architekt autonom aendern (v1.0.X).
Minor-Bump (v1.X.0): braucht Cross-LLM-Validation (rule meta-harness.md §8b).
Major-Bump (vX.0.0): nur mit Martin-Phronesis (L13).

[CRUX-MK]
