"""
Validation Pipeline - Configurable validation system for plans and phases

Provides rule-based validation with severity levels, custom validators,
and detailed error reporting.

Author: Asif Hussain
Version: 1.0.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
import re
import logging

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation result severity levels."""
    ERROR = "error"  # Blocks execution
    WARNING = "warning"  # Should fix but doesn't block
    INFO = "info"  # Informational only


@dataclass
class ValidationResult:
    """Result of a single validation rule."""
    rule_name: str
    severity: ValidationSeverity
    passed: bool
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "passed": self.passed,
            "message": self.message,
            "field": self.field,
            "suggestion": self.suggestion
        }


@dataclass
class ValidationReport:
    """Complete validation report."""
    is_valid: bool = True
    errors: List[ValidationResult] = field(default_factory=list)
    warnings: List[ValidationResult] = field(default_factory=list)
    info: List[ValidationResult] = field(default_factory=list)
    
    def add_result(self, result: ValidationResult) -> None:
        """Add validation result to report."""
        if result.severity == ValidationSeverity.ERROR:
            self.errors.append(result)
            if not result.passed:
                self.is_valid = False
        elif result.severity == ValidationSeverity.WARNING:
            self.warnings.append(result)
        else:
            self.info.append(result)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "is_valid": self.is_valid,
            "error_count": len([e for e in self.errors if not e.passed]),
            "warning_count": len([w for w in self.warnings if not w.passed]),
            "info_count": len([i for i in self.info if not i.passed]),
            "total_checks": len(self.errors) + len(self.warnings) + len(self.info)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "summary": self.get_summary(),
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "info": [i.to_dict() for i in self.info]
        }


class ValidationRule:
    """
    Base validation rule.
    
    Subclass this to create custom validation rules.
    """
    
    def __init__(
        self,
        name: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        enabled: bool = True
    ):
        """
        Initialize validation rule.
        
        Args:
            name: Rule identifier
            severity: Severity level
            enabled: Whether rule is enabled
        """
        self.name = name
        self.severity = severity
        self.enabled = enabled
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate data against rule.
        
        Args:
            data: Data to validate
        
        Returns:
            Validation result
        """
        raise NotImplementedError("Subclasses must implement validate()")


class RequiredFieldRule(ValidationRule):
    """Validate that required fields are present."""
    
    def __init__(self, field: str, severity: ValidationSeverity = ValidationSeverity.ERROR):
        """Initialize required field rule."""
        super().__init__(f"required_field_{field}", severity)
        self.field = field
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Check if field exists and is not empty."""
        exists = self.field in data
        not_empty = bool(data.get(self.field)) if exists else False
        
        passed = exists and not_empty
        message = f"Field '{self.field}' is required" if not passed else f"Field '{self.field}' is present"
        
        return ValidationResult(
            rule_name=self.name,
            severity=self.severity,
            passed=passed,
            message=message,
            field=self.field,
            suggestion=f"Add '{self.field}' field to data" if not passed else None
        )


class FormatRule(ValidationRule):
    """Validate field format using regex."""
    
    def __init__(self, field: str, pattern: str, description: str):
        """Initialize format rule."""
        super().__init__(f"format_{field}")
        self.field = field
        self.pattern = re.compile(pattern)
        self.description = description
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Check if field matches pattern."""
        if self.field not in data:
            return ValidationResult(
                rule_name=self.name,
                severity=self.severity,
                passed=False,
                message=f"Field '{self.field}' not found",
                field=self.field
            )
        
        value = str(data[self.field])
        matches = bool(self.pattern.match(value))
        
        return ValidationResult(
            rule_name=self.name,
            severity=self.severity,
            passed=matches,
            message=f"Field '{self.field}' {'matches' if matches else 'does not match'} {self.description}",
            field=self.field,
            suggestion=f"Format should match: {self.description}" if not matches else None
        )


class RangeRule(ValidationRule):
    """Validate numeric field is within range."""
    
    def __init__(self, field: str, min_val: Optional[float] = None, max_val: Optional[float] = None):
        """Initialize range rule."""
        super().__init__(f"range_{field}")
        self.field = field
        self.min_val = min_val
        self.max_val = max_val
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Check if field is within range."""
        if self.field not in data:
            return ValidationResult(
                rule_name=self.name,
                severity=self.severity,
                passed=False,
                message=f"Field '{self.field}' not found",
                field=self.field
            )
        
        try:
            value = float(data[self.field])
            
            within_range = True
            messages = []
            
            if self.min_val is not None and value < self.min_val:
                within_range = False
                messages.append(f"below minimum {self.min_val}")
            
            if self.max_val is not None and value > self.max_val:
                within_range = False
                messages.append(f"above maximum {self.max_val}")
            
            if within_range:
                message = f"Field '{self.field}' value {value} is within range"
            else:
                message = f"Field '{self.field}' value {value} is {', '.join(messages)}"
            
            return ValidationResult(
                rule_name=self.name,
                severity=self.severity,
                passed=within_range,
                message=message,
                field=self.field,
                suggestion=f"Value should be between {self.min_val} and {self.max_val}" if not within_range else None
            )
        except (ValueError, TypeError):
            return ValidationResult(
                rule_name=self.name,
                severity=self.severity,
                passed=False,
                message=f"Field '{self.field}' is not a valid number",
                field=self.field
            )


