"""Core interfaces for CORTEX orchestration.

Defines protocols and abstract interfaces for orchestrators, executors,
and core framework components.

Author: CORTEX Framework
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
    PLANNING = "planning"


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


class IOrchestrator(ABC):
    """Abstract base class for orchestrator implementations.

    All orchestrators must implement these methods.
    """

    @abstractmethod
    def get_name(self) -> str:
        """Get orchestrator name.

        Returns:
            String name of the orchestrator.
        """
        pass

    @abstractmethod
    def get_version(self) -> str:
        """Get orchestrator version.

        Returns:
            Version string (e.g., "1.0").
        """
        pass

    @abstractmethod
    def initialize(self) -> Any:
        """Initialize orchestrator.

        Returns:
            Result[str] with initialization status.
        """
        pass

    @abstractmethod
    def get_mode(self) -> OperationMode:
        """Get current operation mode.

        Returns:
            Current OperationMode.
        """
        pass

    @abstractmethod
    def get_mcp_tools(self) -> Any:
        """Get available MCP tools.

        Returns:
            Result[Dict[str, Any]] with tool definitions.
        """
        pass

    @abstractmethod
    def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute an operation.

        Args:
            operation_name: Name of operation to execute.
            parameters: Operation parameters.

        Returns:
            Result[Any] with operation results.
        """
        pass

    @abstractmethod
    def get_audit_trail(self, limit: int = 100) -> Any:
        """Get audit trail for orchestrator.

        Args:
            limit: Maximum number of entries (default: 100).

        Returns:
            Result[list] with audit entries.
        """
        pass

    def execute(
        self, user_input: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute orchestrator operation (optional override).

        Args:
            user_input: User input string.
            context: Execution context dictionary.

        Returns:
            Dictionary with orchestrator results.
        """
        return {}

    def validate_input(self, user_input: str) -> bool:
        """Validate user input (optional override).

        Args:
            user_input: Input to validate.

        Returns:
            True if input is valid, False otherwise.
        """
        return bool(user_input)

    def get_capabilities(self) -> list[str]:
        """Get orchestrator capabilities (optional override).

        Returns:
            List of capability strings.
        """
        return []


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


# Import OrchestratorBase for export
try:
    from cortex.core.orchestrator.orchestrator_base import OrchestratorBase
except ImportError:
    OrchestratorBase = None

__all__ = ["IOrchestrator", "IExecutor", "OperationMode", "ExecutionContext", "OrchestratorBase"]
