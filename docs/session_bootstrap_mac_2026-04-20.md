# 🛠 Session Bootstrap Paket: Mac M5 Max Instanz (2026-04-20)

**Zielgruppe:** Claude-Instanz die auf Mac M5 Max frisch bootet.
**Dein Erst-Satz bei der ersten Antwort:** "Ich bin Claude-Instanz auf Mac M5 Max, starte Bootstrap nach kemmer-grid-infra/docs/session_bootstrap_mac_2026-04-20.md."

---

## Sektion 1: Voraussetzungen (Phase-0)

Prüfe Vorhandensein von (Terminal):
```bash
brew --version        # Homebrew (sonst: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)")
xcode-select -p       # Xcode CLI Tools (sonst: xcode-select --install)
python3 --version     # >=3.12
node --version        # LTS v20+
git --version         # >=2.40
gh --version          # GitHub CLI
```

## Sektion 2: Infrastruktur-Seed (Phase-1)

```bash
cd ~
git clone https://github.com/meokemmer-jpg/kemmer-grid-infra.git kemmer-grid
cd kemmer-grid
```

## Sektion 3: Ollama & Modell-Setup (Phase-2)

```bash
brew install ollama
ollama serve &                  # Hintergrund-Service Port 11434
ollama pull gemma2:27b          # ~16GB, 5-15 Min Download
ollama pull mxbai-embed-large   # Embedding-Modell
# Optional upgrade:
# ollama pull llama3.3:70b-instruct-q4_K_M  # ~40GB, braucht 48GB+ RAM
```

**Verifiziere Metal-Beschleunigung:**
```bash
curl http://localhost:11434/api/generate -d '{"model":"gemma2:27b","prompt":"test"}' | head -20
# Aktivitätsanzeige: GPU-Last sollte >50% sein bei Inferenz
```

## Sektion 4: Claude-Code Setup (Phase-3)

```bash
npm install -g @anthropic-ai/claude-code
claude --version                # >=2.0
claude login                    # Browser-OAuth, gleiches Account wie Martin auf PC1
```

**WICHTIG:** Claude-Session auf Drive `G:/` starten, nicht lokal. Martin wird das Drive sichtbar machen (Google Drive File Stream).

## Sektion 5: Environment Variables (Phase-4)

In `~/.zshrc`:
```bash
export MACHINE_ROLE="LOCAL-INFERENCE"
export MACHINE_ID="MAC-M5-01"
export GEMINI_API_KEY="<von Martin>"
export XAI_API_KEY="<von Martin>"
export GRID_MASTER_IP="192.168.1.10"  # PC1 LAN-IP, Martin passt an
export OLLAMA_HOST="0.0.0.0:11434"     # LAN-exposed fuer andere Grid-Nodes
export ENABLE_PROMPT_CACHING_1H="true"
```

Dann: `source ~/.zshrc`

## Sektion 6: Grid-Bootstrap Execution (Phase-5)

```bash
cd ~/kemmer-grid
sh ./scripts/pre-bootstrap-check.sh
# Erwartet: Alle gruen ausser evtl. MCP-Server (optional)

sh ./scripts/grid-bootstrap.sh --role local-inference
# Idempotent, resume-faehig. Bei Fehler: erneut ausfuehren.
```

## Sektion 7: LAN-Publishing (Phase-6)

Registriere Endpoint:
```bash
python3 -c "
import json, socket, datetime
f='/Volumes/GoogleDrive/Meine Ablage/Claude-Knowledge-System/branch-hub/grid-endpoints.json'
try: d=json.load(open(f))
except: d={}
d['MAC-M5-01']={
  'machine_id':'MAC-M5-01',
  'lan_ip':socket.gethostbyname(socket.gethostname()),
  'role':'LOCAL-INFERENCE',
  'ports':{'ollama':11434},
  'model_list':['gemma2:27b','mxbai-embed-large'],
  'capabilities':['gpu-inference','apple-silicon-m5'],
  'last_heartbeat':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'quarantine_status':False
}
json.dump(d,open(f,'w'),indent=2)
print('published')
"
```

