---
name: universal-ai-memory-capture
description: Captures AI conversations from 6 LLM platforms via Chrome into Obsidian Second Brain
version: 1.0.0
trigger: /capture-all
---

# Universal AI Memory Capture System v1.0

## Platforms
ChatGPT | Claude.ai | Grok | Gemini | Copilot | Perplexity

## Vault
C:\Users\marti\OneDrive\Dokumente\Claude\CLaude

## Capture Dirs
captures/{platform}/YYYY-MM-DD-{title-slug}.md

## DOM Extractors
- ChatGPT: [data-message-author-role]
- Claude: .font-claude-message, .font-user-message
- Grok: article, [class*=MessageContent]
- Gemini: message-content, query/response
- Copilot: [class*=UserMessage], [class*=BotMessage]
- Perplexity: [class*=prose], query containers

## Execution
1. Open Chrome tab group with all 6 LLM tabs
2. For each: click recent chat, wait 3s, run JS extractor
3. Parse JSON, format Markdown, write to captures/
4. Log to daily note

## Schedule
Every 30 minutes via Claude Scheduled Task
