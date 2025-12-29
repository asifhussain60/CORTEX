"""
CORTEX 3.0 - Base Validator Interface
=====================================

Base class for all EPMO health dimension validators.
Provides common interface and utility methods for validation logic.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
import logging

from ..validation_suite import ValidationResult, HealthDimension, ValidationSeverity

logger = logging.getLogger(__name__)


class BaseValidator(ABC):
    """Base class for all EPMO health validators."""
    
    def __init__(self):
        """Initialize validator."""
        self.name = self.__class__.__name__
    
    @abstractmethod
    def get_dimension(self) -> HealthDimension:
        """Get the health dimension this validator assesses."""
        pass
    
    @abstractmethod
    def validate(self, epmo_path: Path, project_root: Path) -> List[ValidationResult]:
        """
        Perform validation checks for this dimension.
        
        Args:
            epmo_path: Path to EPMO module being validated
            project_root: Root path of CORTEX project
            
        Returns:
            List of validation results
        """
        pass
    
    def create_result(
        self,
        check_name: str,
        score: float,
        message: str,
        severity: ValidationSeverity = ValidationSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        max_score: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Create a validation result for this dimension.
        
        Args:
            check_name: Name of the validation check
            score: Score from 0.0 to max_score
            message: Human-readable description
            severity: Issue severity level
            details: Optional additional details
            max_score: Maximum possible score (default 1.0)
            metadata: Optional metadata dictionary
            
        Returns:
            ValidationResult instance
        """
        if metadata is None:
            metadata = {'dimension': self.get_dimension(), 'check_id': check_name}
        else:
            metadata = {**metadata, 'dimension': self.get_dimension(), 'check_id': check_name}
            
        return ValidationResult(
            dimension=self.get_dimension(),
            check_name=check_name,
            severity=severity,
            score=score,
            max_score=max_score,
            message=message,
            details=details,
            metadata=metadata
        )
    
    def analyze_python_file(self, file_path: Path) -> Optional[ast.AST]:
        """
        Parse Python file into AST for analysis.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            AST tree or None if parsing failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return ast.parse(content, filename=str(file_path))
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return None
    
    def parse_python_file(self, file_path: Path) -> Optional[ast.AST]:
        """Parse a Python file into an AST (alias for analyze_python_file)."""
        return self.analyze_python_file(file_path)
    
    def get_file_size_kb(self, file_path: Path) -> float:
        """Get file size in kilobytes."""
        try:
            size_bytes = file_path.stat().st_size
            return size_bytes / 1024.0
        except (OSError, FileNotFoundError):
            return 0.0
    
    def get_python_files(self, path: Path) -> List[Path]:
        """
        Get all Python files in a path (file or directory).
        
        Args:
            path: Path to file or directory
            
        Returns:
            List of Python file paths
        """
        if path.is_file() and path.suffix == '.py':
            return [path]
        elif path.is_dir():
            return list(path.glob('**/*.py'))
        else:
            return []
    
    def count_lines_of_code(self, file_path: Path) -> Dict[str, int]:
        """
        Count various line metrics in a Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Dictionary with line counts
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            blank_lines = sum(1 for line in lines if not line.strip())
            comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
            code_lines = total_lines - blank_lines - comment_lines
            
            return {
                'total': total_lines,
                'code': code_lines,
                'blank': blank_lines,
                'comment': comment_lines,
                'comment_ratio': comment_lines / total_lines if total_lines > 0 else 0.0
            }
        except Exception as e:
            logger.warning(f"Failed to count lines in {file_path}: {e}")
            return {
                'total': 0,
                'code': 0,
                'blank': 0,
                'comment': 0,
                'comment_ratio': 0.0
            }
    
    def find_docstring(self, node: ast.AST) -> Optional[str]:
        """
        Extract docstring from AST node.
        
        Args:
            node: AST node (module, class, or function)
            
        Returns:
            Docstring text or None
        """
        if (hasattr(node, 'body') and 
            node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            return node.body[0].value.value
        return None
    
    def calculate_complexity(self, node: ast.AST) -> int:
        """
        Calculate cyclomatic complexity of AST node.
        
        Args:
            node: AST node to analyze
            
        Returns:
            Complexity score (1 = simple, higher = more complex)
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Decision points that increase complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.Lambda):
                complexity += 1
        
        return complexity
    
    def check_naming_convention(self, name: str, convention: str = "snake_case") -> bool:
        """
        Check if name follows naming convention.
        
        Args:
            name: Name to check
            convention: Naming convention ('snake_case', 'camelCase', 'PascalCase')
            
        Returns:
            True if name follows convention
        """
        if convention == "snake_case":
            return bool(re.match(r'^[a-z_][a-z0-9_]*$', name))
        elif convention == "camelCase":
            return bool(re.match(r'^[a-z][a-zA-Z0-9]*$', name))
        elif convention == "PascalCase":
            return bool(re.match(r'^[A-Z][a-zA-Z0-9]*$', name))
        else:
            return True  # Unknown convention, assume valid
    
    def get_file_size_kb(self, file_path: Path) -> float:
        """Get file size in kilobytes."""
        try:
            return file_path.stat().st_size / 1024.0
        except Exception:
            return 0.0