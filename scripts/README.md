# Automation Scripts

This directory contains the "nervous system" of the Dev_Stack. These scripts are responsible for orchestration, quality control, and knowledge management.

## 1. `watcher.py` (The Orchestrator)

**Role**: The central event loop.
**When to run**: Must be running constantly in a terminal window during development.

- **Input**: Monitors `tasks.json`.
- **Action**:
    - Detects changes in `status` or `assigned`.
    - Wakes up the relevant Docker container using `docker exec`.
    - Automatically runs `render_tasks.py` to keep the Markdown view in sync.

**Usage**:
```bash
python scripts/watcher.py
```

## 2. `embed_codebase.py` (The Memory / RAG)

**Role**: Indexer for the semantic search engine.
**When to run**:
- Initially after setup.
- Periodically when large code changes happen (e.g., after a merge to `dev`).

- **Action**: Reads all code files, chunks them, and pushes embeddings to ChromaDB.
- **Goal**: Allows agents to ask "Where is the login logic?" without grepping.

**Usage**:
```bash
python scripts/embed_codebase.py
```

## 3. `render_tasks.py` (The View)

**Role**: Template engine.
**When to run**: Automatically run by `watcher.py`. Rarely run manually.

- **Input**: `tasks.json`
- **Output**: `docs/tasks.md` (Human-readable documentation).

## 4. `git_hooks/pre-commit` (The Gatekeeper)

**Role**: Quality Assurance.
**When to run**: Automatically runs on `git commit`.

- **Action**:
    - Checks Python code with `flake8`.
    - Blocks commit if errors are found.

