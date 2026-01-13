"""
Tests for AC-ROLLOUT-SIMPLE-001: Progressive Rollout Gates
Feature flags and gradual rollout for new capabilities.
"""
import pytest
from src.orchestrators.rollout_gates import RolloutGateManager, RolloutStage


@pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-001")
class TestProgressiveRolloutGates:
    """Test progressive feature rollout with gates."""
    
    @pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-001")
    def test_rollout_stages_defined(self):
        """AC-ROLLOUT-SIMPLE-001: Rollout stages must be defined."""
        expected_stages = {
            RolloutStage.DISABLED,
            RolloutStage.INTERNAL_ONLY,
            RolloutStage.CANARY,
            RolloutStage.GENERAL_AVAILABILITY
        }
        assert len(expected_stages) == 4
    
    @pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-001")
    def test_feature_flag_registration(self):
        """AC-ROLLOUT-SIMPLE-001: Can register feature flags."""
        manager = RolloutGateManager()
        
        manager.register_feature(
            feature_id="new-capability",
            stage=RolloutStage.DISABLED
        )
        
        assert manager.is_registered("new-capability")
    
    @pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-001")
    def test_feature_enabled_check(self):
        """AC-ROLLOUT-SIMPLE-001: Can check if feature is enabled."""
        manager = RolloutGateManager()
        
        # Internal user should always be enabled
        manager.register_feature("beta-feature", RolloutStage.INTERNAL_ONLY)
        
        assert manager.is_enabled("beta-feature", user_id="test-user")
    
    @pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-001")
    def test_disabled_features_blocked(self):
        """AC-ROLLOUT-SIMPLE-001: Disabled features must be blocked."""
        manager = RolloutGateManager()
        
        manager.register_feature("disabled-feature", RolloutStage.DISABLED)
        
        assert not manager.is_enabled("disabled-feature", user_id="any-user")
    
    @pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-001")
    def test_progressive_rollout_stages(self):
        """AC-ROLLOUT-SIMPLE-001: Can progress through rollout stages."""
        manager = RolloutGateManager()
        
        manager.register_feature("new-feature", RolloutStage.DISABLED)
        
        # Progress: DISABLED → INTERNAL_ONLY → CANARY → GA
        manager.set_stage("new-feature", RolloutStage.INTERNAL_ONLY)
        assert manager.get_stage("new-feature") == RolloutStage.INTERNAL_ONLY
        
        manager.set_stage("new-feature", RolloutStage.CANARY)
        assert manager.get_stage("new-feature") == RolloutStage.CANARY
        
        manager.set_stage("new-feature", RolloutStage.GENERAL_AVAILABILITY)
        assert manager.get_stage("new-feature") == RolloutStage.GENERAL_AVAILABILITY
    
    @pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-001")
    def test_canary_percentage_rollout(self):
        """AC-ROLLOUT-SIMPLE-001: Canary rollout respects percentage."""
        manager = RolloutGateManager()
        
        manager.register_feature("canary-feature", RolloutStage.CANARY, canary_percent=10)
        
        # Should enable for ~10% of users
        enabled_count = sum(
            1 for i in range(100)
            if manager.is_enabled("canary-feature", user_id=f"user-{i}")
        )
        
        # Allow 5-15% range (deterministic but approximate)
        assert 5 <= enabled_count <= 15
