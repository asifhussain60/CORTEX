"""
CORTEX 3.0 - Performance Validator
==================================

Validates performance characteristics of EPMOs.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import List
from pathlib import Path

from .base_validator import BaseValidator
from ..validation_suite import ValidationResult, HealthDimension, ValidationSeverity


class PerformanceValidator(BaseValidator):
    """Validates performance characteristics for EPMOs."""
    
    def get_dimension(self) -> HealthDimension:
        return HealthDimension.PERFORMANCE
    
    def validate(self, epmo_path: Path, project_root: Path) -> List[ValidationResult]:
        """Perform performance validation checks."""
        results = []
        python_files = self.get_python_files(epmo_path)
        
        if not python_files:
            return [self.create_result("no_files", 1.0, "No files to validate")]
        
        # Check file sizes (performance impact)
        large_files = 0
        total_size_kb = 0
        
        for file_path in python_files:
            size_kb = self.get_file_size_kb(file_path)
            total_size_kb += size_kb
            
            if size_kb > 100:  # Files >100KB may have performance impact
                large_files += 1
        
        avg_size_kb = total_size_kb / len(python_files)
        
        # Score based on average file size
        if avg_size_kb <= 50:
            score = 1.0
            message = f"Excellent performance: {avg_size_kb:.1f}KB avg file size"
            severity = ValidationSeverity.INFO
        elif avg_size_kb <= 100:
            score = 0.8
            message = f"Good performance: {avg_size_kb:.1f}KB avg file size"
            severity = ValidationSeverity.LOW
        else:
            score = 0.6
            message = f"Fair performance: {avg_size_kb:.1f}KB avg file size"
            severity = ValidationSeverity.MEDIUM
        
        results.append(self.create_result(
            "file_size_performance",
            score,
            message,
            severity,
            {
                "average_size_kb": avg_size_kb,
                "total_size_kb": total_size_kb,
                "large_files": large_files,
                "file_count": len(python_files)
            }
        ))
        
        return results