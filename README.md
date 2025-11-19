# Dev_Stack – Local Multi-Agent Development System

A **fully local, containerized** development workflow where multiple AI agents collaborate in parallel without conflicts. Each agent works in isolation using **Docker containers** and **Git worktrees**.

---

## 🎯 Overview

Dev_Stack enables you to orchestrate multiple specialized AI agents working together on a codebase:

- **Taskmaster**: Plans and assigns tasks
- **Dev1**: Implements core business logic
- **Dev2**: Builds APIs and integrations
- **Testing**: Writes and executes tests
- **Review**: Performs code reviews
- **DevOps**: Merges code and maintains CI/CD

Each agent operates in its own Docker container and Git worktree, preventing conflicts and maintaining clean history.

---

## 🏗️ Architecture

```ascii
   ┌─────────────────┐     1. Edit JSON      ┌───────────────┐
   │  Human / Admin  ├──────────────────────►│  tasks.json   │◄──┐
   └─────────────────┘                       └───────┬───────┘   │
                                                     │           │
                                           2. Detect Change      │ 6. Update Status
                                                     │           │
                                           ┌─────────▼────────┐  │
                                           │    Watcher       │  │
                                           │ (scripts/watcher)│  │
                                           └─────────┬────────┘  │
                                                     │           │
                                           3. Wake Up Agent      │
                                                     │           │
        ┌──────────────────┬──────────────────┬──────▼───────────┴┐
        │                  │                  │                   │
  ┌─────▼──────┐    ┌──────▼─────┐    ┌──────▼─────┐      ┌───────▼──────┐
  │    Dev1    │    │    Dev2    │    │   Testing  │      │    DevOps    │
  │ (Container)│    │ (Container)│    │ (Container)│      │  (Container) │
  └─────┬──────┘    └──────┬─────┘    └──────┬─────┘      └───────┬──────┘
        │                  │                 │                    │
        │ 4. Commit        │                 │                    │
        │                  │                 │                    │
   ┌────▼──────────────────▼─────────────────▼────────────────────▼─────┐
   │                           Git Repository                           │
   │                    (Worktrees & Feature Branches)                  │
   └──────────────────────────────────┬─────────────────────────────────┘
                                      │
                            5. Pre-Commit Hooks
                             (Linting & Checks)
```

### Core Components


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
│   ├── watcher.py      # Automation service
│   ├── embed_codebase.py # RAG indexer
│   └── git_hooks/      # Quality checks
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


---

## 💼 Workflow

1.  **Task Creation**: Add a new task to `tasks.json`.
2.  **Orchestration**: The `watcher.py` sees the new task and notifies the assigned agent.
3.  **Development**: The agent works in its container, committing code to its branch.
4.  **Validation**: Git hooks block bad commits. Tests are run.
5.  **Completion**: Agent updates `tasks.json` to `REVIEW` or `COMPLETED`.

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
