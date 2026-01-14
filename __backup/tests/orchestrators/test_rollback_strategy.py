"""
Tests for AC-ROLLOUT-SIMPLE-002: Rollback Strategy
Safe rollback for failed feature deployments.
"""
import pytest
from src.orchestrators.rollout_gates import RolloutGateManager, RolloutStage
from src.orchestrators.rollback_strategy import RollbackManager


@pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-002")
class TestRollbackStrategy:
    """Test safe rollback for feature deployments."""
    
    @pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-002")
    def test_rollback_manager_initialization(self):
        """AC-ROLLOUT-SIMPLE-002: Can initialize rollback manager."""
        gate_manager = RolloutGateManager()
        rollback_manager = RollbackManager(gate_manager)
        
        assert rollback_manager.gate_manager == gate_manager
    
    @pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-002")
    def test_save_rollback_point(self):
        """AC-ROLLOUT-SIMPLE-002: Can save rollback point before deployment."""
        gate_manager = RolloutGateManager()
        rollback_manager = RollbackManager(gate_manager)
        
        gate_manager.register_feature("risky-feature", RolloutStage.DISABLED)
        
        # Save state before rollout
        rollback_manager.save_rollback_point("risky-feature")
        
        assert rollback_manager.has_rollback_point("risky-feature")
    
    @pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-002")
    def test_rollback_to_previous_state(self):
        """AC-ROLLOUT-SIMPLE-002: Can rollback feature to previous state."""
        gate_manager = RolloutGateManager()
        rollback_manager = RollbackManager(gate_manager)
        
        gate_manager.register_feature("unstable-feature", RolloutStage.DISABLED)
        rollback_manager.save_rollback_point("unstable-feature")
        
        # Deploy to canary
        gate_manager.set_stage("unstable-feature", RolloutStage.CANARY)
        assert gate_manager.get_stage("unstable-feature") == RolloutStage.CANARY
        
        # Rollback after detecting issues
        rollback_manager.rollback("unstable-feature")
        assert gate_manager.get_stage("unstable-feature") == RolloutStage.DISABLED
    
    @pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-002")
    def test_rollback_without_save_point_fails(self):
        """AC-ROLLOUT-SIMPLE-002: Rollback without save point should fail safely."""
        gate_manager = RolloutGateManager()
        rollback_manager = RollbackManager(gate_manager)
        
        gate_manager.register_feature("no-backup", RolloutStage.CANARY)
        
        # Attempting rollback without save point
        with pytest.raises(ValueError, match="No rollback point"):
            rollback_manager.rollback("no-backup")
    
    @pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-002")
    def test_emergency_disable_all(self):
        """AC-ROLLOUT-SIMPLE-002: Can emergency disable all features."""
        gate_manager = RolloutGateManager()
        rollback_manager = RollbackManager(gate_manager)
        
        gate_manager.register_feature("feature-1", RolloutStage.GENERAL_AVAILABILITY)
        gate_manager.register_feature("feature-2", RolloutStage.CANARY)
        
        # Emergency shutdown
        rollback_manager.emergency_disable_all()
        
        assert gate_manager.get_stage("feature-1") == RolloutStage.DISABLED
        assert gate_manager.get_stage("feature-2") == RolloutStage.DISABLED
