# Claude-Execution-Priority [CRUX-MK]

**Lernsatz (Martin-Feedback 2026-04-18T16:15):**
> "das ist das übrigens was ich meine dies hätest du alles machen können"

Anlass: `npm install -g @google/gemini-cli` und `npm install -g @openai/codex` — hätte ich direkt via Bash-Tool selbst ausführen können. Stattdessen habe ich Martin Copy-Paste-Commands gegeben und auf seine Ausführung gewartet. Resultat: Martin wartet, Zeitwert-Verlust, Frust.

## Regel: Self-Execute-First-Check vor Copy-Paste

**Vor JEDEM Copy-Paste-Command an Martin:** Pruefe in dieser Reihenfolge:

1. **Kann ich den Command via Bash-Tool selbst ausfuehren?**
   - Installationen (`npm install`, `pip install`, `winget install`)
   - Datei-Operationen (mv, cp, mkdir, chmod)
   - Git-Operationen (`git status`, `git add`, `git commit`, `git push` falls Token da)
   - Build-/Test-Commands (`pytest`, `npm run build`)
   - Verifikationen (`--version`, `which`, `ls`, `Test-Path`)
   - Config-Reads (`cat`, `grep` — NEIN, dedizierte Tools: Read, Grep)
   - **→ Wenn JA: selbst ausfuehren, nicht Martin bitten**

2. **Braucht der Command Browser-Interaktion oder persoenliche Credentials?**
   - OAuth-Logins (`codex login`, `gh auth login` mit Browser-Flow)
   - Interaktive CLIs mit Google/MS-Auth
   - Subscriptions-aktivierung (Martin-Kreditkarte)
   - **→ Wenn JA: Martin-Aktion noetig, klar kommunizieren**

3. **Ist der Command System-weit (Admin, HKLM)?**
   - `SetEnvironmentVariable` mit Machine-Scope
   - Service-Management
   - **→ Wenn JA: Martin-Aktion (mit Admin-PowerShell)**

4. **Ist der Command destruktiv ohne Undo?**
   - `rm -rf`, `git push --force`, `DROP DATABASE`
   - **→ Wenn JA: Martin-Approval explizit holen vor Ausfuehrung**

## Konkret: Fall A = Selbst-Execute

```
- winget install / npm install / pip install: SELBST (Bash-Tool)
- git clone / git status / git diff: SELBST
- pytest / npm test: SELBST
- Datei-Verifikation (Test-Path, ls): SELBST
- Environment-Checks (where, Get-Command): SELBST via Bash
- mkdir / cp / mv: SELBST
- JSON-Merges, Config-Patches: SELBST via Edit-Tool
```

## Konkret: Fall B = Martin-Aktion

```
- codex login (OAuth-Browser): Martin
- gh auth login (Browser-OTP): Martin  
- gemini (interaktive CLI, Google-Auth): Martin
- copilot /login (Browser-OAuth): Martin
- Subscriptions-Kauf: Martin
- Admin-Scope-System-Aenderungen (HKLM): Martin
- PC-Neustart: Martin
- Terminal-komplett-schliessen+neu: Martin
```

## Anti-Muster

- **"Kopiere diesen Command + führe aus + poste Ergebnis"** wenn ich es selbst kann
- **"Lass uns checken"** als Vorwand fuer Martin-Arbeit
- **Instruktions-Ketten** die Martin sequenziell durchgehen muss wenn 1 Bash-Call sie macht

## Mechanisch

Bei jeder Copy-Paste-Instruktions-Drafting:
1. Frage: **Kann ich das via Bash-Tool in der Claude-Session machen?**
2. Wenn JA und nicht destruktiv: Selbst ausfuehren, Ergebnis berichten.
3. Wenn NEIN (Browser/Credentials/Admin/destruktiv): Erst dann Martin-Instruktion.
4. Wenn UNKLAR: Probieren (Bash-Call), bei Fehler graceful degrade auf Martin.

## rho-Wirkung

- Eingesparte Martin-Zeit pro geretteter Instruktion: 2-10 Min
- Lambda: jede Session >= 5 potenzielle Self-Execute-Chancen
- rho-Gain: +100-500 EUR pro Session, kumulativ substantiell

## SAE-Isomorphie

Dies ist **Kulminationspunkt-Schutz** fuer Martin-Bandwidth: jede Martin-Copy-Paste-Aktion verbraucht Engpass-Ressource. Self-Execute lagert auf nicht-Engpass-Ressource (Claude-Tool-Call).

## CRUX-Bindung

- **K_0**: geschuetzt (keine Fehl-Installs durch Martin bei Copy-Paste-Mistakes)
- **Q_0**: erhoeht (verlaesslichere Ausfuehrung via Tool-Tests)
- **W_0**: besser genutzt (Claude-Arbeitszeit statt Martin-Wartezeit)
- **rho**: direkt positiv (h*W-Faktor reduziert durch weniger Wartezeit)

[CRUX-MK]
