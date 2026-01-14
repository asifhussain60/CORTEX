"""
Tests for AC-LIFECYCLE-001: Lifecycle State Management
7-state lifecycle: IDLE → SPEC → IMPLEMENTED → TESTED → VERIFIED → ACTIVE → DEPRECATED
"""
import pytest
from src.infrastructure.lifecycle_manager import LifecycleManager, LifecycleState


@pytest.mark.ac_id("AC-LIFECYCLE-001")
class TestLifecycleStateManagement:
    """Test 7-state orchestrator lifecycle management."""
    
    @pytest.mark.ac_id("AC-LIFECYCLE-001")
    def test_lifecycle_states_defined(self):
        """AC-LIFECYCLE-001: All 7 states must be defined."""
        expected_states = {
            LifecycleState.IDLE,
            LifecycleState.SPEC,
            LifecycleState.IMPLEMENTED,
            LifecycleState.TESTED,
            LifecycleState.VERIFIED,
            LifecycleState.ACTIVE,
            LifecycleState.DEPRECATED
        }
        assert len(expected_states) == 7
    
    @pytest.mark.ac_id("AC-LIFECYCLE-001")
    def test_state_transitions_valid(self):
        """AC-LIFECYCLE-001: Valid state transitions must be enforced."""
        manager = LifecycleManager()
        
        # Valid transition: IDLE → SPEC
        result = manager.transition_to(LifecycleState.SPEC)
        assert result.success is True
        assert manager.current_state == LifecycleState.SPEC
    
    @pytest.mark.ac_id("AC-LIFECYCLE-001")
    def test_invalid_state_transition_rejected(self):
        """AC-LIFECYCLE-001: Invalid transitions must be rejected."""
        manager = LifecycleManager()
        
        # Invalid: IDLE → VERIFIED (skipping states)
        result = manager.transition_to(LifecycleState.VERIFIED)
        assert result.success is False
        assert manager.current_state == LifecycleState.IDLE
    
    @pytest.mark.ac_id("AC-LIFECYCLE-001")
    def test_quarantine_on_error_threshold(self):
        """AC-LIFECYCLE-001: Quarantine if error rate > 10%."""
        manager = LifecycleManager()
        manager.transition_to(LifecycleState.ACTIVE)
        
        # Simulate 15% error rate
        for _ in range(15):
            manager.record_error()
        for _ in range(85):
            manager.record_success()
        
        # Should auto-quarantine
        assert manager.is_quarantined is True
    
    @pytest.mark.ac_id("AC-LIFECYCLE-001")
    def test_state_history_audit_trail(self):
        """AC-LIFECYCLE-001: All state transitions must be logged."""
        manager = LifecycleManager()
        
        manager.transition_to(LifecycleState.SPEC)
        manager.transition_to(LifecycleState.IMPLEMENTED)
        
        history = manager.get_state_history()
        assert len(history) >= 2
        assert history[0]['from_state'] == 'IDLE'
        assert history[0]['to_state'] == 'SPEC'
