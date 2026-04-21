---
description: SAE v8 Coding-Standards [CRUX-MK] -- Mechanisch durchgesetzt via Rules, nicht Dokumentation
globs: "**/SAE-v8/**"
---

# SAE v8 Coding-Standards [CRUX-MK]

Quelle: Beta (1136 Tests, 100% pass), Gamma (Q_SCALE-Fix), Meta-Session (4 Wargames),
GUI-Session (25 BP), Alpha (KPM), OffRazerAlpha (Stammzellen-Diagnose).
Validiert durch: 6 Wargames (4 HARDENED, 2 CONDITIONAL), Inbox-Cross-Reference.

---

## 1. DUAL-IMPORT-REGEL (Bug-Fix, NIEMALS brechen)

```python
# KORREKT:
from core.models import AgentID, SlotID
from core.governance import GovernanceManager

# FALSCH (Dual-Import Enum Bug, pyproject.toml pythonpath=["."]):
from sae_v8.core.models import AgentID  # VERBOTEN
```

**Warum:** Python laedt Module doppelt wenn sowohl `sae_v8.core.models` als auch
`core.models` importiert werden. Enums werden zu verschiedenen Objekten.
`isinstance()` und `==` schlagen fehl. 4 Import-Bugs in Phase 0-3 gefixt.

---

## 2. TRINITY-PATTERN IST SAKROSANKT

- 200 Slots x 3 Varianten (Conservative, Aggressive, Contrarian) = 600 Agenten
- `core/trinity.py`: NIEMALS `update_scores()` oder `relegate()` aendern
  ohne ALLE bestehenden Tests zu pruefen
- `governance_mgr` ist OPTIONAL (hasattr Guard) -- bestehende Tests erstellen
  TrinitySlot OHNE governance_mgr

**Warum:** Trinity ist die Kern-Architektur der SAE. Jede Aenderung bricht
potenziell 600 Agent-Instanzen. SAE-Isomorphie: Universale Trinitaet.

---

## 3. Q_SCALE = 11.11 (NICHT 25.0)

```python
Q_SCALE_INTEGRAL = Q_SCALE_EMA / GAMMA = 0.5 / 0.045 = 11.11
```

**Mathematischer Beweis:** q_norm_ss muss bei gleichem p identisch sein (EMA vs Integral).
Gamma hat den Bug gefunden. Beta hat ihn gefixt. 6 Wargames haben es validiert.
Wer 25.0 setzt, bricht die Governance-Invarianten.

---

## 4. SIEBEN DESIGN-INVARIANTEN (IMMER pruefen)

| # | Invariante | Bereich | Konsequenz bei Verletzung |
|---|-----------|---------|--------------------------|
| 1 | `q_norm` | [-2, +2] | Governance-Reward explodiert |
| 2 | `T_max` | [T_MIN=2000, T_CAP=50000], Recovery-Floor=20000 | Agent verhungert oder verschwendet |
| 3 | `w` (Gewicht) | [1.0, 4.0], W_CAP=3.0 | Ueberreaktion auf Governance |
| 4 | `epsilon` | [0.01, 0.15] | Exploration zu aggressiv oder tot |
| 5 | `V(q)` | > 0 fuer q != 0 | Potential-Shaping bricht |
| 6 | `F_cum` | Dominiert Relegation (NIE Governance allein) | Falsche Agenten werden relegiert |
| 7 | Feature-Flags | Sofortiger Rollback moeglich | Kein sicheres Deployment |

**Effektive Budget-Untergrenze:** T_RECOVERY_FLOOR / (1+W_CAP) = 5000 Tokens

---

## 5. MEWS-TESTS: MOCK-TOKENMANAGER PFLICHT

```python
# KORREKT:
adapter = MEWSAdapter(hotel_id="hotel-001", token_manager=mock_tm, client=mock_client)

# FALSCH (versucht YAML zu laden, macht echte HTTP-Requests):
adapter = MEWSAdapter(hotel_id="hotel-001")  # VERBOTEN in Tests
```

**Warum:** Ohne Mock macht der Test echte API-Calls gegen MEWS Production.

---

## 6. GOVERNANCE q-FELD NUR UEBER PROPERTY

```python
# KORREKT:
state.q = neuer_wert  # Property mit Q_SCALE Normalisierung

# FALSCH:
state._q = neuer_wert        # VERBOTEN (umgeht Normalisierung)
state.__dict__['q'] = wert    # VERBOTEN
```

---

## 7. FULL-HAMILTONIAN REJECTED

