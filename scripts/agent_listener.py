import time
import os
import sys
import json
from datetime import datetime

# Configuration
AGENT_NAME = os.environ.get("AGENT_NAME", "Unknown")
NOTIFICATION_FILE = "/tmp/agent_notifications"
POLL_INTERVAL = 1  # seconds

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{AGENT_NAME}] {message}")
    sys.stdout.flush()

def process_notification(line):
    log(f"Received notification: {line.strip()}")
    # In a real agent, this would trigger the LLM loop
    # For now, we just acknowledge it
    if "NEW TASK ASSIGNMENT" in line:
        log("Parsing task details...")
        # Simulate thinking time
        time.sleep(2)
        log("I have received the task. I would now read the requirements and start coding.")
        log("To simulate work, I will just wait here. Use 'python scripts/task_manager.py update ...' to change status.")

def main():
    log("Agent Listener started. Waiting for tasks...")
    
    # Ensure notification file exists
    if not os.path.exists(NOTIFICATION_FILE):
        with open(NOTIFICATION_FILE, "w") as f:
            f.write("")
    
    # Open file and seek to end
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
