# Akashic

Akashic is a Git-backed service catalog and knowledge engine designed to automatically index code repositories, extract structured metadata, and maintain developer-friendly service documentation.

This repository implements the Akashic MVP, focusing on the **FastAPI backend** (API adapter layer) and the **Knowledge Engine** (core extraction and compilation pipeline).

## Directory Layout
```
akashic/
├── pyproject.toml          # uv project dependency definitions
├── config.yaml             # workspace paths & project configuration
├── examples/sample-repo/   # local JavaScript package fixture for testing
├── knowledge/              # Git-backed knowledge repository (git initialized on sync)
├── backend/app/
│   ├── main.py             # FastAPI bootstrap & router mapping
│   ├── config.py           # configuration adapter loading config.yaml
│   ├── api/                # API router handlers
│   │   ├── projects.py     # project CRUD API
│   │   ├── sync.py         # sync background tasks & job tracking
│   │   └── knowledge.py    # knowledge base page retrieval
│   └── services/           # business layer services
│       ├── project_service.py
│       └── sync_service.py
└── knowledge_engine/
    ├── models/             # Pydantic V2 IR data structures
    ├── repository/         # git pull / local path checkout preparation
    ├── extraction/         # README and package metadata extractors
    ├── llm/                # deterministic page summary stubs
    ├── compiler/           # markdown frontmatter and human notes compilers
    └── git/                # local git add/commit automation helpers
```

## Getting Started

### Prerequisites
- Python `>=3.11`
- `uv` package manager

### Installation
Run `uv sync` to create a virtual environment and install all dependencies:
```bash
uv sync
```

### Running the API Server
Start the development FastAPI server:
```bash
uv run uvicorn backend.app.main:app --reload
```
API Documentation will be accessible at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Running Tests
Execute the unit and integration test suite:
```bash
PYTHONPATH=. uv run pytest
```

---

## API & Sync Pipeline

### 1. Register a Project
Create a project by supplying its name and Git URL (or relative local directory path):
```bash
curl -X POST http://127.0.0.1:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "sample", "repo": "./examples/sample-repo", "branch": "main"}'
```

### 2. Trigger Repository Sync
Spawn a background sync task to discover, extract metadata, and compile documentation:
```bash
curl -X POST http://127.0.0.1:8000/projects/sample/sync
# Returns {"job_id": "YOUR-JOB-ID"}
```

### 3. Check Sync Job Status
Query status of the spawned background task:
```bash
curl http://127.0.0.1:8000/sync/YOUR-JOB-ID
```

### 4. Query Compiled Knowledge Base
List all compiled documentation files:
```bash
curl http://127.0.0.1:8000/knowledge
```
Or fetch raw Markdown content:
```bash
curl http://127.0.0.1:8000/knowledge/services/sample.md
```
