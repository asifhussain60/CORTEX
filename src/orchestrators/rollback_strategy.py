"""
AC-ROLLOUT-SIMPLE-002: Rollback Strategy
Safe rollback mechanism for failed feature deployments.
"""
from typing import Dict
from src.orchestrators.rollout_gates import RolloutGateManager, RolloutStage


class RollbackManager:
    """
    Manages rollback points and safe feature rollback.
    
    Rollback flow:
    1. Save rollback point before deployment
    2. Deploy feature to next stage
    3. If issues detected, rollback to saved state
    4. Emergency disable all features if critical
    """
    
    def __init__(self, gate_manager: RolloutGateManager):
        self.gate_manager = gate_manager
        self._rollback_points: Dict[str, RolloutStage] = {}
    
    def save_rollback_point(self, feature_id: str):
        """
        Save current feature state as rollback point.
        
        Args:
            feature_id: Feature to save state for
        """
        current_stage = self.gate_manager.get_stage(feature_id)
        if current_stage is not None:
            self._rollback_points[feature_id] = current_stage
    
    def has_rollback_point(self, feature_id: str) -> bool:
        """Check if rollback point exists for feature."""
        return feature_id in self._rollback_points
    
    def rollback(self, feature_id: str):
        """
        Rollback feature to saved state.
        
        Args:
            feature_id: Feature to rollback
            
        Raises:
            ValueError: If no rollback point exists
        """
        if not self.has_rollback_point(feature_id):
            raise ValueError(f"No rollback point saved for feature: {feature_id}")
        
        saved_stage = self._rollback_points[feature_id]
        self.gate_manager.set_stage(feature_id, saved_stage)
    
    def emergency_disable_all(self):
        """
        Emergency shutdown: disable all features immediately.
        
        Use in critical situations where all new features
        must be disabled to restore stability.
        """
        # Access internal features dict to disable all
        for feature_id in self.gate_manager._features.keys():
            self.gate_manager.set_stage(feature_id, RolloutStage.DISABLED)
