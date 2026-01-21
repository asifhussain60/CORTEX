"""Security Tier2 - Advanced security hardening and credential protection.

Provides security violation detection, credential protection mechanisms,
and security event handling.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
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

    def __init__(self, policy_id: str = "default", name: str = "Default Security Policy") -> None:
        """Initialize security policy.

        Args:
            policy_id: Policy identifier.
            name: Human-readable policy name.
        """
        self.policy_id = policy_id
        self.name = name
        self.rules: Dict[str, Any] = {}
        self.permissions: Dict[str, bool] = {}
        self._policies: Dict[str, Any] = {
            "max_input_length": 10000,
            "allowed_file_extensions": [".py", ".yaml", ".yml", ".json", ".txt", ".md"],
            "forbidden_modules": ["os.system", "subprocess.call", "eval", "exec"],
        }

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
    
    def validate_policy(self, policy_name: str, value: Any) -> bool:
        """Validate value against a security policy.
        
        Args:
            policy_name: Name of the policy to validate against.
            value: Value to validate.
            
        Returns:
            True if valid, False otherwise.
        """
        if policy_name == "max_input_length":
            max_length = self._policies.get("max_input_length", 10000)
            if isinstance(value, str):
                return len(value) <= max_length
            return True
        
        elif policy_name == "allowed_file_extensions":
            if isinstance(value, str):
                allowed = self._policies.get("allowed_file_extensions", [])
                # Check if any allowed extension is in the value
                return any(value.endswith(ext) for ext in allowed)
            return True
        
        elif policy_name == "forbidden_modules":
            if isinstance(value, str):
                forbidden = self._policies.get("forbidden_modules", [])
                # Check if any forbidden module is in the value
                return not any(module in value for module in forbidden)
            return True
        
        return True
    
    def get_policy(self, policy_name: str) -> Any:
        """Get a policy value.
        
        Args:
            policy_name: Name of the policy.
            
        Returns:
            Policy value or None if not found.
        """
        return self._policies.get(policy_name)
    
    def set_policy(self, policy_name: str, value: Any) -> None:
        """Set a policy value.
        
        Args:
            policy_name: Name of the policy.
            value: Policy value.
        """
        self._policies[policy_name] = value


class SecurityContext:
    """Security context for request processing.

    Maintains security context, credentials, and permissions.
    """

    def __init__(self, user_id: str = "anonymous", session_id: str = "") -> None:
        """Initialize security context.

        Args:
            user_id: User identifier.
            session_id: Session identifier.
        """
        self.user_id = user_id
        self.session_id = session_id
        self.permissions: set = set()
        self.credentials: Dict[str, Any] = {}
        self._audit_log: List[Dict[str, Any]] = []
        self._validator = SecurityValidator(strict_mode=True)
        self._encoder = OutputEncoder()
        self.policy = SecurityPolicy()

    def validate_and_process(self, data: str, input_type: str, context: str) -> str:
        """Validate and process input data with security checks.

        Args:
            data: Input data to validate.
            input_type: Type of input (sql, cmd, path, etc.).
            context: Processing context.

        Returns:
            str: Validated data if safe.

        Raises:
            SecurityViolation: If validation fails.
        """
        try:
            self._validator.validate_input(data, input_type)
            return data
        except SecurityViolation as e:
            # Log the violation
            self._audit_log.append({
                "user_id": self.user_id,
                "violation_type": input_type,
                "context": context,
                "timestamp": __import__("datetime").datetime.now().isoformat(),
                "error": str(e)
            })
            raise

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log of security violations.

        Returns:
            List[Dict[str, Any]]: List of audit log entries.
        """
        return self._audit_log

    def encode_response(self, data: str, encoding_type: str) -> str:
        """Encode response data for safe output.

        Args:
            data: Data to encode.
            encoding_type: Type of encoding (html, json, url, sql).

        Returns:
            str: Encoded data.
        """
        if encoding_type == "html":
            return self._encoder.encode_html(data)
        elif encoding_type == "json":
            return self._encoder.encode_json(data)
        elif encoding_type == "url":
            return self._encoder.encode_url(data)
        elif encoding_type == "sql":
            return self._encoder.escape_sql(data)
        return data
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


