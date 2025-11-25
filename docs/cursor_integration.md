# Cursor Integration Guide

Dev_Stack is designed to work seamlessly with AI-powered IDEs like Cursor. Since the system is driven by `tasks.json`, you can use Cursor's Chat to interact with the **Taskmaster** role effectively.

## Workflow

1.  **Plan**: You chat with Cursor to define what needs to be done.
2.  **Command**: You ask Cursor to use the `task_manager.py` script to create tasks.
3.  **Execute**: The background `watcher.py` picks up the changes and dispatches Docker agents.

## Recommended Prompts

### Planning Phase (Talking to Taskmaster)

Use these prompts in Cursor Chat to break down features into tasks.

**Prompt:**
> "Act as the Taskmaster. We need to implement a new feature: [Feature Name]. Break this down into atomic tasks for Dev1 (Logic) and Dev2 (Interface). Use the `python scripts/task_manager.py add` command to create them. Ensure you set dependencies correctly."

**Example:**
> "Act as Taskmaster. We need a user profile page. Create a task for Dev1 to build the API endpoint and a task for Dev2 to build the frontend component. The frontend task should depend on the API task."

### Status Updates

If you are manually intervening or want to check status:

**Prompt:**
> "List all tasks currently in progress (WIP) using the task manager script."

**Prompt:**
> "I fixed the bug in T-003. Please update its status to TESTING."

## Best Practices

-   **Always use the Script**: Don't ask Cursor to edit `tasks.json` manually if possible. Using `python scripts/task_manager.py` ensures the file structure remains valid and avoids JSON syntax errors.
-   **Watch the Logs**: Keep a terminal open with `tail -f logs/watcher.err` (or just the watcher terminal) to see when agents pick up the tasks you created via Cursor.
-   **RAG Context**: When asking Cursor about the project, mention `@docs/tasks.md` to give it the current context of all active tasks.
