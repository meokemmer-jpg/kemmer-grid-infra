# Meta-Harness Regel [CRUX-MK]

## Organ 8: Stem Cell -- Das System verbessert sich selbst

### 8a Skill-Creator (Learning-to-Skill Pipeline -- Martin-Direktive 2026-04-08)
**REGEL:** Wenn du etwas LERNST das wiederverwendbar ist:
1. Schreibe Knowledge-Diff in `branch-hub/knowledge-diffs/`
2. **UND** schreibe einen Skill in `~/.claude/skills/[name]/SKILL.md`
3. **UND** kopiere den Skill nach `branch-hub/skills/` (2. Kanal fuer andere Branches)
4. Melde im BULLETIN

**6. Pruef-Frage** (nach den 5 im Knowledge-Diff):
"Kann ich aus diesem Learning einen Skill machen den andere Branches direkt nutzen koennen?"
Wenn JA: Skill schreiben. Sofort. Kein "spaeter".

Zusaetzlich: Nach jedem groesseren Durchlauf pruefen ob ein wiederkehrendes Muster noch keinen Skill hat.

### 8b Self-Edit
SKILL.md Dateien aktualisieren sich selbst nach Erfahrung.
Changelog fuehren. Version-Bump bei Aenderung.

### 8c CLAUDE.md Evolution
Feedback-Regeln die in 3+ Sessions bestaetigt wurden: In CLAUDE.md oder rules/ aufnehmen.
Veraltete Regeln die nicht mehr gelten: Entfernen.
CLAUDE.md ist ein lebendes Dokument.

### 8d Hook Self-Modification
Konfidenz-Map pro Pfad persistent in Finding-Library.
Pfade mit Konfidenz < 0.3 nach 5 Versuchen: Deaktivieren.

### 8e Context Window Self-Awareness
- >50% Context gefuellt: Mechanische Wiederholung verboten. DENKEN.
- >70% Context: /compact triggern.
- >90% Context: STOP. Alles Kritische in Dateien sichern (Memory, Finding-Library, UPDATE_MANIFEST). Dann /compact.
- VOR jedem /compact: Learnings in persistente Schicht schreiben (Theorem 5.3: Session-Handoffs sind lossy).

### CRUX-INHERIT Durchsetzung
Kein Output ohne [CRUX-MK]. 10 Kanaele:
1. NLM-Quellen: Zeile 1 = [CRUX-MK]
2. Chat-Learnings: "LEARNING von [Modell] [CRUX-MK]:"
3. Subagenten: Erste Prompt-Zeile = CRUX
4. Dream-Synthese: [CRUX-MK] + rho-Begruendung
5. Heartbeat: [CRUX-MK] + rho-Begruendung
6. UPDATE_MANIFEST: Pflicht-Spalte rho-Bezug
7. Finding-Library: JSON mit crux_mk + rho_estimate
8. Wargame Cards: CRUX-CHECK
9. Memory-Dateien: Frontmatter crux-mk
10. Neue Skills: YAML crux-mk:true
