---
name: 4-team-wargame
description: Automatisiertes Red/Blue/Purple/Gray Wargame fuer Claims. Nutzt Meta-Lern-Kristall (5 Ordnungen) + CRUX-Gate. Triggers "wargame 4 teams", "haerte this claim", "red blue purple gray", automatisch vor Canon-Eintrag. CRUX-MK-aligned.
crux-mk: true
version: 1.0.0
aktiviert: 2026-04-18
triggers:
  - "wargame 4 teams"
  - "4-team wargame"
  - "haerte this claim"
  - "red blue purple gray"
  - "rbpg wargame"
  - "vor Canon-Eintrag (automatisch)"
  - "claim-hardening"
  - "kristall-audit"
---

# 4-Team-Wargame Skill [CRUX-MK]

**Kernidee:** Ein Claim ist erst dann Canon-reif, wenn er von 4 unabhaengigen Rollen ueberlebt. Dieser Skill automatisiert den Meta-Lern-Kristall-Prozess (Red/Blue/Purple/Gray) und gibt einen verdictbasierten Status zurueck, der mit cross-llm-simulation.md und crux-gate-grenzen.md konsistent ist.

Martin-Direktive 2026-04-18 (woertlich): *"das wissen das wissen zu wissen zu wissen zu wissen zu wissen koennen und dies alles bis in die 5 Ordnung und zwar mit Wargames geprueft aller 4 Teams damit ein Super System entsteht."*

**Bezug:** `Claude-Vault/areas/family/META-LERN-KRISTALL-5-ORDNUNGEN-SUPER-SYSTEM.md` definiert die Ordnungen; dieser Skill macht sie ausfuehrbar.

**Provenienz-Hinweis:** Kanonischer Skill-Pfad ist `~/.claude/skills/4-team-wargame/`. Diese Kopie liegt im Branch-Hub als Zweitkanal fuer andere Branches (per `rules/vault-bridge.md` + `rules/meta-harness.md` §8a). Wenn `~/.claude/skills/`-Schreibrechte zurueck verfuegbar: Datei dorthin kopieren, hub-sync macht den Rest.

---

## 1. Zweck + Wann nutzen

**Pflicht-Triggers (automatisch):**
- **Vor jedem Canon-Eintrag** (CRUX-Gate-Adversarial-Rolle, 2-Wargame-Regel).
- **Claim-Ordnung E3 oder hoeher** (Single-Team reicht nicht, `rules/crux-gate-grenzen.md`).
- **K_0- oder Q_0-relevante Entscheidung** (Kapital- oder Qualitaetsinvarianten beruehrt).

**Empfohlene Triggers (manuell):**
- Rule-Kandidat vor Aktivierung.
- Blueprint-Aufnahme mit Cross-Reference >= 2.
- Phronesis-Vorbereitung (Martin-Decision anstehend, Optionen brauchen Haertung).

**NICHT nutzen fuer:**
- Einmal-Tasks ohne Wiederverwendung (zu teuer, ~15-30 Min Setup).
- Tier-0-Facts mit direkter Messung (E1 empirisch, Cross-LLM reicht).
- Triviale Ja/Nein-Entscheidungen.

---

## 2. Die 4 Teams (Rollen-Definition)

Pro Claim spielen 4 Rollen sequenziell. Jede Rolle hat eine scharf definierte Funktion.

### Red (Falsifier)
**Auftrag:** Widersprueche, Edge-Cases, logische Luecken finden. Popper-Falsifikation.

**Prompt-Kern:**
- "Wie koennte dieser Claim falsch sein?"
- "Welche Situation widerlegt ihn?"
- "Welcher Edge-Case bricht die Invariante?"
- "Welche verdeckte Annahme traegt er?"

**Liefert:** 3-5 Angriffe, jeweils mit konkretem Gegenbeispiel oder logischer Luecke.

### Blue (Affirmer)
**Auftrag:** Evidenz, System-Konsistenz, Math-Stringenz sammeln. Lakatos-Schutzguertel.

**Prompt-Kern:**
- "Welche Daten stuetzen diesen Claim?"
- "Wie passt er in das bestehende System?"
- "Welche Theoreme / Formeln liefern ihn?"
- "Wie wird ein Red-Angriff beantwortet?"

**Liefert:** 3-5 Verteidigungen, jeweils mit Evidenz-Quelle (Datei-Pfad, Theorem-Referenz, empirische Beobachtung).

### Purple (Synthesizer)
**Auftrag:** Red + Blue integrieren zu staerkerer Version. Hegel-Dialektik (These / Antithese / Synthese).

