"""BDOM-002: SLA Compliance Tracking"""
from dataclasses import dataclass, field
from typing import Dict, Optional
from enum import Enum
from datetime import datetime

class SLAComplianceStatus(Enum):
    COMPLIANT = "compliant"
    AT_RISK = "at_risk"
    VIOLATED = "violated"

@dataclass
class SLATracker:
    target_uptime: float
    target_latency_ms: float
    current_uptime: float = 100.0
    current_latency_ms: float = 0.0
    
    def get_compliance_status(self) -> SLAComplianceStatus:
        if self.current_uptime >= self.target_uptime and self.current_latency_ms <= self.target_latency_ms:
            return SLAComplianceStatus.COMPLIANT
        elif self.current_uptime >= (self.target_uptime * 0.95):
            return SLAComplianceStatus.AT_RISK
        return SLAComplianceStatus.VIOLATED
