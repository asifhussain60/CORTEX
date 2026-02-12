"""
gateway-validator-spec: Gateway Validator for Spec Validation

Provides GatewayValidator for validating operation specifications before
execution through MasterGateway, per CORE-040.

CORE Rules Applied:
    - CORE-008: TDD (tests before implementation)
    - CORE-011: Type hints mandatory
    - CORE-012: Google-style docstrings
    - CORE-040: Execution Specification Mandate
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ValidationViolation:
    """Represents a validation violation."""
    code: str
    field: str
    message: str
    severity: str = "error"
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of specification validation."""
    is_valid: bool
    violations: List[ValidationViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Ensure consistency."""
        if self.violations and self.is_valid:
            self.is_valid = False


class GatewayValidator:
    """
    Validates operation specifications before execution.

    Ensures:
        1. Spec format matches JSON schema
        2. Required fields present
        3. Field values valid
        4. Governance rules satisfied
        5. Orchestrator dependencies available
    """

    # Required fields in operation spec
    REQUIRED_FIELDS = {"operation"}

    # Optional fields in operation spec
    OPTIONAL_FIELDS = {"intent", "context", "governance_context", "metadata"}

    def __init__(self) -> None:
        """Initialize validator."""
        logger.debug("GatewayValidator initialized")

    def validate_spec_format(self, spec: Dict[str, Any]) -> ValidationResult:
        """
        Check specification against JSON schema.

        Args:
            spec: Specification to validate

        Returns:
            ValidationResult with any violations found

        Example:
            >>> validator = GatewayValidator()
            >>> result = validator.validate_spec_format({
            ...     "operation": "implement_feature"
            ... })
            >>> assert result.is_valid
        """
        violations: List[ValidationViolation] = []

        # Check spec is dict (pylint: disable=isinstance-dict)
        if not isinstance(spec, dict):  # noqa: E501
            violations.append(ValidationViolation(
                code="SPEC_001",
                field="root",
                message="Specification must be a dictionary",
                severity="critical"
            ))
            return ValidationResult(is_valid=False, violations=violations)

        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in spec:
                violations.append(ValidationViolation(
                    code="SPEC_002",
                    field=field,
                    message=f"Required field '{field}' missing",
                    severity="critical",
                    suggestion=f"Add '{field}' to specification"
                ))

        # Check for unknown fields
        known_fields = self.REQUIRED_FIELDS | self.OPTIONAL_FIELDS
        for field in spec.keys():
            if field not in known_fields:
                violations.append(ValidationViolation(
                    code="SPEC_003",
                    field=field,
                    message=f"Unknown field '{field}'",
                    severity="warning"
                ))

        # Validate operation field
        if "operation" in spec:
            if not isinstance(spec["operation"], str):
                violations.append(ValidationViolation(
                    code="SPEC_004",
                    field="operation",
                    message="Field 'operation' must be a string",
                    severity="critical"
                ))
            elif not spec["operation"].strip():
                violations.append(ValidationViolation(
                    code="SPEC_005",
                    field="operation",
                    message="Field 'operation' cannot be empty",
                    severity="critical"
                ))

        # Validate intent field (optional but should be valid if present)
        if "intent" in spec:
            valid_intents = {"IMPLEMENT", "FIX", "REFACTOR", "ANALYZE",
                           "DOCUMENT", "TEST", "DEPLOY", "GOVERNANCE"}
            if spec["intent"] not in valid_intents:
                violations.append(ValidationViolation(
                    code="SPEC_006",
                    field="intent",
                    message=f"Invalid intent type: {spec['intent']}",
                    severity="warning",
                    suggestion=f"Use one of: {', '.join(valid_intents)}"
                ))

        is_valid = len(violations) == 0
        return ValidationResult(is_valid=is_valid, violations=violations)

    def validate_governance_preconditions(
        self,
        spec: Dict[str, Any]
    ) -> ValidationResult:
        """
        Check governance rules allow execution.

        Args:
            spec: Operation specification

        Returns:
            ValidationResult with any governance violations
        """
        violations: List[ValidationViolation] = []

        # Phase 1: Placeholder - governance checks will be implemented
        # in Phase 2 when GovernanceRegistry is integrated

        logger.debug("Governance preconditions check: Phase 1 placeholder")

        return ValidationResult(is_valid=True, violations=violations)

    def validate_orchestrator_availability(
        self,
        handler: str
    ) -> ValidationResult:
        """
        Check handler orchestrator is available.

        Args:
            handler: Orchestrator name to check

        Returns:
            ValidationResult with any violations found
        """
        violations: List[ValidationViolation] = []

        # Phase 1: Placeholder - orchestrator availability checks
        # will be implemented in Phase 2 when OrchestratorRegistry
        # is fully integrated

        logger.debug(f"Orchestrator availability check: {handler} (Phase 1)")

        return ValidationResult(is_valid=True, violations=violations)

    def validate_complete(self, spec: Dict[str, Any]) -> ValidationResult:
        """
        Run all validation checks on specification.

        Args:
            spec: Operation specification

        Returns:
            Combined ValidationResult from all checks

        Example:
            >>> validator = GatewayValidator()
            >>> result = validator.validate_complete({
            ...     "operation": "implement_feature",
            ...     "intent": "IMPLEMENT"
            ... })
            >>> if not result.is_valid:
            ...     for v in result.violations:
            ...         print(f"  {v.code}: {v.message}")
        """
        violations: List[ValidationViolation] = []
        warnings: List[str] = []

        # Run format validation
        format_result = self.validate_spec_format(spec)
        violations.extend(format_result.violations)
        warnings.extend(format_result.warnings)

        # Only run other checks if format is valid
        if format_result.is_valid:
            # Run governance validation
            gov_result = self.validate_governance_preconditions(spec)
            violations.extend(gov_result.violations)
            warnings.extend(gov_result.warnings)

        is_valid = len(violations) == 0
        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings
        )


__all__ = [
    "GatewayValidator",
    "ValidationResult",
    "ValidationViolation",
]
