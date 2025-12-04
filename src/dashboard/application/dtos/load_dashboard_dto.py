"""
LoadDashboard Use Case DTOs

Request/Response DTOs for loading dashboard data.
DTOs depend only on domain entities (Clean Architecture).

Author: Asif Hussain
"""
from dataclasses import dataclass
from src.dashboard.domain.entities.dashboard_data import DashboardData


@dataclass(frozen=True)
class LoadDashboardRequest:
    """Request to load dashboard for specific app"""
    app_id: str
    
    def __post_init__(self):
        """Validate app_id"""
        if not self.app_id or not self.app_id.strip():
            raise ValueError("app_id cannot be empty")


@dataclass(frozen=True)
class LoadDashboardResponse:
    """Response containing dashboard data"""
    app_id: str
    app_name: str
    data: DashboardData
