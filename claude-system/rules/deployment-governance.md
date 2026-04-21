# Deployment-Governance [CRUX-MK]

Ausgelagert aus `context-budget.md §9` durch METAOPS 2026-04-19 (Cross-LLM-2OF3-HARDENED Grok+Codex: Scope-Cut fuer Sauberkeit).

## §1 Deployment-Status-Pflicht

Jedes geschriebene Artefakt (Proposal, Rule, Skill, Decision-Card, Finding, Blueprint) bekommt eines von drei Feldern im Frontmatter:

```yaml
aktiviert: 2026-04-19            # ist live, wirkt
# ODER
aktiviert-in: 2026-05-19          # wartet auf Trigger, max 30 Tage
# ODER
supersession-gescheitert: 2026-04-19   # abgelehnt, archiviert
```

**Default bei neuer Datei ohne Feld:** `aktiviert-in: <Erstellungsdatum + 30 Tage>`.

## §2 Automatische Supersession-Pruefung

Nach 30 Tagen ohne Aktivierung oder Promotion:
1. Skill `knowledge-janitor` (oder Manual-Run) detectiert abgelaufene Artefakte
2. Entscheidung erzwingen: aktivieren (setze `aktiviert`) ODER archivieren (setze `supersession-gescheitert`)
3. Bei Untaetigkeit nach 7 weiteren Tagen: automatisch `supersession-gescheitert` + Martin-Alert

## §3 Aktivierungs-Trigger (was "live" bedeutet)

- **Rule:** ~/.claude/rules/ erreicht + vom Harness automatisch geladen (Frontmatter-Hook akzeptiert)
- **Skill:** ~/.claude/skills/<name>/SKILL.md vorhanden mit gueltiger Frontmatter
- **Decision-Card:** Martin-Approval im BEACON oder inbox/to-martin.md dokumentiert
- **Finding:** Mindestens 1 Cross-LLM-Validierung + Persistenz in branch-hub/findings/
- **Blueprint:** Mindestens Tier-1-Wargame bestanden + Counter-Lane-Zuordnung

## §4 Deployment-Gap-Monitoring

**Mechanisch:** Skill `meta-learn-kristall-audit` (monatlich) prueft:
- Anzahl Artefakte mit Status `aktiviert-in` die ueber 30 Tage alt sind
- Decision-Cards ohne Martin-Approval-Feld > 14 Tage
- Rules ohne Hook-Validation > 7 Tage

**Alarm-Schwellen:**
- 3+ abgelaufene Artefakte: Warnung im Monatlichen Audit-Report
- 10+ abgelaufene Artefakte: Hard-Stop + Martin-Eskalation (keine neuen Artefakte bis Aufraeumen)

## Bezug zu anderen Rules

- `context-budget.md §§1-7`: regelt eigenes Arbeits-Fenster (Context, Token, Messung, Pre-Flight)
- `parallel-session.md §§1-7`: regelt Multi-Branch-Koordination
- `audit-trail.md §§1-4`: regelt Log-Streams (Writes, Permissions, Workflow)
- **Diese Rule:** regelt Artefakt-Lifecycle (Proposal → Aktivierung → Archivierung)

## SAE-Isomorphie

Dies ist **MYZ-27 Relegation** angewendet auf Artefakte statt Agenten. Ohne Relegation: Artefakt-Bloat. Mit Relegation: saubere Knowledge-Base.

## CRUX-Bindung

- **K_0:** geschuetzt (keine vergessenen Decision-Cards zu K_0-relevanten Entscheidungen)
- **Q_0:** direkt erhoeht (Knowledge-Base integer, keine Zombie-Proposals)
- **I_min:** erhoeht (mechanischer Deployment-Prozess)
- **W_0:** Write-Budget effizient (keine ewig-pending Artefakte)

## Hintergrund

Historisch in context-budget.md §9 als Teil des Context-/Token-Regelwerks. Cross-LLM-Audit P4 (Codex) identifizierte Scope-Inflation: Deployment-Pflicht ist Governance-Layer, nicht Budget-Layer. Grok bestaetigte: Auslagern vermeidet Scope-Creep, klaert Architektur risikoarm.

Originalquelle: `rules/context-budget.md §9` (BIAS-014 CRIT, 2026-04-17). Diese Datei subsumiert die Regel und erweitert sie um §2-§4.

[CRUX-MK]
