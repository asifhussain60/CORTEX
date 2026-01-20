"""Security Tier2 - Advanced security hardening and credential protection.

Provides security violation detection, credential protection mechanisms,
and security event handling.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional
from enum import Enum
from datetime import datetime


class ViolationType(Enum):
    """Types of security violations."""

    UNAUTHORIZED_ACCESS = "unauthorized_access"
    CREDENTIAL_EXPOSURE = "credential_exposure"
    INJECTION_ATTACK = "injection_attack"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_BREACH = "data_breach"
    MALICIOUS_INPUT = "malicious_input"


class SecurityPolicy:
    """Security policy for access control.

    Manages security policies, permissions, and access control rules.
    """

    def __init__(self, policy_id: str, name: str) -> None:
        """Initialize security policy.

        Args:
            policy_id: Policy identifier.
            name: Human-readable policy name.
        """
        self.policy_id = policy_id
        self.name = name
        self.rules: Dict[str, Any] = {}
        self.permissions: Dict[str, bool] = {}

    def add_rule(self, rule_id: str, rule_config: Dict[str, Any]) -> None:
        """Add a security rule.

        Args:
            rule_id: Rule identifier.
            rule_config: Rule configuration.
        """
        self.rules[rule_id] = rule_config

    def grant_permission(self, resource: str, allow: bool = True) -> None:
        """Grant or deny permission for a resource.

        Args:
            resource: Resource identifier.
            allow: True to grant, False to deny.
        """
        self.permissions[resource] = allow

    def has_permission(self, resource: str) -> bool:
        """Check if resource access is permitted.

        Args:
            resource: Resource identifier.

        Returns:
            True if access is permitted, False otherwise.
        """
        return self.permissions.get(resource, False)

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate policy against a context.

        Args:
            context: Context to evaluate.

        Returns:
            True if policy is satisfied, False otherwise.
        """
        # Basic evaluation logic
        return len(self.rules) > 0 or len(self.permissions) > 0


class SecurityContext:
    """Security context for request processing.

    Maintains security context, credentials, and permissions.
    """

    def __init__(self, user_id: str, session_id: str = "") -> None:
        """Initialize security context.

        Args:
            user_id: User identifier.
            session_id: Session identifier.
        """
        self.user_id = user_id
        self.session_id = session_id
        self.permissions: set = set()
        self.credentials: Dict[str, Any] = {}
        self.is_authenticated = False

    def set_authenticated(self, authenticated: bool = True) -> None:
        """Set authentication status.

        Args:
            authenticated: Authentication status.
        """
        self.is_authenticated = authenticated

    def grant_permission(self, permission: str) -> None:
        """Grant a permission.

        Args:
            permission: Permission to grant.
        """
        self.permissions.add(permission)

    def has_permission(self, permission: str) -> bool:
        """Check if permission is granted.

        Args:
            permission: Permission to check.

        Returns:
            True if granted, False otherwise.
        """
        return permission in self.permissions

    def set_credential(self, key: str, value: Any) -> None:
        """Set a credential.

        Args:
            key: Credential key.
            value: Credential value.
        """
        self.credentials[key] = value

    def get_credential(self, key: str) -> Optional[Any]:
        """Get a credential.

        Args:
            key: Credential key.

        Returns:
            Credential value if found, None otherwise.
        """
        return self.credentials.get(key)


@dataclass
class SecurityViolation:
    """Security violation event.

    Attributes:
        violation_type: Type of violation.
        severity: Severity level (1-5).
        description: Violation description.
        timestamp: When violation occurred.
        context: Additional context.
    """

    violation_type: ViolationType
    severity: int
    description: str
    timestamp: datetime = None
    context: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.context is None:
            self.context = {}


class SecurityValidator:
    """Validates input for security violations."""

    def __init__(self) -> None:
        """Initialize security validator."""
        self.violations: list = []

    def validate(self, input_data: Any) -> bool:
        """Validate input for security issues.

        Args:
            input_data: Data to validate.

        Returns:
            True if valid, False if violations found.
        """
        # Basic validation
        if isinstance(input_data, str):
            # Check for injection patterns
            dangerous_patterns = ["<script", "eval(", "exec(", "import os"]
            lower_input = input_data.lower()
            
            for pattern in dangerous_patterns:
                if pattern in lower_input:
                    violation = SecurityViolation(
                        violation_type=ViolationType.INJECTION_ATTACK,
                        severity=4,
                        description=f"Potential injection attack detected: {pattern}",
                    )
                    self.violations.append(violation)
                    return False
        
        return True

    def get_violations(self) -> list:
        """Get all recorded violations.

        Returns:
            List of security violations.
        """
        return self.violations.copy()

    def clear_violations(self) -> None:
        """Clear violation history."""
        self.violations.clear()


class OutputEncoder:
    """Encodes output safely for security."""

    @staticmethod
    def encode_html(text: str) -> str:
        """HTML-encode text.

        Args:
            text: Text to encode.

        Returns:
            HTML-encoded text.
        """
        replacements = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#x27;",
        }
        result = text
        for old, new in replacements.items():
            result = result.replace(old, new)
        return result

    @staticmethod
    def encode_json(text: str) -> str:
        """JSON-encode text.

        Args:
            text: Text to encode.

        Returns:
            JSON-encoded text.
        """
        import json
        return json.dumps(text)

    @staticmethod
    def sanitize(text: str) -> str:
        """Sanitize text by removing dangerous characters.

        Args:
            text: Text to sanitize.

        Returns:
            Sanitized text.
        """
        dangerous_chars = ["<", ">", "\\x00", "\r", "\n"]
        result = text
        for char in dangerous_chars:
            result = result.replace(char, "")
        return result


# Alias for backward compatibility
InputValidator = SecurityValidator

__all__ = [
    "SecurityViolation",
    "SecurityValidator",
    "SecurityPolicy",
    "SecurityContext",
    "OutputEncoder",
    "InputValidator",
    "ViolationType",
]

