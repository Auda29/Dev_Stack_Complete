import os
import sys
import subprocess
import time

def run_task_manager(args):
    """Run task_manager.py with arguments"""
    script_path = os.path.join(os.path.dirname(__file__), "task_manager.py")
    cmd = [sys.executable, script_path] + args
    try:
        subprocess.run(cmd, check=True)
        time.sleep(1) # Give watcher a moment to breathe
    except subprocess.CalledProcessError as e:
        print(f"Error running task manager: {e}")
        sys.exit(1)

def main():
    print("🚀 Seeding Example Project: Todo App")
    print("-----------------------------------")

    # 1. DevOps: Setup
    print("[1/3] Creating DevOps Task: Project Setup")
    run_task_manager([
        "add",
        "--title", "Setup Project Structure",
        "--assigned", "DevOps",
        "--priority", "High",
        "--description", "Initialize a basic Python project structure with a virtual environment setup script and a requirements.txt file.",
        "--tech_notes", "Create setup_env.sh and requirements.txt"
    ])

    # 2. Dev1: Backend
    print("[2/3] Creating Dev1 Task: Backend API")
    run_task_manager([
        "add",
        "--title", "Implement Todo API",
        "--assigned", "Dev1",
        "--priority", "High",
        "--dependencies", "T-001",
        "--description", "Create a simple FastAPI backend with endpoints to GET, POST, and DELETE todos. Use an in-memory list for storage.",
        "--tech_notes", "File: backend/main.py"
    ])

    # 3. Dev2: Frontend
    print("[3/3] Creating Dev2 Task: Frontend UI")
    run_task_manager([
        "add",
        "--title", "Implement Todo UI",
        "--assigned", "Dev2",
        "--priority", "Medium",
        "--dependencies", "T-002",
        "--description", "Create a simple HTML/JS frontend to interact with the API. It should list todos and allow adding new ones.",
        "--tech_notes", "File: frontend/index.html"
    ])

    print("\n✅ Example project seeded!")
    print("Run 'python scripts/watcher.py' to start the automation (if not running).")
    print("Ensure Docker containers are up: 'docker compose up -d'")

if __name__ == "__main__":
    main()
