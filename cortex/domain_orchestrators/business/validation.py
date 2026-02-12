"""Domain Validation Framework

Validation framework for domain operations and contexts.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from cortex.models.canonical_enums import ValidationSeverity


@dataclass
class ValidationResult:
    """Result of validation."""
    is_valid: bool
    severity: ValidationSeverity = ValidationSeverity.INFO
    messages: List[str] = None

    def __post_init__(self):
        """Initialize messages."""
        if self.messages is None:
            self.messages = []


@dataclass
class ValidationRule:
    """Domain validation rule."""
    rule_id: str
    domain: str
    description: str
    validate: Callable[[Dict[str, Any]], bool]
    severity: ValidationSeverity = ValidationSeverity.ERROR


class DomainValidator:
    """Validator for domain operations."""

    def __init__(self):
        """Initialize validator."""
        self._rules: Dict[str, List[ValidationRule]] = {}
        self._domain_compatibility: Dict[tuple, bool] = {}

        # Initialize default compatibility and rules
        self._init_default_compatibility()
        self._init_default_rules()

    def _init_default_rules(self) -> None:
        """Initialize default domain rules."""
        # Financial domain rules
        self._rules["financial"] = [
            ValidationRule(
                rule_id="FIN-001",
                domain="financial",
                description="Amount must be positive",
                validate=lambda ctx: ctx.get("amount", 0) > 0
            )
        ]

        # Healthcare domain rules
        self._rules["healthcare"] = [
            ValidationRule(
                rule_id="HC-001",
                domain="healthcare",
                description="Patient ID must be present",
                validate=lambda ctx: "patient_id" in ctx
            )
        ]

    def _init_default_compatibility(self) -> None:
        """Initialize default domain compatibility."""
        domains = ["financial", "healthcare", "ecommerce"]

        # All domains are self-compatible
        for domain in domains:
            self._domain_compatibility[(domain, domain)] = True

        # E-commerce and financial are compatible for payments
        self._domain_compatibility[("ecommerce", "financial")] = True
        self._domain_compatibility[("financial", "ecommerce")] = True

    def validate_context(self, domain: str, context: Dict[str, Any]) -> ValidationResult:
        """Validate domain context.

        Args:
            domain: Domain name
            context: Context to validate

        Returns:
            Validation result
        """
        rules = self._rules.get(domain, [])

        for rule in rules:
            if not rule.validate(context):
                return ValidationResult(
                    is_valid=False,
                    severity=rule.severity,
                    messages=[f"Rule {rule.rule_id} failed: {rule.description}"]
                )

        return ValidationResult(is_valid=True)

    def validate_operation(self, domain: str, operation: str) -> ValidationResult:
        """Validate domain operation.

        Args:
            domain: Domain name
            operation: Operation name

        Returns:
            Validation result
        """
        # Basic validation - operation is non-empty
        if not operation:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                messages=["Operation name cannot be empty"]
            )

        return ValidationResult(is_valid=True)

    def get_rules(self, domain: str) -> List[ValidationRule]:
        """Get validation rules for domain.

        Args:
            domain: Domain name

        Returns:
            List of rules
        """
        return self._rules.get(domain, [])

    def register_rule(self, rule: ValidationRule) -> None:
        """Register a validation rule.

        Args:
            rule: Rule to register
        """
        domain = rule.domain

        if domain not in self._rules:
            self._rules[domain] = []

        self._rules[domain].append(rule)

    def validate_cross_domain_operation(
        self,
        source_domain: str,
        target_domain: str,
        operation: str,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Validate cross-domain operation.

        Args:
            source_domain: Source domain
            target_domain: Target domain
            operation: Operation name
            context: Operation context

        Returns:
            Validation result
        """
        # Check domain compatibility
        if not self.are_domains_compatible(source_domain, target_domain):
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                messages=[f"Domains {source_domain} and {target_domain} are not compatible"]
            )

        # Validate operation
        op_result = self.validate_operation(target_domain, operation)
        if not op_result.is_valid:
            return op_result

        # Validate context
        ctx_result = self.validate_context(target_domain, context)

        return ctx_result

    def are_domains_compatible(self, domain1: str, domain2: str) -> bool:
        """Check if two domains are compatible.

        Args:
            domain1: First domain
            domain2: Second domain

        Returns:
            True if compatible
        """
        return self._domain_compatibility.get((domain1, domain2), False)


__all__ = ["DomainValidator", "ValidationRule", "ValidationResult", "ValidationSeverity"]
