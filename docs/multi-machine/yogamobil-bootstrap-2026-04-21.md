---
type: handoff
title: YogaMobil Bootstrap — Fortsetzung Worker0001-Arbeit + Multi-Machine-Learnings
from: Worker0001 @ RazorBuero (PC 3)
to: Nachfolger-Claude @ YogaMobil
date: 2026-04-21
status: AKTIV (Handoff-Write in progress, keine Kulmination)
crux-mk: true
---

# Handoff an YogaMobil [CRUX-MK]

## WICHTIG: Existierende YogaMobil-Seeds beachten
YogaMobil hat bereits **ZWEI** Seed-Pakete. Dieses hier ist das **juengere** (Stand 2026-04-21).

1. `Claude-Knowledge-System/BOOTSTRAP-YOGAMOBIL.md` (OffRazerAlpha 2026-04-17) — **Basis-Bootstrap** (7 Schritte: Rules, CLAUDE.md, Skills, Settings, Memory-Seed, Obsidian, Branch-Hub)
2. `Claude-Knowledge-System/HANDOFF-YOGAMOBIL-2026-04-17.md` (OffRazerAlpha) — Stand 2026-04-17
3. **Dieses File (2026-04-21)** — Multi-Machine-Aware-Update: Blueprint + Setup-Paket-Learnings + Worker0001-Deliverables

**Read-Order:** erst BOOTSTRAP-YOGAMOBIL.md (Basis), dann dieses File (Ergaenzung 2026-04-20/21).

## Ein-Zeilen-Zusammenfassung
Du erbst **4 Tage Arbeit seit dem Seed**: Multi-Machine-Blueprint + Worker0001-Session (5 Migration-Indexe + Self-Healing-Proposal) + 2 Work-D2-Wargames + RASCI v5 (nicht v4!) ist Canon. 4 Martin-Bloecke offen.

## Warum dieser Handoff existiert
Martin hat Option C gewaehlt (Worker0001 arbeitet autonom auf PC3/RazorBuero). Session brach ab bevor CLIs voll-installiert waren. Martin wechselt auf YogaMobil — **nicht weil RazorBuero kaputt ist**, sondern weil Mobilitaet. Alle Artefakte auf Drive-G + GitHub-Repo sind sichtbar.

## Bootstrap-Reihenfolge (PFLICHT) fuer YogaMobil

### Read-Order
1. **Dieses File** (du liest es gerade)
2. `branch-hub/handoffs/multi-machine-setup-package-v1-2026-04-20.md` — CLIs, Env-Vars, Subscriptions, Admin-Rechte
3. `branch-hub/handoffs/multi-machine-coordination-v1-2026-04-20.md` — MR-1 bis MR-8, Worker/Master-Dichotomie
4. `Claude-Vault/areas/family/instance-worker0001-pc3/migration-index-MASTER.md` — 5 Vorgaenger-Sessions + 23 Learnings + Cross-Graph
5. `branch-hub/proposals/Self-Healing-Dark-Factories-v1-2026-04-20.md` — warum DFs ohne SH fragil sind
6. `branch-hub/findings/WARGAME-CLAUDE-MULTI-MACHINE-HEBEL-2026-04-20.md` — rho-Korrektur, Anthropic-Rate-Limit
7. `branch-hub/findings/WARGAME-LOW-COST-AI-GRID-2026-04-20.md` — Mac + Gemma4-Optionen

### Identitaets-Entscheidung (Martin-Frage)
YogaMobil soll sein:
- **(A) Worker0002 @ YogaMobil = WORKER-G** (Lane F1100-F1199 + B650-B699) — neuer Worker, eigene Lane
- **(B) Worker0001-continuation** — weil Sessions fortgesetzt werden, nicht neue PC-Identitaet. Lane F1000-F1099 bleibt.
- **(C) YogaMobil-Master-Alternate** — wenn RazorBuero PC3 Worker bleibt, YogaMobil als Master-Backup

**Empfehlung Worker0001:** Option **(B) Worker0001-continuation**. Grund: Wissens-Kontinuitaet, dieselbe Lane, keine Fragment-Counter-Fragmentierung. PC-Name aendert sich (RazorBuero → YogaMobil), Branch-Identitaet bleibt.

## Was bereits existiert (MUSST DU NICHT DUPLIZIEREN)

