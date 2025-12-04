"""
Application Entity

Represents an application registered in the dashboard system.
Pure Python - no framework dependencies (Clean Architecture Domain Layer).

Author: Asif Hussain
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal


@dataclass(frozen=True)
class Application:
    """
    Application entity (immutable).
    
    This is a domain entity in Clean Architecture - it contains NO framework
    dependencies and represents pure business concepts.
    
    Attributes:
        app_id: Unique application identifier
        app_name: Display name for application
        app_type: Type of application (internal/external/user)
        data_path: Path to dashboard data directory
        last_scan: Timestamp of last scan/refresh
    
    Examples:
        >>> app = Application(
        ...     app_id="cortex",
        ...     app_name="CORTEX",
        ...     app_type="internal",
        ...     data_path="/cortex-brain/dashboards/cortex",
        ...     last_scan=datetime.now()
        ... )
        >>> app.is_stale(hours=24)
        False
    """
    app_id: str
    app_name: str
    app_type: Literal["internal", "external", "user"]
    data_path: str
    last_scan: datetime
    
    def is_stale(self, hours: int = 24) -> bool:
        """
        Check if application data is stale (needs refresh).
        
        Args:
            hours: Number of hours after which data is considered stale
        
        Returns:
            True if last_scan is older than specified hours
        """
        threshold = datetime.now() - timedelta(hours=hours)
        return self.last_scan < threshold
    
    def __post_init__(self):
        """Validate app_type after initialization"""
        valid_types = ("internal", "external", "user")
        if self.app_type not in valid_types:
            raise ValueError(
                f"app_type must be one of {valid_types}, got '{self.app_type}'"
            )
