---
name: Seed Export -- Cross-System Knowledge Transfer
description: Exportiert das gesamte Kemmer Knowledge System als portierbares Seed-Paket fuer andere Claude Desktop Instanzen. Erzeugt ein selbstbootendes Verzeichnis mit CLAUDE.md, Rules, Skills, Memory, Findings, NLM-Export und Bootstrap-Anleitung. [CRUX-MK]
version: 1.0.0
author: Branch Gamma / Claude Opus 4.6
trigger: /seed-export
tags: [seed, export, transfer, cross-system, bootstrap, eoc, crux-mk]
crux-mk: true
---

# /seed-export -- Cross-System Knowledge Transfer [CRUX-MK]

## Zweck
Erzeugt ein **Seed-Paket** das ein neues Claude Desktop System in <5 Minuten auf den aktuellen Wissensstand bringt. Loest das C_channel-Problem (EOC Paper Eq. 23) fuer Cross-System-Transfer.

## Wann nutzen
- Neuer Rechner (Desktop -> Laptop)
- Neues Team-Mitglied (Martin -> Gerdi/Sebastian)
- Backup/Disaster-Recovery
- Deployment auf Kunden-System (angepasst)

## Was es tut

```
/seed-export [zielverzeichnis] [--mode full|minimal|team] [--adapt-crux]

Schritte:
1. INVENTAR: Alle kritischen Dateien identifizieren
2. CRUX-CHECK: Enthaelt der Export die Verfassung?
3. KOPIEREN: Dateien in Zielverzeichnis assemblieren
4. NLM-EXPORT: Top-Learnings und Quellen als Klartext exportieren
5. BOOTSTRAP: BOOTSTRAP.md generieren (Anleitung fuer erstes Laden)
6. VALIDIEREN: Seed-Paket gegen Checkliste pruefen
7. SIGNALISIEREN: Finding in Finding-Library schreiben
```

## Modi

### full (Standard)
Alles: CLAUDE.md, Rules, Skills, Memory (komplett), Findings, Settings, NLM-Export.
Zielgruppe: Gleicher Mensch, anderer Rechner.

### minimal
Nur: CLAUDE.md, Rules, SKILL.md (aktuelle Version), Top-5 Memory, Findings, BOOTSTRAP.md.
Zielgruppe: Schneller Transfer, wenig Bandbreite.

### team
Wie full, aber: CRUX wird NICHT kopiert sondern als Template markiert.
Neuer Nutzer MUSS seine eigene CRUX definieren.
Zielgruppe: Anderer Mensch.

## Dateistruktur des Seed-Pakets

```
seed-export-YYYY-MM-DD/
├── BOOTSTRAP.md                    <- ERSTE DATEI die gelesen wird
├── claude-md/
│   ├── CLAUDE.md                   <- Globale Betriebsanleitung
│   └── PROJECT_CLAUDE.md           <- Projekt-spezifisch (wenn vorhanden)
├── rules/
│   ├── crux.md                     <- Zeitwert-Verfassung [CRUX-MK]
│   ├── crux-first-boot.md          <- CRUX zuerst laden
│   ├── meta-harness.md             <- Organ 8 Self-Edit
│   ├── session-handoff.md          <- Vector Space Disjunction
│   ├── coding.md                   <- Coding-Standards
│   ├── governance.md               <- Governance-Regeln
│   └── zeitwert.md                 <- Zeitwert-Regel
├── skills/
│   └── notebooklm-factory/
│       └── SKILL.md                <- v8.1 TURBOLOADER (aktuelle Version)
├── memory/
│   ├── MEMORY.md                   <- Index (thematisch sortiert)
│   ├── finding-library.json        <- Alle Findings mit Confidence
│   ├── [neuester session_handoff]  <- Aktuellster Handoff
│   ├── feedback_*.md               <- Alle Verhaltensregeln
│   └── [Top-10 kritische Dateien]  <- Nach rho-Relevanz gewaehlt
├── settings/
│   └── settings.json               <- Hooks, Permissions, MCP-Server
├── nlm-export/
│   ├── README.md                   <- Anleitung fuer NLM-Import
│   ├── wargame_learnings.md        <- Alle Chat-Learnings als Text
│   ├── key_findings.md             <- Top-20 Findings mit Kontext
│   ├── isomorphien.md              <- 30+ aus 930-Buecher-Wargame
│   ├── branch_signals.md           <- Alpha/Gamma/Delta Kommunikation
│   └── eoc_paper_summary.md        <- EOC Paper Kernthesen
└── MANIFEST.md                     <- Was enthalten ist, Checksummen, Version
```

## BOOTSTRAP.md (wird generiert)