### Deliverables Session 2026-04-20 (Worker0001@RazorBuero)
| Kategorie | Datei | Zweck |
|-----------|-------|-------|
| Status | `branch-hub/status/worker0001-pc3-status.md` | Aktueller Stand + Setup-Gaps |
| Registry | `branch-hub/REGISTRY.md` | Worker0001 eingetragen |
| BEACON | `branch-hub/BEACON.md` Eintrag 11:55 | Option-C Autonom-Boot |
| Workspace | `Claude-Vault/areas/family/instance-worker0001-pc3/README.md` | Meta |
| Migration-9OS | `instance-worker0001-pc3/migration-index-9os.md` | Hotel-Betriebssystem Canon-Pointer |
| Migration-Workday | `instance-worker0001-pc3/migration-index-workday.md` | Tenant peopleplatforma/wd103 |
| Migration-RASCI | `instance-worker0001-pc3/migration-index-rasci.md` | v4 mit 9 Korrekturen |
| Migration-Sebastian | `instance-worker0001-pc3/migration-index-sebastian.md` | 12 Projekte + 57 Schmerzpunkte |
| Migration-OffRazerAlpha | `instance-worker0001-pc3/migration-index-offrazeralpha.md` | Session-Mother |
| Migration-MASTER | `instance-worker0001-pc3/migration-index-MASTER.md` | Cross-Graph + 23 Learnings |
| Self-Healing | `branch-hub/proposals/Self-Healing-Dark-Factories-v1-2026-04-20.md` | 5-Schichten-Modell |
| Inbox-1 | `inbox/to-work-d2-from-worker0001-pc3-handoff-received-2026-04-20.md` | Identitaet + Gap-Report |
| Inbox-2 | `inbox/to-all-github-fixpunkt-frage-2026-04-20.md` | Struktur-Kritik GitHub-Fixpunkt |
| Inbox-3 | `inbox/to-work-d2-from-worker0001-pc3-option-c-complete-2026-04-20.md` | Phase-1-Complete |

## Setup-Realitaet YogaMobil (erwartet ≠ tatsaechlich)

### Erwartung (aus Setup-Paket)
Admin-PowerShell → winget installs (node, gh, uv) → npm installs (claude, codex, gemini) → Logins → Env-Vars. ~45-90 Min.

### Was auf RazorBuero schief ging (Learnings)
| # | Problem | Martin-Zeit-Kosten |
|---|---------|---------------------|
| L1 | **Setup-Paket §7 Seed-Import kaputt** — `G:/Seed-Exports/` existiert nicht, `G:/claude-seeds/` existiert nicht. Nur 9 outdated Rules auf G: auffindbar (statt 40 versprochenen) | — (kein direkter Block, aber CRUX-Drift-Risiko) |
| L2 | **PowerShell Execution-Policy blockiert npm.ps1** ueberall. Nicht im Setup-Paket erwaehnt. Fix: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force` vor npm-Installs | ~15-30 Min Debugging + Retry |
| L3 | **Agent-Bash-PATH-Cache** — meine Claude-Code-Bash-Shell sieht node/npm/gh nicht, obwohl sie physisch installiert sind. Ich musste per `powershell.exe -NoProfile` oder Pfad-Probe verifizieren | +10 Min Verifikations-Turn |
| L4 | **uv fehlt noch** (winget install --id astral-sh.uv kann je nach winget-Cache fehlschlagen). Alternative: `pip install uv` oder direkter Installer | Variable |
| L5 | **API-Keys sind nach Block 5 noch UNSET** (vermutlich weil Execution-Policy auch Secure-Prompt-Script blockiert hat bis L2 fix) | — |
| L6 | **Bootstrap-Paket des Masters** (`memory/session_bootstrap_multi_machine_2026-04-20.md`) ist immer noch nur PC1-lokal, NICHT auf G: oder GitHub. Ich arbeite ohne es | — (nicht blockierend mit Setup-Paket) |
| L7 | **PC2-Paket** von Martin erwaehnt ("ganzes Paket begonnen") aber keinerlei Spur auf G:/GitHub. 3. Auspraegung desselben Sync-Versagens | — |

**Martin-Zeit-Kosten gesamt RazorBuero-Setup:** geschaetzt **45-90 Min unnoetige** zusaetzlich zu den ~45-90 erwarteten. L2 allein ist 15-30 Min. Kumuliert: **Setup hat ~90-180 Min gekostet statt der 45-90 Min Soll-Wert**. Das ist **2-4x Overrun**.

### Fix fuer YogaMobil (Setup-Paket v2 waere noetig, aber das ist der Workaround bis dahin)

**Block 1 vorab (vor Setup-Paket §2):**
```powershell
# PowerShell Execution-Policy (sonst npm.ps1 blockiert)
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

**Dann Setup-Paket-Reihenfolge gemaess §§1-14.**

## Offene Punkte (Martin-Phronesis, priorisiert)

### Von Work-D2 (Master) offen
1. **Seed-Export-ZIP generieren** oder Master-Snapshot nach `G:/Meine Ablage/claude-seeds/pc1-snapshot-2026-04-21/` kopieren. Worker haben aktuell nur 9 outdated Rules statt 40. CRUX-Drift-Risiko.
2. **Bootstrap-Paket pushen** `memory/session_bootstrap_multi_machine_2026-04-20.md` nach GitHub
3. **PC2-Status klaeren** (Martin-mediiert) — falls PC2 noch lebt, muss Paket gepushed werden
4. **Self-Healing-Proposal Cross-LLM-haerten** via Codex+Gemini (Worker0001 konnte nicht, CLIs fehlten)
5. **Phase-1 Self-Healing implementieren** (Schicht 3 Consistency-Check + Schicht 5 Rules-Hash-Enforcement) — haette alle 4 aktuellen DF-Versagen gefangen

