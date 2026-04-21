---
name: decision-owner-per-theme
description: Pro Thema genau ein Decision-Owner-Session, andere Phronesis-Sessions werden Advisor/Challenger
type: rule
meta-ebene: E3
status: ACTIVE-MODIFY-v2-PENDING (C1-Wargame 2/3 MODIFY 2026-04-19, Schaerfungen vor v2-Aktivierung)
modify-v2-schaerfungen: [Co-DOS fuer Cross-Cutting-Themen, Anti-Gaming-Check bei Themen-Zerlegung, SPOF-Mitigation bei DOS-Ausfall]
c1-wargame-finding: branch-hub/findings/FINDING-C1-PROPOSAL-RULES-WARGAME-2026-04-19.md
c1-wargame-detail: branch-hub/cross-llm/2026-04-19-WARGAME-C1-decision-owner-per-theme.md
created: 2026-04-18
aktiviert: 2026-04-19
cross-llm-reference: branch-hub/cross-llm/2026-04-18-work-d-decision-framework-scale-7-to-30-sessions.md
claim-type: logical (organisationsstrukturelle Konsistenz, G4 via formale Single-Owner-Invariante)
---

# Decision-Owner-Per-Theme [CRUX-MK] -- PROPOSAL

> STATUS: PROPOSAL. Wird erst zu `decision-owner-per-theme.md` (ohne `.PROPOSAL`) wenn Martin approve.

## Zweck

Verhindert Phronesis-Konkurrenz bei Skalierung 7 → 30 Sessions. Ohne Single-Owner-Regel entsteht das Problem dass mehrere Sessions sich als berechtigt sehen eine thematische Entscheidung vorzubereiten oder gar zu treffen. Ergebnis: widerspruechliche Empfehlungen an Martin, Zeit-Engpass-Verschaerfung, Entscheidungs-Drift.

Aus Cross-LLM-Konsens (Codex 1OF1-ECHT-UNABHAENGIG, 2026-04-18): **"Pro Thema ein Decision-Owner ist notwendige Skalierungs-Bedingung, keine Option."**

## Regel

1. Jedes **Thema** bekommt genau EINEN **Decision-Owner-Session** (DOS).
2. Andere Sessions die am selben Thema arbeiten sind **Advisor** oder **Challenger**, NIEMALS Mit-Entscheider.
3. **Themen-Liste** (initial, erweiterbar durch Martin):
   - Cape-Coral-Relocation
   - KPM-Familien-Trading
   - HeyLou-Pilot-Hotel (inkl. Hildesheim)
   - 9dots-PMO-Transformation
   - Graphity-Verlag
   - Buecher-Trilogie
   - SAE-v8-Architektur
   - Familien-Gesundheit (K_0/Q_0-Domaene)
   - Meta-Lern-System
4. **Decision-Owner-Rechte:**
   - Darf Decision-Cards verfassen + an Martin leiten
   - Darf Advisor-Input zurueckweisen mit Begruendung
   - Darf Thema-Scope definieren
5. **Advisor/Challenger-Pflichten:**
   - Input via `branch-hub/contracts/advisor-<date>.md` an DOS schicken
   - Nicht direkt an Martin mit Entscheidungs-Vorschlag (nur DOS darf das)
   - Bei Dissens: Challenge ueber formale Advisor-Nachricht, nicht Parallel-Card
6. **Martin-L13-Override** bleibt unveraendert: Martin kann jederzeit DOS-Entscheidung stoppen/revidieren.

## Mechanik

### REGISTRY.md-Erweiterung

```markdown
## Decision-Owner-Matrix

| Thema | DOS | Advisor-Sessions | Aktiviert |
|-------|-----|------------------|-----------|
| Cape-Coral | <session-name> | <session1>, <session2> | <datum> |
| KPM | <session-name> | <session1> | <datum> |
...
```

### Pre-Decision-Card-Check

Vor `docs/decision-cards/*.md` Write:
1. Thema identifizieren (Frontmatter-Feld `thema`)
2. REGISTRY.md lesen: Bin ich DOS fuer das Thema?
3. Wenn JA: Write darf erfolgen
4. Wenn NEIN: STOP. Advisor-Nachricht an DOS schreiben statt Card.

### Eskalations-Matrix

- DOS nicht erreichbar >48h: Martin-Alert via BEACON
- Advisor-Dissens ungeloest >7 Tage: Martin-L13-Eskalation
- DOS-Rolle wechseln (z.B. bei Session-Death): Martin-Entscheidung + REGISTRY-Update

## Anti-Patterns

- **Silent-Owner-Claim**: Session arbeitet am Thema ohne REGISTRY-Eintrag → verletzt Single-Owner
- **Parallel-Decision-Cards**: Zwei Sessions schreiben beide Cards zum gleichen Thema → Konflikt
- **Advisor-Upgrade-Schleichfahrt**: Advisor praesentiert Input als Entscheidung → Rollen-Verletzung
- **Thema-Zerlegung-Missbrauch**: Session spaltet Thema kuenstlich um DOS zu werden → Scope-Gaming

## SAE-Isomorphie

**Trinity-Pattern**: Jeder Slot hat genau einen Winner-Agent (Conservative/Aggressive/Contrarian Variante mit hoechstem Score). Die anderen 2 sind Challenger. Hier: Jedes Thema hat genau einen DOS, andere sind Advisor.

**MYZ-32 Dispatcher**: Events werden nach Agent-Class geroutet, hier: Decision-Requests werden nach DOS geroutet.

**Bounded-Veto (myz33)**: COSMOS kann ueber-ruled werden nur durch explizite Eskalation. Hier: Martin-L13 ist einzige Override-Quelle.

## CRUX-Bindung

- **K_0**: direkt geschuetzt durch Single-Owner (keine widerspruechlichen K_0-Entscheidungen an Martin)
- **Q_0**: direkt geschuetzt (konsistente thematische Entscheidungs-Linie)
- **I_min**: erhoeht durch REGISTRY-Matrix-Struktur
- **W_0**: Martin-Bandbreite nicht durch Parallel-Cards fragmentiert
- **rho-Gain**: geschaetzt +30-80k EUR/J durch vermiedene Entscheidungs-Drift bei 30-Sessions-Skala

## Falsifikations-Bedingung

Regel ist falsifiziert wenn:
- Ueber 6 Monate in 30-Session-Betrieb die Decision-Latenz steigt (DOS-Rolle wird Engpass)
- DOS-Wechsel-Haeufigkeit > 1x pro 2 Monate (Rolle zu starr)
- Martin meldet dass er Advisor-Input direkter braucht als ueber DOS-Filter

**Replacement-Trigger**: Falls Falsifikation eintritt → Wechsel zu Federated-Decision-Model (mehrere Teil-Owner pro Thema-Aspekt).

**Claim-Type**: `empirical` (per G6 meta-governance-framework.md)

[CRUX-MK]
