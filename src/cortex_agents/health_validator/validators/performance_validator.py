"""Performance metrics health validator."""

from typing import Dict, Any, Optional
from .base_validator import BaseHealthValidator


class PerformanceValidator(BaseHealthValidator):
    """Validator for performance metrics from Tier 3."""
    
    def __init__(self, tier3_context=None, min_velocity: float = 5.0):
        """
        Initialize performance validator.
        
        Args:
            tier3_context: Tier 3 Context Intelligence instance
            min_velocity: Minimum acceptable velocity metric
        """
        self.tier3 = tier3_context
        self.min_velocity = min_velocity
    
    def get_risk_level(self) -> str:
        """Performance issues are low-medium risk."""
        return "medium"
    
    def check(self) -> Dict[str, Any]:
        """Check performance metrics from Tier 3."""
        if not self.tier3:
            return {
                "status": "skip",
                "message": "Tier 3 not available",
                "details": [],
                "errors": [],
                "warnings": []
            }
        
        try:
            # Get performance metrics from Tier 3
            summary = self.tier3.get_context_summary()
            
            result = {
                "status": "pass",
                "metrics": {},
                "details": [],
                "errors": [],
                "warnings": []
            }
            
            if "average_velocity" in summary:
                velocity = summary["average_velocity"]
                result["metrics"]["velocity"] = velocity
                
                if velocity is not None and velocity < self.min_velocity:
                    result["status"] = "warn"
                    result["warnings"].append(f"Low velocity: {velocity}")
            
            return result
            
        except Exception as e:
            return {
                "status": "fail",
                "details": [],
                "errors": [f"Performance check failed: {str(e)}"],
                "warnings": []
            }
