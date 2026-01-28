"""
Abstract Interfaces - Base Classes for CORTEX Components

Defines interfaces that all implementations must follow.
Ensures consistency and enables dependency injection.

Author: Asif Hussain
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from cortex.brain.core.result import Result

if TYPE_CHECKING:
    from cortex.infrastructure.enhanced_audit_logger import AuditEntry


class IAuditLogger(ABC):
    """Interface for audit logging."""
    
    @abstractmethod
    def log(
        self,
        operation: str,
        message: str,
        level: str = "INFO",
        ac_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Result[None]:
        """Log an audit entry."""
        pass
    
    @abstractmethod
    def query(
        self,
        ac_id: Optional[str] = None,
        component: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
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


# Re-export canonical IOrchestrator from interfaces/i_orchestrator.py (CORE-035)
from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator, OperationMode  # noqa: F401


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
