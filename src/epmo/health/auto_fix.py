"""
CORTEX 3.0 - Auto-Fix Engine
============================

Automated remediation for EPMO health issues.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import ast
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from .validation_suite import ValidationResult, ValidationSeverity, HealthDimension


class AutoFixEngine:
    """Automated remediation engine for EPMO health issues."""
    
    def __init__(self):
        self.supported_fixes = {
            HealthDimension.CODE_QUALITY: [
                'add_missing_docstrings',
                'simplify_complex_functions',
                'rename_poorly_named_variables'
            ],
            HealthDimension.DOCUMENTATION: [
                'generate_missing_docstrings',
                'update_outdated_documentation'
            ],
            HealthDimension.TEST_COVERAGE: [
                'generate_missing_tests',
                'improve_test_assertions'
            ],
            HealthDimension.MAINTAINABILITY: [
                'extract_duplicate_code',
                'add_error_handling',
                'standardize_naming'
            ]
        }
    
    def can_auto_fix(self, result: ValidationResult) -> bool:
        """Check if a validation result can be auto-fixed."""
        dimension = result.metadata.get('dimension')
        fix_type = result.metadata.get('auto_fix_type')
        
        if not dimension or not fix_type:
            return False
        
        return fix_type in self.supported_fixes.get(dimension, [])
    
    def apply_auto_fix(self, result: ValidationResult, file_path: Path) -> bool:
        """Apply automatic fix for a validation issue."""
        fix_type = result.metadata.get('auto_fix_type')
        
        if not fix_type or not self.can_auto_fix(result):
            return False
        
        try:
            if fix_type == 'add_missing_docstrings':
                return self._add_missing_docstrings(file_path)
            elif fix_type == 'generate_missing_tests':
                return self._generate_missing_tests(file_path)
            elif fix_type == 'add_error_handling':
                return self._add_error_handling(file_path)
            elif fix_type == 'standardize_naming':
                return self._standardize_naming(file_path)
            
            return False
        except Exception:
            return False
    
    def _add_missing_docstrings(self, file_path: Path) -> bool:
        """Add missing docstrings to functions and classes."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Find functions and classes without docstrings
            modified = False
            lines = content.split('\n')
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        # Insert basic docstring
                        indent = self._get_indentation(lines[node.lineno - 1])
                        docstring = f'{indent}    """TODO: Add description."""'
                        lines.insert(node.lineno, docstring)
                        modified = True
            
            if modified:
                with open(file_path, 'w') as f:
                    f.write('\n'.join(lines))
                return True
            
            return False
        except Exception:
            return False
    
    def _generate_missing_tests(self, file_path: Path) -> bool:
        """Generate basic test templates for uncovered functions."""
        try:
            # Create corresponding test file if it doesn't exist
            test_file = self._get_test_file_path(file_path)
            
            if test_file.exists():
                return False  # Tests already exist
            
            # Generate basic test template
            module_name = file_path.stem
            test_content = f'''"""
Tests for {module_name}.

Auto-generated test template.
"""

import pytest
from {module_name} import *


def test_{module_name}_placeholder():
    """Placeholder test - replace with actual tests."""
    assert True  # Replace with actual test logic
'''
            
            test_file.parent.mkdir(parents=True, exist_ok=True)
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            return True
        except Exception:
            return False
    
    def _add_error_handling(self, file_path: Path) -> bool:
        """Add basic error handling to functions that lack it."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            lines = content.split('\n')
            
            modified = False
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has any error handling
                    has_try_except = any(isinstance(n, ast.Try) for n in ast.walk(node))
                    
                    if not has_try_except and len(node.body) > 1:
                        # Add basic try-except wrapper
                        indent = self._get_indentation(lines[node.lineno - 1])
                        
                        # Insert try at function start
                        try_line = f'{indent}    try:'
                        lines.insert(node.lineno, try_line)
                        
                        # Insert except at function end (approximate)
                        except_lines = [
                            f'{indent}    except Exception as e:',
                            f'{indent}        # TODO: Add proper error handling',
                            f'{indent}        raise'
                        ]
                        
                        # Find function end (rough approximation)
                        insert_pos = node.lineno + len(node.body) + 1
                        for line in reversed(except_lines):
                            lines.insert(insert_pos, line)
                        
                        modified = True
            
            if modified:
                with open(file_path, 'w') as f:
                    f.write('\n'.join(lines))
                return True
            
            return False
        except Exception:
            return False
    
    def _standardize_naming(self, file_path: Path) -> bool:
        """Standardize naming conventions (simplified approach)."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Simple replacements for common naming issues
            replacements = {
                'camelCase': 'camel_case',
                'PascalCase': 'pascal_case',
                'SCREAMING_CASE': 'screaming_case'
            }
            
            modified_content = content
            for old, new in replacements.items():
                if old in modified_content and old != new:
                    modified_content = modified_content.replace(old, new)
            
            if modified_content != content:
                with open(file_path, 'w') as f:
                    f.write(modified_content)
                return True
            
            return False
        except Exception:
            return False
    
    def _get_test_file_path(self, source_file: Path) -> Path:
        """Get the corresponding test file path for a source file."""
        # Look for tests directory
        project_root = source_file.parent
        while project_root.parent != project_root:
            tests_dir = project_root / 'tests'
            if tests_dir.exists():
                relative_path = source_file.relative_to(project_root)
                test_path = tests_dir / relative_path.parent / f'test_{source_file.name}'
                return test_path
            project_root = project_root.parent
        
        # Fallback: create tests directory next to source
        return source_file.parent / 'tests' / f'test_{source_file.name}'
    
    def _get_indentation(self, line: str) -> str:
        """Get the indentation of a line."""
        return line[:len(line) - len(line.lstrip())]