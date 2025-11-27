#!/usr/bin/env python3
"""
Dev_Stack Session Starter

This script automates the setup and launch of the Dev_Stack environment:
1. Checks for .env file
2. Installs Python dependencies
3. Starts Docker services
5. Indexes the codebase for RAG
6. Launches the Watcher in a new terminal
7. Launches the Taskmaster Chat in the current terminal
"""

import os
import sys
import subprocess
import time
import platform

def print_step(step, message):
    print(f"\n[{step}/6] {message}...")

def check_env_file():
    print_step(1, "Checking environment configuration")
    if not os.path.exists(".env"):
        print("❌ Error: .env file not found!")
        print("Please copy .env.example to .env and configure your API keys.")
        sys.exit(1)
    print("✅ .env file found")

def install_dependencies():
    print_step(2, "Installing Python dependencies")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies.")
        sys.exit(1)

def start_docker():
    print_step(3, "Starting Docker services")
    try:
        subprocess.check_call(["docker", "compose", "-f", "docker-compose.yml", "-f", "docker-compose.agents.yml", "up", "-d"])
        print("✅ Docker services started")
    except subprocess.CalledProcessError:
        print("❌ Failed to start Docker services.")
        print("Please ensure Docker Desktop is running.")
        sys.exit(1)

def index_codebase():
    print_step(4, "Indexing codebase (RAG)")
    
    embed_script = os.path.join("scripts", "embed_codebase.py")
    if not os.path.exists(embed_script):
        print(f"⚠️  Warning: {embed_script} not found! Skipping indexing.")
        return

    print("Waiting for ChromaDB to be ready...")
    time.sleep(5)  # Give Chroma a moment to start accepting connections
    
    try:
        subprocess.check_call([sys.executable, embed_script])
        print("✅ Codebase indexed")
    except subprocess.CalledProcessError:
        print("⚠️  Failed to index codebase. RAG features might be limited.")
        print("You can try running 'python scripts/embed_codebase.py' manually later.")

def launch_watcher():
    print_step(5, "Launching Watcher")
    
    watcher_script = os.path.join("scripts", "watcher.py")
    if not os.path.exists(watcher_script):
        print(f"❌ Error: {watcher_script} not found!")
        sys.exit(1)

    system = platform.system()
    
    try:
        if system == "Windows":
            # Launch in new command prompt window
            subprocess.Popen(f'start cmd /k "{sys.executable} {watcher_script}"', shell=True)
        elif system == "Darwin":  # macOS
            # Launch in Terminal.app
            subprocess.Popen(['open', '-a', 'Terminal', sys.executable, watcher_script])
        elif system == "Linux":
            # Try common terminal emulators
            terminals = ['gnome-terminal', 'xterm', 'konsole']
            launched = False
            for term in terminals:
                try:
                    if term == 'gnome-terminal':
                        subprocess.Popen([term, '--', sys.executable, watcher_script])
                    else:
                        subprocess.Popen([term, '-e', f"{sys.executable} {watcher_script}"])
                    launched = True
                    break
                except FileNotFoundError:
                    continue
            
            if not launched:
                print("⚠️  Could not detect terminal emulator. Please run 'python scripts/watcher.py' in a separate terminal.")
                return

        print("✅ Watcher launched in new window")
        time.sleep(2)  # Give it a moment to start
        
    except Exception as e:
        print(f"⚠️  Failed to launch watcher automatically: {e}")
        print("Please run 'python scripts/watcher.py' in a separate terminal.")

def launch_taskmaster():
    print_step(6, "Launching Taskmaster")
    
    taskmaster_script = os.path.join("scripts", "taskmaster_chat.py")
    if not os.path.exists(taskmaster_script):
        print(f"❌ Error: {taskmaster_script} not found!")
        sys.exit(1)
        
    print("🚀 Starting Taskmaster Chat...\n")
    try:
        subprocess.call([sys.executable, taskmaster_script])
    except KeyboardInterrupt:
        print("\nSession ended.")

def main():
    print("="*50)
    print("   🚀 Dev_Stack Session Starter")
    print("="*50)
    
    # Ensure we're in the project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    check_env_file()
    install_dependencies()
    start_docker()
    index_codebase()
    launch_watcher()
    launch_taskmaster()

if __name__ == "__main__":
    main()
