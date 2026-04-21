# SUPERSEDED — Verschoben zu: branch-hub/learnings/eigenfehler-catalog.md [CRUX-MK]
# WARNUNG: Dieses Dokument ist veraltet seit 2026-04-18 (METAOPS Mission-2).
# Aktuelle Version: G:/Meine Ablage/Claude-Knowledge-System/branch-hub/learnings/eigenfehler-catalog.md
# Grund: Incident-Katalog ist Datenfile, nicht Verhaltensregel. Rules schreiben vor, Katalog dokumentiert.
# Neu: F7 (Hook-Infrastruktur bei Fork) hinzugefuegt. Mitigation-Referenzen auf konsolidierte Rules aktualisiert.

# Bekannte Methodik-Ausfaelle [CRUX-MK] (ARCHIV)

**Zweck:** Verhindert Eigenfehler EF-4 (Optimismus-Bias bei Methodik-Wiederholung). Wenn etwas bereits dokumentiert fehlgeschlagen ist, wiederhole es nicht ohne Anpassung.

**Regel:** Vor jeder Subagent-/Skill-/Tool-Nutzung die hier gelistet ist — zuerst die Mitigation lesen. Wiederholung ohne Mitigation = Verstoss.

---

## F1 — Chrome-MCP Screenshots in Massen

**Datum:** 2026-04-17 (Meta-Lern-Pilot NLM-Chat) + 2026-04-17 Abend (Welle 1 partial abgebrochen)
**Symptom:** `An image in the conversation exceeds the dimension limit for many-image requests (2000px). Start a new session with fewer images.`
**Ausloeser:** Chrome-MCP `preview_screenshot` oder `javascript_tool` bei JavaScript-heavy SPAs (NotebookLM, Google-Suite) — Screenshots werden zu gross, zu viele pro Session.
**Kosten-Ausfall:** ca 16 min + 98 Tool-Uses ohne Output (Pilot) / 1 Notebook statt 3 (Welle 1).

**Mitigation:**
1. **Kein Chrome-MCP** fuer NLM-Massen-Chats. Nur gezielte Einzel-Aktionen.
2. Alternativer Pfad: Drive-Spiegel-Scan (`nlm-library/`) fuer 70-80% der Inhalte.
3. Fuer residualen Gap: Martin chattet manuell, liefert Transkript als Textdatei.
4. Wenn Chrome-MCP zwingend: `get_page_text` statt `screenshot`, plus Page-at-a-Time statt Batch.

---

## F2 — Single-Instance-Planung bei Multi-Branch-System

**Datum:** 2026-04-17 (Opus 4.7 Architekt-Session parallel zu anderer Session)
**Symptom:** Ich plane und handle als ob ich die einzige Claude-Instanz bin. Parallele Session baut gleichzeitig dieselben Artefakte → Namespace-Kollision (z.B. Fragment F76 doppelt belegt).
**Ausloeser:** Ich ignoriere BEACON + MEMORY-Index oder lese nur erste Zeile.

**Mitigation:** `rules/parallel-session-coordination.md` — BEACON/MEMORY/Handoff komplett lesen bei Session-Start und bei jedem "warum wartest du"-Signal.

---

## F3 — Context-Fuellung per Heuristik ohne Messung

**Datum:** 2026-04-17 (mehrfach)
**Symptom:** Ich schaetze 80-95% Fill, real 33-51%. Bias +30-60 pp pessimistisch.
**Ausloeser:** Ich zaehle Tool-Uses und grosse Reads mechanisch, vergesse dass Subagent-Reports destilliert zurueckkommen und Writes den Context nicht belasten.

**Mitigation:** `rules/meta-calibration.md` (neu in Parallel-Session) — keine Context-Schaetzung ohne Messung. Wenn Martin Zahl liefert: nutzen.

---

## F4 — "Ich warte auf Subagent" als Antwort-Ende

**Datum:** 2026-04-17 (mehrfach, Martin-Korrektur: "dann wartet ihr aufeinander")
**Symptom:** Ich beende Antwort mit "warte auf X, handle nicht weiter". Parallel-Achsen bleiben unbelegt. Clausewitz-Friktion durch Passivitaet.
**Ausloeser:** Ich interpretiere Auftragstaktik als "Anweisung warten" statt "Raum belegen bei Unsicherheit".

**Mitigation:**
1. Anti-Regel: Keine Antwort endet mit "ich warte auf X". Stattdessen "ich mache parallel Y".
2. 6-Agenten-Self-Check (L6) vor Wartezustand: Agent 6 (Energy Guardian) fragt "Ist das der richtige Zeitpunkt zu warten?" — meist nein.

---

## F5 — Binaeres Reifegrad-Denken (Alles oder Nichts)

**Datum:** 2026-04-17 (Martin-Korrektur: "Architekt bleiben aber Limitationen kennen")
**Symptom:** Martin sagt "Level 0 bei X". Ich generalisiere: "Architekt → Student". Ueber-Korrektur.
**Ausloeser:** Fehlende Domaenen-Granularitaet im Reifegrad-Framework.

**Mitigation:** Domaenen-Landkarte in `Claude-Reifegrade-Ressourcen-Matrix.md` §Landkarte. Pro Domaene eigener Level. Bei Fremd-Einschaetzung: nur die genannte Domaene anpassen, nicht Gesamtrolle.

---

---

## F6 — K4-Skizze redundant gebaut (Parallel-Session)

**Datum:** 2026-04-18 (in dieser Session)
**Symptom:** Ich baute K4-Familien-Gluehbirnen-Skizze als Write, bekam "File has not been read yet" — Parallel-Session hatte sie bereits geschrieben. Mein Write waere Overwrite gewesen.
**Ausloeser:** Ich habe `parallel-session-coordination.md` (soeben geschrieben) nicht ANGEWENDET bevor ich handelte. BEACON zeigt Parallel-Aktivitaet, aber ich checkte nicht gezielt fuer K4.

**Mitigation:** Vor JEDEM Write auf `areas/family/` oder `docs/decision-cards/`:
```
ls <target-verzeichnis> | grep -i <thema>
```
Wenn Kollisions-Kandidat existiert: Read first, dann entscheiden ob Append / Supersede / Separate-Datei.

**SAE-Isomorphie:** Diese Mitigation ist die Optimistic-Lock-Regel (Version-Check vor Write). In SAE v8: `state.py` Atomic-Write-Pattern.

---

## Update-Regel

Neue Eintraege werden nach jedem Session-Ende gepruft (meta-learn Skill). Wenn >= 3 Sessions denselben Fehler vermeiden durch Mitigation: promoten zur Sakrosankten Invariante (verschieben in `rules/crux.md` oder Architekten-Doktrin).

## SAE-Isomorphie

Dies ist die Lessons-Learned-Datenbank (learning/finding_library.py in SAE v8). Pattern-Matching: wenn aktuelle Situation zu F1-F5 matched, Mitigation auto-triggern.

[CRUX-MK]
