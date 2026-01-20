"""Audit Performance SLA tracking and enforcement module."""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class SLAStatus(Enum):
    """SLA compliance status."""
    COMPLIANT = "compliant"
    AT_RISK = "at_risk"
    VIOLATED = "violated"


@dataclass
class AuditSLAMetrics:
    """Metrics for tracking audit SLA performance."""
    audit_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    sla_threshold_ms: int = 5000
    status: SLAStatus = SLAStatus.COMPLIANT
    elapsed_ms: float = 0.0
    violations: List[str] = field(default_factory=list)
    
    def check_compliance(self) -> bool:
        """Check if audit meets SLA threshold."""
        if self.end_time:
            self.elapsed_ms = (self.end_time - self.start_time).total_seconds() * 1000
            if self.elapsed_ms > self.sla_threshold_ms:
                self.status = SLAStatus.VIOLATED
                self.violations.append(f"SLA threshold exceeded: {self.elapsed_ms}ms > {self.sla_threshold_ms}ms")
                return False
        return True


class AuditPerformanceSLA:
    """Track and enforce audit performance SLAs."""
    
    def __init__(self, default_threshold_ms: int = 5000):
        self.default_threshold_ms = default_threshold_ms
        self.audit_metrics: Dict[str, AuditSLAMetrics] = {}
        self.sla_breaches: List[Dict[str, Any]] = []
    
    def start_audit(self, audit_id: str, threshold_ms: Optional[int] = None) -> AuditSLAMetrics:
        """Start tracking an audit."""
        threshold = threshold_ms or self.default_threshold_ms
        metrics = AuditSLAMetrics(
            audit_id=audit_id,
            start_time=datetime.now(),
            sla_threshold_ms=threshold
        )
        self.audit_metrics[audit_id] = metrics
        return metrics
    
    def end_audit(self, audit_id: str) -> bool:
        """End audit tracking and check compliance."""
        if audit_id not in self.audit_metrics:
            return False
        
        metrics = self.audit_metrics[audit_id]
        metrics.end_time = datetime.now()
        
        is_compliant = metrics.check_compliance()
        
        if not is_compliant:
            self.sla_breaches.append({
                "audit_id": audit_id,
                "timestamp": datetime.now(),
                "elapsed_ms": metrics.elapsed_ms,
                "threshold_ms": metrics.sla_threshold_ms
            })
        
        return is_compliant
    
    def get_metrics(self, audit_id: str) -> Optional[AuditSLAMetrics]:
        """Get metrics for a specific audit."""
        return self.audit_metrics.get(audit_id)
    
    def get_sla_report(self) -> Dict[str, Any]:
        """Get overall SLA report."""
        if not self.audit_metrics:
            return {"total_audits": 0, "compliant": 0, "violations": 0}
        
        total = len(self.audit_metrics)
        violations = len(self.sla_breaches)
        
        return {
            "total_audits": total,
            "compliant": total - violations,
            "violations": violations,
            "compliance_rate": ((total - violations) / total * 100) if total > 0 else 0,
            "recent_breaches": self.sla_breaches[-10:]
        }
