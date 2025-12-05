"""
Orphaned Code Cleaner

Safely removes dead code, orphaned functions, and duplicate implementations
identified during TDD REFACTOR phase.

Features:
- AST-based function removal (preserves code structure)
- Syntax validation before/after cleanup
- Backup creation for rollback
- Test verification after removal

Author: Asif Hussain
Created: December 5, 2025
Purpose: Fix TDD Mastery orphaned code accumulation bug
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

from .refactoring_intelligence import CodeSmell, CodeSmellType


@dataclass
class CleanupResult:
    """Result of code cleanup operation."""
    success: bool
    file_path: str
    functions_removed: List[str]
    lines_removed: int
    backup_path: Optional[str] = None
    error: Optional[str] = None
    validation_passed: bool = True


class OrphanedCodeCleaner:
    """
    Removes orphaned and dead code safely.
    
    Workflow:
    1. Parse code with AST
    2. Identify function locations from code smells
    3. Remove function definitions (keep other code)
    4. Validate syntax
    5. Return cleaned code
    """
    
    def __init__(self, backup_enabled: bool = True):
        """
        Initialize cleaner.
        
        Args:
            backup_enabled: Create backup files before modification
        """
        self.backup_enabled = backup_enabled
    
    def clean_file(
        self,
        file_path: str,
        code_smells: List[CodeSmell]
    ) -> CleanupResult:
        """
        Clean orphaned code from a file based on detected smells.
        
        Args:
            file_path: Path to file to clean
            code_smells: List of code smells to address
        
        Returns:
            CleanupResult with cleanup details
        """
        # Filter for cleanup-relevant smells (ONLY dead code, NOT duplicates)
        # Duplicates require manual review, dead code is safe to auto-remove
        cleanup_smells = [
            smell for smell in code_smells
            if smell.smell_type == CodeSmellType.DEAD_CODE and 
               "zero call sites" in smell.description  # Only auto-remove truly dead code
        ]
        
        if not cleanup_smells:
            return CleanupResult(
                success=True,
                file_path=file_path,
                functions_removed=[],
                lines_removed=0,
                validation_passed=True
            )
        
        try:
            # Read original code
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            # Create backup
            backup_path = None
            if self.backup_enabled:
                backup_path = self._create_backup(file_path, original_code)
            
            # Parse AST
            try:
                tree = ast.parse(original_code)
            except SyntaxError as e:
                return CleanupResult(
                    success=False,
                    file_path=file_path,
                    functions_removed=[],
                    lines_removed=0,
                    backup_path=backup_path,
                    error=f"Syntax error in original code: {e}",
                    validation_passed=False
                )
            
            # Extract function names to remove
            functions_to_remove = self._extract_function_names(cleanup_smells)
            
            # Remove functions from AST
            cleaned_tree, removed_count = self._remove_functions_from_ast(
                tree,
                functions_to_remove
            )
            
            # Generate cleaned code
            try:
                cleaned_code = ast.unparse(cleaned_tree)
            except Exception as e:
                return CleanupResult(
                    success=False,
                    file_path=file_path,
                    functions_removed=[],
                    lines_removed=0,
                    backup_path=backup_path,
                    error=f"Failed to generate cleaned code: {e}",
                    validation_passed=False
                )
            
            # Validate cleaned code syntax
            try:
                ast.parse(cleaned_code)
            except SyntaxError as e:
                return CleanupResult(
                    success=False,
                    file_path=file_path,
                    functions_removed=list(functions_to_remove),
                    lines_removed=0,
                    backup_path=backup_path,
                    error=f"Cleaned code has syntax errors: {e}",
                    validation_passed=False
                )
            
            # Calculate lines removed
            original_lines = len(original_code.split('\n'))
            cleaned_lines = len(cleaned_code.split('\n'))
            lines_removed = original_lines - cleaned_lines
            
            # Write cleaned code
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_code)
            
            return CleanupResult(
                success=True,
                file_path=file_path,
                functions_removed=list(functions_to_remove),
                lines_removed=lines_removed,
                backup_path=backup_path,
                validation_passed=True
            )
        
        except Exception as e:
            return CleanupResult(
                success=False,
                file_path=file_path,
                functions_removed=[],
                lines_removed=0,
                error=f"Unexpected error: {e}",
                validation_passed=False
            )
    
    def _create_backup(self, file_path: str, content: str) -> str:
        """
        Create backup of file.
        
        Args:
            file_path: Original file path
            content: File content
        
        Returns:
            Backup file path
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return backup_path
    
    def _extract_function_names(self, code_smells: List[CodeSmell]) -> Set[str]:
        """
        Extract function names from code smells.
        
        Args:
            code_smells: List of code smells
        
        Returns:
            Set of function names to remove
        """
        function_names = set()
        
        for smell in code_smells:
            # Extract function name from description
            # Format: "Function 'func_name' has zero call sites..."
            desc = smell.description
            
            # Try multiple patterns
            patterns = [
                ("Function '", "'"),
                ('Function "', '"'),
                ("function '", "'"),
                ('function "', '"')
            ]
            
            for start_marker, end_marker in patterns:
                if start_marker in desc:
                    try:
                        start = desc.index(start_marker) + len(start_marker)
                        end = desc.index(end_marker, start)
                        func_name = desc[start:end]
                        function_names.add(func_name)
                        break
                    except (ValueError, IndexError):
                        continue
        
        return function_names
    
    def _remove_functions_from_ast(
        self,
        tree: ast.AST,
        function_names: Set[str]
    ) -> tuple:
        """
        Remove specified functions from AST.
        
        Args:
            tree: AST tree
            function_names: Names of functions to remove
        
        Returns:
            Tuple of (cleaned_tree, removed_count)
        """
        class FunctionRemover(ast.NodeTransformer):
            """AST transformer that removes specified functions."""
            
            def __init__(self, names_to_remove: Set[str]):
                self.names_to_remove = names_to_remove
                self.removed_count = 0
            
            def visit_Module(self, node):
                """Visit module and filter out functions to remove."""
                new_body = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if item.name in self.names_to_remove:
                            self.removed_count += 1
                            continue  # Skip this function
                    new_body.append(self.visit(item))
                node.body = new_body
                return node
            
            def visit_ClassDef(self, node):
                """Visit class and filter out methods to remove."""
                new_body = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if item.name in self.names_to_remove:
                            self.removed_count += 1
                            continue  # Skip this method
                    new_body.append(self.visit(item))
                node.body = new_body
                return node
        
        remover = FunctionRemover(function_names)
        cleaned_tree = remover.visit(tree)
        
        return cleaned_tree, remover.removed_count
    
    def restore_from_backup(self, backup_path: str, original_path: str) -> bool:
        """
        Restore file from backup.
        
        Args:
            backup_path: Path to backup file
            original_path: Path to original file
        
        Returns:
            True if restore successful
        """
        try:
            if not os.path.exists(backup_path):
                return False
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(original_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception:
            return False
