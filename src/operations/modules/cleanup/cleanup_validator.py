"""
Cleanup Validator - Pre-execution validation

Validates proposed cleanup actions to ensure CORTEX functionality
is not compromised.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
import subprocess
import importlib
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, field

from .critical_file_detector import CriticalFileDetector, ImportInfo

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a validation error"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # import_dependency, test_discovery, entry_point, health
    message: str
    file: Path
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of validation checks"""
    passed: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    validation_time: float = 0.0
    
    @property
    def critical_errors(self) -> List[ValidationError]:
        """Get only critical errors"""
        return [e for e in self.errors if e.severity == 'CRITICAL']
    
    @property
    def has_critical_errors(self) -> bool:
        """Check if any critical errors"""
        return len(self.critical_errors) > 0


class CleanupValidator:
    """Validate cleanup operations before execution"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.detector = CriticalFileDetector(project_root)
    
    def validate_proposed_cleanup(self, manifest: Dict[str, Any]) -> ValidationResult:
        """
        Validate entire cleanup manifest.
        
        Args:
            manifest: Cleanup manifest with proposed_actions
        
        Returns:
            ValidationResult with pass/fail and details
        """
        import time
        start_time = time.time()
        
        logger.info("Starting cleanup validation...")
        
        errors = []
        warnings = []
        
        proposed_actions = manifest.get('proposed_actions', [])
        files_to_delete = [
            Path(action['file']) for action in proposed_actions
            if action.get('action') == 'delete'
        ]
        
        # 1. Import dependency validation
        logger.info("  1. Validating import dependencies...")
        import_errors = self._validate_imports(files_to_delete)
        errors.extend(import_errors)
        
        # 2. Critical file protection
        logger.info("  2. Checking critical file protection...")
        critical_errors = self._validate_critical_files(files_to_delete)
        errors.extend(critical_errors)
        
        # 3. Test discovery validation
        logger.info("  3. Validating test discovery...")
        test_errors = self._validate_test_discovery(files_to_delete)
        errors.extend(test_errors)
        
        # 4. Entry point validation
        logger.info("  4. Validating entry points...")
        entry_errors = self._validate_entry_points()
        errors.extend(entry_errors)
        
        validation_time = time.time() - start_time
        
        result = ValidationResult(
            passed=len([e for e in errors if e.severity == 'CRITICAL']) == 0,
            errors=errors,
            warnings=warnings,
            validation_time=validation_time
        )
        
        logger.info(f"Validation complete in {validation_time:.2f}s: "
                   f"{'PASSED' if result.passed else 'FAILED'}")
        
        return result
    
    def _validate_imports(self, files_to_delete: List[Path]) -> List[ValidationError]:
        """Check if any imports reference files to be deleted"""
        errors = []
        
        for file_path in files_to_delete:
            if not file_path.suffix == '.py':
                continue
            
            # Find all files that import this one
            importers = self.detector.find_importers(file_path)
            
            if importers:
                errors.append(ValidationError(
                    severity='CRITICAL',
                    category='import_dependency',
                    message=f'File imported by {len(importers)} modules',
                    file=file_path,
                    details={
                        'importers': [
                            {
                                'file': str(imp.file_path.relative_to(self.project_root)),
                                'line': imp.line_number
                            }
                            for imp in importers
                        ]
                    }
                ))
        
        return errors
    
    def _validate_critical_files(self, files_to_delete: List[Path]) -> List[ValidationError]:
        """Check if any critical files would be deleted"""
        errors = []
        
        critical_files = self.detector.detect_critical_files()
        
        for file_path in files_to_delete:
            if file_path in critical_files:
                errors.append(ValidationError(
                    severity='CRITICAL',
                    category='critical_file_protection',
                    message='File is critical to CORTEX operation',
                    file=file_path,
                    details={
                        'reason': 'File is in protected directory or import chain'
                    }
                ))
        
        return errors
    
    def _validate_test_discovery(self, files_to_delete: List[Path]) -> List[ValidationError]:
        """Check if test discovery would be affected"""
        errors = []
        
        # Check if any test files would be deleted
        test_files = [f for f in files_to_delete if 'test' in f.name.lower()]
        
        if test_files:
            errors.append(ValidationError(
                severity='HIGH',
                category='test_discovery',
                message=f'{len(test_files)} test files would be deleted',
                file=test_files[0],  # Representative file
                details={
                    'test_files': [str(f.relative_to(self.project_root)) for f in test_files]
                }
            ))
        
        return errors
    
    def _validate_entry_points(self) -> List[ValidationError]:
        """Check if entry points can still be imported"""
        errors = []
        
        critical_imports = [
            'src.main',
            'src.entry_point.cortex_entry',
            'src.cortex_agents.intent_router',
            'src.operations.base_operation_module'
        ]
        
        for module_name in critical_imports:
            try:
                # Try importing
                importlib.import_module(module_name)
            except ImportError as e:
                errors.append(ValidationError(
                    severity='CRITICAL',
                    category='entry_point',
                    message=f'Entry point import failed: {module_name}',
                    file=self.project_root / module_name.replace('.', '/') + '.py',
                    details={'error': str(e)}
                ))
        
        return errors
