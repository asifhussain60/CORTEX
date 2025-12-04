"""
Test Configuration for Presentation Layer

Provides Flask test client fixture for template rendering tests.

Author: Asif Hussain
"""
import pytest
from pathlib import Path


@pytest.fixture
def client(tmp_path):
    """Flask test client with temporary dashboard storage"""
    from src.dashboard.presentation.app import create_app
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    
    # Create repositories
    dashboard_repo = JsonDashboardRepository(base_path=tmp_path / "dashboards")
    
    # Seed default CORTEX dashboard data
    cortex_data = DashboardData(
        app_id="cortex",
        tabs={
            "overview": {"files": 100, "lines": 5000},
            "metrics": {"coverage": 95, "tests": 70},
            "health": {"status": "healthy"}
        },
        metadata={"app_name": "CORTEX"}
    )
    dashboard_repo.save(cortex_data)
    
    # Create Flask app with temp storage paths
    app = create_app(
        dashboard_base_path=tmp_path / "dashboards",
        app_registry_db_path=tmp_path / "apps.db"
    )
    
    # Configure for testing
    app.config['TESTING'] = True
    
    # Return test client
    with app.test_client() as client:
        yield client
