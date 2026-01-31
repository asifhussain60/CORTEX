"""
AC-PHX-008-06: Domain Validation Framework

Validation framework for domain operations, contexts, and cross-domain
interactions.

"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
from enum import Enum

from cortex.models.canonical_enums import ValidationSeverity


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    messages: List[str] = field(default_factory=list)
    severity: ValidationSeverity = ValidationSeverity.INFO
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def add_message(self, message: str, severity: ValidationSeverity = ValidationSeverity.ERROR) -> None:
        """Add a validation message."""
        self.messages.append(message)
        if severity.value > self.severity.value:
            self.severity = severity
        if severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
            self.is_valid = False


@dataclass
class ValidationRule:
    """A validation rule for domain operations."""
    rule_id: str
    domain: str
    description: str
    validate: Callable[[Dict[str, Any]], bool]
    severity: ValidationSeverity = ValidationSeverity.ERROR
    
    def check(self, context: Dict[str, Any]) -> bool:
        """Execute the validation rule."""
        return self.validate(context)


class DomainValidator:
    """
    Validator for domain operations and contexts.
    
    Provides:
    - Context validation per domain
    - Operation validation
    - Cross-domain operation validation
    - Custom rule registration
    """
    
    # Default domain validation rules
    DEFAULT_RULES: Dict[str, List[ValidationRule]] = {}
    
    # Domain compatibility matrix
    DOMAIN_COMPATIBILITY: Dict[str, Set[str]] = {
        "financial": {"financial", "ecommerce"},
        "healthcare": {"healthcare"},
        "ecommerce": {"ecommerce", "financial"},
    }
    
    def __init__(self) -> None:
        """Initialize domain validator."""
        self._rules: Dict[str, List[ValidationRule]] = {
            "financial": [
                ValidationRule(
                    rule_id="fin-001",
                    domain="financial",
                    description="Amount must be positive",
                    validate=lambda ctx: ctx.get("amount", 1) > 0,
                ),
                ValidationRule(
                    rule_id="fin-002",
                    domain="financial",
                    description="Currency must be specified",
                    validate=lambda ctx: "currency" in ctx or "amount" not in ctx,
                ),
            ],
            "healthcare": [
                ValidationRule(
                    rule_id="hc-001",
                    domain="healthcare",
                    description="Authorization required",
                    validate=lambda ctx: "authorized_user" in ctx or ctx.get("operation") == "public_info",
                ),
                ValidationRule(
                    rule_id="hc-002",
                    domain="healthcare",
                    description="Patient ID required for patient operations",
                    validate=lambda ctx: "patient_id" in ctx or not ctx.get("operation", "").startswith("patient"),
                ),
            ],
            "ecommerce": [
                ValidationRule(
                    rule_id="ec-001",
                    domain="ecommerce",
                    description="Order ID required for order operations",
                    validate=lambda ctx: "order_id" in ctx or ctx.get("operation") not in ["process_order", "process_payment"],
                ),
                ValidationRule(
                    rule_id="ec-002",
                    domain="ecommerce",
                    description="Items required for order",
                    validate=lambda ctx: "items" in ctx or ctx.get("operation") != "process_order",
                ),
            ],
        }
    
    def validate_context(
        self,
        domain: str,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate a domain context.
        
        Args:
            domain: Domain name
            context: Context to validate
            
        Returns:
            Validation result
        """
        result = ValidationResult(is_valid=True)
        
        rules = self.get_rules(domain)
        for rule in rules:
            if not rule.check(context):
                result.add_message(
                    f"Rule {rule.rule_id} failed: {rule.description}",
                    rule.severity,
                )
        
        return result
    
    def validate_operation(
        self,
        domain: str,
        operation: str
    ) -> ValidationResult:
        """
        Validate a domain operation.
        
        Args:
            domain: Domain name
            operation: Operation name
            
        Returns:
            Validation result
        """
        result = ValidationResult(is_valid=True)
        
        # Get valid operations for domain
        valid_operations = self._get_valid_operations(domain)
        
        if operation not in valid_operations:
            result.add_message(
                f"Operation '{operation}' not supported for domain '{domain}'",
                ValidationSeverity.ERROR,
            )
        
        return result
    
    def validate_cross_domain_operation(
        self,
        source_domain: str,
        target_domain: str,
        operation: str,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate cross-domain operation.
        
        Args:
            source_domain: Source domain
            target_domain: Target domain
            operation: Operation name
            context: Operation context
            
        Returns:
            Validation result
        """
        result = ValidationResult(is_valid=True)
        
        # Check domain compatibility
        if not self.are_domains_compatible(source_domain, target_domain):
            result.add_message(
                f"Domains '{source_domain}' and '{target_domain}' are not compatible",
                ValidationSeverity.ERROR,
            )
            return result
        
        # Validate context for both domains
        source_result = self.validate_context(source_domain, context)
        if not source_result.is_valid:
            result.is_valid = False
            result.messages.extend(source_result.messages)
        
        target_result = self.validate_context(target_domain, context)
        if not target_result.is_valid:
            result.is_valid = False
            result.messages.extend(target_result.messages)
        
        return result
    
    def get_rules(self, domain: str) -> List[ValidationRule]:
        """
        Get validation rules for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of validation rules
        """
        return self._rules.get(domain, [])
    
    def register_rule(self, rule: ValidationRule) -> None:
        """
        Register a custom validation rule.
        
        Args:
            rule: Validation rule to register
        """
        domain = rule.domain
        if domain not in self._rules:
            self._rules[domain] = []
        self._rules[domain].append(rule)
    
    def are_domains_compatible(
        self,
        source_domain: str,
        target_domain: str
    ) -> bool:
        """
        Check if two domains are compatible.
        
        Args:
            source_domain: Source domain
            target_domain: Target domain
            
        Returns:
            True if domains are compatible
        """
        # All domains are self-compatible
        if source_domain == target_domain:
            return True
        
        compatible = self.DOMAIN_COMPATIBILITY.get(source_domain, {source_domain})
        return target_domain in compatible
    
    def _get_valid_operations(self, domain: str) -> Set[str]:
        """Get valid operations for a domain."""
        operations = {
            "financial": {
                "transfer", "payment", "reconciliation",
                "balance_inquiry", "statement", "wire_transfer",
            },
            "healthcare": {
                "patient_lookup", "appointment_schedule", "prescription",
                "lab_order", "lab_result", "care_note", "billing_query",
            },
            "ecommerce": {
                "process_order", "process_payment", "calculate_shipping",
                "check_inventory", "reserve_inventory", "fulfill_order",
                "process_return",
            },
        }
        return operations.get(domain, set())
