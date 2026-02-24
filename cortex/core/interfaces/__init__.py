"""
Abstract Interfaces — Base Classes for CORTEX Components (Phase 60 merged)
Defines interfaces that all implementations must follow.
Ensures consistency and enables dependency injection.

Author: Asif Hussain
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from cortex.core.result import Result

if TYPE_CHECKING:
    from cortex.infrastructure.enhanced_audit_logger import AuditEntry


# ── IOrchestrator (inlined from i_orchestrator.py — Phase 60) ────────────────

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

    def health_check(self) -> Dict[str, Any]:
        """Return orchestrator health status."""
        return {
            "status": "healthy",
            "orchestrator": self.get_name(),
            "version": self.get_version(),
        }

    def get_recommended_template(self) -> Optional[str]:
        """Return the recommended workflow template ID for this orchestrator."""
        return None


# ── Additional Interfaces ────────────────────────────────────────────────────

class IAuditLogger(ABC):
    """Interface for audit logging."""

    @abstractmethod
    def log(
        self,
        operation: str,
        message: str,
        level: str = "INFO",
        ac_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Result[None]:
        """Log an audit entry."""
        pass

    @abstractmethod
    def query(
        self,
        ac_id: Optional[str] = None,
        component: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Result[List["AuditEntry"]]:
        """Query audit logs."""
        pass


@dataclass
class GovernanceRule:
    """Governance rule structure."""

    rule_id: str
    name: str
    severity: str  # blocked, warning, info
    tier: int  # 0, 1, 2, 3
    description: str
    enforcement: Optional[Dict[str, Any]] = None


class IGovernanceRegistry(ABC):
    """Interface for governance registry."""

    @abstractmethod
    def load_rules(self) -> Result[None]:
        """Load all governance rules."""
        pass

    @abstractmethod
    def get_rule(self, rule_id: str) -> Result[GovernanceRule]:
        """Get a specific rule by ID."""
        pass

    @abstractmethod
    def evaluate(self, context: Dict[str, Any]) -> Result[List[GovernanceRule]]:
        """Evaluate context against all rules."""
        pass


@dataclass
class ExecutionResult:
    """Result from orchestrator execution."""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None


class ITool(ABC):
    """Interface for CLI tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass

    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> Result[Dict[str, Any]]:
        """Execute the tool."""
        pass


# Legacy compatibility — OrchestratorBase re-export
try:
    from cortex.core.orchestrator_base import OrchestratorBase  # noqa: F401
except ImportError:
    OrchestratorBase = None  # type: ignore[assignment,misc]

__all__ = [
    "IOrchestrator",
    "OperationMode",
    "IAuditLogger",
    "IGovernanceRegistry",
    "GovernanceRule",
    "ExecutionResult",
    "ITool",
    "OrchestratorBase",
]
