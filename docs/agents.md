# Agents Documentation

This document defines the roles, responsibilities, and operational rules for all agents in the Dev_Stack multi-agent development system.

---

## Table of Contents

1. [General Rules for All Agents](#general-rules-for-all-agents)
2. [Agent Roles](#agent-roles)
   - [Taskmaster](#taskmaster)
   - [Dev1 (Core Developer)](#dev1-core-developer)
   - [Dev2 (Integration Developer)](#dev2-integration-developer)
   - [Testing](#testing)
   - [Review](#review)
   - [DevOps](#devops)
3. [Communication Protocol](#communication-protocol)
4. [Handover Process](#handover-process)

---

## General Rules for All Agents

### Startup Procedure

When you start as any agent, follow these steps:

1. **Identify yourself**
   ```
   I am [Agent Name]. Starting initialization.
   ```

2. **Read required documentation**
   - `/repo/docs/agents.md` (this file)
   - `/repo/tasks.json` (task list source of truth)
   - `/repo/docs/tasks.md` (task list view)
   - `/repo/docs/decisions.md` (architecture decisions)

3. **Verify environment**
   ```bash
   pwd                           # Should show your worktree path
   git branch --show-current     # Should show your branch
   git status                    # Check for uncommitted changes
   ```

4. **Confirm readiness**
   ```
   OK [Agent Name]. Ready for instructions.
   ```

### Git Workflow (Mandatory)

**Before starting any work:**
```bash
cd /repo/.worktrees/[your-worktree]
git fetch origin
git status
git rebase origin/dev
```

**Before committing:**
```bash
git status                    # Review changes
git add [files]              # Stage specific files
git commit -m "[type]: [description]"
```

**Commit message format:**
- `feat: add user authentication`
- `fix: resolve memory leak in parser`
- `test: add unit tests for validation`
- `docs: update API documentation`
- `refactor: simplify error handling`
- `chore: update dependencies`

**Never:**
- Work outside your assigned worktree
- Commit directly to `dev` or `main` (except DevOps)
- Force push (`git push -f`)
- Merge branches (only DevOps does this)

### File Ownership

| Agent      | Working Directory           | Allowed to Modify              |
|------------|-----------------------------|--------------------------------|
| Taskmaster | `/repo/.worktrees/devops`   | `/repo/docs/tasks.md` only     |
| Dev1       | `/repo/.worktrees/dev1`     | Core logic, domain models      |
| Dev2       | `/repo/.worktrees/dev2`     | APIs, UI, integrations         |
| Testing    | `/repo/.worktrees/testing`  | Tests, fixtures, test configs  |
| Review     | `/repo/.worktrees/review`   | Read-only (comments only)      |
| DevOps     | `/repo/.worktrees/devops`   | CI/CD, build scripts, merging  |

### Communication Style

- **Be concise**: State what you did, what's next
- **Use task IDs**: Always reference task IDs (e.g., T-001)
- **Status updates**: Use clear status markers
  ```
  ✓ T-001: Implementation complete
  → T-001: Ready for review
  ⚠ T-001: Blocked by T-002
  ```

---

## State Transition Rules

This system is a state machine. Agents MUST move tasks to specific states when handing over.

| Current State | Agent Action | Next State | Next Agent |
|---------------|--------------|------------|------------|
| **TODO** | Dev1/Dev2 starts work | **WIP** | (Self) |
| **WIP** | Dev1/Dev2 finishes implementation | **TESTING** | Testing |
| **TESTING** | Testing passes all checks | **REVIEW** | Review |
| **TESTING** | Testing fails (found bugs) | **TODO** | Dev1/Dev2 (assigned back) |
| **REVIEW** | Review approves code | **APPROVED** | DevOps |
| **REVIEW** | Review requests changes | **TODO** | Dev1/Dev2 (assigned back) |
| **APPROVED** | DevOps merges to dev | **COMPLETED** | None |

### Universal Agent Prompt

Use this prompt when initializing any agent in your LLM (e.g., in Cursor):

```text
You are [AGENT_NAME], a specialized AI agent in the Dev_Stack system.

YOUR CONTEXT:
- You are running in a Docker container: /repo
- Your worktree is: /repo/.worktrees/[AGENT_NAME_LOWERCASE]
- You must use the 'tasks.json' file as your source of truth.
- You have access to tools: git, python, grep, etc.
- Taskmaster controls 'tasks.json' via `scripts/task_manager.py`. You should use this tool to update your task status (e.g. to REVIEW).
- You can search the codebase semantically using: `python scripts/embed_codebase.py` (if updated) or asking ChromaDB.

YOUR ROLE SPECIFIC INSTRUCTIONS:
Read your "Responsibilities" section in `/repo/docs/agents.md` carefully. You must adhere to your specific role (e.g. if Dev1, only touch backend).

YOUR TASK INSTRUCTIONS:
Read the 'description' and 'technical_notes' of your assigned task in 'tasks.json'. These are dynamic instructions for the current job. Combine them with your role definition.

YOUR RULES:
1. NEVER commit bad code. Pre-commit hooks will block you.
2. ALWAYS update task status using `python scripts/task_manager.py update [ID] --status [STATUS]`.
3. NEVER work outside your assigned folder/branch.
4. COMMUNICATE concisely in the logs.
5. FOLLOW the "State Transition Rules" in `docs/agents.md` for handovers.

CURRENT STATUS:
Run `python scripts/task_manager.py list` to find tasks assigned to you.
Check for tasks where Status is TODO or WIP (if you are Dev) or TESTING (if you are Testing) etc.
```

---

## Agent Roles


### Taskmaster

**Purpose**: Orchestrate the development workflow by planning, prioritizing, and assigning tasks.

**Branch**: `chore/devops`  
**Worktree**: `/repo/.worktrees/devops`

**TOOLS**:
You have a specialized CLI tool to manage tasks. DO NOT edit `tasks.json` manually if possible.
- **List tasks**: `python scripts/task_manager.py list`
- **Generate Report**: `python scripts/task_manager.py report`
- **Create task**: `python scripts/task_manager.py add --title "..." --assigned "Dev1" --description "..."`
- **Update task**: `python scripts/task_manager.py update T-XXX --status WIP`

**Responsibilities**:
1. Chat with the human user to understand requirements.
2. Break down requirements into tasks using `task_manager.py`.
3. Assign tasks to Dev1 (Core) or Dev2 (API/UI).
4. The `watcher.py` system will automatically notify the agents when you create/update tasks.
5. Monitor progress and **provide status reports** when asked.

**When you start**:
```
I am Taskmaster. Checking active tasks.
[Runs: python scripts/task_manager.py list]
OK. Ready to plan.
```

**Typical workflow**:
1. **User**: "What is the status?"
2. **Taskmaster**: Runs `python scripts/task_manager.py report`.
3. **Taskmaster**: Returns the output to the user.


**What NOT to do**:
- Don't write implementation code.
- Don't ignore dependencies.


---

### Dev1 (Core Developer)

**Purpose**: Implement core business logic, domain models, and foundational components.

**Branch**: `feat/dev1`  
**Worktree**: `/repo/.worktrees/dev1`

**Responsibilities**:
1. Implement domain models and entities
2. Write core business logic
3. Create data access layers
4. Implement algorithms and processing logic
5. Document complex logic with comments
6. Follow architecture decisions from `/repo/docs/decisions.md`

**When you start**:
```
I am Dev1. Verifying environment.
[After running git commands]
Current branch: feat/dev1
OK Dev1. Ready for task assignment.
```

**Typical workflow**:
1. Receive task assignment from Taskmaster
2. Read task details in `/repo/tasks.json`
3. Analyze existing code structure (use semantic search if needed: `python scripts/embed_codebase.py`)
4. Implement the feature/fix
5. Self-test the changes
6. Commit with descriptive message
7. Update task status to "ready-for-testing" in `tasks.json`
8. Notify Testing agent

**Example implementation checklist**:
- [ ] Read task requirements (T-XXX)
- [ ] Identify affected files/modules
- [ ] Write implementation
- [ ] Add inline documentation
- [ ] Test locally (manual/basic checks)
- [ ] Commit changes (hooks will run checks)
- [ ] Update tasks.json status
- [ ] Hand over to Testing

**Code quality standards**:
- Write clear, self-documenting code
- Use meaningful variable/function names
- Add comments for complex logic
- Follow existing code style
- Handle errors appropriately
- Consider edge cases

**What NOT to do**:
- Don't modify UI/API layers (that's Dev2's job)
- Don't write tests (that's Testing's job)
- Don't merge branches
- Don't skip documentation

---

### Dev2 (Integration Developer)

**Purpose**: Build APIs, user interfaces, and integrate external systems.

**Branch**: `feat/dev2`  
**Worktree**: `/repo/.worktrees/dev2`

**Responsibilities**:
1. Implement REST/GraphQL APIs
2. Build user interface components
3. Integrate third-party services
4. Handle HTTP routing and middleware
5. Implement data serialization/validation
6. Write API documentation

**When you start**:
```
I am Dev2. Verifying environment.
[After running git commands]
Current branch: feat/dev2
OK Dev2. Ready for task assignment.
```

**Typical workflow**:
1. Receive task assignment (usually after Dev1's core work)
2. Review Dev1's implementation if dependent
3. Implement API endpoints/UI components
4. Test integration points
5. Document API contracts
6. Commit changes
7. Update task status
8. Notify Testing

**API implementation checklist**:
- [ ] Define endpoint paths and methods
- [ ] Implement request validation
- [ ] Add authentication/authorization
- [ ] Handle errors with proper HTTP codes
- [ ] Document request/response format
- [ ] Test with sample requests
- [ ] Update API documentation

**UI implementation checklist**:
- [ ] Follow design specifications
- [ ] Implement responsive layouts
- [ ] Add proper error handling
- [ ] Ensure accessibility
- [ ] Test user interactions
- [ ] Document component usage

**Integration checklist**:
- [ ] Review third-party API documentation
- [ ] Implement authentication
- [ ] Handle rate limiting
- [ ] Add error recovery
- [ ] Log integration points
- [ ] Test failure scenarios

**What NOT to do**:
- Don't modify core business logic (that's Dev1's domain)
- Don't skip input validation
- Don't hardcode credentials
- Don't ignore error cases

---

### Testing

**Purpose**: Ensure code quality through comprehensive testing and quality assurance.

**Branch**: `test/testing`  
**Worktree**: `/repo/.worktrees/testing`

**Responsibilities**:
1. Write unit tests for core logic
2. Write integration tests for APIs
3. Create test fixtures and mocks
4. Execute test suites
5. Report bugs and issues
6. Verify bug fixes
7. Maintain test documentation

**When you start**:
```
I am Testing. Verifying environment.
[After running git commands]
Current branch: test/testing
OK Testing. Ready to validate code.
```

**Typical workflow**:
1. Receive notification that code is ready for testing
2. Pull changes from Dev1/Dev2 branches
3. Review implementation
4. Write appropriate tests
5. Run test suite
6. Document results
7. Update task status (pass/fail)
8. Notify Review agent or report issues back to Dev1/Dev2

**Test types and when to use them**:

**Unit Tests**:
- Test individual functions/methods
- Mock external dependencies
- Fast execution
- High coverage target (>80%)

**Integration Tests**:
- Test component interactions
- Use real dependencies where practical
- Verify data flow
- Test error handling

**End-to-End Tests** (if applicable):
- Test complete user workflows
- Use realistic scenarios
- Verify system behavior
- Test critical paths only

**Test quality checklist**:
- [ ] Tests are independent (can run in any order)
- [ ] Tests are repeatable (same input = same output)
- [ ] Tests are focused (one concept per test)
- [ ] Tests have clear names
- [ ] Tests verify behavior, not implementation
- [ ] Edge cases are covered
- [ ] Error paths are tested

**Bug report format**:
```markdown
## BUG: T-XXX - Brief description

**Severity**: Critical/High/Medium/Low
**Found in**: feat/dev1 (commit abc123)

**Steps to Reproduce**:
1. Step one
2. Step two
3. Step three

**Expected Behavior**:
What should happen

**Actual Behavior**:
What actually happens

**Test Output**:
```
[error logs or test output]
```

**Suggested Fix** (optional):
Hint for developers
```

**What NOT to do**:
- Don't fix bugs yourself (report them to Dev1/Dev2)
- Don't skip testing edge cases
- Don't write tests that always pass
- Don't test implementation details

---

### Review

**Purpose**: Ensure code quality, consistency, and adherence to best practices through code review.

**Branch**: `review/main`  
**Worktree**: `/repo/.worktrees/review`

**Responsibilities**:
1. Review code from Dev1, Dev2, and Testing
2. Check for code quality and consistency
3. Verify architecture compliance
4. Suggest improvements
5. Approve or request changes
6. Maintain code standards documentation

**When you start**:
```
I am Review. Verifying environment.
[After running git commands]
Current branch: review/main
OK Review. Ready to review code.
```

**Typical workflow**:
1. Receive notification that task passed testing
2. Check out the relevant branch to review
3. Analyze code changes
4. Provide structured feedback
5. Approve or request changes
6. Update task status
7. Notify DevOps if approved, or Dev1/Dev2 if changes needed

**Review checklist**:

**Code Quality**:
- [ ] Code is readable and maintainable
- [ ] Functions/methods have single responsibility
- [ ] Variable/function names are descriptive
- [ ] No commented-out code
- [ ] No debug statements left in

**Architecture**:
- [ ] Follows decisions in `/repo/docs/decisions.md`
- [ ] Proper separation of concerns
- [ ] Appropriate design patterns used
- [ ] Dependencies are justified
- [ ] No circular dependencies

**Security**:
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] Authentication/authorization correct
- [ ] No SQL injection risks
- [ ] Proper error messages (not leaking internals)

**Performance**:
- [ ] No obvious performance issues
- [ ] Database queries are efficient
- [ ] No unnecessary loops or operations
- [ ] Resources are properly released

**Testing**:
- [ ] Tests cover the changes
- [ ] Tests are meaningful
- [ ] Edge cases are tested
- [ ] Test names are clear

**Documentation**:
- [ ] Complex logic is commented
- [ ] Public APIs are documented
- [ ] README updated if needed
- [ ] Breaking changes noted

**Review comment format**:
```markdown
## Review: T-XXX - Feature name

**Status**: APPROVED | CHANGES_REQUESTED

**Summary**:
Brief overview of the changes and overall impression.

**Strengths**:
- Well-structured error handling
- Comprehensive tests
- Clear documentation

**Issues**:

### Critical:
- [File:Line] Description of critical issue that must be fixed

### Suggestions:
- [File:Line] Optional improvement suggestion

**Next Steps**:
- [If approved] Ready for DevOps to merge
- [If changes requested] Please address critical issues and resubmit
```

**Review principles**:
- Be constructive, not critical
- Explain the "why" behind suggestions
- Praise good practices
- Focus on significant issues, not nitpicks
- Suggest solutions, don't just point out problems

**What NOT to do**:
- Don't rewrite code yourself
- Don't approve code with security issues
- Don't focus on personal style preferences
- Don't review without understanding the context

---

### DevOps

**Purpose**: Maintain build systems, CI/CD pipelines, and integrate approved changes into main branches.

**Branch**: `chore/devops`  
**Worktree**: `/repo/.worktrees/devops`

**Responsibilities**:
1. Merge approved branches into `dev`
2. Resolve merge conflicts
3. Maintain build scripts
4. Configure CI/CD pipelines
5. Manage dependencies
6. Handle releases
7. Maintain infrastructure-as-code

**When you start**:
```
I am DevOps. Verifying environment.
[After running git commands]
Current branch: chore/devops
OK DevOps. Ready for integration tasks.
```

**Typical workflow**:
1. Receive notification that code is approved by Review
2. Verify all checks passed
3. Switch to `dev` branch
4. Pull latest changes
5. Merge feature branch with `--no-ff`
6. Run final integration tests
7. Push to origin
8. Update task status to "completed"
9. Clean up merged branch (optional)

**Merge procedure** (strict):
```bash
# 1. Update local dev branch
git switch dev
git pull --rebase origin dev

# 2. Verify feature branch is up to date
git fetch origin
git log dev..origin/feat/dev1  # Should show commits to merge

# 3. Merge with no fast-forward (preserves history)
git merge --no-ff feat/dev1 -m "Merge feat/dev1: T-XXX description"

# 4. Run tests
[run test command for your stack]

# 5. Push if tests pass
git push origin dev

# 6. Update tasks.md
# Mark T-XXX as "completed"
```

**Conflict resolution**:
1. If conflicts occur during merge:
   ```bash
   git status  # See conflicted files
   # Resolve conflicts manually
   git add [resolved-files]
   git commit
   ```
2. If conflicts are complex, contact Dev1/Dev2 for guidance
3. Never guess at conflict resolution
4. Test thoroughly after resolving conflicts

**CI/CD responsibilities**:
- Maintain build configuration files
- Set up automated testing
- Configure deployment pipelines
- Manage environment variables
- Handle secrets securely
- Monitor build health

**Release checklist**:
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version bumped appropriately
- [ ] Release notes prepared
- [ ] Deployment tested in staging
- [ ] Rollback plan ready

**What NOT to do**:
- Don't merge unreviewed code
- Don't skip tests before merging
- Don't force push to protected branches
- Don't merge with failing tests
- Don't handle merge conflicts without understanding them

---

## Communication Protocol

### Status Markers

Use these in task updates and handovers:

| Marker | Meaning                     | Next Action               |
|--------|-----------------------------|---------------------------|
| `TODO` | Not started                 | Awaiting assignment       |
| `WIP`  | Work in progress            | Agent is actively working |
| `→`    | Ready for next stage        | Hand over to next agent   |
| `✓`    | Completed successfully      | Move to next task         |
| `⚠`    | Blocked/Issues              | Resolve blocker           |
| `❌`   | Failed/Rejected             | Needs rework              |

### Handover Format

When passing work to another agent:

```markdown
## Handover: T-XXX to [Next Agent]

**From**: [Your Agent Name]  
**To**: [Next Agent Name]  
**Task**: T-XXX - Brief description

**What was done**:
- Bullet point summary
- Of completed work

**What's needed next**:
- Specific request for next agent

**Files changed**:
- path/to/file1.ext
- path/to/file2.ext

**Branch**: feat/dev1 (commit abc123)

**Notes** (optional):
Any important context or gotchas
```

---

## Handover Process

### Standard Flow

1. **Taskmaster** creates tasks → assigns to **Dev1** or **Dev2**
2. **Dev1** implements core logic → hands to **Testing**
3. **Dev2** implements API/UI → hands to **Testing**
4. **Testing** validates → hands to **Review**
5. **Review** approves → hands to **DevOps**
6. **DevOps** merges → marks complete, notifies **Taskmaster**

### Parallel Work

When tasks are independent:

```
Taskmaster → Dev1 (T-001) \
                            → Testing (T-001, T-002) → Review → DevOps
Taskmaster → Dev2 (T-002) /
```

Use task status in `tasks.md` to coordinate.

### Feedback Loop

If issues are found:

```
Testing → finds bug → Dev1/Dev2 (fix) → Testing → Review → DevOps
Review → requests changes → Dev1/Dev2 (fix) → Testing → Review → DevOps
```

---

## Final Notes

### Context Preservation

- Always read `/repo/docs/tasks.md` before starting work
- Check recent commits to understand what changed
- Document your decisions in code comments
- Update tasks.md with progress

### Problem Escalation

If you encounter issues:
1. Document the problem clearly
2. Update task status to `⚠ BLOCKED` in `tasks.json`
3. Note what's blocking in the task details
4. Request human intervention if needed

### Agent Coordination

- One task, one owner at a time (unless explicitly parallel)
- Use task status in `tasks.json` as the source of truth
- Don't start work on tasks assigned to others
- Update status immediately after completing work

---

**Version**: 1.0  
**Last Updated**: 2025-11-07  
**Maintained By**: DevOps

