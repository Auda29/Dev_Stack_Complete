# Architecture Decision Records (ADR)

This document records all significant architectural decisions for the Dev_Stack project. All agents must read and follow these decisions.

---

## Decision Log

### ADR-001: Multi-Agent Development with Git Worktrees

**Date**: 2025-11-07  
**Status**: Accepted  
**Context**:

We need multiple AI agents to work on the same codebase simultaneously without conflicts or stepping on each other's changes.

**Decision**:

Use Git worktrees to give each agent their own working directory and branch:
- Each agent gets a dedicated worktree folder (`.worktrees/[agent-name]`)
- Each agent works on their own feature branch
- Only DevOps merges branches into `dev`

**Consequences**:

✅ Pros:
- Complete isolation between agents
- No file conflicts during development
- Clean Git history with feature branches
- Easy to review individual agent work

⚠️ Cons:
- Requires discipline in following the workflow
- DevOps must handle merge conflicts
- Slightly more complex setup

**Alternatives Considered**:
- Single shared branch: Too many conflicts
- Separate repositories: Hard to integrate
- File locking: Too restrictive

---

### ADR-002: Docker Container Isolation

**Date**: 2025-11-07  
**Status**: Accepted  
**Context**:

We need process isolation to ensure agents don't interfere with each other's runtime environment.

**Decision**:

Each agent runs in its own Docker container with:
- Shared `/repo` mount for Git repository access
- Individual container names (agent_dev1, agent_dev2, etc.)
- Identical base image for consistency
- No privileged access

**Consequences**:

✅ Pros:
- Complete process isolation
- Reproducible environments
- Easy to start/stop agents
- Works offline/locally

⚠️ Cons:
- Requires Docker installation
- Additional resource overhead
- Windows/Mac may have slower I/O

---

### ADR-003: Commit Message Convention

**Date**: 2025-11-07  
**Status**: Accepted  
**Context**:

We need consistent commit messages for easy navigation and automated tooling.

**Decision**:

Use conventional commit format:
```
<type>: <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code change without fixing bug or adding feature
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example**:
```
feat: add user registration endpoint

Implements POST /api/users with email validation
and password hashing using bcrypt.

Closes: T-023
```

**Consequences**:

✅ Pros:
- Easy to generate changelogs
- Clear intent of each commit
- Searchable history
- Automated versioning possible

---

### ADR-004: Error Handling Convention

**Date**: 2025-11-07  
**Status**: Accepted  
**Context**:

We need a consistent way to handle and report errors across all code.

**Decision**:

Use error envelope pattern for consistency:

```
{
  "success": boolean,
  "data": object | null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": object (optional)
  } | null,
  "timestamp": "ISO8601 datetime"
}
```

**Rules**:
1. Success path: `success: true`, `error: null`
2. Failure path: `success: false`, `data: null`
3. Always include timestamp
4. Error codes should be UPPER_SNAKE_CASE
5. Never expose internal stack traces to end users

**Consequences**:

✅ Pros:
- Consistent API responses
- Easy client-side error handling
- Structured error logging
- Security (no info leakage)

⚠️ Cons:
- Slightly more verbose
- Must be disciplined about following pattern

---

### ADR-005: DateTime Handling

**Date**: 2025-11-07  
**Status**: Accepted  
**Context**:

We need consistent datetime handling to avoid timezone bugs.

**Decision**:

- Store all datetimes in UTC
- Use ISO 8601 format for API responses: `YYYY-MM-DDTHH:mm:ss.sssZ`
- Convert to local timezone only in UI layer
- Use datetime libraries (not string manipulation)

**Example**:
```
2025-11-07T14:30:00.000Z
```

**Consequences**:

✅ Pros:
- No timezone conversion bugs
- International-ready
- Sortable as strings
- Standard format

---

### ADR-006: ID Format Convention

**Date**: 2025-11-07  
**Status**: Accepted  
**Context**:

We need consistent identifier formats across the system.

**Decision**:

**Task IDs**: `T-XXX` (e.g., T-001, T-142)
- Zero-padded to 3 digits minimum
- Prefix "T-" for tasks

**User/Entity IDs**: Generate based on your chosen stack
- UUID v4 for distributed systems
- Auto-increment for simple systems
- Prefix with entity type if using strings (e.g., `user_123`, `order_456`)

**Decision IDs**: `ADR-XXX` (e.g., ADR-001)
- Zero-padded to 3 digits
- Prefix "ADR-" for architecture decisions

**Consequences**:

✅ Pros:
- Easy to reference in discussions
- Sortable
- Type-safe (prefix indicates what it is)
- Collision-free

---

### ADR-007: Testing Strategy

**Date**: 2025-11-07  
**Status**: Accepted  
**Context**:

We need clear testing guidelines for consistent quality.

**Decision**:

Three-tier testing approach:

**1. Unit Tests** (80%+ coverage target):
- Test individual functions/methods
- Mock external dependencies
- Fast execution (<100ms per test)
- Naming: `test_[function]_[scenario]_[expected]`

**2. Integration Tests** (critical paths):
- Test component interactions
- Use test database/services
- Medium execution (100ms-1s per test)
- Focus on data flow and error handling

**3. End-to-End Tests** (minimal, critical flows):
- Test complete user workflows
- Use staging environment
- Slow execution (1s+ per test)
- Only for must-work scenarios

**Test file structure**:
```
src/
  module/
    file.ext
