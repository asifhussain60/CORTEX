"""DevX Debugger for debugging and introspection."""

import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class DebugContext:
    """Debug context for an operation."""

    operation: str
    breakpoints: List[str] = field(default_factory=lambda: [])
    variables: Dict[str, Any] = field(default_factory=lambda: {})
    timestamp: str = ""

    def __post_init__(self) -> None:
        """Initialize timestamp."""
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "operation": self.operation,
            "breakpoints": self.breakpoints,
            "variables": {k: str(v) for k, v in self.variables.items()},
            "timestamp": self.timestamp
        }


class DevxDebugger:
    """Debugging and introspection tools."""

    def __init__(self) -> None:
        """Initialize debugger."""
        self.contexts: Dict[str, DebugContext] = {}
        self.last_exception: str = ""

    def create_context(self, operation: str) -> DebugContext:
        """Create debug context.

        Args:
            operation: Operation name

        Returns:
            DebugContext
        """
        context = DebugContext(operation=operation)
        self.contexts[operation] = context
        return context

    def inspect_variable(
        self,
        context: DebugContext,
        var_name: str,
        var_value: Any
    ) -> Dict[str, Any]:
        """Inspect a variable.

        Args:
            context: Debug context
            var_name: Variable name
            var_value: Variable value

        Returns:
            Inspection results
        """
        context.variables[var_name] = var_value
        return {
            "name": var_name,
            "type": type(var_value).__name__,
            "value": str(var_value),
            "length": len(str(var_value))
        }

    def get_stack_trace(self, context: DebugContext) -> str:
        """Get current stack trace.

        Args:
            context: Debug context

        Returns:
            Stack trace string
        """
        # Get exception info if available
        exc_info = sys.exc_info()
        if exc_info[0] is not None:
            # Format just the exception type and message
            return f"{exc_info[0].__name__}: {exc_info[1]}"

        return "".join(traceback.format_stack())

    def set_breakpoint(self, context: DebugContext, location: str) -> None:
        """Set a breakpoint.

        Args:
            context: Debug context
            location: Breakpoint location
        """
        context.breakpoints.append(location)

    def remove_breakpoint(self, context: DebugContext, location: str) -> None:
        """Remove a breakpoint.

        Args:
            context: Debug context
            location: Breakpoint location
        """
        if location in context.breakpoints:
            context.breakpoints.remove(location)
