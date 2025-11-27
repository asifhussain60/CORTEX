"""
CORTEX 3.0 - Documentation Validator
====================================

Validates documentation quality and completeness for EPMOs.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import List
from pathlib import Path
import ast

from .base_validator import BaseValidator
from ..validation_suite import ValidationResult, HealthDimension, ValidationSeverity


class DocumentationValidator(BaseValidator):
    """Validates documentation quality for EPMOs."""
    
    def get_dimension(self) -> HealthDimension:
        return HealthDimension.DOCUMENTATION
    
    def validate(self, epmo_path: Path, project_root: Path) -> List[ValidationResult]:
        """Perform documentation validation checks."""
        results = []
        python_files = self.get_python_files(epmo_path)
        
        if not python_files:
            return [self.create_result("no_files", 0.0, "No files to validate")]
        
        # Count docstrings
        total_functions = 0
        documented_functions = 0
        total_classes = 0
        documented_classes = 0
        
        for file_path in python_files:
            tree = self.analyze_python_file(file_path)
            if not tree:
                continue
            
            # Module docstring
            module_docstring = self.find_docstring(tree)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    total_functions += 1
                    if self.find_docstring(node):
                        documented_functions += 1
                elif isinstance(node, ast.ClassDef):
                    total_classes += 1
                    if self.find_docstring(node):
                        documented_classes += 1
        
        # Calculate documentation coverage
        total_items = total_functions + total_classes
        documented_items = documented_functions + documented_classes
        
        coverage = documented_items / total_items if total_items > 0 else 1.0
        
        if coverage >= 0.8:
            score = 1.0
            severity = ValidationSeverity.INFO
            message = f"Excellent documentation: {coverage:.1%} coverage"
        elif coverage >= 0.6:
            score = 0.7
            severity = ValidationSeverity.MEDIUM
            message = f"Good documentation: {coverage:.1%} coverage"
        else:
            score = 0.4
            severity = ValidationSeverity.HIGH
            message = f"Poor documentation: {coverage:.1%} coverage"
        
        results.append(self.create_result(
            "docstring_coverage",
            score,
            message,
            severity,
            {
                "coverage": coverage,
                "documented_items": documented_items,
                "total_items": total_items
            }
        ))
        
        return results