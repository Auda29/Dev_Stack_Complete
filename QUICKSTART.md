# Dev_Stack Quick Start Guide

Get your AI agents coding in **5 minutes**! ⚡

---

## ✅ Prerequisites Check

```bash
docker --version   # Should show Docker 20.10+
git --version      # Should show Git 2.25+
python3 --version  # Should show Python 3.8+
```

**You'll also need:**
- An API key from [OpenAI](https://platform.openai.com/api-keys) OR [Anthropic](https://console.anthropic.com/)
- About 5-10 minutes

---

---

## ⚡ Automated Start (Recommended)

After cloning and setting up your environment, you can use the automated session starter:

1. **Clone & Initialize** (see Step 1 below)
2. **Configure .env** (see Step 3 below)
3. **Setup Worktrees** (see Step 4 below)
4. **Run the Starter Script:**

```bash
python scripts/start_session.py
```

This script will automatically:
- Install dependencies
- Start Docker services
- Launch the Watcher
- Launch the Taskmaster Chat

---

## 🚀 Detailed Setup (Manual)

### Step 1: Clone & Initialize (1 min)

```bash
# Clone the repository
git clone https://github.com/your/dev_stack.git my-ai-project
cd my-ai-project

# Initialize Git
git init
git add .
git commit -m "chore: initialize Dev_Stack"
git branch dev
```

### Step 2: Install Dependencies (2 min)

```bash
# Install Python packages
pip install -r requirements.txt
```

This installs all LLM integrations, RAG support, and utilities.

### Step 3: Configure API Keys (1 min)

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your API keys
# You need at least one of:
# - OPENAI_API_KEY=sk-...
# - ANTHROPIC_API_KEY=sk-ant-...
```

**Example `.env`:**
```env
# Use Anthropic for most agents
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Use OpenAI for Taskmaster & Review
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
```

### Step 4: Setup Worktrees (1 min)

```bash
# Bash (Linux/Mac/Git Bash)
bash scripts/setup_worktrees.sh

# PowerShell (Windows)
.\scripts\setup_worktrees.ps1
```

### Step 5: Start the System (30 sec)

```bash
# Start ChromaDB + all 6 AI agents
docker compose -f docker-compose.yml -f docker-compose.agents.yml up -d

# Verify all containers are running
docker ps
```

You should see 7 containers:
- `chroma` - Vector database
- `agent_taskmaster` - Planning agent
- `agent_dev1` - Core development
- `agent_dev2` - API/UI development
- `agent_testing` - QA agent
- `agent_review` - Code review
- `agent_devops` - Deployment agent

---

## 🎯 Your First AI-Generated Code

### Start the Watcher

The watcher monitors `tasks.json` and notifies agents when tasks are added or updated:

```bash
# In Terminal 1, start the watcher
python scripts/watcher.py
```

**You should see:**
```
Starting Watcher for tasks.json...
Loaded 0 tasks. Monitoring for changes...
```

> **Keep this running!** The watcher is essential for agents to receive task notifications.

### Start Interactive Taskmaster

Now start the interactive Taskmaster chat interface:

```bash
# In Terminal 2, start Taskmaster
python scripts/taskmaster_chat.py
```

**You'll see:**
```
============================================================
🎯 Taskmaster - AI Project Manager
============================================================

Welcome! I'm your AI Taskmaster. Tell me what you want to build,
and I'll break it down into tasks and assign them to the team.

Commands:
  - Type your request naturally
  - 'status' - View current tasks
  - 'help' - Show help
  - 'quit' or 'exit' - Exit chat
============================================================

You: 
```

### Create Your First Task

Just chat naturally with the Taskmaster:

```
You: Create a greeting function that takes a name and returns a personalized greeting

🎯 Taskmaster: I'll create a task for this simple function:

📝 Creating tasks...

  ✅ Created T-002: Create a greeting function → Dev1

✅ Created 1 task(s). The watcher will notify agents.
```

### Watch the Magic ✨

In a third terminal, watch the Dev1 agent work:

```bash
# Terminal 3: Watch Dev1 agent
docker logs -f agent_dev1
```

**You'll see:**
```
📨 Received notification: NEW TASK ASSIGNMENT: T-002...
🎯 Picking up task T-002
🔍 Searching codebase for relevant context...
   Found 5 relevant code snippets
🤖 Querying LLM for implementation...
✅ LLM Response received (847 tokens)
📝 Parsing and applying code changes...
✅ Successfully applied 2 file changes
   - utils/greetings.py
   - utils/__init__.py
Auto-reassigning task T-002 to Testing (status: TESTING)
✓ Task T-002 reassigned to Testing
```

### Check the Result

> **⚠️ IMPORTANT**: Agents create code in **worktrees**, not your main directory!

Each agent works in an isolated Git worktree:

```bash
# Code is in the agent's worktree
cat .worktrees/dev1/utils/greetings.py
```

**The AI wrote this:**
```python
def greet(name):
    """Return a personalized greeting."""
    return f"Hello, {name}! Welcome to Dev_Stack!"
```

🎉 **Congratulations!** Your AI agent just wrote its first code!

**Where to find generated code:**
```bash
# Dev1's code
ls .worktrees/dev1/

# Testing's code
ls .worktrees/testing/

# All Python files created by agents
Get-ChildItem -Path .worktrees -Recurse -Filter "*.py"  # PowerShell
find .worktrees -name "*.py"  # Bash
```

### How the Feature Branch Workflow Works

When tasks complete the full pipeline (DEV → TESTING → REVIEW → APPROVED), the DevOps agent automatically:

1. **Creates an integration script** (e.g., `integrate_T-002.sh`)
2. **Runs the script** to create a feature branch
3. **Copies code** from worktrees to the feature branch  
4. **Pushes to origin** for your review

**Check for feature branches:**
```bash
# List all feature branches
git branch -r --list "origin/feature/*"

# Check out a feature branch
git checkout feature/t-002-greeting-function

# Now the code is in your main repo!
cat utils/greetings.py
```

### Try Something More Complex

Back in the Taskmaster chat:

```
You: I need a REST API for managing blog posts with CRUD operations

🎯 Taskmaster: I'll break this down into tasks for the team:

1. Create BlogPost model (Dev1)
2. Add CRUD endpoints for blog posts (Dev2)
3. Add tests for blog API (Testing)

📝 Creating tasks...

  ✅ Created T-003: Create BlogPost model → Dev1
  ✅ Created T-004: Add blog CRUD endpoints → Dev2
  ✅ Created T-005: Add blog API tests → Testing

✅ Created 3 task(s). The watcher will notify agents.

You: status

📊 Current Tasks
============================================================

TODO:
  T-003: Create BlogPost model (Dev1)
  T-004: Add blog CRUD endpoints (Dev2)
  T-005: Add blog API tests (Testing)

TESTING:
  T-002: Create a greeting function (Testing)

============================================================
```

The agents will automatically work on all assigned tasks in parallel!

---

## 🧠 Enable RAG (Recommended)

RAG (Retrieval-Augmented Generation) gives agents "memory" of your codebase:

```bash
# Index your codebase
python scripts/embed_codebase.py
```

Now agents will search for similar code before generating new code, resulting in:
- ✅ Consistent coding patterns
- ✅ Reuse of existing utilities
- ✅ Awareness of project structure
- ✅ Better code quality

---

## 📚 Understanding the Workflow

### 1. Task Creation

```bash
python scripts/task_manager.py add \
  --title "Add user authentication" \
  --assigned "Dev1" \
  --description "Implement JWT-based login and registration"
```

### 2. Automatic Execution

**Dev1 Agent** (Anthropic Claude):
1. Queries RAG for similar auth code
2. Builds context with relevant snippets
3. Generates implementation using Claude
4. Validates syntax
5. Creates files with backups
6. Updates status to `TESTING`

**Testing Agent** (Anthropic Claude):
1. Receives notification
2. Generates test cases
3. Runs tests
4. Updates status to `REVIEW`

**Review Agent** (OpenAI GPT-4o):
1. Reviews code quality
2. Checks security
3. Approves or requests changes
4. Updates status to `APPROVED`

**DevOps Agent** (Anthropic Claude):
1. Creates integration script: `integrate_T-XXX.sh`
2. Script runs `devops_git_integration.py`
3. Creates feature branch: `feature/T-XXX-description`
4. Copies code from worktree to branch
5. Pushes feature branch to origin
6. Updates status to `COMPLETED`

### 3. Review and Merge Completed Features

When the DevOps agent completes integration, it creates a feature branch:

**View available feature branches:**
```bash
# Local branches
git branch --list "feature/*"

# Remote branches (pushed by DevOps)
git branch -r --list "origin/feature/*"
```

**Review changes:**
```bash
# Fetch latest from DevOps
git fetch origin

# Check out the feature branch
git checkout feature/T-001-task-name

# Review the code (now in main repo, not worktrees!)
cat src/module.py

# View commits
git log

# Compare to main
git diff main
```

**Merge to main (if approved):**
```bash
git checkout main
git merge feature/T-001-task-name
git push origin main
```

**Or create a Pull Request** if using GitHub/GitLab for additional review.

### 4. Monitor Progress

```bash
# View all tasks
python scripts/task_manager.py list

# Generate HTML dashboard
python scripts/task_manager.py report --html
open dashboard.html
```

---

## 🛠️ Common Tasks

### View Agent Logs

```bash
# Watch specific agent
docker logs -f agent_dev1

# View all agent logs
docker compose -f docker-compose.agents.yml logs -f
```

### Restart an Agent

```bash
docker restart agent_dev1
```

### Stop Everything

```bash
docker compose -f docker-compose.yml -f docker-compose.agents.yml down
```

### Re-index Codebase (after major changes)

```bash
python scripts/embed_codebase.py
```

---

## 🎓 Advanced: Multi-Agent Collaboration

Create a complex feature that requires multiple agents:

```bash
# Taskmaster creates tasks
python scripts/task_manager.py add \
  --title "User Profile API" \
  --assigned "Dev1" \
  --description "Create User model and profile logic"

python scripts/task_manager.py add \
  --title "Profile REST Endpoints" \
  --assigned "Dev2" \
  --description "Create GET/PUT /api/profile endpoints"

python scripts/task_manager.py add \
  --title "Profile Tests" \
  --assigned "Testing" \
  --description "Test user profile functionality"
```

**Watch them collaborate:**
```bash
# Terminal 1: Dev1
docker logs -f agent_dev1

# Terminal 2: Dev2
docker logs -f agent_dev2

# Terminal 3: Testing
docker logs -f agent_testing
```

---

## 💡 Tips & Best Practices

### 1. Write Clear Task Descriptions

❌ **Bad:**
```bash
--description "Add login"
```

✅ **Good:**
```bash
--description "Implement JWT-based login with email/password. Include password hashing with bcrypt, token generation with 24h expiry, and refresh token support."
```

### 2. Use Technical Notes

```bash
python scripts/task_manager.py add \
  --title "Add caching" \
  --assigned "Dev1" \
  --description "Add Redis caching for user profiles" \
  --technical-notes "Use redis-py library. Cache TTL: 1 hour. Invalidate on profile update."
```

### 3. Monitor Token Usage

Check conversation logs to see costs:
```bash
cat work_artifacts/contexts/T-001_Dev1_conversation.md
```

### 4. Optimize for Cost

Edit `config/agent_config.yml`:
```yaml
dev1:
  max_tokens: 4000      # Reduce for simpler tasks
  temperature: 0.3      # Lower = more focused
  rag_chunks: 5         # Fewer chunks = less context
```

---

## 🐛 Troubleshooting

### Agent Not Responding

```bash
# Check if API key is set
docker exec agent_dev1 env | grep API_KEY

# Check logs for errors
docker logs agent_dev1

# Restart agent
docker restart agent_dev1
```

### "No relevant code found"

```bash
# ChromaDB not running
docker ps | grep chroma

# Codebase not indexed
python scripts/embed_codebase.py
```

### "Token limit exceeded"

Reduce context in `config/agent_config.yml`:
```yaml
dev1:
  max_tokens: 2000
  rag_chunks: 3
```

### Files Not Created

```bash
# Check agent logs for errors
docker logs agent_dev1 | grep "Error"

# Verify file permissions
docker exec agent_dev1 ls -la /repo
```

---

## 📖 Next Steps

### Learn More

1. **[README.md](README.md)** - Full documentation
2. **[docs/llm_integration.md](docs/llm_integration.md)** - LLM integration guide
3. **[docs/agents.md](docs/agents.md)** - Detailed agent roles
4. **[docs/architecture_decisions.md](docs/architecture_decisions.md)** - Design decisions

### Try Advanced Features

1. **Custom Agent Prompts** - Edit `agent_listener.py` → `load_agent_prompt()`
2. **Different LLM Providers** - Mix OpenAI, Anthropic, Google per agent
3. **Agent-Specific Models** - Use GPT-4o-mini for simple tasks
4. **Conversation Export** - Review full agent reasoning in `work_artifacts/`

### Build Something Real

```bash
# Example: Build a REST API
python scripts/task_manager.py add \
  --title "Create FastAPI project structure" \
  --assigned "Dev1"

python scripts/task_manager.py add \
  --title "Add CRUD endpoints for todos" \
  --assigned "Dev2"

python scripts/task_manager.py add \
  --title "Add API tests" \
  --assigned "Testing"
```

---

## 🎯 Quick Reference

### Agent Overview

| Agent | LLM | Purpose |
|-------|-----|---------|
| Taskmaster | GPT-4o | Planning & task decomposition |
| Dev1 | Claude | Core business logic |
| Dev2 | Claude | APIs & integrations |
| Testing | Claude | Test generation & QA |
| Review | GPT-4o | Code review & security |
| DevOps | Claude | Merging & deployment |

### Essential Commands

```bash
# Interactive Taskmaster (recommended)
python scripts/taskmaster_chat.py

# Watcher (required for task notifications)
python scripts/watcher.py

# Manual task management
python scripts/task_manager.py add --title "..." --assigned "Dev1"
python scripts/task_manager.py list
python scripts/task_manager.py update T-001 --status COMPLETED

# Container management
docker compose -f docker-compose.yml -f docker-compose.agents.yml up -d
docker logs -f agent_dev1
docker restart agent_dev1

# RAG
python scripts/embed_codebase.py
python scripts/rag_client.py "search query"

# Monitoring
docker ps
docker compose -f docker-compose.agents.yml logs -f
```

---

**Ready to build with AI! 🚀**

For questions or issues, see the full [README.md](README.md) or check [docs/](docs/).
