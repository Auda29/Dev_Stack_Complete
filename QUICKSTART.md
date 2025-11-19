# Dev_Stack Quick Start Guide

Get up and running with Dev_Stack in 5 minutes.

---

## Prerequisites

```bash
docker --version  # Should show Docker 20.10+
git --version     # Should show Git 2.25+
```

---

## Setup Steps

### 1. Initialize Git

```bash
cd your-project
git init
git add .
git commit -m "chore: initialize Dev_Stack"
git branch dev
```

### 2. Setup Worktrees

**Linux/Mac:**
```bash
bash scripts/setup_worktrees.sh
```

**Windows:**
```bash
# Use Git Bash
bash scripts/setup_worktrees.sh

# Or inside container
docker compose -f docker-compose.yml -f docker-compose.agents.yml run --rm agent_devops bash scripts/setup_worktrees.sh
```

### 3. Start Containers

```bash
docker compose -f docker-compose.yml -f docker-compose.agents.yml up -d
```

### 4. Verify

```bash
docker ps  # Should show 6 agent containers + 1 ChromaDB service
```

---

## Using an Agent

### Terminal Method

```bash
# Connect to agent
docker exec -it agent_dev1 bash

# Verify location
pwd                        # /repo/.worktrees/dev1
git branch --show-current  # feat/dev1
```

### IDE Method (VS Code/Cursor)

1. Install Docker extension
2. Right-click container → "Attach Visual Studio Code"
3. Open AI assistant in attached window
4. Give initial prompt:

```
You are Dev1. Read:
- /repo/docs/agents.md
- /repo/docs/tasks.md
- /repo/docs/decisions.md

Respond: "OK Dev1. Ready for tasks."
```

---

## First Task Example

### In Taskmaster (or using task_manager.py)

**Option 1: Via Taskmaster Agent (Recommended)**
Chat with the Taskmaster agent in `agent_taskmaster` container. It will use `task_manager.py` to create tasks.

**Option 2: Via CLI**
```bash
python scripts/task_manager.py add --title "Create User Model" --assigned "Dev1" --priority "High" --description "Create a User model/entity with basic fields"
```

### In Dev1 Agent

```bash
# Work on the task
cd /repo/.worktrees/dev1
git pull --rebase origin dev

# Create your implementation
# (your code here)

# Commit
git add .
git commit -m "feat: add user model"
git push origin feat/dev1

# Update task status using task_manager.py
python scripts/task_manager.py update T-100 --status TESTING
```

---

## Basic Git Workflow

**Before starting work:**
```bash
git fetch origin
git rebase origin/dev
```

**After completing work:**
```bash
git add .
git commit -m "feat: descriptive message"
git push origin <your-branch>
```

**Status markers in tasks.md:**
- `TODO` → Ready to start
- `WIP` → Currently working
- `TESTING` → Ready for Testing agent
- `REVIEW` → Ready for Review agent
- `APPROVED` → Ready for DevOps to merge
- `COMPLETED` → Merged to dev

---

## Common Commands

### Container Management
```bash
# Start all agents
docker compose -f docker-compose.yml -f docker-compose.agents.yml up -d

# Stop all agents
docker compose -f docker-compose.yml -f docker-compose.agents.yml down

# View logs
docker logs agent_dev1

# Restart specific agent
docker restart agent_dev1

# Rebuild after Dockerfile changes
docker compose -f docker-compose.yml -f docker-compose.agents.yml build
```

### Git Commands
```bash
# See all branches
git branch -a

# See worktrees
git worktree list

# View commit history
git log --oneline --graph --all

# Check status
git status
```

---

## Troubleshooting

### Container won't start
```bash
docker logs agent_dev1
docker compose -f docker-compose.yml -f docker-compose.agents.yml build --no-cache
```

### Worktree missing
```bash
docker exec -it agent_devops bash
cd /repo
bash scripts/setup_worktrees.sh
```

### Git conflicts
```bash
git status
git fetch origin
git rebase origin/dev
# Fix conflicts in files
git add .
git rebase --continue
```

---

## Next Steps

1. Read `/docs/agents.md` for detailed agent roles
2. Read `/docs/decisions.md` for architecture guidelines
3. Start assigning tasks using `python scripts/task_manager.py` or chat with Taskmaster agent
4. Connect your IDE to agent containers
5. Begin development!

---

## Agent Quick Reference

| Agent      | Container          | Branch         | Purpose           |
|------------|--------------------|----------------|-------------------|
| Taskmaster | agent_taskmaster   | chore/devops   | Task planning     |
| Dev1       | agent_dev1         | feat/dev1      | Core logic        |
| Dev2       | agent_dev2         | feat/dev2      | APIs/UI           |
| Testing    | agent_testing      | test/testing   | QA & tests        |
| Review     | agent_review       | review/main    | Code review       |
| DevOps     | agent_devops       | chore/devops   | Merging & CI/CD   |

---

**Ready to build!** 🚀

---

## What Happens Next?

After setup, your typical workflow will be:

1. **Start the Watcher** (in a separate terminal):
   ```bash
   python scripts/watcher.py
   ```
   This monitors `tasks.json` and automatically wakes up agents when tasks are assigned.

2. **Connect to Taskmaster** (via IDE or terminal):
   - Attach to `agent_taskmaster` container
   - Chat with the agent: "Plan a new feature for user authentication"
   - Taskmaster will create tasks and assign them to Dev1/Dev2

3. **Agents work automatically**:
   - Watcher detects new tasks → wakes up assigned agents
   - Dev1/Dev2 implement → commit → update status to TESTING
   - Testing agent validates → Review agent checks → DevOps merges

4. **Monitor progress**:
   - Use `python scripts/task_manager.py report` for status overview
   - Check `docs/tasks.md` (auto-generated) for human-readable view

For complete documentation, see [README.md](README.md)
