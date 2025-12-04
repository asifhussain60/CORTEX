"""
Application Layer DTOs and Use Cases Tests - RED Phase

Tests for request/response DTOs and use cases.
Following TDD: Write failing tests FIRST, then implement.

Author: Asif Hussain
"""
import pytest
from datetime import datetime


# ==================== DTO Tests ====================

def test_load_dashboard_request_dto():
    """Test LoadDashboardRequest DTO creation"""
    from src.dashboard.application.dtos.load_dashboard_dto import LoadDashboardRequest
    
    # Arrange & Act
    request = LoadDashboardRequest(app_id="cortex")
    
    # Assert
    assert request.app_id == "cortex"


def test_load_dashboard_response_dto():
    """Test LoadDashboardResponse DTO creation"""
    from src.dashboard.application.dtos.load_dashboard_dto import LoadDashboardResponse
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange
    data = DashboardData(
        app_id="cortex",
        tabs={"overview": {"files": 100}},
        metadata={"version": "3.3.0"}
    )
    
    # Act
    response = LoadDashboardResponse(
        app_id="cortex",
        app_name="CORTEX",
        data=data
    )
    
    # Assert
    assert response.app_id == "cortex"
    assert response.app_name == "CORTEX"
    assert response.data == data


# ==================== Use Case Tests ====================

def test_load_dashboard_use_case_success():
    """Test LoadDashboardUseCase successfully loads dashboard"""
    from src.dashboard.application.use_cases.load_dashboard import LoadDashboardUseCase
    from src.dashboard.application.dtos.load_dashboard_dto import LoadDashboardRequest
    from src.dashboard.domain.repositories.dashboard_repository import DashboardRepository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange - Fake repository
    class FakeDashboardRepo(DashboardRepository):
        def get_by_id(self, app_id: str) -> DashboardData:
            return DashboardData(
                app_id=app_id,
                tabs={"overview": {"files": 100}},
                metadata={"app_name": "CORTEX", "version": "3.3.0"}
            )
        
        def save(self, data: DashboardData) -> None:
            pass
        
        def exists(self, app_id: str) -> bool:
            return True
    
    # Act
    repo = FakeDashboardRepo()
    use_case = LoadDashboardUseCase(repo)
    request = LoadDashboardRequest(app_id="cortex")
    response = use_case.execute(request)
    
    # Assert
    assert response.app_id == "cortex"
    assert response.app_name == "CORTEX"
    assert response.data.tabs["overview"]["files"] == 100


def test_load_dashboard_use_case_not_found():
    """Test LoadDashboardUseCase raises error for missing dashboard"""
    from src.dashboard.application.use_cases.load_dashboard import LoadDashboardUseCase
    from src.dashboard.application.dtos.load_dashboard_dto import LoadDashboardRequest
    from src.dashboard.domain.repositories.dashboard_repository import DashboardRepository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange - Fake repository that raises error
    class FakeDashboardRepo(DashboardRepository):
        def get_by_id(self, app_id: str) -> DashboardData:
            raise FileNotFoundError(f"Dashboard not found for app_id='{app_id}'")
        
        def save(self, data: DashboardData) -> None:
            pass
        
        def exists(self, app_id: str) -> bool:
            return False
    
    # Act & Assert
    repo = FakeDashboardRepo()
    use_case = LoadDashboardUseCase(repo)
    request = LoadDashboardRequest(app_id="nonexistent")
    
    with pytest.raises(FileNotFoundError, match="Dashboard not found"):
        use_case.execute(request)


def test_load_dashboard_use_case_validates_app_id():
    """Test LoadDashboardRequest DTO validates app_id is not empty"""
    from src.dashboard.application.dtos.load_dashboard_dto import LoadDashboardRequest
    
    # Act & Assert - Validation happens in DTO __post_init__
    with pytest.raises(ValueError, match="app_id cannot be empty"):
        LoadDashboardRequest(app_id="")


def test_refresh_dashboard_request_dto():
    """Test RefreshDashboardRequest DTO creation"""
    from src.dashboard.application.dtos.refresh_dashboard_dto import RefreshDashboardRequest
    
    # Arrange & Act
    request = RefreshDashboardRequest(app_id="cortex", force=True)
    
    # Assert
    assert request.app_id == "cortex"
    assert request.force is True


def test_refresh_dashboard_response_dto():
    """Test RefreshDashboardResponse DTO creation"""
    from src.dashboard.application.dtos.refresh_dashboard_dto import RefreshDashboardResponse
    
    # Arrange & Act
    response = RefreshDashboardResponse(
        app_id="cortex",
        success=True,
        message="Dashboard refreshed successfully",
        refresh_time=datetime.now()
    )
    
    # Assert
    assert response.app_id == "cortex"
    assert response.success is True
    assert "refreshed successfully" in response.message


def test_refresh_dashboard_use_case_success():
    """Test RefreshDashboardUseCase successfully refreshes dashboard"""
    from src.dashboard.application.use_cases.refresh_dashboard import RefreshDashboardUseCase
    from src.dashboard.application.dtos.refresh_dashboard_dto import RefreshDashboardRequest
    from src.dashboard.domain.repositories.dashboard_repository import DashboardRepository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange - Fake repository with save tracking
    saved_data = None
    
    class FakeDashboardRepo(DashboardRepository):
        def get_by_id(self, app_id: str) -> DashboardData:
            return DashboardData(
                app_id=app_id,
                tabs={},
                metadata={}
            )
        
        def save(self, data: DashboardData) -> None:
            nonlocal saved_data
            saved_data = data
        
        def exists(self, app_id: str) -> bool:
            return True
    
    # Act
    repo = FakeDashboardRepo()
    use_case = RefreshDashboardUseCase(repo)
    request = RefreshDashboardRequest(app_id="cortex", force=False)
    response = use_case.execute(request)
    
    # Assert
    assert response.success is True
    assert saved_data is not None
    assert saved_data.app_id == "cortex"


def test_refresh_dashboard_use_case_skips_if_fresh():
    """Test RefreshDashboardUseCase skips refresh if data is fresh and force=False"""
    from src.dashboard.application.use_cases.refresh_dashboard import RefreshDashboardUseCase
    from src.dashboard.application.dtos.refresh_dashboard_dto import RefreshDashboardRequest
    from src.dashboard.domain.repositories.dashboard_repository import DashboardRepository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange - Data is fresh (last updated recently)
    class FakeDashboardRepo(DashboardRepository):
        def get_by_id(self, app_id: str) -> DashboardData:
            return DashboardData(
                app_id=app_id,
                tabs={},
                metadata={"last_updated": datetime.now().isoformat()}
            )
        
        def save(self, data: DashboardData) -> None:
            pass  # Should not be called
        
        def exists(self, app_id: str) -> bool:
            return True
    
    # Act
    repo = FakeDashboardRepo()
    use_case = RefreshDashboardUseCase(repo)
    request = RefreshDashboardRequest(app_id="cortex", force=False)
    response = use_case.execute(request)
    
    # Assert
    assert response.success is True
    assert "skipped" in response.message.lower() or "fresh" in response.message.lower()
