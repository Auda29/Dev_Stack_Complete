#!/bin/bash
# Install Git Hooks

HOOKS_DIR=".git/hooks"
SOURCE_DIR="scripts/git_hooks"

echo "Installing Git Hooks..."

if [ ! -d ".git" ]; then
    echo "Error: Not in a git repository root."
    exit 1
fi

# Ensure hooks directory exists
mkdir -p "$HOOKS_DIR"

# Copy hooks
cp "$SOURCE_DIR/pre-commit" "$HOOKS_DIR/pre-commit"
chmod +x "$HOOKS_DIR/pre-commit"

echo "✓ pre-commit hook installed."
echo ""
echo "Note: Hooks are installed in .git/hooks/ which is shared by all worktrees."

