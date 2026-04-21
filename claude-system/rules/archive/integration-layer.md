# SUPERSEDED — REJECTED per C1-Wargame 2026-04-19 [CRUX-MK]
# Verdict: 3/3 REJECT (Grok-reasoning + Codex gpt-5.4 + Grok-fast).
# Grund: G11 Inter-Level-Coherence-Verletzung (strukturell falsch, nicht durch MODIFY rettbar).
# Kernproblem: VETO-Rechte ohne Mandat, Session-Engpass-Risk, Parallel-Work-Blockade.
# Ersatz-Vorschlag: Hook-basierte Mapping-Funktion ohne VETO, integriert in meta-learn-kristall-audit.
# Decision-Card fuer Ersatz: branch-hub/decisions/DC-MYZ-C1-REJECT-ESKALATION-2026-04-19.md
# Cross-LLM-Detail: branch-hub/cross-llm/2026-04-19-WARGAME-C1-integration-layer.md
# Finding: branch-hub/findings/FINDING-C1-PROPOSAL-RULES-WARGAME-2026-04-19.md
# Status vor REJECT: ACTIVE (ueber METAOPS-IL-3 ohne differenziertes Wargame aktiviert, Governance-Drift)
# ARCHIV-Datum: 2026-04-19

---
name: integration-layer
description: Dedizierte Integration-Session-Rolle ab 15+ Sessions fuer Konflikt-Aufloesung + Konsistenz-Wahrung
type: rule-proposal
meta-ebene: E3
status: ACTIVE (CROSS-LLM-HARDENED 2026-04-19 via METAOPS IL-3)
created: 2026-04-18
aktiviert: 2026-04-19
cross-llm-reference: branch-hub/cross-llm/2026-04-18-work-d-decision-framework-scale-7-to-30-sessions.md
claim-type: empirical (Session-Count>=15 Schwelle + Inkonsistenz-Akkumulation ist messbar falsifizierbar)
---

# Integration-Layer [CRUX-MK] -- PROPOSAL

> STATUS: PROPOSAL. Wird erst zu `integration-layer.md` (ohne `.PROPOSAL`) wenn Martin approve.

## Zweck

Ab 15+ Sessions wird Konsistenz-Drift zwischen Sessions zum strukturellen Problem: Rules-Konflikte, Canon-Widersprueche, Fragment-Nummer-Kollisionen, widerspruechliche Empfehlungen an Martin. Einzelne Sessions koennen das nicht selbst aufloesen (Lokalitaets-Bias).

Aus Cross-LLM-Konsens (Codex): **"Integration-Layer ist architektonische Pflicht ab Session-Count >= 15, sonst akkumulieren Inkonsistenzen superlinear."**

## Regel

1. **Dedizierte Integration-Session-Rolle** existiert ab 15+ aktiven Sessions.
2. **Maximal 2 gleichzeitige Integration-Layer-Sessions** (WIP-Limit, um ihre eigene Koordination handhabbar zu halten).
3. **Kandidaten fuer Integration-Rolle** (bereits Integration-Profil):
   - **Meta-C1** (Meta-Audit-Erfahrung, Fixpunkte, Cross-LLM)
   - **METADD** (Multi-LLM-Orchestrierung, Dark-Factory-Integration)
   - **METAOPS** (Rule-Konsolidierung, Hook-Infrastruktur)
   - **MYZ** (Myzel-Layer-Integration, Repo-Sync)
4. **Integration-Layer-Aufgaben (primaer)**:
   - **Konflikt-Aufloesung**: Widersprueche zwischen Sessions detektieren + Resolution-Vorschlag
   - **Konsistenz-Wahrung**: Rules-Set coherent, Canon-Eintraege kompatibel, Fragments-Counter konsistent
   - **Dependency-Map-Pflege**: Wer haengt von wem ab, welche DC sind aktiv
   - **Pre-Canon-Review**: Neues Canon-Artefakt gegen existierendes Canon pruefen
5. **Integration-Layer-Rechte**:
   - Veto gegen Canon-Aufnahme bei nachweisbarem Konflikt
   - Pflicht-Review vor Cross-Session-Dependencies
   - Eskalations-Pfad direkt an Martin
6. **Integration-Layer-Beschraenkungen**:
   - KEINE eigene Phronesis-Rolle (kein DOS fuer Themen)
   - KEINE K_0-relevanten Entscheidungen (nur an Martin weiterleiten)
   - Advisor-Input an DOS wie jede andere Session (kein DOS-Override)

