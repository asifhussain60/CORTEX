"""Core interfaces for CORTEX orchestration.

Defines protocols and abstract interfaces for orchestrators, executors,
and core framework components.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Any, Dict, Optional, Protocol, runtime_checkable
from enum import Enum
from abc import ABC, abstractmethod


class OperationMode(Enum):
    """Execution modes for orchestrators."""

    NORMAL = "normal"
    DEBUG = "debug"
    STRICT = "strict"
    ADAPTIVE = "adaptive"


class ExecutionContext:
    """Execution context for orchestrator operations.

    Attributes:
        mode: Current operation mode.
        timeout: Timeout in seconds.
        max_retries: Maximum retry attempts.
        metadata: Additional context metadata.
    """

    def __init__(
        self,
        mode: OperationMode = OperationMode.NORMAL,
        timeout: float = 300.0,
        max_retries: int = 3,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize execution context.

        Args:
            mode: Operation mode (default: NORMAL).
            timeout: Timeout in seconds (default: 300).
            max_retries: Maximum retries (default: 3).
            metadata: Optional metadata dictionary.
        """
        self.mode = mode
        self.timeout = timeout
        self.max_retries = max_retries
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary.

        Returns:
            Dictionary representation of context.
        """
        return {
            "mode": self.mode.value,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "metadata": self.metadata,
        }


@runtime_checkable
class IOrchestrator(Protocol):
    """Protocol for orchestrator implementations.

    Defines the interface all orchestrators must implement.
    """

    def execute(
        self, user_input: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute orchestrator operation.

        Args:
            user_input: User input string.
            context: Execution context dictionary.

        Returns:
            Dictionary with orchestrator results.

        Raises:
            ValueError: If input validation fails.
            RuntimeError: If execution fails.
        """
        ...

    def validate_input(self, user_input: str) -> bool:
        """Validate user input.

        Args:
            user_input: Input to validate.

        Returns:
            True if input is valid, False otherwise.
        """
        ...

    def get_capabilities(self) -> list[str]:
        """Get orchestrator capabilities.

        Returns:
            List of capability strings.
        """
        ...


class IExecutor(ABC):
    """Abstract executor interface."""

    @abstractmethod
    def execute(
        self, task: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute a task.

        Args:
            task: Task definition.
            context: Execution context.

        Returns:
            Task execution results.
        """
        pass

    @abstractmethod
    def can_execute(self, task: Dict[str, Any]) -> bool:
        """Check if executor can handle task.

        Args:
            task: Task definition.

        Returns:
            True if executor can handle the task.
        """
        pass


__all__ = ["IOrchestrator", "IExecutor", "OperationMode", "ExecutionContext"]
