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

```
┌─────────────┐
│ Taskmaster  │ ← Plans tasks, assigns to agents
└──────┬──────┘
       │
   ┌───┴───────────────┬──────────────┐
   │                   │              │
┌──▼───┐         ┌─────▼──┐      ┌───▼────┐
│ Dev1 │         │  Dev2  │      │Testing │
│(Core)│         │(API/UI)│      │  (QA)  │
└──┬───┘         └────┬───┘      └───┬────┘
   │                  │              │
   └──────────┬───────┴──────────────┘
              │
         ┌────▼─────┐
         │  Review  │ ← Code quality checks
         └────┬─────┘
              │
         ┌────▼─────┐
         │  DevOps  │ ← Merges to dev branch
         └──────────┘
```

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
│   ├── tasks.md        # Task tracking
│   └── decisions.md    # Architecture decisions
├── docker/
│   ├── Dockerfile.dev
│   └── entrypoint.sh
├── scripts/
│   └── setup_worktrees.sh
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
# On Linux/Mac
bash scripts/setup_worktrees.sh

# On Windows (Git Bash)
bash scripts/setup_worktrees.sh

# Or manually inside DevOps container
docker compose -f docker-compose.yml -f docker-compose.agents.yml run --rm agent_devops bash scripts/setup_worktrees.sh
```

This creates isolated working directories for each agent:
```
.worktrees/
├── devops/     (branch: chore/devops)
├── dev1/       (branch: feat/dev1)
├── dev2/       (branch: feat/dev2)
├── testing/    (branch: test/testing)
└── review/     (branch: review/main)
```

### 5. Start Agent Containers

```bash
docker compose -f docker-compose.yml -f docker-compose.agents.yml up -d
```

**Verify containers are running:**
```bash
docker ps
```

You should see 6 containers:
- agent_taskmaster
- agent_dev1
- agent_dev2
- agent_testing
- agent_review
- agent_devops

### 6. Connect to an Agent

```bash
# Open a shell in any agent
docker exec -it agent_dev1 bash

# Check your location
pwd
git branch --show-current
```

---

## 💼 Using Agents in Your IDE

### VS Code / Cursor Setup

1. **Install Docker Extension** (if not already installed)

2. **Attach to Container**:
   - Click Docker icon in sidebar
   - Right-click on `agent_dev1` → "Attach Visual Studio Code"
   - Or use Command Palette: "Remote-Containers: Attach to Running Container"

3. **Open Agent Chat**:
   - In the attached container window, open your AI assistant
   - Give the agent its initial prompt:

```
You are Dev1, a core development agent in the Dev_Stack system.

Please read these files to understand your role:
- /repo/docs/agents.md
- /repo/docs/tasks.md
- /repo/docs/decisions.md

Confirm your understanding by responding: "OK Dev1. Ready for task assignment."
```

4. **Assign a Task**:
```
Implement task T-XXX from /repo/docs/tasks.md
```

### Working with Multiple Agents

You can have multiple IDE windows open, each attached to a different agent container:

- **Window 1**: Attached to `agent_dev1` → Implementing core logic
- **Window 2**: Attached to `agent_dev2` → Building API endpoints
- **Window 3**: Attached to `agent_testing` → Writing tests

---

## 📚 Documentation Structure

### `docs/agents.md`
Complete agent role definitions, responsibilities, workflows, and communication protocols.

**Key sections:**
- Agent startup procedures
- Git workflow rules
- Individual agent responsibilities
- Handover processes

### `docs/tasks.md`
Source of truth for all project tasks.

**Task format:**
```markdown
### T-XXX: Task Title
**Status**: TODO/WIP/TESTING/REVIEW/APPROVED/COMPLETED
**Assigned**: Agent Name
**Description**: What needs to be done
**Acceptance Criteria**: Checkboxes for completion
```

### `docs/decisions.md`
Architecture Decision Records (ADRs) documenting important technical decisions.

**Examples:**
- ADR-001: Multi-Agent Development with Git Worktrees
- ADR-002: Docker Container Isolation
- ADR-003: Commit Message Convention

---

## 🔄 Typical Workflow

### Creating a New Feature

1. **Taskmaster** creates task in `docs/tasks.md`:
```markdown
### T-042: Add User Login

**Status**: TODO
**Assigned**: Dev1
**Priority**: High
```

2. **Dev1** implements the core logic:
```bash
# In agent_dev1 container
cd /repo/.worktrees/dev1
git pull --rebase origin dev
# ... implement feature ...
git add .
git commit -m "feat: implement user login logic"
git push origin feat/dev1
```

3. **Dev2** adds the API endpoint:
```bash
# In agent_dev2 container
cd /repo/.worktrees/dev2
git pull --rebase origin dev
# ... implement API ...
git commit -m "feat: add login endpoint"
git push origin feat/dev2
```

4. **Testing** validates:
```bash
# In agent_testing container
git fetch origin
git merge origin/feat/dev1
git merge origin/feat/dev2
# ... write and run tests ...
git commit -m "test: add login tests"
```

5. **Review** checks code quality:
```markdown
## Review: T-042

