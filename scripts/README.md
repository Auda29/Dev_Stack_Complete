# Automation Scripts

This directory contains scripts for automating the agent workflow.

## watcher.py

This script monitors `docs/tasks.md` for changes and automatically triggers the assigned agent containers when a task status changes or a new task is assigned.

### Usage

```bash
python scripts/watcher.py
```

## git_hooks/

Contains Git hooks to enforce code quality.

- `pre-commit`: Checks for Python errors using `flake8`.

### Installation

```bash
bash scripts/install_hooks.sh
```

## embed_codebase.py (RAG)

Indexes the codebase into a ChromaDB vector database. This allows agents to perform semantic searches on the code.

### Prerequisites

1. Start the ChromaDB service:
   ```bash
   docker compose up -d chroma
   ```

2. Install Python dependencies (if running on host):
   ```bash
   pip install chromadb
   ```

### Usage

**From Host:**
```bash
# Windows PowerShell
$env:CHROMA_HOST="localhost"; python scripts/embed_codebase.py

# Linux/Mac
CHROMA_HOST=localhost python scripts/embed_codebase.py
```

**From Agent Container:**
```bash
docker exec -it agent_dev1 python /repo/scripts/embed_codebase.py
```
