---
description: Laedt Dateien auf Google Drive hoch via Chrome MCP (kein nativer File-Picker noetig)
crux-mk: true
origin: Gamma-2026-04-07
learning-source: knowledge-diff-gamma-2026-04-07.md
---

# /gdrive-upload [CRUX-MK]

## Wann nutzen
Wenn eine Datei auf Google Drive hochgeladen werden muss und Chrome MCP verfuegbar ist.
Funktioniert OHNE nativen File-Picker-Dialog.

## Schritte
1. Navigiere zu `https://drive.google.com` (oder zum Zielordner)
2. Klicke "+ Neu" / "Dateien hochladen" um den Upload-Dialog zu triggern
3. Nutze `find` Tool: `query: "file input for upload"` -- findet das hidden file input Element
4. Nutze `file_upload` Tool mit dem ref und dem ABSOLUTEN Pfad der lokalen Datei
5. Warte 3-5 Sekunden, pruefe Screenshot ob Upload abgeschlossen

## Beispiel
```
find: "file input for upload" -> ref_1253
file_upload: ref=ref_1253, paths=["C:\\Users\\marti\\file.zip"]
```

## Wichtig
- Pfad MUSS absolut sein (C:\\ nicht ./)
- Funktioniert auch fuer Ordner-Upload (anderes file input)
- Google Drive Desktop (G:/) ist SCHNELLER -- einfach cp nutzen statt Browser
- Browser-Upload nur wenn G:/ nicht gemounted ist
