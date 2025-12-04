"""
CSS Styling Tests (RED Phase)

Tests for CSS file existence and styling validation.
Verifies CSS structure, responsive design, and visual elements.

Author: Asif Hussain
"""
import pytest
from pathlib import Path


def test_css_file_exists():
    """Test that style.css exists in static/css directory"""
    css_path = Path("src/dashboard/presentation/static/css/style.css")
    assert css_path.exists(), "style.css not found in static/css directory"


def test_css_contains_dashboard_container(client):
    """Test that rendered HTML references dashboard-container class"""
    response = client.get('/', follow_redirects=True)
    assert b'dashboard-container' in response.data


def test_css_contains_metrics_grid(client):
    """Test that rendered HTML references metrics-grid class"""
    # Use default cortex dashboard that's already seeded in conftest
    response = client.get('/', follow_redirects=True)
    assert b'metrics-grid' in response.data


def test_css_contains_tab_button_class(client):
    """Test that rendered HTML references tab-button class"""
    response = client.get('/', follow_redirects=True)
    assert b'tab-button' in response.data


def test_css_contains_metric_card_class(client):
    """Test that rendered HTML references metric-card class"""
    response = client.get('/', follow_redirects=True)
    assert b'metric-card' in response.data


def test_css_file_not_empty():
    """Test that style.css is not empty"""
    css_path = Path("src/dashboard/presentation/static/css/style.css")
    if css_path.exists():
        content = css_path.read_text()
        assert len(content) > 100, "style.css appears to be empty or too small"


def test_css_contains_responsive_rules():
    """Test that style.css contains responsive media queries"""
    css_path = Path("src/dashboard/presentation/static/css/style.css")
    if css_path.exists():
        content = css_path.read_text()
        assert "@media" in content, "No responsive media queries found in style.css"


def test_css_contains_color_scheme():
    """Test that style.css defines a color scheme"""
    css_path = Path("src/dashboard/presentation/static/css/style.css")
    if css_path.exists():
        content = css_path.read_text()
        # Check for color definitions (hex, rgb, or color names)
        assert "#" in content or "rgb" in content or "var(--" in content, \
            "No color scheme found in style.css"
