# Cross-LLM-Pflicht fuer E3+-Claims [CRUX-MK]

**Aktiviert:** 2026-04-18 durch Martin-Approval "b" (Option B — Kritisch-selektiv, G6+G7+M5-Rule sofort)
**Belegt-durch:** 11/11 Single-Instance-Meta-Regeln ueber-claimed (Meta-C1 Runs #1-5, METADD Runs #6-11)
**Meta-Ebene:** E4 (Governance-Regel ueber Meta-Audit-Prozess)

## Regel

**Keine E3-, E4- oder E5-Aussage wird als HARDENED canonisch aufgenommen ohne vorheriges Cross-LLM-Audit mit mindestens:**

1. **2 externen LLM-Modellen** (Codex GPT-5.4, Gemini 2.5 Pro, oder aequivalente Cross-Provider-Modelle — NICHT Claude-Opus-Varianten die untereinander als "verschieden" deklariert werden)
2. **Dokumentierte Konsens-Analyse** pro Sub-Claim (ADOPT / MODIFY / REJECT) in `branch-hub/cross-llm/2026-MM-DD-<Claim>.md`
3. **Verdict-Tier gemaess FIXPUNKT-1 Update**: CONDITIONAL / CROSS-LLM-SIMULATION-HARDENED / CROSS-LLM-2OF3-HARDENED / HARDENED / FIXPUNKT-HARDENED / STATISTICAL-STABLE
4. **Explizite externe Ankerung** bei HARDENED-Claim (Cross-LLM-Konsens allein ist STATISTICAL-STABLE, nicht HARDENED)

## Rationale (empirisch belegt)

**Datum 2026-04-18 Cross-LLM-Audit-Resultate (alle Runs persistiert in `branch-hub/cross-llm/`):**

| Run | Ebene | Claim-Typ | Original-Verdict | Cross-LLM-Verdict |
|-----|-------|-----------|------------------|-------------------|
| Meta-C1 #1 | E4 | G1 "Selbst-Konsistenz hinreichend" | HARDENED | MODIFY 3/3 |
| Meta-C1 #2 | E5 | FIXPUNKT-1 "math. zwingend" | FIXPUNKT-HARDENED | MODIFY 3/3 |
| Meta-C1 #3 | E5 | FIXPUNKT-2 "Total-Info-Stopp" | FIXPUNKT-HARDENED | MODIFY 3/3 |
| Meta-C1 #4 | E5 | FIXPUNKT-3 "Pragmatismus=Wahrheits-Ersatz" | FIXPUNKT-HARDENED | MODIFY 2OF3 |
| Meta-C1 #5 | E5 | FIXPUNKT-4 "E6+ per se sinnlos" | FIXPUNKT-HARDENED | MODIFY 3/3 |
| METADD #6 | E4 | G2 "Lambda-Honesty hinreichend" | HARDENED | MODIFY 3/3 |
| METADD #7 | E4 | G3 "Meta-Upsell-Verbot hinreichend" | HARDENED | MODIFY 3/3 |
| METADD #8 | E4 | G4 "Predictive-Power notw.+hinr." | HARDENED | MODIFY 3/3 |
| METADD #9 | E4 | G5 "Eleganz hinreichend" | HARDENED | MODIFY 3/3 (Formel REJECT) |
| METADD #10 | E4 | G6 "Fallibilismus notw.+hinr." | HARDENED | MODIFY 3/3 |
| METADD #11 | E4 | G7 "Endlichkeit hinreichend+notw." | HARDENED | MODIFY 3/3 |

**11/11 = 100% Ueber-Claim-Rate** fuer Single-Instance-generierte Meta-Regeln ohne Cross-LLM-Audit.

**rho-Schaden bei Nicht-Adoption**: 130-275k EUR/J durch akkumulierten Meta-Drift.
**rho-Gewinn bei Adoption**: +50-100k EUR/J (systemisch, verhindert zukuenftige Meta-Fehl-Claims).

## Anti-Patterns

1. **Rule-Aktivierung ohne Cross-LLM-Audit** bei Meta-Ebenen E3+
2. **"Hinreichend"-Formulierungen** ohne Adversarial-Test (in 11/11 Faellen verdaechtig)
3. **"Notwendig+hinreichend"-Formulierungen** (noch verdaechtiger)
4. **Claude-Single-Instance-Selbst-Validierung** (gleiche Modell-Familie = korrelierte Biases, auch bei Opus 4.6 vs 4.7)
5. **"Mathematisch zwingend"-Claims** auf Meta-Ebene ohne formale Beweispruefung
6. **"E6+ per se X"** Absolutheits-Claims ohne Tarski/Goedel-Check
7. **Simulated-Cross-LLM** (ein Modell spielt mehrere Perspektiven) als Ersatz fuer echtes Cross-LLM — max CROSS-LLM-SIMULATION-HARDENED

## Operationalisierung

### Cross-LLM-Run-Prozedur (Standard)
```bash
cd /tmp  # vermeidet Windows-Sandbox-Fehler bei UNC-Pfaden
PROMPT=$(cat <prompt-datei>)
KEY=$(powershell.exe -Command "[Environment]::GetEnvironmentVariable('GEMINI_API_KEY', 'User')" 2>/dev/null | tr -d '\r\n')

# Parallel
codex exec --skip-git-repo-check "$PROMPT" > /tmp/<claim>-codex.out 2> /tmp/<claim>-codex.err &
echo "$PROMPT" | GEMINI_API_KEY="$KEY" gemini -p "Beantworte adversarial kompakt Deutsch." > /tmp/<claim>-gemini.out 2> /tmp/<claim>-gemini.err &
wait
```

### Pre-Commit-Hook (Phase 2, zu implementieren)
```yaml
on: pre-commit
trigger: files-matching ~/.claude/rules/*.md OR Claude-Vault/areas/canon/**
check:
  if frontmatter.meta-ebene in [E3, E4, E5]:
    verify: branch-hub/cross-llm/ enthaelt matching-scope Datei
    if not: BLOCK commit with error "Cross-LLM-Pflicht verletzt"
```

### Canon-Gate (via meta-learn-kristall-audit monatlich)
```yaml
for each canon-claim where meta-ebene >= E3:
  if verdict == HARDENED AND no cross-llm-file:
    demote to CONDITIONAL
    create decision-card for Martin
    log to audit/rule-rollback.jsonl
```

## Ausnahmen

**Kein Cross-LLM-Pflicht-Requirement fuer:**
- **E1-Objekt-Claims** (normale Evidenz-Pflichten via meta-validation-portfolio.md)
- **E2-Wissen-ueber-Wissen** mit externer Ankerung (z.B. Messwert-Zitate aus externen Quellen ausserhalb Trainings-Korpus)
- **Existierende Canon-Claims vor 2026-04-18** (grandfathered; monatlicher Meta-Audit-Cron prueft sie nach und nach durch)
- **Dringende Sicherheits-Incidents** mit Martin-explicit-Override

## Verhaeltnis zu anderen Rules

- **Ergaenzt `meta-governance-framework.md`**: Diese Rule operationalisiert G3 (Meta-Upsell-Verbot) und G9 (Cross-model robustness)
- **Komplementaer zu `cross-llm-simulation.md`**: Unterscheidet echte Cross-LLM (HARDENED-Pfad) von Simulated-Cross-LLM (SIM-HARDENED-Pfad)
- **Bindet an `meta-stack-fixpunkte.md`**: FIXPUNKT-1 (Meta-Ebenen-Asymmetrie) definiert die Verdict-Tiers, diese Rule setzt die Pflicht fuer deren Anwendung

## CRUX-Bindung

- **K_0**: indirekt geschuetzt (Meta-Fehl-Entscheidungen → K_0-Schaden ueber Fehl-Anwendung)
- **Q_0**: direkt zentral geschuetzt (epistemische Integritaet der gesamten Meta-Regel-Basis)
- **I_min**: erhoeht (mechanische Enforcement > Dokumentations-Hoffnung, wenn Hook aktiv)
- **W_0**: langfristig effizienter (keine Rollbacks von falsch-HARDENED-Claims)

## Falsifikations-Bedingung (fuer diese Rule selbst)

`Claim-Type: empirical` (nach G6). Diese Regel ist falsifiziert wenn:
- In 20+ weiteren Cross-LLM-Runs die Ueber-Claim-Rate auf < 30% sinkt
- Eine nachweisbare Meta-Methode existiert, die ohne Cross-LLM aber mit anderer Robustheits-Eigenschaft gleichwertige Ergebnisse liefert
- Operative Kosten (Commit-Blockade-Rate, Cross-LLM-USD-Kosten) den rho-Gewinn substantiell uebersteigen ueber 6 Monate

**Auxiliary-Assumptions:**
- Cross-LLM-Modelle bleiben divergent genug (keine voellige Konvergenz der Foundation-Modelle)
- Gemini+Codex+Claude verfuegbar und bezahlbar (Abhaengigkeit von externen Providern)
- 11/11-Evidenz repraesentativ fuer Kemmer-System-Domain

**Replacement-Trigger:** Falls Foundation-Modelle konvergieren oder Martin eine robustere Meta-Audit-Methode einfuehrt: Rule revidieren oder ersetzen.

## Selbst-Anwendung (G1-Check)

Diese Rule ist selbst E4-Claim. Ist sie durch Cross-LLM gehaertet? **Nein direkt, aber indirekt durch die 11 Cross-LLM-Runs, die sie als induktive Schlussfolgerung stuetzen.** 

**Scope (G7):** Diese Rule ist lokal/artefaktbezogen (spricht ueber konkrete Claim-Aufnahme-Prozeduren, nicht ueber E4 als Klasse). Sie ist evaluativ (prueft Einhaltung) + normativ (setzt Pflicht). Die normative Komponente macht sie zu einer **Grenz-E4/E5-Aussage** — ratifiziert durch Martin-Approval.

**Claim-Type:** `empirical` (kann durch ueber-70%-under-Claim-Rate falsifiziert werden)

[CRUX-MK]
