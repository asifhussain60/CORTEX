"""
CORTEX 3.0 - Maintainability Validator
======================================

Validates maintainability characteristics of EPMOs.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import ast
from typing import List, Set
from pathlib import Path

from .base_validator import BaseValidator
from ..validation_suite import ValidationResult, HealthDimension, ValidationSeverity


class MaintainabilityValidator(BaseValidator):
    """Validates maintainability characteristics for EPMOs."""
    
    def get_dimension(self) -> HealthDimension:
        return HealthDimension.MAINTAINABILITY
    
    def validate(self, epmo_path: Path, project_root: Path) -> List[ValidationResult]:
        """Perform maintainability validation checks."""
        results = []
        python_files = self.get_python_files(epmo_path)
        
        if not python_files:
            return [self.create_result("no_files", 1.0, "No files to validate")]
        
        # Check code consistency
        consistency_score = self._check_code_consistency(python_files)
        results.append(self.create_result(
            "code_consistency",
            consistency_score,
            f"Code consistency: {consistency_score*100:.1f}%",
            ValidationSeverity.LOW if consistency_score < 0.7 else ValidationSeverity.INFO
        ))
        
        # Check dependency management
        dependency_score = self._check_dependency_management(python_files)
        results.append(self.create_result(
            "dependency_management",
            dependency_score,
            f"Dependency management: {dependency_score*100:.1f}%",
            ValidationSeverity.MEDIUM if dependency_score < 0.6 else ValidationSeverity.INFO
        ))
        
        # Check for code duplication
        duplication_score = self._check_code_duplication(python_files)
        results.append(self.create_result(
            "code_duplication",
            duplication_score,
            f"Code duplication: {(1-duplication_score)*100:.1f}% duplicated",
            ValidationSeverity.MEDIUM if duplication_score < 0.7 else ValidationSeverity.INFO
        ))
        
        # Check error handling consistency
        error_handling_score = self._check_error_handling(python_files)
        results.append(self.create_result(
            "error_handling",
            error_handling_score,
            f"Error handling: {error_handling_score*100:.1f}%",
            ValidationSeverity.LOW if error_handling_score < 0.8 else ValidationSeverity.INFO
        ))
        
        return results
    
    def _check_code_consistency(self, python_files: List[Path]) -> float:
        """Check for consistent coding patterns across files."""
        # Check naming consistency
        naming_patterns = {
            'snake_case_functions': 0,
            'camel_case_functions': 0,
            'snake_case_variables': 0,
            'camel_case_variables': 0
        }
        
        for file_path in python_files:
            tree = self.parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if self._is_snake_case(node.name):
                            naming_patterns['snake_case_functions'] += 1
                        else:
                            naming_patterns['camel_case_functions'] += 1
                    
                    elif isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                if self._is_snake_case(target.id):
                                    naming_patterns['snake_case_variables'] += 1
                                else:
                                    naming_patterns['camel_case_variables'] += 1
        
        # Score based on consistency
        total_functions = naming_patterns['snake_case_functions'] + naming_patterns['camel_case_functions']
        total_variables = naming_patterns['snake_case_variables'] + naming_patterns['camel_case_variables']
        
        if total_functions == 0 and total_variables == 0:
            return 1.0
        
        function_consistency = 0.0
        if total_functions > 0:
            function_consistency = max(
                naming_patterns['snake_case_functions'] / total_functions,
                naming_patterns['camel_case_functions'] / total_functions
            )
        
        variable_consistency = 0.0
        if total_variables > 0:
            variable_consistency = max(
                naming_patterns['snake_case_variables'] / total_variables,
                naming_patterns['camel_case_variables'] / total_variables
            )
        
        return (function_consistency + variable_consistency) / 2
    
    def _check_dependency_management(self, python_files: List[Path]) -> float:
        """Check for proper dependency management."""
        import_counts = {}
        total_imports = 0
        
        for file_path in python_files:
            tree = self.parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        total_imports += 1
                        module_name = self._get_module_name(node)
                        import_counts[module_name] = import_counts.get(module_name, 0) + 1
        
        if total_imports == 0:
            return 1.0
        
        # Score based on import diversity (fewer repeated imports = better)
        unique_imports = len(import_counts)
        diversity_score = unique_imports / total_imports
        return min(1.0, diversity_score * 2)  # Boost for good diversity
    
    def _check_code_duplication(self, python_files: List[Path]) -> float:
        """Check for code duplication using simple heuristics."""
        function_bodies = []
        
        for file_path in python_files:
            tree = self.parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Get function body as string (simplified)
                        body_hash = hash(ast.dump(node))
                        function_bodies.append(body_hash)
        
        if not function_bodies:
            return 1.0
        
        unique_bodies = len(set(function_bodies))
        total_bodies = len(function_bodies)
        
        # Score based on uniqueness
        uniqueness_ratio = unique_bodies / total_bodies
        return uniqueness_ratio
    
    def _check_error_handling(self, python_files: List[Path]) -> float:
        """Check for consistent error handling patterns."""
        total_functions = 0
        functions_with_error_handling = 0
        
        for file_path in python_files:
            tree = self.parse_python_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_functions += 1
                        # Check if function has try/except or raises exceptions
                        if self._has_error_handling(node):
                            functions_with_error_handling += 1
        
        if total_functions == 0:
            return 1.0
        
        error_handling_ratio = functions_with_error_handling / total_functions
        return error_handling_ratio
    
    def _is_snake_case(self, name: str) -> bool:
        """Check if name follows snake_case convention."""
        return '_' in name and name.islower()
    
    def _get_module_name(self, node) -> str:
        """Extract module name from import node."""
        if isinstance(node, ast.Import):
            return node.names[0].name if node.names else "unknown"
        elif isinstance(node, ast.ImportFrom):
            return node.module or "relative"
        return "unknown"
    
    def _has_error_handling(self, node: ast.FunctionDef) -> bool:
        """Check if function has error handling (try/except or raises)."""
        for n in ast.walk(node):
            if isinstance(n, (ast.Try, ast.Raise)):
                return True
        return False