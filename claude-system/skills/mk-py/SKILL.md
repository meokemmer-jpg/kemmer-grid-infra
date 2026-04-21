---
name: mk-py
description: Generate NotebookLM podcasts, videos, quizzes, flashcards, slide decks, mind maps from documents using Google NotebookLM API
version: 1.0.1
source: https://github.com/teng-lin/notebooklm-py
---

# MK-py Integration Skill (NotebookLM Python Client)

## Overview
Unofficial Python client for Google NotebookLM. Enables programmatic access to generate podcasts, videos, quizzes, flashcards, slide decks, mind maps and more from source documents.

## Prerequisites
- Python 3.10+
- `pip install notebooklm-py`
- `pip install "notebooklm-py[browser]"` (for initial auth)
- `playwright install chromium` (for browser login)

## Installation
```bash
pip install "notebooklm-py[browser]"
playwright install chromium
```

## Authentication
First run requires browser-based Google login:
```python
from notebooklm import NotebookLM
nb = NotebookLM()
# Browser opens for Google OAuth
```

## Core Usage Patterns

### Create Notebook from Sources
```python
from notebooklm import NotebookLM

nb = NotebookLM()
notebook = nb.create_notebook("My Research")
notebook.add_source("path/to/document.pdf")
notebook.add_source("https://example.com/article")
```

### Generate Podcast
```python
podcast = notebook.generate_audio(
    style="podcast",
    instructions="Focus on key findings"
)
podcast.download("output.mp3")
```

### Generate Quiz/Flashcards
```python
quiz = notebook.generate_quiz()
flashcards = notebook.generate_flashcards()
```

### Generate Mind Map
```python
mindmap = notebook.generate_mindmap()
```

### Batch Operations
```python
# Add multiple sources
for doc in documents:
    notebook.add_source(doc)

# Generate multiple outputs
podcast = notebook.generate_audio()
slides = notebook.generate_slides()
summary = notebook.generate_summary()
```

## When to Use
- Converting research documents into audio summaries
- Creating study materials (quizzes, flashcards) from papers
- Generating slide decks from long-form content
- Building mind maps for visual knowledge organization
- Batch processing multiple documents

## Limitations
- Uses undocumented Google APIs (may break without notice)
- Requires Google account authentication
- Not suitable for production systems
- Rate limits apply
