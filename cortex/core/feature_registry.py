"""Live feature discovery system."""

from typing import Any, Dict, List, Optional


class FeatureRegistry:
    """Manages live feature discovery and manifest system."""

    def __init__(self) -> None:
        """Initialize feature registry."""
        self.features: Dict[str, Any] = {}

    def register_feature(self, feature_id: str, metadata: Dict[str, Any]) -> None:
        """Register a feature with metadata."""
        self.features[feature_id] = metadata

    def get_feature(self, feature_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve feature metadata."""
        return self.features.get(feature_id)

    def list_features(self) -> List[str]:
        """List all registered features."""
        return list(self.features.keys())

    def is_enabled(self, feature_id: str) -> bool:
        """Check if feature is enabled."""
        feature = self.features.get(feature_id)
        return feature and feature.get("enabled", False) if feature else False
