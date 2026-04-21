---
description: SAE v8 Security-Standards [CRUX-MK] -- Prompt Injection, API-Keys, DSGVO, Rate-Limits
globs: "**/SAE-v8/**"
---

# SAE v8 Security-Standards [CRUX-MK]

Quelle: Meta-Session (MYZ-36 + MYZ-37), to-gui Inbox, to-meta Inbox, 4 Wargames.
CRUX-Relevanz: Q_0 (Qualitaetsinvarianz) + K_0 (Kapitalerhaltung bei Breach).

---

## 1. PROMPT INJECTION IN MYZ-36 (Meta-Prompting-Router)

**Angriffsvektor:** GSA gibt manipulierten Text ein der den LLM-Prompt ueberschreibt.
**Realitaets-Check (Wargame):** Hotel-GSAs koennten Injection NICHT absichtlich durchfuehren.
Aber: Copy-Paste von WhatsApp/Social-Media koennte Injection-Payloads enthalten.

**Schutzmassnahmen:**
1. Haiku-Classifier (Tier 0/1/2) filtert VOR dem LLM-Call
2. COP-Templates haben feste System-Prompts (nicht user-modifizierbar)
3. Canary-Queries pruefen COP-Integritaet (canary_score >= 0.8)
4. Input-Laenge begrenzt (max 500 Zeichen fuer GSA, max 2000 fuer Manager)
5. Output-Filter: Keine internen System-Prompts in Antworten exponieren
6. Neutralitaetsfilter: Gossip/Slurs werden VOR LLM-Verarbeitung entfernt

**NICHT ueberengineeren:** Realistisches Risiko = Gossip/Slander, nicht sophistizierte Attacks.

---

## 2. API-KEY MANAGEMENT

**MEWS:** ClientToken + AccessToken pro Hotel (7 Paare). POST-Body, NICHT Header.
- Keys NIEMALS in Code, Config-Dateien oder Git
- Keys in Environment Variables oder Secret Manager
- Rotation: Mindestens alle 90 Tage
- Monitoring: Fehlgeschlagene Auth-Versuche loggen

**LLM-APIs:** Claude, Gemini, GPT, Gemma -- jeweils eigene Keys.
- Tier-0 (Cache) braucht KEINEN API-Key
- Fallback-Kette: Wenn Primary-LLM down, naechstes LLM (Key muss vorhanden sein)
- Rate-Limits pro Hotel pro Tag (Token-Budget aus Governance, T_max)

**Workday ISU:** SOAP-basiert, Credentials fuer SSO-Integration.
- Separater Credential-Store (nicht im SAE-Code)

---

## 3. DSGVO / AUDIO-VERARBEITUNG

**Voice-Gateway (MYZ-37):**
1. STT via Whisper (lokal oder API)
2. Audio wird SOFORT nach Transkription geloescht (kein Speichern)
3. DSGVO-Freigabe fuer Audio im Arbeitsvertrag VORHANDEN (Martin bestaetigt)
4. Transkribierter Text unterliegt denselben Regeln wie Chat-Input
5. Keine biometrische Stimmidentifikation (nicht erlaubt ohne explizite Einwilligung)

**Personenbezogene Daten:**
- Gast-Daten: Nur ueber MEWS-API, nicht lokal gespeichert
- GSA-Profile: Aus Workday, Cultural Index lokal (aggregiert, nicht individuell identifizierbar)
- Produktivitaets-Daten: NUR aggregiert an Manager (P5: nie individuell)
- Emotions-Verteilung: Aggregiert (Stress/Neutral/Positiv), nie pro Person

---

## 4. RATE-LIMITING UND COST-CONTROL

**Token-Budget pro Agent:**
- T_max aus Governance (Sigmoid auf q_norm)
- Recovery-Floor: 20.000 Tokens bei q < 0 (Death-Spiral-Schutz)
- T_CAP: 50.000 Tokens max (kein unbegrenzter Verbrauch)
- Effektive Untergrenze: T_RECOVERY_FLOOR / (1+W_CAP) = 5.000 Tokens

**Hotel-Level:**
- Gesamtbudget pro Hotel pro Tag: $50 ohne Router, $7.30 mit Router
- 85% Savings durch Tier-Routing (empirisch, Martin)
- Tier 0 (Cache): $0.001/Query, Tier 1: ~$0.01, Tier 2: ~$0.10

**Alarm bei:**
- Token-Verbrauch > 150% des Tagesbudgets
- Einzelner Agent > T_CAP (sollte unmoeglich sein, aber Monitor)
- Canary-Score < 0.7 (COP moeglicherweise korrumpiert)

---

## 5. BOUNDED VETO (COSMOS)

**Mechanismus (myz33_veto.py):**
- ActionLevel: READ (1.0), WRITE (0.5), DESTROY (0.1)
- epsilon_eff = min(governance_epsilon, bv_calibrated) * DAMPENING
- complexity >= 0.8 → Eskalation an Manager
- Fallback-Timeout adaptiv: 5min (q<-1.5), 15min (q<0), 60min (q>0)

**5 Harte Grenzen (aus GUI-Rechte-Architektur):**
1. Kein GSA kann Governance-Parameter aendern
2. Kein Manager kann SAE-Internals sehen (nur aggregierte Metriken)
3. Kein Hotel-Owner kann andere Hotels sehen
4. Kein COSMOS-Override ohne Martin-Approval
5. Keine Loesch-Operation ohne Double-Confirmation

---

## 6. NICHT-FUNKTIONALE SICHERHEIT

**Availability:**
- Docker Compose mit Health Checks (P1 offen)
- TLS fuer alle externen Verbindungen
- Reverse Proxy vor SAE-API

**Logging:**
- Alle API-Calls loggen (Request-ID, Timestamp, Agent-ID, Hotel-ID)
- KEINE personenbezogenen Daten im Log
- Log-Retention: 90 Tage (DSGVO)

**Incident Response:**
- Feature-Flags fuer sofortigen Rollback (Invariante 7)
- Shadow-Mode: Governance beobachtet aber greift nicht ein (shadow_mode=True Default)
- Canary-Score als Fruehwarnsystem
