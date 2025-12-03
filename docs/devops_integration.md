# DevOps Feature Branch Integration

## How It Works

1. **DevOps Agent** reviews approved code in worktrees
2. **Creates integration script** (e.g., `integrate_T-002.sh`)
3. **Git integration script** copies files and creates feature branch
4. **Pushes to origin** for review
5. **Automatically fetches** so your local repo knows about the new branch

## Manual Integration

If you want to manually integrate a task:

```bash
# From the main repo directory
python scripts/devops_git_integration.py T-002 .worktrees/dev1
```

This will:
- Create branch `feature/t-002-<task-title>`
- Copy files from worktree to main repo
- Commit changes
- Push to origin

## Viewing Generated Code

Generated code is in worktrees:

```bash
# Dev1's code
ls .worktrees/dev1/src/

# Dev2's code  
ls .worktrees/dev2/src/

# Tests
ls .worktrees/testing/tests/

# All Python files created
Get-ChildItem -Path .worktrees -Recurse -Filter "*.py"
```

## Automatic Branch Syncing

The integration script automatically runs `git fetch` after pushing, so your local repository immediately knows about new feature branches.

**To manually fetch at any time**:
```bash
git fetch origin
```

**To automatically sync in the background** (optional):
```bash
# Fetch every 60 seconds
python scripts/branch_sync.py

# Or fetch once
python scripts/branch_sync.py --once
```

**Checking out a feature branch**:
```bash
# List available feature branches
git branch -r --list "origin/feature/*"

# Check out a specific branch
git checkout feature/t-002-personalized-greeting

# Or create local tracking branch
git checkout -b feature/t-002-personalized-greeting origin/feature/t-002-personalized-greeting
```

## Feature Branch Workflow

1. **Agent completes task** → Status: APPROVED
2. **DevOps creates feature branch** → `feature/t-xxx-description`  
3. **You review the branch**
4. **Merge when ready** → `git merge feature/t-xxx-description`

## Troubleshooting

### "No changes to commit"

The agent may have already created the file in a previous run. Check:
```bash
git log --all --grep="T-002"
```

### "Push failed"

Check your Git remote configuration:
```bash
git remote -v
```

Add origin if missing:
```bash
git remote add origin <your-repo-url>
```
