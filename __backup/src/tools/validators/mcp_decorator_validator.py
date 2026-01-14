"""
CORTEX 6.0 - MCP Decorator Validator

Implements CORE-024: Static analysis validator for @mcp_tool decorator enforcement.
Scans src/mcp/*_tools.py for undecorated functions to prevent registration drift.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
Version: 1.0.0
Created: 2026-01-10
AC-ID: AC-MCP-PROTOCOL-001
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class Violation:
    """MCP decorator violation"""
    file: Path
    line: int
    function_name: str
    
    def __str__(self):
        return f"{self.file}:{self.line} - {self.function_name}()"


class MCPDecoratorValidator:
    """
    Validates that all MCP tools use @mcp_tool decorator.
    
    Usage:
        validator = MCPDecoratorValidator()
        violations = validator.check_all()
        
        if violations:
            print(f"Found {len(violations)} violations")
            sys.exit(1)
    """
    
    def __init__(self, workspace_root: Path = None):
        """
        Initialize validator.
        
        Args:
            workspace_root: Path to CORTEX workspace (defaults to cwd)
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.tools_dir = self.workspace_root / "src" / "mcp"
    
    def check_all(self) -> List[Violation]:
        """
        Check all tool modules for decorator violations.
        
        Returns:
            List of violations found
        """
        violations = []
        
        tool_files = list(self.tools_dir.glob("*_tools.py"))
        
        for file in tool_files:
            file_violations = self.check_file(file)
            violations.extend(file_violations)
        
        return violations
    
    def check_file(self, file: Path) -> List[Violation]:
        """
        Check single file for decorator violations.
        
        Args:
            file: Path to Python file
        
        Returns:
            List of violations in this file
        """
        violations = []
        
        try:
            with open(file) as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip private functions
                    if node.name.startswith('_'):
                        continue
                    
                    # Check if function has @mcp_tool decorator
                    has_mcp_decorator = self._has_mcp_decorator(node)
                    
                    if not has_mcp_decorator:
                        violations.append(Violation(
                            file=file.relative_to(self.workspace_root),
                            line=node.lineno,
                            function_name=node.name
                        ))
        
        except SyntaxError as e:
            print(f"⚠️  Syntax error in {file}: {e}", file=sys.stderr)
        
        except Exception as e:
            print(f"⚠️  Error checking {file}: {e}", file=sys.stderr)
        
        return violations
    
    def _has_mcp_decorator(self, node: ast.FunctionDef) -> bool:
        """
        Check if function has @mcp_tool decorator.
        
        Args:
            node: Function definition AST node
        
        Returns:
            True if decorated with @mcp_tool
        """
        for decorator in node.decorator_list:
            # Handle: @mcp_tool
            if isinstance(decorator, ast.Name) and decorator.id == 'mcp_tool':
                return True
            
            # Handle: @mcp_decorator.mcp_tool
            if isinstance(decorator, ast.Attribute) and decorator.attr == 'mcp_tool':
                return True
            
            # Handle: @mcp_tool(...)
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name) and decorator.func.id == 'mcp_tool':
                    return True
                if isinstance(decorator.func, ast.Attribute) and decorator.func.attr == 'mcp_tool':
                    return True
        
        return False
    
    def print_violations(self, violations: List[Violation]):
        """
        Print violations in human-readable format.
        
        Args:
            violations: List of violations to print
        """
        if not violations:
            print("✅ CORE-024 PASSED: All MCP tools properly decorated")
            return
        
        print("❌ CORE-024 VIOLATION: Undecorated MCP tools found\n")
        
        for v in violations:
            print(f"   {v}")
        
        print(f"\n📊 Total violations: {len(violations)}")
        print("\n📖 Fix: Add @mcp_tool decorator")
        print("   See: cortex-brain/tier2/mcp-tool-creation-protocol.md")
        print("   Example:")
        print("     from src.mcp.mcp_decorator import mcp_tool")
        print("     ")
        print("     @mcp_tool(")
        print("         name='cortex_<function_name>',")
        print("         description='...',")
        print("         category='audit|governance|planning|...',")
        print("         parameters={...}")
        print("     )")
        print("     def your_function(...):")
        print("         pass")


def main():
    """CLI entry point for pre-commit hook"""
    validator = MCPDecoratorValidator()
    violations = validator.check_all()
    
    validator.print_violations(violations)
    
    if violations:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