**Prompt-Kern:**
- "Welcher Red-Angriff trifft, welcher nicht?"
- "Welche Blue-Verteidigung steht, welche wackelt?"
- "Wie laesst sich der Claim so reformulieren, dass er die validen Red-Angriffe ueberlebt?"
- "Wo sind Scope-Grenzen noetig?"

**Liefert:** Eine praezisierte Version des Claims (kann modifiziert sein) + explizite Scope-Annotationen.

### Gray (Outsider)
**Auftrag:** Paradigma-Wechsel, Querdomaenen-Check, Meta-Framing. Bricht die Zirkularitaet.

**Prompt-Kern:**
- "Wie wuerde ein Buddhist / Physiker / Ethnograph / Programmierer diesen Claim sehen?"
- "Welche andere Domaene hat aehnliches Problem anders geloest?"
- "Ist das Framing selbst das Problem?"
- "Was uebersieht der Purple-Synthesizer aus Innen-Perspektive?"

**Liefert:** 2-3 Querdomaenen-Perspektiven + 1 Meta-Framing-Einwand. Mindestens eine Quelle aus einer NICHT-Kemmer-Domaene (Philosophie, Naturwissenschaft, andere Kulturen).

---

## 3. Ablauf (6 Schritte)

### Schritt 1: Claim-Typ klassifizieren (E1-E5-Ordnung)

```
E1 = Objekt-Fakt (ueberpruefbar durch Messung)
E2 = Meta: Aussage ueber Validierungs-Methoden
E3 = Meta^2: Aussage ueber Methoden-Audit
E4 = Meta^3: Aussage ueber Audit-Kriterien
E5 = Meta^4: Struktur-Fixpunkt-Aussage
```

Klassifikations-Frage: **Worueber spricht der Claim?**
- Ueber die Welt = E1
- Ueber Validierungs-Methoden = E2
- Ueber Methoden-Audit = E3
- Ueber Audit-Kriterien = E4
- Ueber die Meta-Stack-Architektur = E5

**Tag im Output:** `ordnung: E3` (Pflicht-Feld).

### Schritt 2: Red-Runde (3-5 Angriffe)

Schreibe 3-5 separate Angriffe. Jeder Angriff = 1 Absatz mit:
- Angriffsvektor (Widerspruch, Edge-Case, Zirkularitaet, fehlende Evidenz, etc.)
- Konkretes Gegenbeispiel oder logische Argumentation
- Schaerfe-Level (mild / scharf / vernichtend)

### Schritt 3: Blue-Runde (3-5 Verteidigungen)

Fuer jeden Red-Angriff entweder:
- Direkte Widerlegung (mit Evidenz-Quelle)
- Eingestaendnis mit Scope-Praezisierung ("Angriff trifft bei X, aber Claim gilt nur fuer Y")
- Methodik-Korrektur (Claim wird reformuliert, nicht verworfen)

Zusaetzlich: System-Konsistenz-Check gegen bestehende Rules (CRUX, crux-gate-grenzen, cross-llm-simulation).

### Schritt 4: Purple-Synthese

Tabelle Red-Angriff x Blue-Antwort x Verdict:

| # | Red-Angriff | Blue-Antwort | Verdict |
|---|-------------|--------------|---------|
| 1 | ... | ... | TRIFFT / WIDERLEGT / PRAEZISIERT |

Schreibe dann die **praezisierte Version** des Claims (oft mit engerem Scope).

### Schritt 5: Gray-Perspektive (Querdomaenen)

Mindestens 2 Querdomaenen-Checks + 1 Meta-Framing-Einwand.
Mindestens eine Quelle aus NICHT-Kemmer-Domaene.

Frage am Ende: **Gibt es einen Paradigma-Wechsel der den Claim obsolet macht?**
Wenn ja: Claim-Reformulierung auf Meta-Ebene oder REJECT.

### Schritt 6: Verdict

Verdict-Matrix abhaengig von (Ordnung x Outcome):

| Ordnung | Red ueberlebt | Blue-Evidenz | Gray-Paradigma ok | Max-Verdict |
|---------|---------------|--------------|-------------------|-------------|
| E1 | ja | ja | ja | **HARDENED** |
| E1 | partiell | ja | ja | **CONDITIONAL** |
| E2 | ja | ja | ja | **HARDENED** |
| E2 | partiell | ja | ja | **CONDITIONAL** |
| E3 | ja | pragmatisch belegt | ja | **CONDITIONAL** (default) oder HARDENED (wenn rho-Gain empirisch) |
| E4 | ja | pragmatisch | ja | **CROSS-LLM-SIMULATION-HARDENED** (max) |
| E5 | ja (Fixpunkt) | zwingend-logisch | ja | **FIXPUNKT-HARDENED** |
| - | nein (vernichtend) | - | - | **REJECTED** |
| - | - | - | Paradigma-Problem | **REJECTED** oder Reframe |

