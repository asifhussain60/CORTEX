"""
Tests for Planning Orchestrator Observer Integration (Task 5.1.2)

Test coverage:
    - Observer subscription/unsubscription
    - Phase completion event emission
    - Event payload validation
    - Observer notification on phase completion
    - Error handling for failing observers

Author: Asif Hussain
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from src.orchestrators.planning_orchestrator import PlanningOrchestrator


class TestPlanningOrchestratorObserver:
    """Test suite for Planning Orchestrator observer pattern integration."""
    
    @pytest.fixture
    def cortex_root(self, tmp_path):
        """Create temporary CORTEX root for testing."""
        root = tmp_path / "CORTEX"
        root.mkdir()
        
        # Create required directory structure
        brain = root / "cortex-brain"
        brain.mkdir()
        
        config_dir = brain / "config"
        config_dir.mkdir()
        
        plans_dir = brain / "documents" / "planning" / "features" / "active"
        plans_dir.mkdir(parents=True)
        
        # Create minimal schema
        schema = config_dir / "plan-schema.yaml"
        schema.write_text("""
version: "1.0"
required:
  - metadata
  - phases
""")
        
        return str(root)
    
    @pytest.fixture
    def orchestrator(self, cortex_root):
        """Create PlanningOrchestrator instance."""
        with patch('src.orchestrators.planning_orchestrator.ManifestValidator'):
            with patch('src.orchestrators.planning_orchestrator.ResponseTemplateManager'):
                orch = PlanningOrchestrator(cortex_root)
                orch.observers = []  # Ensure clean observer list
                return orch
    
    @pytest.fixture
    def mock_observer(self):
        """Create mock observer."""
        observer = Mock()
        observer.on_phase_completion = Mock()
        return observer
    
    # ==================== Subscription Tests ====================
    
    def test_subscribe_adds_observer(self, orchestrator, mock_observer):
        """Test that subscribe adds observer to list."""
        orchestrator.subscribe(mock_observer)
        
        assert mock_observer in orchestrator.observers
        assert len(orchestrator.observers) == 1
    
    def test_subscribe_prevents_duplicates(self, orchestrator, mock_observer):
        """Test that subscribing same observer twice doesn't duplicate."""
        orchestrator.subscribe(mock_observer)
        orchestrator.subscribe(mock_observer)
        
        assert len(orchestrator.observers) == 1
    
    def test_subscribe_multiple_observers(self, orchestrator):
        """Test subscribing multiple observers."""
        observer1 = Mock()
        observer2 = Mock()
        observer3 = Mock()
        
        orchestrator.subscribe(observer1)
        orchestrator.subscribe(observer2)
        orchestrator.subscribe(observer3)
        
        assert len(orchestrator.observers) == 3
        assert all(obs in orchestrator.observers for obs in [observer1, observer2, observer3])
    
    def test_unsubscribe_removes_observer(self, orchestrator, mock_observer):
        """Test that unsubscribe removes observer from list."""
        orchestrator.subscribe(mock_observer)
        orchestrator.unsubscribe(mock_observer)
        
        assert mock_observer not in orchestrator.observers
        assert len(orchestrator.observers) == 0
    
    def test_unsubscribe_nonexistent_observer_safe(self, orchestrator, mock_observer):
        """Test unsubscribing non-existent observer doesn't raise error."""
        # Should not raise exception
        orchestrator.unsubscribe(mock_observer)
        assert len(orchestrator.observers) == 0
    
    # ==================== Event Emission Tests ====================
    
    def test_emit_phase_completion_notifies_observer(self, orchestrator, mock_observer):
        """Test that phase completion event notifies subscribed observer."""
        orchestrator.subscribe(mock_observer)
        
        orchestrator._emit_phase_completion_event(
            phase_id="1",
            phase_name="Phase 1: Foundation",
            duration_seconds=120.5,
            dor_compliant=True,
            dod_compliant=True,
            threat_model_applied=True,
            acceptance_criteria_defined=True,
            estimated_hours=8,
            actual_hours=10
        )
        
        mock_observer.on_phase_completion.assert_called_once()
        call_args = mock_observer.on_phase_completion.call_args[0][0]
        
        assert call_args["phase_id"] == "1"
        assert call_args["phase_name"] == "Phase 1: Foundation"
        assert call_args["duration_seconds"] == 120.5
        assert call_args["dor_compliant"] is True
        assert call_args["dod_compliant"] is True
        assert call_args["threat_model_applied"] is True
        assert call_args["estimated_hours"] == 8
        assert call_args["actual_hours"] == 10
        assert "timestamp" in call_args
    
    def test_emit_phase_completion_notifies_multiple_observers(self, orchestrator):
        """Test that event notifies all subscribed observers."""
        observer1 = Mock()
        observer2 = Mock()
        observer3 = Mock()
        
        orchestrator.subscribe(observer1)
        orchestrator.subscribe(observer2)
        orchestrator.subscribe(observer3)
        
        orchestrator._emit_phase_completion_event(
            phase_id="2",
            phase_name="Phase 2: Development",
            dor_compliant=True,
            dod_compliant=False
        )
        
        observer1.on_phase_completion.assert_called_once()
        observer2.on_phase_completion.assert_called_once()
        observer3.on_phase_completion.assert_called_once()
    
    def test_emit_phase_completion_event_payload_complete(self, orchestrator, mock_observer):
        """Test that event payload contains all required fields."""
        orchestrator.subscribe(mock_observer)
        
        orchestrator._emit_phase_completion_event(
            phase_id="3",
            phase_name="Phase 3: Validation",
            duration_seconds=300.0,
            dor_compliant=True,
            dod_compliant=True,
            threat_model_applied=False,
            acceptance_criteria_defined=True,
            estimated_hours=12,
            actual_hours=15
        )
        
        call_args = mock_observer.on_phase_completion.call_args[0][0]
        
        required_fields = [
            "phase_id", "phase_name", "duration_seconds",
            "dor_compliant", "dod_compliant", "threat_model_applied",
            "acceptance_criteria_defined", "estimated_hours", "actual_hours",
            "timestamp"
        ]
        
        for field in required_fields:
            assert field in call_args, f"Missing required field: {field}"
    
    def test_emit_phase_completion_handles_observer_failure(self, orchestrator):
        """Test that observer failure doesn't break event emission to other observers."""
        failing_observer = Mock()
        failing_observer.on_phase_completion = Mock(side_effect=Exception("Observer error"))
        
        working_observer = Mock()
        working_observer.on_phase_completion = Mock()
        
        orchestrator.subscribe(failing_observer)
        orchestrator.subscribe(working_observer)
        
        # Should not raise exception
        orchestrator._emit_phase_completion_event(
            phase_id="1",
            phase_name="Test Phase",
            dor_compliant=True,
            dod_compliant=True
        )
        
        # Working observer should still be called
        working_observer.on_phase_completion.assert_called_once()
    
    def test_emit_phase_completion_estimation_accuracy_data(self, orchestrator, mock_observer):
        """Test that estimation accuracy data is preserved."""
        orchestrator.subscribe(mock_observer)
        
        orchestrator._emit_phase_completion_event(
            phase_id="1",
            phase_name="Test Phase",
            estimated_hours=10,
            actual_hours=12,  # 20% over estimate
            dor_compliant=True,
            dod_compliant=True
        )
        
        call_args = mock_observer.on_phase_completion.call_args[0][0]
        
        assert call_args["estimated_hours"] == 10
        assert call_args["actual_hours"] == 12
        # LearningObserver calculates: actual/estimated = 12/10 = 1.2
    
    # ==================== Default Value Tests ====================
    
    def test_emit_phase_completion_default_values(self, orchestrator, mock_observer):
        """Test that default values are properly set."""
        orchestrator.subscribe(mock_observer)
        
        orchestrator._emit_phase_completion_event(
            phase_id="1",
            phase_name="Test Phase"
            # All other parameters use defaults
        )
        
        call_args = mock_observer.on_phase_completion.call_args[0][0]
        
        assert call_args["duration_seconds"] == 0.0
        assert call_args["dor_compliant"] is False
        assert call_args["dod_compliant"] is False
        assert call_args["threat_model_applied"] is False
        assert call_args["acceptance_criteria_defined"] is False
        assert call_args["estimated_hours"] == 0
        assert call_args["actual_hours"] == 0
    
    # ==================== Integration Tests ====================
    
    def test_observer_pattern_integration(self, orchestrator):
        """Test complete observer pattern integration flow."""
        from src.orchestrators.learning_observer import LearningObserver
        
        # Create mock KG
        mock_kg = Mock()
        mock_kg.store_pattern = Mock(return_value={"pattern_id": "test-123"})
        
        # Create real observer
        observer = LearningObserver(mock_kg)
        
        # Subscribe
        orchestrator.subscribe(observer)
        
        # Emit event
        orchestrator._emit_phase_completion_event(
            phase_id="1",
            phase_name="Phase 1: Foundation",
            duration_seconds=120.0,
            dor_compliant=True,
            dod_compliant=True,
            threat_model_applied=True,
            acceptance_criteria_defined=True,
            estimated_hours=8,
            actual_hours=10
        )
        
        # Verify observer captured pattern
        mock_kg.store_pattern.assert_called_once()
        call_args = mock_kg.store_pattern.call_args
        
        assert call_args.kwargs["pattern_type"] == "workflow"
        assert "Phase 1: Foundation" in call_args.kwargs["title"]
        assert call_args.kwargs["metadata"]["dor_compliant"] is True
        assert call_args.kwargs["source"] == "planning_orchestrator"
