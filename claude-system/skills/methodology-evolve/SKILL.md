---
name: methodology-evolve
description: Meta-Harness der Methodik systematisch verbessert. Nimmt Outcomes (Yield-Delta, Plan-Qualitaet, Martin-Feedback, Cross-LLM-Verdict-Stabilitaet) und generiert Methodik-Patches. Triggers "evolve methodology", "meta-harness improve", "method audit", automatisch monatlich + nach Blueprint-Rollout. Komplementaer zu dark-factory-evolve (fuer Factories) und meta-learn-kristall-audit (fuer Kristall).
type: skill-meta-harness
tier: 2 (Meta-Dark-Factory auf Methodik-Ebene)
meta-ebene: E4 (Audit-Audit ueber Methodik)
crux-mk: true
version: 1.0.0
created: 2026-04-19
status: SKELETON (produktions-ready erst nach 3-Monats-Shadow)
depends-on:
  - meta-learn
  - meta-learn-kristall-audit
  - dark-factory-evolve
  - ordnung-3-audit-template
  - monthly-model-audit
---

# Skill: methodology-evolve [CRUX-MK]

## Zweck

Verbessert systematisch die **Art wie Kemmer-System strategische Plaene baut** — die Methodik selbst als evolviertes System. Nicht Inhalt, sondern Prozess.

**Martin-Direktive 2026-04-19:** *"einen Meta Harness auch fuer verbesserung der Methodik"*

Komplementaer zu `github-bauplan-publish` (Publikations-Skill). Dieser Skill haertet die **Methodik selbst** kontinuierlich — Meta-Learning ueber die Art wie wir Plaene bauen.

## Abgrenzung zu bestehenden Meta-Skills (3-Ebenen-Meta-System)

| Ebene | Skill | Scope | Output |
|-------|-------|-------|--------|
| **LLMs (Instrumente)** | `monthly-model-audit` | LLM-Portfolio, Preise, Rate-Limits | Model-Routing-Rules |
| **Factories (Orchestrierung)** | `dark-factory-evolve` | Dark-Factory-Configs, Success-Rate, Cost/Run | Factory-Patches |
| **Claims (Wissens-Struktur)** | `meta-learn-kristall-audit` | 5-Ordnungen-Kristall, Verdict-Stabilitaet, Drift | Canon-Entscheidungen |
| **Methoden (Prozesse) — NEU** | `methodology-evolve` | Art wie wir Plaene bauen, Wargame-Methoden, Haertungs-Prozesse | Methodik-Patches |

**Differenzierung:**
- `dark-factory-evolve` evolviert **Factory-Instanzen** (DF-01, DF-03, DF-06 etc.) — konkrete Orchestrierungs-Pipelines
- `meta-learn-kristall-audit` auditiert **Claim-Base** — was wir als wahr/haert halten
- `methodology-evolve` evolviert **Methoden die IN Factories laufen** — wie wir 4-Team-Wargames durchfuehren, wie wir Cross-LLM-Audits strukturieren, wie wir Pentagon-Prozesse orchestrieren

Zusammen bilden diese 3 Skills das **3-Ebenen-Meta-System**: Instrumente + Prozesse + Strukturen.

## 7-Schritt-Loop

### S1 Outcome-Sampling

Letzte 30 Tage durchsuchen:
- Alle Blueprints in `Claude-Vault/canon/blueprints/` mit Outcome-Daten
- Yield-Delta vor/nach Wargame (aus B202 12-Layer-Tests auf KPM+9OS)
- Plan-Qualitaets-Score (O_total aus `ordnung-3-audit-template` Outputs)
- Martin-Feedback-Stimmung aus Session-Handoff-Logs (`memory/session_handoff_*.md`)
- Cross-LLM-Verdict-Stabilitaet (ADOPT/MODIFY/REJECT-Rate aus `branch-hub/cross-llm/`)
- Pattern-Extraktion aus `branch-hub/learnings/eigenfehler-catalog.md`
- Welle-2/4-Meta-Lessons (F411-F417) als Baseline

**Output:** `/tmp/methodology-evolve/s1-outcome-data.json`

### S2 Methodik-Inventory

Liste aller aktuell-aktiven Methoden extrahieren:
- `4-team-wargame` (Red/Blue/Purple/Gray)
- `multi-llm-parallel` (Orchestrierung ueber 5 LLMs)
- `ordnung-3-audit-template` (Meta-Methoden-Audit)
- `meta-harness-archon` (Claim-Haertung)
- `strategic-wargame-dark-factory` (Level-5 Autonomie)
- `cross-llm-real` (HARDENED statt SIM)
- `gemini-isolated-retry` (Anti-Kontamination)
- `meta-prompting` (Conductor + OPRO)
- `wargame` (v7 Modell-Adaptiv)

Pro Methode: Anwendungs-Count, Success-Rate, Failure-Patterns, avg. Token-Cost.

**Output:** `/tmp/methodology-evolve/s2-methodology-inventory.json`

### S3 Gap-Analyse

