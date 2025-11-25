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

## 🚀 5-Minute Setup

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
# Create Git worktrees for each agent
bash scripts/setup_worktrees.sh
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

### Create a Task

```bash
python scripts/task_manager.py add \
  --title "Create a greeting function" \
  --assigned "Dev1" \
  --description "Create a Python function that takes a name and returns a personalized greeting"
```

### Watch the Magic ✨

```bash
# Watch Dev1 agent work
docker logs -f agent_dev1
```

**You'll see:**
```
🔍 Searching codebase for relevant context...
   Found 3 relevant code snippets
🤖 Querying LLM for implementation...
✅ LLM Response received (847 tokens)
📝 Parsing and applying code changes...
✅ Successfully applied 1 file changes
   - utils/greetings.py
```

### Check the Result

```bash
cat utils/greetings.py
```

**The AI wrote this:**
```python
def greet(name):
    """Return a personalized greeting."""
    return f"Hello, {name}!"
```

🎉 **Congratulations!** Your AI agent just wrote its first code!

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
1. Merges to dev branch
2. Updates status to `COMPLETED`

### 3. Monitor Progress

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
# Task management
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
