# PATCH: CLAUDE.md §0.3 — MAC-M5-LOCAL-INFERENCE-NODE

*Einzufügen in ~/.claude/CLAUDE.md nach Sektion 0.2 (Bootstrap-Protokoll) durch PC1 Master nach Mac-Bootstrap-Abschluss.*

### 0.3 Spezialisierung: Mac M5 Max (Local-Inference)

Diese Regeln gelten exklusiv, wenn `$MACHINE_ROLE == "LOCAL-INFERENCE"`.

#### A. Tooling & Capabilities

- **Primäres LLM (lokal):** `gemma2:27b` via Ollama auf `localhost:11434`
- **Secondary (lokal):** `llama3.3:70b-q4` (falls installiert, fuer komplexere Tasks)
- **Embedding:** `mxbai-embed-large` lokal fuer RAG auf G:/
- **Cloud-Tools** (wie auf anderen Machines): `gh`, `gemini`, `codex`, `copilot` nutzbar via normales Routing

#### B. Routing-Logik (Local-First)

Diese Routing-Regel ueberschreibt den Default:

- **Routine-Code** (Refactoring, Docstrings, Tests, Dummy-Fix): → **Immer lokal auf gemma2:27b**
- **Batch-Klassifikation** (Rules-Tagging, Skill-Indexing, Metadata-Enrichment): → **Immer lokal**
- **RAG-Embedding** (Repo-Suche, Context-Retrieval): → **Immer lokal mit mxbai-embed-large**
- **Logik-Fehler** (Bugs, Algorithmen, Multi-Step-Reasoning): → **Claude-Sonnet** (via Cloud)
- **Architektur** (K_0/Q_0/Phronesis/Rule-Design): → **Niemals lokal. Immer Cloud-Claude-Opus über LiteLLM-Router.**
- **Cross-LLM-Haertung E3+**: → **Cloud** (Flat-Abos Codex+Gemini+Grok, nicht lokal)

#### C. Performance-Gates

- Erwarteter Durchput: >40 Tokens/sec fuer `gemma2:27b`
- Wenn Latenz >2s pro Response → Pruefe Hintergrundprozesse (Video-Encoding/Time-Machine/Indexierung)
- Wenn `ollama list` sagt `27b` ist nicht geladen → `ollama run gemma2:27b` prewarm

#### D. LiteLLM-Router-Integration

Der Mac-Node wird von PC1's LiteLLM-Router als Endpoint `gemma2-27b-local` registriert. Router-Config (`router/litellm-router-config.yaml` im kemmer-grid-infra Repo) priorisiert Mac fuer:
- `criticality_score < 0.3` (Routine)
- `cost_budget = 0` (lokal = gratis)
- Priority-Tag `low` oder `zero-cost`

Bei Mac-Outage: automatischer Fallback auf Cloud-Gemini oder Cloud-Claude-Sonnet (im Router definiert).

#### E. Scheduled Tasks

**Erlaubt:**
- `com.kemmer.heartbeat` (alle 5 Min, LAN-Publish + Status)
- `com.kemmer.ollama-keepalive` (Modell im VRAM halten)

**Verboten (Master-Only):**
- `com.kemmer.DF-*` (Dark-Factories)
- `com.kemmer.NLM-*` (NotebookLM-Automation)
- `com.kemmer.vault-sync` (zentral auf PC1)
- `com.kemmer.archon-*` (Master-exklusiv)

#### F. Kill-Switch-Specifik Mac

Path: `~/kemmer-grid/scripts/kill-switch.sh`
Trigger ausserdem:
- macOS `Low Battery` unter 10% (falls Laptop, nicht Desktop-Mac)
- Disk-Space <5GB auf Home-Volume (verhindert Log-Flooding-Crash)

#### G. Branch-Hub-Zugriff

Mac liest/schreibt via `/Volumes/GoogleDrive/Meine Ablage/Claude-Knowledge-System/branch-hub/`. Schreibregeln:
- Eigenes Status-File: `branch-hub/status/mac-m5-01-status.md`
- Eigene Instanz-Workspace: `/Volumes/.../areas/family/instance-mac-m5-01/`
- BEACON-Append mit 5-Min-Lock-Check (wie andere Branches)
- Keine direkten Canon-Writes ohne Cross-LLM-Review

#### H. Connection zu anderen Grid-Nodes

LAN-Discovery via `branch-hub/grid-endpoints.json`. Bei Master-Unreachable >30 Min:
- Lokaler Safe-Mode
- Ollama bleibt online (damit andere Nodes noch routen koennen)
- Keine Destructive-Actions
- Kein Retry-Spam auf Master-Endpoint

[CRUX-MK]
