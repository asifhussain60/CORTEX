"""
Phase Validator for TDD Orchestrator
Validates Definition of Ready (DoR) and Definition of Done (DoD) for RED/GREEN/REFACTOR phases

Author: Asif Hussain
Date: December 10, 2025
"""

from dataclasses import dataclass
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of DoR/DoD validation."""
    passed: bool
    errors: List[str]
    warnings: List[str]
    phase: str
    validation_type: str  # "DoR" or "DoD"
    
    def is_valid(self) -> bool:
        """Check if validation passed with no errors."""
        return self.passed and len(self.errors) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'passed': self.passed,
            'errors': self.errors,
            'warnings': self.warnings,
            'phase': self.phase,
            'validation_type': self.validation_type
        }


class PhaseValidator:
    """
    Validates DoR/DoD conditions for TDD phases.
    
    RED Phase DoR:
    - Feature name provided
    - Acceptance criteria defined
    - Test file path determined
    - No existing test file
    - Git working directory clean
    
    RED Phase DoD:
    - Test file created
    - Tests run successfully (fail as expected)
    - Git checkpoint created
    - Metrics recorded
    
    GREEN Phase DoR:
    - RED DoD complete
    - Tests still failing
    - Implementation path determined
    
    GREEN Phase DoD:
    - All tests pass (100%)
    - Coverage ≥ 80%
    - Minimal implementation (no over-engineering)
    - Git checkpoint created
    
    REFACTOR Phase DoR:
    - GREEN DoD complete
    - Tests passing
    - Code smells detected
    
    REFACTOR Phase DoD:
    - Code smells reduced
    - Tests still pass
    - No new complexity added
    - Git checkpoint created
    """
    
    def __init__(self):
        """Initialize phase validator."""
        self.logger = logging.getLogger(f"{__name__}.PhaseValidator")
    
    def validate_red_dor(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate RED phase Definition of Ready.
        
        Args:
            context: Workflow context with feature_name, acceptance_criteria, test_file_path, git_status
        
        Returns:
            ValidationResult with errors/warnings
        """
        errors = []
        warnings = []
        
        # Check feature name
        if not context.get('feature_name'):
            errors.append("Feature name not provided")
        
        # Check acceptance criteria
        if not context.get('acceptance_criteria'):
            errors.append("Acceptance criteria not defined")
        
        # Check test file path
        if not context.get('test_file_path'):
            errors.append("Test file path not determined")
        
        # Check no existing test file
        if context.get('test_file_exists', False):
            errors.append("Test file already exists for this feature")
        
        # Check git status
        if not context.get('git_clean', False):
            warnings.append("Git working directory not clean")
        
        passed = len(errors) == 0
        self.logger.info(f"RED DoR validation: {'PASSED' if passed else 'FAILED'}")
        
        return ValidationResult(
            passed=passed,
            errors=errors,
            warnings=warnings,
            phase="RED",
            validation_type="DoR"
        )
    
    def validate_red_dod(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate RED phase Definition of Done.
        
        Args:
            context: Workflow context with test_file_created, tests_ran, tests_failed, git_checkpoint
        
        Returns:
            ValidationResult with errors/warnings
        """
        errors = []
        warnings = []
        
        # Check test file created
        if not context.get('test_file_created', False):
            errors.append("Test file not created")
        
        # Check tests ran
        if not context.get('tests_ran', False):
            errors.append("Tests did not run")
        
        # Check tests failed correctly (not syntax errors)
        if context.get('tests_ran', False) and not context.get('tests_failed_correctly', False):
            errors.append("Tests did not fail as expected")
        
        # Check git checkpoint
        if not context.get('git_checkpoint_created', False):
            warnings.append("Git checkpoint not created")
        
        # Check metrics recorded
        if not context.get('metrics_recorded', False):
            warnings.append("Metrics not recorded")
        
        passed = len(errors) == 0
        self.logger.info(f"RED DoD validation: {'PASSED' if passed else 'FAILED'}")
        
        return ValidationResult(
            passed=passed,
            errors=errors,
            warnings=warnings,
            phase="RED",
            validation_type="DoD"
        )
    
    def validate_green_dor(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate GREEN phase DoR."""
        errors = []
        warnings = []
        
        # Check RED DoD complete
        if not context.get('red_dod_complete', False):
            errors.append("RED DoD not complete")
        
        # Check tests still failing
        if not context.get('tests_failing', False):
            errors.append("Tests not failing (RED phase incomplete)")
        
        # Check implementation path
        if not context.get('implementation_path'):
            errors.append("Implementation path not determined")
        
        passed = len(errors) == 0
        return ValidationResult(passed=passed, errors=errors, warnings=warnings, phase="GREEN", validation_type="DoR")
    
    def validate_green_dod(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate GREEN phase DoD."""
        errors = []
        warnings = []
        
        # Check all tests pass
        test_pass_rate = context.get('test_pass_rate', 0.0)
        if test_pass_rate < 1.0:
            errors.append(f"Not all tests passing ({test_pass_rate*100:.1f}%)")
        
        # Check coverage
        coverage = context.get('coverage', 0.0)
        if coverage < 0.8:
            errors.append(f"Coverage below 80% ({coverage*100:.1f}%)")
        
        # Check minimal implementation
        if context.get('over_engineering_detected', False):
            warnings.append("Over-engineering detected")
        
        passed = len(errors) == 0
        return ValidationResult(passed=passed, errors=errors, warnings=warnings, phase="GREEN", validation_type="DoD")
    
    def validate_refactor_dor(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate REFACTOR phase DoR."""
        errors = []
        warnings = []
        
        # Check GREEN DoD complete
        if not context.get('green_dod_complete', False):
            errors.append("GREEN DoD not complete")
        
        # Check tests passing
        if not context.get('tests_passing', False):
            errors.append("Tests not passing before refactoring")
        
        # Check code smells detected
        if not context.get('code_smells_detected', False):
            warnings.append("No code smells detected")
        
        passed = len(errors) == 0
        return ValidationResult(passed=passed, errors=errors, warnings=warnings, phase="REFACTOR", validation_type="DoR")
    
    def validate_refactor_dod(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate REFACTOR phase DoD."""
        errors = []
        warnings = []
        
        # Check code smells reduced
        smells_before = context.get('smells_before', 0)
        smells_after = context.get('smells_after', 0)
        if smells_after >= smells_before:
            errors.append(f"Code smells not reduced ({smells_before} -> {smells_after})")
        
        # Check tests still pass
        if not context.get('tests_passing', False):
            errors.append("Tests not passing after refactoring")
        
        # Check no new complexity
        complexity_before = context.get('complexity_before', 0)
        complexity_after = context.get('complexity_after', 0)
        if complexity_after > complexity_before:
            warnings.append(f"Complexity increased ({complexity_before} -> {complexity_after})")
        
        passed = len(errors) == 0
        return ValidationResult(passed=passed, errors=errors, warnings=warnings, phase="REFACTOR", validation_type="DoD")
