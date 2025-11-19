# Automation Scripts

This directory contains scripts for automating the agent workflow.

## watcher.py

This script monitors `docs/tasks.md` for changes and automatically triggers the assigned agent containers when a task status changes or a new task is assigned.

### Usage

```bash
python scripts/watcher.py
```

### How it works

1. Parses `docs/tasks.md` looking for task blocks.
2. Detects changes in **Status** or **Assigned** fields.
3. If a task is assigned to a known agent (e.g., Dev1, Dev2), it executes a `docker exec` command to notify the agent.
4. Currently, it writes a notification to `/tmp/agent_notifications` inside the container.

### Requirements

- Python 3.6+
- Docker (must be running and accessible)

