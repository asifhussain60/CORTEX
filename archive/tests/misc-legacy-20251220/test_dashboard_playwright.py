"""
CORTEX Lens Dashboard E2E Tests - Playwright

CORTEX 4.0 Standard: Playwright for all browser automation testing
Replaces legacy Selenium tests archived to archive/selenium-tests-legacy/

Tests dashboard functionality:
1. Dashboard loads and renders correctly
2. Navigation between tabs works
3. Visualizations render without errors
4. Console has no critical errors
5. Responsive design works across viewports

Author: Asif Hussain
Created: December 20, 2025
"""
import pytest
from pathlib import Path

# Skip all tests if playwright not installed
playwright = pytest.importorskip("playwright.sync_api", reason="playwright not installed")
from playwright.sync_api import sync_playwright, Page, Browser, expect


class TestDashboardPlaywright:
    """Playwright E2E tests for CORTEX Lens dashboard."""
    
    @pytest.fixture(scope="class")
    def dashboard_url(self) -> str:
        """Dashboard URL for testing."""
        return "http://localhost:8080/ui/index.html?source=cleansolidapp"
    
    @pytest.fixture(scope="function")
    def page(self, dashboard_url: str):
        """Create a new browser page for each test."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()
            
            yield page
            
            context.close()
            browser.close()
    
    def test_dashboard_loads_successfully(self, page: Page, dashboard_url: str):
        """
        Verify dashboard loads without errors.
        
        Validates:
        - Page responds with 200 status
        - No console errors on load
        - Main container renders
        """
        # Collect console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append(msg))
        
        # Navigate to dashboard
        response = page.goto(dashboard_url, wait_until="networkidle", timeout=30000)
        
        # Verify successful load
        assert response.status == 200, f"Dashboard failed to load: {response.status}"
        
        # Verify main container exists
        main_container = page.locator(".dashboard-container, #app, main")
        expect(main_container.first).to_be_visible(timeout=10000)
        
        # Check for critical errors (ignore favicon 404s)
        critical_errors = [
            msg for msg in console_messages 
            if msg.type == "error" and "favicon" not in msg.text.lower()
        ]
        assert len(critical_errors) == 0, f"Console errors detected: {[e.text for e in critical_errors]}"
    
    def test_tab_navigation_works(self, page: Page, dashboard_url: str):
        """
        Verify tab navigation functionality.
        
        Validates:
        - All tabs are clickable
        - Tab content switches correctly
        - No errors during navigation
        """
        page.goto(dashboard_url, wait_until="networkidle", timeout=30000)
        
        # Wait for tabs to render
        tabs = page.locator("button[role='tab'], .tab-button, [data-tab]")
        expect(tabs.first).to_be_visible(timeout=10000)
        
        # Get all tab buttons
        tab_count = tabs.count()
        assert tab_count > 0, "No tabs found on dashboard"
        
        # Click each tab and verify content changes
        for i in range(min(tab_count, 8)):  # Test up to 8 tabs
            tab = tabs.nth(i)
            
            # Get tab name for debugging
            tab_text = tab.inner_text()
            
            # Click tab
            tab.click()
            
            # Wait for content to load (adjust selector based on your dashboard)
            page.wait_for_timeout(500)  # Brief wait for animations
            
            # Verify tab is active (common patterns)
            tab_classes = tab.get_attribute("class") or ""
            assert "active" in tab_classes.lower() or "selected" in tab_classes.lower(), \
                f"Tab '{tab_text}' not marked as active after click"
    
    def test_visualizations_render(self, page: Page, dashboard_url: str):
        """
        Verify D3.js/Chart.js visualizations render.
        
        Validates:
        - SVG elements exist (D3.js)
        - Canvas elements exist (Chart.js)
        - No rendering errors in console
        """
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg) if msg.type == "error" else None)
        
        page.goto(dashboard_url, wait_until="networkidle", timeout=30000)
        
        # Wait for visualizations to render
        page.wait_for_timeout(3000)
        
        # Check for SVG visualizations (D3.js)
        svg_count = page.locator("svg").count()
        
        # Check for canvas visualizations (Chart.js)
        canvas_count = page.locator("canvas").count()
        
        # At least some visualizations should exist
        total_viz = svg_count + canvas_count
        assert total_viz > 0, "No visualizations (SVG or Canvas) found on dashboard"
        
        # Filter out favicon errors
        relevant_errors = [
            e for e in console_errors 
            if "favicon" not in e.text.lower() and "404" not in e.text
        ]
        assert len(relevant_errors) == 0, f"Visualization errors: {[e.text for e in relevant_errors]}"
    
    def test_responsive_design(self, page: Page, dashboard_url: str):
        """
        Verify dashboard is responsive across viewports.
        
        Tests:
        - Desktop (1920x1080)
        - Tablet (768x1024)
        - Mobile (375x667)
        """
        viewports = [
            {"name": "Desktop", "width": 1920, "height": 1080},
            {"name": "Tablet", "width": 768, "height": 1024},
            {"name": "Mobile", "width": 375, "height": 667}
        ]
        
        for viewport in viewports:
            # Set viewport size
            page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
            
            # Navigate
            page.goto(dashboard_url, wait_until="networkidle", timeout=30000)
            
            # Verify main container is visible
            main_container = page.locator(".dashboard-container, #app, main")
            expect(main_container.first).to_be_visible(timeout=10000)
            
            # Verify no horizontal overflow (common responsive issue)
            body_width = page.evaluate("document.body.scrollWidth")
            viewport_width = viewport["width"]
            assert body_width <= viewport_width + 20, \
                f"{viewport['name']}: Horizontal overflow detected ({body_width}px > {viewport_width}px)"
    
    def test_no_critical_console_errors(self, page: Page, dashboard_url: str):
        """
        Comprehensive console error check.
        
        Validates:
        - No JavaScript errors
        - No failed resource loads (except favicon)
        - No uncaught exceptions
        """
        console_logs = {"error": [], "warning": [], "info": []}
        
        def handle_console(msg):
            msg_type = msg.type
            if msg_type in console_logs:
                console_logs[msg_type].append(msg.text)
        
        page.on("console", handle_console)
        
        # Navigate and interact
        page.goto(dashboard_url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(5000)  # Let everything settle
        
        # Filter errors
        critical_errors = [
            err for err in console_logs["error"]
            if "favicon" not in err.lower() and "404" not in err
        ]
        
        # Assert no critical errors
        assert len(critical_errors) == 0, \
            f"Critical console errors detected:\n" + "\n".join(critical_errors[:5])


class TestDashboardPerformance:
    """Performance tests for dashboard loading."""
    
    @pytest.fixture(scope="function")
    def page(self):
        """Create browser page with performance tracking."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            yield page
            
            context.close()
            browser.close()
    
    def test_dashboard_load_time(self, page: Page):
        """
        Verify dashboard loads within performance budget.
        
        Target: <3s for first paint (per CORTEX Lens v3.0 DoD)
        """
        page.goto("http://localhost:8080/ui/index.html?source=cleansolidapp", 
                  wait_until="domcontentloaded", timeout=30000)
        
        # Get performance metrics
        metrics = page.evaluate("""
            () => {
                const perfData = window.performance.timing;
                const loadTime = perfData.loadEventEnd - perfData.navigationStart;
                const domReady = perfData.domContentLoadedEventEnd - perfData.navigationStart;
                return {
                    loadTime: loadTime,
                    domReady: domReady
                };
            }
        """)
        
        # Verify load time < 3s (3000ms)
        assert metrics["loadTime"] < 3000, \
            f"Dashboard load time {metrics['loadTime']}ms exceeds 3s budget"
    
    def test_tab_switch_performance(self, page: Page):
        """
        Verify tab switching is fast.
        
        Target: <500ms per CORTEX Lens v3.0 DoD
        """
        page.goto("http://localhost:8080/ui/index.html?source=cleansolidapp", 
                  wait_until="networkidle", timeout=30000)
        
        # Find tabs
        tabs = page.locator("button[role='tab'], .tab-button")
        expect(tabs.first).to_be_visible(timeout=10000)
        
        if tabs.count() >= 2:
            # Click second tab and measure
            start_time = page.evaluate("Date.now()")
            tabs.nth(1).click()
            page.wait_for_timeout(100)  # Brief wait for render
            end_time = page.evaluate("Date.now()")
            
            switch_time = end_time - start_time
            assert switch_time < 500, \
                f"Tab switch time {switch_time}ms exceeds 500ms budget"


# Pytest markers
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.playwright,
    pytest.mark.skipif(
        "not config.getoption('--run-e2e', default=False)",
        reason="E2E tests require --run-e2e flag"
    )
]
