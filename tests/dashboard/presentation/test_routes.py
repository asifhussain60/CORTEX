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
    """Test GET / returns CORTEX dashboard"""
    # Arrange - Create dashboard data
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    
    repo = JsonDashboardRepository(base_path=tmp_path / "dashboards")
    data = DashboardData(
        app_id="cortex",
        tabs={"overview": {"files": 100}},
        metadata={"app_name": "CORTEX"}
    )
    repo.save(data)
    
    # Act
    response = client.get('/')
    
    # Assert
    assert response.status_code == 200
    assert b"CORTEX" in response.data


def test_get_dashboard_by_id(client, tmp_path):
    """Test GET /<app_id> returns specific dashboard"""
    # Arrange
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    
    repo = JsonDashboardRepository(base_path=tmp_path / "dashboards")
    data = DashboardData(
        app_id="my-app",
        tabs={"overview": {"status": "active"}},
        metadata={"app_name": "My App"}
    )
    repo.save(data)
    
    # Act
    response = client.get('/my-app')
    
    # Assert
    assert response.status_code == 200
    assert b"My App" in response.data


def test_get_dashboard_not_found(client):
    """Test GET /<app_id> returns 404 for non-existent dashboard"""
    # Act
    response = client.get('/nonexistent')
    
    # Assert
    assert response.status_code == 404


def test_post_refresh_dashboard(client, tmp_path):
    """Test POST /refresh/<app_id> refreshes dashboard"""
    # Arrange - Create initial dashboard
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    
    repo = JsonDashboardRepository(base_path=tmp_path / "dashboards")
    data = DashboardData(
        app_id="cortex",
        tabs={},
        metadata={"last_updated": "2025-12-01T10:00:00"}
    )
    repo.save(data)
    
    # Act
    response = client.post('/refresh/cortex')
    
    # Assert
    assert response.status_code == 200
    assert b"success" in response.data.lower() or b"refreshed" in response.data.lower()


def test_post_refresh_dashboard_force(client, tmp_path):
    """Test POST /refresh/<app_id>?force=true forces refresh"""
    # Arrange
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    
    repo = JsonDashboardRepository(base_path=tmp_path / "dashboards")
    data = DashboardData(
        app_id="cortex",
        tabs={},
        metadata={"last_updated": datetime.now().isoformat()}
    )
    repo.save(data)
    
    # Act - Force refresh even though data is fresh
    response = client.post('/refresh/cortex?force=true')
    
    # Assert
    assert response.status_code == 200
