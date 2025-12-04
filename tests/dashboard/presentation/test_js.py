"""
JavaScript Functionality Tests (RED Phase)

Tests for dashboard.js interactivity.
Verifies tab switching, refresh functionality, and DOM manipulation.

Author: Asif Hussain
"""
import pytest
from pathlib import Path


def test_js_file_exists():
    """Test that dashboard.js exists in static/js directory"""
    js_path = Path("src/dashboard/presentation/static/js/dashboard.js")
    assert js_path.exists(), "dashboard.js not found in static/js directory"


def test_js_file_not_empty():
    """Test that dashboard.js is not empty"""
    js_path = Path("src/dashboard/presentation/static/js/dashboard.js")
    if js_path.exists():
        content = js_path.read_text()
        assert len(content) > 50, "dashboard.js appears to be empty or too small"


def test_js_contains_tab_switching_function():
    """Test that dashboard.js contains tab switching logic"""
    js_path = Path("src/dashboard/presentation/static/js/dashboard.js")
    if js_path.exists():
        content = js_path.read_text()
        # Check for tab-related functions
        assert "tab" in content.lower(), "No tab-related code found in dashboard.js"


def test_js_contains_refresh_function():
    """Test that dashboard.js contains refresh functionality"""
    js_path = Path("src/dashboard/presentation/static/js/dashboard.js")
    if js_path.exists():
        content = js_path.read_text()
        assert "refresh" in content.lower(), "No refresh functionality found in dashboard.js"


def test_js_contains_event_listeners():
    """Test that dashboard.js sets up event listeners"""
    js_path = Path("src/dashboard/presentation/static/js/dashboard.js")
    if js_path.exists():
        content = js_path.read_text()
        assert "addEventListener" in content or "onclick" in content.lower(), \
            "No event listeners found in dashboard.js"


def test_html_includes_js_script(client):
    """Test that rendered HTML includes dashboard.js script tag"""
    response = client.get('/')
    assert b'dashboard.js' in response.data


def test_tab_buttons_have_data_attributes(client):
    """Test that tab buttons have data-tab attributes for JS targeting"""
    response = client.get('/')
    assert b'data-tab' in response.data
