---
name: dependency-contracts
description: Formalisierte Handover-Artefakte (Brief, DR, OQ, DC) zwischen Sessions statt Ad-hoc-Inbox
type: rule
meta-ebene: E3
status: ACTIVE (CROSS-LLM-SIM-HARDENED 2026-04-19 via C1-Wargame 2/3 ADOPT Codex+Grok-fast)
created: 2026-04-18
aktiviert: 2026-04-19
reconfirmed: 2026-04-19 (Martin-Option-B, C1-Wargame bestaetigt ADOPT)
cross-llm-reference: branch-hub/cross-llm/2026-04-19-WARGAME-C1-dependency-contracts.md
c1-wargame-finding: branch-hub/findings/FINDING-C1-PROPOSAL-RULES-WARGAME-2026-04-19.md
claim-type: logical (4-Artefakt-Typen-Taxonomie, G4 via formale Lifecycle-Invarianten)
schaerfungen-v1.1-pending: [REGISTER-Auto-Heartbeat, DR-Supersede-Pfad, 30d-Monitoring, 90s-Brief-Template]
---

# Dependency-Contracts [CRUX-MK] — AKTIV

> **STATUS: ACTIVE** per Martin-Option-B 2026-04-19 nach C1-Wargame (2/3 ADOPT Konsens).
> 4 Schaerfungen als v1.1-Pending: Cross-LLM empfiehlt Implementation-Details, aber Kernregel ist bereits aktiv.
> Details siehe `FINDING-C1-PROPOSAL-RULES-WARGAME-2026-04-19.md` §Rule-2.

## Zweck

Ersetzt Ad-hoc Inbox-Nachrichten bei Hoch-Frequenz-Multi-Session-Betrieb. Bei 30 Sessions entstehen taeglich 50+ Handovers. Unstrukturierte Inbox-Messages fuehren zu: Info-Verlust (Theorem 5.3), Kontext-Inkompatibilitaeten, schwer nachvollziehbare Dependencies, Session-Handoff-Chaos.

Aus Cross-LLM-Konsens (Codex): **"Formalisierte Handover-Artefakte sind strukturelle Pflicht fuer Skalierung, ohne sie wird Koordination O(N^2)."**

## Regel

### Vier Artefakt-Typen (formalisiert)

1. **Brief** (Kurz-Uebergabe, einseitig)
   - Wer, Was, Warum, Bis Wann
   - Keine Erwartung an Antwort
   - Max 200 Zeilen

2. **DR (Decision Record)** (Entscheidung mit Begruendung)
   - Kontext, Optionen, Entscheidung, Rationale, Konsequenzen
   - Immutable nach Acknowledge (keine Revision ohne neues DR)
   - Ersetzt Parallel-Decision-Cards bei Cross-Session-Entscheidungen

3. **OQ (Open Questions)** (Offene Fragen-Liste)
   - Strukturierte Q&A mit Status (offen/beantwortet/eskaliert)
   - An DOS oder Advisor adressiert
   - Lifecycle: Draft → Sent → Answered → Closed

4. **DC (Dependency Contract)** (Verbindliche Abhaengigkeit)
   - From-Session garantiert X, To-Session garantiert Y
   - Mit Deadline + Escalation-Trigger
   - Lifecycle: Draft → Proposed → Acknowledged → Active → Closed/Breached

### Speicherort

`branch-hub/contracts/<type>-<from>-to-<to>-<date>-<short-title>.md`

Beispiele:
- `branch-hub/contracts/brief-meta-c1-to-work-d-2026-04-18-patch-review.md`
- `branch-hub/contracts/dr-metadd-to-all-2026-04-18-option-b-selektiv.md`
- `branch-hub/contracts/oq-work-c2-to-meta-c1-2026-04-18-cross-llm-setup.md`
- `branch-hub/contracts/dc-myz-to-beta-2026-04-18-repo-sync-weekly.md`

### Template-Struktur pro Artefakt

