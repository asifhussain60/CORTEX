"""
RefreshDashboard Use Case DTOs

Request/Response DTOs for refreshing dashboard data.
DTOs depend only on Python standard library (Clean Architecture).

Author: Asif Hussain
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class RefreshDashboardRequest:
    """Request to refresh dashboard data"""
    app_id: str
    force: bool = False  # Force refresh even if data is fresh
    
    def __post_init__(self):
        """Validate app_id"""
        if not self.app_id or not self.app_id.strip():
            raise ValueError("app_id cannot be empty")


@dataclass(frozen=True)
class RefreshDashboardResponse:
    """Response containing refresh result"""
    app_id: str
    success: bool
    message: str
    refresh_time: datetime
