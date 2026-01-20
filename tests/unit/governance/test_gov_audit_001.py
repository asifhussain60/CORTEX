"""Test suite for CORE-027b: Audit Performance SLA"""

import pytest
from datetime import datetime, timedelta
from cortex.core.governance.audit_performance_sla import (
    AuditPerformanceSLA,
    SLAStatus,
)


class TestAuditPerformanceSLA:
    """Tests for audit performance SLA."""
    
    def test_sla_initialization(self):
        """Test SLA manager initialization."""
        sla = AuditPerformanceSLA()
        assert len(sla.operations) == 0
        assert len(sla.sla_targets) > 0
    
    def test_record_compliant_operation(self):
        """Test recording compliant operation."""
        sla = AuditPerformanceSLA()
        start = datetime.utcnow()
        end = start + timedelta(milliseconds=50)
        
        result = sla.record_operation("op1", "read", start, end)
        
        assert result.success
        assert result.value.status == SLAStatus.COMPLIANT
    
    def test_record_warning_operation(self):
        """Test recording warning operation."""
        sla = AuditPerformanceSLA()
        start = datetime.utcnow()
        end = start + timedelta(milliseconds=110)  # 10% over 100ms target
        
        result = sla.record_operation("op1", "read", start, end)
        
        assert result.success
        assert result.value.status == SLAStatus.WARNING
    
    def test_record_violated_operation(self):
        """Test recording violated operation."""
        sla = AuditPerformanceSLA()
        start = datetime.utcnow()
        end = start + timedelta(milliseconds=150)  # 50% over 100ms target
        
        result = sla.record_operation("op1", "read", start, end)
        
        assert result.success
        assert result.value.status == SLAStatus.VIOLATED
    
    def test_sla_report(self):
        """Test SLA compliance report."""
        sla = AuditPerformanceSLA()
        start = datetime.utcnow()
        
        # Add compliant operations
        for i in range(3):
            sla.record_operation(f"op{i}", "read", start, start + timedelta(milliseconds=50))
        
        # Add violated operation
        sla.record_operation("op_bad", "read", start, start + timedelta(milliseconds=200))
        
        report = sla.get_sla_report()
        
        assert report["total_operations"] == 4
        assert report["compliant"] == 3
        assert report["violations"] == 1
    
    def test_sla_empty_report(self):
        """Test report with no operations."""
        sla = AuditPerformanceSLA()
        report = sla.get_sla_report()
        
        assert report["total_operations"] == 0
        assert report["compliance_percentage"] == 0.0
