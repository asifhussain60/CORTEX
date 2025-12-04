"""
DashboardData Entity

Represents complete dashboard data for an application.
Pure Python - no framework dependencies (Clean Architecture Domain Layer).

Author: Asif Hussain
"""
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass(frozen=True)
class DashboardData:
    """
    Dashboard data entity (immutable).
    
    This is a domain entity in Clean Architecture - it contains NO framework
    dependencies and represents pure business concepts.
    
    Attributes:
        app_id: Unique application identifier (e.g., "cortex", "noor-canvas")
        tabs: Dictionary mapping tab names to their data
        metadata: Application metadata (name, version, last_scan)
    
    Examples:
        >>> data = DashboardData(
        ...     app_id="cortex",
        ...     tabs={"overview": {"files": 100}},
        ...     metadata={"version": "3.3.0"}
        ... )
        >>> data.app_id
        'cortex'
    """
    app_id: str
    tabs: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def get_tab_names(self) -> List[str]:
        """
        Get list of available tab names.
        
        Returns:
            List of tab names (e.g., ["overview", "architecture"])
        """
        return list(self.tabs.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary.
        
        Returns:
            Dictionary representation of dashboard data
        """
        return {
            "app_id": self.app_id,
            "tabs": self.tabs,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DashboardData':
        """
        Deserialize from dictionary.
        
        Args:
            data: Dictionary with app_id, tabs, metadata keys
        
        Returns:
            DashboardData instance
        """
        return cls(
            app_id=data["app_id"],
            tabs=data["tabs"],
            metadata=data["metadata"]
        )
