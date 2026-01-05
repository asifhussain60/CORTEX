"""
CORTEX Audit Logger - Feature Flags System
Version: 1.0.0
Purpose: Dynamic feature control with per-orchestrator toggles and runtime reload
"""

import os
import threading
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml


class FeatureState(Enum):
    """Feature flag states"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    GRADUAL_ROLLOUT = "gradual_rollout"
    TESTING = "testing"


class RolloutStrategy(Enum):
    """Gradual rollout strategies"""
    PERCENTAGE = "percentage"
    USER_BASED = "user_based"
    ORCHESTRATOR_BASED = "orchestrator_based"
    TIME_BASED = "time_based"


class FeatureFlag:
    """Individual feature flag with metadata"""
    
    def __init__(
        self,
        name: str,
        state: FeatureState,
        description: str = "",
        rollout_percentage: int = 100,
        rollout_strategy: Optional[RolloutStrategy] = None,
        target_orchestrators: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        dependencies: Optional[List[str]] = None
    ):
        self.name = name
        self.state = state
        self.description = description
        self.rollout_percentage = rollout_percentage
        self.rollout_strategy = rollout_strategy
        self.target_orchestrators = target_orchestrators or []
        self.start_time = start_time
        self.end_time = end_time
        self.dependencies = dependencies or []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
    def is_enabled(self, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if feature is enabled for given context"""
        if self.state == FeatureState.DISABLED:
            return False
            
        if self.state == FeatureState.ENABLED:
            return True
            
        if self.state == FeatureState.TESTING:
            # Only enable in non-production environments
            env = os.getenv("CORTEX_ENV", "development")
            return env in ["development", "staging"]
            
        if self.state == FeatureState.GRADUAL_ROLLOUT:
            return self._evaluate_rollout(context)
            
        return False
        
    def _evaluate_rollout(self, context: Optional[Dict[str, Any]] = None) -> bool:
        """Evaluate gradual rollout criteria"""
        if not context:
            return False
            
        if self.rollout_strategy == RolloutStrategy.PERCENTAGE:
            # Simple percentage-based rollout
            import random
            return random.randint(1, 100) <= self.rollout_percentage
            
        elif self.rollout_strategy == RolloutStrategy.ORCHESTRATOR_BASED:
            # Enable for specific orchestrators
            orchestrator = context.get("orchestrator")
            return orchestrator in self.target_orchestrators
            
        elif self.rollout_strategy == RolloutStrategy.TIME_BASED:
            # Enable during specific time window
            now = datetime.now()
            if self.start_time and now < self.start_time:
                return False
            if self.end_time and now > self.end_time:
                return False
            return True
            
        return False
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "name": self.name,
            "state": self.state.value,
            "description": self.description,
            "rollout_percentage": self.rollout_percentage,
            "rollout_strategy": self.rollout_strategy.value if self.rollout_strategy else None,
            "target_orchestrators": self.target_orchestrators,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "dependencies": self.dependencies,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class FeatureFlagManager:
    """
    Feature flag management system with runtime reload
    
    Features:
    - Per-orchestrator feature toggles
    - Runtime configuration reload (no redeployment)
    - Gradual rollout support
    - Dependency management
    - Thread-safe operations
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.flags: Dict[str, FeatureFlag] = {}
            self.orchestrator_overrides: Dict[str, Dict[str, bool]] = {}
            self.config_path: Optional[Path] = None
            self.auto_reload = False
            self.reload_interval = 60  # seconds
            self.reload_thread: Optional[threading.Thread] = None
            self._stop_reload = threading.Event()
            self._initialized = True
            
    def load_from_config(self, config_path: str) -> None:
        """Load feature flags from YAML configuration"""
        self.config_path = Path(config_path)
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        self._parse_config(config)
        
    def _parse_config(self, config: Dict[str, Any]) -> None:
        """Parse configuration and create feature flags"""
        features = config.get("features", {})
        
        for feature_name, feature_config in features.items():
            state = FeatureState(feature_config.get("state", "disabled"))
            
            # Parse rollout strategy
            rollout_strategy = None
            if "rollout_strategy" in feature_config:
                rollout_strategy = RolloutStrategy(feature_config["rollout_strategy"])
                
            # Parse timestamps
            start_time = None
            if "start_time" in feature_config:
                start_time = datetime.fromisoformat(feature_config["start_time"])
                
            end_time = None
            if "end_time" in feature_config:
                end_time = datetime.fromisoformat(feature_config["end_time"])
                
            flag = FeatureFlag(
                name=feature_name,
                state=state,
                description=feature_config.get("description", ""),
                rollout_percentage=feature_config.get("rollout_percentage", 100),
                rollout_strategy=rollout_strategy,
                target_orchestrators=feature_config.get("target_orchestrators", []),
                start_time=start_time,
                end_time=end_time,
                dependencies=feature_config.get("dependencies", [])
            )
            
            self.flags[feature_name] = flag
            
        # Load orchestrator overrides
        self.orchestrator_overrides = config.get("orchestrator_overrides", {})
        
    def is_enabled(
        self,
        feature_name: str,
        orchestrator: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if feature is enabled
        
        Priority:
        1. Orchestrator-specific override
        2. Feature flag evaluation
        3. Default to False
        """
        # Check orchestrator override
        if orchestrator and orchestrator in self.orchestrator_overrides:
            if feature_name in self.orchestrator_overrides[orchestrator]:
                return self.orchestrator_overrides[orchestrator][feature_name]
                
        # Check feature flag
        if feature_name in self.flags:
            flag = self.flags[feature_name]
            
            # Check dependencies
            if flag.dependencies:
                for dep in flag.dependencies:
                    if not self.is_enabled(dep, orchestrator, context):
                        return False
                        
            # Add orchestrator to context
            if context is None:
                context = {}
            if orchestrator:
                context["orchestrator"] = orchestrator
                
            return flag.is_enabled(context)
            
        return False
        
    def enable_feature(self, feature_name: str) -> None:
        """Enable a feature flag"""
        if feature_name in self.flags:
            self.flags[feature_name].state = FeatureState.ENABLED
            self.flags[feature_name].updated_at = datetime.now()
            
    def disable_feature(self, feature_name: str) -> None:
        """Disable a feature flag"""
        if feature_name in self.flags:
            self.flags[feature_name].state = FeatureState.DISABLED
            self.flags[feature_name].updated_at = datetime.now()
            
    def set_orchestrator_override(
        self,
        orchestrator: str,
        feature_name: str,
        enabled: bool
    ) -> None:
        """Set orchestrator-specific feature override"""
        if orchestrator not in self.orchestrator_overrides:
            self.orchestrator_overrides[orchestrator] = {}
            
        self.orchestrator_overrides[orchestrator][feature_name] = enabled
        
    def remove_orchestrator_override(
        self,
        orchestrator: str,
        feature_name: str
    ) -> None:
        """Remove orchestrator-specific override"""
        if orchestrator in self.orchestrator_overrides:
            self.orchestrator_overrides[orchestrator].pop(feature_name, None)
            
    def reload_config(self) -> None:
        """Reload configuration from file"""
        if not self.config_path or not self.config_path.exists():
            return
            
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        self._parse_config(config)
        
    def start_auto_reload(self, interval: int = 60) -> None:
        """Start automatic configuration reload thread"""
        self.auto_reload = True
        self.reload_interval = interval
        self.reload_thread = threading.Thread(target=self._auto_reload_loop, daemon=True)
        self.reload_thread.start()
        
    def stop_auto_reload(self) -> None:
        """Stop automatic configuration reload"""
        self.auto_reload = False
        self._stop_reload.set()
        if self.reload_thread:
            self.reload_thread.join(timeout=5)
            
    def _auto_reload_loop(self) -> None:
        """Auto-reload loop (runs in background thread)"""
        while self.auto_reload and not self._stop_reload.is_set():
            try:
                self.reload_config()
            except Exception as e:
                print(f"Error reloading feature flags: {e}")
                
            self._stop_reload.wait(self.reload_interval)
            
    def get_all_flags(self) -> Dict[str, Dict[str, Any]]:
        """Get all feature flags as dictionary"""
        return {name: flag.to_dict() for name, flag in self.flags.items()}
        
    def get_enabled_features(self, orchestrator: Optional[str] = None) -> Set[str]:
        """Get set of enabled feature names"""
        enabled = set()
        for name in self.flags:
            if self.is_enabled(name, orchestrator):
                enabled.add(name)
        return enabled
        
    def export_to_file(self, output_path: str) -> None:
        """Export current configuration to file"""
        config = {
            "features": self.get_all_flags(),
            "orchestrator_overrides": self.orchestrator_overrides
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)


# Global instance
_feature_flags = FeatureFlagManager()


def get_feature_flags() -> FeatureFlagManager:
    """Get global feature flag manager instance"""
    return _feature_flags


def is_feature_enabled(
    feature_name: str,
    orchestrator: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Convenience function to check if feature is enabled
    
    Args:
        feature_name: Name of feature flag
        orchestrator: Orchestrator name (optional)
        context: Additional context for evaluation (optional)
        
    Returns:
        True if feature is enabled, False otherwise
    """
    return _feature_flags.is_enabled(feature_name, orchestrator, context)