Wargame OSCILLATOR-001 Verdict: CONDITIONAL.
Wargame OSCILLATOR-002 Verdict: CONDITIONAL.
**Ergebnis:** Moltke > Hamilton. Einfach starten, beobachten, eskalieren.

```
H = u + lambda*f           # KORREKT (bestehendes hamilton.py)
H_eff = u + lambda*f + ...  # NUR ERWEITERN, nicht refactoren
# KEIN Full-Hamiltonian-Oscillator (Over-Engineering, CRUX-GATE rejected)
```

Jeder Governance-Tier ist in sich abgeschlossen und deploybar. Kein Big-Bang.

---

## 8. MODEL-AGNOSTIC-LAYER AB TAG 1

```python
# KORREKT: OpenAI-kompatibles Interface, Backend austauschbar
# 1-Zeilen-Migration: OpenAI SDK -> localhost:11434/v1 (Ollama/Gemma 4)

# FALSCH: Hardcoded API-Keys, Provider-spezifische Imports im Kern
```

**Warum:** Gemma 4 26B MoE kommt Q3 2026 lokal (MacBook M5 Max).
SAE muss Provider-agnostisch sein. Wargame GEMMA4-SAE-001: CONDITIONAL, 3 Patches.

---

## 9. TERMINOLOGIE

| FALSCH | KORREKT | Warum |
|--------|---------|-------|
| Keystone Score | **HIVE Score** | Keystone = separates Produkt (Leadership-Playbook) |
| Query-Layer | **MYZ-36 Meta-Prompting-Router** | GSA spricht MIT ihrem Agenten, kein separater Layer |
| MVP | **MSP** (Minimum Sellable Product) | Hotels sind Kunden. Hoteldirektor muss "will ich" sagen |
| AI-Agenten vs. Mitarbeiter | **GSA = MENSCH, SAE-Agent = Digitaler Zwilling** | EIN System, nicht zwei |

---

## 10. CRUX-KONSTANTEN (aus SAE v8 Code, validiert)

```python
F_CUM_DECAY     = 0.98    # Fitness-Verfall pro Zyklus (HWZ ~34 Tage)
                          # Martin-Direktive 2026-04-17: Familien-Ewigkeits-Horizont verlangt
                          # langsame Relegation. 0.70 war alter Trading-Wert (HWZ 2 Tage).
RELEGATION      = 0.3     # Relegations-Schwelle
INCUMBENT_ADV   = 1.15    # Amtsinhaber-Vorteil (Challenger muss 15% besser sein)
H_MAX           = 3.32    # log2(10) bits fuer 10 AgentClasses
Q_SCALE_EMA     = 0.5
GAMMA           = 0.045
Q_SCALE_INTEGRAL = 11.11  # = Q_SCALE_EMA / GAMMA (NICHT 25.0)
T_MIN           = 2000
T_CAP           = 50000
T_RECOVERY_FLOOR = 20000
W_CAP           = 3.0
```

---

## ALLGEMEINE CODING-REGELN (aus CLAUDE.md Sektion 3)

- TypeScript: strict mode, kein `any`
- Python: Type Hints, Black + Ruff
- Jede Funktion: Pre/Post-Conditions (Pydantic, Dataclasses, Property-Guards)
- Keine Magic Numbers: Benannte Konstanten mit Einheit (siehe §10)
- Naming: Deutsch fuer Domaenen-Konzepte, Englisch fuer Tech
- Pentagon-Verfahren: Plan → Spec → Implement → Test → Refine
- Test-Kommando: `python -m pytest tests/ --ignore=tests/test_integration -q`
- Governance verifizieren: `python -m scripts.verify_governance` (55/55 Checks)

---

## ANTI-PATTERNS (aus 6 Wargames + Inbox-DONT's)

1. NICHT `from sae_v8.xxx` in Tests (Dual-Import)
2. NICHT MEWS-Tests ohne Mock-TokenManager
3. NICHT Q_SCALE = 25.0
4. NICHT Full-Hamiltonian implementieren
5. NICHT kooperatives rho in Observer mischen
6. NICHT governance.py, trinity.py, crux.py, hamilton.py grundlegend refactoren
7. NICHT iOS-First (Android-First: Samsung Galaxy A-Serie)
8. NICHT individuelle Produktivitaets-Daten an Manager zeigen (nur aggregiert)
9. NICHT Text-schwere GUI (Piktogramme fuer Low-Literacy)
10. NICHT Voice als Feature (Voice = Inklusion = MSP-PFLICHT)
