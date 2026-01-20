"""SLA tracking and compliance monitoring."""

from enum import Enum
from typing import Dict, List, Any
from datetime import datetime


class SLAComplianceStatus(Enum):
    """SLA compliance status."""
    COMPLIANT = "compliant"
    AT_RISK = "at_risk"
    VIOLATED = "violated"


class SLATracker:
    """Track and monitor SLA compliance."""
    
    def __init__(self, default_sla_ms: int = 1000):
        self.default_sla_ms = default_sla_ms
        self.slas: Dict[str, Dict[str, Any]] = {}
    
    def track_operation(self, operation_id: str, duration_ms: float) -> SLAComplianceStatus:
        """Track operation duration against SLA."""
        if duration_ms > self.default_sla_ms:
            status = SLAComplianceStatus.VIOLATED
        elif duration_ms > self.default_sla_ms * 0.8:
            status = SLAComplianceStatus.AT_RISK
        else:
            status = SLAComplianceStatus.COMPLIANT
        
        self.slas[operation_id] = {
            "duration_ms": duration_ms,
            "status": status,
            "timestamp": datetime.now()
        }
        return status
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """Get SLA compliance report."""
        if not self.slas:
            return {"total": 0, "compliant": 0, "at_risk": 0, "violated": 0}
        
        total = len(self.slas)
        compliant = sum(1 for s in self.slas.values() if s["status"] == SLAComplianceStatus.COMPLIANT)
        at_risk = sum(1 for s in self.slas.values() if s["status"] == SLAComplianceStatus.AT_RISK)
        violated = sum(1 for s in self.slas.values() if s["status"] == SLAComplianceStatus.VIOLATED)
        
        return {
            "total": total,
            "compliant": compliant,
            "at_risk": at_risk,
            "violated": violated,
            "compliance_rate": (compliant / total * 100) if total > 0 else 0
        }
