"""
Test suite for AC Completion Audit Requirements (AC-AR-014-02)

Tests for AuditRequiredValidator and ACCompletionAuditValidator.
Enforces minimum audit entry requirements before AC-ID completion.
"""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import json

from cortex.core.audit_required_validator import (
    AuditOperationType,
    AuditValidationResult,
    AuditEntry,
    ACCompletionStatus,
    AuditOperationsTracker,
    ACCompletionAuditValidator,
    AuditRequiredValidator,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def governance_db():
    """Create temporary governance database with audit_log table."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            ac_id TEXT,
            operation TEXT,
            actor TEXT,
            details TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    Path(db_path).unlink()


@pytest.fixture
def db_with_complete_audit(governance_db):
    """Create database with complete audit trail for an AC-ID."""
    conn = sqlite3.connect(governance_db)
    cursor = conn.cursor()
    
    # Add complete audit sequence
    cursor.execute(
        """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
           VALUES (?, ?, ?, ?, ?)""",
        ("2026-01-15T10:00:00Z", "AC-TEST-001", "AC_START", "system", 
         json.dumps({"initiator": "test"}))
    )
    cursor.execute(
        """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
           VALUES (?, ?, ?, ?, ?)""",
        ("2026-01-15T10:15:00Z", "AC-TEST-001", "AC_EXECUTE", "system",
         json.dumps({"tests_run": 10}))
    )
    cursor.execute(
        """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
           VALUES (?, ?, ?, ?, ?)""",
        ("2026-01-15T10:30:00Z", "AC-TEST-001", "AC_COMPLETE", "system",
         json.dumps({"status": "success"}))
    )
    
    conn.commit()
    conn.close()
    
    return governance_db


@pytest.fixture
def db_with_incomplete_audit(governance_db):
    """Create database with incomplete audit trail."""
    conn = sqlite3.connect(governance_db)
    cursor = conn.cursor()
    
    # Only START and EXECUTE, no COMPLETE
    cursor.execute(
        """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
           VALUES (?, ?, ?, ?, ?)""",
        ("2026-01-15T10:00:00Z", "AC-INCOMPLETE", "AC_START", "system", "{}")
    )
    cursor.execute(
        """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
           VALUES (?, ?, ?, ?, ?)""",
        ("2026-01-15T10:15:00Z", "AC-INCOMPLETE", "AC_EXECUTE", "system", "{}")
    )
    
    conn.commit()
    conn.close()
    
    return governance_db


# =============================================================================
# TEST: AuditEntry
# =============================================================================

class TestAuditEntry:
    """Test AuditEntry dataclass."""
    
    def test_create_audit_entry(self):
        """Test creating an audit entry."""
        entry = AuditEntry(
            id=1,
            timestamp="2026-01-15T10:00:00Z",
            ac_id="AC-TEST",
            operation="AC_START",
            actor="system",
            details={"key": "value"}
        )
        
        assert entry.ac_id == "AC-TEST"
        assert entry.operation == "AC_START"
    
    def test_audit_entry_to_dict(self):
        """Test converting audit entry to dictionary."""
        entry = AuditEntry(
            id=1,
            timestamp="2026-01-15T10:00:00Z",
            ac_id="AC-TEST",
            operation="AC_START",
            actor="system",
            details={}
        )
        
        d = entry.to_dict()
        assert d["ac_id"] == "AC-TEST"
        assert d["operation"] == "AC_START"


# =============================================================================
# TEST: ACCompletionStatus
# =============================================================================

class TestACCompletionStatus:
    """Test ACCompletionStatus dataclass."""
    
    def test_status_creation(self):
        """Test creating completion status."""
        status = ACCompletionStatus(
            ac_id="AC-TEST",
            total_entries=3,
            required_entries=3,
            is_valid=True,
            result_code=AuditValidationResult.SUFFICIENT.value,
            reason="Ready for completion"
        )
        
        assert status.is_valid is True
        assert status.total_entries == 3
    
    def test_status_to_dict(self):
        """Test converting status to dictionary."""
        status = ACCompletionStatus(
            ac_id="AC-TEST",
            total_entries=3,
            required_entries=3,
            is_valid=True,
            result_code=AuditValidationResult.SUFFICIENT.value,
            reason="Ready for completion",
            has_start=True,
            has_execute=True,
            has_complete=True
        )
        
        d = status.to_dict()
        assert d["is_valid"] is True
        assert d["has_start"] is True


# =============================================================================
# TEST: AuditOperationsTracker
# =============================================================================

class TestAuditOperationsTracker:
    """Test audit operations tracking."""
    
    def test_get_ac_entries_empty(self, governance_db):
        """Test getting entries for non-existent AC."""
        tracker = AuditOperationsTracker(governance_db)
        entries, error = tracker.get_ac_entries("AC-NONEXISTENT")
        
        assert entries == []
        assert error is None
    
    def test_get_ac_entries_with_data(self, db_with_complete_audit):
        """Test retrieving audit entries."""
        tracker = AuditOperationsTracker(db_with_complete_audit)
        entries, error = tracker.get_ac_entries("AC-TEST-001")
        
        assert error is None
        assert len(entries) == 3
        assert entries[0].operation == "AC_START"
        assert entries[1].operation == "AC_EXECUTE"
        assert entries[2].operation == "AC_COMPLETE"
    
    def test_get_operation_counts(self, db_with_complete_audit):
        """Test counting operations."""
        tracker = AuditOperationsTracker(db_with_complete_audit)
        counts = tracker.get_operation_counts("AC-TEST-001")
        
        assert counts["AC_START"] == 1
        assert counts["AC_EXECUTE"] == 1
        assert counts["AC_COMPLETE"] == 1


# =============================================================================
# TEST: ACCompletionAuditValidator - Complete Audits
# =============================================================================

class TestACCompletionValidatorComplete:
    """Test validation of complete audit trails."""
    
    def test_validate_complete_ac(self, db_with_complete_audit):
        """Test validation of AC with complete audit trail."""
        validator = ACCompletionAuditValidator(db_with_complete_audit)
        status = validator.validate_ac_completion("AC-TEST-001")
        
        assert status.is_valid is True
        assert status.result_code == AuditValidationResult.SUFFICIENT.value
        assert status.total_entries == 3
        assert status.has_start is True
        assert status.has_execute is True
        assert status.has_complete is True
    
    def test_timeline_calculation(self, db_with_complete_audit):
        """Test timeline calculation for complete audit."""
        validator = ACCompletionAuditValidator(db_with_complete_audit)
        status = validator.validate_ac_completion("AC-TEST-001")
        
        assert status.start_time == "2026-01-15T10:00:00Z"
        assert status.execute_time == "2026-01-15T10:15:00Z"
        assert status.complete_time == "2026-01-15T10:30:00Z"
        assert status.total_duration_minutes == 30.0
    
    def test_sequencing_validation(self, db_with_complete_audit):
        """Test operation sequencing is correct."""
        validator = ACCompletionAuditValidator(db_with_complete_audit)
        status = validator.validate_ac_completion("AC-TEST-001")
        
        assert status.is_sequenced is True
        assert status.sequence_order == ["AC_START", "AC_EXECUTE", "AC_COMPLETE"]


# =============================================================================
# TEST: ACCompletionAuditValidator - Incomplete Audits
# =============================================================================

class TestACCompletionValidatorIncomplete:
    """Test validation of incomplete audit trails."""
    
    def test_no_entries(self, governance_db):
        """Test AC with no audit entries."""
        validator = ACCompletionAuditValidator(governance_db)
        status = validator.validate_ac_completion("AC-EMPTY")
        
        assert status.is_valid is False
        assert status.result_code == AuditValidationResult.NOT_FOUND.value
    
    def test_insufficient_entries(self, db_with_incomplete_audit):
        """Test AC with insufficient entries."""
        validator = ACCompletionAuditValidator(db_with_incomplete_audit)
        status = validator.validate_ac_completion("AC-INCOMPLETE")
        
        assert status.is_valid is False
        assert status.result_code == AuditValidationResult.INSUFFICIENT.value
        assert status.total_entries == 2
    
    def test_missing_start_operation(self, governance_db):
        """Test AC missing AC_START."""
        conn = sqlite3.connect(governance_db)
        cursor = conn.cursor()
        
        # Add 3 entries but no START
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:00:00Z", "AC-NO-START", "AC_VERIFY", "system", "{}")
        )
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:05:00Z", "AC-NO-START", "AC_EXECUTE", "system", "{}")
        )
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:15:00Z", "AC-NO-START", "AC_COMPLETE", "system", "{}")
        )
        conn.commit()
        conn.close()
        
        validator = ACCompletionAuditValidator(governance_db)
        status = validator.validate_ac_completion("AC-NO-START")
        
        assert status.is_valid is False
        assert status.result_code == AuditValidationResult.MISSING_START.value
    
    def test_missing_execute_operation(self, governance_db):
        """Test AC missing AC_EXECUTE."""
        conn = sqlite3.connect(governance_db)
        cursor = conn.cursor()
        
        # Add 3 entries but no EXECUTE
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:00:00Z", "AC-NO-EXEC", "AC_START", "system", "{}")
        )
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:05:00Z", "AC-NO-EXEC", "AC_VERIFY", "system", "{}")
        )
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:15:00Z", "AC-NO-EXEC", "AC_COMPLETE", "system", "{}")
        )
        conn.commit()
        conn.close()
        
        validator = ACCompletionAuditValidator(governance_db)
        status = validator.validate_ac_completion("AC-NO-EXEC")
        
        assert status.is_valid is False
        assert status.result_code == AuditValidationResult.MISSING_EXECUTE.value
    
    def test_missing_complete_operation(self, governance_db):
        """Test AC missing AC_COMPLETE."""
        conn = sqlite3.connect(governance_db)
        cursor = conn.cursor()
        
        # Add 3 entries but no COMPLETE
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:00:00Z", "AC-NO-COMP", "AC_START", "system", "{}")
        )
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:05:00Z", "AC-NO-COMP", "AC_EXECUTE", "system", "{}")
        )
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:15:00Z", "AC-NO-COMP", "AC_VERIFY", "system", "{}")
        )
        conn.commit()
        conn.close()
        
        validator = ACCompletionAuditValidator(governance_db)
        status = validator.validate_ac_completion("AC-NO-COMP")
        
        assert status.is_valid is False
        assert status.result_code == AuditValidationResult.MISSING_COMPLETE.value


# =============================================================================
# TEST: ACCompletionAuditValidator - Sequencing
# =============================================================================

class TestSequencingValidation:
    """Test operation sequencing validation."""
    
    def test_correct_sequencing(self, db_with_complete_audit):
        """Test correct operation sequence."""
        validator = ACCompletionAuditValidator(db_with_complete_audit)
        status = validator.validate_ac_completion("AC-TEST-001")
        
        assert status.is_sequenced is True
    
    def test_out_of_order_operations(self, governance_db):
        """Test out-of-order operations are rejected."""
        conn = sqlite3.connect(governance_db)
        cursor = conn.cursor()
        
        # Insert in wrong order: EXECUTE, START, COMPLETE
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:00:00Z", "AC-BAD-ORDER", "AC_EXECUTE", "system", "{}")
        )
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:15:00Z", "AC-BAD-ORDER", "AC_START", "system", "{}")
        )
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:30:00Z", "AC-BAD-ORDER", "AC_COMPLETE", "system", "{}")
        )
        conn.commit()
        conn.close()
        
        validator = ACCompletionAuditValidator(governance_db)
        status = validator.validate_ac_completion("AC-BAD-ORDER")
        
        assert status.is_valid is False
        assert status.result_code == AuditValidationResult.SEQUENCING_ERROR.value


# =============================================================================
# TEST: AuditRequiredValidator
# =============================================================================

class TestAuditRequiredValidator:
    """Test audit requirement enforcement."""
    
    def test_can_mark_complete_with_valid_audit(self, db_with_complete_audit):
        """Test AC can be marked complete with valid audit."""
        validator = AuditRequiredValidator(db_with_complete_audit)
        allowed, reason = validator.can_mark_ac_complete("AC-TEST-001")
        
        assert allowed is True
        assert "ready" in reason.lower()
    
    def test_cannot_mark_incomplete_audit(self, governance_db):
        """Test AC cannot be marked complete without audit."""
        validator = AuditRequiredValidator(governance_db)
        allowed, reason = validator.can_mark_ac_complete("AC-EMPTY")
        
        assert allowed is False
        assert "audit" in reason.lower() or "not found" in reason.lower()
    
    def test_get_completion_blockers(self, governance_db):
        """Test getting completion blockers."""
        conn = sqlite3.connect(governance_db)
        cursor = conn.cursor()
        
        # Only START operation
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:00:00Z", "AC-BLOCKED", "AC_START", "system", "{}")
        )
        conn.commit()
        conn.close()
        
        validator = AuditRequiredValidator(governance_db)
        blockers = validator.get_completion_blockers("AC-BLOCKED")
        
        assert len(blockers) > 0
        assert any("insufficient" in b.lower() or "only" in b.lower() for b in blockers)
    
    def test_get_ac_audit_summary(self, db_with_complete_audit):
        """Test getting comprehensive audit summary."""
        validator = AuditRequiredValidator(db_with_complete_audit)
        summary = validator.get_ac_audit_summary("AC-TEST-001")
        
        assert summary["ready_for_completion"] is True
        assert summary["entries_count"] == 3
        assert summary["operations"]["start"] is True
        assert summary["operations"]["execute"] is True
        assert summary["operations"]["complete"] is True


# =============================================================================
# TEST: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_duplicate_operations(self, governance_db):
        """Test AC with duplicate operations."""
        conn = sqlite3.connect(governance_db)
        cursor = conn.cursor()
        
        # Multiple START operations
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:00:00Z", "AC-DUPS", "AC_START", "system", "{}")
        )
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:05:00Z", "AC-DUPS", "AC_START", "system", "{}")
        )
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:10:00Z", "AC-DUPS", "AC_EXECUTE", "system", "{}")
        )
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:15:00Z", "AC-DUPS", "AC_COMPLETE", "system", "{}")
        )
        conn.commit()
        conn.close()
        
        validator = AuditRequiredValidator(governance_db)
        # Should still be valid (only checks presence, not count uniqueness)
        allowed, reason = validator.can_mark_ac_complete("AC-DUPS")
        
        assert allowed is True
    
    def test_additional_operations(self, governance_db):
        """Test AC with additional VERIFY operations."""
        conn = sqlite3.connect(governance_db)
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:00:00Z", "AC-EXTRA", "AC_START", "system", "{}")
        )
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:10:00Z", "AC-EXTRA", "AC_EXECUTE", "system", "{}")
        )
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:15:00Z", "AC-EXTRA", "AC_VERIFY", "system", "{}")
        )
        cursor.execute(
            """INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) 
               VALUES (?, ?, ?, ?, ?)""",
            ("2026-01-15T10:20:00Z", "AC-EXTRA", "AC_COMPLETE", "system", "{}")
        )
        conn.commit()
        conn.close()
        
        validator = AuditRequiredValidator(governance_db)
        allowed, reason = validator.can_mark_ac_complete("AC-EXTRA")
        
        assert allowed is True
    
    def test_invalid_db_path(self):
        """Test handling of invalid database path."""
        validator = ACCompletionAuditValidator("/nonexistent/path.db")
        status = validator.validate_ac_completion("AC-TEST")
        
        assert status.is_valid is False
        assert status.result_code == AuditValidationResult.DATABASE_ERROR.value
