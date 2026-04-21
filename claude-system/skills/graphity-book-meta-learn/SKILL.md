---
name: graphity-book-meta-learn
description: |
  Archon-Workflow-Skill fuer Graphity-Buchschreibe-Prozess. Multi-Category-Framework (C1-C7)
  mit kategorie-spezifischen Best-Practices. Nutzt 3 reproduzierbare Templates T1 (Zutaten-Matrix),
  T2 (Character-Psychogramm 18 Schichten), T3 (Figuren-Kapitel-Bogen).
  Triggers (run): "masterplan schreiben", "playbook bauen", "produktionsbibel", "/graphity-book"
  Triggers (category): "roman kapitel", "sachbuch argument", "mathebuch charakter", "verlagsbuch"
  Capability: 6-Phasen-Pipeline (Masterplan -> Playbook -> Kapitel-Draft -> Wargame -> Produktionsbibel -> PMO)
  mit Category-Router, Anti-Drift-Guard (11-Ebenen max), Cross-Reference-Index-Validator.
  NICHT: Fiktions-Generator ohne Kochrezept. Braucht Masterplan + Playbook als Input.
crux-mk: true
version: 1.1.0-live
meta-ebene: E3
origin: opus-4.7-MYZ-2026-04-19 post-Martin-Direktive-2 (150h Budget)
status: LIVE (17 Scripts deployed + 3 SQLite-Schemas + Pilot-Registry validiert + C1-C5-Template-Catalog komplett + Wave-3 Cross-LLM-2OF3-HARDENED)
depends-on:
  - rules/crux.md
  - rules/meta-governance-framework.md
  - Skill: meta-harness-archon (fuer Phase 4 Wargame-Haertung)
  - Python 3.10+ mit pyyaml (optional: spacy, nltk, sentence-transformers fuer V5)
---

# graphity-book-meta-learn [CRUX-MK]

## Wann nutzen

- Neues Buch-Projekt starten (Phase 1 Masterplan)
- Existierender Masterplan → Playbook ableiten (Phase 2)
- Playbook → Kapitel-Draft (Phase 3)
- Fertiger Kapitel-Draft → Wargame-Haertung (Phase 4)
- Kapitel-Wargame-Output → Produktionsbibel-Update (Phase 5)

NICHT fuer: Ad-hoc-Schreibwuensche, Blog-Posts, Social-Media-Content.

## Multi-Category-Routing (C1-C7)

Pro Buch-Projekt: Category-Classifier waehlt Best-Practice-Modul.

| Category | Trigger-Signale | Pipeline-Variante |
|----------|-----------------|-------------------|
| **C1 Roman** | Figuren + Plot + Ort | 11-Ebenen-Architektur, 3D-Matrix (Zutat×Figur×Kapitel) |
| **C2 Sachbuch** | Thesen + Argumente + Cases | Thesen-Graph, Argument-Ketten-Validator |
| **C3 Interaktiv** | Multi-Charakter + Didaktik + Aufgaben | Lernziel-Progression, Multi-Voice-Konsistenz |
| **C4 Verlags/Business-Doc** | KPIs + Governance + Board | McKinsey-Layout, Daten-Tabellen, Governance-Layer |
| **C5 Co-Autorschaft** | Mehrere Autoren + Meetings | Voice-Fingerprint-Diff, Meeting-Zyklus-Integration |
| **C6 Technisches-Manual** | Checklisten + Spec-Refs + Compliance | Prozess-Schritte, Cross-Spec-Validator |
| **C7 Meta/Rezeptions** | Quellen-Extraktion + Destillat | Isomorphie-Mapping, Quellen-Attribution |

## Architektur (Event-Driven, geerbt von archon-roadmap-orchestrator)

