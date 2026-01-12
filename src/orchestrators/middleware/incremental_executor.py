"""
IncrementalExecutor Middleware - Enforce CORE-001 Governance Rule

CORE-001: Small Incremental Autonomous Operations Required
  - ALL operations MUST work in <500 line increments
  - Prevents token limit errors (HTTP 502)
  - Enables autonomous execution without manual intervention
  - State persisted between increments for continuation

Author: CORTEX Governance System
Version: 1.0.0
Created: 2026-01-12
"""

import logging
from typing import Callable, Any, Dict, Optional, List
from functools import wraps
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ExecutionPhase(Enum):
    """Execution phase enumeration."""

    SETUP = "setup"
    EXECUTION = "execution"
    VALIDATION = "validation"
    TEARDOWN = "teardown"
    COMPLETE = "complete"


@dataclass
class IncrementState:
    """State for a single increment of execution."""

    increment_id: int
    phase: ExecutionPhase
    total_lines: int
    processed_lines: int
    status: str  # 'pending', 'in_progress', 'complete', 'failed'
    context: Dict[str, Any]  # Persisted context for continuation


class IncrementalExecutor:
    """Middleware to enforce CORE-001 incremental execution requirements."""

    # Line count limits (conservative to avoid token exhaustion)
    MAX_LINES_PER_INCREMENT = 500
    SAFETY_MARGIN = 0.8  # Use 80% of max to ensure safety

    # Token estimation (rough: 1 token ≈ 4 characters)
    CHARS_PER_TOKEN = 4.5
    MAX_TOKENS_PER_INCREMENT = 8000  # Conservative for safety

    def __init__(self):
        self.current_increment = 0
        self.execution_history: List[IncrementState] = []
        self.global_context: Dict[str, Any] = {}

    def split_operation(
        self, operation_data: str, max_lines: int = None
    ) -> List[str]:
        """
        Split an operation into increments of specified line count.

        Args:
            operation_data: Operation content (code, data, etc.)
            max_lines: Max lines per increment (default: MAX_LINES_PER_INCREMENT)

        Returns:
            List of increments
        """
        if max_lines is None:
            max_lines = self.MAX_LINES_PER_INCREMENT

        lines = operation_data.split('\n')
        increments = []

        for i in range(0, len(lines), max_lines):
            chunk = '\n'.join(lines[i : i + max_lines])
            increments.append(chunk)

        logger.info(
            f"✅ Split operation into {len(increments)} increments "
            f"(max {max_lines} lines each)"
        )
        return increments

    def check_token_budget(self, content: str) -> bool:
        """
        Check if content fits within token budget.

        Args:
            content: Content to check

        Returns:
            True if within budget, False otherwise
        """
        estimated_tokens = len(content) / self.CHARS_PER_TOKEN
        if estimated_tokens > self.MAX_TOKENS_PER_INCREMENT:
            logger.warning(
                f"⚠️  Content exceeds token budget: "
                f"{estimated_tokens:.0f} tokens (max {self.MAX_TOKENS_PER_INCREMENT})"
            )
            return False

        logger.info(
            f"✅ Token budget check passed: {estimated_tokens:.0f}/"
            f"{self.MAX_TOKENS_PER_INCREMENT} tokens"
        )
        return True

    def check_line_count(self, content: str) -> bool:
        """
        Check if content fits within line count limit.

        Args:
            content: Content to check

        Returns:
            True if within limit, False otherwise
        """
        line_count = len(content.split('\n'))
        max_allowed = int(self.MAX_LINES_PER_INCREMENT * self.SAFETY_MARGIN)

        if line_count > max_allowed:
            logger.warning(
                f"⚠️  Content exceeds line limit: "
                f"{line_count} lines (max {max_allowed})"
            )
            return False

        logger.info(
            f"✅ Line count check passed: {line_count}/{max_allowed} lines"
        )
        return True

    def validate_operation(self, operation_data: str) -> tuple[bool, Optional[str]]:
        """
        Validate an operation against CORE-001 requirements.

        Args:
            operation_data: Operation to validate

        Returns:
            Tuple of (is_valid: bool, reason: str or None)
        """
        # Check line count
        if not self.check_line_count(operation_data):
            return (
                False,
                f"CORE-001 VIOLATION: Operation exceeds {self.MAX_LINES_PER_INCREMENT} lines. "
                f"Split into smaller increments.",
            )

        # Check token budget
        if not self.check_token_budget(operation_data):
            return (
                False,
                f"CORE-001 VIOLATION: Operation exceeds token budget. "
                f"Reduce complexity or split operation.",
            )

        return True, None

    def create_checkpoint(self, state_key: str, state_value: Any) -> None:
        """
        Create a checkpoint for operation continuation.

        Args:
            state_key: Key for state persistence
            state_value: State to persist
        """
        self.global_context[state_key] = state_value
        logger.info(f"✅ Checkpoint created: {state_key}")

    def load_checkpoint(self, state_key: str) -> Optional[Any]:
        """
        Load a checkpoint for operation continuation.

        Args:
            state_key: Key for state to load

        Returns:
            State value or None if not found
        """
        value = self.global_context.get(state_key)
        if value:
            logger.info(f"✅ Checkpoint loaded: {state_key}")
        return value

    def can_continue(self) -> bool:
        """
        Check if operation can continue incrementally.

        Returns:
            True if continuation support is available
        """
        return bool(self.global_context)


def enforce_incremental_execution(max_lines: int = 500):
    """
    Decorator to enforce CORE-001 incremental execution on functions.

    Args:
        max_lines: Maximum lines allowed per invocation
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            executor = IncrementalExecutor()

            # Try to extract operation data
            operation_data = kwargs.get('operation') or (
                args[0] if len(args) > 0 else None
            )

            if operation_data and isinstance(operation_data, str):
                is_valid, reason = executor.validate_operation(operation_data)
                if not is_valid:
                    logger.error(f"🚫 Operation validation failed: {reason}")
                    raise OperationTooLargeError(reason)

                logger.info(
                    f"✅ CORE-001 validation passed for {len(operation_data.split(chr(10)))} line operation"
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


class OperationTooLargeError(Exception):
    """Exception raised when operation exceeds CORE-001 limits."""

    pass


# Public API
def validate_incremental_operation(content: str) -> bool:
    """Validate if operation meets CORE-001 requirements."""
    executor = IncrementalExecutor()
    is_valid, _ = executor.validate_operation(content)
    return is_valid


def split_large_operation(
    content: str, max_lines: int = 500
) -> List[str]:
    """Split large operation into increments."""
    executor = IncrementalExecutor()
    return executor.split_operation(content, max_lines)