class CustomRule(ValidationRule):
    """Custom validation rule using a callable."""
    
    def __init__(
        self,
        name: str,
        validator: Callable[[Dict[str, Any]], bool],
        message: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR
    ):
        """
        Initialize custom rule.
        
        Args:
            name: Rule name
            validator: Callable that returns True if valid
            message: Error message
            severity: Severity level
        """
        super().__init__(name, severity)
        self.validator = validator
        self.message_template = message
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Run custom validator."""
        try:
            passed = self.validator(data)
            return ValidationResult(
                rule_name=self.name,
                severity=self.severity,
                passed=passed,
                message=self.message_template if not passed else f"Custom rule '{self.name}' passed"
            )
        except Exception as e:
            return ValidationResult(
                rule_name=self.name,
                severity=self.severity,
                passed=False,
                message=f"Custom rule '{self.name}' raised error: {str(e)}"
            )


class ValidationPipeline:
    """
    Configurable validation pipeline.
    
    Chain multiple validation rules and generate comprehensive reports.
    """
    
    def __init__(self, name: str = "validation"):
        """Initialize validation pipeline."""
        self.name = name
        self.rules: List[ValidationRule] = []
    
    def add_rule(self, rule: ValidationRule) -> 'ValidationPipeline':
        """
        Add validation rule to pipeline.
        
        Returns:
            Self for chaining
        """
        self.rules.append(rule)
        return self
    
    def add_required_field(self, field: str, severity: ValidationSeverity = ValidationSeverity.ERROR) -> 'ValidationPipeline':
        """Convenience method to add required field rule."""
        self.add_rule(RequiredFieldRule(field, severity))
        return self
    
    def add_format_rule(self, field: str, pattern: str, description: str) -> 'ValidationPipeline':
        """Convenience method to add format rule."""
        self.add_rule(FormatRule(field, pattern, description))
        return self
    
    def add_range_rule(
        self,
        field: str,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None
    ) -> 'ValidationPipeline':
        """Convenience method to add range rule."""
        self.add_rule(RangeRule(field, min_val, max_val))
        return self
    
    def add_custom_rule(
        self,
        name: str,
        validator: Callable[[Dict[str, Any]], bool],
        message: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR
    ) -> 'ValidationPipeline':
        """Convenience method to add custom rule."""
        self.add_rule(CustomRule(name, validator, message, severity))
        return self
    
    def validate(self, data: Dict[str, Any]) -> ValidationReport:
        """
        Run all validation rules.
        
        Args:
            data: Data to validate
        
        Returns:
            Complete validation report
        """
        report = ValidationReport()
        
        for rule in self.rules:
            if rule.enabled:
                try:
                    result = rule.validate(data)
                    report.add_result(result)
                except Exception as e:
                    logger.error(f"Validation rule '{rule.name}' failed: {e}")
                    report.add_result(ValidationResult(
                        rule_name=rule.name,
                        severity=rule.severity,
                        passed=False,
                        message=f"Rule execution failed: {str(e)}"
                    ))
        
        return report
    
    def validate_batch(self, items: List[Dict[str, Any]]) -> List[ValidationReport]:
        """
        Validate multiple items.
        
        Args:
            items: List of items to validate
        
        Returns:
            List of validation reports
        """
        return [self.validate(item) for item in items]


# Predefined validation pipelines for common use cases

def create_plan_validation_pipeline() -> ValidationPipeline:
    """Create validation pipeline for plan metadata."""
    return (
        ValidationPipeline("plan_validation")
        .add_required_field("plan_id")
        .add_required_field("plan_name")
        .add_required_field("plan_type")
        .add_format_rule("plan_id", r"^[a-z0-9-]+$", "lowercase alphanumeric with hyphens")
        .add_custom_rule(
            "valid_plan_type",
            lambda d: d.get("plan_type") in ["epic", "feature"],
            "plan_type must be 'epic' or 'feature'"
        )
    )


def create_phase_validation_pipeline() -> ValidationPipeline:
    """Create validation pipeline for phase data."""
    return (
        ValidationPipeline("phase_validation")
        .add_required_field("phase_number")
        .add_required_field("phase_name")
        .add_range_rule("phase_number", min_val=0)
        .add_range_rule("progress_percentage", min_val=0, max_val=100)
        .add_custom_rule(
            "valid_status",
            lambda d: d.get("status") in ["not-started", "in-progress", "completed", "blocked", "failed", "deferred"],
            "status must be one of: not-started, in-progress, completed, blocked, failed, deferred"
        )
    )
