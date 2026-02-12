"""
SecretsFilter - redacts sensitive data from logs and outputs.

Prevents credential exposure through logging by detecting and masking API keys,
passwords, PII, and other sensitive patterns before they reach log output.

Author: CORTEX Implementation
Phase: impl-arch-005-hardening (HARD-PROD-001-01)
Compliance: CORE-011 (100% typed), CORE-012 (Google docstrings), CORE-013 (no bare except)
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern


class SecretsFilter(logging.Filter):
    """Redacts sensitive data from logs and outputs.

    Prevents exposure of secrets like API keys, passwords, and PII by
    detecting common patterns and replacing them with [REDACTED] markers.
    Maintains audit trail of what was redacted and why.

    Attributes:
        patterns: Dictionary of secret patterns to detect
        audit_log: List of redaction audit trail entries
    """

    def __init__(self) -> None:
        """Initialize SecretsFilter with default patterns.

        Sets up standard patterns for API keys, passwords, PII, and tokens.
        Initializes empty audit trail.
        """
        super().__init__()
        self.patterns: Dict[str, Pattern[str]] = {}
        self.audit_log: List[Dict[str, Any]] = []
        self.compile_patterns()

    def compile_patterns(self) -> None:
        """Compile regex patterns for secret detection.

        Compiles patterns for:
        - AWS credentials (access key, secret key)
        - GitHub tokens
        - Generic API key patterns
        - Database connection strings with passwords
        - Social Security Numbers
        - Credit card numbers
        - Email addresses
        - Phone numbers
        - JWT/Bearer tokens

        Uses case-insensitive matching for improved detection rate.
        """
        self.patterns = {
            "aws_access_key": re.compile(
                r"AKIA[0-9A-Z]{16}",
                re.IGNORECASE
            ),
            "aws_secret_key": re.compile(
                r"aws_secret_access_key['\"]?\s*[=:]\s*['\"]?([A-Za-z0-9/+=]{40})",
                re.IGNORECASE
            ),
            "github_token": re.compile(
                r"ghp_[A-Za-z0-9_]{36}",
                re.IGNORECASE
            ),
            "api_key_generic": re.compile(
                r"(api[_-]?key|apikey)['\"]?\s*[=:]\s*['\"]?([A-Za-z0-9\-_.]{20,})['\"]?",
                re.IGNORECASE
            ),
            "password_assignment": re.compile(
                r"(password|passwd|pwd)['\"]?\s*[=:]\s*['\"]?([^'\"\\s\]]+)",
                re.IGNORECASE
            ),
            "connection_string": re.compile(
                r"(?:connection_string|connection)[_-]string)['\"]?\s*[=:]\s*['\"]?([^'\"]+[^'\"\\s])['\"]?",
                re.IGNORECASE
            ),
            "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            "credit_card": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "phone": re.compile(r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b"),
            "jwt_bearer": re.compile(r"Bearer\s+([A-Za-z0-9\-._~+/]+=*)+"),
            "session_token": re.compile(r"(?:session|token))['\"]?\s*[=:]\s*['\"]?([A-Za-z0-9\-._]+)['\"]?"),
        }

    def add_custom_pattern(self, pattern: str, name: str) -> None:
        """Add a custom secret pattern.

        Args:
            pattern: Regex pattern string to compile and add
            name: Name/identifier for this pattern

        Raises:
            ValueError: If pattern is invalid regex
        """
        try:
            self.patterns[name] = re.compile(pattern, re.IGNORECASE)
        except re.error as err:
            raise ValueError(f"Invalid regex pattern: {err}") from err

    def mask_sensitive_data(self, text: str) -> str:
        """Mask sensitive data in text.

        Searches text for all known secret patterns and replaces them
        with [REDACTED] markers. Records redaction in audit trail.

        Args:
            text: Text to mask

        Returns:
            Text with sensitive data replaced by [REDACTED]
        """
        if text is None:
            return text

        try:
            masked_text = text
            for pattern_name, pattern in self.patterns.items():
                matches = list(pattern.finditer(text))
                if matches:
                    masked_text = pattern.sub("[REDACTED]", masked_text)
                    self.audit_log.append({
                        "pattern": pattern_name,
                        "count": len(matches),
                        "action": "redacted"
                    })
            return masked_text
        except (TypeError, AttributeError):
            # Handle non-string inputs gracefully
            return str(text)

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record by masking sensitive data.

        This is the main logging.Filter entry point. Called by logging
        system on each log record. Masks any sensitive data found.

        Args:
            record: The log record to filter

        Returns:
            True to allow the record, False to drop it (always returns True)
        """
        try:
            # Mask message
            if record.msg:
                if isinstance(record.msg, str):
                    record.msg = self.mask_sensitive_data(record.msg)

            # Mask exception traceback
            if record.exc_info:
                record.exc_text = self.mask_sensitive_data(
                    record.exc_text or ""
                )

            # Mask args
            if record.args:
                if isinstance(record.args, dict):
                    record.args = {
                        k: self.mask_sensitive_data(str(v))
                        if isinstance(v, str) else v
                        for k, v in record.args.items()
                    }
                elif isinstance(record.args, tuple):
                    record.args = tuple(
                        self.mask_sensitive_data(arg)
                        if isinstance(arg, str) else arg
                        for arg in record.args
                    )

            return True
        except Exception:  # CORE-013: Explicit exception (not bare except)
            # If redaction fails, still allow the record to be logged
            return True

    def redact_log_record(self, record: logging.LogRecord) -> None:
        """Redact a log record in-place.

        Args:
            record: The log record to redact
        """
        self.filter(record)

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Get audit trail of redactions.

        Returns:
            List of redaction audit entries
        """
        return self.audit_log.copy()

    def clear_audit_trail(self) -> None:
        """Clear audit trail (useful for testing)."""
        self.audit_log.clear()
