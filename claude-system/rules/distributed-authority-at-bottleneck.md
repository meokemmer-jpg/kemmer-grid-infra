# Verteilte Autoritaet am Engpass [CRUX-MK]

**Lernsatz (Bruecken-Fund 2026-04-18, B13 Peak-Season-Protokoll + B23 Knowledge-Janitor):**
Wenn Entscheidungs-Konsens am Engpass waertet, muss die Autoritaet verteilt werden — nicht delegiert, sondern verteilt.

## Das Prinzip

**Klassisch:** Hierarchie = ein Entscheider am Engpass. Problem: bei Ueberlast bricht das System.

**Verteilt:** Mehrere koennen am Engpass handeln, aber nur in klar definierten Faellen. Niedrigere Stufen bleiben zentralisiert.

## Manifeste Anwendung

### B13 Peak-Season-Familien-Protokoll (Patch P-B13-6 Fremd-Diagnose-Regel)
- **Engpass:** Martin/Gerdi-Mental-Bandwidth
- **Regel:** Jedes Familienmitglied (inkl. Kinder altersgerecht) kann einseitig Peak erklaeren
- **Hoehere Stufe gilt automatisch** — kein Konsens noetig
- **Warum:** Ein Peak-Erklaerer genuegt, weil falsche Peak-Annahme ist billiger als verpasste Peak-Warnung (asymmetrischer Schaden)

### B23 Knowledge-Janitor (Patch P-B23-18 Deputy-Regel)
- **Engpass:** Martin-Review-Bandbreite fuer KB-Kandidaten
- **Regel:** Bei Martin-Ausfall > 4 Wochen pausiert Janitor automatisch
- **Deputy (Gerdi) moeglich** fuer niedrig-risiko Domains (graphity, personal)
- **NICHT fuer** sae-v8, 9os, heylou, kpm, cape-coral (K_0-Naehe)

## Invarianten

### I1: Autoritaets-Verteilung nur bei asymmetrischem Schaden
Die verteilte Autoritaet gilt nur wenn gilt:
```
Cost(false positive) << Cost(false negative)
```
Also: ueberreagieren ist billig, untereagieren ist teuer. Nur dann darf einzelner Akteur eskalieren.

### I2: Domains-Trennung ist Pflicht
Niemals pauschal "jeder darf alles am Engpass". Stattdessen: Domain-Matrix mit klaren Erlaubnis-Lisken. 

Beispiel B23:
- Gerdi DARF: graphity, personal (niedrig K_0-Risiko)
- Gerdi DARF NICHT: sae-v8, 9os, heylou, kpm, cape-coral (hoch K_0-Risiko)

### I3: MHC-Override bleibt zentral
Auch bei verteilter Autoritaet: Martin kann jede Deputy-Entscheidung overruleen. Zentrale Autoritaet bleibt, wird nur bei Ueberlast temporaer delegiert.

### I4: Rueckkehr-Trigger muessen definiert sein
Wenn Martin wieder verfuegbar ist: Deputy-Rolle SOFORT endet. Kein schleichender Autoritaets-Transfer.

## Wann anwendbar

Diese Regel gilt fuer Design-Entscheidungen wenn:
- Ein Engpass identifiziert ist
- Asymmetrischer Schaden vorliegt (I1)
- Domains-Trennung moeglich ist (I2)
- MHC-Override erhalten bleibt (I3)
- Rueckkehr-Trigger definierbar ist (I4)

## Wann NICHT anwendbar

- Binaere Entscheidungen ohne Domain-Trennung
- K_0-naehe Aktionen (keine Deputy-Erlaubnis)
- Meta-Entscheidungen ueber die Regel selbst

## Anti-Patterns

- "Jeder darf alles" — verletzt I2
- "Deputy unbefristet" — verletzt I4
- "Deputy bei K_0" — verletzt I1 + I3
- "Konsens am Engpass" — verletzt das Kernprinzip (Konsens ist der Engpass, nicht die Loesung)

## SAE-Isomorphie

Dies ist isomorph zu **Trinity-Voting bei hoher Last:** wenn EIN Agent antworten muss und Zeit knapp ist, genuegt die hoechste score aus 3 Varianten. Konsens-Wait waere der Engpass.

Weitere Isomorphie: **Cooperative-ρ-Mechanismus bei >85% Occupancy (F9, Ostrom):** Nicht-Revenue-Agenten helfen bei Peak. Das ist verteilte Autoritaet in Hotel-Kontext.

## CRUX-Bindung

- K_0: geschuetzt durch Domain-Matrix (I2)
- Q_0: erhalten durch MHC-Override (I3)
- I_min: erhoeht (strukturierte Autoritaets-Regel)
- W_0: Regel waechst mit jeder Anwendung (I4-Rueckkehr-Trigger als Lerngelegenheit)

[CRUX-MK]
