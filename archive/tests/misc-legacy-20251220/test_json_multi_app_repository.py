"""
Tests for JsonMultiAppRepository - multi-application data storage.

TDD RED Phase: These tests will fail until implementation is complete.
"""
import pytest
import json
import tempfile
from pathlib import Path
from src.dashboard.domain.entities.dashboard_data import DashboardData
from src.dashboard.domain.entities.application_registry import Application
from src.dashboard.infrastructure.repositories.json_multi_app_repository import JsonMultiAppRepository


class TestJsonMultiAppRepository:
    """Tests for multi-application JSON repository."""
    
    @pytest.fixture
    def temp_dashboard_root(self):
        """Create temporary dashboard root directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def cortex_app(self):
        """Create CORTEX application fixture."""
        return Application(
            id="cortex",
            name="CORTEX",
            display_name="CORTEX Dashboard",
            dashboard_path="dashboards/data/repos/cortex",
            is_active=True
        )
    
    @pytest.fixture
    def external_app(self):
        """Create external application fixture."""
        return Application(
            id="external-repo",
            name="External",
            display_name="External Repository Dashboard",
            dashboard_path="dashboards/external-repo",
            is_active=True
        )
    
    def test_create_repository_with_root_path(self, temp_dashboard_root):
        """RED: Should create repository with specified root path."""
        repo = JsonMultiAppRepository(str(temp_dashboard_root))
        assert repo is not None
    
    def test_initialize_app_directory_structure(self, temp_dashboard_root, cortex_app):
        """RED: Should create app-specific directory structure on initialization."""
        repo = JsonMultiAppRepository(str(temp_dashboard_root))
        repo.initialize_app(cortex_app)
        
        app_dir = temp_dashboard_root / "cortex"
        assert app_dir.exists()
        assert app_dir.is_dir()
        
        metadata_file = app_dir / "metadata.json"
        assert metadata_file.exists()
    
    def test_initialize_app_creates_metadata_file(self, temp_dashboard_root, cortex_app):
        """RED: Should create metadata.json with app information."""
        repo = JsonMultiAppRepository(str(temp_dashboard_root))
        repo.initialize_app(cortex_app)
        
        metadata_file = temp_dashboard_root / "cortex" / "metadata.json"
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        assert metadata["app_id"] == "cortex"
        assert metadata["name"] == "CORTEX"
        assert metadata["display_name"] == "CORTEX Dashboard"
        assert "created_at" in metadata
    
    def test_save_dashboard_data_for_specific_app(self, temp_dashboard_root, cortex_app):
        """RED: Should save dashboard data to app-specific directory."""
        repo = JsonMultiAppRepository(str(temp_dashboard_root))
        repo.initialize_app(cortex_app)
        
        dashboard_data = DashboardData(
            app_id="cortex",
            tabs={"overview": {"metric": "value"}, "architecture": {"diagrams": 5}},
            metadata={"name": "CORTEX", "version": "3.2.0"}
        )
        
        repo.save_for_app(cortex_app.id, dashboard_data)
        
        data_file = temp_dashboard_root / "cortex" / "dashboard_data.json"
        assert data_file.exists()
    
    def test_load_dashboard_data_for_specific_app(self, temp_dashboard_root, cortex_app):
        """RED: Should load dashboard data from app-specific directory."""
        repo = JsonMultiAppRepository(str(temp_dashboard_root))
        repo.initialize_app(cortex_app)
        
        dashboard_data = DashboardData(
            app_id="cortex",
            tabs={"overview": {"metric": "value"}, "architecture": {"diagrams": 5}},
            metadata={"name": "CORTEX", "version": "3.2.0"}
        )
        
        repo.save_for_app(cortex_app.id, dashboard_data)
        loaded_data = repo.load(cortex_app.id)
        
        assert loaded_data.app_id == "cortex"
        assert len(loaded_data.tabs) == 2
        assert loaded_data.tabs["overview"]["metric"] == "value"
    
    def test_data_isolation_between_apps(self, temp_dashboard_root, cortex_app, external_app):
        """RED: Should maintain data isolation between different applications."""
        repo = JsonMultiAppRepository(str(temp_dashboard_root))
        repo.initialize_app(cortex_app)
        repo.initialize_app(external_app)
        
        cortex_data = DashboardData(
            app_id="cortex",
            tabs={"overview": {"metric": "cortex_value"}},
            metadata={"name": "CORTEX"}
        )
        
        external_data = DashboardData(
            app_id="external-repo",
            tabs={"dashboard": {"metric": "external_value"}},
            metadata={"name": "External"}
        )
        
        repo.save_for_app(cortex_app.id, cortex_data)
        repo.save_for_app(external_app.id, external_data)
        
        loaded_cortex = repo.load(cortex_app.id)
        loaded_external = repo.load(external_app.id)
        
        assert loaded_cortex.app_id == "cortex"
        assert loaded_external.app_id == "external-repo"
        assert loaded_cortex.tabs["overview"]["metric"] == "cortex_value"
        assert loaded_external.tabs["dashboard"]["metric"] == "external_value"
    
    def test_load_nonexistent_app_returns_none(self, temp_dashboard_root):
        """RED: Should return None when loading data for nonexistent app."""
        repo = JsonMultiAppRepository(str(temp_dashboard_root))
        result = repo.load("nonexistent-app")
        assert result is None
    
    def test_prevent_path_traversal_attacks(self, temp_dashboard_root):
        """RED: Should reject app IDs with path traversal attempts."""
        repo = JsonMultiAppRepository(str(temp_dashboard_root))
        
        # Application entity validation should catch this in Phase 3.1
        # This test verifies that Application validation works
        with pytest.raises(ValueError, match="Application ID must be alphanumeric"):
            Application(
                id="../malicious",
                name="Malicious",
                display_name="Malicious App",
                dashboard_path="dashboards/malicious",
                is_active=True
            )
    
    def test_list_all_initialized_apps(self, temp_dashboard_root, cortex_app, external_app):
        """RED: Should list all apps that have been initialized."""
        repo = JsonMultiAppRepository(str(temp_dashboard_root))
        repo.initialize_app(cortex_app)
        repo.initialize_app(external_app)
        
        apps = repo.list_apps()
        assert len(apps) == 2
        assert "cortex" in apps
        assert "external-repo" in apps
    
    def test_delete_app_data(self, temp_dashboard_root, cortex_app):
        """RED: Should delete all data for specified app."""
        repo = JsonMultiAppRepository(str(temp_dashboard_root))
        repo.initialize_app(cortex_app)
        
        dashboard_data = DashboardData(
            app_id="cortex",
            tabs={"overview": {"metric": "value"}},
            metadata={"name": "CORTEX"}
        )
        
        repo.save_for_app(cortex_app.id, dashboard_data)
        assert repo.load(cortex_app.id) is not None
        
        repo.delete_app(cortex_app.id)
        assert repo.load(cortex_app.id) is None
        
        app_dir = temp_dashboard_root / "cortex"
        assert not app_dir.exists()
    
    def test_get_app_metadata(self, temp_dashboard_root, cortex_app):
        """RED: Should retrieve app metadata without loading full dashboard."""
        repo = JsonMultiAppRepository(str(temp_dashboard_root))
        repo.initialize_app(cortex_app)
        
        metadata = repo.get_metadata(cortex_app.id)
        assert metadata["app_id"] == "cortex"
        assert metadata["name"] == "CORTEX"
        assert "created_at" in metadata
    
    def test_update_app_metadata(self, temp_dashboard_root, cortex_app):
        """RED: Should update app metadata without affecting dashboard data."""
        repo = JsonMultiAppRepository(str(temp_dashboard_root))
        repo.initialize_app(cortex_app)
        
        new_metadata = {
            "app_id": "cortex",
            "name": "CORTEX",
            "display_name": "CORTEX Dashboard v2",
            "version": "3.2.0",
            "last_updated": "2025-12-04T10:00:00Z"
        }
        
        repo.update_metadata(cortex_app.id, new_metadata)
        
        metadata = repo.get_metadata(cortex_app.id)
        assert metadata["display_name"] == "CORTEX Dashboard v2"
        assert metadata["version"] == "3.2.0"
