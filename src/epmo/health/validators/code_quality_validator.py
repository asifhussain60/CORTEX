"""
CORTEX 3.0 - Code Quality Validator
===================================

Validates code quality metrics for EPMOs including:
- Cyclomatic complexity
- Function/class size
- Naming conventions
- Code style compliance
- Import organization

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import List, Dict, Any
from pathlib import Path
import ast

from .base_validator import BaseValidator
from ..validation_suite import ValidationResult, HealthDimension, ValidationSeverity


class CodeQualityValidator(BaseValidator):
    """Validates code quality metrics for EPMOs."""
    
    def get_dimension(self) -> HealthDimension:
        """Get the health dimension this validator assesses."""
        return HealthDimension.CODE_QUALITY
    
    def validate(self, epmo_path: Path, project_root: Path) -> List[ValidationResult]:
        """Perform code quality validation checks."""
        results = []
        python_files = self.get_python_files(epmo_path)
        
        if not python_files:
            return [self.create_result(
                "no_python_files",
                0.0,
                "No Python files found to validate",
                ValidationSeverity.HIGH
            )]
        
        # Aggregate metrics
        total_complexity = 0
        total_functions = 0
        total_classes = 0
        naming_violations = 0
        large_files = 0
        total_files = len(python_files)
        
        for file_path in python_files:
            tree = self.analyze_python_file(file_path)
            if not tree:
                continue
            
            # File size check
            file_size_kb = self.get_file_size_kb(file_path)
            if file_size_kb > 500:  # Large file threshold
                large_files += 1
            
            # Analyze functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_functions += 1
                    complexity = self.calculate_complexity(node)
                    total_complexity += complexity
                    
                    # Check naming convention
                    if not self.check_naming_convention(node.name, "snake_case"):
                        naming_violations += 1
                
                elif isinstance(node, ast.ClassDef):
                    total_classes += 1
                    
                    # Check naming convention
                    if not self.check_naming_convention(node.name, "PascalCase"):
                        naming_violations += 1
        
        # Calculate scores and create results
        results.extend(self._evaluate_complexity(total_complexity, total_functions))
        results.extend(self._evaluate_file_sizes(large_files, total_files))
        results.extend(self._evaluate_naming_conventions(naming_violations, total_functions + total_classes))
        results.extend(self._evaluate_code_organization(python_files))
        
        return results
    
    def _evaluate_complexity(self, total_complexity: int, total_functions: int) -> List[ValidationResult]:
        """Evaluate cyclomatic complexity metrics."""
        if total_functions == 0:
            return [self.create_result(
                "complexity_no_functions",
                1.0,
                "No functions found to analyze complexity",
                ValidationSeverity.INFO
            )]
        
        avg_complexity = total_complexity / total_functions
        
        # Scoring: 1-5 = excellent, 6-10 = good, 11-15 = fair, 16+ = poor
        if avg_complexity <= 5:
            score = 1.0
            message = f"Excellent complexity: {avg_complexity:.1f} avg (≤5 target)"
            severity = ValidationSeverity.INFO
        elif avg_complexity <= 10:
            score = 0.8
            message = f"Good complexity: {avg_complexity:.1f} avg (6-10 range)"
            severity = ValidationSeverity.LOW
        elif avg_complexity <= 15:
            score = 0.6
            message = f"Fair complexity: {avg_complexity:.1f} avg (11-15 range)"
            severity = ValidationSeverity.MEDIUM
        else:
            score = 0.3
            message = f"High complexity: {avg_complexity:.1f} avg (>15, refactor needed)"
            severity = ValidationSeverity.HIGH
        
        return [self.create_result(
            "cyclomatic_complexity",
            score,
            message,
            severity,
            {
                "average_complexity": avg_complexity,
                "total_complexity": total_complexity,
                "total_functions": total_functions,
                "threshold": 10
            }
        )]
    
    def _evaluate_file_sizes(self, large_files: int, total_files: int) -> List[ValidationResult]:
        """Evaluate file size distribution."""
        large_file_ratio = large_files / total_files if total_files > 0 else 0
        
        if large_file_ratio == 0:
            score = 1.0
            message = "Excellent file sizes: No files >500KB"
            severity = ValidationSeverity.INFO
        elif large_file_ratio <= 0.2:  # ≤20% large files
            score = 0.8
            message = f"Good file sizes: {large_files}/{total_files} files >500KB"
            severity = ValidationSeverity.LOW
        elif large_file_ratio <= 0.4:  # ≤40% large files
            score = 0.6
            message = f"Fair file sizes: {large_files}/{total_files} files >500KB"
            severity = ValidationSeverity.MEDIUM
        else:
            score = 0.3
            message = f"Large files detected: {large_files}/{total_files} files >500KB"
            severity = ValidationSeverity.HIGH
        
        return [self.create_result(
            "file_sizes",
            score,
            message,
            severity,
            {
                "large_files": large_files,
                "total_files": total_files,
                "large_file_ratio": large_file_ratio,
                "threshold_kb": 500
            }
        )]
    
    def _evaluate_naming_conventions(self, violations: int, total_items: int) -> List[ValidationResult]:
        """Evaluate naming convention compliance."""
        if total_items == 0:
            return [self.create_result(
                "naming_conventions_no_items",
                1.0,
                "No functions or classes found to check naming",
                ValidationSeverity.INFO
            )]
        
        compliance_ratio = (total_items - violations) / total_items
        
        if violations == 0:
            score = 1.0
            message = "Excellent naming: All items follow conventions"
            severity = ValidationSeverity.INFO
        elif compliance_ratio >= 0.9:  # ≥90% compliance
            score = 0.9
            message = f"Good naming: {violations}/{total_items} violations"
            severity = ValidationSeverity.LOW
        elif compliance_ratio >= 0.8:  # ≥80% compliance
            score = 0.7
            message = f"Fair naming: {violations}/{total_items} violations"
            severity = ValidationSeverity.MEDIUM
        else:
            score = 0.5
            message = f"Poor naming: {violations}/{total_items} violations"
            severity = ValidationSeverity.HIGH
        
        return [self.create_result(
            "naming_conventions",
            score,
            message,
            severity,
            {
                "violations": violations,
                "total_items": total_items,
                "compliance_ratio": compliance_ratio
            }
        )]
    
    def _evaluate_code_organization(self, python_files: List[Path]) -> List[ValidationResult]:
        """Evaluate code organization and structure."""
        results = []
        
        # Check for __init__.py files in packages
        package_dirs = set()
        init_files = set()
        
        for file_path in python_files:
            if file_path.name == "__init__.py":
                init_files.add(file_path.parent)
            else:
                package_dirs.add(file_path.parent)
        
        # Calculate package organization score
        if package_dirs:
            missing_init = package_dirs - init_files
            organization_score = 1.0 - (len(missing_init) / len(package_dirs))
        else:
            organization_score = 1.0  # Single file modules are fine
        
        if organization_score >= 0.9:
            score = 1.0
            message = "Excellent organization: Proper package structure"
            severity = ValidationSeverity.INFO
        elif organization_score >= 0.8:
            score = 0.8
            message = f"Good organization: {len(missing_init)} missing __init__.py files"
            severity = ValidationSeverity.LOW
        else:
            score = 0.6
            message = f"Poor organization: {len(missing_init)} missing __init__.py files"
            severity = ValidationSeverity.MEDIUM
        
        results.append(self.create_result(
            "code_organization",
            score,
            message,
            severity,
            {
                "package_dirs": len(package_dirs),
                "init_files": len(init_files),
                "missing_init": len(missing_init)
            }
        ))
        
        return results