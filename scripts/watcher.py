import time
import os
import json
import subprocess
import sys
from datetime import datetime

# Configuration
# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
TASKS_FILE = os.path.join(PROJECT_ROOT, "tasks.json")
RENDER_SCRIPT = os.path.join(BASE_DIR, "render_tasks.py")
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
POLL_INTERVAL = 2  # seconds

# Ensure log directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


# Agent to Container Mapping
AGENT_MAPPING = {
    "Taskmaster": "agent_taskmaster",
    "Dev1": "agent_dev1",
    "Dev2": "agent_dev2",
    "Testing": "agent_testing",
    "Review": "agent_review",
    "DevOps": "agent_devops"
}


def get_file_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: File {filepath} contains invalid JSON.")
        return None


def parse_tasks(content):
    """
    Parses the JSON content and returns a dictionary of tasks.
    Structure: { 'T-001': { 'status': 'TODO', 'assigned': 'Dev1', 'title': '...' } }
    """
    tasks = {}
    if not content or "tasks" not in content:
        return tasks

    for task in content["tasks"]:
        tasks[task['id']] = {
            'id': task['id'],
            'title': task['title'],
            'status': task['status'],
            'assigned': task['assigned']
        }

    return tasks


def notify_agent(agent_name, task_info):
    """
    Triggers the agent container.
    """
    container_name = AGENT_MAPPING.get(agent_name)
    if not container_name:
        print(f"Warning: No container mapping found for agent '{agent_name}'")
        return

    print(f"[*] Notifying {agent_name} ({container_name}) about task {task_info['id']}...")

    # Construct the message
    message = f"NEW TASK ASSIGNMENT: {task_info['id']} - {task_info['title']} (Status: {task_info['status']})"

    # Docker exec command
    # We try to write to a notification file inside the container
    # and also print to stdout which might be visible if attached
    cmd = [
        "docker", "exec", container_name,
        "sh", "-c",
        f"echo '{message}' >> /tmp/agent_notifications && echo '{message}'"
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"[+] Notification sent to {container_name}")
    except subprocess.CalledProcessError as e:
        print(f"[-] Failed to notify {container_name}: {e}")


def update_markdown_view():
    """
    Runs the render_tasks.py script to update docs/tasks.md
    """
    try:
        cmd = [sys.executable, RENDER_SCRIPT]
        subprocess.run(cmd, check=True, capture_output=True)
        print("[+] Updated docs/tasks.md")
    except subprocess.CalledProcessError as e:
        print(f"[-] Failed to update markdown view: {e}")


def main():
    print(f"Starting Watcher for {TASKS_FILE}...")
    print(f"Logging to {LOG_DIR}")
    
    # Redirect stderr to file
    sys.stderr = open(os.path.join(LOG_DIR, "watcher.err"), "a")

    last_mtime = 0
    last_tasks = {}

    # Initial load
    if os.path.exists(TASKS_FILE):
        last_mtime = os.path.getmtime(TASKS_FILE)
        content = get_file_content(TASKS_FILE)
        last_tasks = parse_tasks(content)
        print(f"Loaded {len(last_tasks)} tasks. Monitoring for changes...")
    else:
        print("Waiting for tasks file to be created...")

    try:
        while True:
            time.sleep(POLL_INTERVAL)

            if not os.path.exists(TASKS_FILE):
                continue

            current_mtime = os.path.getmtime(TASKS_FILE)

            if current_mtime > last_mtime:
                print(f"\n[!] Change detected at {datetime.now().strftime('%H:%M:%S')}")
                last_mtime = current_mtime

                # Update Markdown View
                update_markdown_view()

                content = get_file_content(TASKS_FILE)
                current_tasks = parse_tasks(content)

                # Detect changes
                for task_id, task in current_tasks.items():
                    old_task = last_tasks.get(task_id)

                    if not old_task:
                        print(f"New task detected: {task_id}")
                        # Optionally notify if it's assigned immediately
                        if task['assigned'] != 'UNKNOWN' and task['assigned'] != 'Unassigned':
                            notify_agent(task['assigned'], task)
                    else:
                        # Check for relevant changes
                        status_changed = task['status'] != old_task['status']
                        assigned_changed = task['assigned'] != old_task['assigned']

                        if status_changed or assigned_changed:
                            print(f"Update on {task_id}:")
                            if status_changed:
                                print(f"  Status: {old_task['status']} -> {task['status']}")
                            if assigned_changed:
                                print(f"  Assigned: {old_task['assigned']} -> {task['assigned']}")

                            # Trigger logic
                            # Status-based routing
                            if status_changed:
                                new_status = task['status']
                                if new_status == "TESTING":
                                    notify_agent("Testing", task)
                                elif new_status == "REVIEW":
                                    notify_agent("Review", task)
                                elif new_status == "APPROVED":
                                    notify_agent("DevOps", task)
                                elif new_status in ["TODO", "WIP"]:
                                    # Notify the assigned dev if status moves back
                                    if task['assigned'] in AGENT_MAPPING:
                                        notify_agent(task['assigned'], task)
                            
                            # Assignment-based routing
                            elif assigned_changed:
                                if task['assigned'] in AGENT_MAPPING:
                                    notify_agent(task['assigned'], task)

                last_tasks = current_tasks

    except KeyboardInterrupt:
        print("\nStopping Watcher.")


if __name__ == "__main__":
    main()
