"""
CORTEX 3.0 - Architecture Validator
===================================

Validates architectural adherence of EPMOs.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import ast
from typing import List
from pathlib import Path

from .base_validator import BaseValidator
from ..validation_suite import ValidationResult, HealthDimension, ValidationSeverity


class ArchitectureValidator(BaseValidator):
    """Validates architectural adherence for EPMOs."""
    
    def get_dimension(self) -> HealthDimension:
        return HealthDimension.ARCHITECTURE
    
    def validate(self, epmo_path: Path, project_root: Path) -> List[ValidationResult]:
        """Perform architecture validation checks."""
        results = []
        python_files = self.get_python_files(epmo_path)
        
        if not python_files:
            return [self.create_result("no_files", 1.0, "No files to validate")]
        
        # Check for proper separation of concerns
        separation_score = self._check_separation_of_concerns(epmo_path)
        results.append(self.create_result(
            "separation_of_concerns",
            separation_score,
            f"Separation of concerns: {separation_score*100:.1f}%",
            ValidationSeverity.LOW if separation_score < 0.7 else ValidationSeverity.INFO
        ))
        
        # Check for single responsibility principle
        srp_violations = 0
        total_classes = 0
        
        for file_path in python_files:
            tree = self.parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        total_classes += 1
                        # Check if class has too many methods (SRP violation)
                        method_count = sum(1 for n in ast.walk(node) if isinstance(n, ast.FunctionDef))
                        if method_count > 15:  # Threshold for SRP violation
                            srp_violations += 1
        
        if total_classes > 0:
            srp_score = 1 - (srp_violations / total_classes)
        else:
            srp_score = 1.0
        
        results.append(self.create_result(
            "single_responsibility",
            srp_score,
            f"Single Responsibility Principle: {srp_violations}/{total_classes} violations",
            ValidationSeverity.MEDIUM if srp_violations > 0 else ValidationSeverity.INFO
        ))
        
        # Check for proper interface usage
        interface_score = self._check_interface_usage(python_files)
        results.append(self.create_result(
            "interface_usage",
            interface_score,
            f"Interface usage score: {interface_score*100:.1f}%",
            ValidationSeverity.LOW if interface_score < 0.5 else ValidationSeverity.INFO
        ))
        
        return results
    
    def _check_separation_of_concerns(self, epmo_path: Path) -> float:
        """Check for proper separation of concerns."""
        expected_structure = {
            'operations': 0.3,
            'models': 0.2,
            'health': 0.2,
            'tests': 0.3
        }
        
        actual_structure = {}
        total_files = 0
        
        for category in expected_structure:
            category_path = epmo_path / category
            if category_path.exists():
                file_count = len(list(category_path.rglob("*.py")))
                actual_structure[category] = file_count
                total_files += file_count
        
        if total_files == 0:
            return 1.0
        
        # Calculate deviation from expected structure
        total_deviation = 0
        for category, expected_ratio in expected_structure.items():
            actual_ratio = actual_structure.get(category, 0) / total_files
            deviation = abs(actual_ratio - expected_ratio)
            total_deviation += deviation
        
        # Convert deviation to score (lower deviation = higher score)
        score = max(0.0, 1.0 - (total_deviation / 2.0))
        return score
    
    def _check_interface_usage(self, python_files: List[Path]) -> float:
        """Check for proper interface (ABC) usage."""
        total_classes = 0
        interface_classes = 0
        
        for file_path in python_files:
            tree = self.parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        total_classes += 1
                        # Check if class inherits from ABC or has abstractmethod
                        if self._is_interface_class(node):
                            interface_classes += 1
        
        if total_classes == 0:
            return 1.0
        
        # Score based on ratio of interface classes
        interface_ratio = interface_classes / total_classes
        return min(1.0, interface_ratio * 2)  # Boost for having interfaces
    
    def _is_interface_class(self, node: ast.ClassDef) -> bool:
        """Check if a class is an interface (ABC or has abstract methods)."""
        # Check for ABC base class
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in ['ABC', 'BaseValidator']:
                return True
        
        # Check for abstract methods
        for n in ast.walk(node):
            if isinstance(n, ast.FunctionDef):
                for decorator in n.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod':
                        return True
        
        return False