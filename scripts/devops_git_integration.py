"""
DevOps Git Integration Script

This script helps the DevOps agent create feature branches and push code.
Called by the DevOps agent after reviewing approved code.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime


def run_git_command(cmd, cwd=None):
    """Execute a git command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def get_task_info(task_id):
    """Load task information from tasks.json."""
    tasks_file = Path(__file__).parent.parent / "tasks.json"
    
    try:
        with open(tasks_file, 'r') as f:
            data = json.load(f)
            for task in data.get('tasks', []):
                if task['id'] == task_id:
                    return task
    except Exception as e:
        print(f"Error loading task info: {e}")
    
    return None


def create_feature_branch(task_id, task_title, worktree_path, main_repo_path):
    """
    Create a feature branch from worktree changes.
    
    Args:
        task_id: Task ID (e.g., 'T-002')
        task_title: Task title for branch name
        worktree_path: Path to the agent's worktree
        main_repo_path: Path to main repository
        
    Returns:
        (success, message)
    """
    print(f"\n{'='*60}")
    print(f"DevOps: Creating feature branch for {task_id}")
    print(f"{'='*60}\n")
    
    # Sanitize task title for branch name
    branch_suffix = task_title.lower()
    branch_suffix = branch_suffix.replace(' ', '-')
    branch_suffix = ''.join(c for c in branch_suffix if c.isalnum() or c == '-')
    branch_suffix = branch_suffix[:50]  # Limit length
    
    branch_name = f"feature/{task_id.lower()}-{branch_suffix}"
    
    print(f"📌 Branch name: {branch_name}")
    print(f"📁 Worktree: {worktree_path}")
    print(f"📁 Main repo: {main_repo_path}\n")
    
    # Step 1: Get list of changed files in worktree
    print("🔍 Step 1: Checking for changes in worktree...")
    success, output = run_git_command("git status --short", cwd=worktree_path)
    
    if not success:
        return False, f"Failed to check git status: {output}"
    
    if not output:
        # Check for committed changes ahead of origin/dev
        success, output = run_git_command("git diff --name-only origin/dev HEAD", cwd=worktree_path)
        if not output:
            print("⚠️  No changes detected in worktree (staged, unstaged, or committed)")
            return False, "No changes to commit"
        else:
            print("✅ Found committed changes ahead of origin/dev")
    
    changed_files = output.split('\n')
    print(f"✅ Found {len(changed_files)} changed file(s):\n")
    for file in changed_files[:10]:  # Show first 10
        print(f"   {file}")
    if len(changed_files) > 10:
        print(f"   ... and {len(changed_files) - 10} more")
    print()
    
    # Step 2: Create feature branch in main repo
    print(f"🌿 Step 2: Creating branch '{branch_name}' in main repo...")
    
    # Fetch latest from main
    run_git_command("git fetch origin main", cwd=main_repo_path)
    
    # Check if branch already exists
    success, output = run_git_command(f"git branch --list {branch_name}", cwd=main_repo_path)
    if output:
        print(f"⚠️  Branch '{branch_name}' already exists, using it")
        run_git_command(f"git checkout {branch_name}", cwd=main_repo_path)
    else:
        # Create new branch from main
        success, output = run_git_command(f"git checkout -b {branch_name}", cwd=main_repo_path)
        if not success:
            return False, f"Failed to create branch: {output}"
        print(f"✅ Created branch '{branch_name}'")
    
    print()
    
    # Step 3: Copy files from worktree to main repo
    print("📋 Step 3: Copying changes from worktree to main repo...")
    
    # Get list of modified/added files (comparing against origin/dev to catch commits)
    success, output = run_git_command(
        "git diff --name-only origin/dev...HEAD",
        cwd=worktree_path
    )
    
    if success and output:
        files_to_copy = output.split('\n')
        copied_count = 0
        
        for file_path in files_to_copy:
            src = Path(worktree_path) / file_path
            dst = Path(main_repo_path) / file_path
            
            if src.exists():
                # Create parent directories if needed
                dst.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                import shutil
                shutil.copy2(src, dst)
                copied_count += 1
                print(f"   ✓ Copied: {file_path}")
        
        print(f"\n✅ Copied {copied_count} file(s)")
    else:
        print("⚠️  No files to copy (using git add -A instead)")
    
    print()
    
    # Step 4: Stage all changes
    print("➕ Step 4: Staging changes...")
    success, output = run_git_command("git add -A", cwd=main_repo_path)
    if not success:
        return False, f"Failed to stage changes: {output}"
    print("✅ Changes staged")
    print()
    
    # Step 5: Commit changes
    print("💾 Step 5: Committing changes...")
    commit_message = f"Integrate {task_id}: {task_title}\n\n"
    commit_message += "This commit integrates work from the multi-agent system:\n"
    commit_message += f"- Task: {task_id}\n"
    commit_message += f"- Title: {task_title}\n"
    commit_message += f"- Timestamp: {datetime.now().isoformat()}\n"
    
    success, output = run_git_command(
        f'git commit -m "{commit_message}"',
        cwd=main_repo_path
    )
    
    if not success:
        if "nothing to commit" in output.lower():
            print("⚠️  Nothing to commit (changes may already be committed)")
        else:
            return False, f"Failed to commit: {output}"
    else:
        print(f"✅ Committed changes")
    print()
    
    # Step 6: Push to remote
    print(f"🚀 Step 6: Pushing '{branch_name}' to origin...")
    success, output = run_git_command(
        f"git push -u origin {branch_name}",
        cwd=main_repo_path
    )
    
    if not success:
        print(f"⚠️  Push failed: {output}")
        print("Note: You may need to push manually or check remote configuration")
        return True, f"Branch '{branch_name}' created locally (push failed: {output})"
    
    print(f"✅ Pushed to origin/{branch_name}")
    print()
    
    # Step 7: Fetch in main repo so local knows about new branch
    print(f"🔄 Step 7: Updating local repository...")
    success, output = run_git_command("git fetch origin", cwd=main_repo_path)
    if success:
        print(f"✅ Local repository updated with remote branches")
    print()
    
    # Step 8: Create summary
    summary = f"""
{'='*60}
DevOps Integration Complete
{'='*60}

✅ Task: {task_id} - {task_title}
🌿 Branch: {branch_name}
📁 Files changed: {len(changed_files)}
🚀 Status: Pushed to origin
🔄 Local repo: Updated

Next Steps:
1. Switch to feature branch: git checkout {branch_name}
2. Review the changes
3. Create a pull request if using GitHub/GitLab
4. Merge when ready: git merge {branch_name}

{'='*60}
"""
    
    print(summary)
    
    return True, f"Feature branch '{branch_name}' created and pushed successfully"


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python devops_git_integration.py <task_id> <worktree_path>")
        print("Example: python devops_git_integration.py T-002 /repo/.worktrees/dev1")
        sys.exit(1)
    
    task_id = sys.argv[1]
    worktree_path = sys.argv[2]
    
    # Get main repo path (parent of .worktrees)
    main_repo_path = Path(worktree_path).parent.parent
    
    # Get task info
    task_info = get_task_info(task_id)
    if not task_info:
        print(f"Error: Task {task_id} not found in tasks.json")
        sys.exit(1)
    
    task_title = task_info.get('title', 'Unknown Task')
    
    # Create feature branch
    success, message = create_feature_branch(
        task_id,
        task_title,
        worktree_path,
        main_repo_path
    )
    
    if success:
        print(f"\n✅ Success: {message}")
        sys.exit(0)
    else:
        print(f"\n❌ Error: {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
