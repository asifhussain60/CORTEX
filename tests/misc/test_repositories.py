"""
Repository Interface Tests - RED Phase

Tests for DashboardRepository and ApplicationRepository abstract interfaces.
Following TDD: Write failing tests FIRST, then implement.

Author: Asif Hussain
"""
import pytest
from datetime import datetime
from typing import List, Optional


def test_dashboard_repository_interface_exists():
    """Test DashboardRepository abstract interface can be imported"""
    from src.dashboard.domain.repositories.dashboard_repository import DashboardRepository
    
    assert DashboardRepository is not None


def test_dashboard_repository_get_by_id():
    """Test DashboardRepository.get_by_id() method with fake implementation"""
    from src.dashboard.domain.repositories.dashboard_repository import DashboardRepository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange - Create fake implementation
    class FakeDashboardRepository(DashboardRepository):
        def get_by_id(self, app_id: str) -> DashboardData:
            return DashboardData(
                app_id=app_id,
                tabs={"overview": {"files": 100}},
                metadata={"version": "3.3.0"}
            )
        
        def save(self, data: DashboardData) -> None:
            pass
        
        def exists(self, app_id: str) -> bool:
            return True
    
    # Act
    repo = FakeDashboardRepository()
    data = repo.get_by_id("cortex")
    
    # Assert
    assert data.app_id == "cortex"
    assert data.tabs["overview"]["files"] == 100


def test_dashboard_repository_get_by_id_not_found():
    """Test DashboardRepository.get_by_id() raises error for missing app"""
    from src.dashboard.domain.repositories.dashboard_repository import DashboardRepository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange
    class FakeDashboardRepository(DashboardRepository):
        def get_by_id(self, app_id: str) -> DashboardData:
            raise FileNotFoundError(f"Dashboard not found for app_id='{app_id}'")
        
        def save(self, data: DashboardData) -> None:
            pass
        
        def exists(self, app_id: str) -> bool:
            return False
    
    # Act & Assert
    repo = FakeDashboardRepository()
    with pytest.raises(FileNotFoundError, match="Dashboard not found"):
        repo.get_by_id("nonexistent")


def test_dashboard_repository_save():
    """Test DashboardRepository.save() method"""
    from src.dashboard.domain.repositories.dashboard_repository import DashboardRepository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange
    saved_data = None
    
    class FakeDashboardRepository(DashboardRepository):
        def get_by_id(self, app_id: str) -> DashboardData:
            return saved_data
        
        def save(self, data: DashboardData) -> None:
            nonlocal saved_data
            saved_data = data
        
        def exists(self, app_id: str) -> bool:
            return saved_data is not None
    
    # Act
    repo = FakeDashboardRepository()
    data = DashboardData(
        app_id="test",
        tabs={},
        metadata={}
    )
    repo.save(data)
    
    # Assert
    assert saved_data == data
    assert repo.exists("test")


def test_dashboard_repository_exists():
    """Test DashboardRepository.exists() method"""
    from src.dashboard.domain.repositories.dashboard_repository import DashboardRepository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    
    # Arrange
    class FakeDashboardRepository(DashboardRepository):
        def __init__(self):
            self.stored_ids = ["cortex", "noor-canvas"]
        
        def get_by_id(self, app_id: str) -> DashboardData:
            pass
        
        def save(self, data: DashboardData) -> None:
            pass
        
        def exists(self, app_id: str) -> bool:
            return app_id in self.stored_ids
    
    # Act
    repo = FakeDashboardRepository()
    
    # Assert
    assert repo.exists("cortex") is True
    assert repo.exists("nonexistent") is False


def test_application_repository_interface_exists():
    """Test ApplicationRepository abstract interface can be imported"""
    from src.dashboard.domain.repositories.application_repository import ApplicationRepository
    
    assert ApplicationRepository is not None


