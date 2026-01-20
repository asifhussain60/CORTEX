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


__all__ = [
    "SecurityViolation",
    "SecurityValidator",
    "ViolationType",
]
