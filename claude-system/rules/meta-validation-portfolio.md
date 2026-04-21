---
aktiviert: 2026-04-18
---

# Meta-Validation-Portfolio (E2) [CRUX-MK]

**Ebene:** E2 (Wissen ueber Wissen, per META-LERN-KRISTALL §Ordnung-2)
**Referenz:** `Claude-Vault/areas/family/META-LERN-KRISTALL-5-ORDNUNGEN-SUPER-SYSTEM.md` §E2

## Kern-These

**Keine Validierungs-Methode ist universal.** Jede Methode hat einen Scope, ausserhalb dessen sie versagt oder trivial wird.

Aus dem Kristall-Wargame E2 (Purple-Team): *"Meta-Lern-System braucht Methoden-Portfolio statt Methoden-Monopol. Auswahl methoden-spezifisch pro Aussage-Typ."*

## Aussage-Typ x Methode Matrix (Revised 2026-04-18 via Cross-LLM-2OF3-HARDENED)

**Belegung:** `branch-hub/cross-llm/2026-04-18-Mission-2-3-4-Konsolidiert.md` §Mission-2 (3/3 MODIFY)

### Kern-Matrix (korrigiert + erweitert)

| Aussage-Typ | Primaer-Methode | Sekundaer-Methode | NICHT brauchbar |
|-------------|-----------------|-------------------|-----------------|
| Empirische Fakten (Messwerte, Daten) | **Provenienz + Mess-Audit** | Multi-Source-Triangulation | ~~Cross-LLM 4/7~~ (Echokammer-Risiko; nur Tertiaer als Anomalie-Detektor) |
| Mathematische Identitaeten | Formal-Beweis + Unit-Test (Z3/Lean bei Randfaellen) | Cross-LLM nur als Sanity-Check | SHA, LLM-Halluzinationen bei Fliesskomma |
| Theorien / Kausal-Modelle | Popper-Falsifikation + Peer-Review | Cross-LLM | Counts/Frequenzen |
| Artefakt-Integritaet (Files) | SHA256-Verification | Git-Commit-Chain | Philosophische Argumente |
| **Semantische Identitaet** (Code/Text-Logik) | **AST-Graph-Isomorphie** | LLM-Paraphrasen-Check | SHA256 (zu rigide) |
| Session-Uebergaenge | **Knowledge-Diff + State-Snapshot + Replay + Failure-Ledger** | BEACON-Lese-Pflicht | Cross-LLM, statische Snapshots allein |
| Meta-Aussagen (E2+) | Cross-LLM-Simulation-Hardened + externe Ankerung | Selbst-Konsistenz-Check | Single-Expert-Meinung |
| Isomorphie-Uebertragungen | Empirische Validierung in Target-Domain | Strukturelle Aehnlichkeit-Check | Hand-waving |

### Neue Zeilen (8 fehlende Aussage-Typen ergaenzt)

| Aussage-Typ | Primaer-Methode | Sekundaer-Methode | NICHT brauchbar |
|-------------|-----------------|-------------------|-----------------|
| **Normative/ethische Aussagen** ("sollte X") | Prinzipien-Audit + Reflective Equilibrium | Stakeholder-Konfliktanalyse | SHA, Mehrheits-LLM, empirische Daten allein |
| **Counterfactual / Policy-Claims** ("was waere wenn") | Kausalmodell + Intervention/Simulation + Backtesting | Sensitivitaetsanalyse | Peer-Review allein |
| **Temporale / dynamische Aussagen** (Zustands-Uebergaenge) | Invarianten + Event-Log-Replay | Zustandsuebergangs-Tests | statische Snapshots |
| **Definitorische / taxonomische Aussagen** ("X ist Instanz Y") | Begriffsfixierung + Grenzfalltests | Korpusgebrauch | Frequenz allein |
| **Phaenomenale Aussagen** ("wie fuehlt sich X an") | strukturierter Selbstbericht | intersubjektive Muster / Proxys | externe Falsifikation allein |
| **Heuristische Aussagen** ("in 80% der Faelle X") | Backtesting (Success-Rate) | Monte-Carlo-Simulation | formaler Beweis |
| **System-Constraints** ("X gilt nur wenn Y") | Boundary-Value-Analysis | Stress-Testing | Cross-LLM 4/7 |
| **Kalibrierungs-/Unsicherheitsaussagen** ("80% sicher") | Brier-Score + ECE gegen Holdout | Bayesianische Posterior-Update | Selbstdeklaration ohne Ground-Truth |

### Zusatz-Regel fuer E3-E5 (Anti-Zirkularitaet)

Validierung von Meta-Methoden darf NIEMALS ausschliesslich durch das Werkzeug erfolgen, das die Methode anwendet. E5 (Fixpunkte) erfordert **Topologische Invarianz-Pruefung** statt Cross-LLM-Konsens.

### Format-Hinweis

**1-Methode-pro-Zelle ist Vereinfachung.** Realistisch = Methoden-Portfolio pro Typ mit Aggregationsregel: notwendige Checks + optionale + Tie-Breaker + Eskalationspfad. Fuer Hoch-Sicherheits-Claims (K_0-Relevanz) Multi-Dimensional-Erweiterung (Typ x Sicherheits-Anspruch x Kosten-Budget) empfohlen (3D-Tensor). Separate Decision-Card fuer 3D-Umbau steht aus.

## Pflicht-Klassifizierung vor Validierung

Bei jeder Claim-Aufnahme in Canon:
1. **Aussage-Typ bestimmen** (eine Zeile im Frontmatter oder Decision-Card)
2. **Methode aus Matrix auswaehlen** (nicht ad-hoc)
3. **Scope-Check**: Matched der Claim wirklich den Methoden-Scope?
4. **Dokumentation**: welche Methode(n) wurden angewendet, mit welchem Ergebnis?

## Anti-Patterns

- **Universal-Cross-LLM**: 4/7-Regel auf Meta-Meta-Aussagen = korrelierte Biases (siehe rules/cross-llm-simulation.md)
- **SHA-fuer-Semantik**: byte-identische Duplikate finden, aber semantisch aequivalente uebersehen
- **Popper-fuer-Fakten**: "Wie koennte es falsch sein?" bei Messwerten trivialisiert (Messfehler ist immer moeglich)
- **Single-Methode-Monopol**: nur eine Methode fuer alle Aussage-Typen anwenden

## Operationalisierung

- Decision-Cards bekommen Feld `validation-type` (muss Matrix-Eintrag matchen)
- Findings bekommen Feld `validation-method` im Frontmatter
- Review-Gate pruft: stimmt Methode mit Aussage-Typ ueberein? Sonst ablehnen.

## SAE-Isomorphie

Trinity-Pattern auf Validierungs-Ebene: **3 Methoden pro Aussage-Typ-Klasse** (Primary, Secondary, Adversarial). Bester Vote gewinnt, ohne Konvergenz = CONDITIONAL.

## CRUX-Bindung

- **Q_0**: geschuetzt durch Methoden-Scope-Disziplin (keine falschen Validierungen)
- **I_min**: erhoeht (strukturierte Matrix)
- **W_0**: Write-Bandwidth effizienter (keine redundanten Validierungs-Runden)

## Falsifikations-Bedingung

Wenn ein Claim mit Matrix-konformer Methode validiert und spaeter als falsch erwiesen wird: Methoden-Eintrag in Matrix pruefen und ggf. anpassen.

[CRUX-MK]