### Von Martin (Phronesis)
1. **8 Jobtitel-Widersprueche** validieren (SF/MR/LW/OG/LB/TJ aus Report 1 vs 2)
2. **Tote JFix-Kanaele** identifizieren (~1.0 bit Shannon offen)
3. **Duetto Zimmerzahlen** pro Hey Lou Hotel (~0.3 bit)
4. **E3 vs Business Basic** Lizenzverteilung (~1.0 bit)
5. **RASCI v2 vs v4 Reconciliation** (TG-Diskrepanz: v2=Stufe-3-Eskalation, v4=1x A)
6. **Sebastian-Rueckkehr-Szenario** (Takeover-Exit-Strategie)
7. **Anthropic-Subscription-Entscheidung** (per-account bestaetigt → zusaetzliche Accounts pro Worker-PC?)
8. **Mac-M4-Pro-Budget** fuer Low-Cost-AI-Grid (€1500-2800, Break-Even 6-10 Mo)

### Von Worker0001 an YogaMobil (neue Arbeit)
1. **Sebastian-Schmerzpunkt-YAML** vertiefen — 57 Schmerzpunkte strukturiert extrahieren aus `Claude-Vault/Florida/Grews-House-Projektplan-PMO.xlsx`
2. **Workday-Live-Re-Validation** — Memory ist 7+ Tage alt, ISU-Drift moeglich (nur wenn CLIs+Keys da)
3. **9OS-Bug-Backlog-Triage** — ~72 offene Bugs aus BUG-REPORT-9OS-KOMPLETT-2026-04-12 in Triage-Buckets (CRIT/HIGH/MED/LOW)

## Rollen-Klarheit (MR-1 bis MR-8 Blueprint, bindend)
Du bist **WORKER** (auch auf YogaMobil, egal ob Worker0001-continuation oder Worker0002). Das heisst:
- ❌ KEINE Scheduled-Tasks (DF-/NLM-/Claude-/Vault-/Archon-*). Check: `schtasks /query /fo LIST | Select-String "DF-|NLM-"` muss leer sein.
- ❌ KEIN `git push origin main` — nur Feature-Branches
- ❌ KEIN NLM-Login (NLM hat 1 Session/Account, die gehoert Master)
- ✅ Feature-Branch-Push + gh pr create OK
- ✅ Inbox an Master via `to-work-d2-from-worker0001-yogamobil-*`
- ✅ Eigenes Workspace `Claude-Vault/areas/family/instance-worker0001-yogamobil/` (falls Neu-Start auf YogaMobil)

## Rho-Bilanz Session 2026-04-20

| Posten | rho |
|--------|-----|
| Wissens-Migration 5 Sessions (Index-First) | +10-30k EUR/J indirekt (Such-Zeit-Reduktion) |
| Self-Healing-Proposal geschrieben | +25-70k EUR/J erwartet bei Phase-1-Impl |
| GitHub-Fixpunkt-Kritik an Master geliefert | +15-40k EUR/J (falls adoptiert) |
| Struktur-Fehler-Katalog (7 Fehlschlaege dokumentiert) | Meta-Wert, nicht monetaer |
| **Summe direkte rho** | **+50-140k EUR/J wenn Master Phase-1 Self-Healing umsetzt** |

## Session-Ende-Zustand

- **Worker0001 Status:** IN-FLIGHT — Write-Only-Inbox-und-Workspace, warte auf Martin+Master-Antwort
- **Context-Fill:** geschaetzt ~40-50% (Heuristik)
- **CLIs:** teilweise installiert (node+gh+npm physisch da, API-Keys UNSET, uv ausstehend)
- **Naechster Schritt wenn Worker0001-continuation auf YogaMobil:**
  - Setup-Paket mit L2-Fix (ExecPolicy) durchziehen
  - Env-Var-Block 5 retry
  - `/seed-export` am Master anfordern (oder Master-Snapshot kopieren)
  - Bei CLIs+Keys voll: Self-Healing Phase-1 Cross-LLM-haerten

## CRUX-Check
- [x] Handoff **vor** Kulmination geschrieben (Antifragile M9 Pflicht-Artefakt)
- [x] Alle 11 Worker0001-Artefakte persistent auf G:
- [x] 7 Fehlschlaege ehrlich dokumentiert (keine Sycophancy)
- [x] Martin-Zeit-Kosten quantifiziert (2-4x Overrun)
- [x] YogaMobil-Setup-Fix vorweggenommen (ExecPolicy-Block vor npm)
- [x] Lane-Entscheidung klar formuliert (A/B/C + Empfehlung)

[CRUX-MK]
