"""
Tests for enhanced URL routing with multi-app support.

TDD RED Phase: These tests will fail until implementation is complete.
"""
import pytest
from flask import Flask
from pathlib import Path
import tempfile

from src.dashboard.presentation.app import create_app
from src.dashboard.domain.entities.dashboard_data import DashboardData
from src.dashboard.domain.entities.application_registry import Application
from src.dashboard.infrastructure.repositories.json_multi_app_repository import JsonMultiAppRepository


class TestMultiAppRouting:
    """Tests for multi-application URL routing."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dashboard_dir = Path(tmpdir) / "dashboards"
            dashboard_dir.mkdir()
            db_path = Path(tmpdir) / "test.db"
            yield dashboard_dir, db_path
    
    @pytest.fixture
    def multi_app_repo(self, temp_dirs):
        """Create multi-app repository with test data."""
        dashboard_dir, _ = temp_dirs
        repo = JsonMultiAppRepository(str(dashboard_dir))
        
        # Initialize CORTEX app
        cortex_app = Application(
            id="cortex",
            name="CORTEX",
            display_name="CORTEX Dashboard",
            dashboard_path="dashboards/cortex",
            is_active=True
        )
        repo.initialize_app(cortex_app)
        
        cortex_data = DashboardData(
            app_id="cortex",
            tabs={"overview": {"files": 100, "tests": 50}},
            metadata={"name": "CORTEX", "version": "3.2.0"}
        )
        repo.save_for_app("cortex", cortex_data)
        
        # Initialize external app
        external_app = Application(
            id="external-repo",
            name="External",
            display_name="External Repository",
            dashboard_path="dashboards/external-repo",
            is_active=True
        )
        repo.initialize_app(external_app)
        
        external_data = DashboardData(
            app_id="external-repo",
            tabs={"dashboard": {"components": 25}},
            metadata={"name": "External", "version": "1.0.0"}
        )
        repo.save_for_app("external-repo", external_data)
        
        return repo
    
    def test_dashboard_index_route(self, temp_dirs, multi_app_repo):
        """RED: Root / should redirect to /dashboard/cortex."""
        dashboard_dir, db_path = temp_dirs
        app = create_app(dashboard_dir, db_path)
        client = app.test_client()
        
        response = client.get('/')
        assert response.status_code == 302  # Redirect
        assert '/dashboard/cortex' in response.location
    
    def test_dashboard_cortex_route(self, temp_dirs, multi_app_repo):
        """RED: /dashboard/cortex should display CORTEX dashboard."""
        dashboard_dir, db_path = temp_dirs
        app = create_app(dashboard_dir, db_path)
        client = app.test_client()
        
        response = client.get('/dashboard/cortex')
        assert response.status_code == 200
        assert b'CORTEX' in response.data
        assert b'overview' in response.data
    
    def test_dashboard_with_app_id_route(self, temp_dirs, multi_app_repo):
        """RED: /dashboard/<app_id> should display app-specific dashboard."""
        dashboard_dir, db_path = temp_dirs
        app = create_app(dashboard_dir, db_path)
        client = app.test_client()
        
        response = client.get('/dashboard/external-repo')
        assert response.status_code == 200
        assert b'external-repo' in response.data.lower()
        assert b'dashboard' in response.data.lower()
    
    def test_dashboard_with_invalid_app_id(self, temp_dirs, multi_app_repo):
        """RED: /dashboard/<invalid_id> should return 404."""
        dashboard_dir, db_path = temp_dirs
        app = create_app(dashboard_dir, db_path)
        client = app.test_client()
        
        response = client.get('/dashboard/nonexistent')
        assert response.status_code == 404
    
    def test_dashboard_with_path_traversal_attempt(self, temp_dirs, multi_app_repo):
        """RED: /dashboard/../malicious should be rejected."""
        dashboard_dir, db_path = temp_dirs
        app = create_app(dashboard_dir, db_path)
        client = app.test_client()
        
        response = client.get('/dashboard/../malicious')
        assert response.status_code in [400, 404]  # Bad request or not found
    
    def test_dashboard_refresh_route(self, temp_dirs, multi_app_repo):
        """RED: /dashboard/<app_id>/refresh should refresh dashboard data."""
        dashboard_dir, db_path = temp_dirs
        app = create_app(dashboard_dir, db_path)
        client = app.test_client()
        
        response = client.post('/dashboard/cortex/refresh')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['app_id'] == 'cortex'
    
    def test_dashboard_refresh_with_force_parameter(self, temp_dirs, multi_app_repo):
        """RED: /dashboard/<app_id>/refresh?force=true should force refresh."""
        dashboard_dir, db_path = temp_dirs
        app = create_app(dashboard_dir, db_path)
        client = app.test_client()
        
        response = client.post('/dashboard/cortex/refresh?force=true')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['force'] is True
    
    def test_backward_compatibility_with_old_routes(self, temp_dirs, multi_app_repo):
        """RED: Old /<app_id> routes should redirect to /dashboard/<app_id>."""
        dashboard_dir, db_path = temp_dirs
        app = create_app(dashboard_dir, db_path)
        client = app.test_client()
        
        response = client.get('/cortex')
        assert response.status_code == 302  # Redirect
        assert '/dashboard/cortex' in response.location
    
    def test_app_id_validation_rejects_special_characters(self, temp_dirs, multi_app_repo):
        """RED: App ID with special characters should be rejected."""
        dashboard_dir, db_path = temp_dirs
        app = create_app(dashboard_dir, db_path)
        client = app.test_client()
        
        # Test various invalid characters
        invalid_ids = ['app@123', 'app/test', 'app\\test', 'app;test', 'app|test']
        for invalid_id in invalid_ids:
            response = client.get(f'/dashboard/{invalid_id}')
            assert response.status_code in [400, 404], f"Failed for: {invalid_id}"
    
    def test_app_id_allows_alphanumeric_and_hyphens(self, temp_dirs, multi_app_repo):
        """RED: App ID with alphanumeric and hyphens should be allowed."""
        dashboard_dir, db_path = temp_dirs
        app = create_app(dashboard_dir, db_path)
        client = app.test_client()
        
        # Valid IDs (will 404 if not initialized, but should not be rejected)
        valid_ids = ['app123', 'my-app', 'app-123-test']
        for valid_id in valid_ids:
            response = client.get(f'/dashboard/{valid_id}')
            # Should be 404 (not found) not 400 (bad request)
            assert response.status_code == 404, f"Failed for: {valid_id}"
