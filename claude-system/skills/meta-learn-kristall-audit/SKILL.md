---
name: meta-learn-kristall-audit
description: |
  Archon-Workflow (Tier 1) fuer regelmaessiges Audit des Meta-Lern-Kristalls (5 Ordnungen E1-E5).
  Prueft Claim-Inventar-Drift, Verdict-Stabilitaet, Ebenen-Kollaps, Fixpunkt-Verletzungen,
  Meta-Upsell. Produziert Decision-Card mit Audit-Ergebnis und Cross-LLM-Eskalations-Pakete.
  KEIN Dark-Factory (Meta-Ebene ist Q_0-relevant, Lambda 1/Monat, Martin-Approval Pflicht
  fuer Canon-Freigabe).
  Triggers (run): "audit meta kristall", "check meta learning", "fehlertyp-scan meta",
    "meta-kristall audit", "meta-drift check", "meta-lern-audit starten",
    "/meta-learn-kristall-audit".
  Triggers (status): "wann war letzter meta-kristall audit", "kristall-drift status".
  Capability: Iteriert ueber Canon-Claims in Meta-Lern-Kristall, klassifiziert E1-E5,
    prueft Drift seit letztem Audit, eskaliert verdaechtige Claims ueber 4-team-wargame,
    prueft Fixpunkt-Invarianten, generiert Cross-LLM-Prompt-Pakete fuer E3+-Claims,
    schreibt Decision-Card + Audit-Report.
crux-mk: true
version: 0.1.0
origin: opus-4.7-architekt-2-instanz-b-2026-04-18
archon-tier: 1
schedule: monatlich (1. des Monats 04:00, plus manueller Trigger)
decision-card: G:/Meine Ablage/Claude-Vault/docs/decision-cards/DF-Meta-Kristall-Audit.md
canonical-path: C:/Users/marti/.claude/skills/meta-learn-kristall-audit/SKILL.md
workflow-yaml: G:/Meine Ablage/Claude-Knowledge-System/branch-hub/.archon/workflows/meta-learn-kristall-audit.yaml
note: |
  Kanonischer Ort ist ~/.claude/skills/meta-learn-kristall-audit/ (siehe canonical-path).
  Diese Datei hier ist der Zweitkanal (branch-hub) gemaess meta-harness.md §8a und
  rules/vault-bridge.md (Skill-Provenienz). Martin muss diese Datei manuell nach
  ~/.claude/skills/meta-learn-kristall-audit/SKILL.md kopieren (Sandbox verhindert
  den direkten Write in ~/.claude/ durch Subagenten).
  Der Kristall selbst: Claude-Vault/areas/family/META-LERN-KRISTALL-5-ORDNUNGEN-SUPER-SYSTEM.md.
aktiviert: 2026-04-18 (Martin-Kopie abgeschlossen, METAOPS Trial-Run 2026-04-18 bestaetigt deployment-ready, 4 Minor-Bugs dokumentiert in branch-hub/findings/META-AUDIT-TRIAL-2026-04-18.md)
---

# /meta-learn-kristall-audit [CRUX-MK]

## Essenz

**Meta-Drift ist die gefaehrlichste Qualitaetserosion,** weil sie unsichtbar ist.
Das Meta-Lern-Kristall (5 Ordnungen E1-E5) braucht regelmaessiges Audit, sonst:
- E1-Claims werden durch neue Evidenz widersprochen, aber HARDENED-Status bleibt bestehen
- E3+-Claims werden faelschlich als "Cross-LLM-validated" gekennzeichnet (Meta-Upsell)
- Ebenen-Kollaps: Meta-q wird in Objekt-q gemischt (Goodhart-Meta)
- E5-Fixpunkte werden unbemerkt verletzt (Super-System-Integritaet bricht)

**Mit Audit:** monatlich 30-60 Min autonome Arbeit, 2 Martin-Entscheidungen (Canon-Freigabe),
strukturierter Report. Kein Auto-Merge.

## Wann nutzen

- **Monatlich** (default 1. des Monats 04:00 via Scheduled Task)
- **Nach jedem groesseren Lern-Ereignis** (neue Rule, neue Cross-LLM-Runde, neuer META-Eintrag)
- **Bei Verdacht auf Meta-Drift** (z.B. wenn ein Meta-Claim auf Objekt-Entscheidungen wirkt)

## Wann NICHT

- Wenn Martin < 30 Min Zeit hat (Canon-Freigabe braucht bewusstes Lesen)
- Wenn gleichzeitig aktiver Wargame-Sprint laeuft (Drift-Detection wird zu geraeuschvoll)
- **NIEMALS als Dark-Factory** (Meta-Ebene ist Q_0-relevant, Learning-Domain sakrosankt per M7)