```markdown
---
type: brief | dr | oq | dc
from: <session-name>
to: <session-name> oder 'all'
created: <ISO-timestamp>
status: draft | sent | acknowledged | active | closed | breached
deadline: <ISO-timestamp> (nur DC)
crux-mk: true
---

## <Titel>

### Kontext

### Kernaussage (Brief) | Entscheidung (DR) | Fragen (OQ) | Vereinbarung (DC)

### Begruendung/Belegung

### Nachste Schritte / Acknowledge-Anforderung

### CRUX-Bindung

[CRUX-MK]
```

### Lifecycle-Regeln

- **Brief**: Draft → Sent. Keine Acknowledge-Pflicht. Auto-archived nach 14 Tagen.
- **DR**: Draft → Sent → Acknowledged (min. 1 Session). Immutable ab Acknowledge.
- **OQ**: Draft → Sent → Answered (per Frage) → Closed (alle beantwortet). Eskalation an Martin bei >7 Tagen offen.
- **DC**: Draft → Proposed → Acknowledged (by to-session) → Active → Closed (fulfilled) / Breached (deadline missed). Breached DC → BEACON-Alert.

### Register

`branch-hub/contracts/REGISTER.md` enthaelt Index aller aktiven Contracts mit Status und Deadline.

## Mechanik

### Pre-Inbox-Regel

Vor `inbox/to-<session>.md` Write:
1. Ist dies ein Handover mit Strukturpotenzial? (Brief/DR/OQ/DC?)
2. Wenn JA: Formalisiertes Contract erstellen statt Inbox-Nachricht
3. Inbox nur fuer niedrig-strukturierte Messaging (Status-Updates, informelle Fragen)

### Session-Start-Ritual

Bei Bootstrap:
1. `branch-hub/contracts/REGISTER.md` lesen
2. Aktive DC pruefen bei deren from/to ich stehe
3. Status-Update auf meine aktiven Contracts
4. Offene OQ beantworten wenn in meinem Scope

### Breach-Behandlung

Bei DC-Breach (Deadline missed ohne Update):
1. BEACON-Eintrag mit Breach-Info
2. 24h Grace-Period
3. Danach: Eskalation an Martin
4. Lessons-Learned in `branch-hub/learnings/contract-breaches.jsonl`

## Anti-Patterns

- **Inbox-Abuse**: Struktur-relevante Handovers als informelle Inbox-Messages → verletzt Formalisierung
- **DR-Overwriting**: Decision Record nachtraeglich editieren → Immutability-Verletzung
- **OQ-Ghosting**: OQ stellen aber nicht auf Antworten reagieren → blockiert sender-session
- **DC-Casualness**: DC ohne Deadline oder ohne Acknowledge → kein echter Contract

## SAE-Isomorphie

**Myzel-Layer-Events**: Strukturierte Events mit Typen (evt-000000X) ersetzen unstrukturierte Inter-Agent-Kommunikation. Hier: 4 Contract-Typen ersetzen Inbox-Floodung.

**Governance-Tier-Invariante**: Jeder Event hat definierte Fields. Hier: Jedes Contract hat Pflicht-Frontmatter.

**Audit-Trail (action-log.jsonl)**: Jede Aenderung wird gelogged. Hier: Contract-Lifecycle wird im REGISTER gelogged.

## CRUX-Bindung

- **Q_0**: direkt geschuetzt (keine Info-Verluste durch strukturierte Handovers)
- **I_min**: erhoeht (Contracts-Infrastruktur + REGISTER)
- **W_0**: Martin-Zeit geschuetzt durch Klarheit der Contracts (keine Rueckfrage-Schleifen)
- **rho-Gain**: geschaetzt +60-150k EUR/J durch vermiedene Koordinations-Verluste bei 30-Sessions-Skala

## Falsifikations-Bedingung

Regel ist falsifiziert wenn:
- Contract-Overhead groesser als Koordinations-Ersparnis (empirisch ueber 3 Monate)
- Session-Team meldet dass 4 Typen zu viel sind (Konsolidierung gewuenscht)
- Breach-Rate > 30% (Contracts zu unrealistisch)

**Replacement-Trigger**: Falls Falsifikation → Vereinfachte 2-Typen-Variante (Brief + DC) oder Ruckkehr zu strukturierterter Inbox.

**Claim-Type**: `empirical` (per G6)

[CRUX-MK]
