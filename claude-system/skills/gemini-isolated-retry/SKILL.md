---
name: gemini-isolated-retry
description: Fuehrt Gemini-CLI-Call in isolierter /tmp CWD mit Anti-Kontaminations-Klausel + Post-Call-Audit durch. Verhindert Gemini-File-Access-Rueckkopplung bei Cross-LLM-Runs. Empirisch belegt 2x in Welle-1/Welle-2.
type: skill
meta-ebene: E3
claim-type: empirical
falsification-condition: "Wenn >= 5 Calls bei CWD=/tmp dennoch Workspace-Referenzen in Gemini-Output enthalten (Post-Call-Audit positiv), Hypothese verworfen"
crux-mk: true
version: 1.0.1
created: 2026-04-19
triggers:
  - "gemini isolated"
  - "gemini retry sauber"
  - "cross-llm gemini unabhaengig"
  - automatisch bei jedem Gemini-Cross-LLM-Call (Pre-Flight-Hook-Kandidat)
---

# Skill: gemini-isolated-retry [CRUX-MK]

## Zweck
Gemini-CLI mit Workspace-Access hat empirisch belegte Datei-Lese-Tendenz. Bei Cross-LLM-Runs im Kemmer-Vault-Verzeichnis kann dies zu Rueckkopplung fuehren: Gemini zieht bestehende Claude-/Session-Artefakte als "externe Evidenz" heran und erzeugt Schein-Konvergenz statt unabhaengiger Cross-LLM-Haertung. Dieser Skill kapselt das 5-Schritt-Protokoll (Isolated-CWD + Anti-Kontaminations-Klausel + Post-Call-Audit) fuer saubere Cross-LLM-Runs.

## 5-Schritt-Protokoll

### Schritt 1: CWD-Wechsel
`cd /tmp` vor jedem Gemini-Call. Entzieht Gemini den Workspace-Lese-Scope mechanisch. Kein Opt-in-Vertrauen auf Prompt-Hardening allein.

### Schritt 2: Prompt-Hardening
Fuegen zum User-Prompt hinzu:
```
WICHTIG: Antworte NUR aus deinem Wissensstand. KEINE Dateien im Workspace lesen. Keine Suche nach bestehenden Files. Cross-LLM-Unabhaengigkeit ist kritisch. Lambda-Honesty bei Unsicherheit.
```

### Schritt 3: GEMINI_API_KEY aus User-Env
```
KEY=$(powershell.exe -Command "[Environment]::GetEnvironmentVariable('GEMINI_API_KEY', 'User')" 2>/dev/null | tr -d '\r\n')
```

### Schritt 4: Call
```
echo "$PROMPT" | GEMINI_API_KEY="$KEY" gemini -p "Adversarial kompakt DE." > /tmp/<claim>-gemini.out 2> /tmp/<claim>-gemini.err
```

### Schritt 5: Post-Call-Audit
Pruefen ob Output kontaminiert ist:
- grep Output nach `/Meine Ablage`, `Claude-Knowledge-System`, branch-/session-spezifischen Namen
- 0 Matches = SAUBER, 1+ Match = KONTAMINIERT, Retry noetig

## Fehler-Behandlung
- Rate-Limit 429: 2-min-Wait, max 1 Retry
- Key-Env leer: Fehler + Abbruch
- stderr-Prozess-Fehler: stdout kann trotzdem Content haben (Codex-Parallele Erfahrung)

## Belegung
- F412 Fragment-Map-Ergaenzung-S
- Welle-1 Kontamination: Token-Economics-Run 2026-04-18 (SCHEIN-KONVERGENT)
- Welle-2 Sauber: Paket-12-Retry + Token-Economics-Retry 2026-04-19 (beide ECHT-UNABHAENGIG)

## rho-Impact
30-60k EUR/J systemisch (verhindert false HARDENED-Claims die Rollbacks erzwingen).

## Anti-Patterns
- Gemini-Call ohne CWD-Wechsel
- Prompt ohne Anti-Kontaminations-Klausel
- Keine Post-Call-Audit-Verifikation
- "Sieht plausibel aus also ist es sauber"-Annahme

## SAE-Isomorphie
Bounded-Veto auf LLM-Ebene (myz33). Gemini-Toolchain wird mechanisch beschraenkt.

[CRUX-MK]
