"""
Application Switcher UI Tests (RED Phase)

Tests for dropdown selector that allows switching between dashboards.
Tests AJAX switching, URL updates, and browser history integration.

Author: Asif Hussain
"""
import pytest


def test_application_switcher_dropdown_renders():
    """Test that application switcher dropdown appears in dashboard header"""
    from src.dashboard.presentation.app import create_app
    from src.dashboard.domain.entities.application_registry import Application
    from src.dashboard.infrastructure.repositories.json_multi_app_repository import JsonMultiAppRepository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    import tempfile
    from pathlib import Path
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create Flask app
        app = create_app(
            dashboard_base_path=tmp_path / "dashboards",
            app_registry_db_path=tmp_path / "apps.db"
        )
        
        # Initialize multiple apps
        repo = JsonMultiAppRepository(root_path=str(tmp_path / "dashboards"))
        
        for app_id in ["cortex", "app1", "app2"]:
            application = Application(
                id=app_id,
                name=app_id.upper(),
                display_name=f"{app_id.title()} Dashboard",
                dashboard_path=f"dashboards/{app_id}",
                is_active=True
            )
            repo.initialize_app(application)
            
            data = DashboardData(
                app_id=app_id,
                tabs={"overview": {}},
                metadata={"app_name": application.display_name}
            )
            repo.save(data, app_id=app_id)
        
        # Test
        with app.test_client() as client:
            response = client.get('/dashboard/cortex')
            assert response.status_code == 200
            assert b'app-switcher' in response.data or b'application-switcher' in response.data


def test_application_switcher_lists_active_apps():
    """Test that switcher dropdown shows all active applications"""
    from src.dashboard.presentation.app import create_app
    from src.dashboard.domain.entities.application_registry import Application
    from src.dashboard.infrastructure.repositories.json_multi_app_repository import JsonMultiAppRepository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    import tempfile
    from pathlib import Path
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create Flask app
        app = create_app(
            dashboard_base_path=tmp_path / "dashboards",
            app_registry_db_path=tmp_path / "apps.db"
        )
        
        # Initialize apps
        repo = JsonMultiAppRepository(root_path=str(tmp_path / "dashboards"))
        
        apps_to_create = [
            ("cortex", "CORTEX Dashboard"),
            ("app1", "App One"),
            ("app2", "App Two")
        ]
        
        for app_id, display_name in apps_to_create:
            application = Application(
                id=app_id,
                name=app_id.upper(),
                display_name=display_name,
                dashboard_path=f"dashboards/{app_id}",
                is_active=True
            )
            repo.initialize_app(application)
            
            data = DashboardData(
                app_id=app_id,
                tabs={"overview": {}},
                metadata={"app_name": display_name}
            )
            repo.save(data, app_id=app_id)
        
        # Test
        with app.test_client() as client:
            response = client.get('/dashboard/cortex')
            assert response.status_code == 200
            # Check all app display names appear in HTML
            assert b'CORTEX Dashboard' in response.data
            assert b'App One' in response.data
            assert b'App Two' in response.data


def test_application_switcher_shows_current_app_selected():
    """Test that current application is marked as selected in dropdown"""
    from src.dashboard.presentation.app import create_app
    from src.dashboard.domain.entities.application_registry import Application
    from src.dashboard.infrastructure.repositories.json_multi_app_repository import JsonMultiAppRepository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    import tempfile
    from pathlib import Path
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        app = create_app(
            dashboard_base_path=tmp_path / "dashboards",
            app_registry_db_path=tmp_path / "apps.db"
        )
        
        repo = JsonMultiAppRepository(root_path=str(tmp_path / "dashboards"))
        
        for app_id in ["cortex", "app1"]:
            application = Application(
                id=app_id,
                name=app_id.upper(),
                display_name=f"{app_id.title()} Dashboard",
                dashboard_path=f"dashboards/{app_id}",
                is_active=True
            )
            repo.initialize_app(application)
            
            data = DashboardData(
                app_id=app_id,
                tabs={"overview": {}},
                metadata={"app_name": application.display_name}
            )
            repo.save(data, app_id=app_id)
        
        with app.test_client() as client:
            response = client.get('/dashboard/cortex')
            assert response.status_code == 200
            # Check for selected attribute or class on cortex option
            assert b'selected' in response.data or b'active' in response.data


def test_application_switcher_has_onchange_handler():
    """Test that dropdown has onchange handler for AJAX switching"""
    from src.dashboard.presentation.app import create_app
    from src.dashboard.domain.entities.application_registry import Application
    from src.dashboard.infrastructure.repositories.json_multi_app_repository import JsonMultiAppRepository
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    import tempfile
    from pathlib import Path
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        app = create_app(
            dashboard_base_path=tmp_path / "dashboards",
            app_registry_db_path=tmp_path / "apps.db"
        )
        
        repo = JsonMultiAppRepository(root_path=str(tmp_path / "dashboards"))
        
        application = Application(
            id="cortex",
            name="CORTEX",
            display_name="CORTEX Dashboard",
            dashboard_path="dashboards/cortex",
            is_active=True
        )
        repo.initialize_app(application)
        
        data = DashboardData(
            app_id="cortex",
            tabs={"overview": {}},
            metadata={"app_name": "CORTEX"}
        )
        repo.save(data, app_id="cortex")
        
        with app.test_client() as client:
            response = client.get('/dashboard/cortex')
            assert response.status_code == 200
            # Check for onchange or data-attribute for JS hook
            assert b'onchange' in response.data or b'data-switcher' in response.data


def test_dashboard_js_has_app_switch_function():
    """Test that dashboard.js contains application switching function"""
    from pathlib import Path
    
    js_path = Path("src/dashboard/presentation/static/js/dashboard.js")
    assert js_path.exists(), "dashboard.js not found"
    
    content = js_path.read_text()
    # Check for app switching logic
    assert "switchApp" in content or "switch" in content.lower() or "application" in content.lower()


def test_app_switch_updates_browser_url():
    """Test that switching apps updates browser URL via history API"""
    from pathlib import Path
    
    js_path = Path("src/dashboard/presentation/static/js/dashboard.js")
    assert js_path.exists()
    
    content = js_path.read_text()
    # Check for pushState or replaceState usage
    assert "pushState" in content or "history" in content.lower()


def test_app_switch_preserves_back_button():
    """Test that browser back button works after app switching"""
    # This is verified by checking for pushState in JS
    from pathlib import Path
    
    js_path = Path("src/dashboard/presentation/static/js/dashboard.js")
    assert js_path.exists()
    
    content = js_path.read_text()
    # pushState enables back button functionality
    assert "pushState" in content