```
Phase-Event (masterplan-requested)
     │
     ▼
category_router.py (C1-C7 Classifier + Template-Selector)
     │
     ▼
pipeline/phase_<N>_<category>.py (36 Moduls: 6 Phasen × 6 Kategorien ohne C7-Phases 1-3)
     │
     ▼
template_engine.py (T1/T2/T3 + Kategorie-Varianten)
     │
     ▼
anti_drift_guard.py (max 11 Ebenen, Ebenen-Cursor, Sub-Prompt pro Ebene)
     │
     ▼
cross_ref_resolver.py (3D-Matrix-Validator, {{CRX:...}}-Placeholder)
     │
     ▼
kaestner_guardian.py (Stil-Invariante: <20 Worte/Satz, kein Filler)
     │
     ▼
wargame_gate.py (Phase 4, meta-harness-archon 4-Team, CONDITIONAL min)
     │
     ▼
Output (Markdown + DOCX via pandoc, Frontmatter + Cross-Refs aufgeloest)
```

## Pentagon-Ablauf

### Phase 1: PLAN (Masterplan v1)
- User-Input: Buch-Idee + Genre + Ziel-Laenge
- Category-Router klassifiziert (C1-C7)
- Template T1 (Zutaten-Matrix) wird befuellt: 5-15 Einfluesse
- Template T3 (Kapitel-Bogen) wird initialisiert: N Kapitel x grober Plot
- Output: `<buch>/masterplan_v1.md` (20-25k Worte)

### Phase 2: SPEC (Playbook)
- Masterplan v1 -> Analyse-Script identifiziert Luecken
- Masterplan v2 (erweitert mit fehlenden Ebenen)
- Pro Figur Template T2 (Character-Psychogramm, 18 Schichten)
- Pro Kapitel Template T3 befuellen (was passiert + innerer Zustand + dominanter Einfluss)
- 11-Ebenen-Matrix aufbauen (Kapitel × Ebene)
- Output: `<buch>/playbook.md` + `<buch>/11_ebenen_matrix.yaml`

### Phase 3: IMPLEMENT (Kapitel-Draft iterativ)
- Pro Kapitel: Komplett -> V2 -> FINAL -> ERWEITERT
- Dark-Factory `graphity-book-abschnitt-writer` uebernimmt Abschnitt-Generierung
- Cross-Ref-Placeholder werden eingesetzt, Resolver validiert
- Kaestner-Guardian blocked Style-Drift

### Phase 4: TEST (Wargame)
- Pro Kapitel: meta-harness-archon 4-Team (Red/Blue/Purple/Gray)
- CONDITIONAL-Schwelle: kein Kapitel published ohne bestandenes Wargame
- Patches werden iterativ eingebaut

### Phase 5: REFINE (Produktionsbibel)
- Alle finalen Kapitel in Produktionsbibel konsolidiert
- Cross-Ref-Index vollstaendig aufgeloest
- PMO-Layer (Phase 6): Board-Praesentation, Arithmetik, Governance

## Scripts-Interface (v1.0.0 LIVE, 16 Scripts)

### Build-Pipeline (Registry → SQLite → Chapter)

| Script | Zweck | CLI | Status |
|--------|-------|-----|--------|
| `parse_claude_conversations.py` | Chat-Export → K1-K5-MDs (ijson-Streaming 231MB) | `--input conversations.json --output dir/` | ✅ 169 Conv parsed |
| `yaml_to_sqlite.py` | Registry-YAMLs → SQLite 25 Tables + 12 Views | `--registry <dir> --db <sqlite>` | ✅ Pilot validiert |
| `resolve_crx.py` | CRX-Placeholder `{{CRX:ENTITY:FIGUR:KAP-N}}` Resolver | `--input <kap.md> --db <sqlite> --book <slug> --mode draft\|release` | ✅ 5/6 OK + BLOCK |
| `impact_report.py` | Entity-Change-Impact-Scanner | `--db <sqlite> --entity <id> --change-type renamed\|modified` | ✅ Temporal-Violations caught |

### Category + Anti-Drift (Typklassen statt flache Liste, Wave-1 Konsens)

