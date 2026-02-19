"""Tier2 Governance: Sla Tracking

Author: CORTEX Framework
"""

from dataclasses import dataclass
from enum import Enum


class SLAComplianceStatus(Enum):
    """SLA compliance status."""
    COMPLIANT = "compliant"
    AT_RISK = "at_risk"
    NON_COMPLIANT = "non_compliant"
    VIOLATED = "violated"


@dataclass
class SLATracker:
    """Track SLA compliance.
    
    Attributes:
        target_uptime: Target uptime percentage (e.g., 99.9)
        target_latency_ms: Target latency in milliseconds
        current_uptime: Current uptime percentage
        current_latency_ms: Current latency in milliseconds
    """
    target_uptime: float
    target_latency_ms: int
    current_uptime: float = 0.0
    current_latency_ms: int = 0
    sla_threshold_ms: int = 1000
    
    def track(self, duration_ms: int) -> bool:
        """Track duration against SLA threshold.
        
        Args:
            duration_ms: Duration in milliseconds
            
        Returns:
            True if within SLA threshold
        """
        return duration_ms <= self.sla_threshold_ms
    
    def get_compliance_status(self) -> SLAComplianceStatus:
        """Get current SLA compliance status.
        
        Returns:
            SLAComplianceStatus indicating compliance level
        """
        # Check uptime compliance
        uptime_margin = self.current_uptime - self.target_uptime
        
        # Violated: 5% or more below target
        if uptime_margin <= -5.0:
            return SLAComplianceStatus.VIOLATED
        
        # At risk: between 1-5% below target
        if uptime_margin < -1.0:
            return SLAComplianceStatus.AT_RISK
        
        # Compliant: within acceptable range
        return SLAComplianceStatus.COMPLIANT


__all__ = ["SLAComplianceStatus", "SLATracker"]