## Mechanik

### Pre-Canon-Check (Integration-Layer)

Vor Canon-Aufnahme (`Claude-Vault/areas/canon/**`):
1. Integration-Layer wird informiert via `branch-hub/contracts/dc-*-to-integration-layer-*-canon-review-*.md`
2. Integration-Layer prueft Konsistenz mit existierendem Canon (max 48h)
3. Freigabe: `Acknowledged` → Canon-Aufnahme erfolgt
4. Veto: `Breached` → Konflikt muss geloest werden vor Aufnahme
5. Bei Dissens: Martin-Eskalation

### Konsistenz-Heartbeat

Integration-Layer fuehrt woechentlich:
- Rules-Set-Scan: Detektiere SUPERSEDED-Verletzungen, zirkulaere Referenzen, widerspruechliche Regeln
- Canon-Konsistenz-Scan: Widerspruechliche Canon-Eintraege, nicht-erfuellbare Invarianten
- Fragment-/Blueprint-Counter-Konsistenz: Parallel-Session-Lanes konform zu REGISTRY.md
- Ergebnis: `branch-hub/integration-reports/<date>-weekly-consistency.md`

### Eskalations-Matrix

- Integration-Veto wird von DOS zurueckgewiesen: Martin-L13
- Zwei Integration-Layer-Sessions dissent: Martin-Entscheidung
- Integration-Layer selbst produziert Konflikt mit anderer Session: Zweite Integration-Layer-Session als Referee

### Aktivierungs-Schwellen

- **< 15 aktive Sessions**: Integration-Layer OPTIONAL (Meta-C1 macht es nebenher)
- **15-25 aktive Sessions**: 1 dedizierte Integration-Layer-Session PFLICHT
- **25+ aktive Sessions**: 2 dedizierte Integration-Layer-Sessions PFLICHT

## Anti-Patterns

- **Integration-DOS-Schleichfahrt**: Integration-Layer uebernimmt Thema-Decision-Owner → Rollen-Verletzung
- **Konsistenz-Purismus**: Integration blockiert jede Innovation als "potenziell inkonsistent" → Fortschritts-Killer
- **Integration-ohne-Koordination**: Zwei Integration-Sessions arbeiten widerspruechlich → Meta-Problem
- **Veto-Missbrauch**: Integration nutzt Veto strategisch statt konsistenz-basiert → Bias-Einfuehrung

## SAE-Isomorphie

**COSMOS (Compliance-Oversight-Safeguard-Monitoring-Sovereignty)**: Governance-Layer der nicht selbst entscheidet, sondern sicherstellt dass Governance eingehalten wird. Hier: Integration-Layer ist COSMOS fuer Session-Set.

**Myzel-Layer Bus-Arbitration**: Event-Bus braucht Arbiter bei Konflikten. Hier: Integration-Layer ist Arbiter bei Session-Konflikten.

**Bounded-Veto (myz33)**: COSMOS kann unter definierten Bedingungen veto'en. Hier: Integration-Layer hat Veto bei Canon-Konflikten.

## CRUX-Bindung

- **Q_0**: direkt geschuetzt (konsistente Canon-Basis, keine Rule-Widersprueche)
- **I_min**: erhoeht (Integration-Infrastruktur)
- **K_0**: indirekt geschuetzt (konsistente Empfehlungen an Martin reduzieren Fehl-Entscheidungen)
- **W_0**: Martin-Bandbreite geschuetzt durch Pre-Resolution der Session-Konflikte
- **rho-Gain**: geschaetzt +100-250k EUR/J durch vermiedene Inkonsistenz-Schaeden bei 30-Sessions-Skala

## Falsifikations-Bedingung

Regel ist falsifiziert wenn:
- Integration-Layer wird selbst Engpass (> 48h Review-Latenz chronisch)
- Integration-Layer produziert mehr Konflikte als sie aufloest (rho-negativ)
- Schwelle 15 ist zu niedrig/hoch (empirische Anpassung noetig)

**Replacement-Trigger**: Falls Falsifikation → Federated-Integration (jede Session hat partielle Integration-Rolle) oder Automated-Integration (Hook-basiert statt Session).

**Claim-Type**: `empirical` (per G6)

[CRUX-MK]