## Pentagon-Ablauf

### Phase 1: PLAN -- Audit-Scope festlegen

Martin beantwortet 3 Fragen beim Start (bei manuellem Trigger; bei Scheduled: Defaults):
1. **Scope**: "voll" (default, alle 5 Ordnungen) / "E1-E2" (empirische Ebenen) / "E3-E5" (Meta-Ebenen)
2. **Zeitgrenze seit letztem Audit**: Default = letzter Eintrag in `audit/meta-kristall-audit-log.jsonl`
3. **Budget**: Default 20 Min LLM-Zeit (~80k Token), max 60 Min (~250k Token)

### Phase 2: SPEC -- Audit-Kriterien

Pro Audit werden **5 Drift-Typen** geprueft:

| # | Kriterium | Messung | Schwellwert |
|---|-----------|---------|-------------|
| 1 | Claim-Inventar-Drift | Anzahl neuer/geaenderter Claims seit letztem Audit | > 0 neue Claims triggert Wargame |
| 2 | Verdict-Stabilitaet | HARDENED-Claims mit neuer widersprueechlicher Evidenz | Jeder widersprueechliche Fund = Wargame |
| 3 | Ebenen-Kollaps | Meta-Claim (E3+) in Objekt-Entscheidung (E1) zitiert | 1 Verletzung = STOP + Martin-Alert |
| 4 | Fixpunkt-Verletzung | 4 E5-Fixpunkte respektiert? | Jede Verletzung = CRITICAL |
| 5 | Meta-Upsell | "alle LLMs stimmen zu" faelschlich als HARDENED auf E3+ | Verdict-Downgrade auf CROSS-LLM-SIM-HARDENED max |

**Canon-Kandidaten (bei Aufnahme in Canon: Martin-Approval Pflicht):**
- Neue Claims mit Verdict >= CROSS-LLM-SIM-HARDENED
- Revidierte Verdicts (HARDENED -> CONDITIONAL nach Widerspruch)
- Neue Rules aus Eigenfehler-Catalog (BIAS-Catalog)

**Nicht-auditierbar (sakrosankt, nie automatisch veraendert):**
- Die 4 E5-Fixpunkte selbst (nur Martin kann sie aendern)
- CRUX-Invariante (`rules/crux.md`)
- CLAUDE.md

### Phase 3: IMPLEMENT -- 7-Node-DAG

**Node 0 `crux-gate` (Bash):**
- Pruefe CRUX-First-Boot (rules/crux-first-boot.md geladen)
- Pruefe Martin-Zeitfenster oder Scheduled-Trigger
- Pruefe `META-LERN-KRISTALL-5-ORDNUNGEN-SUPER-SYSTEM.md` existiert

**Node 1 `collect-claims` (Bash + Glob):**
- Glob alle Canon-Dateien mit Meta-Ebenen-Tags:
  - `Claude-Vault/areas/family/META-LERN-KRISTALL-*.md`
  - `branch-hub/findings/LEARNING-*.md`
  - `branch-hub/findings/LERNEN-*.md`
  - `branch-hub/findings/META-*.md`
- Extrahiere Frontmatter + Claim-Listen (regex auf "HARDENED|CONDITIONAL|REJECTED")
- Output: `$ARTIFACTS/claim-inventar.json`

**Node 2 `classify-ordnung` (Claude Haiku, 1 Call):**
- Fuer jeden Claim: E1/E2/E3/E4/E5-Klassifikation nach Schema
- Output: `$ARTIFACTS/claim-classified.json`

**Node 3 `check-drift` (Bash deterministisch):**
- Vergleiche `claim-classified.json` mit letztem Audit-Snapshot aus `audit/meta-kristall-audit-log.jsonl`
- Identifiziere: neue Claims, geaenderte Verdicts, geloeschte Claims
- Output: `$ARTIFACTS/drift-report.json`

**Node 4 `4-team-wargame` (Claude Opus/Sonnet, 1 Call pro verdaechtigem Claim, max 5):**
- Fuer jeden neuen/verdaechtigen Claim: Red/Blue/Purple/Gray-Wargame
- Ruft `4-team-wargame`-Skill auf (falls vorhanden) oder Inline-Fallback
- Limitiere auf TOP-5 Kandidaten (nach Risiko-Score) um Budget zu schuetzen
- Output: `$ARTIFACTS/wargames/<claim-id>.json`

