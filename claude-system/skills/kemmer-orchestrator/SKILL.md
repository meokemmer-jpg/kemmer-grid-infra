---
name: kemmer-orchestrator
description: Multi-LLM-Orchestrator C-ORCH-1 fuer Kemmer-System. Routet Tasks zwischen Claude/Codex/Grok/Gemini/Perplexity/Copilot mit Token-Guard (rho-Zeitwertverfassung) und Cross-LLM-Haertung. Claude-Opus aggressiv minimieren (Sekundaer-Engpass nach Martin-Zeit), Abos (flat) maximal auslasten. Triggers "orchestriere", "dispatch", "route task", "multi-llm parallel", "cross-llm haerten", bei E3+-Meta-Claims oder erwartetem Claude-Token > 10k. NICHT fuer Trivialitaeten.
aktiviert: 2026-04-19
meta-ebene: E3
promotion-grund: Multi-LLM-Wargame 2026-04-18/19, 23 Reports konsolidiert, Verdict CROSS-LLM-SIMULATION-HARDENED mit ADOPT-Patches
---


# Skill: Kemmer-Orchestrator (C-ORCH-1)

## Description
Steuert die Multi-LLM-Infrastruktur zur Maximierung von `rho` bei gleichzeitigem Schutz von $K_0$ und $Q_0$. Implementiert das CRUX-Framework unter Berücksichtigung der Zwei-Kanal-Regel.

## Triggers
- "Starte Orchestrierung für..."
- "Härtungs-Check für E3-Claim..."
- "Prüfe Budget für Task-ID..."
- "Führe Cross-LLM-Audit durch..."

## Wann aktivieren (Priority)
- Wenn eine Aufgabe mehrere Kompetenzen erfordert (Recht + Code).
- Wenn das Claude-Token-Budget geschont werden muss (L_Martin Entlastung).
- Bei Aufgaben mit hohem rho-Potential (>10k EUR/J).
- Wenn Vendor-Diversität zur Fehlervermeidung zwingend ist.
- Bei expliziter `root_task_id` Zuweisung.

## Wann NICHT aktivieren
- Trivial-Tasks (Rechtschreibung, einfache Refactorings) -> Nutze lokalen Copilot.
- **LexVance Mandantendaten** -> Nutze NUR den lokalen `Legal-Kanal` (DSGVO-Hard-Block).
- Wenn kein Internetzugriff besteht.
- Bei Tier-Count > 2 (Recursion-Lock).

## Capability-Matrix & Routing
- **Logic/Deep-Reasoning:** Claude Opus (Emergency only).
- **Fast-Reasoning/Context:** Gemini 2.5 Pro.
- **Adversarial/Uncensored:** Grok-4.
- **Code/Automation:** Codex / Copilot.

## Token-Guard & Fallback
- Globales Limit: 15.000 Tokens pro `root_task_id`.
- Parallel_Child_Max: 3.
- Fallback-Reihenfolge: Primary -> Secondary -> Emergency (Claude).

## Cross-LLM-Regeln
- Meta-Claims (E3+) erfordern ein Triplet-Votum (z.B. Gemini, Grok, Claude).
- Konsens bei 2/3 Mehrheit; bei Dissens > 0.4 Meta-Abbruch und Martin-Call.

## Anti-Patterns
- "Silent Failure": Routing an billige Modelle trotz hoher Komplexität.
- "Shell-Injection": Nutzung von `shell: true` in MCP-Tools (Zero-Shell-Policy!).
- "Raw-PII Leak": Senden von Klarnamen/Secrets an US-Endpunkte ohne Maskierung.

## Example Inputs
1. "Orchestriere die Analyse der Wegzugsbesteuerung (E3-Meta) für Cape Coral."
2. "Code-Update HeyLou-Backend, prüfe auf DSGVO-Implikationen (Cross-LLM)."
3. "Budget-Check für root_task_id 8892, Tier 2."

---