def test_application_repository_get_all():
    """Test ApplicationRepository.get_all() returns list of applications"""
    from src.dashboard.domain.repositories.application_repository import ApplicationRepository
    from src.dashboard.domain.entities.application import Application
    
    # Arrange
    class FakeApplicationRepository(ApplicationRepository):
        def get_all(self) -> List[Application]:
            return [
                Application(
                    app_id="cortex",
                    app_name="CORTEX",
                    app_type="internal",
                    data_path="/cortex-brain/dashboards/data/repos/cortex",
                    last_scan=datetime.now()
                ),
                Application(
                    app_id="noor-canvas",
                    app_name="Noor-Canvas",
                    app_type="external",
                    data_path="/cortex-brain/dashboards/data/repos/noor-canvas",
                    last_scan=datetime.now()
                )
            ]
        
        def get_by_id(self, app_id: str) -> Optional[Application]:
            pass
        
        def register(self, app: Application) -> None:
            pass
        
        def exists(self, app_id: str) -> bool:
            return app_id in ("cortex", "noor-canvas")
    
    # Act
    repo = FakeApplicationRepository()
    apps = repo.get_all()
    
    # Assert
    assert len(apps) == 2
    assert apps[0].app_id == "cortex"
    assert apps[1].app_id == "noor-canvas"


def test_application_repository_get_by_id():
    """Test ApplicationRepository.get_by_id() returns specific application"""
    from src.dashboard.domain.repositories.application_repository import ApplicationRepository
    from src.dashboard.domain.entities.application import Application
    
    # Arrange
    class FakeApplicationRepository(ApplicationRepository):
        def get_all(self) -> List[Application]:
            pass
        
        def get_by_id(self, app_id: str) -> Optional[Application]:
            if app_id == "cortex":
                return Application(
                    app_id="cortex",
                    app_name="CORTEX",
                    app_type="internal",
                    data_path="/cortex-brain/dashboards/data/repos/cortex",
                    last_scan=datetime.now()
                )
            return None
        
        def register(self, app: Application) -> None:
            pass
        
        def exists(self, app_id: str) -> bool:
            return app_id == "cortex"
    
    # Act
    repo = FakeApplicationRepository()
    app = repo.get_by_id("cortex")
    not_found = repo.get_by_id("nonexistent")
    
    # Assert
    assert app is not None
    assert app.app_id == "cortex"
    assert not_found is None


def test_application_repository_register():
    """Test ApplicationRepository.register() adds new application"""
    from src.dashboard.domain.repositories.application_repository import ApplicationRepository
    from src.dashboard.domain.entities.application import Application
    
    # Arrange
    registered_apps = []
    
    class FakeApplicationRepository(ApplicationRepository):
        def get_all(self) -> List[Application]:
            return registered_apps
        
        def get_by_id(self, app_id: str) -> Optional[Application]:
            return next((a for a in registered_apps if a.app_id == app_id), None)
        
        def register(self, app: Application) -> None:
            registered_apps.append(app)
        
        def exists(self, app_id: str) -> bool:
            return any(a.app_id == app_id for a in registered_apps)
    
    # Act
    repo = FakeApplicationRepository()
    app = Application(
        app_id="test",
        app_name="Test App",
        app_type="user",
        data_path="/test",
        last_scan=datetime.now()
    )
    repo.register(app)
    
    # Assert
    assert len(repo.get_all()) == 1
    assert repo.exists("test")
    assert repo.get_by_id("test") == app


def test_application_repository_exists():
    """Test ApplicationRepository.exists() checks app registration"""
    from src.dashboard.domain.repositories.application_repository import ApplicationRepository
    from src.dashboard.domain.entities.application import Application
    
    # Arrange
    class FakeApplicationRepository(ApplicationRepository):
        def __init__(self):
            self.registered_ids = ["cortex", "noor-canvas"]
        
        def get_all(self) -> List[Application]:
            pass
        
        def get_by_id(self, app_id: str) -> Optional[Application]:
            pass
        
        def register(self, app: Application) -> None:
            pass
        
        def exists(self, app_id: str) -> bool:
            return app_id in self.registered_ids
    
    # Act
    repo = FakeApplicationRepository()
    
    # Assert
    assert repo.exists("cortex") is True
    assert repo.exists("unknown") is False
