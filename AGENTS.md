# Developer Agent Guidelines

Welcome, coding agent! This document describes rules, structural layout, and best practices for developing and maintaining the Akashic codebase. Please read it carefully before making edits.

---

## Architectural Principles

1. **Separation of Concerns**:
   - `backend/app/`: The API adapter layer. It must remain extremely thin, only parsing request formats, handling FastAPI endpoints, managing HTTP error codes, and keeping track of background tasks in-memory.
   - `knowledge_engine/`: The core business logic layer. All metadata extraction, file discovery, repository cloning/checking, markdown compilation, and git commit processes MUST reside here. Never import FastAPI/HTTP concerns here.

2. **Git is the Source of Truth**:
   - Generated files are written to the `knowledge` directory, which is tracked as a separate git repository. Every execution of the pipeline commits newly compiled pages.
   - The pipeline checks if a repository is initialized at the start of execution via `ensure_repo`.

3. **Compiler and Human Annotations**:
   - Built markdown documentation files contain a section enclosed in:
     ```html
     <!-- HUMAN START -->
     ...
     <!-- HUMAN END -->
     ```
   - When regenerations occur, the compiler MUST extract the current text in this block from any existing file and re-inject it. **Never overwrite manual developer notes.**
   - Ensure modifications to the compiler are verified against `test_pipeline.py`.

---

## Testing & Verification

- All unit and integration tests are situated under `tests/`.
- **Never mutate the real `config.yaml` or workspace `knowledge/` folder during tests.**
- Always utilize or refer to the `setup_test_config` pytest fixture in `conftest.py`, which redirect configs and checkouts to safe system temp directories.
- To execute the test suite:
  ```bash
  PYTHONPATH=. uv run pytest
  ```
