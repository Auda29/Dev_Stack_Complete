# Architecture Decisions & Trade-offs

## 1. Scalability & Performance

### Current Limitations
The current system uses `tasks.json` as a single source of truth. This is simple but has limitations:
- **File Locking**: Concurrent writes are handled by atomic file replacement, but high load could cause retries.
- **Polling**: The Watcher polls the file every 2 seconds. With 50+ agents, this might need optimization.

### Scalability Strategy
For larger deployments (50+ agents):
1.  **Database Migration**: Replace `tasks.json` with a proper database (PostgreSQL/Redis).
2.  **Event Bus**: Replace polling with an event bus (RabbitMQ/Kafka) for real-time task distribution.
3.  **Sharding**: Split agents into different clusters/networks to reduce Docker bridge overhead.

## 2. Conflict Resolution

### Git Workflow
Agents work on isolated worktrees and branches (`feat/dev1`, `feat/dev2`).
- **Merge Strategy**: The DevOps agent uses `git merge --no-ff` to preserve history.
- **Conflict Handling**:
    1.  If a merge conflict occurs, the DevOps agent aborts the merge.
    2.  The task status is set to `BLOCKED`.
    3.  A new task is created for a human or a senior agent to resolve the conflict manually.

### Deadlock Prevention
- **Timeouts**: Agents have a maximum execution time per task.
- **Dependency Graph**: The Taskmaster ensures tasks are assigned in dependency order (DAG) to prevent circular waits.

## 3. Security

### Container Security
- **Non-Root User**: Agents run as `devstack` user to prevent privilege escalation.
- **Network Isolation**: Agents are on a private Docker bridge network.

### Secrets Management
- **Environment Variables**: API keys and secrets are injected via `.env` file.
- **No Hardcoding**: Secrets are never committed to the repo.

## 4. Observability

### Monitoring
- **Dashboard**: A static HTML dashboard (`dashboard.html`) provides a snapshot of system state.
- **Logs**: All agent logs are captured by Docker and can be shipped to ELK/Prometheus in production.
