# Dev_Stack – Local Multi-Agent Development System

A **fully local, containerized** development workflow where multiple AI agents collaborate in parallel without conflicts.
Each agent works in isolation using **Docker containers** and **Git worktrees**.

---

## 🎯 Overview

Dev_Stack enables you to orchestrate multiple specialized AI agents working together on a codebase:

- **Taskmaster**: Plans and assigns tasks
- **Dev1**: Implements core business logic
- **Dev2**: Builds APIs and integrations
- **Testing**: Writes and executes tests
- **Review**: Performs code reviews
- **DevOps**: Merges code and maintains CI/CD

1.  **tasks.json** (Source of Truth):
    -   All tasks and their status are stored in a structured JSON format.
    -   `docs/tasks.md` is auto-generated from this file for human readability.
    -   Agents read/write JSON to avoid parsing errors.

2.  **Watcher Service** (`scripts/watcher.py`):
    -   Monitors `tasks.json` for changes.
    -   Automatically wakes up agents (via Docker Exec) when a task is assigned to them or their status changes.

3.  **RAG Memory** (ChromaDB):
    -   A vector database indexes the entire codebase.
    -   Agents can perform semantic searches to understand context without reading every file.

4.  **Safety Net** (Git Hooks):
    -   `pre-commit` hooks ensure that only valid code (linted, no syntax errors) is committed.

---

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ **Docker Desktop** installed and running
- ✅ **Git** installed (version 2.25+)
- ✅ An IDE that supports Docker (VS Code, Cursor, etc.)

**Verify installation:**
```bash
docker --version
git --version
```

---

## 🚀 Quick Start

### 1. Clone or Create Your Project

```bash
# If starting fresh
mkdir my-devstack-project
cd my-devstack-project
git init
```

### 2. Copy Dev_Stack Files

Copy all files from this repository into your project:

```
your-project/
├── docs/
│   ├── agents.md       # Agent roles and responsibilities
│   ├── tasks.md        # Task tracking (auto-generated)
│   └── decisions.md    # Architecture decisions
├── docker/
│   ├── Dockerfile.dev
│   └── entrypoint.sh
├── scripts/
│   ├── setup_worktrees.sh
│   ├── task_manager.py  # Task CLI tool
│   ├── watcher.py       # Automation service
│   ├── embed_codebase.py # RAG indexer
│   └── git_hooks/       # Quality checks
├── tasks.json          # Task database
├── docker-compose.yml
├── docker-compose.agents.yml
├── .gitignore
└── README.md
```

### 3. Initialize Git Repository

```bash
# Create initial commit
git add .
git commit -m "chore: initialize Dev_Stack"

# Create dev branch
git branch dev
```

### 4. Setup Worktrees

```bash
# On Linux/Mac/Git Bash
bash scripts/setup_worktrees.sh

# Install Git Hooks
bash scripts/install_hooks.sh
```

### 5. Start System

1. **Start Infrastructure**:
   ```bash
   # Starts ChromaDB and Agent Containers in background
   docker compose -f docker-compose.yml -f docker-compose.agents.yml up -d
   ```

2. **Start Watcher** (in a new terminal window):
   This script acts as the "nervous system", connecting tasks to agents.
   ```bash
   python scripts/watcher.py
   ```
   _Keep this terminal open to see automation logs._

### 6. Index Code (RAG)

To give agents a "memory" of the codebase:
```bash
# From the host
python scripts/embed_codebase.py
```
(See [scripts/embed_codebase.py](scripts/embed_codebase.py) for implementation details)
```


---

## 💼 Workflow

### 1. Planning (Human ↔ Taskmaster)

You generally don't edit `tasks.json` manually. Instead, use the CLI tool or chat with the **Taskmaster Agent**.

**Recommended:**
- **Chat**: "Taskmaster, create a task for login."
- **CLI**: `python scripts/task_manager.py add ...`

**Fallback:**
- Edit `tasks.json` manually (only if tools fail).

**Human**: "We need a new login page."
**Taskmaster**: Uses `scripts/task_manager.py` to create tasks:
- `T-001: Backend Login Logic` (assigned to Dev1)
- `T-002: Frontend Login Form` (assigned to Dev2)

### 2. Automation (Watcher)

The `watcher.py` script detects the new tasks in `tasks.json`.
- It **wakes up** the `agent_dev1` container.
- It **wakes up** the `agent_dev2` container.

### 3. Development (Dev Agents)

The agents receive the notification and start working.
- **Dev1**: Implements backend, commits code.
- **Dev1**: Updates status: `python scripts/task_manager.py update T-001 --status TESTING`
- **Dev2**: Implements frontend, commits code.
- **Dev2**: Updates status: `python scripts/task_manager.py update T-002 --status TESTING`

### 4. Testing

- **Watcher** detects status change to `TESTING`.
- **Testing Agent** is triggered, writes and runs tests.
- If tests pass: Updates to `REVIEW` status.
- If tests fail: Updates back to `TODO` and notifies Dev1/Dev2.

### 5. Review & Merge

- **Review Agent** is triggered when status is `REVIEW`.
- Reviews code quality, approves or requests changes.
- If approved: Updates to `APPROVED` status.
- **DevOps Agent** is triggered, merges approved code to `dev` branch.
- Updates status to `COMPLETED`.

---


## 🛠️ Agent Roles & Branches

| Agent      | Container          | Branch         | Responsibility              |
|------------|--------------------|----------------|----------------------------|
| Taskmaster | `agent_taskmaster` | `chore/devops` | Task planning & assignment |
| Dev1       | `agent_dev1`       | `feat/dev1`    | Core business logic        |
| Dev2       | `agent_dev2`       | `feat/dev2`    | APIs & integrations        |
| Testing    | `agent_testing`    | `test/testing` | Test automation & QA       |
| Review     | `agent_review`     | `review/main`  | Code review                |
| DevOps     | `agent_devops`     | `chore/devops` | CI/CD & merging            |

---

## 🐛 Troubleshooting

### Container won't start
```bash
# Rebuild images
docker compose -f docker-compose.yml -f docker-compose.agents.yml build --no-cache
```

### Watcher not triggering
- Ensure `tasks.json` is valid JSON.
- Check if Docker is running.
- Check watcher logs.

---

**Version**: 1.1  
**Last Updated**: 2025-11-19  
**Maintained By**: Dev_Stack Community
