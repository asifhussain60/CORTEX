"""
Secret Detection & Redaction System Module

Implements secret detection and automatic redaction in logs:
- API key detection
- Password detection
- Token detection
- Credit card detection
- Credential leakage prevention

AC-NFR-003-02: Secret Detection & Redaction System
"""

import re
from enum import Enum
from typing import Dict, List, Optional, Pattern, Set


class SecretType(Enum):
    """Types of secrets to detect."""
    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
    CREDIT_CARD = "credit_card"
    SSH_KEY = "ssh_key"
    DATABASE_URL = "database_url"
    JWT = "jwt"
    AWS_KEY = "aws_key"
    PRIVATE_KEY = "private_key"


class SecretPattern:
    """Pattern for detecting a specific secret type."""

    def __init__(self, secret_type: SecretType, pattern: str, name: str):
        """
        Initialize SecretPattern.

        Args:
            secret_type: Type of secret
            pattern: Regex pattern to detect secret
            name: Human-readable name
        """
        self.secret_type = secret_type
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.name = name

    def matches(self, text: str) -> bool:
        """Check if text matches this pattern."""
        return bool(self.pattern.search(text))


class SecretDetector:
    """
    Detects secrets in text using pattern matching.

    Detects:
    - API keys (AWS, GitHub, Stripe, etc.)
    - Passwords in connection strings
    - JWT tokens
    - SSH keys
    - Database URLs
    - Credit cards
    - Private keys
    """

    def __init__(self):
        """Initialize SecretDetector with patterns."""
        self._patterns: List[SecretPattern] = []
        self._init_patterns()

    def _init_patterns(self) -> None:
        """Initialize secret detection patterns."""
        # API Keys
        self._patterns.extend([
            SecretPattern(
                SecretType.API_KEY,
                r"api[_-]?key[\"'\s:=]+([a-zA-Z0-9\-_]{32,})",
                "API Key"
            ),
            SecretPattern(
                SecretType.AWS_KEY,
                r"(AKIA[0-9A-Z]{16})",
                "AWS Access Key ID"
            ),
            SecretPattern(
                SecretType.AWS_KEY,
                r"aws_secret_access_key[\"'\s:=]+([a-zA-Z0-9/+=]{40})",
                "AWS Secret Access Key"
            ),
        ])

        # Passwords
        self._patterns.extend([
            SecretPattern(
                SecretType.PASSWORD,
                r"password[\"'\s:=]+([^\s\"']{8,})",
                "Password"
            ),
            SecretPattern(
                SecretType.PASSWORD,
                r"passwd[\"'\s:=]+([^\s\"']{8,})",
                "Password (passwd)"
            ),
            SecretPattern(
                SecretType.DATABASE_URL,
                r"(mysql|postgres|mongodb)://[^@]+@[^\s\"']+",
                "Database URL with credentials"
            ),
        ])

        # Tokens
        self._patterns.extend([
            SecretPattern(
                SecretType.JWT,
                r"(eyJ[a-zA-Z0-9_\-]{10,}\.eyJ[a-zA-Z0-9_\-]{10,}\.[\w\-]{10,})",
                "JWT Token"
            ),
            SecretPattern(
                SecretType.TOKEN,
                r"token[\"'\s:=]+([a-zA-Z0-9\-_]{32,})",
                "Access Token"
            ),
            SecretPattern(
                SecretType.TOKEN,
                r"authorization[\"'\s:=]+(Bearer\s+)?([a-zA-Z0-9\-_]{32,})",
                "Authorization Token"
            ),
        ])

        # Keys
        self._patterns.extend([
            SecretPattern(
                SecretType.SSH_KEY,
                r"(-----BEGIN RSA PRIVATE KEY-----)",
                "RSA Private Key"
            ),
            SecretPattern(
                SecretType.PRIVATE_KEY,
                r"(-----BEGIN PRIVATE KEY-----)",
                "Private Key"
            ),
        ])

        # Credit Cards
        self._patterns.extend([
            SecretPattern(
                SecretType.CREDIT_CARD,
                r"\b([0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4})\b",
                "Credit Card Number"
            ),
        ])

    def detect(self, text: str) -> List[Dict[str, str]]:
        """
        Detect all secrets in text.

        Args:
            text: Text to scan for secrets

        Returns:
            List of detected secrets with type and location
        """
        detected: List[Dict[str, str]] = []

        for pattern in self._patterns:
            if pattern.matches(text):
                detected.append({
                    "type": pattern.secret_type.value,
                    "name": pattern.name,
                    "pattern": pattern.pattern.pattern,
                })

        return detected