| Script | Zweck | CLI | Status |
|--------|-------|-----|--------|
| `category_router_v2.py` | Bitmask K1-K5 + Overlays (Co-Author/Bundle/Biografisch) | `--input <masterplan.md> [--json]` | ✅ Hybrid-Support |
| `anti_drift_guard_v2.py` | Typklassen-Tier (default/narrative/business/didactic) + Sliding-Window 200T | `--check <file> --chapter-contract <yaml>` | ✅ Gemini-Sliding |
| `kaestner_guardian_v2.py` | Staffel-Cap (K1=22, K2=25, K3=18, K4=20, K5=20, K6=14) + Adjektiv-Fasten + Konkretheits-Index | `--check <file> --category K1 [--report-json]` | ✅ Kap-10 BLOCK 57, KI 0.977 |

### State-Machine + Kontrolle (E11 + E12 aus B401 v1.4)

| Script | Zweck | CLI | Status |
|--------|-------|-----|--------|
| `run_control_kernel.py` | Saga-FSM (claimed→generation_done→files_written→git_committed→state_applied), STOP.flag, Martin-Alert | `--run-id <id> --action start\|heartbeat\|commit` | ✅ Tier-2 |
| `context_injector.py` | State-Aware RAG (book_meta + active_figures + theses + chapter_contract + cross_refs) | `--book <slug> --chapter N --budget-tokens 4000` | ✅ Fallback |

### Wave-3 Voice/Versionierung/Scheduling/Isolation (Codex+Gemini 2OF3-HARDENED)

| Script | Zweck | CLI | Status |
|--------|-------|-----|--------|
| `voice_fingerprint.py` | V1 Burrows + V2 Syntax + V3 Six-Pillar + V4 Rolling, Fusion 0.20V1+0.30V2+0.25V3+0.15V4 | `--baseline \| --check \| --report --author X --category K1_narrativ --db <sqlite>` | ✅ Baseline built |
| `change_propagator.py` | 5-Stufen-FSM (ChangeSet→Invalidation→AutoReDraft-shadow→Manual→AtomicPromotion) | `--stage 1..5 --db <sqlite> --book <slug> [--masterplan-new <path>] [--revision-id <id>] [--promote]` | ✅ Stage-1 additive |
| `weekly_scheduler.py` | Review-Gated Knapsack (WIP_MAX=3, R_week hart, 60-Tag-DMS) | `--plan --db <sqlite> --week YYYY-MM-DD --review-budget 180` | ✅ 4 Kap geplant |
| `context_capsule.py` | Vector-Namespace-Isolation (Whitelist + Negative-List + NER-Diff) | `--build \| --check --db <sqlite> --book <slug>` | ✅ 7 Entities |

### Template-Engine (Skeleton-Generator)

| Script | Zweck | CLI | Status |
|--------|-------|-----|--------|
| `template_engine.py` | T1/T2/T3 Skeleton aus Leitfossil-Findings + Book-Context (SQLite) | `--category K1_narrativ --template T2 --book <slug> --db <sqlite>` | ✅ UTF-8-Fix |

## Kategorie-Leitfossil-Findings (Template-Catalog v1.0 komplett)

| Cat | Finding | Zeilen | Besonderheit |
|-----|---------|--------|--------------|
| **K1 Narrativ** | `MYZ00006-Templates-Cat-1-Roman.md` | ~1100 | 34 Zutaten + 18-Schichten-Charaktere + 22-Kap-Bogen |
| **K2 Argumentativ** | `MYZ00008-Templates-Cat-2-Business-Sachbuch.md` | 476 | 10 Gegenthesen + 18 Quellen + 3 These-Psychogramme (L=D×I) |
| **K3 Didaktisch** | `MYZ00009-Templates-Cat-3-Didaktisch.md` | 552 | 12 Lernziele Bloom + 4 Chars (Anton/Conny/Dana/Bernd) + 16-Kap + Phase-3.5 Begleit-Spiel |
| **K4 Operativ** | `MYZ00010-Templates-Cat-4-Operativ.md` | 646 | KPI-Matrix + Governance-Layer + Entscheidungs-Fluss (Verlags-Doc/Board) |
| **K5 Referenziell** | `MYZ00011-Templates-Cat-5-Referenziell.md` | 757 | Quellen-Attribution (20+) + 5 Destillat-Konzepte + Isomorphie-Map |

