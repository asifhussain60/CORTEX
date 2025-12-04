"""
Template Rendering Tests (RED Phase)

Tests for Jinja2 template rendering with Flask.
Verifies templates render correctly with proper context data.

Author: Asif Hussain
"""
import pytest
from pathlib import Path


def test_base_template_renders(client):
    """Test base template renders with title"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'<!DOCTYPE html>' in response.data
    assert b'<html' in response.data
    assert b'</html>' in response.data


def test_dashboard_shows_app_name(client, tmp_path):
    """Test dashboard displays application name"""
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    
    repo = JsonDashboardRepository(base_path=tmp_path / "dashboards")
    data = DashboardData(
        app_id="cortex",
        tabs={"overview": {"files": 100}},
        metadata={"app_name": "CORTEX"}
    )
    repo.save(data)
    
    response = client.get('/')
    assert b'CORTEX' in response.data


def test_dashboard_shows_tab_count(client, tmp_path):
    """Test dashboard displays number of tabs"""
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    
    repo = JsonDashboardRepository(base_path=tmp_path / "dashboards")
    data = DashboardData(
        app_id="cortex",
        tabs={"overview": {}, "metrics": {}, "health": {}},
        metadata={"app_name": "CORTEX"}
    )
    repo.save(data)
    
    response = client.get('/')
    assert b'3' in response.data or b'three' in response.data.lower()


def test_template_includes_css(client):
    """Test template includes CSS stylesheet link"""
    response = client.get('/')
    assert b'<link' in response.data
    assert b'stylesheet' in response.data.lower()
    assert b'.css' in response.data


def test_template_includes_navigation(client):
    """Test template includes navigation menu"""
    response = client.get('/')
    assert b'<nav' in response.data or b'navigation' in response.data.lower()


def test_template_has_responsive_viewport(client):
    """Test template includes responsive viewport meta tag"""
    response = client.get('/')
    assert b'viewport' in response.data
    assert b'width=device-width' in response.data


def test_template_renders_tab_data(client, tmp_path):
    """Test template renders tab content data"""
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    
    repo = JsonDashboardRepository(base_path=tmp_path / "dashboards")
    data = DashboardData(
        app_id="cortex",
        tabs={"overview": {"total_files": 250, "total_lines": 12500}},
        metadata={"app_name": "CORTEX"}
    )
    repo.save(data)
    
    response = client.get('/')
    assert b'250' in response.data or b'total_files' in response.data


def test_template_escapes_html_in_data(client, tmp_path):
    """Test template properly escapes HTML in user data"""
    from src.dashboard.domain.entities.dashboard_data import DashboardData
    from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
    
    repo = JsonDashboardRepository(base_path=tmp_path / "dashboards")
    data = DashboardData(
        app_id="test-xss",
        tabs={},
        metadata={"app_name": "<script>alert('XSS')</script>"}
    )
    repo.save(data)
    
    response = client.get('/test-xss')
    # Should be escaped, not executed
    assert b'&lt;script&gt;' in response.data or b'<script>' not in response.data
