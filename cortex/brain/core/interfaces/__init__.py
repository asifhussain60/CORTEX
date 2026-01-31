"""
Core Interfaces - Subdirectory

This directory provides i_orchestrator.py.
Other interfaces (IAuditLogger, GovernanceRule) are in parent cortex.brain.core.interfaces module.
"""

from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator, OperationMode

# Import from parent module (consolidation - i_audit_logger.py deleted)
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from cortex.brain.core.result import Result

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
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Result[List]:
        """Query audit logs."""
        pass


@dataclass
class GovernanceRule:
    """Governance rule structure."""
    rule_id: str
    name: str
    severity: str
    tier: int
    description: str
    enforcement: Optional[Dict[str, Any]] = None


__all__ = [
    "IOrchestrator",
    "OperationMode",
    "IAuditLogger",
    "GovernanceRule",
]