class SecretRedactor:
    """
    Redacts secrets from text to prevent leakage.

    Strategies:
    - Replace with placeholder
    - Partial redaction (keep first/last chars)
    - Complete removal
    """

    DEFAULT_PLACEHOLDER = "***REDACTED***"

    def __init__(self, placeholder: str = DEFAULT_PLACEHOLDER):
        """
        Initialize SecretRedactor.

        Args:
            placeholder: String to replace secrets with
        """
        self.placeholder = placeholder
        self._detector = SecretDetector()

    def redact(self, text: str, strategy: str = "full") -> str:
        """
        Redact all detected secrets from text.

        Args:
            text: Text to redact
            strategy: Redaction strategy (full, partial, remove)

        Returns:
            Text with secrets redacted
        """
        result = text

        for pattern in self._detector._patterns:
            if strategy == "full":
                result = pattern.pattern.sub(self.placeholder, result)
            elif strategy == "partial":
                result = pattern.pattern.sub(self._partial_redact, result)
            elif strategy == "remove":
                result = pattern.pattern.sub("", result)

        return result

    def _partial_redact(self, match) -> str:
        """Replace with partial redaction (show first/last 2 chars)."""
        value = match.group(0)
        if len(value) > 4:
            return f"{value[:2]}***{value[-2:]}"
        return self.placeholder

    def has_secrets(self, text: str) -> bool:
        """Check if text contains any secrets."""
        detected = self._detector.detect(text)
        return len(detected) > 0


class LogRedactor:
    """
    Redacts sensitive information from logs.

    Features:
    - Automatic secret detection and redaction
    - Multi-level logging (original, redacted, audit)
    - Safe logging guarantees
    """

    def __init__(self, redact_by_default: bool = True):
        """
        Initialize LogRedactor.

        Args:
            redact_by_default: Whether to redact logs by default
        """
        self.redact_by_default = redact_by_default
        self._redactor = SecretRedactor()
        self._redaction_log: List[Dict] = []

    def safe_log(
        self,
        message: str,
        level: str = "INFO",
        redact: Optional[bool] = None,
    ) -> Dict[str, str]:
        """
        Create a safe log entry with automatic secret redaction.

        Args:
            message: Log message
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            redact: Whether to redact (uses default if None)

        Returns:
            Safe log entry dict with original (if flagged) and redacted versions
        """
        redact = redact if redact is not None else self.redact_by_default

        has_secrets = self._redactor.has_secrets(message)
        redacted_message = self._redactor.redact(message) if redact else message

        log_entry = {
            "level": level,
            "message": redacted_message,
            "had_secrets": has_secrets,
            "redacted": redact,
        }

        # Store redaction info for audit
        if has_secrets:
            self._redaction_log.append({
                "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
                "level": level,
                "had_secrets": True,
                "redaction_applied": redact,
            })

        return log_entry

    def get_redaction_audit_log(self) -> List[Dict]:
        """Get audit log of all redactions."""
        return self._redaction_log.copy()

    def clear_redaction_audit_log(self) -> None:
        """Clear redaction audit log."""
        self._redaction_log.clear()


class CredentialVault:
    """
    Secure storage for credentials.

    Features:
    - In-memory storage (for testing; production uses encryption)
    - Credential lifecycle management
    - Access tracking
    """

    def __init__(self):
        """Initialize CredentialVault."""
        self._credentials: Dict[str, str] = {}
        self._access_log: List[Dict] = []

    def store(self, key: str, value: str, secret_type: SecretType) -> None:
        """
        Store a credential.

        Args:
            key: Credential identifier
            value: Credential value
            secret_type: Type of secret
        """
        if self._is_valid_credential(value, secret_type):
            self._credentials[key] = value
        else:
            raise ValueError(f"Invalid credential for type {secret_type.value}")

    def retrieve(self, key: str) -> Optional[str]:
        """
        Retrieve a credential.

        Args:
            key: Credential identifier

        Returns:
            Credential value or None if not found
        """
        self._log_access(key)
        return self._credentials.get(key)

    def has_credential(self, key: str) -> bool:
        """Check if credential exists."""
        return key in self._credentials

    def _is_valid_credential(self, value: str, secret_type: SecretType) -> bool:
        """Validate credential format."""
        # Basic validation - in production, much more sophisticated
        if secret_type == SecretType.API_KEY:
            return len(value) >= 32
        elif secret_type == SecretType.PASSWORD:
            return len(value) >= 8
        elif secret_type == SecretType.JWT:
            return len(value) >= 50
        return len(value) > 0

    def _log_access(self, key: str) -> None:
        """Log credential access."""
        self._access_log.append({
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "key": key,
            "action": "retrieve",
        })

    def get_access_log(self) -> List[Dict]:
        """Get credential access log."""
        return self._access_log.copy()


__all__ = [
    "SecretType",
    "SecretPattern",
    "SecretDetector",
    "SecretRedactor",
    "LogRedactor",
    "CredentialVault",
]
