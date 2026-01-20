"""
CORE-027b: Audit Performance SLA - Audit operation timing and compliance
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any


class SLAStatus(Enum):
    """Status of SLA compliance."""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATED = "violated"


@dataclass
class AuditOperation:
    """Single audit operation record."""
    operation_id: str
    operation_type: str
    start_time: datetime
    end_time: datetime
    duration_ms: float
    sla_target_ms: float
    status: SLAStatus = SLAStatus.COMPLIANT


@dataclass
class Result:
    """Generic result type."""
    success: bool
    value: Optional[Any] = None
    error: Optional[str] = None
    
    @classmethod
    def ok(cls, value: Any) -> Result:
        return cls(success=True, value=value)
    
    @classmethod
    def error(cls, error: str) -> Result:
        return cls(success=False, error=error)


class AuditPerformanceSLA:
    """Manages audit operation SLA compliance."""
    
    # Default SLA targets (milliseconds)
    DEFAULT_SLA_TARGETS = {
        "read": 100.0,
        "write": 500.0,
        "delete": 300.0,
        "search": 200.0,
        "export": 2000.0,
    }
    
    def __init__(self):
        """Initialize SLA manager."""
        self.operations: List[AuditOperation] = []
        self.sla_targets = self.DEFAULT_SLA_TARGETS.copy()
    
    def record_operation(
        self,
        operation_id: str,
        operation_type: str,
        start_time: datetime,
        end_time: datetime
    ) -> Result:
        """Record an audit operation."""
        try:
            duration_ms = (end_time - start_time).total_seconds() * 1000
            target = self.sla_targets.get(operation_type, 1000.0)
            
            status = self._determine_sla_status(duration_ms, target)
            
            operation = AuditOperation(
                operation_id=operation_id,
                operation_type=operation_type,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                sla_target_ms=target,
                status=status
            )
            
            self.operations.append(operation)
            return Result.ok(operation)
        except Exception as e:
            return Result.error(f"Failed to record operation: {str(e)}")
    
    def _determine_sla_status(self, duration: float, target: float) -> SLAStatus:
        """Determine SLA status based on duration vs target."""
        if duration <= target:
            return SLAStatus.COMPLIANT
        elif duration <= target * 1.2:  # 20% over is warning
            return SLAStatus.WARNING
        else:
            return SLAStatus.VIOLATED
    
    def get_sla_report(self) -> Dict[str, Any]:
        """Get SLA compliance report."""
        if not self.operations:
            return {
                "total_operations": 0,
                "compliant": 0,
                "warnings": 0,
                "violations": 0,
                "compliance_percentage": 0.0,
            }
        
        compliant = sum(1 for o in self.operations if o.status == SLAStatus.COMPLIANT)
        warnings = sum(1 for o in self.operations if o.status == SLAStatus.WARNING)
        violations = sum(1 for o in self.operations if o.status == SLAStatus.VIOLATED)
        
        return {
            "total_operations": len(self.operations),
            "compliant": compliant,
            "warnings": warnings,
            "violations": violations,
            "compliance_percentage": (compliant / len(self.operations)) * 100,
        }
