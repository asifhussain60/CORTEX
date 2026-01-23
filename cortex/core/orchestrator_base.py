"""Orchestrator Base - Base class for orchestrators.

Abstract base class for orchestrator implementations.

Author: CORTEX Framework
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from enum import Enum
import threading


class OrchestrationState(Enum):
    """Orchestration state."""

    IDLE = "idle"
    INITIALIZING = "initializing"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


class OrchestratorBase(ABC):
    """Base class for orchestrators."""

    def __init__(self, name: str = "OrchestratorBase") -> None:
        """Initialize orchestrator.

        Args:
            name: Orchestrator name.
        """
        self.name = name
        self.version = "1.0"
        self.state = OrchestrationState.IDLE
        self.internal_state: Dict[str, Any] = {}
        # REM-CRIT-001: Thread-safe state management with lock
        self._state_lock = threading.Lock()

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the orchestrator."""
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Any:
        """Execute orchestration.

        Args:
            context: Execution context.

        Returns:
            Execution result.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the orchestrator."""
        pass

    def get_name(self) -> str:
        """Get orchestrator name.

        Returns:
            Orchestrator name.
        """
        return self.name

    def get_version(self) -> str:
        """Get orchestrator version.

        Returns:
            Version string.
        """
        return self.version

    def get_state(self) -> OrchestrationState:
        """Get current state (thread-safe).

        Returns:
            OrchestrationState.
        """
        with self._state_lock:
            return self.state

    def set_state(self, state: OrchestrationState) -> None:
        """Set orchestration state (thread-safe, atomic transition).

        Args:
            state: New state.
        """
        with self._state_lock:
            self.state = state

    def clear_state(self) -> None:
        """Clear internal state (thread-safe)."""
        with self._state_lock:
            self.internal_state = {}


class OrchestrationContext:
    """Context for orchestration.

    Attributes:
        execution_id: Unique execution identifier.
        orchestrator_id: Orchestrator identifier.
        orchestrator_name: Orchestrator name.
        parameters: Execution parameters.
        metadata: Additional metadata.
        tier_access: Set of tiers this context has access to.
    """

    def __init__(
        self,
        execution_id: Optional[str] = None,
        orchestrator_id: Optional[str] = None,
        orchestrator_name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tier_access: Optional[set] = None,
    ) -> None:
        """Initialize orchestration context.

        Args:
            execution_id: Execution ID (optional).
            orchestrator_id: Orchestrator ID (optional).
            orchestrator_name: Orchestrator name (optional).
            parameters: Optional parameters.
            metadata: Optional metadata.
            tier_access: Optional tier access set.
        """
        self.execution_id = execution_id or ""
        self.orchestrator_id = orchestrator_id or ""
        self.orchestrator_name = orchestrator_name or ""
        self.parameters = parameters or {}
        self.metadata = metadata or {}
        self.progress_percent = 0.0
        self.domain_name = ""
        self.tier_access = tier_access or set()


__all__ = ["OrchestratorBase", "OrchestrationContext", "OrchestrationState"]