- Welche Outcome-Probleme tauchen wiederholt auf? (Pattern-Mining ueber S1-Daten)
- Welche Methoden versagen haeufig (>30% Fail-Rate)?
- Welche Gaps haben aktuelle Methoden nicht abgedeckt?
  - Beispiel B202-Yield-Probleme: 34%/55% vs 92% Target → welche Methode fehlt?
  - Single-Auditor-Beschraenkung (F411) → deckt `ordnung-3-audit-template` das jetzt?
  - Copy-Paste-Muedigkeit (F413) → mechanisch adressiert?
- Cross-Gap-Analyse: Wenn Methode A scheitert, hilft Methode B?

**Output:** `/tmp/methodology-evolve/s3-gap-analysis.json`

### S4 Methodik-Patch-Generation

Pro identifiziertem Gap: 2-3 Patch-Vorschlaege.

Patch-Typen:
- **Rule-Aenderung** (`~/.claude/rules/*.md`): neue Invarianten, geaenderte Schwellwerte
- **Skill-Update**: Version-Bump mit veraenderter Logik (bestehenden Skill anpassen)
- **Neue Skill-Spec**: ganz neue Methode einfuehren (Skelett schreiben, Shadow)
- **Config-Justierung**: Schwellen, Timeouts, Fallback-Regeln in existing Skills
- **Trigger-Pattern-Anpassung**: wann wird Methode X automatisch aktiviert?

Pro Patch: rho-Schaetzung, Setup-Cost, erwarteter Yield-Gain, CRUX-Check.

**Output:** `/tmp/methodology-evolve/s4-patches/<patch-id>.md`

### S5 Cross-LLM-Audit der Patches

Vor Deployment: Codex + Gemini + Grok adversarial.
- Silent-Killer-Check: Haette Patch den Outcome-Problem-Pattern vermieden? (Counterfactual)
- Regression-Test: Welche bestehenden Methoden koennten durch Patch brechen?
- G1-G14-Check (meta-governance-framework.md): Selbst-Konsistenz, Lambda-Honesty, Divergenz-Proxies
- `gemini-isolated-retry` Pflicht (verhindert Gemini-File-Access-Rueckkopplung)

**Output:** `/tmp/methodology-evolve/s5-cross-llm/<patch-id>.md`

### S6 Shadow-Deployment

Patch laeuft 2 Wochen im Shadow (parallel zur bestehenden Methode):
- A/B-Vergleich: Outcome mit vs ohne Patch
- Metriken: Yield-Delta, Martin-Rejects, Token-Cost, Runtime
- Statistische Auswertung nach 14 Tagen (t-test oder Mann-Whitney-U)
- Wenn Lambda < 5 in 2 Wochen: Shadow auf 4 Wochen verlaengern

**Output:** `/tmp/methodology-evolve/s6-shadow/<patch-id>-ab-results.json`

### S7 Promotion oder Rollback

- **Shadow-Metrik signifikant besser (p < 0.05):** Promote
  - Rule aktivieren (von `.PROPOSAL` zu aktivem Dateinamen)
  - Skill-Version bumpen
  - BULLETIN-Eintrag
  - Knowledge-Diff schreiben
- **Shadow-Metrik gleich oder schlechter:** Rollback
  - Dokumentation als Fehlversuch in `branch-hub/learnings/eigenfehler-catalog.md`
  - Neuer Eintrag: "Methode X gegen Methode Y getestet, kein Gain"
- **Unklar:** Shadow verlaengern (max 6 Wochen), dann Rollback wenn kein Signal

**Output:** Entweder Deploy-Commit oder Rollback-Dokumentation.

## Trigger-Pattern

- **Monatlich automatisch** (1. jeden Monats 04:00 via Scheduled-Task oder DF-07)
- **Nach jedem Blueprint-Rollout** (Trigger: neuer File in `Claude-Vault/canon/blueprints/`)
- **Nach 3 consecutive Failures** einer Methode (aus `audit/action-log.jsonl` gefiltert)
- **Explizit:** "evolve methodology", "improve meta-method", "method audit", "evolve method"

## Integration mit bestehenden Skills

Aufruf-Kette (typisches Monatliches-Evolve):

```
methodology-evolve
  → S1: Sample outcomes (inkl. dark-factory-evolve-Metriken als Input)
  → S2: Read meta-learn-kristall-audit inventory output
  → S3: Run ordnung-3-audit-template auf verdaechtige Methoden
  → S4: Generate patches
  → S5: Invoke multi-llm-parallel fuer Cross-LLM-Audit
  → S6: Shadow via workflow-checkpoint
  → S7: Promote via meta-harness-archon (Canon-Aufnahme)
```

## Anti-Patterns

- **Patch-Inflation:** mehr als 3 neue Methoden pro Monat promoten (Cognitive-Overload)
- **Methode retten ohne Outcome-Evidenz:** emotionale Bindung an Methode X, aber Daten sagen sie taugt nicht
- **Shadow-Deployment ueberspringen:** direkt deployen, weil "ist offensichtlich besser"
- **Cross-LLM-Audit skippen:** `gemini-isolated-retry`-Pflicht verletzt
- **"Neue Methode statt alte reparieren":** Komplexitaet akkumuliert, alte Methode bleibt ungepflegt
- **Methode B evaluieren mit Methode B:** Zirkel, braucht unabhaengige Auditor-Methode
- **Nur Quantitative Metriken:** Martin-Qualitaets-Urteil (Phronesis) ist auch ein Signal

