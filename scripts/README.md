# Automation Scripts

This directory contains the "nervous system" of the Dev_Stack. These scripts are responsible for orchestration, quality control, and knowledge management.

## 1. `task_manager.py` (The Task CLI)

**Role**: Human-friendly interface to `tasks.json`.
**When to run**: Whenever you need to create, update, or query tasks.

- **Commands**:
    - `python scripts/task_manager.py add --title "..." --assigned "Dev1" --description "..."` - Create new task
    - `python scripts/task_manager.py update T-XXX --status WIP` - Update task status
    - `python scripts/task_manager.py list` - Show all tasks
    - `python scripts/task_manager.py report` - Generate markdown status report

**Usage**:
```bash
# Create a task
python scripts/task_manager.py add --title "Implement Login" --assigned "Dev1" --description "Add user authentication"

# Update status
python scripts/task_manager.py update T-001 --status TESTING

# Get status report
python scripts/task_manager.py report
```

**Note**: This is the preferred way to manage tasks. Editing `tasks.json` manually is error-prone.

## 2. `watcher.py` (The Orchestrator)

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

## 3. `embed_codebase.py` (The Memory / RAG)

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

## 4. `render_tasks.py` (The View)

**Role**: Template engine.
**When to run**: Automatically run by `watcher.py`. Rarely run manually.

- **Input**: `tasks.json`
- **Output**: `docs/tasks.md` (Human-readable documentation).

## 5. `git_hooks/pre-commit` (The Gatekeeper)

**Role**: Quality Assurance.
**When to run**: Automatically runs on `git commit`.

- **Action**:
    - Checks Python code with `flake8`.
    - Blocks commit if errors are found.

