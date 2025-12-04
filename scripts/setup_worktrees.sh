#!/bin/bash
# Setup Git Worktrees for Dev_Stack Agents
# This script creates worktrees for each agent in their respective directories

set -e

echo "================================================"
echo "Dev_Stack Worktree Setup"
echo "================================================"

# Check if we're in a Git repository
if [ ! -d ".git" ]; then
    echo "ERROR: Not in a Git repository root!"
    echo "Please run this script from the repository root."
    exit 1
fi

# Configuration
WORKTREE_BASE=".worktrees"
AGENTS=(
    "devops:chore/devops"
    "dev1:feat/dev1"
    "dev2:feat/dev2"
    "testing:test/testing"
    "review:review/main"
)

# Create worktree base directory if it doesn't exist
if [ ! -d "$WORKTREE_BASE" ]; then
    echo "Creating worktree base directory: $WORKTREE_BASE"
    mkdir -p "$WORKTREE_BASE"
fi

# Ensure we're on a valid branch
CURRENT_BRANCH=$(git branch --show-current)
if [ -z "$CURRENT_BRANCH" ]; then
    echo "Creating initial commit on main branch..."
    git checkout -b main 2>/dev/null || git checkout main
    if [ ! -f "README.md" ]; then
        echo "# Dev_Stack Project" > README.md
        git add README.md
        git commit -m "chore: initial commit"
    fi
fi

# Create dev branch if it doesn't exist
if ! git show-ref --verify --quiet refs/heads/dev; then
    echo "Creating 'dev' branch..."
    git branch dev
fi

echo ""
echo "Creating worktrees for agents..."
echo ""

# Create each agent's worktree
for AGENT_CONFIG in "${AGENTS[@]}"; do
    IFS=':' read -r AGENT_DIR BRANCH <<< "$AGENT_CONFIG"
    WORKTREE_PATH="$WORKTREE_BASE/$AGENT_DIR"
    
    echo "----------------------------------------"
    echo "Agent: $AGENT_DIR"
    echo "Branch: $BRANCH"
    echo "Path: $WORKTREE_PATH"
    
    # Check if worktree directory already exists
    if [ -d "$WORKTREE_PATH" ]; then
        # Check if it's a valid worktree (must contain .git file)
        if [ -f "$WORKTREE_PATH/.git" ]; then
            echo "✓ Worktree already exists and is valid, skipping..."
            continue
        else
            echo "⚠ Directory exists but is NOT a valid worktree!"
            echo "  Backing up to ${WORKTREE_PATH}_backup..."
            mv "$WORKTREE_PATH" "${WORKTREE_PATH}_backup"
            echo "  Recreating worktree..."
        fi
    fi
    
    # Check if branch exists
    if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
        echo "✓ Branch exists: $BRANCH"
    else
        echo "Creating branch: $BRANCH"
        git branch "$BRANCH" dev
    fi
    
    # Create worktree
    echo "Creating worktree..."
    git worktree add "$WORKTREE_PATH" "$BRANCH"
    
    echo "✓ Worktree created successfully"
done

echo ""
echo "================================================"
echo "Worktree Setup Complete!"
echo "================================================"
echo ""
echo "Worktrees created:"
git worktree list
echo ""
echo "You can now start the agent containers:"
echo "  docker compose -f docker-compose.yml -f docker-compose.agents.yml up -d"
echo ""
echo "To remove worktrees in the future:"
echo "  git worktree remove <path>"
echo "  or"
echo "  git worktree prune"
echo "================================================"