**Node 5 `fixpunkt-check` (Claude Sonnet, 1 Call):**
- Pruefe die 4 E5-Fixpunkte auf Verletzung:
  - FIXPUNKT-1: Meta-Ebenen-Asymmetrie (gilt sie noch?)
  - FIXPUNKT-2: Ebenen-Kollaps-Verbot (Meta-q nicht in Objekt-q)
  - FIXPUNKT-3: Praktische Gueltigkeit > Wahrheit auf Meta-Ebene
  - FIXPUNKT-4: Endlichkeit der Meta-Stacks (5 Ordnungen reichen)
- Scanne Action-Log + Decision-Logs der letzten 30 Tage nach Verletzungen
- Output: `$ARTIFACTS/fixpunkt-check.json`

**Node 6 `cross-llm-eskalation` (Bash + Claude Sonnet, bedingt):**
- Pro E3+-Claim ohne CROSS-LLM-SIM-HARDENED-Verdict: generiere Prompt-Paket
  - 4 Perspektiven: Grok / Gemini / GPT-5 / Claude-Opus
  - Jeweils 200-500 Wort Prompt mit Claim + Kontext
- Speichere in `$ARTIFACTS/cross-llm-prompts/<claim-id>.md` zur Martin-Verwendung
- NICHT auto-ausfuehren (per `rules/cross-llm-simulation.md` Regel 4: echter Cross-LLM
  braucht Martin-Koordination)

**Node 7 `report` (Claude Sonnet, 1 Call):**
- Schreibe Decision-Card nach `Claude-Vault/docs/decision-cards/DF-Meta-Kristall-Audit-<DATE>.md`
- Schreibe Audit-Report nach `branch-hub/findings/META-KRISTALL-AUDIT-<DATE>.md`
- Inhalt: 5 Drift-Typen mit Findings + Martin-Entscheidungs-Liste (max 2 pro Audit)
- Append JSONL-Eintrag in `branch-hub/audit/meta-kristall-audit-log.jsonl`

### Phase 4: TEST -- Smoke + Gate

**Smoke-Test vor jedem Lauf:**
1. `META-LERN-KRISTALL-5-ORDNUNGEN-SUPER-SYSTEM.md` existiert und ist lesbar
2. Audit-Log existiert oder wird initialisiert (erster Lauf)
3. `4-team-wargame`-Skill ist verfuegbar (oder Fallback auf Inline-Wargame)
4. Decision-Card-Ordner existiert

**Hard-Stop (Audit wird abgebrochen):**
- Fixpunkt-Verletzung entdeckt: SOFORT STOP + Martin-Alert (`branch-hub/inbox/to-martin.md`)
- Budget ueberschritten: STOP, Teil-Report schreiben
- `META-LERN-KRISTALL-*`-Datei enthaelt Write-Error oder ist leer: STOP, Integritaets-Alert

**Human-in-the-Loop (Martin-Approval Pflicht):**
- Canon-Freigabe neuer Claims (aus Node 4 Wargame-Verdict HARDENED)
- Verdict-Revision bestehender Claims (HARDENED -> CONDITIONAL)
- Neue Rule-Vorschlaege aus BIAS-Catalog-Drift

### Phase 5: REFINE -- Post-Lauf

**Nach Martin's Reviews:**
- Pro genehmigter Canon-Aenderung: Write in `META-LERN-KRISTALL-*.md` (SEPARATE Session!)
- Pro abgelehnter Aenderung: Vermerk in Audit-Report "Martin-Decision-<Datum>: REJECTED, Grund X"
- Bei Fixpunkt-Verletzung: Sofort-Patch geschrieben, dann Martin-Review

**Lern-Loop (meta-harness §8a):**
- Nach 3 Laeufen: Statistik in `learnings/meta-kristall-audit-stats.md`:
  - Drift-Haeufigkeit pro Ordnung E1-E5
  - False-Positive-Rate der Wargame-Eskalation
  - Martin-Approval-Rate
- Bei False-Positive-Rate > 40%: Kriterien ueberarbeiten (Version-Bump)

## Invocation-Syntax

```
/meta-learn-kristall-audit                          # Default Scope=voll, seit letztem Audit
/meta-learn-kristall-audit scope=E3-E5              # Nur Meta-Ebenen
/meta-learn-kristall-audit since=2026-03-01         # Expliziter Zeitraum
/meta-learn-kristall-audit budget=60min             # Max-Budget override
```

Erwartete Dauer: 30-60 Min (autonom). Martin-Zeit: 20-40 Min (Report + Canon-Decisions).

## CRUX-Gate (2 Wargames)

Siehe Decision-Card `DF-Meta-Kristall-Audit.md`.

