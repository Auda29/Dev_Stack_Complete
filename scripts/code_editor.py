"""
Code Editor - Intelligent Code Modification Engine

This module handles parsing LLM responses and applying code changes safely.
Supports multiple edit formats: full rewrites, diffs, function replacements, etc.
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class CodeEdit:
    """Represents a single code edit operation."""
    
    def __init__(self, file_path: str, content: str, edit_type: str = "full_rewrite"):
        self.file_path = file_path
        self.content = content
        self.edit_type = edit_type  # full_rewrite, diff, function_replace
        self.backup_path = None
        
    def __repr__(self):
        return f"CodeEdit({self.file_path}, type={self.edit_type})"


class CodeEditor:
    """Handles intelligent code modifications from LLM outputs."""
    
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.backup_dir = self.workspace_root / ".code_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def parse_llm_response(self, response_text: str) -> List[CodeEdit]:
        """
        Parse LLM response for code changes.
        
        Supported formats:
        1. ### File: path/to/file.py
           ```python
           code...
           ```
        
        2. FILE: path/to/file.py
           ```
           code...
           ```
        
        Args:
            response_text: LLM response containing code blocks
            
        Returns:
            List of CodeEdit objects
        """
        edits = []
        
        # Pattern 1: ### File: path
        pattern1 = r"###\s*File:\s*(.+?)\n.*?```\w*\n(.*?)```"
        matches1 = re.findall(pattern1, response_text, re.DOTALL)
        
        for file_path, code_content in matches1:
            file_path = file_path.strip()
            edits.append(CodeEdit(file_path, code_content, "full_rewrite"))
        
        # Pattern 2: FILE: path (alternative format)
        pattern2 = r"FILE:\s*(.+?)\n.*?```\w*\n(.*?)```"
        matches2 = re.findall(pattern2, response_text, re.DOTALL)
        
        for file_path, code_content in matches2:
            file_path = file_path.strip()
            # Avoid duplicates
            if not any(e.file_path == file_path for e in edits):
                edits.append(CodeEdit(file_path, code_content, "full_rewrite"))
        
        return edits
    
    def validate_edit(self, edit: CodeEdit) -> Tuple[bool, Optional[str]]:
        """
        Validate a code edit before applying.
        
        Args:
            edit: CodeEdit to validate
            
        Returns:
            (is_valid, error_message)
        """
        # Security check: prevent path traversal
        if ".." in edit.file_path or edit.file_path.startswith("/"):
            return False, f"Unsafe file path: {edit.file_path}"
        
        # Check if Python file has valid syntax (if it's a .py file)
        if edit.file_path.endswith('.py'):
            try:
                compile(edit.content, edit.file_path, 'exec')
            except SyntaxError as e:
                return False, f"Python syntax error: {e}"
        
        return True, None
    
    def backup_file(self, file_path: Path) -> Optional[Path]:
        """
        Create a backup of the file before modification.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Path to backup file, or None if file doesn't exist
        """
        if not file_path.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.{timestamp}.bak"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def apply_edit(self, edit: CodeEdit, validate: bool = True) -> Tuple[bool, str]:
        """
        Apply a code edit to the filesystem.
        
        Args:
            edit: CodeEdit to apply
            validate: Whether to validate before applying
            
        Returns:
            (success, message)
        """
        # Validate if requested
        if validate:
            is_valid, error = self.validate_edit(edit)
            if not is_valid:
                return False, f"Validation failed: {error}"
        
        full_path = self.workspace_root / edit.file_path
        
        # Create parent directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing file
        if full_path.exists():
            backup_path = self.backup_file(full_path)
            edit.backup_path = backup_path
        
        # Write the file
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(edit.content)
            
            # Auto-format Python files
            if edit.file_path.endswith('.py'):
                self._format_python_file(full_path)
            
            return True, f"Successfully wrote {edit.file_path}"
            
        except Exception as e:
            # Rollback if backup exists
            if edit.backup_path and edit.backup_path.exists():
                shutil.copy2(edit.backup_path, full_path)
                return False, f"Error writing file (rolled back): {e}"
            return False, f"Error writing file: {e}"
    
    def _format_python_file(self, file_path: Path):
        """
        Auto-format a Python file using black (if available).
        
        Args:
            file_path: Path to Python file
        """
        try:
            import black
            
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            mode = black.Mode()
            formatted = black.format_file_contents(source, fast=False, mode=mode)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted)
                
        except ImportError:
            # Black not installed, skip formatting
            pass
        except Exception as e:
            # Formatting failed, but file is already written
            print(f"Warning: Could not auto-format {file_path}: {e}")
    
    def apply_all(self, edits: List[CodeEdit], stop_on_error: bool = False) -> Dict:
        """
        Apply multiple edits.
        
        Args:
            edits: List of CodeEdit objects
            stop_on_error: Stop applying if any edit fails
            
        Returns:
            Dictionary with results:
                {
                    'success_count': int,
                    'failure_count': int,
                    'results': List[Dict]
                }
        """
        results = {
            'success_count': 0,
            'failure_count': 0,
            'results': []
        }
        
        for edit in edits:
            success, message = self.apply_edit(edit)
            
            results['results'].append({
                'file': edit.file_path,
                'success': success,
                'message': message
            })
            
            if success:
                results['success_count'] += 1
            else:
                results['failure_count'] += 1
                if stop_on_error:
                    break
        
        return results
    
    def rollback_edit(self, edit: CodeEdit) -> bool:
        """
        Rollback an edit using its backup.
        
        Args:
            edit: CodeEdit with backup_path set
            
        Returns:
            Success status
        """
        if not edit.backup_path or not edit.backup_path.exists():
            print(f"No backup found for {edit.file_path}")
            return False
        
        full_path = self.workspace_root / edit.file_path
        
        try:
            shutil.copy2(edit.backup_path, full_path)
            return True
        except Exception as e:
            print(f"Error rolling back {edit.file_path}: {e}")
            return False
    
    def list_backups(self) -> List[Path]:
        """List all backup files."""
        if not self.backup_dir.exists():
            return []
        return sorted(self.backup_dir.glob("*.bak"), reverse=True)
    
    def parse_and_apply(self, llm_response: str, validate: bool = True) -> Dict:
        """
        Parse LLM response and apply all code changes.
        
        Args:
            llm_response: Full LLM response text
            validate: Whether to validate edits
            
        Returns:
            Results dictionary from apply_all()
        """
        edits = self.parse_llm_response(llm_response)
        
        if not edits:
            return {
                'success_count': 0,
                'failure_count': 0,
                'results': [],
                'message': 'No code blocks found in LLM response'
            }
        
        return self.apply_all(edits, stop_on_error=False)


def apply_code_changes(response_text: str, workspace_root: str = "."):
    """
    Convenience function to parse and apply code changes from LLM response.
    
    This is the backward-compatible function used by agent_listener.py
    
    Args:
        response_text: LLM response containing code blocks
        workspace_root: Root directory for file operations
    """
    editor = CodeEditor(workspace_root)
    results = editor.parse_and_apply(response_text, validate=True)
    
    # Log results
    print(f"\n=== Code Changes Applied ===")
    print(f"Success: {results['success_count']}")
    print(f"Failures: {results['failure_count']}")
    
    for result in results['results']:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['file']}: {result['message']}")
    
    return results


if __name__ == "__main__":
    # Test the code editor
    print("Testing CodeEditor...")
    
    # Sample LLM response
    sample_response = """
Here's the implementation:

### File: test_example.py
```python
def hello_world():
    '''A simple hello world function.'''
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
```

### File: utils/helper.py
```python
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
```
"""
    
    editor = CodeEditor(workspace_root=".")
    edits = editor.parse_llm_response(sample_response)
    
    print(f"\nFound {len(edits)} edits:")
    for edit in edits:
        print(f"  - {edit}")
    
    # Apply edits (commented out to avoid actually creating files in test)
    # results = editor.apply_all(edits)
    # print(f"\nResults: {results}")
