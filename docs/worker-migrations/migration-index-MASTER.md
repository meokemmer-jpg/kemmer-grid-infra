---
type: master-index
migrator: Worker0001 @ RazorBuero (PC 3)
migration-date: 2026-04-20
sessions-migrated: 5 (OffRazerAlpha, 9OS, Workday, RASCI, Sebastian)
transfer-approach: Index-Files + Canon-Pointer (NICHT Volltext-Duplikat)
verlustfreiheit: hoch — alle Primaer-Artefakte bleiben auf Drive-G erhalten
---

# Master Migration-Index: 5 Vorgaenger-Sessions → Worker0001 [CRUX-MK]

## Martin-Auftrag (2026-04-20)
> "OffRazerAlpha 9OS Workday RASCI und Sebastian sind alles Sessions die dieses erst möglich gemacht haben und wo wissen (zum teil altes Wissen zum tiel sehr wertvoll zum teil veraltet) noch Verlustfrei ins System muss sowie alle Learnings daraus."

## Transfer-Strategie
**Index-First statt Volltext-Kopie.** Begruendung:
- Alle 5 Sessions haben persistente Artefakte auf Drive-G (Handoffs, Decision-Cards, Findings, Code, Excel)
- Volltext-Duplikation = Drive-Sync-Risiko + Canon-Drift
- **Index-Files = Zugriffs-Kompass** + Canon-Markierung + Cross-References + Veraltet-Markierung

## 5 Session-Indexe
| # | Session | Datei | Risk |
|---|---------|-------|------|
| 1 | **OffRazerAlpha** | [migration-index-offrazeralpha.md](./migration-index-offrazeralpha.md) | SEHR NIEDRIG (Handoff 218 Zeilen vollstaendig) |
| 2 | **9OS** | [migration-index-9os.md](./migration-index-9os.md) | NIEDRIG (Production-Code + 12 Findings) |
| 3 | **Workday** | [migration-index-workday.md](./migration-index-workday.md) | NIEDRIG-MITTEL (Live-Drift moeglich) |
| 4 | **RASCI** | [migration-index-rasci.md](./migration-index-rasci.md) | NIEDRIG (v4-Canon + Excel persistent) |
| 5 | **Sebastian** | [migration-index-sebastian.md](./migration-index-sebastian.md) | MITTEL (Soft-Wissen bei 40% der 57 Schmerzpunkte) |

## Cross-Session-Dependencies (Wissens-Graph)

```
OffRazerAlpha (Session-Mother)
    ├── erstellt→ RASCI v4 (37 Personen, 33 JFix)
    ├── erstellt→ Organigramm 4 Ebenen
    └── dokumentiert→ 17 M365-Konten + 15 Gesellschaften
         ↓
    RASCI v4 ←→ Sebastian-Takeover
         (v2 Projekt-fokus + v4 JFix-fokus, TG-Diskrepanz!)
         ↓
    Sebastian-Projekte (12) → Workday (#2) + ADP (#10) + GSA-Hildesheim (#5+#7)
         ↓
    Workday-Tenant peopleplatforma/wd103 ←→ 9OS Workday-Adapter
         ↓
    9OS (Canon-Production) ←→ RASCI-Rechte (GUI-RECHTE-ARCHITEKTUR)
         ↓
    9OS-Pilot-Hotel Hildesheim ←→ B24-Pilot-Hotel-Haerte (Work-D2 2026-04-18)
```

## Learnings-Katalog (cross-session, strukturiert)

### Methodische Learnings
1. **Shannon-Bit-Tiefen-Reduktion** (OffRazerAlpha): 43.8 → 2.3 bit in einer Session moeglich via Copilot-Research-Agents + Azure-AD-Abfrage
2. **3 Copilot-Reports** kombiniert liefern 85-95% Coverage (OffRazerAlpha)
3. **Ebene-2 = NUR Kemmers** ist harte Hierarchie-Regel (nicht variabel)
4. **Skills muessen ausfuehrbar sein, nicht nur gelesen** (feedback_lesen_ist_nicht_koennen.md)
5. **Pre-Compact-Write-Zwang** (aus CR-2026-04-19-001 gelernt)

### Organisations-Learnings
6. **TG = Einkaufsleiter** (nicht Head of Ops) — kritische Korrektur
7. **Daniela Schade → Thomas Kemmer** (Manager-Feld Azure-AD Drift)
8. **Gerdi = CTO** (KI + IT) mit Viktor Maul (VIBE) + Till Ole Klobes (SQL)
9. **Sebastian Kemmer ausgefallen** seit 2026-04-07, Takeover durch Martin
10. **Hotel Manager Hildesheim UNBESETZT** seit August 2025, Selin Polat faktisch

### Tech-Learnings
11. **9OS = React Native Expo 55 + FastAPI + SAE v8** (Canon-Architektur)
12. **600 KI-Agenten** in Trinity + HIVE + COSMOS
13. **MYZ-36 Router + MYZ-37 Voice** systemweit via `from myzel import X`
14. **Workday Tenant peopleplatforma/wd103** mit 121 Scopes MCP + 4 Scopes n8n
15. **INT1005 Workday→ADP PECI** kritischer Integration-Path

### Projekt-Learnings
16. **57 Schmerzpunkte kategorisiert** (SV=27 + DI=15 + SUE=6 + TA=3 + GR=6)
17. **4-Kreis-Architektur** (Budget/Pipeline/Delivery/Produkt, Navina seit 2026-03-17)
18. **4 Projekte ROT**: Workday-Verhandlung, DD-Colliers, Energie, ADP
19. **2 Projekte GRUEN**: DOBI, Q-Park

### Meta-Learnings (fuer System-Evolution)
20. **Drive-Sync ist SPOF** (FINDING-DRIVE-SYNC-CHAOS, drei unabhaengige Forensik-Reports)
21. **GitHub-Repo `/rules/` outdated** (9 statt 40 Files) — Sync-Kanal funktioniert nicht
22. **Anthropic Rate-Limit per-account** — Multi-Machine-Hebel fuer Claude-Opus = Illusion
23. **Dark Factories ohne Self-Healing fragil** (Martin-Direktive 2026-04-20)

## Veraltet (markiert, nicht geloescht)
- RASCI v3 (16 Personen) → Historie, nicht mehr aktiv verwenden
- Report-1-vs-Report-2-Jobtitel-Widersprueche (8 Personen) → Martin-Validation offen
- Azure AD Manager-Feld fuer 8 Personen → Update pending (Daniela → TK)
- Memory `reference_workday_sandbox.md` 6 Tage alt → Re-Validation bei konkreter Task

## Offene Punkte (an Martin zurueck)
1. 8 Jobtitel-Widersprueche validieren (SF/MR/LW/OG/LB/TJ)
2. Tote JFix-Kanaele identifizieren (~1.0 bit Shannon offen)
3. Duetto Zimmerzahlen pro Hotel (~0.3 bit)
4. E3 vs Business Basic Lizenzverteilung (~1.0 bit)
5. RASCI v2 vs v4 Reconciliation (TG-Diskrepanz)
6. Sebastian-Rueckkehr-Szenario (Takeover-Exit-Strategie)

## Wissens-Verlust-Gesamt-Risiko: NIEDRIG-MITTEL
- Alle 5 Session-Outputs persistent auf Drive-G
- Index-Files machen alles auffindbar
- **Hauptrisiko:** Sebastian-Soft-Wissen (40% der 57 Schmerzpunkte) + Workday-Live-Drift

## Naechster Schritt
→ Self-Healing-Proposal fuer Dark-Factories (Martin-Direktive, separate Datei)
