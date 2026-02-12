"""
Security Hardening Framework Module

Implements production security hardening for CORTEX:
- Input validation (OWASP Top 10)
- Output encoding
- Security governance enforcement

AC-NFR-003-01: Security Hardening Framework
"""

import html
import re
from pathlib import Path
from typing import Any, Dict, Optional, Pattern, Set


class SecurityViolation(Exception):
    """Raised when security policy is violated."""
    pass


class InputValidator:
    """
    Validates input against OWASP Top 10 security patterns.

    Covers:
    - SQL Injection detection
    - Command Injection detection
    - Path Traversal detection
    - XSS Injection detection
    - Script Injection detection
    """

    def __init__(self, strict_mode: bool = True):
        """
        Initialize InputValidator.

        Args:
            strict_mode: If True, reject suspicious patterns. If False, log only.
        """
        self.strict_mode = strict_mode
        self._violations: list[str] = []
        self._init_patterns()

    def _init_patterns(self) -> None:
        """Initialize regex patterns for OWASP threats."""
        # SQL Injection patterns
        self._sql_patterns = [
            r"(\bUNION\b).*?(\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b)",
            r"(\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b).*?['\"]",
            r"(\-\-|;|\/\*)",
            r"(\bOR\b|\bAND\b).*?['\"].*?['\"]",
        ]

        # Command Injection patterns
        self._cmd_patterns = [
            r"([`$\(\){}[\]|;&])",
            r"(rm\s+|kill\s+|curl\s+|wget\s+)",
        ]

        # Path Traversal patterns
        self._path_patterns = [
            r"(\.\.[\\/])+",
            r"(\.\.%2[fF])+",
        ]

        # XSS patterns
        self._xss_patterns = [
            r"(<script[^>]*>|</script>)",
            r"(javascript:|onerror=|onload=|onmouseover=)",
            r"(<iframe|<embed|<object)",
        ]

        # Script Injection patterns
        self._script_patterns = [
            r"(__import__|exec|eval|compile)",
            r"(pickle|marshal|subprocess)",
        ]

    def validate_input(self, value: Any, field_name: str = "input") -> bool:
        """
        Validate input against security patterns.

        Args:
            value: Input value to validate
            field_name: Name of field for logging

        Returns:
            True if valid, False if invalid

        Raises:
            SecurityViolation: If strict_mode and violation detected
        """
        if not isinstance(value, str):
            return True  # Non-string values assumed safe

        self._violations.clear()

        # Check SQL injection
        if self._check_sql_injection(value):
            violation = f"SQL Injection detected in {field_name}"
            self._violations.append(violation)
            if self.strict_mode:
                raise SecurityViolation(violation)
            return False

        # Check command injection
        if self._check_command_injection(value):
            violation = f"Command Injection detected in {field_name}"
            self._violations.append(violation)
            if self.strict_mode:
                raise SecurityViolation(violation)
            return False

        # Check path traversal
        if self._check_path_traversal(value):
            violation = f"Path Traversal detected in {field_name}"
            self._violations.append(violation)
            if self.strict_mode:
                raise SecurityViolation(violation)
            return False

        # Check XSS
        if self._check_xss(value):
            violation = f"XSS Injection detected in {field_name}"
            self._violations.append(violation)
            if self.strict_mode:
                raise SecurityViolation(violation)
            return False

        # Check script injection
        if self._check_script_injection(value):
            violation = f"Script Injection detected in {field_name}"
            self._violations.append(violation)
            if self.strict_mode:
                raise SecurityViolation(violation)
            return False

        return True

    def _check_sql_injection(self, value: str) -> bool:
        """Check for SQL injection patterns."""
        return any(
            re.search(pattern, value, re.IGNORECASE)
            for pattern in self._sql_patterns
        )

    def _check_command_injection(self, value: str) -> bool:
        """Check for command injection patterns."""
        return any(
            re.search(pattern, value, re.IGNORECASE)
            for pattern in self._cmd_patterns
        )

    def _check_path_traversal(self, value: str) -> bool:
        """Check for path traversal patterns."""
        return any(
            re.search(pattern, value, re.IGNORECASE)
            for pattern in self._path_patterns
        )

    def _check_xss(self, value: str) -> bool:
        """Check for XSS injection patterns."""
        return any(
            re.search(pattern, value, re.IGNORECASE)
            for pattern in self._xss_patterns
        )

    def _check_script_injection(self, value: str) -> bool:
        """Check for script injection patterns."""
        return any(
            re.search(pattern, value, re.IGNORECASE)
            for pattern in self._script_patterns
        )

    def get_violations(self) -> list[str]:
        """Get list of detected violations."""
        return self._violations.copy()


