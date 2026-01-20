"""Test for BDOM-002: SLA Compliance Tracking"""
import pytest
from cortex.core.governance.sla_tracking import SLATracker, SLAComplianceStatus

class TestSLATracking:
    def test_create_tracker(self):
        tracker = SLATracker(target_uptime=99.9, target_latency_ms=200)
        assert tracker.target_uptime == 99.9
    
    def test_compliant(self):
        tracker = SLATracker(target_uptime=99.0, target_latency_ms=200)
        tracker.current_uptime = 99.5
        tracker.current_latency_ms = 150
        assert tracker.get_compliance_status() == SLAComplianceStatus.COMPLIANT
    
    def test_at_risk(self):
        tracker = SLATracker(target_uptime=99.0, target_latency_ms=200)
        tracker.current_uptime = 95.0
        assert tracker.get_compliance_status() == SLAComplianceStatus.AT_RISK
    
    def test_violated(self):
        tracker = SLATracker(target_uptime=99.0, target_latency_ms=200)
        tracker.current_uptime = 94.0
        assert tracker.get_compliance_status() == SLAComplianceStatus.VIOLATED
