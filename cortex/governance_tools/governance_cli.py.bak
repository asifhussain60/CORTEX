"""Governance CLI - Command-line interface for governance operations.

Author: CORTEX Framework
"""

import ast
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class CommandType(Enum):
    """CLI command types."""
    CHECK = "check"
    ENFORCE = "enforce"
    REPORT = "report"
    AUDIT = "audit"


@dataclass
class CLICommand:
    """CLI command."""
    name: str
    command_type: CommandType
    args: List[str]
    options: Dict[str, Any]


class GovernanceValidator:
    """Validates code against governance rules."""
    
    def __init__(self):
        """Initialize the validator."""
        self.violations: List[Dict[str, Any]] = []
    
    def validate_type_hints(self, code: str) -> bool:
        """Validate that functions have type hints.
        
        Args:
            code: Python code to validate
            
        Returns:
            True if all functions have return type hints, False otherwise
        """
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.returns is None:
                        return False
            return True
        except SyntaxError:
            return False
    
    def validate_docstrings(self, code: str) -> bool:
        """Validate that code has docstrings.
        
        Args:
            code: Python code to validate
            
        Returns:
            True if docstrings are present
        """
        return '"""' in code or "'''" in code
    
    def validate_paths(self, code: str) -> bool:
        """Validate that no hardcoded absolute paths are used.
        
        Args:
            code: Python code to validate
            
        Returns:
            True if no absolute paths found, False otherwise
        """
        # Check for common absolute path patterns
        absolute_path_patterns = [
            r'/Users/\w+',
            r'C:\\Users\\',
            r'/home/\w+',
        ]
        
        for pattern in absolute_path_patterns:
            if re.search(pattern, code):
                return False
        return True
    
    def validate(self, code: str) -> Dict[str, bool]:
        """Run all validations on code.
        
        Args:
            code: Python code to validate
            
        Returns:
            Dictionary with validation results
        """
        return {
            "type_hints": self.validate_type_hints(code),
            "docstrings": self.validate_docstrings(code),
            "paths": self.validate_paths(code)
        }


class GovernanceCLI:
    """Command-line interface for governance."""
    
    def __init__(self):
        """Initialize CLI."""
        self.commands: Dict[str, CLICommand] = {}
        self.validator = GovernanceValidator()
    
    def register_command(self, command: CLICommand) -> None:
        """Register a CLI command.
        
        Args:
            command: The command to register
        """
        self.commands[command.name] = command
    
    def execute(self, command_name: str, args: Optional[List[str]] = None) -> Any:
        """Execute a command.
        
        Args:
            command_name: Name of the command to execute
            args: Optional command arguments
            
        Returns:
            Command execution result
            
        Raises:
            ValueError: If command not found
        """
        command = self.commands.get(command_name)
        if not command:
            raise ValueError(f"Unknown command: {command_name}")
        
        return {"status": "success", "command": command_name}
    
    def report_violations(self) -> List[Dict[str, Any]]:
        """Get a report of all violations.
        
        Returns:
            List of violation dictionaries
        """
        return self.validator.violations
    
    def help(self) -> str:
        """Get help text.
        
        Returns:
            Help text describing available commands
        """
        lines = ["Available commands:"]
        for name, cmd in self.commands.items():
            lines.append(f"  {name} - {cmd.command_type.value}")
        return "\n".join(lines)

        return "Governance CLI - Available commands: " + ", ".join(self.commands.keys())


__all__ = ["CommandType", "CLICommand", "GovernanceCLI"]
