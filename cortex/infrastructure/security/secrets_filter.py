"""SecretsFilter compatibility implementation for log redaction tests."""

import logging
import re
from typing import Any, Dict, List, Pattern


class SecretsFilter(logging.Filter):
    """Redacts sensitive patterns from log text and tracks audit entries."""

    def __init__(self) -> None:
        super().__init__()
        self.patterns: Dict[str, Pattern[str]] = {}
        self.audit_log: List[Dict[str, Any]] = []
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        self.patterns = {
            "aws_access_key": re.compile(r"AKIA[0-9A-Z]{12,24}", re.IGNORECASE),
            "aws_secret_key": re.compile(r"(aws_secret_access_key\s*[=:]\s*)([^\s]+)", re.IGNORECASE),
            "github_token": re.compile(r"ghp_[A-Za-z0-9_]{8,}", re.IGNORECASE),
            "api_key_generic": re.compile(r"(api[_-]?key\s*[=:]\s*)([^\s]+)", re.IGNORECASE),
            "password_assignment": re.compile(r"(password\s*[=:]\s*)([^\s]+)", re.IGNORECASE),
            "connection_string": re.compile(r":([^@\s]+)@"),
            "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            "credit_card": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            "phone": re.compile(r"\+?1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}"),
            "jwt_bearer": re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/=]+"),
            "session_token": re.compile(r"(session[_-]?id\s*[=:]\s*)([A-Za-z0-9\-._]+)", re.IGNORECASE),
        }

    def add_custom_pattern(self, pattern: str, name: str) -> None:
        self.patterns[name] = re.compile(pattern, re.IGNORECASE)

    def mask_sensitive_data(self, text: str) -> str:
        if text is None:
            return ""

        masked = text
        for name, pattern in self.patterns.items():
            before = masked
            masked = pattern.sub(lambda match: self._replacement(match), masked)
            if before != masked:
                self.audit_log.append({"pattern": name, "action": "redacted"})
        return masked

    def _replacement(self, match: re.Match) -> str:
        if match.lastindex and match.lastindex >= 2:
            return f"{match.group(1)}[REDACTED]"
        if match.lastindex and match.lastindex == 1:
            return "[REDACTED]"
        return "[REDACTED]"

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
            redacted = self.mask_sensitive_data(message)
            record.msg = redacted
            record.args = ()
            return True
        except Exception:
            return True

    def redact_log_record(self, record: logging.LogRecord) -> str:
        self.filter(record)
        return str(record.msg)

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        return self.audit_log.copy()

    def clear_audit_trail(self) -> None:
        self.audit_log.clear()


__all__ = ["SecretsFilter"]
