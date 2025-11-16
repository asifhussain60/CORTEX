"""Velocity metrics tracker from Tier 3."""

from typing import Dict, Any, Optional
import logging
from ..utils import safe_get


class VelocityTracker:
    """Tracks development velocity metrics from Tier 3."""
    
    def __init__(self, tier3_context=None):
        """Initialize with Tier 3 context intelligence."""
        self.tier3 = tier3_context
        self.logger = logging.getLogger(__name__)
    
    def get_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Get velocity/capacity metrics from Tier 3.
        
        Returns:
            Velocity metrics dictionary or None if unavailable
        """
        if not self.tier3:
            return None
        
        try:
            # Get context summary with velocity data
            summary = self.tier3.get_context_summary()
            
            velocity_data = {
                "average_velocity": safe_get(summary, "average_velocity", default=15.0),
                "recent_commits": safe_get(summary, "total_commits", default=0),
                "active_developers": 1  # Default assumption
            }
            
            return velocity_data
        except Exception as e:
            self.logger.warning(f"Tier 3 velocity query failed: {str(e)}")
            return None
