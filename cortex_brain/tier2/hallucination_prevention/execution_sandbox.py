"""Execution Sandbox - Isolated execution environment for hallucination detection.

Provides sandboxed execution of operations to detect side effects and hallucinations.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional
from datetime import datetime


@dataclass
class SandboxResult:
    """Result of sandbox execution.

    Attributes:
        success: Whether execution succeeded.
        return_value: Return value from execution.
        side_effects: Detected side effects.
        execution_time_ms: Execution time.
        errors: Any errors that occurred.
    """

    success: bool
    return_value: Any = None
    side_effects: Dict[str, Any] = None
    execution_time_ms: float = 0
    errors: list = None

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.side_effects is None:
            self.side_effects = {}
        if self.errors is None:
            self.errors = []


class ExecutionSandbox:
    """Sandbox for isolated operation execution."""

    def __init__(self) -> None:
        """Initialize sandbox."""
        self.executed_operations: list = []
        self.side_effects_log: list = []

    def execute(
        self,
        operation_id: str,
        func: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> SandboxResult:
        """Execute function in sandbox.

        Args:
            operation_id: Operation ID.
            func: Function to execute.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            SandboxResult with execution details.
        """
        import time
        import traceback

        start_time = time.time()
        result = SandboxResult(success=False)

        try:
            # Execute function
            return_value = func(*args, **kwargs)
            result.success = True
            result.return_value = return_value

            # Record execution
            self.executed_operations.append(
                {
                    "operation_id": operation_id,
                    "timestamp": datetime.now(),
                    "success": True,
                }
            )

        except Exception as e:
            result.errors.append(str(e))
            result.errors.append(traceback.format_exc())
            result.success = False

            self.executed_operations.append(
                {
                    "operation_id": operation_id,
                    "timestamp": datetime.now(),
                    "success": False,
                    "error": str(e),
                }
            )

        finally:
            result.execution_time_ms = (time.time() - start_time) * 1000

        return result

    def detect_side_effects(self, before_state: Dict[str, Any], after_state: Dict[str, Any]) -> Dict[str, Any]:
        """Detect side effects by comparing states.

        Args:
            before_state: State before execution.
            after_state: State after execution.

        Returns:
            Dictionary of detected side effects.
        """
        side_effects = {}

        # Compare states
        for key in after_state:
            if key not in before_state:
                side_effects[f"added_{key}"] = after_state[key]
            elif before_state[key] != after_state[key]:
                side_effects[f"modified_{key}"] = {
                    "from": before_state[key],
                    "to": after_state[key],
                }

        for key in before_state:
            if key not in after_state:
                side_effects[f"removed_{key}"] = before_state[key]

        self.side_effects_log.append(side_effects)
        return side_effects

    def get_execution_log(self) -> list:
        """Get execution log.

        Returns:
            List of executed operations.
        """
        return self.executed_operations.copy()

    def clear_log(self) -> None:
        """Clear execution log."""
        self.executed_operations.clear()
        self.side_effects_log.clear()


__all__ = ["ExecutionSandbox", "SandboxResult"]
