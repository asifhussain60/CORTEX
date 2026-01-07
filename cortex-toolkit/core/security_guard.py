"""
Security Guard for CORTEX Toolkit.

This module provides:
- Input sanitization and validation
- Shell injection prevention
- Path traversal prevention
- SQL injection pattern detection
- XSS pattern detection
- Privilege level enforcement

Part of Phase 6: Security Hardening implementation.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Pattern
import urllib.parse


# =============================================================================
# Constants
# =============================================================================

class Severity(Enum):
    """Severity levels for security violations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PrivilegeLevel(Enum):
    """Privilege levels for tool execution."""
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"


# Default forbidden patterns
DEFAULT_FORBIDDEN_PATTERNS = {
    "shell_metachar": [
        r'[;&|]',             # Shell command separators
        r'`',                 # Backtick command substitution
        r'\$\(',              # Dollar-paren command substitution
    ],
    "path_traversal": [
        r'\.\.',              # Path traversal
        r'%2e%2e',            # URL-encoded path traversal
        r'%252e%252e',        # Double-encoded path traversal
    ],
    "absolute_path": [
        r'^/',                # Unix absolute paths
        r'^[A-Za-z]:',        # Windows drive paths
    ],
    "unc_path": [
        r'\\\\',              # UNC paths
        r'^//',               # Forward slash UNC
    ],
    "sql_injection": [
        r'DROP\s+TABLE',      # DROP TABLE
        r'DELETE\s+FROM',     # DELETE FROM
        r'UNION\s+SELECT',    # UNION SELECT
        r"'\s*OR\s*'",        # OR injection
        r"'\s*OR\s+\d",       # OR 1=1 pattern
        r';\s*--',            # Comment injection
    ],
    "xss": [
        r'<\s*script',        # Script tags
        r'javascript:',       # JavaScript protocol
        r'on\w+\s*=',         # Event handlers
        r'<\s*iframe',        # Iframe tags
    ],
}


# Sensitive argument names that should be masked
SENSITIVE_PATTERNS = [
    r'password',
    r'passwd',
    r'secret',
    r'api[_-]?key',
    r'token',
    r'auth',
    r'credential',
]


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class SecurityViolation:
    """Represents a security violation detected in arguments."""
    
    arg_index: int
    argument: str
    pattern: str
    pattern_type: str
    severity: str
    
    def __str__(self) -> str:
        return (
            f"SecurityViolation(arg[{self.arg_index}]: '{self.argument[:50]}...', "
            f"type={self.pattern_type}, severity={self.severity})"
        )


@dataclass
class SanitizeResult:
    """Result of argument sanitization."""
    
    safe: bool
    violations: List[SecurityViolation] = field(default_factory=list)
    sanitized_args: Optional[List[str]] = None
    
    def get_summary(self) -> str:
        """Get a summary of the sanitization result."""
        if self.safe:
            return "All arguments passed security validation."
        
        critical_count = sum(1 for v in self.violations if v.severity == "critical")
        high_count = sum(1 for v in self.violations if v.severity == "high")
        
        return (
            f"Security violations detected: {len(self.violations)} total "
            f"({critical_count} critical, {high_count} high severity)"
        )


@dataclass
class PrivilegeCheckResult:
    """Result of privilege level check."""
    
    allowed: bool
    reason: str
    required_level: str
    current_level: str


# =============================================================================
# SecurityGuard Class
# =============================================================================

