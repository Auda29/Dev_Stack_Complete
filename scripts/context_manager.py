"""
Context Manager for Agent Conversations

This module manages conversation history and context windows for LLM interactions.
It ensures agents maintain coherent multi-turn conversations while staying within token limits.
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path


class ContextManager:
    """Manages conversation context and history for agent tasks."""
    
    def __init__(self, 
                 task_id: str,
                 agent_name: str,
                 max_tokens: int = 8000,
                 context_dir: str = "work_artifacts/contexts"):
        """
        Initialize context manager for a task.
        
        Args:
            task_id: Unique task identifier (e.g., T-001)
            agent_name: Name of the agent
            max_tokens: Maximum tokens to maintain in context
            context_dir: Directory to persist context data
        """
        self.task_id = task_id
        self.agent_name = agent_name
        self.max_tokens = max_tokens
        self.context_dir = Path(context_dir)
        self.context_file = self.context_dir / f"{task_id}_{agent_name}.json"
        
        # Message history
        self.messages: List[Dict] = []
        self.total_tokens = 0
        
        # Ensure context directory exists
        self.context_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing context if available
        self._load_context()
    
    def add_message(self, role: str, content: str, tokens: Optional[int] = None):
        """
        Add a message to the conversation history.
        
        Args:
            role: Message role ('system', 'user', 'assistant')
            content: Message content
            tokens: Optional pre-calculated token count
        """
        # Estimate tokens if not provided (rough estimate: ~4 chars per token)
        if tokens is None:
            tokens = len(content) // 4
        
        message = {
            'role': role,
            'content': content,
            'tokens': tokens,
            'timestamp': datetime.now().isoformat()
        }
        
        self.messages.append(message)
        self.total_tokens += tokens
        
        # Trim if exceeding max tokens
        self._trim_if_needed()
        
        # Auto-save
        self._save_context()
    
    def add_system_message(self, content: str):
        """Add a system message."""
        self.add_message('system', content)
    
    def add_user_message(self, content: str):
        """Add a user message."""
        self.add_message('user', content)
    
    def add_assistant_message(self, content: str, tokens: Optional[int] = None):
        """Add an assistant message."""
        self.add_message('assistant', content, tokens)
    
    def get_messages(self, include_system: bool = True) -> List[Dict]:
        """
        Get conversation messages formatted for LLM API.
        
        Args:
            include_system: Whether to include system messages
            
        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        messages = []
        for msg in self.messages:
            if not include_system and msg['role'] == 'system':
                continue
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        return messages
    
    def get_context_summary(self) -> str:
        """
        Get a summary of the conversation context.
        
        Returns:
            Formatted summary string
        """
        if not self.messages:
            return "No conversation history."
        
        summary = f"# Context for Task {self.task_id} ({self.agent_name})\n\n"
        summary += f"Messages: {len(self.messages)}\n"
        summary += f"Total Tokens: ~{self.total_tokens}\n"
        summary += f"Started: {self.messages[0]['timestamp']}\n"
        summary += f"Last Update: {self.messages[-1]['timestamp']}\n\n"
        
        summary += "## Recent Messages:\n"
        for msg in self.messages[-5:]:  # Last 5 messages
            summary += f"- [{msg['role']}] {msg['content'][:100]}...\n"
        
        return summary
    
    def _trim_if_needed(self):
        """Trim old messages if exceeding token limit."""
        if self.total_tokens <= self.max_tokens:
            return
        
        # Keep system messages and trim oldest user/assistant messages
        system_messages = [msg for msg in self.messages if msg['role'] == 'system']
        other_messages = [msg for msg in self.messages if msg['role'] != 'system']
        
        # Calculate tokens in system messages
        system_tokens = sum(msg['tokens'] for msg in system_messages)
        available_tokens = self.max_tokens - system_tokens
        
        # Keep most recent messages that fit
        trimmed_messages = []
        current_tokens = 0
        
        for msg in reversed(other_messages):
            if current_tokens + msg['tokens'] <= available_tokens:
                trimmed_messages.insert(0, msg)
                current_tokens += msg['tokens']
            else:
                break
        
        # Guarantee at least the most recent non-system message survives trimming
        if not trimmed_messages and other_messages:
            preserved_msg = other_messages[-1]
            trimmed_messages = [preserved_msg]
            current_tokens = preserved_msg['tokens']
        
        # Add summary of trimmed messages if any were removed
        if len(trimmed_messages) < len(other_messages):
            removed_count = len(other_messages) - len(trimmed_messages)
            summary = {
                'role': 'system',
                'content': f'[Context trimmed: {removed_count} older messages removed to maintain token limit]',
                'tokens': 50,
                'timestamp': datetime.now().isoformat()
            }
            trimmed_messages.insert(0, summary)
            current_tokens += 50
        
        # If total tokens still exceed limit, drop newest system messages first
        while system_messages and (system_tokens + current_tokens) > self.max_tokens:
            removed = system_messages.pop()  # remove latest system context (e.g., RAG snippet)
            system_tokens -= removed['tokens']
        
        # Reconstruct messages list
        self.messages = system_messages + trimmed_messages
        self.total_tokens = system_tokens + current_tokens
    
    def _save_context(self):
        """Persist context to disk."""
        try:
            data = {
                'task_id': self.task_id,
                'agent_name': self.agent_name,
                'max_tokens': self.max_tokens,
                'total_tokens': self.total_tokens,
                'messages': self.messages,
                'last_saved': datetime.now().isoformat()
            }
            
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not save context: {e}")
    
    def _load_context(self):
        """Load context from disk if it exists."""
        if not self.context_file.exists():
            return
        
        try:
            with open(self.context_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.messages = data.get('messages', [])
            self.total_tokens = data.get('total_tokens', 0)
            
        except Exception as e:
            print(f"Warning: Could not load context: {e}")
    
    def clear(self):
        """Clear all conversation history."""
        self.messages = []
        self.total_tokens = 0
        
        # Remove context file
        if self.context_file.exists():
            self.context_file.unlink()
    
    def export_conversation(self, output_path: Optional[str] = None) -> str:
        """
        Export conversation to a markdown file.
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            Path to exported file
        """
        if output_path is None:
            output_path = self.context_dir / f"{self.task_id}_{self.agent_name}_conversation.md"
        
        output_path = Path(output_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Conversation: {self.task_id} - {self.agent_name}\n\n")
            f.write(f"Total Messages: {len(self.messages)}\n")
            f.write(f"Total Tokens: ~{self.total_tokens}\n\n")
            f.write("---\n\n")
            
            for msg in self.messages:
                f.write(f"## {msg['role'].upper()}\n")
                f.write(f"*{msg['timestamp']}* ({msg['tokens']} tokens)\n\n")
                f.write(f"{msg['content']}\n\n")
                f.write("---\n\n")
        
        return str(output_path)
    
    def add_code_context(self, code_snippets: List[Dict], max_snippets: int = 5):
        """
        Add code context from RAG results to the conversation.
        
        Args:
            code_snippets: List of code snippets from RAG query
            max_snippets: Maximum number of snippets to include
        """
        if not code_snippets:
            return
        
        context = "## Relevant Code Context\n\n"
        for i, snippet in enumerate(code_snippets[:max_snippets]):
            context += f"### {snippet.get('source', 'Unknown source')}\n"
            context += f"```\n{snippet.get('content', '')}\n```\n\n"
        
        self.add_system_message(context)


class MultiAgentContextManager:
    """Manages contexts for multiple agents working on the same task."""
    
    def __init__(self, task_id: str, context_dir: str = "work_artifacts/contexts"):
        """
        Initialize multi-agent context manager.
        
        Args:
            task_id: Task identifier
            context_dir: Directory for context storage
        """
        self.task_id = task_id
        self.context_dir = context_dir
        self.agent_contexts: Dict[str, ContextManager] = {}
    
    def get_context(self, agent_name: str, max_tokens: int = 8000) -> ContextManager:
        """
        Get or create context for an agent.
        
        Args:
            agent_name: Name of the agent
            max_tokens: Maximum tokens for the agent
            
        Returns:
            ContextManager instance for the agent
        """
        if agent_name not in self.agent_contexts:
            self.agent_contexts[agent_name] = ContextManager(
                task_id=self.task_id,
                agent_name=agent_name,
                max_tokens=max_tokens,
                context_dir=self.context_dir
            )
        
        return self.agent_contexts[agent_name]
    
    def get_shared_summary(self) -> str:
        """
        Get a summary of all agent conversations for this task.
        
        Returns:
            Combined summary from all agents
        """
        summary = f"# Multi-Agent Context for Task {self.task_id}\n\n"
        
        for agent_name, context in self.agent_contexts.items():
            summary += f"## {agent_name}\n"
            summary += context.get_context_summary()
            summary += "\n\n"
        
        return summary


if __name__ == "__main__":
    # Test the context manager
    print("Testing ContextManager...")
    
    ctx = ContextManager("T-TEST", "TestAgent", max_tokens=500)
    
    ctx.add_system_message("You are a helpful coding assistant.")
    ctx.add_user_message("Write a hello world function in Python")
    ctx.add_assistant_message("Here's a hello world function:\n\ndef hello():\n    print('Hello, World!')")
    
    print(ctx.get_context_summary())
    print(f"\nContext saved to: {ctx.context_file}")
    
    # Test export
    export_path = ctx.export_conversation()
    print(f"Conversation exported to: {export_path}")