**Wichtige Regeln:**
- Single-Instanz-Wargame maxt bei **CROSS-LLM-SIMULATION-HARDENED** (per `cross-llm-simulation.md` Regel 5).
- **Echter HARDENED-PRODUCTION** verlangt `multi-llm-parallel` zusaetzlich (siehe Sektion 5).
- **Meta-Meta (E3+)** ist per `crux-gate-grenzen.md` default CONDITIONAL, nur bei Selbst-Konsistenz + pragmatischem Nutzen HARDENED.

---

## 4. Verdict-Matrix (kompakt)

```
HARDENED                 = E1/E2, alle 4 Teams ueberlebt, Cross-LLM vorliegt
CONDITIONAL              = E1-E3, 1-2 Red-Angriffe partiell treffen, Scope praezisiert
CROSS-LLM-SIM-HARDENED   = E4 oder Single-Instanz, 4-Team-Process komplett, pragmatisch nutzbar
FIXPUNKT-HARDENED        = E5, Selbst-Konsistenz bewiesen, strukturell-logisch zwingend
HARDENED-PRODUCTION      = HARDENED + Multi-LLM-Real + Produktions-Stichprobe (separat)
REJECTED                 = Red vernichtet oder Gray-Paradigma-Break
```

**Supersession:** Neuer Claim mit besserem Wargame kann alten CONDITIONAL zu HARDENED promoten. Alter HARDENED wird nie automatisch demotiert (nur bei neuem widersprechenden Cross-LLM-Run).

---

## 5. Integration mit Cross-LLM-Simulation-Rule und wargame-v7

Dieser Skill simuliert 4 Rollen im selben Modell (Opus 4.7). Das ist **Simulation**, nicht echter Multi-LLM-Run.

**Konsequenzen (per `rules/cross-llm-simulation.md`):**
- Max-Verdict dieses Skills allein: **CROSS-LLM-SIMULATION-HARDENED**
- Fuer echte HARDENED: nachgeschaltet `multi-llm-parallel` nutzen (Claude + Copilot + ChatGPT + Grok + Perplexity).
- Fuer HARDENED-PRODUCTION: zusaetzlich externer Benchmark + Produktions-Stichprobe.

**Abgrenzung zu `wargame` (v7, strategisch):**
- `wargame` v7 = strategisches Wargaming im Clausewitz/Moltke/Shannon-Stil, breit (Musashi, 36 Strategeme, 20 Sprachen).
- `4-team-wargame` = claim-spezifisches Hardening mit fester Rollen-Anzahl (4) und Ordnungs-Klassifikation (E1-E5).
- Beide ko-existieren: `wargame` fuer strategische Szenarien (ganze Initiativen), `4-team-wargame` fuer einzelne Claims/Rules/Fragments.

**Abgrenzung zu `mathebuch-wargame`:**
- `mathebuch-wargame` = domain-specific fuer Buch-Kapitel-Haertung.
- `4-team-wargame` = domain-agnostisch, fuer beliebige Claims.

**Pipeline (wenn echter Multi-LLM gewuenscht):**
```
Schritt 1: 4-team-wargame (Simulation, ~20 Min)
Schritt 2: multi-llm-parallel mit Prompt aus Schritt 1 (~60 Min, Martin-faehrt)
Schritt 3: Claim-Level-Consensus aggregieren (>=3 von 5 LLMs ADOPT = HARDENED)
Schritt 4: Canon-Eintrag mit Multi-LLM-Log als Evidenz
```

---

## 6. Template-Output (Markdown-Schema)

Pro Wargame schreibe eine Datei `wargame-<slug>-<YYYY-MM-DD>.md` mit folgendem Frontmatter + Body:

