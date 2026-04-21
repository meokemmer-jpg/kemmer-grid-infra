---
name: knowledge-janitor
description: |
  Archon-Workflow (Tier 1) zum Aufraeumen der Knowledge Base. Findet veraltete Findings,
  inkonsistente Referenzen und fehlende SUPERSEDED-Header. Produziert PRO Kandidat ein
  Wargame-Vorschlag, den Martin einzeln genehmigt (Human-in-the-Loop). KEIN Dark-Factory
  (Lambda zu niedrig, Q_0-Risiko bei Auto-Merge).
  Triggers (run): "kb janitor starten", "knowledge-janitor lauf", "kb aufraeumen",
    "/knowledge-janitor", "wissensbasis aufraeumen", "kb-cleanup".
  Triggers (status): "janitor status", "wie sieht die kb aus".
  Capability: Iteriert ueber branch-hub/findings + Claude-Vault/resources/**, findet
    Supersession-Kandidaten, schreibt pro Kandidat ein Proposal-MD zur Martin-Genehmigung,
    logged Action + Decision in audit/janitor-log.jsonl.
crux-mk: true
version: 0.1.0
origin: opus-4.7-architekt-sprint-2026-04-18
archon-tier: 1
decision-card: G:/Meine Ablage/Claude-Knowledge-System/SAE-v8/docs/decision-cards/knowledge-janitor-archon-workflow-v1.md
canonical-path: C:/Users/marti/.claude/skills/knowledge-janitor/SKILL.md
note: |
  Kanonischer Ort ist ~/.claude/skills/knowledge-janitor/ (siehe canonical-path).
  Diese Datei ist der Zweitkanal (branch-hub) gemaess meta-harness.md §8a und
  rules/vault-bridge.md (Skill-Provenienz). Sync erfolgt via hub-sync.ps1
  oder manuell durch Martin.
---

# /knowledge-janitor [CRUX-MK]

## Essenz

**M8 Wissens-Relegation ist Pflicht.** Ohne Janitor: Findings > 30 Tage akkumulieren,
Cross-Refs veralten, Bootstrap wird teurer, neue Branches lesen Muell. Positiver
Feedback-Loop aus kb-hygiene.md. **Mit Janitor:** monatlich 20-60 min Martin-Zeit,
Proposals pro Kandidat, Martin entscheidet. **Kein Auto-Merge.**

## Wann nutzen

- Monatlich (default erster Montag): Voll-Scan branch-hub/findings + resources/
- Nach jedem groesseren Ereignis (z.B. Architektur-Entscheidung): Gezielter Scan
  der betroffenen Domaene (`kb janitor fuer sae-v8`)

## Wann NICHT

- Wenn Martin < 30 min Zeit hat (Proposals lesen braucht Lesezeit)
- Wenn gleichzeitig aktiver Wargame-Sprint laeuft (Scan-Rauschen)
- Nie als Dark-Factory (K_0-relevante Dokumente wie CLAUDE.md / rules/ darf
  NIE automatisch geaendert werden, siehe `rules/when-to-archon.md` Tier 2 §3.3)

## Pentagon-Ablauf

### Phase 1: PLAN -- Scan-Scope festlegen

Martin beantwortet 3 Fragen beim Start:
1. **Scope**: "alle" (default) / "sae-v8" / "9os" / "family" / "projects/..."
2. **Zeitgrenze**: Default >30 Tage, Override moeglich (z.B. 7 Tage fuer Sprint-Zyklen)
3. **Budget**: Default 15 min LLM-Zeit (~50k Token), max 40 min (~150k Token)

### Phase 2: SPEC -- Kriterien fuer Supersession-Kandidat

Ein Finding/Doc ist **Supersession-Kandidat**, wenn mindestens 2 von 4 Kriterien gelten:

| # | Kriterium | Messung |
|---|-----------|---------|
| 1 | Alter | created > 30 Tage AND kein update in 30 Tagen |
| 2 | Cross-Ref-Rot | >= 1 referenzierte Datei/Pfad existiert nicht mehr |
| 3 | Widerspruch | Zu neuerem Finding im gleichen Topic (Titel-/Tag-Overlap >60%) |
| 4 | Deprecation-Signal | Kommt in der SUPERSEDES-Kette eines anderen Findings vor, aber hat selbst keinen Header |

**Nicht-Kandidaten (immer ausnehmen):**
- `rules/**` (nur Martin-Decision)
- `CLAUDE.md` (alle)
- `BEACON.md`, `BULLETIN.md`, `REGISTRY.md`, `TASK-BOARD.md`
- Dateien mit `lifecycle: canonical` UND updated < 30 Tage

### Phase 3: IMPLEMENT -- Node-DAG (Archon-Workflow-Struktur)

**Node 0 `crux-gate` (Bash):**
- Pruefe CRUX-First-Boot (rules/crux-first-boot.md geladen)
- Pruefe Martin-Zeitfenster vorhanden (sonst: Abort mit Hinweis)

**Node 1 `scan-scope` (Bash):**
- Baue Datei-Liste fuer den Scope (Glob, exclude nicht-Kandidaten)
- Schreibe `$ARTIFACTS/scan-list.json`

**Node 2 `check-age-and-refs` (Bash, deterministisch):**
- Fuer jede Datei: Extrahiere Frontmatter (created, updated), scan fuer Inline-Refs
  (Wikilinks, Dateipfade, URLs zu branch-hub/)
- Pruefe Existenz jeder Ref. Output `$ARTIFACTS/age-refs.json`

**Node 3 `find-topic-overlap` (Claude Haiku, 1 Call pro Kandidat-Paar):**
- Fuer Dateien der letzten 30 Tage: Vergleiche Titel + Top-5-Tags mit aelteren.
- Overlap >60% -> Kandidat fuer "Widerspruch"-Kriterium. Output `$ARTIFACTS/overlaps.json`
- **Cross-LLM-Validierung** (M10): Bei mehr als 5 Kandidaten zusaetzlich einmal
  Gemini oder GPT prompten fuer Overlap-Set. Konvergenz = harder Kandidat.

**Node 4 `build-proposals` (Claude Sonnet, 1 Call pro Kandidat):**
- Pro Kandidat: Schreibe 1 Proposal-MD in
  `branch-hub/proposals/janitor-YYYY-MM-DD-<slug>.md`
- Inhalt: Kandidat-Pfad, Kriterien-Match, vorgeschlagener SUPERSEDED-Header,
  Alternativ-Verweis (neueres Finding), rho-Begruendung (Martin-Zeit gespart,
  Bootstrap-Effizienz, Lesefehler-Risiko).
- Jedes Proposal hat 3 Buttons (Text): `[APPROVE]`, `[REJECT]`, `[DEFER-30]`.

**Node 5 `write-digest` (Claude Sonnet, 1 Call total):**
- Schreibe `branch-hub/proposals/janitor-digest-YYYY-MM-DD.md`
- Zusammenfassung: N Kandidaten, M Auto-Deferred (unter Schwelle), Martin-Review-Pflicht,
  geschaetzte Zeit.

**Node 6 `audit-log` (Bash):**
- Append 1 Zeile pro Proposal in `audit/janitor-log.jsonl`
- Format `{"ts":"ISO","scope":"X","candidates":N,"digest":"pfad","status":"proposals-pending"}`

### Phase 4: TEST -- Smoke + Gate

**Smoke-Test vor jedem Lauf:**
1. Scan-Scope liefert >= 1 Datei
2. Keine Nicht-Kandidaten-Datei in Scan-Liste (CLAUDE.md / rules/ / BEACON etc.)
3. Proposals liegen in `branch-hub/proposals/` (nicht in `findings/` -- kein Doppel-Canon)
4. Digest-MD validiert (Frontmatter + mindestens 1 Kandidat oder "keine Kandidaten"-Fall)

**Hard-Stop:**
- Wenn Node 2 eine Datei mit `tag: crux-mk: true` UND `lifecycle: canonical` vorschlaegt,
  die NICHT durch Node 3-Topic-Overlap abgesichert ist: STOP. Martin-Direkt-Review.
- Wenn Budget ueberschritten: STOP.

### Phase 5: REFINE -- Post-Lauf

**Nach Martin's Reviews:**
- Pro Proposal: Entscheidung aufzeichnen in `audit/janitor-decisions.jsonl`
- Bei APPROVE: Claude (neue Session!) setzt den SUPERSEDED-Header **in der
  Primaerquelle** (branch-hub/findings/ oder Vault, NICHT _from-hub-Spiegel).
  Die Header-Setzung ist eine SEPARATE Aktion (Martin-OK pro Stueck).
- Bei REJECT: Vermerk im Finding "Janitor-Check <Datum>: als aktuell bestaetigt."
- Bei DEFER-30: Termin in `janitor-defer-YYYY-MM-DD.txt`, naechster Lauf greift erst danach wieder.

**Lern-Loop (meta-harness §8a):**
- Nach 3 Laeufen: Statistik in `learnings/knowledge-janitor-stats.md` schreiben.
  - Treffer-Quote (APPROVE / gesamt)
  - Haeufigste False-Positives
  - Zeit-pro-Review-Median
- Bei Treffer-Quote < 30% nach 3 Laeufen: Kriterien ueberarbeiten
  (Skill-Version-Bump + knowledge-diff).

## CRUX-Gate (2 Wargames)

Siehe Decision-Card `docs/decision-cards/knowledge-janitor-archon-workflow-v1.md`.

**Wargame A (Adversarial):** CONDITIONAL, 3 Patches (False-Positives bei canonical Dokumenten,
Martin-Zeitbudget realistisch, Cross-LLM-Budget).

**Wargame B (CRUX-Alignment):** CONDITIONAL, 1 Patch (Dark-Factory-Promotion explizit
VERBOTEN -- Learning-Domain ist sakrosankt, M7).

**Kombiniertes Verdict:** CONDITIONAL. Patches in diesem SKILL integriert.

## Lambda-Honesty (M2)

| Parameter | Schaetzung | Konfidenz | Basis |
|-----------|-----------|-----------|-------|
| Lambda (Laeufe/Monat) | 1-2 | mittel | Monatliche Kadenz Default |
| Kandidaten/Lauf | 5-20 | niedrig | Abhaengig von Scope + Wachstumsrate KB |
| Approval-Rate | 50-75% | niedrig | erste 3 Laeufe werden Daten liefern |
| Martin-Zeit/Review-Proposal | 2-5 min | mittel | Lesen + Entscheidung |
| Martin-Zeit/Lauf (Digest + Proposals) | 20-60 min | mittel | 5-20 Proposals x 2-5 min + Digest 10 min |
| Vermiedener KB-Schaden/Jahr | 5-30k EUR | sehr niedrig | Tester-Wargame zeigte 20-50k potenzial pro MAJOR Vorfall |
| Setup-Aufwand einmalig | 6-10h | mittel | Diesen Skill, Workflow-YAML, Test-Lauf |

**rho-Rechnung:**
- Netto-rho (bei Lambda=1.5/Mon, avg Schaden 10k/J, Setup 10h x 200 EUR/h = 2k):
  Break-Even in ~3 Monaten.
- CRUX-Check: K_0 (unantastbar durch Human-in-Loop), Q_0 (KB-Qualitaet steigt),
  I_min (Ordnung in KB explizit gestaerkt).

## Referenzen (persistente Dateien)

- `rules/kb-hygiene.md` (Grund-Regeln SUPERSEDED-Disziplin)
- `rules/when-to-archon.md` (Archon-Tier-1 vs. Dark-Factory Kriterien)
- `rules/meta-harness.md` §8a (Learning-to-Skill)
- `Mechanismen-MASTER §6 Dark-Factory-Kandidaten` (Tier-2 Janitor explizit HIER als Archon-1 degradiert wegen Lambda + K_0-Risiko)
- `Wargames-META M8` (Wissens-Relegation)

## Bekannte Grenzen

- **KEINE Auto-Execution von SUPERSEDED-Setzungen.** Jeder Header wird MANUELL gesetzt
  nach Martin-APPROVE (separater Run, separate Session).
- **Keine Rule/CLAUDE.md-Manipulation.** Explizit exkludiert.
- **Single-Agent-Wargame im CRUX-Gate.** HARDENED-Status erst nach 3 erfolgreichen
  Laeufen + Cross-LLM-Verifizierung einer Stichprobe von Kandidaten.

## Changelog

- **2026-04-18** (Opus 4.7, Architekt-Sprint): v0.1.0. Skelett-Workflow. Decision-Card
  geschrieben. Wargames A+B (CONDITIONAL). Deployment: Shadow-Modus nach Setup.

[CRUX-MK]
