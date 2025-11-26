#!/usr/bin/env python3
"""
Interactive Taskmaster Chat Interface

This script provides an interactive chat interface where users can:
- Describe what they want to build in natural language
- Have the Taskmaster AI create and assign tasks automatically
- Monitor task progress
- Get project planning advice
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_client import get_llm_client
from task_manager import TaskManager


class TaskmasterChat:
    def __init__(self):
        """Initialize the Taskmaster chat interface."""
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.base_dir)
        self.tasks_file = os.path.join(self.project_root, "tasks.json")
        
        # Initialize LLM client (using OpenAI for Taskmaster)
        self.llm = get_llm_client(provider="openai")
        
        # Initialize task manager
        self.task_manager = TaskManager(self.tasks_file)
        
        # Conversation history
        self.conversation_history = []
        
        # System prompt for Taskmaster
        self.system_prompt = """You are the Taskmaster, an AI project manager for a multi-agent development system.

Your role is to:
1. Understand user requests for features, fixes, or improvements
2. Break down complex requests into specific, actionable tasks
3. Assign tasks to the appropriate agents:
   - Dev1: Core business logic, models, utilities
   - Dev2: APIs, integrations, UI components
   - Testing: Test generation and QA
   - Review: Code review and security checks
   - DevOps: Deployment, CI/CD, infrastructure

4. Create tasks with clear descriptions and technical notes
5. Provide project planning advice and estimates

When a user describes what they want, respond with:
1. A brief acknowledgment of their request
2. A breakdown of the tasks you'll create
3. Then output task creation commands in this EXACT format:

CREATE_TASK:
Title: [task title]
Assigned: [agent name]
Description: [detailed description]
Priority: [High/Medium/Low]
Technical Notes: [optional technical guidance]
---

You can create multiple tasks by repeating the CREATE_TASK block.

Be conversational and helpful. Ask clarifying questions if the request is unclear."""

    def print_banner(self):
        """Print welcome banner."""
        print("\n" + "="*60)
        print("🎯 Taskmaster - AI Project Manager")
        print("="*60)
        print("\nWelcome! I'm your AI Taskmaster. Tell me what you want to build,")
        print("and I'll break it down into tasks and assign them to the team.\n")
        print("Commands:")
        print("  - Type your request naturally")
        print("  - 'status' - View current tasks")
        print("  - 'help' - Show help")
        print("  - 'quit' or 'exit' - Exit chat")
        print("="*60 + "\n")

    def get_current_tasks_summary(self):
        """Get a summary of current tasks for context."""
        tasks = self.task_manager.list_tasks()
        
        if not tasks:
            return "No current tasks."
        
        summary = []
        for task in tasks:
            if task['status'] != 'COMPLETED':
                summary.append(f"- {task['id']}: {task['title']} ({task['status']}, assigned to {task['assigned']})")
        
        return "\n".join(summary) if summary else "All tasks completed!"

    def parse_task_creation(self, response):
        """Parse task creation commands from LLM response."""
        tasks_to_create = []
        
        # Split by CREATE_TASK markers
        blocks = response.split("CREATE_TASK:")
        
        for block in blocks[1:]:  # Skip first split (before first CREATE_TASK)
            # Parse task fields
            task = {
                'title': '',
                'assigned': 'Dev1',  # Default
                'description': '',
                'priority': 'Medium',
                'technical_notes': ''
            }
            
            lines = block.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('Title:'):
                    task['title'] = line.replace('Title:', '').strip()
                elif line.startswith('Assigned:'):
                    task['assigned'] = line.replace('Assigned:', '').strip()
                elif line.startswith('Description:'):
                    task['description'] = line.replace('Description:', '').strip()
                elif line.startswith('Priority:'):
                    task['priority'] = line.replace('Priority:', '').strip()
                elif line.startswith('Technical Notes:'):
                    task['technical_notes'] = line.replace('Technical Notes:', '').strip()
            
            # Only add if we have at least a title
            if task['title']:
                tasks_to_create.append(task)
        
        return tasks_to_create

    def create_tasks(self, tasks):
        """Create tasks using task_manager."""
        created_tasks = []
        
        for task in tasks:
            try:
                task_id = self.task_manager.add_task(
                    title=task['title'],
                    assigned=task['assigned'],
                    description=task['description'],
                    priority=task['priority'],
                    technical_notes=task.get('technical_notes', '')
                )
                created_tasks.append(task_id)
                print(f"  ✅ Created {task_id}: {task['title']} → {task['assigned']}")
            except Exception as e:
                print(f"  ❌ Failed to create task '{task['title']}': {e}")
        
        return created_tasks

    def chat(self, user_message):
        """Process a user message and get Taskmaster response."""
        # Add current tasks context
        tasks_context = self.get_current_tasks_summary()
        
        # Build messages for LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "system", "content": f"Current tasks:\n{tasks_context}"}
        ]
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add user message
        messages.append({"role": "user", "content": user_message})
        
        # Get LLM response
        print("\n🤔 Taskmaster is thinking...\n")
        response = self.llm.generate_with_messages(messages)
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Keep history manageable (last 10 exchanges)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        return response

    def show_status(self):
        """Show current task status."""
        print("\n" + "="*60)
        print("📊 Current Tasks")
        print("="*60 + "\n")
        
        tasks = self.task_manager.list_tasks()
        
        if not tasks:
            print("No tasks yet. Tell me what you want to build!\n")
            return
        
        # Group by status
        by_status = {}
        for task in tasks:
            status = task['status']
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(task)
        
        # Display
        for status in ['TODO', 'WIP', 'TESTING', 'REVIEW', 'APPROVED', 'COMPLETED']:
            if status in by_status:
                print(f"\n{status}:")
                for task in by_status[status]:
                    print(f"  {task['id']}: {task['title']} ({task['assigned']})")
        
        print("\n" + "="*60 + "\n")

    def show_help(self):
        """Show help information."""
        print("\n" + "="*60)
        print("📖 Help")
        print("="*60)
        print("""
How to use Taskmaster:

1. Describe what you want to build naturally:
   "I need a user authentication system with JWT tokens"
   "Add a REST API for managing blog posts"
   "Create unit tests for the payment module"

2. I'll break it down into tasks and assign them to agents

3. Use commands:
   - 'status' - View all current tasks
   - 'help' - Show this help
   - 'quit' or 'exit' - Exit chat

The agents will automatically work on assigned tasks!
        """)
        print("="*60 + "\n")

    def run(self):
        """Run the interactive chat loop."""
        self.print_banner()
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit']:
                    print("\n👋 Goodbye! Your agents will keep working on the tasks.\n")
                    break
                
                if user_input.lower() == 'status':
                    self.show_status()
                    continue
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                # Get Taskmaster response
                response = self.chat(user_input)
                
                # Parse and create tasks
                tasks_to_create = self.parse_task_creation(response)
                
                # Display response (without CREATE_TASK blocks)
                response_text = response.split("CREATE_TASK:")[0].strip()
                print(f"\n🎯 Taskmaster: {response_text}\n")
                
                # Create tasks if any were specified
                if tasks_to_create:
                    print("\n📝 Creating tasks...\n")
                    created = self.create_tasks(tasks_to_create)
                    
                    if created:
                        print(f"\n✅ Created {len(created)} task(s). The watcher will notify agents.\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Your agents will keep working on the tasks.\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                print("Please try again or type 'help' for assistance.\n")


def main():
    """Main entry point."""
    chat = TaskmasterChat()
    chat.run()


if __name__ == "__main__":
    main()