```markdown
---
type: wargame
domain: <sae | 9os | heylou | kpm | meta | ...>
lifecycle: canonical
crux-mk: true
datum: <YYYY-MM-DD>
autor: <Instanz-ID>
scope: 4-Team-Wargame (RBPG) auf <Claim-Kurztitel>
claim: "<voller Claim-Text>"
ordnung: E<1-5>
verdict: <HARDENED | CONDITIONAL | CROSS-LLM-SIM-HARDENED | FIXPUNKT-HARDENED | REJECTED>
aktiviert: <YYYY-MM-DD oder "pending">
---

# 4-Team-Wargame: <Claim-Kurztitel> [CRUX-MK]

## Claim (zu haerten)
<voller Claim-Text, praezise>

## Ordnung
E<1-5> - Begruendung: <1 Zeile>

## Red-Team Angriffe

### R1: <Angriffs-Titel>
<Beschreibung, 2-4 Saetze>

### R2: ...

## Blue-Team Verteidigungen

### B1 (vs R1): <Verteidigungs-Titel>
<Beschreibung mit Evidenz-Quelle>

### B2 (vs R2): ...

## Purple-Synthese

| # | Red | Blue | Verdict |
|---|-----|------|---------|
| 1 | R1 | B1 | TRIFFT / WIDERLEGT / PRAEZISIERT |
| 2 | R2 | B2 | ... |

**Praezisierte Claim-Version:**
> <reformulierter Claim mit engerem Scope oder bestaetigte Original-Version>

## Gray-Perspektive

### Querdomaene 1: <Name>
<Perspektive>

### Querdomaene 2: <Name>
<Perspektive>

### Meta-Framing-Einwand
<Kritik am Framing selbst>

## CRUX-Check

- K_0: <geschuetzt / neutral / beruehrt>
- Q_0: <geschuetzt / neutral / beruehrt>
- I_min: <erhoeht / neutral / gesenkt>
- W_0: <Wissenszuwachs-Effekt>
- MHC: <Martin-Override-Pfad falls noetig>

## Verdict

**<HARDENED | CONDITIONAL | CROSS-LLM-SIM-HARDENED | FIXPUNKT-HARDENED | REJECTED>**

Begruendung: <2-3 Saetze>

Naechste Schritte (falls CONDITIONAL):
- [ ] Multi-LLM-Parallel-Run fuer echte HARDENED
- [ ] Rule-Aenderung falls Purple-Synthese Reformulierung verlangt
- [ ] Fragment-/Blueprint-Aufnahme bei Cross-Reference >= 2

[CRUX-MK]
```

---

## Speicherort fuer Wargame-Outputs

- **Canon-Kandidat:** `branch-hub/findings/WARGAME-4T-<slug>-<datum>.md`
- **Vault-Spiegel (auto via `hub-sync.ps1`):** `Claude-Vault/resources/_from-hub/findings/`
- **Inbox (wenn noch nicht Canon):** `branch-hub/inbox/to-<addressee>.md` + Link auf Wargame

---

## Anti-Muster (REJECTED)

- **3-Team-Wargame** (ohne Gray) = Zirkularitaets-Risiko, Gray ist Pflicht.
- **Red ohne konkrete Gegenbeispiele** = Hand-waving, nicht akzeptabel.
- **Blue ohne Evidenz-Quelle** = Bestaetigungs-Bias.
- **Purple-Synthese ohne Scope-Annotation** = verdeckte Praezisierung.
- **Gray ohne NICHT-Kemmer-Domaene** = Zirkel-Schluss.
- **HARDENED-Verdict auf E3+** ohne crux-gate-grenzen-Ausnahme = Regel-Verletzung.
- **Single-Instanz-HARDENED** ohne Cross-LLM-Real = cross-llm-simulation.md-Verletzung.

---

## SAE-Isomorphie

Dieser Skill ist die Meta-Harness-Instanziierung des Trinity-Patterns + Gray-Outsider:
- Red + Blue + Purple = 3-Varianten-Governance (Conservative / Aggressive / Contrarian analog).
- Gray = externer Auditor (COSMOS-Isomorphie).
- Verdict-Matrix = q-Normalisierung auf Meta-Ebenen (`rules/crux-gate-grenzen.md` §SAE-Isomorphie).

## CRUX-Bindung

- **K_0:** geschuetzt durch Pflicht-Wargame vor K_0-Aktionen.
- **Q_0:** erhoeht durch strukturierte Haertung (keine Canon-Eintraege ohne 4-Team-Ueberlebung).
- **I_min:** direkt erhoeht (Wargame-Template = I_min-Baustein).
- **W_0:** Hauptzweck (Wissens-Akkumulation durch HARDENED-Claims).
- **MHC:** Martin kann jedes Verdict overrideen (Phronesis, L13 nicht delegiert).

## Version / Changelog

- **v1.0.0 (2026-04-18):** Initial Release. Basiert auf META-LERN-KRISTALL-5-ORDNUNGEN-SUPER-SYSTEM.md + `rules/crux-gate-grenzen.md` + `rules/cross-llm-simulation.md`. Erste Anwendung auf E4-Fixpunkt-1 (Selbst-Konsistenz als Fixpunkt-Kriterium) dokumentiert in `example-e4-fixpunkt-1.md`.

[CRUX-MK]
