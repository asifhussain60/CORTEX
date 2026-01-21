"""Live feature discovery system."""

class FeatureRegistry:
    """Manages live feature discovery and manifest system."""
    
    def __init__(self):
        """Initialize feature registry."""
        self.features = {}
    
    def register_feature(self, feature_id, metadata):
        """Register a feature with metadata."""
        self.features[feature_id] = metadata
    
    def get_feature(self, feature_id):
        """Retrieve feature metadata."""
        return self.features.get(feature_id)
    
    def list_features(self):
        """List all registered features."""
        return list(self.features.keys())
    
    def is_enabled(self, feature_id):
        """Check if feature is enabled."""
        feature = self.features.get(feature_id)
        return feature and feature.get("enabled", False) if feature else False
