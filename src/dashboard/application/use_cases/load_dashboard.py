"""
LoadDashboard Use Case

Business logic for loading dashboard data.
Depends only on domain layer (repositories + entities).

Author: Asif Hussain
"""
from src.dashboard.domain.repositories.dashboard_repository import DashboardRepository
from src.dashboard.application.dtos.load_dashboard_dto import (
    LoadDashboardRequest,
    LoadDashboardResponse
)


class LoadDashboardUseCase:
    """Use case for loading dashboard data by app_id"""
    
    def __init__(self, dashboard_repo: DashboardRepository):
        """
        Initialize with dashboard repository.
        
        Args:
            dashboard_repo: Repository for dashboard persistence
        """
        self._dashboard_repo = dashboard_repo
    
    def execute(self, request: LoadDashboardRequest) -> LoadDashboardResponse:
        """
        Execute use case to load dashboard.
        
        Args:
            request: LoadDashboardRequest with app_id (validated by DTO)
            
        Returns:
            LoadDashboardResponse with dashboard data
            
        Raises:
            FileNotFoundError: If dashboard doesn't exist
        """
        # Load dashboard from repository
        data = self._dashboard_repo.get_by_id(request.app_id)
        
        # Extract app_name from metadata with fallback
        app_name = data.metadata.get("app_name", request.app_id.upper())
        
        return LoadDashboardResponse(
            app_id=request.app_id,
            app_name=app_name,
            data=data
        )