tests/
  module/
    test_file.ext          # Unit tests
    test_file_integration.ext  # Integration tests
    test_file_e2e.ext         # E2E tests
```

**Consequences**:

✅ Pros:
- Clear testing boundaries
- Fast feedback loop
- Comprehensive coverage
- Maintainable test suite

---

### ADR-008: Branch Strategy

**Date**: 2025-11-07  
**Status**: Accepted  
**Context**:

We need a branching strategy that supports parallel development and clean history.

**Decision**:

**Branch Types**:
- `main`: Production-ready code (protected)
- `dev`: Integration branch for development (protected)
- `feat/*`: Feature branches (agent work)
- `fix/*`: Bug fixes
- `test/*`: Testing work
- `chore/*`: DevOps/maintenance work
- `review/*`: Review working branch

**Workflow**:
1. Agents work on `feat/*`, `test/*`, etc.
2. DevOps merges approved work to `dev` with `--no-ff`
3. Releases are tagged and merged to `main`

**Branch Protection**:
- `main`: No direct commits, merge from `dev` only
- `dev`: No direct commits (except DevOps), require review

**Consequences**:

✅ Pros:
- Clear branch purpose
- Protected production code
- Clean history
- Easy to track features

---

### ADR-009: Documentation Requirements

**Date**: 2025-11-07  
**Status**: Accepted  
**Context**:

We need consistent documentation for maintainability.

**Decision**:

**Required Documentation**:

1. **Code Comments**:
   - Complex logic must have explaining comments
   - Public APIs must have documentation comments
   - Use doc-string format native to your language

2. **README Files**:
   - Root `README.md` with project overview
   - Module `README.md` for complex subsystems

3. **API Documentation**:
   - Endpoint path and method
   - Request/response format with examples
   - Error codes
   - Authentication requirements

4. **Architecture Docs**:
   - `/docs/agents.md` - Agent roles
   - `/docs/tasks.md` - Task tracking
   - `/docs/decisions.md` - This file (ADRs)

**Consequences**:

✅ Pros:
- Easy onboarding
- Reduced confusion
- Self-documenting decisions
- Knowledge preservation

---

### ADR-010: Security Best Practices

**Date**: 2025-11-07  
**Status**: Accepted  
**Context**:

We need baseline security practices to prevent common vulnerabilities.

**Decision**:

**Mandatory Security Rules**:

1. **Secrets Management**:
   - Never commit secrets to Git
   - Use environment variables
   - Use `.env` files (add to `.gitignore`)
   - Rotate secrets regularly

2. **Input Validation**:
   - Validate all user input
   - Sanitize before database queries
   - Use parameterized queries
   - Set max input lengths

3. **Authentication**:
   - Hash passwords (bcrypt, argon2)
   - Use secure session tokens
   - Implement rate limiting
   - Add brute-force protection

4. **Authorization**:
   - Check permissions on every request
   - Use principle of least privilege
   - Audit access logs

5. **Dependencies**:
   - Keep dependencies updated
   - Scan for vulnerabilities
   - Use lock files

**Consequences**:

✅ Pros:
- Prevents common attacks
- Protects user data
- Compliance-ready
- Builds security culture

---

## Decision Template

Use this template for new ADRs:

```markdown
### ADR-XXX: [Decision Title]

**Date**: YYYY-MM-DD  
**Status**: Proposed | Accepted | Superseded | Deprecated  
**Context**:

What is the issue we're seeing that is motivating this decision?

**Decision**:

What is the change that we're proposing and/or doing?

**Consequences**:

✅ Pros:
- Benefit 1
- Benefit 2

⚠️ Cons:
- Drawback 1
- Drawback 2

**Alternatives Considered**:
- Alternative 1: Why not chosen
- Alternative 2: Why not chosen
```

---

### ADR-011: Event-Driven Automation & JSON Source of Truth

**Date**: 2025-11-19  
**Status**: Accepted  
**Context**:
The manual workflow of polling `tasks.md` was inefficient and error-prone. Agents needed to check files manually, and markdown parsing was fragile.

**Decision**:
1. **Source of Truth**: Switch to `tasks.json` for all task data.
2. **View Layer**: `docs/tasks.md` is now auto-generated from JSON.
3. **Automation**: A watcher service monitors `tasks.json` and triggers agent containers via Docker API when assignments change.
4. **Context Awareness**: Integration of ChromaDB (RAG) for semantic code search.
5. **Quality Gates**: Mandatory Git pre-commit hooks.

**Consequences**:

✅ Pros:
- Immediate agent reaction time (no polling)
- Type-safe task management (no markdown parsing errors)
- Better context for agents (RAG)
- Higher code quality (hooks)

⚠️ Cons:
- Requires Python/Docker setup for the watcher
- Agents must handle JSON structure


---

## Superseded Decisions

### ADR-000: Example Superseded Decision

**Date**: 2025-01-01  
**Status**: Superseded by ADR-XXX  
**Reason**: Better approach found

[Original content preserved for reference]

---

**Last Updated**: 2025-11-07  
**Maintained By**: All Agents (propose), Taskmaster (approve)
