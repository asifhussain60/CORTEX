"""
CORTEX Toolkit Manager Exceptions

Custom exceptions for the toolkit manager layer.
"""
from typing import List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class ValidationCheck:
    """Result of a single validation check."""
    name: str
    passed: bool
    message: str = ""
    severity: str = "error"  # error, warning, info
    details: Optional[Any] = None


@dataclass
class ValidationResult:
    """Result of all validation checks."""
    passed: bool
    checks: List[ValidationCheck] = field(default_factory=list)
    
    @property
    def errors(self) -> List[ValidationCheck]:
        """Get failed checks with error severity."""
        return [c for c in self.checks if not c.passed and c.severity == "error"]
    
    @property
    def warnings(self) -> List[ValidationCheck]:
        """Get failed checks with warning severity."""
        return [c for c in self.checks if not c.passed and c.severity == "warning"]
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "checks": [
                {
                    "name": c.name,
                    "passed": c.passed,
                    "message": c.message,
                    "severity": c.severity
                }
                for c in self.checks
            ]
        }


class ToolkitError(Exception):
    """Base exception for all toolkit errors."""
    pass


class ToolNotFoundError(ToolkitError):
    """Raised when a requested tool is not found in the registry."""
    
    def __init__(self, tool_name: str, similar_tools: Optional[List[str]] = None):
        self.tool_name = tool_name
        self.similar_tools = similar_tools or []
        message = f"Tool not found: '{tool_name}'"
        if self.similar_tools:
            message += f". Did you mean: {', '.join(self.similar_tools)}?"
        super().__init__(message)


class PlatformNotSupportedError(ToolkitError):
    """Raised when current platform is not supported by the tool."""
    
    def __init__(self, tool_name: str, current_platform: str, supported_platforms: List[str]):
        self.tool_name = tool_name
        self.current_platform = current_platform
        self.supported_platforms = supported_platforms
        message = (
            f"Tool '{tool_name}' not supported on '{current_platform}'. "
            f"Supported platforms: {', '.join(supported_platforms)}"
        )
        super().__init__(message)


class DependencyError(ToolkitError):
    """Raised when tool dependencies are not satisfied."""
    
    def __init__(self, tool_name: str, missing_dependencies: List[str]):
        self.tool_name = tool_name
        self.missing_dependencies = missing_dependencies
        message = (
            f"Tool '{tool_name}' has unmet dependencies: "
            f"{', '.join(missing_dependencies)}"
        )
        super().__init__(message)


class SecurityViolationError(ToolkitError):
    """Raised when a security check fails."""
    
    def __init__(self, tool_name: str, violation_type: str, details: str):
        self.tool_name = tool_name
        self.violation_type = violation_type
        self.details = details
        message = f"Security violation in '{tool_name}': {violation_type} - {details}"
        super().__init__(message)


class ValidationError(ToolkitError):
    """Raised when validation fails."""
    
    def __init__(self, tool_name: str, validation_result: ValidationResult):
        self.tool_name = tool_name
        self.validation_result = validation_result
        errors = validation_result.errors
        message = f"Validation failed for '{tool_name}': "
        if errors:
            message += "; ".join(e.message for e in errors)
        else:
            message += "Unknown validation error"
        super().__init__(message)


class ExecutionError(ToolkitError):
    """Raised when tool execution fails."""
    
    def __init__(
        self, 
        tool_name: str, 
        exit_code: int, 
        stderr: Optional[str] = None,
        checkpoint_id: Optional[str] = None
    ):
        self.tool_name = tool_name
        self.exit_code = exit_code
        self.stderr = stderr
        self.checkpoint_id = checkpoint_id
        message = f"Execution failed for '{tool_name}' (exit code: {exit_code})"
        if stderr:
            message += f": {stderr[:200]}"  # Truncate long stderr
        if checkpoint_id:
            message += f". Rollback available: checkpoint '{checkpoint_id}'"
        super().__init__(message)


class RateLimitError(ToolkitError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, tool_name: str, limit: int, reset_seconds: int):
        self.tool_name = tool_name
        self.limit = limit
        self.reset_seconds = reset_seconds
        message = (
            f"Rate limit exceeded for '{tool_name}' "
            f"(max {limit}/min). Reset in {reset_seconds}s"
        )
        super().__init__(message)


class DuplicationWarning(ToolkitError):
    """Raised when attempting to create a duplicate tool."""
    
    def __init__(self, requested_tool: str, existing_tools: List[str], similarity_scores: Optional[dict] = None):
        self.requested_tool = requested_tool
        self.existing_tools = existing_tools
        self.similarity_scores = similarity_scores or {}
        message = (
            f"Tool '{requested_tool}' overlaps with existing tools: "
            f"{', '.join(existing_tools)}. Consider using existing tools."
        )
        super().__init__(message)


class CheckpointError(ToolkitError):
    """Raised when checkpoint/recovery operations fail."""
    
    def __init__(self, operation: str, checkpoint_id: Optional[str] = None, reason: str = ""):
        self.operation = operation
        self.checkpoint_id = checkpoint_id
        self.reason = reason
        message = f"Checkpoint {operation} failed"
        if checkpoint_id:
            message += f" for '{checkpoint_id}'"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class CircularDependencyError(ToolkitError):
    """Raised when circular dependency is detected."""
    
    def __init__(self, cycle: List[str]):
        self.cycle = cycle
        message = f"Circular dependency detected: {' -> '.join(cycle)}"
        super().__init__(message)
