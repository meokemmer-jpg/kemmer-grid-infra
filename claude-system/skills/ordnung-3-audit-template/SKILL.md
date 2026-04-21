---
name: ordnung-3-audit-template
description: Template + Prozess fuer Ordnung-3-Audit (Meta-Methoden-Audit) ueber bestehende Claim-Files. Verhindert Single-Auditor-Beschraenkung + Copy-Paste-Muedigkeit durch mechanische Multi-Auditor-Pflicht + explizite G-Kriterien-Matrix. Triggers "ordnung-3 audit", "meta-audit files", "g1-g14 durchlauf", "pruefe claims systematisch". Empirisch belegt via Subagent-K Welle-2 (11 Files x 16 Kriterien, 5 systematische Gaps identifiziert, Self-Verdict CONDITIONAL). Liefert Matrix-Tabelle + Gap-Analyse + priorisierten Nachbesserungs-Plan.
type: skill
meta-ebene: E3
claim-type: logical
replacement-trigger: "Wenn Single-Auditor-Limit durch neue Multi-Agent-Architektur obsolet wird, ODER wenn in 6+ Audits Cross-LLM/2. Auditor nie echte Divergenz liefert (Ueber-Engineering)"
crux-mk: true
version: 1.0.1
created: 2026-04-19
aktiviert: 2026-04-19
triggers:
  - "ordnung-3 audit"
  - "meta-audit files"
  - "g1-g14 durchlauf"
  - "pruefe claims systematisch"
  - "claim-audit ueber ordner"
  - "systematic claim review"
---

# Skill: ordnung-3-audit-template [CRUX-MK]

## Zweck

Systematischer Audit von Claim-Files gegen G1-G14 + rho-Gain + Zirkularitaet. Baut Multi-Auditor-Anforderung mechanisch ein (ein Auditor = max CONDITIONAL-Verdict). Verhindert zwei empirisch belegte Ausfaelle:

- **F411 Audit-Single-Auditor-Limitation** (max CONDITIONAL ohne G9-Cross-Model-Check)
- **F413 Copy-Paste-Muedigkeit** bei Batch-Audit (Kriterien-Einheitsbrei statt G-spezifischer Pruefung)

## 7-Schritt-Protokoll

### Schritt 1: Scope definieren

- Ziel-Ordner (z.B. `branch-hub/cross-llm/<session>-*`)
- Meta-Ebene der Claims (E1/E2/E3/E4/E5) — aus Frontmatter, nicht geraten
- Audit-Ziel: Vollstaendigkeit / Lambda-Honesty / Cross-Model-Robustness / alle

### Schritt 2: File-Liste erstellen

`glob <pattern>` und pruefen N (erwartet vs tatsaechlich). **Lambda-Honesty:** wenn Zahl abweicht, sofort dokumentieren. Diskrepanz ist erstes Audit-Signal.

### Schritt 3: Matrix-Skeleton

Erstelle Tabelle: Files x Kriterien. Kriterien-Set pro meta-ebene:

| meta-ebene | Pflicht-Kriterien |
|------------|-------------------|
| E1 | G1-G3 + G6 + Primaerquellen-Check |
| E2 | G1-G7 (leicht) + G9 Cross-Model |
| E3 | G1-G9 + rho-Gain + Zirkularitaet |
| E4 | G1-G14 voll |
| E5 | G1 + strukturelle Konsistenz (FIXPUNKT-Check) |

### Schritt 4: Pro-File-Audit (parallel wo moeglich)

Pro File `Read` mit `limit=60` (Frontmatter + Verdict-Section reicht). **NICHT Volltext.**
Klassifiziere Zelle als `✓` (erfuellt) / `~` (partial) / `✗` (fehlt) / `N/A` (nicht anwendbar).

### Schritt 5: Multi-Auditor-Check (G9-PFLICHT)

- **Single-Auditor Self-Audit:** Verdict MAX `CONDITIONAL-Self-Audit` (nicht HARDENED)
- **HARDENED moeglich nur mit:** 2. Auditor via Cross-LLM ODER menschlicher Reviewer ODER anderes Subagent-Design (unabhaengige Architektur)

Dieser Schritt ist der **Anker gegen F411**. Ohne ihn wird jeder Audit ueber-claimed.

### Schritt 6: Gap-Analyse

Systematische Luecken identifizieren: Kriterium das in >=50% der Files fehlt. Top-5 priorisiert nach Wirkung (rho-Impact) x Aufwand (Zeitschaetzung).