class SecurityViolation(Exception):
    """Security violation exception.

    Attributes:
        violation_type: Type of violation.
        severity: Severity level (1-5).
        description: Violation description.
        timestamp: When violation occurred.
        context: Additional context.
    """

    def __init__(
        self,
        violation_type: ViolationType,
        severity: int,
        description: str,
        timestamp: datetime = None,
        context: Dict[str, Any] = None,
    ) -> None:
        """Initialize security violation.
        
        Args:
            violation_type: Type of violation.
            severity: Severity level (1-5).
            description: Violation description.
            timestamp: When violation occurred.
            context: Additional context.
        """
        self.violation_type = violation_type
        self.severity = severity
        self.description = description
        self.timestamp = timestamp if timestamp else datetime.now()
        self.context = context if context else {}
        super().__init__(self.description)


class SecurityValidator:
    """Validates input for security violations."""

    def __init__(self, strict_mode: bool = False) -> None:
        """Initialize security validator.
        
        Args:
            strict_mode: Enable strict validation mode.
        """
        self.violations: list = []
        self.strict_mode = strict_mode

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
    
    def validate_input(self, input_data: str, field_name: str = "") -> bool:
        """Validate input data for security violations.
        
        Args:
            input_data: Input string to validate.
            field_name: Field name for context.
            
        Returns:
            True if valid.
            
        Raises:
            SecurityViolation: If security violation detected in strict mode.
        """
        # SQL injection patterns
        sql_patterns = [
            "union select",
            "insert into",
            "delete from",
            "drop table",
            "' or '1'='1",
            "' or 1=1",
            "--",
            "/*",
            "*/",
            "exec(",
            "execute(",
        ]
        
        # XSS patterns
        xss_patterns = [
            "<script",
            "javascript:",
            "onerror=",
            "onload=",
            "<iframe",
        ]
        
        # Path traversal patterns
        path_traversal_patterns = [
            "../",
            "..\\",
            "/etc/passwd",
            "c:\\windows",
            "..%2f",
            "..%5c",
        ]
        
        # Command injection patterns
        command_patterns = [
            "; rm -rf",
            "rm -rf",
            "| cat",
            "`whoami`",
            "$(whoami)",
            "; ls",
            "| ls",
            "& dir",
        ]
        
        # Script injection patterns
        script_patterns = [
            "__import__",
            "eval(",
            "exec(",
            "pickle.loads",
            "import os",
            "import sys",
            "__builtins__",
        ]
        
        lower_input = input_data.lower()
        
        # Check SQL injection
        for pattern in sql_patterns:
            if pattern in lower_input:
                violation = SecurityViolation(
                    violation_type=ViolationType.INJECTION_ATTACK,
                    severity=5,
                    description=f"SQL injection detected in {field_name}: {pattern}",
                )
                self.violations.append(violation)
                if self.strict_mode:
                    raise violation
                return False
        
        # Check XSS
        for pattern in xss_patterns:
            if pattern in lower_input:
                violation = SecurityViolation(
                    violation_type=ViolationType.INJECTION_ATTACK,
                    severity=4,
                    description=f"XSS pattern detected in {field_name}: {pattern}",
                )
                self.violations.append(violation)
                if self.strict_mode:
                    raise violation
                return False
        
        # Check path traversal
        for pattern in path_traversal_patterns:
            if pattern in lower_input:
                violation = SecurityViolation(
                    violation_type=ViolationType.INJECTION_ATTACK,
                    severity=4,
                    description=f"Path traversal detected in {field_name}: {pattern}",
                )
                self.violations.append(violation)
                if self.strict_mode:
                    raise violation
                return False
        
        # Check command injection
        for pattern in command_patterns:
            if pattern in lower_input:
                violation = SecurityViolation(
                    violation_type=ViolationType.INJECTION_ATTACK,
                    severity=5,
                    description=f"Command injection detected in {field_name}: {pattern}",
                )
                self.violations.append(violation)
                if self.strict_mode:
                    raise violation
                return False
        
        # Check script injection
        for pattern in script_patterns:
            if pattern in lower_input:
                violation = SecurityViolation(
                    violation_type=ViolationType.INJECTION_ATTACK,
                    severity=5,
                    description=f"Script injection detected in {field_name}: {pattern}",
                )
                self.violations.append(violation)
                if self.strict_mode:
                    raise violation
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
    def encode_url(text: str) -> str:
        """URL-encode text.

        Args:
            text: Text to encode.

        Returns:
            URL-encoded text.
        """
        from urllib.parse import quote
        return quote(text)
    
    @staticmethod
    def escape_sql(text: str) -> str:
        """Escape SQL special characters.

        Args:
            text: Text to escape.

        Returns:
            SQL-escaped text.
        """
        # Double single quotes for SQL escaping
        return text.replace("'", "''")

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

