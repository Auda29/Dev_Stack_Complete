# LLM Integration Guide

This document explains how LLM integration works in Dev_Stack and how to use it effectively.

## Overview

Dev_Stack agents are fully integrated with LLM providers (OpenAI, Anthropic, Google Gemini). Each agent:

- Queries the codebase semantically using RAG (ChromaDB)
- Maintains conversation history across task execution
- Generates context-aware code based on existing patterns
- Validates and formats code automatically
- Tracks token usage and costs

## Quick Start

### 1. Configure API Keys

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Index Your Codebase

```bash
docker compose up -d chroma
python scripts/embed_codebase.py
```

### 4. Start Agents

```bash
docker compose -f docker-compose.agents.yml up -d
```

## RAG Integration

### How It Works

RAG (Retrieval-Augmented Generation) provides agents with codebase context:

1. Your code is chunked and embedded into ChromaDB
2. Agents search for similar code using semantic similarity
3. Relevant snippets are injected into the LLM prompt

### Indexing Your Code

```bash
python scripts/embed_codebase.py
```

Re-run this when you make significant code changes.

### Testing RAG

Query from command line:
```bash
python scripts/rag_client.py "authentication logic"
```

## Agent Prompts

Each agent has a role-specific system prompt defined in `agent_listener.py`:

- **Taskmaster**: Task decomposition and planning
- **Dev1**: Core business logic development
- **Dev2**: API/UI integration development
- **Testing**: Test generation and execution
- **Review**: Code quality and security review
- **DevOps**: Merging and deployment

## Token Usage and Costs

### Tracking

Agents automatically track token usage:
- Per-request tokens logged in agent output
- Total tokens tracked in `llm_client.total_tokens_used`
- Conversation history saved in `work_artifacts/contexts/`

### Estimated Costs

Based on typical task complexity:

| Provider | Model | Typical Task Cost |
|----------|-------|-------------------|
| OpenAI | GPT-4o | $0.01 - $0.10 |
| Anthropic | Claude 3.5 Sonnet | $0.015 - $0.15 |
| Google | Gemini 1.5 Pro | $0.007 - $0.07 |

### Cost Optimization

1. **Lower temperature** for code generation (0.3 vs 0.7)
2. **Limit RAG chunks** (5-10 instead of 15+)
3. **Use smaller models** for simple tasks
4. **Enable context trimming** (automatic)

## Configuration

### Per-Agent Settings

Edit `config/agent_config.yml`:

```yaml
dev1:
  max_tokens: 8000
  temperature: 0.3
  rag_chunks: 15
```

### Global Settings

Environment variables in `.env`:
- `LLM_PROVIDER`: openai, anthropic, or google
- `OPENAI_MODEL`: gpt-4o, gpt-4o-mini, etc.
- `ANTHROPIC_MODEL`: claude-3-5-sonnet-20241022, etc.
- `GOOGLE_MODEL`: gemini-1.5-pro, etc.

## Code Generation Format

Agents use this format for file changes:

```markdown
### File: path/to/file.py
\```python
def hello():
    print("Hello, World!")
\```
```

The Code Editor automatically:
- Validates Python syntax
- Creates backups in `.code_backups/`
- Auto-formats with Black (if installed)
- Handles file creation and updates

## Troubleshooting

### Agent Not Responding

1. Check logs: `docker logs -f agent_dev1`
2. Verify API key in `.env`
3. Check network: `docker compose ps`

### RAG Not Finding Code

1. Re-index: `python scripts/embed_codebase.py`
2. Check ChromaDB: `docker logs chroma`
3. Verify collection: `python scripts/rag_client.py "test query"`

### Token Limit Errors

1. Reduce `max_tokens` in agent config
2. Limit `rag_chunks` to 3-5
3. Clear old conversation: Delete files in `work_artifacts/contexts/`

### Invalid Code Generated

1. Check task description clarity
2. Ensure codebase is indexed
3. Review system prompts in `agent_listener.py`
4. Lower temperature to 0.1-0.3 for code tasks

## Advanced Usage

### Custom Prompts

Modify `load_agent_prompt()` in `agent_listener.py`:

```python
def load_agent_prompt():
    return """Your custom system prompt here..."""
```

### Adding New LLM Providers

1. Create new class in `llm_client.py` extending `LLMClient`
2. Implement `generate_text()` and `generate_with_messages()`
3. Add to `get_llm_client()` factory function

### Programmatic Access

```python
from llm_client import get_llm_client
from rag_client import RAGClient

# Initialize
llm = get_llm_client()
rag = RAGClient()

# Query with context
results = rag.query("authentication code", n_results=5)
context = rag.format_for_llm(results)

# Generate
response = llm.generate_text(
    prompt=f"{context}\\n\\nImplement login function",
    temperature=0.3
)
```

## Best Practices

1. **Write clear task descriptions** with specific requirements
2. **Use technical_notes** field for implementation hints
3. **Re-index regularly** as codebase grows
4. **Monitor token usage** to control costs
5. **Review generated code** before committing
6. **Keep system prompts focused** on agent role

## Future Enhancements

Potential improvements (not yet implemented):

- Streaming LLM responses
- Multi-agent collaboration on single task
- Learning from past tasks
- Automatic test execution
- Code diff suggestions instead of full rewrites
- Budget limits and alerts
