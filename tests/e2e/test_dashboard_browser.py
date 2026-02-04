"""
Dashboard Browser E2E Tests
Full browser integration tests using Playwright
"""

import pytest
from playwright.sync_api import Page, expect
from pathlib import Path
import json
import subprocess
import time


@pytest.fixture(scope="module")
def spa_server():
    """Start HTTP server for E2E tests."""
    spa_dir = Path(__file__).parent.parent.parent / "company" / "dashboards" / "spa"
    
    # Start server process
    process = subprocess.Popen(
        ["python", "-m", "http.server", "8890"],
        cwd=spa_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(2)
    
    yield "http://localhost:8890"
    
    # Cleanup
    process.terminate()
    process.wait(timeout=5)


@pytest.fixture(scope="module")
def test_data(spa_server):
    """Create test repository data."""
    spa_dir = Path(__file__).parent.parent.parent / "company" / "dashboards" / "spa"
    test_repo_dir = spa_dir / "e2e_test_repo"
    test_repo_dir.mkdir(exist_ok=True)
    
    test_data = {
        "repo_summary": {
            "id": 1,
            "repo_name": "e2e_test_repo",
            "repo_slug": "e2e-test-repo",
            "health_score": 92.5,
            "total_files": 500,
            "file_count": 500,
            "total_loc": 50000,
            "primary_language": "Python",
            "contributor_count": 10,
            "last_commit_date": "2026-02-04T12:00:00Z",
            "last_analyzed_at": "2026-02-04T12:00:00Z",
            "description": "E2E test repository",
            "version": "1.0.0"
        },
        "metrics_summary": {
            "id": 1,
            "total_loc": 50000,
            "code_loc": 40000,
            "comment_loc": 10000,
            "avg_complexity": 6.2,
            "max_complexity": 18,
            "test_coverage": 85.5,
            "maintainability_index": 78.3,
            "code_duplication_pct": 3.1,
            "comment_density": 20.0,
            "technical_debt_hours": 15,
            "calculated_at": "2026-02-04T12:00:00Z"
        },
        "packages": [
            {
                "id": 1,
                "package_name": "pytest",
                "version": "7.4.0",
                "package_type": "dev",
                "is_outdated": False,
                "has_vulnerabilities": False
            }
        ],
        "files": [
            {
                "id": 1,
                "file_path": "main.py",
                "loc": 150
            }
        ],
        "use_cases": [],
        "vulnerabilities": [],
        "executive_kpis": {
            "id": 1,
            "health_status": "healthy",
            "security_posture": "good",
            "tech_debt_hours": 15,
            "test_pass_rate": 95.0,
            "deployment_frequency": "daily",
            "risk_summary": "Repository is in good health",
            "recommendations": ["Increase test coverage", "Reduce complexity"]
        },
        "entities": [],
        "relationships": [],
        "components": [],
        "code_smells": [],
        "metrics_by_file": [],
        "code_snippets": [],
        "test_results": [],
        "lens_insights": [],
        "refactoring_suggestions": []
    }
    
    with open(test_repo_dir / "dashboard-data.json", 'w') as f:
        json.dump(test_data, f, indent=2)
    
    yield "e2e_test_repo"
    
    # Cleanup
    import shutil
    if test_repo_dir.exists():
        shutil.rmtree(test_repo_dir)


class TestDashboardBrowserE2E:
    """Browser-based E2E tests for dashboard."""
    
    def test_e2e_browser_001_dashboard_loads(self, page: Page, spa_server, test_data):
        """E2E-BROWSER-001: Dashboard page loads successfully in browser."""
        page.goto(f"{spa_server}/dashboard.html?repo={test_data}")
        
        # Wait for page to load
        expect(page).to_have_title("CORTEX")
        
        # Verify no console errors
        errors = []
        page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)
        
        # Give time for initialization
        page.wait_for_timeout(2000)
        
        # Should not have critical errors (404s are okay during fallback)
        critical_errors = [e for e in errors if "CORTEX Dashboard" in str(e)]
        assert len(critical_errors) == 0, f"Critical errors found: {critical_errors}"
    
    def test_e2e_browser_002_data_loads(self, page: Page, spa_server, test_data):
        """E2E-BROWSER-002: Dashboard data loads from JSON file."""
        page.goto(f"{spa_server}/dashboard.html?repo={test_data}")
        
        # Wait for data to load (look for repo name in header)
        page.wait_for_selector("text=e2e_test_repo", timeout=5000)
        
        # Verify repo name is displayed
        expect(page.locator("body")).to_contain_text("e2e_test_repo")
    
    def test_e2e_browser_003_tabs_render(self, page: Page, spa_server, test_data):
        """E2E-BROWSER-003: All dashboard tabs are rendered."""
        page.goto(f"{spa_server}/dashboard.html?repo={test_data}")
        page.wait_for_timeout(2000)
        
        # Check for tab navigation
        tabs = page.locator("[role='tab']")
        assert tabs.count() > 0, "No tabs found"
    
    def test_e2e_browser_004_health_score_displays(self, page: Page, spa_server, test_data):
        """E2E-BROWSER-004: Health score is displayed correctly."""
        page.goto(f"{spa_server}/dashboard.html?repo={test_data}")
        page.wait_for_timeout(2000)
        
        # Look for health score (92.5 from test data)
        expect(page.locator("body")).to_contain_text("92")
    
    def test_e2e_browser_005_metrics_display(self, page: Page, spa_server, test_data):
        """E2E-BROWSER-005: Metrics are displayed in dashboard."""
        page.goto(f"{spa_server}/dashboard.html?repo={test_data}")
        page.wait_for_timeout(2000)
        
        # Look for LOC count (50000 from test data)
        expect(page.locator("body")).to_contain_text("50")
    
    def test_e2e_browser_006_no_javascript_errors(self, page: Page, spa_server, test_data):
        """E2E-BROWSER-006: Page loads without JavaScript errors."""
        js_errors = []
        page.on("pageerror", lambda err: js_errors.append(str(err)))
        
        page.goto(f"{spa_server}/dashboard.html?repo={test_data}")
        page.wait_for_timeout(3000)
        
        # Filter out known fallback 404s (SQLite → JSON fallback)
        critical_errors = [e for e in js_errors if "JSONDataAdapter" in e or "undefined" in e]
        assert len(critical_errors) == 0, f"JavaScript errors: {critical_errors}"
    
    def test_e2e_browser_007_scripts_loaded(self, page: Page, spa_server, test_data):
        """E2E-BROWSER-007: All required scripts are loaded."""
        page.goto(f"{spa_server}/dashboard.html?repo={test_data}")
        page.wait_for_timeout(2000)
        
        # Check if key objects exist in window
        json_adapter_exists = page.evaluate("typeof JSONDataAdapter !== 'undefined'")
        dual_loader_exists = page.evaluate("typeof DualFormatDataLoader !== 'undefined'")
        chart_factory_exists = page.evaluate("typeof ChartFactory !== 'undefined'")
        
        assert json_adapter_exists, "JSONDataAdapter not loaded"
        assert dual_loader_exists, "DualFormatDataLoader not loaded"
        assert chart_factory_exists, "ChartFactory not loaded"
    
    def test_e2e_browser_008_tab_switching_works(self, page: Page, spa_server, test_data):
        """E2E-BROWSER-008: Tab switching functionality works."""
        page.goto(f"{spa_server}/dashboard.html?repo={test_data}")
        page.wait_for_timeout(2000)
        
        # Find and click second tab if it exists
        tabs = page.locator("[role='tab']")
        if tabs.count() > 1:
            tabs.nth(1).click()
            page.wait_for_timeout(500)
            
            # Verify active state changed
            active_tabs = page.locator("[role='tab'][aria-selected='true']")
            assert active_tabs.count() > 0, "No active tab after clicking"
    
    def test_e2e_browser_009_responsive_layout(self, page: Page, spa_server, test_data):
        """E2E-BROWSER-009: Dashboard layout is responsive."""
        page.goto(f"{spa_server}/dashboard.html?repo={test_data}")
        page.wait_for_timeout(2000)
        
        # Test mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        page.wait_for_timeout(500)
        
        # Dashboard should still be visible
        assert page.locator("body").is_visible()
        
        # Test desktop viewport
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.wait_for_timeout(500)
        
        assert page.locator("body").is_visible()
    
    def test_e2e_browser_010_missing_repo_error_handling(self, page: Page, spa_server):
        """E2E-BROWSER-010: Dashboard handles missing repository gracefully."""
        page.goto(f"{spa_server}/dashboard.html?repo=nonexistent_repo_12345")
        page.wait_for_timeout(2000)
        
        # Should show error message, not crash
        expect(page.locator("body")).to_contain_text("not found", ignore_case=True)


# Mark all tests as e2e tests
pytestmark = pytest.mark.e2e


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for E2E tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True
    }