### Schritt 7: Nachbesserungs-Plan

Pro Gap: mechanisch fixable (Template-Patch)? Oder braucht Cross-LLM-Retry?
Output-Priorisierung: **Wirkung HOCH x Aufwand NIEDRIG zuerst**.

## Output-Format

```markdown
---
type: finding
meta-ebene: E3
audit-scope: <Ordner/Pattern>
auditor-count: <1 = CONDITIONAL, 2+ = HARDENED-moeglich>
files-audited: <N>
criteria-count: <14-16>
date: 2026-MM-DD
---

# <Titel> Ordnung-3-Systematic-Audit

## Executive Summary (3-5 Zeilen)

## Matrix-Tabelle
<Files x Kriterien, kompakte Darstellung: ✓ / ~ / ✗ / N/A>

## Gap-Analyse
Top-5 systematische Luecken mit Begruendung (warum in >=50% fehlt).

## Priorisierte Nachbesserungen
Wirkung x Aufwand, 5 Vorschlaege mit konkretem Patch-Pfad.

## Selbst-Audit (G1-Konformitaet)
Audit-Bericht auf sich selbst anwenden: erfuellt er selbst G1-G9?
```

## Anti-Patterns

- **F411 Single-Auditor-Inflation**: "Wurde auditiert" ohne G9-Check → Verdict-Gate CONDITIONAL schreiben, nicht HARDENED
- **F413 Copy-Paste-Muedigkeit**: Wiederholungs-Template ohne explizite G-Felder pro File
- **Volltext-Reads**: Token-Verschwendung. Frontmatter + Verdict-Section (~60 Zeilen) reichen
- **G-Kriterien-Einheitsbrei**: Kriterium-Set nicht auf meta-ebene angepasst (E1 braucht weniger als E4)
- **Audit als Beweis**: Audit ist hypothesis-erzeugend, nicht beweisfuehrend (G6 Fallibilismus)
- **Implizite Auditor-Annahme**: "Ich bin objektiv" — max CONDITIONAL bis 2. Auditor bestaetigt

## Empirische Belegung

- **Subagent-K Welle-2 2026-04-18**: 11 Files x 16 Kriterien, 5 systematische Gaps (G9, G13, rho-Quantifizierung, Zirkularitaet-Doku, Replacement-Trigger)
- **Self-Verdict**: CONDITIONAL (G9 ✗ Single-Auditor, G13 ✗ kein Adversarial-Test)
- **Gap-Patch-Zeit**: N1 22min + N2 31min + N4 15min = 68min fuer 3/5 Gaps (mechanisch fixable)
- **F411 Trigger**: Audit-Bericht claimte HARDENED ohne G9 — korrigiert zu CONDITIONAL
- **F413 Trigger**: Bei File 7-11 wurde Kriterien-Matrix reflexartig ausgefuellt — Skill erzwingt nun explizite Re-Klassifikation pro File

## rho-Impact

15-40k EUR/J (verhindert systematische Blindstellen bei Cross-LLM-Claim-Aufnahmen).
Lambda: 2-4 Audits/Monat x CM ~500-1000 EUR/Audit-Verhinderter-Fehlclaim.

## SAE-Isomorphie

- **COSMOS-Audit-Matrix-Pattern** auf Knowledge-Base-Ebene
- **Trinity-Pattern** fuer Multi-Auditor (3 Varianten: Primary, Secondary, Adversarial)
- **MYZ-33 BoundedVeto** analog: Single-Auditor-Verdict ist lokal, globale Autoritaet braucht 2+

## Bezug zu anderen Rules

- `meta-governance-framework.md` G1-G14 (E4-Governance-Regeln, die hier mechanisiert werden)
- `meta-methodological-pragmatism.md` rho-Gain-Messung (Schritt 6 Gap-Priorisierung)
- `meta-validation-portfolio.md` Methoden-Matrix (pro meta-ebene unterschiedliche Kriterien)
- `cross-llm-pflicht-e3-plus.md` (Multi-Auditor-Pflicht fuer E3+ Claims)

## CRUX-Bindung

- **Q_0**: direkt geschuetzt (verhindert ueber-claimed HARDENED-Verdicts)
- **I_min**: erhoeht (strukturierte Matrix statt Ad-hoc-Review)
- **W_0**: effizienter (Frontmatter-Only-Reads, nicht Volltext)
- **K_0**: indirekt geschuetzt (Meta-Fehlclaim → Fehlentscheidung → K_0-Schaden)

[CRUX-MK]
