#!/bin/bash
# Dev_Stack Container Entrypoint Script
# Runs when container starts to initialize the environment

set -e

echo "================================================"
echo "Dev_Stack Agent Container Starting"
echo "Agent: ${AGENT_NAME:-Unknown}"
echo "Role: ${AGENT_ROLE:-Unknown}"
echo "================================================"

# Verify Git is available
if ! command -v git &> /dev/null; then
    echo "ERROR: Git is not installed!"
    exit 1
fi

# Display Git version
echo "Git version: $(git --version)"

# Verify we're in a Git repository
if [ -d "/repo/.git" ]; then
    echo "✓ Git repository detected at /repo"
else
    echo "⚠ Warning: /repo does not appear to be a Git repository"
    echo "  This is expected on first setup. Initialize with:"
    echo "  cd /repo && git init"
fi

# Display current branch if we're in a worktree
if [ -f ".git" ]; then
    echo "✓ Worktree detected"
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "none")
    echo "  Current branch: ${CURRENT_BRANCH}"
fi

# Display working directory
echo "Working directory: $(pwd)"

# Agent-specific initialization
case "${AGENT_NAME}" in
    "Taskmaster")
        echo "Taskmaster agent ready for orchestration tasks"
        ;;
    "Dev1")
        echo "Dev1 agent ready for core development"
        ;;
    "Dev2")
        echo "Dev2 agent ready for integration development"
        ;;
    "Testing")
        echo "Testing agent ready for QA tasks"
        ;;
    "Review")
        echo "Review agent ready for code review"
        ;;
    "DevOps")
        echo "DevOps agent ready for integration and deployment"
        ;;
    *)
        echo "Unknown agent type"
        ;;
esac

echo "================================================"
echo "Initialization complete. Ready for commands."
echo "================================================"

# Start the agent listener in the background
echo "Starting Agent Listener..."
python3 /usr/local/bin/agent_listener.py &

# Execute the main command
exec "$@"
