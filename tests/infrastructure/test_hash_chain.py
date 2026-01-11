"""
Test suite for AC-AUDIT-007: Hash Chain Integrity

Tests tamper detection via event_hash + prev_event_hash chain.

Author: Asif Hussain
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import pytest
import hashlib
import json
from pathlib import Path
from src.infrastructure.enhanced_audit_logger import (
    AuditStorage, AuditEntry, AuditLevel, AuditCategory
)


class TestHashChainIntegrity:
    """Test hash chain for tamper detection."""
    
    @pytest.fixture
    def temp_audit_db(self, tmp_path):
        """Create temporary audit database."""
        db_path = tmp_path / "test_audit.db"
        return db_path
    
    @pytest.fixture
    def logger(self, temp_audit_db):
        """Create audit logger instance."""
        return AuditStorage(db_path=temp_audit_db)
    
    def test_hash_chain_creation(self, logger):
        """
        AC-AUDIT-007: Test that each audit entry has event_hash.
        
        GIVEN: A fresh audit logger
        WHEN: Multiple events are logged
        THEN: Each event should have a unique event_hash computed from its fields
        """
        # Log 3 events
        logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.GOVERNANCE,
            component="test",
            operation="test_op_1",
            message="First event",
            ac_id="AC-TEST-001"
        )
        
        logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.GOVERNANCE,
            component="test",
            operation="test_op_2",
            message="Second event",
            ac_id="AC-TEST-002"
        )
        
        logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.GOVERNANCE,
            component="test",
            operation="test_op_3",
            message="Third event",
            ac_id="AC-TEST-003"
        )
        
        # Query all events
        events = logger.query_audit_trail(limit=3)
        
        # Verify each has event_hash
        assert len(events) == 3
        for event in events:
            assert 'event_hash' in event, "Each event must have event_hash"
            assert len(event['event_hash']) == 64, "SHA-256 hash must be 64 chars"
    
    def test_prev_event_hash_chain(self, logger):
        """
        AC-AUDIT-007: Test prev_event_hash links to previous event.
        
        GIVEN: Multiple audit events logged sequentially
        WHEN: Events are retrieved in order
        THEN: Each event's prev_event_hash must match the previous event's event_hash
        """
        # Log 5 events
        for i in range(5):
            logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.ORCHESTRATOR,
                component="test",
                operation=f"op_{i}",
                message=f"Event {i}",
                ac_id=f"AC-TEST-{i:03d}"
            )
        
        # Query events in order
        events = logger.query_audit_trail(limit=5, order="ASC")
        
        # First event should have NULL prev_event_hash (chain start)
        assert events[0].get('prev_event_hash') is None, "First event has no predecessor"
        
        # Subsequent events should link
        for i in range(1, len(events)):
            prev_hash = events[i-1]['event_hash']
            curr_prev_hash = events[i]['prev_event_hash']
            assert curr_prev_hash == prev_hash, \
                f"Event {i} prev_event_hash must match event {i-1} event_hash"
    
    def test_hash_verification_success(self, logger):
        """
        AC-AUDIT-007: Test verification passes for untampered chain.
        
        GIVEN: An audit chain with multiple events
        WHEN: verify_chain() is called
        THEN: Verification should pass with no tampering detected
        """
        # Log events
        for i in range(10):
            logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.VALIDATION,
                component="test",
                operation=f"op_{i}",
                message=f"Event {i}"
            )
        
        # Verify chain
        is_valid, error = logger.verify_chain()
        
        assert is_valid is True, "Untampered chain should verify successfully"
        assert error is None, "No error should be returned for valid chain"
    
    def test_hash_verification_detects_tampering(self, logger, temp_audit_db):
        """
        AC-AUDIT-007: Test tampering detection.
        
        GIVEN: An audit chain
        WHEN: A message is tampered with directly in the database
        THEN: verify_chain() should detect the tampering and raise AuditIntegrityError
        """
        # Log events
        for i in range(5):
            logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.INFRASTRUCTURE,
                component="test",
                operation=f"op_{i}",
                message=f"Original message {i}"
            )
        
        # Tamper with event #3 directly in database
        import sqlite3
        conn = sqlite3.connect(temp_audit_db)
        conn.execute(
            "UPDATE audit_logs SET message = ? WHERE operation = ?",
            ("TAMPERED MESSAGE", "op_2")
        )
        conn.commit()
        conn.close()
        
        # Verify should detect tampering
        is_valid, error = logger.verify_chain()
        
        assert is_valid is False, "Tampering should be detected"
        assert error is not None, "Error message should describe tampering"
        assert "tamper" in error.lower() or "integrity" in error.lower()
    
    def test_hash_computation_performance(self, logger):
        """
        AC-AUDIT-007: Hash computation must be <1ms.
        
        GIVEN: An audit logger
        WHEN: An event is logged
        THEN: Hash computation overhead must be <1ms
        """
        import time
        
        start = time.perf_counter()
        logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.MCP,
            component="test",
            operation="perf_test",
            message="Performance test event"
        )
        end = time.perf_counter()
        
        duration_ms = (end - start) * 1000
        assert duration_ms < 1.0, f"Hash computation took {duration_ms:.2f}ms (must be <1ms)"
    
    def test_chain_verification_performance(self, logger):
        """
        AC-AUDIT-007: Chain verification must be <10ms per 100 events.
        
        GIVEN: A chain of 100 events
        WHEN: verify_chain() is called
        THEN: Verification must complete in <10ms
        """
        import time
        
        # Log 100 events
        for i in range(100):
            logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.BRAIN,
                component="test",
                operation=f"op_{i}",
                message=f"Event {i}"
            )
        
        # Verify performance
        start = time.perf_counter()
        is_valid, error = logger.verify_chain()
        end = time.perf_counter()
        
        duration_ms = (end - start) * 1000
        assert is_valid is True, "Chain should be valid"
        assert duration_ms < 10.0, f"Verification took {duration_ms:.2f}ms (must be <10ms for 100 events)"
    
    def test_hash_includes_all_critical_fields(self, logger):
        """
        AC-AUDIT-007: event_hash must include all critical fields.
        
        GIVEN: Two events with different fields
        WHEN: Hashes are computed
        THEN: Any change in timestamp, component, operation, message, ac_id should change hash
        """
        # Log base event
        logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.GOVERNANCE,
            component="component_a",
            operation="operation_x",
            message="message_1",
            ac_id="AC-TEST-001"
        )
        
        # Log event with different message
        logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.GOVERNANCE,
            component="component_a",
            operation="operation_x",
            message="message_2",  # Different
            ac_id="AC-TEST-001"
        )
        
        events = logger.query_audit_trail(limit=2)
        
        # Hashes must be different
        assert events[0]['event_hash'] != events[1]['event_hash'], \
            "Different messages must produce different hashes"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
