"""Base health validator interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseHealthValidator(ABC):
    """Abstract base class for health validators."""
    
    @abstractmethod
    def check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Check result dict with keys:
            - status: str ("pass", "warn", "fail", "skip")
            - details: List[Dict] (check details)
            - errors: List[str] (error messages if any)
            - warnings: List[str] (warning messages if any)
        """
        pass
    
    @abstractmethod
    def get_risk_level(self) -> str:
        """
        Get risk level for this validator.
        
        Returns:
            Risk level: "critical", "high", "medium", "low"
        """
        pass
