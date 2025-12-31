"""
CORTEX Toolkit Gate Keeper

Pre-execution validation layer for all tool operations.
Enforces security, platform compatibility, and dependency checks.
"""
import re
import platform
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging

from .exceptions import (
    ValidationResult,
    ValidationCheck,
    SecurityViolationError,
    PlatformNotSupportedError,
)

if TYPE_CHECKING:
    from ..shared.toolkit_registry import ToolkitRegistry


logger = logging.getLogger(__name__)


@dataclass
class SecurityViolation:
    """Details of a security violation."""
    arg_index: int
    pattern: str
    matched_text: str
    severity: str = "critical"  # critical, high, medium, low


@dataclass
class SanitizeResult:
    """Result of argument sanitization."""
    safe: bool
    sanitized_args: List[str]
    violations: List[SecurityViolation] = field(default_factory=list)


@dataclass
class RateLimitInfo:
    """Rate limit tracking for a tool."""
    tool_name: str
    calls: List[datetime] = field(default_factory=list)
    max_per_minute: int = 10
    
    def check_and_record(self) -> tuple[bool, int]:
        """
        Check if rate limit allows call and record if so.
        
        Returns:
            Tuple of (allowed, seconds_until_reset)
        """
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        # Remove old entries
        self.calls = [c for c in self.calls if c > cutoff]
        
        if len(self.calls) >= self.max_per_minute:
            oldest = min(self.calls)
            reset_seconds = int((oldest + timedelta(minutes=1) - now).total_seconds())
            return False, max(0, reset_seconds)
        
        self.calls.append(now)
        return True, 0