## rho-Impact

- **Methodik-Qualitaets-Hebel ueber Zeit:** +5-10% pro Quartal (kumulativ kompoundierend)
- **Bei 20+ Plaenen/Jahr:** +50-150k EUR/J (durch bessere Plan-Qualitaet)
- **Vermiedene Rework-Kosten** durch Fehl-Methoden: +30-80k/J (KPM-1000-Buecher-Wargame: wieviel Zeit haette methodisch-schlechter Plan gekostet?)
- **Break-Even:** 4-6 Monate (nach Shadow-Phase)
- **Setup-Aufwand:** ~6h (Skeleton), dann 2h/Monat Betrieb + Martin-Zeit 30 Min/Monat fuer Patch-Approvals

## SAE-Isomorphie

- **Trinity-Relegation auf Methoden-Ebene:** underperformende Methoden werden archiviert, hochperformende kriegen Lambda-Bonus (mehr Trigger-Pfade)
- **Hamilton-H ueber Methoden-Portfolio:** H = u(Outcome) + lambda*f(Methode-Cost)
- **Goodhart-Schutz:** 3-Tier wenn Metrik vom Ziel abdriftet (Yield-Score, Martin-Satisfaction, Cross-LLM-Stabilitaet)
- **F_CUM_DECAY=0.98 auf Methoden:** langsamer Verfall, nicht Trading-Schnellrelegation

## Falsifikations-Bedingung

- **Nach 6 Monaten 0 substantielle Methodik-Verbesserungen:** Skill archivieren (S1-Signal zu schwach)
- **Wenn Methodik-Rollback-Rate > 70%:** Audit-Qualitaet schlecht, Skill-Revision (S5 unzuverlaessig)
- **Wenn Shadow-Pooling zu klein (Lambda < 3/Monat):** Shadow-Windows verlaengern oder Skill pausieren
- **Wenn Monthly-Cost > rho-Gain:** rho-negativ, pausieren bis Methoden-Pool grenzwertig

## Self-Modifying-Guard

**WICHTIG:** Dieser Skill darf sich NICHT selbst als Patch-Target waehlen.
- Evolution-Targets = alle Methoden ausser `methodology-evolve` selbst
- Aenderungen an diesem Skill = Martin-Pflege (nicht Auto-Evolve)
- Begruendung: Rekursive Selbst-Aenderung ist nicht auditierbar

## Shadow-Deployment (v1.0.0 SKELETON)

Status: **SKELETON**. Produktions-ready nach:
1. 3-Monats-Shadow ab 2026-05-01 (monatlicher Lauf ohne Auto-Promote)
2. 3 erfolgreiche Patch-Zyklen (S1-S7 durchlaufen ohne Martin-Revision)
3. Cross-LLM-Audit bestaetigt G1-G14-Konformitaet
4. Eigenfehler-Catalog zeigt keine neuen Bias-Eintraege durch Skill

Dann Version 2.0.0 = LIVE.

## CRUX-Bindung

- **K_0:** geschuetzt (schlechte Methoden werden nicht auf K_0-Plaenen deployed; Shadow-Pflicht)
- **Q_0:** direkt optimiert (Methodik-Qualitaet = Plan-Qualitaet = Wissens-Integritaet)
- **I_min:** strukturierter 7-Schritt-Loop + G1-G14-Audit
- **W_0:** Martin-Zeit gespart durch bessere Methoden (cumulative ueber Jahre)
- **rho:** +30-80k/J vermiedene Rework, +50-150k/J bessere Plan-Qualitaet, ~200k/J Baseline

## Cross-Reference

- `~/.claude/rules/meta-governance-framework.md` (G1-G14 Pflicht-Kriterien fuer S5)
- `~/.claude/rules/meta-methodological-pragmatism.md` (rho-Gain-Messung, Revised 2026-04-18)
- `~/.claude/rules/meta-stack-fixpunkte.md` (FIXPUNKT-1-4, nicht verletzbar durch Patches)
- `~/.claude/rules/cross-llm-pflicht-e3-plus.md` (Cross-LLM-Pflicht fuer S5 bei E3+-Patches)
- `Claude-Vault/canon/blueprints/B201-ASWDF.md` + `B202-Chipfabrik.md` (Yield-Data)
- `branch-hub/findings/WORK-D-SELF-AUDIT-2-SKILLS-2026-04-19.md` (Audit-Template-Pattern, F411-F417)
- `branch-hub/learnings/eigenfehler-catalog.md` (Rollback-Dokumentation)

## Changelog

- **2026-04-19** (Opus 4.7 Subagent-TT): v1.0.0 SKELETON. 7-Schritt-Loop spezifiziert.
  Differenzierung zu dark-factory-evolve + meta-learn-kristall-audit + monthly-model-audit.
  archon-workflow.yaml als Skeleton. scripts/ Platzhalter. Shadow ab 2026-05-01.

[CRUX-MK]
