"""
Test Base Test Classes

Verify base test classes provide correct fixtures and helpers.

Authority: AC-GOLDEN-FRAMEWORK-002
"""
from pathlib import Path
import sqlite3

import pytest

# Import using underscore naming (Python module convention)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from base_orchestrator_test import BaseOrchestratorTest
from base_negative_test import BaseNegativeTest
from base_edge_case_test import BaseEdgeCaseTest
from base_recovery_test import BaseRecoveryTest


class TestBaseOrchestratorTest:
    """Test BaseOrchestratorTest fixtures and helpers."""
    
    def test_provides_real_event_bus_fixture(self):
        """Should provide real EventBus fixture."""
        base = BaseOrchestratorTest()
        # Fixture exists and has correct signature
        assert hasattr(base, 'real_event_bus')
    
    def test_provides_audit_db_fixture(self, tmp_path):
        """Should provide real SQLite audit database fixture."""
        base = BaseOrchestratorTest()
        db_path = base.audit_db(tmp_path)
        
        assert db_path.exists()
        assert db_path.suffix == ".db"
        
        # Verify schema created
        conn = sqlite3.connect(db_path)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='audit_log'"
        )
        assert cursor.fetchone() is not None
        conn.close()
    
    def test_provides_real_registry_fixture(self):
        """Should provide real GitBackedRegistry fixture."""
        base = BaseOrchestratorTest()
        assert hasattr(base, 'real_registry')
    
    def test_assert_audit_trail_helper(self, tmp_path):
        """Should verify audit trail entries."""
        base = BaseOrchestratorTest()
        db_path = base.audit_db(tmp_path)
        
        # Insert test entry
        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO audit_log (ac_id, timestamp, operation, status) VALUES (?, ?, ?, ?)",
            ("AC-TEST-001", "2026-02-15T10:00:00", "test", "COMPLETE")
        )
        conn.commit()
        conn.close()
        
        # Should pass
        base.assert_audit_trail(db_path, "AC-TEST-001")
    
    def test_assert_audit_trail_fails_when_missing(self, tmp_path):
        """Should fail when audit entry missing."""
        base = BaseOrchestratorTest()
        db_path = base.audit_db(tmp_path)
        
        with pytest.raises(AssertionError, match="Audit trail missing"):
            base.assert_audit_trail(db_path, "AC-MISSING-001")
    
    def test_create_test_context_helper(self):
        """Should create test orchestration context."""
        base = BaseOrchestratorTest()
        context = base.create_test_context(intent="IMPLEMENT", user_request="test")
        
        assert context["intent"] == "IMPLEMENT"
        assert context["user_request"] == "test"
        assert context["source"] == "test"
        assert "session_id" in context


class TestBaseNegativeTest:
    """Test BaseNegativeTest helpers."""
    
    def test_assert_blocked_helper(self):
        """Should verify action is blocked correctly."""
        base = BaseNegativeTest()
        
        def forbidden_action():
            raise ValueError("MCP bypass not allowed")
        
        # Should pass
        base.assert_blocked(
            action=forbidden_action,
            expected_error=ValueError,
            expected_message_contains="MCP bypass"
        )
    
    def test_assert_blocked_fails_on_wrong_error(self):
        """Should fail when wrong exception type raised."""
        base = BaseNegativeTest()
        
        def action():
            raise TypeError("wrong error")
        
        with pytest.raises(TypeError):
            base.assert_blocked(
                action=action,
                expected_error=ValueError,
                expected_message_contains="test"
            )


class TestBaseEdgeCaseTest:
    """Test BaseEdgeCaseTest helpers."""
    
    def test_create_extreme_context_empty(self):
        """Should create empty extreme context."""
        base = BaseEdgeCaseTest()
        context = base.create_extreme_context("empty")
        
        assert context["user_request"] == ""
        assert context["context"] == {}
        assert context["dependencies"] == []
    
    def test_create_extreme_context_massive(self):
        """Should create massive extreme context."""
        base = BaseEdgeCaseTest()
        context = base.create_extreme_context("massive")
        
        assert len(context["user_request"]) == 1_000_000
        assert len(context["context"]) == 10_000
        assert len(context["dependencies"]) == 1_000
    
    def test_create_extreme_context_circular(self):
        """Should create circular dependency context."""
        base = BaseEdgeCaseTest()
        context = base.create_extreme_context("circular")
        
        assert "A" in context["dependencies"]
        assert context["dependencies"].count("A") > 1  # Circular


class TestBaseRecoveryTest:
    """Test BaseRecoveryTest helpers."""
    
    def test_simulate_crash_helper(self):
        """Should simulate crash at execution point."""
        base = BaseRecoveryTest()
        
        def action():
            return "success"
        
        crash = base.simulate_crash(action, crash_point="mid_execution")
        
        assert isinstance(crash, Exception)
        assert "Simulated mid-execution crash" in str(crash)
    
    def test_assert_state_recovered_helper(self, tmp_path):
        """Should verify state recovery logged."""
        base = BaseRecoveryTest()
        db_path = base.audit_db(tmp_path)
        
        # Insert recovery entry
        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO audit_log (ac_id, timestamp, operation, status, details) VALUES (?, ?, ?, ?, ?)",
            ("AC-RECOVER-001", "2026-02-15T10:00:00", "RECOVERY", "COMPLETE", "routing_complete")
        )
        conn.commit()
        conn.close()
        
        # Should pass
        base.assert_state_recovered(db_path, "routing_complete")
    
    def test_assert_rollback_complete_helper(self, tmp_path):
        """Should verify rollback completion."""
        base = BaseRecoveryTest()
        db_path = base.audit_db(tmp_path)
        
        # Insert rollback entry
        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO audit_log (ac_id, timestamp, operation, status) VALUES (?, ?, ?, ?)",
            ("AC-TEST-001", "2026-02-15T10:00:00", "test", "ROLLED_BACK")
        )
        conn.commit()
        conn.close()
        
        # Should pass
        base.assert_rollback_complete(db_path, "AC-TEST-001")