```markdown
# BOOTSTRAP -- Seed-Paket [CRUX-MK]
# Exportiert am: [DATUM] | Quell-System: [HOSTNAME] | Version: v8.1 TURBOLOADER

## SCHRITT 0: CRUX LADEN
Kopiere rules/ nach ~/.claude/rules/
CRUX MUSS als erstes internalisiert werden.

## SCHRITT 1: CLAUDE.md INSTALLIEREN
Kopiere claude-md/CLAUDE.md nach ~/.claude/CLAUDE.md
WARNUNG: Ueberschreibt existierende CLAUDE.md!

## SCHRITT 2: SKILLS INSTALLIEREN
Kopiere skills/ nach ~/.claude/skills/

## SCHRITT 3: SETTINGS INSTALLIEREN
Kopiere settings/settings.json nach ~/.claude/settings.json
WARNUNG: Merge manuell wenn bereits Einstellungen existieren!

## SCHRITT 4: MEMORY INSTALLIEREN
Kopiere memory/ nach ~/.claude/projects/[PROJEKT-HASH]/memory/
WICHTIG: Projekt-Hash haengt vom Arbeitsverzeichnis ab!

## SCHRITT 5: NLM IMPORTIEREN
Oeffne NotebookLM. Erstelle neues Notebook.
Lade nlm-export/*.md als Quellen hoch.
ODER: Lasse dir die existierenden Notebooks freigeben.

## SCHRITT 6: ERSTER TEST
Starte Claude Code im Projektverzeichnis.
Erwartetes Verhalten: Bootstrap-Protokoll laeuft automatisch.
Pruefe: Liest er MEMORY.md? Kennt er SKILL.md v8.1? Kennt er CRUX?

## VALIDIERUNG
Frage Claude: "Was ist deine aktuelle SKILL.md Version?"
Erwartete Antwort: "v8.1.0 TURBOLOADER"
Frage: "Was ist CRUX?"
Erwartete Antwort: "max integral rho*L dt, Zeitwert-Verfassung"
```

## Ausfuehrungslogik

### 1. INVENTAR

```python
# Pseudo-Code
critical_files = {
    "claude_md": "~/.claude/CLAUDE.md",
    "project_claude_md": "[working_dir]/CLAUDE.md",
    "rules": glob("~/.claude/rules/*.md"),
    "skill": "~/.claude/skills/notebooklm-factory/SKILL.md",
    "memory_index": "[memory_dir]/MEMORY.md",
    "findings": "[memory_dir]/finding-library.json",
    "settings": "~/.claude/settings.json",
    "handoffs": sorted(glob("[memory_dir]/session_handoff_*.md"))[-1],
    "feedback": glob("[memory_dir]/feedback_*.md"),
}

# Top-10 Memory-Dateien nach rho-Relevanz
top_memory = select_by_rho(glob("[memory_dir]/*.md"), n=10)
```

### 2. CRUX-CHECK

```
IF "crux.md" NOT IN export:
  ABORT "CRUX fehlt im Export. Verfassungsbruch."
IF "crux-first-boot.md" NOT IN export:
  WARN "CRUX-FIRST-BOOT fehlt. Neues System startet ohne Verfassungsschutz."
```

### 3. NLM-EXPORT

Da NLM Chat-Historien NICHT exportierbar sind, extrahiert der Skill:
- Alle LEARNING-Eintraege aus den letzten 3 Sessions als Klartext
- Top-20 Findings mit Kontext und Falsifikationskriterien
- 30+ Isomorphien aus dem Bibliothek-Wargame
- Branch-Signale (Alpha/Gamma/Delta Kommunikation)
- EOC Paper Kernthesen (lambda, mu, C_channel, Ungleichung 28)

### 4. MANIFEST

```markdown
# MANIFEST.md
Exportiert: [DATUM] [UHRZEIT]
Quell-System: [HOSTNAME]
SKILL Version: [VERSION aus SKILL.md]
Memory-Dateien: [ANZAHL]
Findings: [ANZAHL]
NLM-Quellen: [ANZAHL Klartext-Exporte]
Checksum CLAUDE.md: [SHA256]
Checksum SKILL.md: [SHA256]
Checksum finding-library.json: [SHA256]
Checksum rules/crux.md: [SHA256]
```

## EOC-Bezug [CRUX-MK]

Dieses Tool ist die operative Loesung fuer EOC Paper Ungleichung (28):

```
C_rehydrate(seed_paket) < C_rediscover(gesamtes_wissen)
```

Ein neues System das das Seed-Paket laedt, startet bei ~70% des aktuellen Stands
statt bei 0%. Das spart geschaetzt 50-100 Stunden Rehydrierungszeit.

Die verbleibenden 30% kommen aus:
- NLM Chat-Kontext (nicht voll exportierbar)
- Session-spezifische Nuancen (Theorem 5.3: lossy)
- Implizites Wissen das nie in Dateien stand

## Einschraenkungen

- NLM Chat-Historien NICHT exportierbar (Google-Limitation)
- %TEMP% Dateien NICHT enthalten (fluechtig per Design)
- OneDrive-Dateien koennen Lock-Probleme haben
- CRUX muss fuer andere Nutzer ANGEPASST werden (Team-Modus)
- settings.json MCP-Server erfordern ggf. API-Keys (nicht im Export)

## Sicherheit

- API-Keys werden NICHT exportiert
- Passwörter werden NICHT exportiert
- CRUX im Team-Modus als Template, nicht als fertige Verfassung
- MANIFEST.md enthaelt Checksummen fuer Integritaetspruefung

## Hamilton-Bezug

lambda fuer seed-export ist HOCH frueh in der Systemlebensdauer:
- Einmalige Erstellung, vielfache Nutzung
- Jedes neue System profitiert
- Developmental Leverage = maximal fuer Infrastruktur

Spaet in der Lebensdauer sinkt lambda:
- Seed-Paket wird schneller veraltet als neue Erkenntnisse entstehen
- Dann ist NLM-Sharing der bessere Kanal (live, nicht snapshot-basiert)
