"""
Orchestrator Interface - Reference Architecture (AC-AR-011)

Defines contract for orchestrators:
- PlanningOrchestrator registered in OrchestratorRegistry (AC-AR-011-01)
- PlanningOrchestrator exposed as MCP tools (AC-AR-011-02)
- All operations audit-logged with hash chain (AC-AR-011-03)

Author: Asif Hussain
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, Optional

from cortex.brain.core.result import Result


class OperationMode(Enum):
    """Orchestration modes."""
    PLANNING = auto()
    EXECUTION = auto()
    VALIDATION = auto()
    RECOVERY = auto()
    EDUCATIONAL = auto()  # Phase 22: ASK Mode


class IOrchestrator(ABC):
    """
    Interface contract for all orchestrators.

    Guarantees:
    - Registry integration
    - MCP tool exposure
    - Audit logging
    - Result pattern compliance
    """

    @abstractmethod
    def get_name(self) -> str:
        """Get orchestrator name."""
        pass

    @abstractmethod
    def get_version(self) -> str:
        """Get orchestrator version."""
        pass

    @abstractmethod
    def initialize(self) -> Result[str]:
        """Initialize orchestrator."""
        pass

    @abstractmethod
    def get_mode(self) -> OperationMode:
        """Get current operation mode."""
        pass

    @abstractmethod
    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """AC-AR-011-02: Get exposed MCP tools."""
        pass

    @abstractmethod
    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """Execute operation with audit logging."""
        pass

    @abstractmethod
    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """AC-AR-011-03: Get audit trail with hash chain."""
        pass
