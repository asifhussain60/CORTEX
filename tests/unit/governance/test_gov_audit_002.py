"""Test suite for CORE-027c: Audit Immutability & Tamper Detection"""

import pytest
from cortex.core.governance.audit_immutability import (
    AuditImmutability,
    TamperStatus,
)


class TestAuditImmutability:
    """Tests for audit immutability."""
    
    def test_create_record(self):
        """Test creating immutable record."""
        manager = AuditImmutability()
        record = manager.create_record("rec1", "test content", "sig123")
        
        assert record.record_id == "rec1"
        assert record.tamper_status == TamperStatus.INTACT
    
    def test_verify_intact_record(self):
        """Test verifying intact record."""
        manager = AuditImmutability()
        manager.create_record("rec1", "content", "sig123")
        
        status = manager.verify_record("rec1")
        assert status == TamperStatus.INTACT
    
    def test_detect_tampered_record(self):
        """Test detecting tampered record."""
        manager = AuditImmutability()
        manager.create_record("rec1", "original content", "sig123")
        
        # Tamper with content
        manager.records["rec1"].content = "modified content"
        
        status = manager.verify_record("rec1")
        assert status == TamperStatus.TAMPERED
    
    def test_immutability_report(self):
        """Test immutability report."""
        manager = AuditImmutability()
        
        manager.create_record("rec1", "content1", "sig1")
        manager.create_record("rec2", "content2", "sig2")
        
        report = manager.get_immutability_report()
        
        assert report["total_records"] == 2
        assert report["intact"] == 2
        assert report["tampered"] == 0
    
    def test_empty_report(self):
        """Test report with no records."""
        manager = AuditImmutability()
        report = manager.get_immutability_report()
        
        assert report["total_records"] == 0