**Status**: APPROVED

**Strengths**:
- Clean implementation
- Good error handling

**Issues**: None

**Next Steps**: Ready for DevOps
```

6. **DevOps** merges to dev:
```bash
# In agent_devops container
git switch dev
git pull --rebase origin dev
git merge --no-ff feat/dev1 -m "Merge feat/dev1: T-042 user login"
git merge --no-ff feat/dev2 -m "Merge feat/dev2: T-042 login endpoint"
git push origin dev
```

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

## 🎛️ Configuration

### Adding Language Support

Edit `docker/Dockerfile.dev` to add your technology stack:

**For Node.js:**
```dockerfile
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*
```

**For Python:**
```dockerfile
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*
```

**For Go:**
```dockerfile
RUN wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz \
    && rm go1.21.5.linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin
```

After changes, rebuild:
```bash
docker compose -f docker-compose.yml -f docker-compose.agents.yml build
```

### Adding Shared Services

Edit `docker-compose.yml` to add databases, cache, etc.:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: devpass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs agent_dev1

# Rebuild images
docker compose -f docker-compose.yml -f docker-compose.agents.yml build --no-cache
```

### Worktree errors
```bash
# Inside agent_devops container
git worktree prune
bash scripts/setup_worktrees.sh
```

### Git conflicts
```bash
# In affected agent container
git status
git fetch origin
git rebase origin/dev
# Resolve conflicts manually
git add .
git rebase --continue
```

### Permission issues (Linux)
```bash
# Fix ownership
sudo chown -R $USER:$USER .
```

---

## 📖 Advanced Usage

### Parallel Task Execution

For independent tasks, multiple agents can work simultaneously:

```markdown
# In tasks.md
### T-050: Add Search Feature
**Status**: WIP
**Assigned**: Dev1
**Dependencies**: None

### T-051: Add Export Feature
**Status**: WIP
**Assigned**: Dev2
**Dependencies**: None
```

Both agents can work without conflicts due to worktree isolation.

### Custom Agent

To add a new agent:

1. Add to `docker-compose.agents.yml`:
```yaml
agent_docs:
  build:
    context: ./docker
    dockerfile: Dockerfile.dev
  container_name: agent_docs
  volumes:
    - .:/repo
  working_dir: /repo/.worktrees/docs
  environment:
    - AGENT_NAME=Docs
  command: tail -f /dev/null
```

2. Add worktree to `scripts/setup_worktrees.sh`:
```bash
AGENTS=(
    # ... existing agents ...
    "docs:docs/documentation"
)
```

3. Document role in `docs/agents.md`

---

## 🔒 Security & Privacy

- ✅ **Fully Local**: No data leaves your machine
- ✅ **Isolated**: Each agent in separate container
- ✅ **No Cloud**: Works 100% offline
- ⚠️ **Secrets**: Use `.env` files (add to `.gitignore`)

---

## 📊 Monitoring & Status

### Check Agent Status
```bash
# List all containers
docker ps

# Check specific agent
docker exec -it agent_dev1 git status
```

### View Task Progress
```bash
# Inside any agent container
cat /repo/docs/tasks.md
```

### Git History
```bash
# See what all agents did
git log --all --graph --oneline --decorate
```

---

## 🧹 Cleanup

### Stop all agents
```bash
docker compose -f docker-compose.yml -f docker-compose.agents.yml down
```

### Remove worktrees
```bash
git worktree remove .worktrees/dev1
git worktree remove .worktrees/dev2
# ... etc ...

# Or remove all
rm -rf .worktrees
git worktree prune
```

### Complete cleanup
```bash
# Stop and remove containers
docker compose -f docker-compose.yml -f docker-compose.agents.yml down -v

# Remove images
docker compose -f docker-compose.yml -f docker-compose.agents.yml down --rmi all
```

---

## 🤝 Contributing

This is a framework for your own projects. Adapt it to your needs:

- Modify agent roles
- Add more agents
- Adjust workflows
- Customize documentation

---

## 📝 License

This framework is provided as-is for local AI-assisted development. Use and modify freely.

---

## 🆘 Getting Help

1. **Check Documentation**: Read `docs/agents.md`, `docs/decisions.md`
2. **Review Logs**: `docker logs <container-name>`
3. **Verify Setup**: Ensure worktrees and branches exist
4. **Git Status**: Check for conflicts or uncommitted changes

---

## 🎯 Best Practices

1. **Always read documentation** before starting work
2. **Update tasks.md** when status changes
3. **Commit early and often** with clear messages
4. **Rebase before committing** to avoid merge conflicts
5. **Let DevOps handle merges** – don't merge yourself
6. **Test before handing over** to next agent
7. **Document decisions** in `decisions.md`

---

**Version**: 1.0  
**Last Updated**: 2025-11-07  
**Maintained By**: Dev_Stack Community

---

## 🚀 Next Steps

1. ✅ Read `docs/agents.md`
2. ✅ Initialize your project
3. ✅ Setup worktrees
4. ✅ Start containers
5. ✅ Assign first task to Taskmaster
6. 🎉 Start building!
