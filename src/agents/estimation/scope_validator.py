"""
CORTEX Scope Validator

Purpose: Validate scope boundaries and identify missing elements for clarification
Target: Confidence threshold validation + gap detection + clarification questions
Status: TDD GREEN Phase - Implementation to pass RED tests

Component of: SWAGGER Entry Point Module (Phase 3.3)
"""

import logging
from dataclasses import dataclass, field
from typing import List, Set
from enum import Enum

from src.agents.estimation.scope_inference_engine import ScopeBoundary

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    ERROR = "error"  # Blocks progression
    WARNING = "warning"  # Flags for review
    INFO = "info"  # Informational only


@dataclass
class ValidationRule:
    """Single validation rule"""
    name: str
    severity: ValidationSeverity
    message: str
    passed: bool


@dataclass
class ValidationResult:
    """Result of scope validation"""
    is_valid: bool
    requires_clarification: bool
    confidence_score: float
    validation_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    missing_elements: List[str] = field(default_factory=list)
    rules_evaluated: List[ValidationRule] = field(default_factory=list)


class ScopeValidator:
    """
    Validate scope boundaries and generate clarification questions
    
    Key Innovation: Smart validation that distinguishes between:
    - Missing critical elements (tables, files) → clarification required
    - Optional elements (services) → no clarification needed
    - Over-limit scope → prioritization required
    """
    
    # Confidence threshold for auto-proceed
    HIGH_CONFIDENCE_THRESHOLD = 0.70
    
    # Complexity thresholds
    HIGH_COMPLEXITY_THRESHOLD = 70.0
    CRITICAL_COMPLEXITY_THRESHOLD = 85.0
    
    # Size thresholds
    MAX_TABLES = 50
    MAX_FILES = 100
    
    def __init__(self):
        """Initialize validator with default rules"""
        pass
    
    def validate_scope(self, boundary: ScopeBoundary) -> ValidationResult:
        """
        Validate scope boundary against quality rules
        
        Args:
            boundary: Scope boundary from inference engine
            
        Returns:
            ValidationResult with errors, warnings, and missing elements
        """
        result = ValidationResult(
            is_valid=True,
            requires_clarification=False,
            confidence_score=boundary.confidence
        )
        
        # Rule 1: Confidence threshold check
        if boundary.confidence < self.HIGH_CONFIDENCE_THRESHOLD:
            result.is_valid = False
            result.requires_clarification = True
            result.validation_errors.append(
                f"Confidence score {boundary.confidence:.2f} below threshold "
                f"({self.HIGH_CONFIDENCE_THRESHOLD:.2f}). Clarification required."
            )
            
            rule = ValidationRule(
                name="confidence_threshold",
                severity=ValidationSeverity.ERROR,
                message=f"Confidence too low: {boundary.confidence:.2f}",
                passed=False
            )
            result.rules_evaluated.append(rule)
        
        # Rule 2: Missing tables check (critical)
        if boundary.table_count == 0:
            result.missing_elements.append("tables")
            result.validation_errors.append("No database tables identified. What tables will be affected?")
            result.warnings.append("Scope has no database tables - is this a data-free feature?")
            
            rule = ValidationRule(
                name="tables_present",
                severity=ValidationSeverity.WARNING,
                message="No tables identified",
                passed=False
            )
            result.rules_evaluated.append(rule)
        
        # Rule 3: Missing files check (critical)
        if boundary.file_count == 0:
            result.missing_elements.append("files")
            result.validation_errors.append("No code files identified. What files will be modified?")
            
            rule = ValidationRule(
                name="files_present",
                severity=ValidationSeverity.ERROR,
                message="No code files identified",
                passed=False
            )
            result.rules_evaluated.append(rule)
        
        # Rule 4: Over-limit checks (safety)
        if boundary.table_count > self.MAX_TABLES:
            result.validation_errors.append(
                f"Scope exceeds {self.MAX_TABLES} table limit ({boundary.table_count} tables). "
                "Prioritization required."
            )
            
            rule = ValidationRule(
                name="table_count_limit",
                severity=ValidationSeverity.ERROR,
                message=f"Too many tables: {boundary.table_count}",
                passed=False
            )
            result.rules_evaluated.append(rule)
        
        if boundary.file_count > self.MAX_FILES:
            result.validation_errors.append(
                f"Scope exceeds {self.MAX_FILES} file limit ({boundary.file_count} files). "
                "Prioritization required."
            )
            
            rule = ValidationRule(
                name="file_count_limit",
                severity=ValidationSeverity.ERROR,
                message=f"Too many files: {boundary.file_count}",
                passed=False
            )
            result.rules_evaluated.append(rule)
        
        # Rule 5: Complexity scoring
        if boundary.estimated_complexity > self.CRITICAL_COMPLEXITY_THRESHOLD:
            result.warnings.append(
                f"Very high complexity score ({boundary.estimated_complexity:.1f}/100). "
                "Consider breaking into smaller phases."
            )
            
            rule = ValidationRule(
                name="complexity_check",
                severity=ValidationSeverity.WARNING,
                message=f"High complexity: {boundary.estimated_complexity:.1f}",
                passed=False
            )
            result.rules_evaluated.append(rule)
        elif boundary.estimated_complexity > self.HIGH_COMPLEXITY_THRESHOLD:
            result.warnings.append(
                f"High complexity score ({boundary.estimated_complexity:.1f}/100). "
                "Review scope carefully."
            )
        
        # Rule 6: Enterprise monolith detection
        if boundary.table_count >= self.MAX_TABLES and boundary.file_count >= self.MAX_FILES:
            result.warnings.append(
                f"Large-scale feature detected ({boundary.table_count} tables, "
                f"{boundary.file_count} files). Ensure proper planning and phasing."
            )
        
        # Rule 7: Zero confidence check
        if boundary.confidence == 0.0:
            result.is_valid = False
            result.requires_clarification = True
            result.validation_errors.append("Empty scope - no entities detected. Cannot proceed.")
        
        # Rule 8: Incorporate gaps from inference engine
        if boundary.gaps:
            for gap in boundary.gaps:
                if "exceeds" in gap.lower():
                    # Already handled by over-limit checks
                    pass
                elif any(keyword in gap.lower() for keyword in ["no", "missing", "not"]):
                    result.requires_clarification = True
                else:
                    result.warnings.append(gap)
        
        # Final validation decision
        if result.validation_errors:
            result.is_valid = False
            result.requires_clarification = True
        
        logger.info(f"Validation result: valid={result.is_valid}, "
                   f"requires_clarification={result.requires_clarification}, "
                   f"errors={len(result.validation_errors)}, warnings={len(result.warnings)}")
        
        return result
    
    def generate_clarification_questions(
        self, 
        validation_result: ValidationResult, 
        boundary: ScopeBoundary
    ) -> List[str]:
        """
        Generate targeted clarification questions based on validation gaps
        
        Args:
            validation_result: Result from validate_scope()
            boundary: Original scope boundary
            
        Returns:
            List of clarification questions (empty if no clarification needed)
        """
        if not validation_result.requires_clarification:
            return []
        
        questions = []
        
        # Generate questions for missing elements
        if "tables" in validation_result.missing_elements:
            questions.append(
                "What database tables will be affected by this feature? "
                "Please list all tables that will be created, modified, or queried."
            )
        
        if "files" in validation_result.missing_elements:
            questions.append(
                "What code files or classes will be modified? "
                "Please identify the main services, controllers, or components involved."
            )
        
        # Generate questions from boundary gaps
        for gap in boundary.gaps:
            if "dependencies" in gap.lower():
                questions.append(
                    "Are there any external service integrations (APIs, auth providers, etc.)? "
                    "If yes, please list them."
                )
            elif "incomplete" in gap.lower() or "more" in gap.lower():
                questions.append(
                    "The detected scope seems incomplete. Can you provide more details about "
                    "the full extent of this feature?"
                )
        
        # Add confidence-based questions
        if validation_result.confidence_score < 0.40:
            questions.append(
                "The requirements are quite vague. Can you provide more specific details about "
                "what this feature does and what components are involved?"
            )
        elif validation_result.confidence_score < self.HIGH_CONFIDENCE_THRESHOLD:
            questions.append(
                "I've identified some scope elements but need clarification. "
                "Are there any other tables, files, or dependencies not mentioned?"
            )
        
        logger.info(f"Generated {len(questions)} clarification questions")
        
        return questions


if __name__ == "__main__":
    # Quick test
    from src.agents.estimation.scope_inference_engine import ScopeBoundary
    
    validator = ScopeValidator()
    
    # Test 1: High confidence scope
    boundary_high = ScopeBoundary(
        table_count=5, file_count=8, service_count=2,
        dependency_depth=1, estimated_complexity=45.0,
        confidence=0.75, gaps=[]
    )
    result = validator.validate_scope(boundary_high)
    print(f"High confidence: valid={result.is_valid}, clarification={result.requires_clarification}")
    
    # Test 2: Low confidence scope
    boundary_low = ScopeBoundary(
        table_count=1, file_count=0, service_count=0,
        dependency_depth=1, estimated_complexity=5.0,
        confidence=0.25, gaps=["No code files mentioned"]
    )
    result = validator.validate_scope(boundary_low)
    questions = validator.generate_clarification_questions(result, boundary_low)
    print(f"Low confidence: valid={result.is_valid}, questions={len(questions)}")
    print(f"Questions: {questions}")
