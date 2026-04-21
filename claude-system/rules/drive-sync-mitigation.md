# Drive-Sync-Mitigation (Option D) [CRUX-MK]

**Zweck:** Verhindert Drive-Sync-Chaos bei parallelen Claude-Sessions.
**Quelle:** `branch-hub/findings/FINDING-DRIVE-SYNC-CHAOS-2026-04-18.md`
**Aktiviert:** 2026-04-18 durch Martin-Approval "erst mal Option D dann Option A"

## Hintergrund

Google Drive File Stream hat **keine Merge-Auflösung** bei gleichzeitigen Edits.
Bei Konflikt erzeugt es Kaskaden-Duplikate `<name> (1) (1) (1)...` (real gemessen:
35+ in `Subnautica-Fragment-Map-Ergaenzung-H-Welle-5.md`, 60+ in `MOC-Fragment-Map.md`).

## Regel 1: Instanz-getrennte Workspaces fuer WIP

Jede aktive Session hat einen eigenen Unterordner fuer Work-in-Progress-Writes:

- `areas/family/instance-a/` fuer Instanz A (NLM-Welle-Scan)
- `areas/family/instance-b/` fuer Instanz B (Formel-Sweep)
- Neue Instanzen: `instance-c/`, `instance-d/`, ...

**WIP-Writes** (Drafts, Skizzen, Session-Reports, unfertige Decisions) gehen
in den Instanz-Ordner.

## Regel 2: Canon-Dateien brauchen BEACON-Mutex

Dateien die **mehrere Sessions lesen** (Fragment-Map-Master, MOCs,
REGISTRY, BEACON) werden nur von einer Session gleichzeitig geschrieben.

Ablauf vor Canon-Write:
1. Read BEACON (aktuell)
2. Pruefe: Hat andere Session die Datei in den letzten 5 Min modifiziert?
3. Wenn JA: 5 Min warten oder in Instanz-Ordner auslagern
4. Wenn NEIN: Write + sofort BEACON updaten mit Lock-Info

## Regel 3: Eindeutige Datei-Namen bei parallelen Additiven

Fragment-Map-Ergaenzungen heissen mit Zweck-Suffix (nicht nur Buchstabe):

Beispiele (bereits umgesetzt):
- `Subnautica-Fragment-Map-Ergaenzung-G-Welle-4.md` (Instanz A)
- `Subnautica-Fragment-Map-Ergaenzung-H-Welle-5.md` (Instanz A)
- `Subnautica-Fragment-Map-Ergaenzung-I-Formel-Sweep.md` (Instanz B)
- Zukuenftig: `-J-Welle-6`, `-K-Nebenbedingungs-Sweep`, etc.

## Regel 4: Bei Drive-Sync-Kollision sofort reporten

Wenn Write-Tool mit "File has been modified since read" blockt:
1. **NICHT** retry-spammen
2. Read die Datei neu (aktueller Stand)
3. Entscheide: Overwrite wuerde Parallel-Session-Arbeit zerstoeren?
4. Bei Overwrite-Risiko: **Martin eskalieren**, nicht autonom schreiben

## Regel 5: Cleanup-Kadenz

Drive-Sync-Duplikate akkumulieren nach Pattern `*(N).md` oder `*(N) (M).md`.

- **Manuell alle 48h**: Glob `*(*).md`, SHA-Verify, identische loeschen
- **Dark-Factory-04 (geplant)**: taeglich 06:00 vor hub-sync.ps1
- **Tests vor Cleanup**: niemals Datei ohne Original-Version loeschen

## Regel 6: Vor jedem Write Glob-Pre-Check

Vor Write in `areas/family/` oder `00-moc/` oder `branch-hub/findings/`:

```
glob target_dir/<filename-stem>*.md
```

Wenn mehr als 1 Datei zurueckkommt (Duplikate existieren): **Warning in Chat**, dann
informierte Entscheidung treffen (Hotfix via Rule 2-4).

## Regel 7: Session-Ende-Merge

Am Session-Ende der jeweiligen Instanz:
1. Reife Artefakte aus `instance-<id>/` in Canon-Ordner promoviert
2. Promotion wird in BEACON dokumentiert ("Canon-Promotion: X.md aus instance-b/")
3. `instance-<id>/` bleibt mit archivierten unreifen Artefakten

## SAE-Isomorphie

- **MYZ-32 Dispatcher**: Events werden nach Agent-Class geroutet.
  Hier: Writes werden nach Session-Instanz geroutet.
- **Trinity-Slot-Promotion**: Agenten werden aus Challenger-Pool in aktive Slots promoviert.
  Hier: Artefakte werden aus `instance-<id>/` in Canon-Ordner promoviert.
- **Shannon-Entropy**: Jede Instanz hat disjunkte Schreib-Domaene
  = niedrige Konflikt-Entropie.

## Warum das nicht Option A ersetzt

Option D ist **Hotfix** (billig, sofort, nicht destruktiv).
Option A (Git-Backend) ist **Architektur-Loesung** (mittelfristig).

Option D waehrend Option-A-Migration laeuft. Nach Option-A-Live wird Option D entweder:
- Teil des Git-Workflows (Branch pro Instanz) → formalisiert
- Oder abgeschaltet → Git-Merge uebernimmt Konflikt-Resolution

Martin entscheidet zum Option-A-Go-Live.

## CRUX-Bezug

- **K_0**: indirekt geschuetzt (Vault-Integritaet → keine Falsch-Steuer-Berechnung aus Duplikaten)
- **Q_0**: direkt geschuetzt (Canon-Konsistenz)
- **I_min**: direkt geschuetzt (strukturierte Ordnung der Writes)
- **rho**: Spart ~2-5h pro paralleler Session-Stunde = 500-1500 EUR/Session

[CRUX-MK]