## Sektion 8: Cross-Node Test (Phase-7)

Von PC1 aus testen (oder lokal hier):
```bash
curl http://<MAC-LAN-IP>:11434/api/generate -d '{"model": "gemma2:27b", "prompt": "Status? Kurz."}'
# Erwartete Antwort: JSON mit "response" Feld, non-empty
```

## Sektion 9: Master-Handshake (Phase-8)

```bash
cat > "/Volumes/GoogleDrive/Meine Ablage/Claude-Knowledge-System/branch-hub/inbox/to-work-d2-from-mac-m5-handshake-2026-04-20.md" << 'EOF'
---
from: MAC-M5-01 (Local-Inference-Node)
to: Opus47-Work-D2 (PC1 Master)
date: 2026-04-20
status: BOOTSTRAP_COMPLETE
crux-mk: true
---
# Mac-Handshake

Ich bin online. Ollama:11434 mit gemma2:27b verfuegbar.

- LAN-IP: <IP>
- Modell: gemma2:27b (Q4 quantisiert)
- Bootstrap: alle Phasen 1-12 durchgelaufen
- Kill-Switch: getestet
- Scheduled Tasks: nur kemmer-heartbeat + ollama-keepalive

Warte auf Master-Ack + erste Routing-Zuweisung.

[CRUX-MK]
EOF
```

## Sektion 10: Scheduled Tasks (Phase-9)

Nur zwei launchd-Plists:
```bash
# kemmer-heartbeat alle 5 Min
cat > ~/Library/LaunchAgents/com.kemmer.heartbeat.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.kemmer.heartbeat</string>
  <key>ProgramArguments</key>
  <array><string>/bin/sh</string><string>/Users/$USER/kemmer-grid/scripts/heartbeat.sh</string></array>
  <key>StartInterval</key><integer>300</integer>
  <key>StandardOutPath</key><string>/tmp/kemmer-heartbeat.log</string>
</dict>
</plist>
EOF
launchctl load ~/Library/LaunchAgents/com.kemmer.heartbeat.plist

# ollama-keepalive (OLLAMA_KEEP_ALIVE env var)
launchctl setenv OLLAMA_KEEP_ALIVE "2h"
```

## Sektion 11: Anti-Passivitaets-Check (Phase-10)

Wenn keine Task-Zuweisung: Lies `G:/Meine Ablage/Claude-Knowledge-System/branch-hub/META-ROADMAP.md` und scanne IDLE-PRIO-Section. Pulle Items mit Lane-Empfehlung "Local-Inference" oder "Mac".

Keine DF-*/NLM-* Task (gehoert Master).

## Sektion 12: Kill-Switch Test (Phase-11)

```bash
sh ./scripts/kill-switch.sh test
cat ~/.kemmer-grid/killed.flag          # sollte jetzt existieren
rm ~/.kemmer-grid/killed.flag           # cleanup
sh ./scripts/kill-switch.sh status      # sollte "not killed" sagen
```

## Sektion 13: Fehlerbehebung (Phase-12)

Bei fehlenden Libraries dokumentieren in `mac-setup-log.md`:
```bash
echo "$(date -u +%FT%TZ) - fehlt: $LIB - action: brew install $LIB" >> mac-setup-log.md
```

**Keine manuellen Fixes ohne Log!** Jeder unnotierte Fix wird spaeter zum Drift-Problem.

---

## Hard-Stops (immer aktiv, siehe MASTERPLAN-v2)

| Trigger | Action |
|---------|--------|
| Martin-h/Woche steigt >30% vs Baseline | HALT + BEACON-Alert |
| API-Cost >50 EUR/h (dieser Node) | AUTO-KILL (kill-switch) |
| >100 Auto-Repair-Versuche in 24h | AUTO-KILL |
| Rho-Netto nach W8 <+180 EUR | SHUTDOWN-Empfehlung an Martin |

[CRUX-MK]