### Legacy / Superseded

| Script | Status |
|--------|--------|
| `category_router.py` (v1 YAML) | SUPERSEDED durch `_v2.py` (Bitmask) |
| `anti_drift_guard.py` (v1 flache Liste) | SUPERSEDED durch `_v2.py` (Typklassen) |
| `kaestner_guardian.py` (v1 global) | SUPERSEDED durch `_v2.py` (Staffel) |

## SQLite-Schema (25 Tables + 12 Views)

- `schemas/cross-reference-index.schema.sql` — entities, books, book_occurrences, edges, aliases, chapter_contracts, resolver_log, impact_reports + Views (v_temporal_violations, v_dominance_violations, v_chapter_refs, v_entity_chapters)
- `schemas/state-machine-extensions.schema.sql` — book_state, chapter_state, leases, runs, state_transitions, claims, story_assertions, task_history + Views (v_stuck_approvals, v_orphaned_runs, v_claims_unverified, v_story_inconsistencies)
- `schemas/wave3-extensions.schema.sql` — voice_baselines, voice_scores, book_revisions, chapter_invalidations, scheduler_runs, book_metrics, context_capsules, collision_checks + Views (v_voice_drift_alerts, v_active_schedule, v_book_priority, v_chapter_invalidation_status)

## Token-Guard-Integration

Alle Phasen durch `token_guard.py` (archon-roadmap-orchestrator):
- Pre: `--check` schaetzt cost_eur, blockt bei Ueberschreitung
- Post: `--record` loggt actual cost, rho_run
- Finalize: `--finalize` aggregiert, alert bei rho < 0

Budget pro Buch: 5-15 EUR Claude-Kosten, 500-2000 EUR Martin-Zeit-Opportunity.

## Cross-LLM-Pflicht

Pro kategorie-spezifische Best-Practice vor Canon-Aufnahme:
- Codex + Gemini Cross-LLM (Skill `cross-llm-real`)
- Verdict-Tier: mindestens CROSS-LLM-2OF3-HARDENED
- Belegung in `branch-hub/cross-llm/2026-MM-DD-graphity-<cat>-best-practice.md`

## Anti-Patterns

1. **11+ Ebenen pro Kapitel gleichzeitig** — LLM-Drift (Beleg: Martin-Direktive 2026-04-19 "ab 12-14 unsauber")
2. **Wargame-Skip** — Phase 4 ist Pflicht, nicht optional (Martin-Direktive "alles plus Wargames")
3. **Category-Override ohne Evidenz** — Classifier-Empfehlung nur bei gegenteiliger Martin-Phronesis uebersteuern
4. **Cross-Ref-Placeholder ohne Resolver-Check** — silent fail = Build-Fail
5. **Opus-Tokens fuer Boilerplate** — Sonnet/Haiku/Codex/Gemini fuer Templates, Opus nur fuer Phronesis

## rho-Bilanz (Ziel, zu validieren in Phase F Pilots)

- CM: 30-80k EUR pro Buch (Qualitaets-Gain + Zeit-Ersparnis)
- Lambda: 3-6 Buecher/Jahr
- OPEX: 10-40h Martin-Zeit pro Buch (statt 100-200h Manual)
- rho_jaehrlich: +135-260k EUR/J (siehe B401 150h-Plan)

## Falsifikations-Bedingung

Skill ist falsifiziert wenn:
- Pilot E2E (Phase F MYZ00030-32) zeigt Qualitaets-Verlust vs Martin-Manual
- Category-Router < 80% Classifier-Accuracy
- Anti-Drift-Guard false-positives > 20%
- Cross-Ref-Resolver Build-Fails > 5% bei validen Placeholders

[CRUX-MK]
