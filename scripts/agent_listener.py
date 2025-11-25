import time
import os
import sys
import json
import subprocess
from datetime import datetime

# Configuration
AGENT_NAME = os.environ.get("AGENT_NAME", "Unknown")
import tempfile
NOTIFICATION_FILE = os.path.join(tempfile.gettempdir(), "agent_notifications")
TASKS_FILE = "/repo/tasks.json"
TASK_MANAGER = "/repo/scripts/task_manager.py"
POLL_INTERVAL = 1  # seconds
WORK_SIMULATION_TIME = 15  # seconds to simulate work

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{AGENT_NAME}] {message}")
    sys.stdout.flush()


def read_tasks():
    """Read and parse tasks.json"""
    try:
        with open(TASKS_FILE, 'r') as f:
            data = json.load(f)
            return data.get('tasks', [])
    except FileNotFoundError:
        log(f"Tasks file not found: {TASKS_FILE}")
        return []
    except json.JSONDecodeError as e:
        log(f"Error parsing tasks.json: {e}")
        return []


def get_my_tasks():
    """Get tasks assigned to this agent with status TODO or WIP"""
    tasks = read_tasks()
    my_tasks = [
        task for task in tasks
        if task.get('assigned') == AGENT_NAME and task.get('status') in ['TODO', 'WIP']
    ]
    return my_tasks


def update_task_status(task_id, new_status):
    """Update task status using task_manager.py"""
    log(f"Updating task {task_id} to status {new_status}...")
    try:
        cmd = [
            sys.executable,
            TASK_MANAGER,
            'update',
            task_id,
            '--status',
            new_status
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        log(f"✓ Task {task_id} updated to {new_status}")
        return True
    except subprocess.CalledProcessError as e:
        log(f"✗ Failed to update task: {e.stderr}")
        return False


def determine_next_status(agent_name, current_status):
    """Determine the next status based on agent role and current status"""
    # Status progression workflow
    if agent_name in ["Dev1", "Dev2"]:
        # Developer agents: TODO -> WIP -> TESTING
        if current_status == "TODO":
            return "WIP"
        elif current_status == "WIP":
            return "TESTING"
    elif agent_name == "Testing":
        # Testing agent: TODO/TESTING -> WIP -> REVIEW
        if current_status in ["TODO", "TESTING"]:
            return "WIP"
        elif current_status == "WIP":
            return "REVIEW"
    elif agent_name == "Review":
        # Review agent: REVIEW -> WIP -> APPROVED
        if current_status == "REVIEW":
            return "WIP"
        elif current_status == "WIP":
            return "APPROVED"
    elif agent_name == "DevOps":
        # DevOps agent: APPROVED -> WIP -> COMPLETED
        if current_status == "APPROVED":
            return "WIP"
        elif current_status == "WIP":
            return "COMPLETED"
    elif agent_name == "Taskmaster":
        # Taskmaster doesn't auto-execute tasks
        return None
    
    return None


from llm_client import get_llm_client

def execute_work(task):
    """Execute work on a task using the configured LLM provider"""
    task_id = task['id']
    title = task['title']
    description = task.get('description', 'No description')
    
    log(f"📋 Starting work on task {task_id}: {title}")
    log(f"   Description: {description}")
    
    try:
        client = get_llm_client()
        
        # Construct prompt
        system_prompt = f"You are an AI agent named {AGENT_NAME}. Your role is {os.environ.get('AGENT_ROLE', 'Developer')}."
        prompt = f"""
        Task ID: {task_id}
        Title: {title}
        Description: {description}
        
        Please perform this task. 
        If you need to create or modify files, use the following format EXACTLY:
        
        ### File: path/to/filename.ext
        ```language
        code content...
        ```
        
        You can provide multiple files.
        """
        
        log("🤖 Querying LLM...")
        response = client.generate_text(prompt, system_prompt)
        
        log(f"✅ LLM Response received ({len(response)} chars)")
        log("---------------------------------------------------")
        log(response)
        log("---------------------------------------------------")
        
        # Save response to artifact
        work_dir = "work_artifacts"
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
            
        artifact_path = os.path.join(work_dir, f"{task_id}_response.md")
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write(f"# Task {task_id}: {title}\n\n")
            f.write(response)
            
        log(f"💾 Saved response to {artifact_path}")
        
        # Apply changes
        apply_code_changes(response)
        
    except Exception as e:
        log(f"❌ Error executing work: {e}")

def apply_code_changes(response_text):
    """
    Parses markdown code blocks and applies them to files.
    Format expected:
    
    ### File: path/to/file.py
    ```python
    code...
    ```
    """
    import re
    
    # Regex to find file paths and code blocks
    # Looks for lines starting with "### File: <path>" followed by a code block
    pattern = r"### File: (.+?)\n.*?```\w*\n(.*?)```"
    matches = re.findall(pattern, response_text, re.DOTALL)
    
    if not matches:
        log("ℹ️ No code blocks to apply found in response.")
        return

    for file_path, code_content in matches:
        file_path = file_path.strip()
        
        # Security check: prevent writing outside repo
        if ".." in file_path or file_path.startswith("/"):
            log(f"⚠️ Skipping unsafe file path: {file_path}")
            continue
            
        full_path = os.path.join(os.getcwd(), file_path)
        dir_name = os.path.dirname(full_path)
        
        try:
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name)
                
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(code_content)
            log(f"✅ Wrote code to {file_path}")
            
        except Exception as e:
            log(f"❌ Failed to write to {file_path}: {e}")