class OutputEncoder:
    """
    Encodes output to prevent injection attacks.

    Supports:
    - HTML encoding
    - JSON encoding
    - URL encoding
    - SQL parameter escaping
    - Shell escaping
    """

    @staticmethod
    def encode_html(text: str) -> str:
        """
        Encode text for safe HTML output.

        Args:
            text: Text to encode

        Returns:
            HTML-encoded text
        """
        return html.escape(text, quote=True)

    @staticmethod
    def encode_json(text: str) -> str:
        """
        Encode text for safe JSON output.

        Args:
            text: Text to encode

        Returns:
            JSON-encoded text
        """
        import json
        return json.dumps(text)

    @staticmethod
    def encode_url(text: str) -> str:
        """
        Encode text for safe URL parameters.

        Args:
            text: Text to encode

        Returns:
            URL-encoded text
        """
        from urllib.parse import quote
        return quote(text)

    @staticmethod
    def escape_sql(text: str) -> str:
        """
        Escape text for SQL queries.

        Args:
            text: Text to escape

        Returns:
            SQL-escaped text
        """
        # Replace single quotes with double single quotes
        return text.replace("'", "''")

    @staticmethod
    def escape_shell(text: str) -> str:
        """
        Escape text for shell execution.

        Args:
            text: Text to escape

        Returns:
            Shell-escaped text
        """
        from shlex import quote
        return quote(text)


class SecurityPolicy:
    """
    Enforces security policies for CORTEX operations.

    Policies:
    - Allowed input character sets
    - Allowed operations
    - Resource limits
    - Access controls
    """

    def __init__(self) -> None:
        """Initialize SecurityPolicy."""
        self.input_validator = InputValidator(strict_mode=True)
        self.output_encoder = OutputEncoder()
        self._policies: Dict[str, Any] = {}
        self._init_default_policies()

    def _init_default_policies(self) -> None:
        """Initialize default security policies."""
        self._policies = {
            "max_input_length": 10000,
            "max_recursion_depth": 100,
            "allowed_file_extensions": {".py", ".yaml", ".json", ".txt", ".md"},
            "forbidden_modules": {"os.system", "subprocess.call", "eval", "exec"},
            "require_auth": True,
            "timeout_seconds": 300,
        }

    def validate_policy(self, policy_name: str, value: Any) -> bool:
        """
        Validate value against security policy.

        Args:
            policy_name: Name of policy to check
            value: Value to validate

        Returns:
            True if policy satisfied, False otherwise
        """
        if policy_name == "max_input_length":
            return len(str(value)) <= self._policies["max_input_length"]
        elif policy_name == "max_recursion_depth":
            return True  # Implementation depends on runtime context
        elif policy_name == "allowed_file_extensions":
            if not isinstance(value, str):
                return True
            ext = Path(value).suffix
            return ext in self._policies["allowed_file_extensions"]
        elif policy_name == "forbidden_modules":
            if not isinstance(value, str):
                return True
            return not any(mod in value for mod in self._policies["forbidden_modules"])

        return True

    def get_policy(self, policy_name: str) -> Any:
        """
        Get security policy value.

        Args:
            policy_name: Name of policy

        Returns:
            Policy value
        """
        return self._policies.get(policy_name)

    def set_policy(self, policy_name: str, value: Any) -> None:
        """
        Set security policy value.

        Args:
            policy_name: Name of policy
            value: New policy value
        """
        self._policies[policy_name] = value


class SecurityContext:
    """
    Manages security context for operations.

    Provides:
    - Input validation before processing
    - Output encoding before returning
    - Security audit logging
    - Policy enforcement
    """

    def __init__(self, user_id: Optional[str] = None) -> None:
        """
        Initialize SecurityContext.

        Args:
            user_id: Optional user identifier for audit logging
        """
        self.user_id = user_id or "system"
        self.validator = InputValidator(strict_mode=True)
        self.encoder = OutputEncoder()
        self.policy = SecurityPolicy()
        self._audit_log: list[Dict[str, Any]] = []

    def validate_and_process(
        self, value: Any, field_name: str = "input", context: str = "general"
    ) -> Any:
        """
        Validate input and process safely.

        Args:
            value: Input value
            field_name: Field name for logging
            context: Operation context

        Returns:
            Validated value

        Raises:
            SecurityViolation: If validation fails
        """
        if isinstance(value, str):
            try:
                # Try validation in strict mode (will raise on violation)
                if not self.validator.validate_input(value, field_name):
                    self._log_violation(field_name, context, value)
                    raise SecurityViolation(f"Invalid input in {field_name}")
            except SecurityViolation:
                # Log before re-raising
                self._log_violation(field_name, context, value)
                raise

        return value

    def encode_response(self, value: Any, encoding: str = "html") -> str:
        """
        Encode response for safe output.

        Args:
            value: Value to encode
            encoding: Type of encoding (html, json, url, shell)

        Returns:
            Encoded value
        """
        str_value = str(value)

        if encoding == "html":
            return self.encoder.encode_html(str_value)
        elif encoding == "json":
            return self.encoder.encode_json(str_value)
        elif encoding == "url":
            return self.encoder.encode_url(str_value)
        elif encoding == "shell":
            return self.encoder.escape_shell(str_value)
        else:
            return str_value

    def _log_violation(
        self, field_name: str, context: str, value: str
    ) -> None:
        """
        Log security violation.

        Args:
            field_name: Field where violation occurred
            context: Operation context
            value: Violating value (truncated)
        """
        from datetime import datetime

        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": self.user_id,
            "field_name": field_name,
            "context": context,
            "violation_type": "input_validation_failure",
            "value_preview": value[:50] + "..." if len(value) > 50 else value,
        }
        self._audit_log.append(audit_entry)

    def get_audit_log(self) -> list[Dict[str, Any]]:
        """Get audit log entries."""
        return self._audit_log.copy()


__all__ = [
    "SecurityViolation",
    "InputValidator",
    "OutputEncoder",
    "SecurityPolicy",
    "SecurityContext",
]