**Wargame A (Adversarial):** Erwartet CONDITIONAL. Patches:
- Cross-LLM-Budget begrenzen (Martin-Ressource)
- Fixpunkt-Check darf nicht selbst Meta-Ebenen-Kollaps erzeugen
- 4-team-wargame-Skill-Abhaengigkeit: Fallback auf Inline-Wargame

**Wargame B (CRUX-Alignment):** Erwartet CONDITIONAL. Patches:
- Dark-Factory-Promotion explizit VERBOTEN (Learning-Domain M7)
- Q_0-Schutz: keine automatische Aenderung an Meta-Kristall-Datei ohne Martin-OK

**Kombiniertes Verdict:** CONDITIONAL. Patches in diesem SKILL integriert.

## Lambda-Honesty (M2)

| Parameter | Schaetzung | Konfidenz | Basis |
|-----------|-----------|-----------|-------|
| Lambda (Laeufe/Monat) | 1-2 | mittel | Monatliche Kadenz Default + ad-hoc |
| Drift-Events/Lauf | 2-10 | niedrig | Abhaengig von Lern-Aktivitaet |
| Wargame-Eskalationen/Lauf | 0-5 (max hard-capped) | mittel | TOP-5 nach Risiko-Score |
| Martin-Approval-Rate | 60-80% | niedrig | erste 3 Laeufe werden Daten liefern |
| Martin-Zeit/Lauf | 20-40 Min | mittel | 2 Canon-Entscheidungen + Report lesen |
| Vermiedener Meta-Drift-Schaden/Jahr | 50-150k EUR | niedrig | Meta-Drift erzeugt Wissen-Halluzinationen die K_0/Q_0 gefaehrden |
| Setup-Aufwand einmalig | 4h | hoch | Diese Session (Skill + YAML + Decision-Card) |

**rho-Rechnung:**
- Setup: 4h x 200 EUR/h = 800 EUR einmalig
- Betrieb: ~0.5h Martin-Zeit/Monat x 200 EUR/h = 100 EUR/Monat = 1.2k EUR/Jahr
- OPEX: ~0.2 EUR/Lauf x 12 = 2.4 EUR/Jahr (Claude-Token)
- **Benefit (Vermeidung Meta-Drift):** 50-150k EUR/Jahr
- **Netto-rho:** +48-148k EUR/Jahr
- **Break-Even:** < 1 Monat
- CRUX-Check: K_0 (unantastbar durch Human-in-Loop), Q_0-up (Meta-Integritaet),
  I_min-up (strukturiertes Audit), MHC (Martin-Override auf jeden Canon-Vorschlag)

## Referenzen (persistente Dateien)

- `Claude-Vault/areas/family/META-LERN-KRISTALL-5-ORDNUNGEN-SUPER-SYSTEM.md` (die zu auditierende Struktur)
- `~/.claude/rules/when-to-archon.md` (Tier-1-Kriterien)
- `~/.claude/rules/crux-gate-grenzen.md` (Meta-Ebenen-Asymmetrie)
- `~/.claude/rules/cross-llm-simulation.md` (Simulation vs. echter Cross-LLM)
- `~/.claude/rules/meta-harness.md` §8a (Learning-to-Skill)
- `~/.claude/rules/meta-calibration.md` (Lambda-Honesty, Meta-Upsell-Verbot)
- `branch-hub/.archon/workflows/meta-learn-kristall-audit.yaml` (DAG-Definition)

## Scheduling

**Default:** Monatlich, 1. des Monats 04:00 (Deutsche Zeit).
**Setup via:** `mcp__scheduled-tasks__create_scheduled_task` mit Cron `0 4 1 * *`.
**Manueller Trigger:** `/meta-learn-kristall-audit` oder Natural-Language-Trigger.

## Bekannte Grenzen

- **KEINE Auto-Execution von Canon-Aenderungen.** Jede Aenderung wird MANUELL gesetzt
  nach Martin-APPROVE (separate Session).
- **KEINE automatische Cross-LLM-Ausfuehrung.** Nur Prompt-Paket-Generierung.
- **Fixpunkt-Check ist heuristisch**, nicht formal beweisbar (per E5-Selbst-Konsistenz-Fixpunkt-1).
- **Single-Agent-Wargame im CRUX-Gate.** HARDENED-Status erst nach 3 erfolgreichen Laeufen
  + Cross-LLM-Verifizierung einer Stichprobe.

## Changelog

- **2026-04-18** (Opus 4.7 Architekt-2 Instanz-B): v0.1.0. Skelett-Workflow.
  Decision-Card geschrieben. Wargames A+B (CONDITIONAL). Deployment: Shadow-Modus
  nach Setup. Erster echter Lauf geplant 2026-05-01 04:00.

[CRUX-MK]