def execute_task(task):
    """Execute a single task"""
    task_id = task['id']
    current_status = task['status']
    
    # Determine what status to move to
    if current_status == "TODO":
        # Start working: TODO -> WIP
        next_status = "WIP"
        log(f"🎯 Picking up task {task_id}")
        if not update_task_status(task_id, next_status):
            return False
        
        # Execute work
        execute_work(task)
        
        # Move to next stage
        final_status = determine_next_status(AGENT_NAME, "WIP")
        if final_status:
            update_task_status(task_id, final_status)
    
    elif current_status == "WIP":
        # Already in progress, continue and finish
        log(f"⚡ Continuing work on task {task_id}")
        execute_work(task)
        
        # Complete and move to next status
        next_status = determine_next_status(AGENT_NAME, "WIP")
        if next_status:
            update_task_status(task_id, next_status)
    
    return True


def process_notification(line):
    """Process a notification from the watcher"""
    log(f"📨 Received notification: {line.strip()}")
    
    if "NEW TASK ASSIGNMENT" in line or "Status:" in line:
        # Task change detected, check for our tasks
        log("Checking for my assigned tasks...")
        my_tasks = get_my_tasks()
        
        if my_tasks:
            log(f"Found {len(my_tasks)} task(s) to process")
            for task in my_tasks:
                execute_task(task)
        else:
            log("No tasks assigned to me in TODO or WIP status")


def main():
    log("🚀 Agent Listener started. Waiting for tasks...")
    log(f"   Agent Role: {os.environ.get('AGENT_ROLE', 'unknown')}")
    log(f"   Working Directory: {os.getcwd()}")
    
    # Ensure notification file exists
    if not os.path.exists(NOTIFICATION_FILE):
        with open(NOTIFICATION_FILE, "w") as f:
            f.write("")
    
    # Check for existing tasks on startup
    log("Checking for existing assigned tasks...")
    my_tasks = get_my_tasks()
    if my_tasks:
        log(f"Found {len(my_tasks)} existing task(s) on startup")
        for task in my_tasks:
            execute_task(task)
    else:
        log("No tasks assigned to me. Waiting for notifications...")
    
    # Monitor notification file for new tasks
    with open(NOTIFICATION_FILE, "r") as f:
        f.seek(0, os.SEEK_END)
        
        while True:
            line = f.readline()
            if line:
                process_notification(line)
            else:
                time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
