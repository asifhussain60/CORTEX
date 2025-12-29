"""
RefreshDashboard Use Case

Business logic for refreshing dashboard data.
Depends only on domain layer (repositories + entities).

Author: Asif Hussain
"""
from datetime import datetime, timedelta
from src.dashboard.domain.repositories.dashboard_repository import DashboardRepository
from src.dashboard.application.dtos.refresh_dashboard_dto import (
    RefreshDashboardRequest,
    RefreshDashboardResponse
)


class RefreshDashboardUseCase:
    """Use case for refreshing dashboard data"""
    
    FRESHNESS_THRESHOLD_HOURS = 1  # Data is fresh if updated within 1 hour
    
    def __init__(self, dashboard_repo: DashboardRepository):
        """
        Initialize with dashboard repository.
        
        Args:
            dashboard_repo: Repository for dashboard persistence
        """
        self._dashboard_repo = dashboard_repo
    
    def execute(self, request: RefreshDashboardRequest) -> RefreshDashboardResponse:
        """
        Execute use case to refresh dashboard.
        
        Args:
            request: RefreshDashboardRequest with app_id (validated by DTO) and force flag
            
        Returns:
            RefreshDashboardResponse with refresh result
        """
        current_data = self._dashboard_repo.get_by_id(request.app_id)
        now = datetime.now()
        
        # Skip refresh if data is fresh and not forced
        if not request.force and self._is_fresh(current_data):
            return self._skip_response(request.app_id, now)
        
        # Update dashboard with new timestamp (Phase 1.6 will add repo scanning)
        refreshed_data = self._create_refreshed_data(current_data, now)
        self._dashboard_repo.save(refreshed_data, app_id=request.app_id)
        
        return RefreshDashboardResponse(
            app_id=request.app_id,
            success=True,
            message="Dashboard refreshed successfully",
            refresh_time=now
        )
    
    def _skip_response(self, app_id: str, refresh_time: datetime) -> RefreshDashboardResponse:
        """Create response for skipped refresh"""
        return RefreshDashboardResponse(
            app_id=app_id,
            success=True,
            message="Dashboard is fresh, refresh skipped",
            refresh_time=refresh_time
        )
    
    def _create_refreshed_data(self, current_data, refresh_time: datetime):
        """Create refreshed dashboard data with updated timestamp"""
        refreshed_metadata = {
            **current_data.metadata,
            "last_updated": refresh_time.isoformat()
        }
        
        return type(current_data)(
            app_id=current_data.app_id,
            tabs=current_data.tabs,
            metadata=refreshed_metadata
        )
    
    def _is_fresh(self, data) -> bool:
        """Check if dashboard data is fresh"""
        last_updated_str = data.metadata.get("last_updated")
        if not last_updated_str:
            return False
        
        try:
            last_updated = datetime.fromisoformat(last_updated_str)
            threshold = datetime.now() - timedelta(hours=self.FRESHNESS_THRESHOLD_HOURS)
            return last_updated > threshold
        except (ValueError, TypeError):
            return False
