"""Feature discovery API endpoints."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# In-memory feature registry — populated at startup or via register_feature()
_FEATURE_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register_feature(
    feature_id: str,
    name: str,
    enabled: bool = True,
    **meta: Any,
) -> None:
    """Register a feature in the runtime registry.

    Args:
        feature_id: Unique feature identifier (e.g. "lens_analysis").
        name: Human-readable feature name.
        enabled: Whether the feature is currently active.
        **meta: Additional metadata (version, owner, rollout_pct, etc.).
    """
    _FEATURE_REGISTRY[feature_id] = {
        "id": feature_id,
        "name": name,
        "enabled": enabled,
        **meta,
    }


def get_features() -> List[Dict[str, Any]]:
    """Get all available features.

    Returns:
        List of feature metadata dicts sorted by feature id.
    """
    return sorted(_FEATURE_REGISTRY.values(), key=lambda f: f["id"])


def get_feature(feature_id: str) -> Optional[Dict[str, Any]]:
    """Get single feature metadata.

    Args:
        feature_id: The feature identifier to look up.

    Returns:
        Feature metadata dict, or None if not found.
    """
    return _FEATURE_REGISTRY.get(feature_id)


def list_enabled_features() -> List[Dict[str, Any]]:
    """Get only enabled features.

    Returns:
        List of feature metadata dicts where enabled is True.
    """
    return [f for f in _FEATURE_REGISTRY.values() if f.get("enabled", False)]


def check_feature_enabled(feature_id: str, user_id: Optional[str] = None) -> bool:
    """Check if feature is enabled, optionally for a specific user.

    Applies rollout_pct field when present: a float 0.0–1.0 that gates
    access by hashing user_id.

    Args:
        feature_id: Feature identifier.
        user_id: Optional user identifier for percentage rollout.

    Returns:
        True if the feature is enabled (and user falls within rollout).
    """
    feature = _FEATURE_REGISTRY.get(feature_id)
    if feature is None:
        return False
    if not feature.get("enabled", False):
        return False

    rollout_pct: float = feature.get("rollout_pct", 1.0)
    if rollout_pct >= 1.0:
        return True
    if user_id is None:
        return False

    # Stable per-user bucketing via hash
    bucket = (hash(f"{feature_id}:{user_id}") % 1000) / 1000.0
    return bucket < rollout_pct