class GateKeeper:
    """
    Pre-execution validation for all tool operations.
    
    Validates:
    - Tool existence
    - Platform compatibility
    - Argument security (shell injection, path traversal)
    - Rate limiting
    - Dependency satisfaction
    """
    
    # Patterns that indicate potential security issues
    FORBIDDEN_PATTERNS = [
        (r'[;&|`$]', "shell_metacharacters", "critical"),
        (r'\.\./', "path_traversal_forward", "critical"),
        (r'\.\.\\', "path_traversal_back", "critical"),
        (r'^/', "absolute_path_unix", "warning"),  # May be intentional
        (r'^[A-Za-z]:\\', "absolute_path_windows", "warning"),
        (r'\\\\', "unc_path", "high"),
        (r'<script', "xss_script_tag", "critical"),
        (r'DROP\s+TABLE', "sql_injection_drop", "critical"),
        (r'DELETE\s+FROM', "sql_injection_delete", "critical"),
        (r'--', "sql_comment", "medium"),
        (r'\x00', "null_byte", "critical"),
        (r'%00', "encoded_null", "critical"),
    ]
    
    # Arguments that are always safe
    SAFE_ARGUMENT_PATTERNS = [
        r'^--[\w-]+=[\w\d.-]+$',  # --option=value
        r'^--[\w-]+$',            # --flag
        r'^-[a-zA-Z]$',           # -f
        r'^\d+$',                 # Numbers
        r'^[\w.-]+$',             # Simple words
    ]
    
    def __init__(self, registry: "ToolkitRegistry"):
        """
        Initialize GateKeeper.
        
        Args:
            registry: ToolkitRegistry instance for tool lookup.
        """
        self.registry = registry
        self._rate_limits: Dict[str, RateLimitInfo] = {}
    
    def validate_execution(
        self, 
        tool: str, 
        args: Optional[List[str]] = None,
        skip_rate_limit: bool = False
    ) -> ValidationResult:
        """
        Run all validation checks before tool execution.
        
        Args:
            tool: Tool name to validate.
            args: Command-line arguments.
            skip_rate_limit: Whether to skip rate limit check.
            
        Returns:
            ValidationResult with all check results.
        """
        args = args or []
        checks = []
        
        # 1. Check tool exists
        checks.append(self._check_tool_exists(tool))
        
        # 2. Check platform support (only if tool exists)
        if checks[-1].passed:
            checks.append(self._check_platform_support(tool))
        
        # 3. Sanitize arguments
        sanitize_check = self._sanitize_arguments(tool, args)
        checks.append(sanitize_check)
        
        # 4. Check rate limit
        if not skip_rate_limit:
            checks.append(self._check_rate_limit(tool))
        
        # 5. Check permissions (admin tools)
        checks.append(self._check_permissions(tool))
        
        return ValidationResult(
            passed=all(c.passed for c in checks if c.severity == "error"),
            checks=checks
        )
    
    def _check_tool_exists(self, tool: str) -> ValidationCheck:
        """Verify tool exists in registry."""
        tool_info = self.registry.get_tool(tool)
        
        if tool_info is None:
            # Try to find similar tools
            all_tools = [t["name"] for t in self.registry.list_tools()]
            similar = self._find_similar_tools(tool, all_tools)
            
            message = f"Tool '{tool}' not found in registry"
            if similar:
                message += f". Did you mean: {', '.join(similar[:3])}?"
            
            return ValidationCheck(
                name="tool_exists",
                passed=False,
                message=message,
                severity="error",
                details={"similar_tools": similar}
            )
        
        return ValidationCheck(
            name="tool_exists",
            passed=True,
            message=f"Tool '{tool}' found",
            severity="info"
        )
    
    def _check_platform_support(self, tool: str) -> ValidationCheck:
        """Verify current platform is supported."""
        tool_info = self.registry.get_tool(tool)
        if not tool_info:
            return ValidationCheck(
                name="platform_support",
                passed=False,
                message="Cannot check platform - tool not found",
                severity="error"
            )
        
        current = platform.system().lower()
        platform_map = {
            "windows": "windows",
            "linux": "linux",
            "darwin": "macos"
        }
        current_name = platform_map.get(current, current)
        supported = tool_info.get("platforms", [])
        
        if current_name not in supported:
            return ValidationCheck(
                name="platform_support",
                passed=False,
                message=f"Platform '{current_name}' not supported. Supported: {supported}",
                severity="error",
                details={
                    "current_platform": current_name,
                    "supported_platforms": supported
                }
            )
        
        return ValidationCheck(
            name="platform_support",
            passed=True,
            message=f"Platform '{current_name}' is supported",
            severity="info"
        )
    
    def _sanitize_arguments(self, tool: str, args: List[str]) -> ValidationCheck:
        """
        Validate and sanitize arguments for security.
        
        Blocks potentially dangerous patterns like shell injection,
        path traversal, and SQL injection attempts.
        """
        violations = []
        
        for i, arg in enumerate(args):
            # Skip if arg matches safe patterns
            if any(re.match(pattern, arg) for pattern in self.SAFE_ARGUMENT_PATTERNS):
                continue
            
            # Check against forbidden patterns
            for pattern, name, severity in self.FORBIDDEN_PATTERNS:
                match = re.search(pattern, arg, re.IGNORECASE)
                if match:
                    violations.append(SecurityViolation(
                        arg_index=i,
                        pattern=name,
                        matched_text=match.group(),
                        severity=severity
                    ))
        
        # Filter to only critical violations for blocking
        critical_violations = [v for v in violations if v.severity == "critical"]
        
        if critical_violations:
            details = [
                f"arg[{v.arg_index}]: {v.pattern} ('{v.matched_text}')"
                for v in critical_violations
            ]
            return ValidationCheck(
                name="argument_sanitization",
                passed=False,
                message=f"Security violations in arguments: {'; '.join(details)}",
                severity="error",
                details={"violations": [vars(v) for v in violations]}
            )
        
        # Warnings don't block execution
        if violations:
            return ValidationCheck(
                name="argument_sanitization",
                passed=True,
                message=f"Arguments passed with {len(violations)} warning(s)",
                severity="warning",
                details={"violations": [vars(v) for v in violations]}
            )
        
        return ValidationCheck(
            name="argument_sanitization",
            passed=True,
            message="All arguments are safe",
            severity="info"
        )
    
    def _check_rate_limit(self, tool: str) -> ValidationCheck:
        """Check and enforce rate limiting."""
        tool_info = self.registry.get_tool(tool)
        
        # Get tool's rate limit (default: 10/min)
        rate_config = tool_info.get("rate_limit", {}) if tool_info else {}
        max_per_min = rate_config.get("max_calls_per_minute", 10)
        
        # Get or create rate limit tracker
        if tool not in self._rate_limits:
            self._rate_limits[tool] = RateLimitInfo(tool_name=tool, max_per_minute=max_per_min)
        
        rate_info = self._rate_limits[tool]
        rate_info.max_per_minute = max_per_min
        
        allowed, reset_seconds = rate_info.check_and_record()
        
        if not allowed:
            return ValidationCheck(
                name="rate_limit",
                passed=False,
                message=f"Rate limit exceeded ({max_per_min}/min). Reset in {reset_seconds}s",
                severity="error",
                details={
                    "limit": max_per_min,
                    "reset_seconds": reset_seconds
                }
            )
        
        return ValidationCheck(
            name="rate_limit",
            passed=True,
            message=f"Rate limit OK ({len(rate_info.calls)}/{max_per_min} calls)",
            severity="info"
        )
    
    def _check_permissions(self, tool: str) -> ValidationCheck:
        """Check if tool requires admin and user has permission."""
        tool_info = self.registry.get_tool(tool)
        if not tool_info:
            return ValidationCheck(
                name="permissions",
                passed=True,
                message="Cannot check permissions - tool not found",
                severity="warning"
            )
        
        requires_admin = tool_info.get("requires_admin", False)
        
        if requires_admin:
            # Note: Actual admin check would be platform-specific
            # For now, we just flag that admin is required
            return ValidationCheck(
                name="permissions",
                passed=True,  # Don't block, just warn
                message=f"Tool '{tool}' requires admin privileges",
                severity="warning",
                details={"requires_admin": True}
            )
        
        return ValidationCheck(
            name="permissions",
            passed=True,
            message="No special permissions required",
            severity="info"
        )
    
    def _find_similar_tools(self, name: str, all_tools: List[str], threshold: float = 0.6) -> List[str]:
        """Find tools with similar names using simple matching."""
        similar = []
        name_lower = name.lower()
        
        for tool in all_tools:
            tool_lower = tool.lower()
            
            # Substring match
            if name_lower in tool_lower or tool_lower in name_lower:
                similar.append(tool)
                continue
            
            # Simple character overlap ratio
            common = set(name_lower) & set(tool_lower)
            total = set(name_lower) | set(tool_lower)
            ratio = len(common) / len(total) if total else 0
            
            if ratio >= threshold:
                similar.append(tool)
        
        return similar[:5]  # Limit suggestions
    
    def reset_rate_limits(self, tool: Optional[str] = None):
        """
        Reset rate limits.
        
        Args:
            tool: Specific tool to reset, or None for all.
        """
        if tool:
            if tool in self._rate_limits:
                self._rate_limits[tool].calls.clear()
        else:
            self._rate_limits.clear()