class SecurityGuard:
    """
    Input validation and security checks for toolkit operations.
    
    Features:
    - Shell injection prevention
    - Path traversal detection
    - SQL injection pattern detection
    - XSS pattern detection
    - Privilege level enforcement
    """
    
    def __init__(
        self,
        additional_patterns: Optional[List[str]] = None,
        strict_mode: bool = False
    ):
        """
        Initialize SecurityGuard.
        
        Args:
            additional_patterns: Extra patterns to check beyond defaults.
            strict_mode: Enable stricter validation rules.
        """
        self.strict_mode = strict_mode
        self.forbidden_patterns = self._build_patterns(additional_patterns)
        self._compiled_patterns: Dict[str, List[Pattern]] = {}
        self._compile_patterns()
    
    def _build_patterns(
        self, 
        additional: Optional[List[str]]
    ) -> Dict[str, List[str]]:
        """Build complete pattern dictionary."""
        patterns = {k: list(v) for k, v in DEFAULT_FORBIDDEN_PATTERNS.items()}
        
        if additional:
            patterns["custom"] = additional
        
        return patterns
    
    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for performance."""
        for pattern_type, patterns in self.forbidden_patterns.items():
            self._compiled_patterns[pattern_type] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]
    
    # =========================================================================
    # Sanitization Methods
    # =========================================================================
    
    def sanitize_arguments(
        self,
        args: List[Any],
        allow_absolute: bool = False
    ) -> SanitizeResult:
        """
        Validate and sanitize all arguments.
        
        Args:
            args: List of command-line arguments.
            allow_absolute: Whether to allow absolute paths.
            
        Returns:
            SanitizeResult with safety status and any violations.
        """
        violations: List[SecurityViolation] = []
        
        for i, arg in enumerate(args):
            # Handle None values
            if arg is None:
                continue
            
            # Convert to string
            arg_str = str(arg)
            
            # Check each pattern type
            arg_violations = self._check_argument(i, arg_str, allow_absolute)
            violations.extend(arg_violations)
        
        return SanitizeResult(
            safe=len(violations) == 0,
            violations=violations,
            sanitized_args=[str(a) if a is not None else "" for a in args]
        )
    
    def _check_argument(
        self,
        index: int,
        arg: str,
        allow_absolute: bool
    ) -> List[SecurityViolation]:
        """Check a single argument against all patterns."""
        violations = []
        
        # URL decode to catch encoded attacks
        try:
            decoded_arg = urllib.parse.unquote(arg)
        except Exception:
            decoded_arg = arg
        
        for pattern_type, compiled_patterns in self._compiled_patterns.items():
            # Skip absolute path check if allowed
            if pattern_type == "absolute_path" and allow_absolute:
                continue
            
            for pattern in compiled_patterns:
                # Check both original and decoded
                if pattern.search(arg) or pattern.search(decoded_arg):
                    severity = self._get_severity(pattern_type)
                    violations.append(SecurityViolation(
                        arg_index=index,
                        argument=arg,
                        pattern=pattern.pattern,
                        pattern_type=pattern_type,
                        severity=severity.value
                    ))
                    # Break after first match of this type
                    break
        
        return violations
    
    def _get_severity(self, pattern_type: str) -> Severity:
        """Get severity level for a pattern type."""
        severity_map = {
            "shell_metachar": Severity.CRITICAL,
            "sql_injection": Severity.CRITICAL,
            "xss": Severity.HIGH,
            "path_traversal": Severity.HIGH,
            "absolute_path": Severity.MEDIUM,
            "unc_path": Severity.HIGH,
            "custom": Severity.MEDIUM,
        }
        return severity_map.get(pattern_type, Severity.MEDIUM)
    
    # =========================================================================
    # Privilege Level Methods
    # =========================================================================
    
    def check_privilege(
        self,
        tool_name: str,
        required_level: str = "user",
        current_level: str = "user",
        system_flag: bool = False
    ) -> PrivilegeCheckResult:
        """
        Check if current privilege level allows tool execution.
        
        Args:
            tool_name: Name of the tool being executed.
            required_level: Privilege level required by the tool.
            current_level: Current user's privilege level.
            system_flag: Whether system-level execution is explicitly enabled.
            
        Returns:
            PrivilegeCheckResult with allowed status and reason.
        """
        level_order = {"user": 0, "admin": 1, "system": 2}
        
        required_int = level_order.get(required_level, 0)
        current_int = level_order.get(current_level, 0)
        
        # System level requires explicit flag
        if required_level == "system" and not system_flag:
            return PrivilegeCheckResult(
                allowed=False,
                reason=f"Tool '{tool_name}' requires system-level privileges with explicit flag.",
                required_level=required_level,
                current_level=current_level
            )
        
        # Check privilege hierarchy
        if current_int >= required_int:
            return PrivilegeCheckResult(
                allowed=True,
                reason="Sufficient privileges.",
                required_level=required_level,
                current_level=current_level
            )
        else:
            return PrivilegeCheckResult(
                allowed=False,
                reason=f"Tool '{tool_name}' requires {required_level} privileges, current level is {current_level}.",
                required_level=required_level,
                current_level=current_level
            )
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def is_sensitive_argument(self, arg_name: str) -> bool:
        """Check if an argument name indicates sensitive data."""
        arg_lower = arg_name.lower().strip('-')
        
        for pattern in SENSITIVE_PATTERNS:
            if re.search(pattern, arg_lower, re.IGNORECASE):
                return True
        
        return False
    
    def mask_sensitive_value(self, value: str) -> str:
        """Mask a sensitive value for logging."""
        if len(value) <= 4:
            return "****"
        return value[:2] + "****" + value[-2:]
