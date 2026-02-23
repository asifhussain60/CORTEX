"""Core interfaces for CORTEX orchestration.

Defines protocols and abstract interfaces for orchestrators, executors,
and core framework components.

CORE-035: Re-exports canonical IOrchestrator from cortex.core.interfaces.i_orchestrator

Author: CORTEX Framework
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Protocol, runtime_checkable

# Phase 59-b: Single canonical OperationMode — imported from cortex.core.core.interfaces.i_orchestrator
from cortex.core.core.interfaces.i_orchestrator import (  # noqa: F401
    IOrchestrator,
    OperationMode,
)

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
        mode: OperationMode = OperationMode.PLANNING,
        timeout: float = 300.0,
        max_retries: int = 3,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize execution context.

        Args:
            mode: Operation mode (default: PLANNING).
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



# ============================================================================
# CORE-035: Single Canonical Implementation — IOrchestrator and OperationMode
# already imported at top of file from cortex.core.core.interfaces.i_orchestrator
# ============================================================================

# Backward-compat alias (retained for any caller using OrchestratorOperationMode)
OrchestratorOperationMode = OperationMode


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
