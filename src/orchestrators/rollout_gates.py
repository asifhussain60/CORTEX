"""
AC-ROLLOUT-SIMPLE-001: Progressive Rollout Gates
Feature flag system for gradual capability rollout.
"""
from enum import Enum
from typing import Dict, Optional
import hashlib


class RolloutStage(Enum):
    """Progressive rollout stages."""
    DISABLED = "disabled"
    INTERNAL_ONLY = "internal_only"
    CANARY = "canary"
    GENERAL_AVAILABILITY = "general_availability"


class RolloutGateManager:
    """
    Manages feature flags and progressive rollout.
    
    Rollout progression:
    1. DISABLED: Feature blocked for all users
    2. INTERNAL_ONLY: Enabled only for internal testing
    3. CANARY: Enabled for X% of users (gradual rollout)
    4. GENERAL_AVAILABILITY: Enabled for all users
    """
    
    def __init__(self):
        self._features: Dict[str, Dict] = {}
    
    def register_feature(
        self,
        feature_id: str,
        stage: RolloutStage,
        canary_percent: int = 10
    ):
        """
        Register a feature with rollout stage.
        
        Args:
            feature_id: Unique feature identifier
            stage: Current rollout stage
            canary_percent: Percentage of users for canary (default 10%)
        """
        self._features[feature_id] = {
            'stage': stage,
            'canary_percent': canary_percent
        }
    
    def is_registered(self, feature_id: str) -> bool:
        """Check if feature is registered."""
        return feature_id in self._features
    
    def is_enabled(self, feature_id: str, user_id: str = "default") -> bool:
        """
        Check if feature is enabled for a user.
        
        Args:
            feature_id: Feature to check
            user_id: User identifier (for canary rollout)
            
        Returns:
            True if feature is enabled for this user
        """
        if not self.is_registered(feature_id):
            return False
        
        feature = self._features[feature_id]
        stage = feature['stage']
        
        if stage == RolloutStage.DISABLED:
            return False
        
        if stage == RolloutStage.INTERNAL_ONLY:
            # Only enable for internal users (could check user_id against allowlist)
            return user_id.startswith("internal-") or user_id == "test-user"
        
        if stage == RolloutStage.CANARY:
            # Use deterministic hash to assign users to canary
            canary_percent = feature['canary_percent']
            user_hash = int(hashlib.md5(f"{feature_id}:{user_id}".encode()).hexdigest(), 16)
            return (user_hash % 100) < canary_percent
        
        if stage == RolloutStage.GENERAL_AVAILABILITY:
            return True
        
        return False
    
    def set_stage(self, feature_id: str, stage: RolloutStage):
        """Update feature rollout stage."""
        if not self.is_registered(feature_id):
            raise ValueError(f"Feature not registered: {feature_id}")
        
        self._features[feature_id]['stage'] = stage
    
    def get_stage(self, feature_id: str) -> Optional[RolloutStage]:
        """Get current rollout stage for feature."""
        if not self.is_registered(feature_id):
            return None
        
        return self._features[feature_id]['stage']
