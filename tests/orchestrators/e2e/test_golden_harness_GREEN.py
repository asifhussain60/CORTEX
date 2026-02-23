"""
Tests for Golden Test Harness (GREEN Phase).

Authority: AC-GOLDEN-E2E-018
TDD Phase: GREEN - These tests demonstrate audit logging working
"""

import pytest
from pathlib import Path

from tests.orchestrators.e2e.test_golden_harness import (
    GoldenTestHarness,
    AuditAssertion,
)
from cortex.orchestrators.core.audit_mixin import OrchestratorAuditMixin


class MockMasterOrchestrator(OrchestratorAuditMixin):
    """Mock MasterOrchestrator for GREEN testing."""
    
    def __init__(self, db_path: Path):
        super().__init__()
        self._audit_db_path = db_path
        self.session_id = "test-session-green"
    
    def classify_intent(self, utterance: str) -> dict:
        """Mock intent classification with audit logging."""
        with self.audit_activity(
            "CLASSIFY_INTENT",
            input_parameters={"utterance": utterance},
            workflow_stage="INTENT"
        ) as correlation_id:
            # Mock classification
            if "implement" in utterance.lower():
                intent_type = "IMPLEMENT"
            elif "fix" in utterance.lower():
                intent_type = "FIX"
            elif "golden" in utterance.lower() or "e2e" in utterance.lower():
                intent_type = "TEST"
            else:
                intent_type = "UNKNOWN"
            
            return {
                "intent_type": intent_type,
                "confidence": 0.95,
                "correlation_id": correlation_id
            }


class TestGoldenTestHarnessGREEN:
    """GREEN tests - audit logging is implemented."""
    
    @pytest.fixture
    def temp_db(self, tmp_path: Path) -> Path:
        """Create temporary database with schema."""
        db_path = tmp_path / "test_audit.db"
        
        # Apply schema
        schema_path = Path(__file__).parent.parent.parent.parent / "cortex" / "intelligence" / "audit" / "schema.sql"
        
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())
        conn.close()
        
        return db_path
    
    @pytest.fixture
    def harness(self, temp_db: Path) -> GoldenTestHarness:
        """Create golden test harness."""
        return GoldenTestHarness(db_path=temp_db)
    
    def test_audit_logging_works_with_mixin(self, temp_db: Path):
        """
        GREEN TEST: Audit logging works with OrchestratorAuditMixin.
        
        This demonstrates the GREEN phase:
        - Orchestrator uses audit mixin
        - Events are logged to database
        - Events can be retrieved
        """
        orchestrator = MockMasterOrchestrator(db_path=temp_db)
        
        result = orchestrator.classify_intent("implement user authentication")
        
        # Verify audit events were logged
        events = orchestrator.get_audit_events(correlation_id=result["correlation_id"])
        
        assert len(events) >= 2  # START + COMPLETE
        assert events[0]['activity'] == 'CLASSIFY_INTENT'
        assert events[0]['status'] == 'STARTED'
        assert events[-1]['status'] == 'COMPLETED'
    
    def test_audit_sequence_validation_passes(self, temp_db: Path, harness: GoldenTestHarness):
        """
        GREEN TEST: Audit sequence validation passes when events present.
        """
        orchestrator = MockMasterOrchestrator(db_path=temp_db)
        
        result = orchestrator.classify_intent("implement feature X")
        correlation_id = result["correlation_id"]
        
        # Define expected sequence
        expected_sequence = [
            AuditAssertion(
                orchestrator="MockMasterOrchestrator",
                activity="CLASSIFY_INTENT",
                workflow_stage="INTENT"
            )
        ]
        
        # Should NOT raise AssertionError
        harness.assert_audit_sequence(correlation_id, expected_sequence)
    
    def test_field_assertions_work(self, temp_db: Path):
        """GREEN TEST: Field assertions validate correctly."""
        orchestrator = MockMasterOrchestrator(db_path=temp_db)
        
        result = orchestrator.classify_intent("implement feature")
        
        # Verify output contains expected fields
        assert result["intent_type"] == "IMPLEMENT"
        assert result["confidence"] >= 0.90
    
    def test_multiple_orchestrator_activities(self, temp_db: Path):
        """GREEN TEST: Multiple activities are logged correctly."""
        orchestrator = MockMasterOrchestrator(db_path=temp_db)
        
        # Classify multiple intents
        result1 = orchestrator.classify_intent("implement login")
        result2 = orchestrator.classify_intent("fix authentication bug")
        result3 = orchestrator.classify_intent("run golden tests")
        
        # Verify all events logged
        all_events = orchestrator.get_audit_events()
        
        # Should have 6 events (2 per activity: START + COMPLETE)
        assert len(all_events) >= 6
        
        # Verify intents classified correctly
        assert result1["intent_type"] == "IMPLEMENT"
        assert result2["intent_type"] == "FIX"
        assert result3["intent_type"] == "TEST"
    
    def test_harness_load_scenario_works(self, harness: GoldenTestHarness):
        """GREEN TEST: Harness can load scenarios."""
        scenario = harness.load_scenario("golden_01_implement_flow")
        
        assert scenario.name == "golden_01_implement_flow"
        assert len(scenario.expected_audit_events) > 0
    
    def test_duration_tracking(self, temp_db: Path):
        """GREEN TEST: Duration is tracked for activities."""
        orchestrator = MockMasterOrchestrator(db_path=temp_db)
        
        result = orchestrator.classify_intent("implement feature")
        
        events = orchestrator.get_audit_events(correlation_id=result["correlation_id"])
        completed_event = [e for e in events if e['status'] == 'COMPLETED'][0]
        
        # Should have duration tracked
        assert completed_event['duration_ms'] is not None
        assert completed_event['duration_ms'] >= 0


class TestGoldenTestHarnessIntegration:
    """Integration tests with real audit database."""
    
    def test_production_database_has_table(self):
        """Production governance.db should have orchestrator_audit_events table."""
        import sqlite3
        
        db_path = Path(__file__).parent.parent.parent.parent / "cortex.intelligence" / "governance.db"
        
        if not db_path.exists():
            pytest.skip("Production database not found")
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='orchestrator_audit_events'"
        )
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None, "orchestrator_audit_events table missing in production DB"
    
    def test_production_database_has_view(self):
        """Production database should have golden test audit trail view."""
        import sqlite3
        
        db_path = Path(__file__).parent.parent.parent.parent / "cortex.intelligence" / "governance.db"
        
        if not db_path.exists():
            pytest.skip("Production database not found")
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='view' AND name='v_golden_test_audit_trail'"
        )
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None, "v_golden_test_audit_trail view missing"
