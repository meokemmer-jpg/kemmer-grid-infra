# Agent Type System [CRUX-MK]

## Jeder Branch hat einen Typ. Der Typ bestimmt was der Branch tun DARF.

### Typen und Beschraenkungen

**RESEARCH (Alpha, OffRazerAlpha):**
- DARF: Read, WebSearch, WebFetch, Grep, Glob, Agent (Subagenten), Write(findings/), Write(knowledge-diffs/)
- DARF NICHT: Write(SAE-v8/**) direkt, Bash(docker *), Bash(pytest *)
- ROLLE: Wargames, API-Research, Architektur-Entscheidungen, Specs schreiben

**CODE (Beta):**
- DARF: Read, Write, Edit, Bash, Agent, Glob, Grep, Bash(pytest), Bash(docker)
- DARF NICHT: NLM-Upload ohne Review, Write(rules/**) ohne Martin-OK
- ROLLE: SAE-Code implementieren, Tests schreiben, Docker, CI/CD

**OPS (Gamma, Delta):**
- DARF: Read, Write(branch-hub/**), Write(Vault/**), Chrome_MCP, Agent
- DARF NICHT: Write(SAE-v8/**), Bash(docker *)
- ROLLE: Vault-Management, NLM-Uploads, PMO, Kommunikation, Prozesse

### Bei Session-Start
1. Lies REGISTRY.md -- finde deinen Typ
2. Respektiere die Beschraenkungen (als RULE, wie CRUX)
3. Wenn du etwas tun MUSST das dein Typ verbietet: Delegiere an den richtigen Branch-Typ

### SAE-Isomorphie
Dies ist AgentClass (10 Enum-Werte) + klassenspezifische Strategien.
Ein HOUSEKEEPING-Agent macht kein Revenue Management. Ein RESEARCH-Branch schreibt keinen SAE-Code.
