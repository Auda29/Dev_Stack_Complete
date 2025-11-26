import time
import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
AGENT_NAME = os.environ.get("AGENT_NAME", "Unknown")
import tempfile
NOTIFICATION_FILE = os.path.join(tempfile.gettempdir(), "agent_notifications")

# Dynamic path resolution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
TASKS_FILE = os.path.join(REPO_ROOT, "tasks.json")
TASK_MANAGER = os.path.join(SCRIPT_DIR, "task_manager.py")
POLL_INTERVAL = 1  # seconds

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


def load_agent_prompt():
    """Load role-specific system prompt for this agent"""
    agent_role = os.environ.get("AGENT_ROLE", "developer")
    
    # Base prompt
    base_prompt = f"""You are {AGENT_NAME}, an AI agent in a multi-agent development system.
Your role is: {agent_role}

CRITICAL RULES:
1. You work in a collaborative multi-agent environment
2. Follow the task description and technical notes exactly
3. When creating or modifying files, use this EXACT format:

### File: path/to/filename.ext
```language
code content here
```

4. You can provide multiple files in one response
5. Always write production-quality, well-documented code
6. Consider existing codebase patterns and conventions
"""
    
    # Role-specific additions
    role_prompts = {
        "orchestration": """
As Taskmaster, your job is to:
- Break down vague requirements into specific, atomic tasks
- Assign tasks appropriately (Dev1 for core logic, Dev2 for APIs/UI, etc.)
- Define dependencies between tasks
- You don't write code yourself, only plan and organize
""",
        "core_development": """
As Dev1 (Core Developer), you:
- Implement business logic, domain models, and core algorithms
- Focus on backend functionality and data processing
- Write clean, type-hinted, well-documented code
- Ensure your code is testable and follows SOLID principles
""",
        "integration_development": """
As Dev2 (Integration Developer), you:
- Build APIs, user interfaces, and integrations
- Implement request/response handling and validation
- Create frontend components and external service integrations
- Ensure API contracts are clear and well-documented
""",
        "quality_assurance": """
As the Testing agent, you:
- Write comprehensive unit and integration tests
- Execute test suites and validate functionality
- Report bugs clearly with reproduction steps
- Verify bug fixes and edge cases
""",
        "code_review": """
As the Review agent, you:
- Check code quality, security, and best practices
- Verify architecture compliance
- Provide constructive feedback
- Approve code for deployment or request changes
""",
        "integration_deployment": """
As the DevOps agent, you:
- Merge approved branches
- Resolve merge conflicts
- Maintain CI/CD pipelines
- Handle deployments and releases
"""
    }
    
    additional_prompt = role_prompts.get(agent_role, "")
    return base_prompt + "\n" + additional_prompt


from llm_client import get_llm_client
from rag_client import RAGClient
from context_manager import ContextManager
from code_editor import apply_code_changes

def execute_work(task):
    """Execute work on a task using the configured LLM provider with RAG"""
    task_id = task['id']
    title = task['title']
    description = task.get('description', 'No description')
    technical_notes = task.get('technical_notes', '')
    
    log(f"📋 Starting work on task {task_id}: {title}")
    log(f"   Description: {description}")
    
    try:
        # Initialize clients
        llm_client = get_llm_client()
        rag_client = RAGClient()
        context = ContextManager(task_id, AGENT_NAME, max_tokens=8000)
        
        # Load agent-specific system prompt
        system_prompt = load_agent_prompt()
        context.add_system_message(system_prompt)
        
        # === RAG: Query codebase for relevant context ===
        log("🔍 Searching codebase for relevant context...")
        rag_query = f"{title} {description}"
        rag_results = rag_client.query(rag_query, n_results=5)
        
        if rag_results:
            log(f"   Found {len(rag_results)} relevant code snippets")
            context.add_code_context(rag_results, max_snippets=5)
        else:
            log("   No relevant code found (codebase may not be indexed)")
        
        # === Construct enhanced prompt ===
        prompt = f"""
# Task Assignment

**Task ID**: {task_id}
**Title**: {title}
**Description**: {description}
"""
        
        if technical_notes:
            prompt += f"""
**Technical Notes**: {technical_notes}
"""
        
        prompt += """

## Your Task

Please complete this task according to your role and the requirements above.

**Output Format**:
If you need to create or modify files, use this EXACT format:

### File: path/to/filename.ext
```language
code content...
```

You can provide multiple files. Include any necessary imports, error handling, and documentation.

## Additional Guidance

1. Check the relevant code context provided above
2. Follow existing patterns and conventions
3. Write production-quality code with proper error handling
4. Add comments for complex logic
5. Consider edge cases and validation

Begin your implementation now.
"""
        
        context.add_user_message(prompt)
        
        # === Query LLM ===
        log("🤖 Querying LLM for implementation...")
        messages = context.get_messages()
        
        response = llm_client.generate_with_messages(
            messages=messages,
            temperature=0.3,  # Lower temperature for more focused code generation
            max_tokens=4096
        )
        
        # Track response
        context.add_assistant_message(response, llm_client.last_token_count)
        
        log(f"✅ LLM Response received ({llm_client.last_token_count} tokens)")
        log(f"   Total tokens used: {llm_client.total_tokens_used}")
        
        # === Save full response ===
        work_dir = Path("work_artifacts")
        work_dir.mkdir(exist_ok=True)
        
        artifact_path = work_dir / f"{task_id}_response.md"
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write(f"# Task {task_id}: {title}\n\n")
            f.write(f"**Agent**: {AGENT_NAME}\n")
            f.write(f"**Timestamp**: {datetime.now().isoformat()}\n\n")
            f.write("## Response\n\n")
            f.write(response)
        
        log(f"💾 Saved response to {artifact_path}")
        
        # Export conversation history
        conversation_path = context.export_conversation()
        log(f"💾 Saved conversation to {conversation_path}")
        
        # === Apply code changes ===
        log("📝 Parsing and applying code changes...")
        results = apply_code_changes(response, workspace_root=os.getcwd())
        
        if results['success_count'] > 0:
            log(f"✅ Successfully applied {results['success_count']} file changes")
        
        if results['failure_count'] > 0:
            log(f"⚠️  {results['failure_count']} file changes failed")
        
        return True
        
    except Exception as e:
        log(f"❌ Error executing work: {e}")
        import traceback
        traceback.print_exc()
        return False


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
        success = execute_work(task)
        
        if success:
            # Move to next stage
            final_status = determine_next_status(AGENT_NAME, "WIP")
            if final_status:
                update_task_status(task_id, final_status)
        else:
            log(f"⚠️  Task {task_id} execution had errors, keeping in WIP status")
    
    elif current_status == "WIP":
        # Already in progress, continue and finish
        log(f"⚡ Continuing work on task {task_id}")
        success = execute_work(task)
        
        if success:
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
    log("🚀 Enhanced Agent Listener started with LLM integration")
    log(f"   Agent: {AGENT_NAME}")
    log(f"   Role: {os.environ.get('AGENT_ROLE', 'unknown')}")
    log(f"   LLM Provider: {os.environ.get('LLM_PROVIDER', 'openai')}")
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
