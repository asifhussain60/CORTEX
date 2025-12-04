"""
Tests for Application entity and ApplicationRegistry.

TDD RED Phase: These tests will fail until implementation is complete.
"""
import pytest
from datetime import datetime
from src.dashboard.domain.entities.application_registry import Application, ApplicationRegistry


class TestApplication:
    """Tests for Application domain entity."""
    
    def test_create_application_with_required_fields(self):
        """RED: Application should be created with required fields."""
        app = Application(
            id="cortex",
            name="CORTEX",
            display_name="CORTEX Dashboard",
            dashboard_path="cortex-brain/dashboards/cortex",
            is_active=True
        )
        
        assert app.id == "cortex"
        assert app.name == "CORTEX"
        assert app.display_name == "CORTEX Dashboard"
        assert app.dashboard_path == "cortex-brain/dashboards/cortex"
        assert app.is_active is True
    
    def test_application_id_must_be_alphanumeric_with_hyphens(self):
        """RED: Application ID should only allow alphanumeric and hyphens."""
        with pytest.raises(ValueError, match="Application ID must be alphanumeric"):
            Application(
                id="cortex@2023",  # Invalid: contains @
                name="CORTEX",
                display_name="CORTEX Dashboard",
                dashboard_path="cortex-brain/dashboards/cortex",
                is_active=True
            )
    
    def test_application_id_cannot_be_empty(self):
        """RED: Application ID cannot be empty."""
        with pytest.raises(ValueError, match="Application ID cannot be empty"):
            Application(
                id="",
                name="CORTEX",
                display_name="CORTEX Dashboard",
                dashboard_path="cortex-brain/dashboards/cortex",
                is_active=True
            )
    
    def test_application_name_cannot_be_empty(self):
        """RED: Application name cannot be empty."""
        with pytest.raises(ValueError, match="Application name cannot be empty"):
            Application(
                id="cortex",
                name="",
                display_name="CORTEX Dashboard",
                dashboard_path="cortex-brain/dashboards/cortex",
                is_active=True
            )
    
    def test_application_is_immutable(self):
        """RED: Application should be immutable (frozen dataclass)."""
        app = Application(
            id="cortex",
            name="CORTEX",
            display_name="CORTEX Dashboard",
            dashboard_path="cortex-brain/dashboards/cortex",
            is_active=True
        )
        
        with pytest.raises(AttributeError):
            app.name = "Modified"
    
    def test_application_with_optional_metadata(self):
        """RED: Application should support optional metadata field."""
        metadata = {
            "version": "3.2.0",
            "repo_url": "github.com/asifhussain60/CORTEX",
            "last_scan": "2025-12-04T10:00:00Z"
        }
        
        app = Application(
            id="cortex",
            name="CORTEX",
            display_name="CORTEX Dashboard",
            dashboard_path="cortex-brain/dashboards/cortex",
            is_active=True,
            metadata=metadata
        )
        
        assert app.metadata == metadata
        assert app.metadata["version"] == "3.2.0"
    
    def test_application_equality(self):
        """RED: Two applications with same ID should be equal."""
        app1 = Application(
            id="cortex",
            name="CORTEX",
            display_name="CORTEX Dashboard",
            dashboard_path="cortex-brain/dashboards/cortex",
            is_active=True
        )
        
        app2 = Application(
            id="cortex",
            name="CORTEX",
            display_name="CORTEX Dashboard",
            dashboard_path="cortex-brain/dashboards/cortex",
            is_active=True
        )
        
        assert app1 == app2
    
    def test_application_hash(self):
        """RED: Application should be hashable for use in sets/dicts."""
        app = Application(
            id="cortex",
            name="CORTEX",
            display_name="CORTEX Dashboard",
            dashboard_path="cortex-brain/dashboards/cortex",
            is_active=True
        )
        
        # Should be usable as dict key
        app_dict = {app: "data"}
        assert app_dict[app] == "data"


