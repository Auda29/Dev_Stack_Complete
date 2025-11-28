#!/usr/bin/env python3
"""
Auto-execute DevOps Git Integration

This script automatically runs when the DevOps agent completes a task.
It watches for integration scripts created by the DevOps agent and executes them.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class IntegrationScriptHandler(FileSystemEventHandler):
    """Watches for integration scripts and executes them."""
    
    def __init__(self, worktree_path):
        self.worktree_path = Path(worktree_path)
        self.processed = set()
    
    def on_created(self, event):
        """Called when a file is created."""
        if event.is_directory:
            return
        
        filepath = Path(event.src_path)
        
        # Check if it's an integration script
        if filepath.name.startswith('integrate_') and filepath.name.endswith('.sh'):
            self.execute_integration_script(filepath)
    
    def execute_integration_script(self, script_path):
        """Execute the integration script."""
        if str(script_path) in self.processed:
            return
        
        self.processed.add(str(script_path))
        
        print(f"\n{'='*60}")
        print(f"🚀 Auto-executing integration script: {script_path.name}")
        print(f"{'='*60}\n")
        
        try:
            # Make script executable
            os.chmod(script_path, 0o755)
            
            # Execute the script
            result = subprocess.run(
                ['bash', str(script_path)],
                capture_output=True,
                text=True,
                cwd=self.worktree_path
            )
            
            print(result.stdout)
            
            if result.returncode != 0:
                print(f"❌ Integration failed:\n{result.stderr}")
            else:
                print("\n✅ Integration completed successfully!")
                
        except Exception as e:
            print(f"❌ Error executing integration script: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python devops_auto_integrator.py <worktree_path>")
        print("Example: python devops_auto_integrator.py /repo/.worktrees/devops")
        sys.exit(1)
    
    worktree_path = sys.argv[1]
    
    if not os.path.exists(worktree_path):
        print(f"Error: Worktree path does not exist: {worktree_path}")
        sys.exit(1)
    
    print(f"🔍 Watching for integration scripts in: {worktree_path}")
    print("Press Ctrl+C to stop")
    
    event_handler = IntegrationScriptHandler(worktree_path)
    observer = Observer()
    observer.schedule(event_handler, worktree_path, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n\n👋 Stopped watching for integration scripts")
    
    observer.join()


if __name__ == "__main__":
    main()
