"""Tier2 Governance: Audit Performance SLA

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any


class SLAStatus(Enum):
    """SLA compliance status."""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATED = "violated"
    BREACH = "breach"


@dataclass
class SLAResult:
    """SLA evaluation result.
    
    Attributes:
        status: Compliance status
        duration_ms: Operation duration in milliseconds
        threshold_ms: SLA threshold in milliseconds
    """
    status: SLAStatus
    duration_ms: float
    threshold_ms: int


@dataclass
class OperationResult:
    """Result wrapper for operation recording.
    
    Attributes:
        success: Whether operation succeeded
        value: SLAResult if successful
    """
    success: bool
    value: SLAResult = None


class AuditPerformanceSLA:
    """Audit performance SLA tracker.
    
    Tracks audit operation performance against SLA targets.
    
    Attributes:
        operations: List of recorded operations
        sla_targets: SLA thresholds by operation type
    """
    
    def __init__(self):
        """Initialize SLA tracker."""
        self.operations: List[Dict[str, Any]] = []
        self.sla_targets: Dict[str, int] = {
            "read": 100,  # 100ms
            "write": 200,
            "query": 150,
            "update": 200,
        }
    
    def record_operation(
        self,
        operation_id: str,
        operation_type: str,
        start_time: datetime,
        end_time: datetime
    ) -> OperationResult:
        """Record an audit operation.
        
        Args:
            operation_id: Unique operation identifier
            operation_type: Type of operation (read, write, etc.)
            start_time: Operation start time
            end_time: Operation end time
            
        Returns:
            OperationResult with SLA status
        """
        duration_ms = (end_time - start_time).total_seconds() * 1000
        threshold_ms = self.sla_targets.get(operation_type, 100)
        
        # Determine status
        if duration_ms <= threshold_ms:
            status = SLAStatus.COMPLIANT
        elif duration_ms <= threshold_ms * 1.2:  # 20% over
            status = SLAStatus.WARNING
        else:
            status = SLAStatus.VIOLATED
        
        # Record operation
        self.operations.append({
            "operation_id": operation_id,
            "operation_type": operation_type,
            "duration_ms": duration_ms,
            "status": status,
            "start_time": start_time,
            "end_time": end_time,
        })
        
        result = SLAResult(
            status=status,
            duration_ms=duration_ms,
            threshold_ms=threshold_ms
        )
        
        return OperationResult(success=True, value=result)
    
    def get_sla_report(self) -> Dict[str, Any]:
        """Get SLA compliance report.
        
        Returns:
            Dictionary with compliance metrics
        """
        if not self.operations:
            return {
                "total_operations": 0,
                "compliant": 0,
                "warnings": 0,
                "violations": 0,
                "compliance_percentage": 0.0,
            }
        
        total = len(self.operations)
        compliant = sum(1 for op in self.operations if op["status"] == SLAStatus.COMPLIANT)
        warnings = sum(1 for op in self.operations if op["status"] == SLAStatus.WARNING)
        violations = sum(1 for op in self.operations if op["status"] == SLAStatus.VIOLATED)
        
        return {
            "total_operations": total,
            "compliant": compliant,
            "warnings": warnings,
            "violations": violations,
            "compliance_percentage": (compliant / total) * 100 if total > 0 else 0.0,
        }
    
    def check_sla(self, duration_ms: int) -> bool:
        """Check if duration meets SLA (backward compatibility).
        
        Args:
            duration_ms: Duration in milliseconds
            
        Returns:
            True if compliant
        """
        return duration_ms <= 1000


__all__ = ["SLAStatus", "SLAResult", "OperationResult", "AuditPerformanceSLA"]
