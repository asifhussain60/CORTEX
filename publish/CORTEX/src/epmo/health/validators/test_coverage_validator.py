"""
CORTEX 3.0 - Test Coverage Validator
====================================

Validates test coverage and test quality for EPMOs.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import List
from pathlib import Path

from .base_validator import BaseValidator
from ..validation_suite import ValidationResult, HealthDimension, ValidationSeverity


class TestCoverageValidator(BaseValidator):
    """Validates test coverage for EPMOs."""
    
    def get_dimension(self) -> HealthDimension:
        return HealthDimension.TEST_COVERAGE
    
    def validate(self, epmo_path: Path, project_root: Path) -> List[ValidationResult]:
        """Perform test coverage validation checks."""
        results = []
        
        # Find source files
        source_files = self.get_python_files(epmo_path)
        
        # Find corresponding test files
        test_files = self._find_test_files(epmo_path, project_root)
        
        # Calculate test coverage ratio
        source_count = len([f for f in source_files if not f.name.startswith('test_')])
        test_count = len(test_files)
        
        if source_count == 0:
            coverage_ratio = 1.0
            message = "No source files to test"
        else:
            coverage_ratio = min(test_count / source_count, 1.0)
            message = f"Test coverage: {test_count}/{source_count} files tested ({coverage_ratio:.1%})"
        
        if coverage_ratio >= 0.8:
            score = 1.0
            severity = ValidationSeverity.INFO
        elif coverage_ratio >= 0.6:
            score = 0.7
            severity = ValidationSeverity.MEDIUM
        else:
            score = 0.4
            severity = ValidationSeverity.HIGH
        
        results.append(self.create_result(
            "test_file_coverage",
            score,
            message,
            severity,
            {
                "coverage_ratio": coverage_ratio,
                "test_files": test_count,
                "source_files": source_count
            }
        ))
        
        return results
    
    def _find_test_files(self, epmo_path: Path, project_root: Path) -> List[Path]:
        """Find test files related to the EPMO."""
        test_files = []
        
        # Look in tests/ directory
        tests_dir = project_root / "tests"
        if tests_dir.exists():
            # Find tests related to this EPMO
            epmo_name = epmo_path.name if epmo_path.is_dir() else epmo_path.stem
            
            for test_file in tests_dir.glob(f"**/*{epmo_name}*test*.py"):
                test_files.append(test_file)
            
            for test_file in tests_dir.glob(f"**/test*{epmo_name}*.py"):
                test_files.append(test_file)
        
        return list(set(test_files))  # Remove duplicates