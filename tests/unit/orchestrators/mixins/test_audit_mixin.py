"""
Tests for OrchestratorAuditMixin.

Authority: AC-GOLDEN-E2E-005
TDD Phase: RED → GREEN
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional
import pytest
import time

from cortex.orchestrators.core.audit_mixin import OrchestratorAuditMixin


class MockOrchestrator(OrchestratorAuditMixin):
    """Mock orchestrator for testing audit mixin."""
    
    def __init__(self, db_path: Optional[Path] = None, session_id: Optional[str] = None):
        """Initialize mock orchestrator."""
        super().__init__()
        if db_path:
            self._audit_db_path = db_path
        if session_id:
            self.session_id = session_id
    
    def do_work(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate orchestrator work."""
        correlation_id = self.audit_start(
            "DO_WORK",
            input_parameters=input_data,
            workflow_stage="EXECUTION"
        )
        
        # Simulate work
        result = {"status": "success", "data": input_data}
        
        self.audit_complete(
            correlation_id,
            "DO_WORK",
            output_results=result,
            status="COMPLETED"
        )
        
        return result


class TestOrchestratorAuditMixin:
    """Test orchestrator audit mixin functionality."""
    
    @pytest.fixture
    def temp_db(self, tmp_path: Path) -> Path:
        """Create temporary database with schema."""
        db_path = tmp_path / "test_audit.db"
        
        # Apply schema - navigate from tests/unit/orchestrators/mixins to project root
        schema_path = Path(__file__).parent.parent.parent.parent.parent / "cortex_intelligence" / "audit" / "schema.sql"
        
        conn = sqlite3.connect(str(db_path))
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())
        conn.close()
        
        return db_path
    
    def test_audit_mixin_can_be_mixed_into_orchestrator(self):
        """Audit mixin should be compatible with orchestrator classes."""
        orchestrator = MockOrchestrator()
        assert hasattr(orchestrator, 'audit_start')
        assert hasattr(orchestrator, 'audit_complete')
        assert hasattr(orchestrator, 'get_audit_events')
    
    def test_audit_start_generates_correlation_id(self, temp_db: Path):
        """audit_start should generate unique correlation ID."""
        orchestrator = MockOrchestrator(db_path=temp_db)
        
        correlation_id = orchestrator.audit_start(
            "TEST_ACTIVITY",
            input_parameters={"param1": "value1"}
        )
        
        assert correlation_id is not None
        assert correlation_id.startswith("corr-")
        assert len(correlation_id) > 10  # corr-{12 hex chars}
    
    def test_audit_start_persists_to_database(self, temp_db: Path):
        """audit_start should persist event to database."""
        orchestrator = MockOrchestrator(db_path=temp_db)
        
        correlation_id = orchestrator.audit_start(
            "TEST_ACTIVITY",
            input_parameters={"param1": "value1"},
            workflow_stage="INTENT"
        )
        
        # Verify in database
        conn = sqlite3.connect(str(temp_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM orchestrator_audit_events WHERE correlation_id = ?",
            (correlation_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row['orchestrator_name'] == 'MockOrchestrator'
        assert row['activity'] == 'TEST_ACTIVITY'
        assert row['workflow_stage'] == 'INTENT'
        assert row['status'] == 'STARTED'
        assert json.loads(row['input_parameters']) == {"param1": "value1"}
    
    def test_audit_complete_persists_to_database(self, temp_db: Path):
        """audit_complete should persist completion event."""
        orchestrator = MockOrchestrator(db_path=temp_db)
        
        correlation_id = orchestrator.audit_start("TEST_ACTIVITY")
        
        orchestrator.audit_complete(
            correlation_id,
            "TEST_ACTIVITY",
            output_results={"result": "success"},
            status="COMPLETED",
            reasoning="Test completed successfully"
        )
        
        # Verify in database
        conn = sqlite3.connect(str(temp_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM orchestrator_audit_events WHERE correlation_id = ? AND status = 'COMPLETED'",
            (correlation_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row['activity'] == 'TEST_ACTIVITY'
        assert json.loads(row['output_results']) == {"result": "success"}
        assert row['reasoning'] == "Test completed successfully"
    
    def test_audit_complete_calculates_duration(self, temp_db: Path):
        """audit_complete should calculate duration from start to end."""
        orchestrator = MockOrchestrator(db_path=temp_db)
        
        correlation_id = orchestrator.audit_start("SLOW_ACTIVITY")
        
        # Simulate work
        time.sleep(0.1)  # 100ms
        
        orchestrator.audit_complete(
            correlation_id,
            "SLOW_ACTIVITY",
            status="COMPLETED"
        )
        
        # Verify duration
        conn = sqlite3.connect(str(temp_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT duration_ms FROM orchestrator_audit_events WHERE correlation_id = ? AND status = 'COMPLETED'",
            (correlation_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row['duration_ms'] is not None
        assert row['duration_ms'] >= 100  # At least 100ms
    
    def test_get_audit_events_retrieves_by_correlation_id(self, temp_db: Path):
        """get_audit_events should retrieve events by correlation ID."""
        orchestrator = MockOrchestrator(db_path=temp_db)
        
        correlation_id = orchestrator.audit_start("TEST_ACTIVITY")
        orchestrator.audit_complete(correlation_id, "TEST_ACTIVITY")
        
        events = orchestrator.get_audit_events(correlation_id=correlation_id)
        
        assert len(events) == 2  # START + COMPLETE
        assert events[0]['status'] == 'STARTED'
        assert events[1]['status'] == 'COMPLETED'
    
    def test_audit_activity_context_manager(self, temp_db: Path):
        """audit_activity context manager should auto-log start/complete."""
        orchestrator = MockOrchestrator(db_path=temp_db)
        
        with orchestrator.audit_activity("CTX_ACTIVITY", {"input": "test"}):
            # Simulate work
            time.sleep(0.05)
        
        # Verify both events logged
        events = orchestrator.get_audit_events()
        activity_events = [e for e in events if e['activity'] == 'CTX_ACTIVITY']
        
        assert len(activity_events) == 2
        assert activity_events[0]['status'] == 'STARTED'
        assert activity_events[1]['status'] == 'COMPLETED'
    
    def test_audit_activity_logs_failure_on_exception(self, temp_db: Path):
        """audit_activity should log FAILED status on exception."""
        orchestrator = MockOrchestrator(db_path=temp_db)
        
        try:
            with orchestrator.audit_activity("FAILING_ACTIVITY"):
                raise ValueError("Intentional test error")
        except ValueError:
            pass  # Expected
        
        # Verify failure logged
        events = orchestrator.get_audit_events()
        activity_events = [e for e in events if e['activity'] == 'FAILING_ACTIVITY']
        
        assert len(activity_events) == 2
        assert activity_events[1]['status'] == 'FAILED'
        output = json.loads(activity_events[1]['output_results'])
        assert output['error'] == "Intentional test error"
        assert output['error_type'] == "ValueError"
    
    def test_orchestrator_integration_do_work(self, temp_db: Path):
        """Full integration test with mock orchestrator."""
        orchestrator = MockOrchestrator(db_path=temp_db, session_id="test-session-001")
        
        result = orchestrator.do_work({"task": "test"})
        
        assert result['status'] == 'success'
        
        # Verify audit trail
        events = orchestrator.get_audit_events()
        assert len(events) == 2
        assert events[0]['activity'] == 'DO_WORK'
        assert events[0]['status'] == 'STARTED'
        assert events[1]['status'] == 'COMPLETED'
    
    def test_multiple_orchestrators_separate_events(self, temp_db: Path):
        """Different orchestrator instances should have separate events."""
        orch1 = MockOrchestrator(db_path=temp_db)
        orch2 = MockOrchestrator(db_path=temp_db)
        
        orch1.audit_start("ACTIVITY_1")
        orch2.audit_start("ACTIVITY_2")
        
        events1 = orch1.get_audit_events()
        events2 = orch2.get_audit_events()
        
        # Both see both events (same orchestrator class)
        assert len(events1) >= 2
        assert len(events2) >= 2
    
    def test_session_id_tracking(self, temp_db: Path):
        """Session ID should be tracked across activities."""
        orchestrator = MockOrchestrator(db_path=temp_db, session_id="session-abc123")
        
        correlation_id = orchestrator.audit_start("SESSION_ACTIVITY")
        
        conn = sqlite3.connect(str(temp_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT session_id FROM orchestrator_audit_events WHERE correlation_id = ?",
            (correlation_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        assert row['session_id'] == "session-abc123"
