"""
Presentation Layer - Flask Routes Tests (RED Phase)

Tests for Flask dashboard routes with dependency injection.
Uses Flask test client for isolated HTTP testing.

Author: Asif Hussain
"""
import pytest
from datetime import datetime
from pathlib import Path


@pytest.fixture
def app(tmp_path):
    """Create Flask app for testing"""
    from src.dashboard.presentation.app import create_app
    
    # Create test app with temp database
    app = create_app(
        dashboard_base_path=tmp_path / "dashboards",
        app_registry_db_path=tmp_path / "apps.db"
    )
    app.config['TESTING'] = True
    
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


def test_get_dashboard_cortex(client, tmp_path):
    """Test GET / redirects to /dashboard/cortex"""
    # Arrange - Create dashboard data with multi-app repository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    from src.dashboard.infrastructure.repositories.json_multi_app_repository import JsonMultiAppRepository
    from src.dashboard.domain.entities.application_registry import Application
    
    repo = JsonMultiAppRepository(root_path=str(tmp_path / "dashboards"))
    app = Application(
        id="cortex",
        name="CORTEX",
        display_name="CORTEX Dashboard",
        dashboard_path="dashboards/cortex",
        is_active=True
    )
    repo.initialize_app(app)
    
    data = DashboardData(
        app_id="cortex",
        tabs={"overview": {"files": 100}},
        metadata={"app_name": "CORTEX"}
    )
    repo.save(data, app_id="cortex")
    
    # Act
    response = client.get('/', follow_redirects=True)
    
    # Assert
    assert response.status_code == 200
    assert b"CORTEX" in response.data


def test_get_dashboard_by_id(client, tmp_path):
    """Test GET /<app_id> redirects to /dashboard/<app_id> and returns specific dashboard"""
    # Arrange
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    from src.dashboard.infrastructure.repositories.json_multi_app_repository import JsonMultiAppRepository
    from src.dashboard.domain.entities.application_registry import Application
    
    repo = JsonMultiAppRepository(root_path=str(tmp_path / "dashboards"))
    app = Application(
        id="my-app",
        name="MyApp",
        display_name="My App",
        dashboard_path="dashboards/my-app",
        is_active=True
    )
    repo.initialize_app(app)
    
    data = DashboardData(
        app_id="my-app",
        tabs={"overview": {"status": "active"}},
        metadata={"app_name": "My App"}
    )
    repo.save(data, app_id="my-app")
    
    # Act
    response = client.get('/my-app', follow_redirects=True)
    
    # Assert
    assert response.status_code == 200
    assert b"My App" in response.data


def test_get_dashboard_not_found(client):
    """Test GET /<app_id> returns 404 for non-existent dashboard (after redirect)"""
    # Act
    response = client.get('/nonexistent', follow_redirects=True)
    
    # Assert
    assert response.status_code == 404


def test_post_refresh_dashboard(client, tmp_path):
    """Test POST /dashboard/<app_id>/refresh refreshes dashboard"""
    # Arrange - Create initial dashboard
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    from src.dashboard.infrastructure.repositories.json_multi_app_repository import JsonMultiAppRepository
    from src.dashboard.domain.entities.application_registry import Application
    
    repo = JsonMultiAppRepository(root_path=str(tmp_path / "dashboards"))
    app = Application(
        id="cortex",
        name="CORTEX",
        display_name="CORTEX Dashboard",
        dashboard_path="dashboards/cortex",
        is_active=True
    )
    repo.initialize_app(app)
    
    data = DashboardData(
        app_id="cortex",
        tabs={},
        metadata={"last_updated": "2025-12-01T10:00:00"}
    )
    repo.save(data, app_id="cortex")
    
    # Act
    response = client.post('/dashboard/cortex/refresh')
    
    # Assert
    assert response.status_code == 200
    assert b"success" in response.data.lower() or b"refreshed" in response.data.lower()


def test_post_refresh_dashboard_force(client, tmp_path):
    """Test POST /dashboard/<app_id>/refresh?force=true forces refresh"""
    # Arrange
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    from src.dashboard.infrastructure.repositories.json_multi_app_repository import JsonMultiAppRepository
    from src.dashboard.domain.entities.application_registry import Application
    
    repo = JsonMultiAppRepository(root_path=str(tmp_path / "dashboards"))
    app = Application(
        id="cortex",
        name="CORTEX",
        display_name="CORTEX Dashboard",
        dashboard_path="dashboards/cortex",
        is_active=True
    )
    repo.initialize_app(app)
    
    data = DashboardData(
        app_id="cortex",
        tabs={},
        metadata={"last_updated": datetime.now().isoformat()}
    )
    repo.save(data, app_id="cortex")
    
    # Act - Force refresh even though data is fresh
    response = client.post('/dashboard/cortex/refresh?force=true')
    
    # Assert
    assert response.status_code == 200