class TestApplicationRegistry:
    """Tests for ApplicationRegistry domain service."""
    
    def test_create_empty_registry(self):
        """RED: Should create empty application registry."""
        registry = ApplicationRegistry()
        assert len(registry.get_all()) == 0
    
    def test_register_single_application(self):
        """RED: Should register a new application."""
        registry = ApplicationRegistry()
        
        app = Application(
            id="cortex",
            name="CORTEX",
            display_name="CORTEX Dashboard",
            dashboard_path="cortex-brain/dashboards/cortex",
            is_active=True
        )
        
        registry.register(app)
        assert len(registry.get_all()) == 1
        assert registry.get("cortex") == app
    
    def test_register_duplicate_application_raises_error(self):
        """RED: Should raise error when registering duplicate app ID."""
        registry = ApplicationRegistry()
        
        app1 = Application(
            id="cortex",
            name="CORTEX",
            display_name="CORTEX Dashboard",
            dashboard_path="cortex-brain/dashboards/cortex",
            is_active=True
        )
        
        app2 = Application(
            id="cortex",
            name="CORTEX Modified",
            display_name="CORTEX Dashboard Modified",
            dashboard_path="cortex-brain/dashboards/cortex",
            is_active=True
        )
        
        registry.register(app1)
        
        with pytest.raises(ValueError, match="Application .* already registered"):
            registry.register(app2)
    
    def test_get_nonexistent_application_returns_none(self):
        """RED: Should return None for nonexistent application."""
        registry = ApplicationRegistry()
        assert registry.get("nonexistent") is None
    
    def test_unregister_application(self):
        """RED: Should unregister an application."""
        registry = ApplicationRegistry()
        
        app = Application(
            id="cortex",
            name="CORTEX",
            display_name="CORTEX Dashboard",
            dashboard_path="cortex-brain/dashboards/cortex",
            is_active=True
        )
        
        registry.register(app)
        assert len(registry.get_all()) == 1
        
        registry.unregister("cortex")
        assert len(registry.get_all()) == 0
        assert registry.get("cortex") is None
    
    def test_get_active_applications_only(self):
        """RED: Should filter only active applications."""
        registry = ApplicationRegistry()
        
        app1 = Application(
            id="cortex",
            name="CORTEX",
            display_name="CORTEX Dashboard",
            dashboard_path="cortex-brain/dashboards/cortex",
            is_active=True
        )
        
        app2 = Application(
            id="external",
            name="External",
            display_name="External Dashboard",
            dashboard_path="cortex-brain/dashboards/external",
            is_active=False
        )
        
        registry.register(app1)
        registry.register(app2)
        
        active_apps = registry.get_active()
        assert len(active_apps) == 1
        assert active_apps[0].id == "cortex"
    
    def test_update_application(self):
        """RED: Should update existing application."""
        registry = ApplicationRegistry()
        
        app = Application(
            id="cortex",
            name="CORTEX",
            display_name="CORTEX Dashboard",
            dashboard_path="cortex-brain/dashboards/cortex",
            is_active=True
        )
        
        registry.register(app)
        
        updated_app = Application(
            id="cortex",
            name="CORTEX Updated",
            display_name="CORTEX Dashboard v2",
            dashboard_path="cortex-brain/dashboards/cortex",
            is_active=True
        )
        
        registry.update(updated_app)
        
        retrieved = registry.get("cortex")
        assert retrieved.name == "CORTEX Updated"
        assert retrieved.display_name == "CORTEX Dashboard v2"
    
    def test_list_all_applications_sorted_by_name(self):
        """RED: Should list all applications sorted by name."""
        registry = ApplicationRegistry()
        
        app1 = Application(
            id="zebra",
            name="Zebra App",
            display_name="Zebra Dashboard",
            dashboard_path="cortex-brain/dashboards/zebra",
            is_active=True
        )
        
        app2 = Application(
            id="alpha",
            name="Alpha App",
            display_name="Alpha Dashboard",
            dashboard_path="cortex-brain/dashboards/alpha",
            is_active=True
        )
        
        registry.register(app1)
        registry.register(app2)
        
        all_apps = registry.get_all()
        assert len(all_apps) == 2
        assert all_apps[0].name == "Alpha App"
        assert all_apps[1].name == "Zebra App"
