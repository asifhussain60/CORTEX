"""
TabContent Entity

Represents content for a single dashboard tab.
Pure Python - no framework dependencies (Clean Architecture Domain Layer).

Author: Asif Hussain
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Any, Literal


# Valid tab names (7 tabs in unified dashboard)
VALID_TAB_NAMES = ("overview", "techstack", "architecture", "health", "metrics", "security", "reports")


@dataclass(frozen=True)
class TabContent:
    """
    Tab content entity (immutable).
    
    This is a domain entity in Clean Architecture - it contains NO framework
    dependencies and represents pure business concepts.
    
    Attributes:
        tab_name: Name of the tab (must be one of 7 valid tabs)
        data: Tab-specific data dictionary
        last_updated: Timestamp of last update
    
    Examples:
        >>> tab = TabContent(
        ...     tab_name="overview",
        ...     data={"files": 100, "health": 95.5},
        ...     last_updated=datetime.now()
        ... )
        >>> tab.is_stale(hours=1)
        False
    """
    tab_name: Literal["overview", "techstack", "architecture", "health", "metrics", "security", "reports"]
    data: Dict[str, Any]
    last_updated: datetime
    
    def is_stale(self, hours: int = 24) -> bool:
        """
        Check if tab content is stale (needs refresh).
        
        Args:
            hours: Number of hours after which content is considered stale
        
        Returns:
            True if last_updated is older than specified hours
        """
        threshold = datetime.now() - timedelta(hours=hours)
        return self.last_updated < threshold
    
    def __post_init__(self):
        """Validate tab_name after initialization"""
        if self.tab_name not in VALID_TAB_NAMES:
            raise ValueError(
                f"tab_name must be one of {VALID_TAB_NAMES}, got '{self.tab_name}'"
            )
