"""
Test CORTEX Lens Landing Page Loading and Navigation

Tests:
- Page loads successfully
- All tabs are present and clickable
- Tab switching works correctly
- Logo displays properly
- No JavaScript errors
"""

import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import http.server
import socketserver
import threading
import os


class TestLandingPage:
    """Test suite for CORTEX Lens landing page"""
    
    @classmethod
    def setup_class(cls):
        """Setup web server and browser before all tests"""
        # Start local web server
        cls.PORT = 8001
        cls.server_thread = None
        cls.start_server()
        
        # Setup Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(10)
        cls.base_url = f"http://localhost:{cls.PORT}"
        
    @classmethod
    def start_server(cls):
        """Start HTTP server for testing"""
        os.chdir('d:/PROJECTS/CORTEX/cortex-lens-output/mock-landing')
        
        handler = http.server.SimpleHTTPRequestHandler
        cls.httpd = socketserver.TCPServer(("", cls.PORT), handler)
        
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1)  # Wait for server to start
        
    @classmethod
    def teardown_class(cls):
        """Cleanup after all tests"""
        cls.driver.quit()
        cls.httpd.shutdown()
        
    def test_page_loads(self):
        """Test that the page loads successfully"""
        self.driver.get(self.base_url)
        
        # Wait for page to load
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Check title
        assert "CORTEX - Repository Analysis" in self.driver.title
        
    def test_no_javascript_errors(self):
        """Test that there are no JavaScript errors (ignoring favicon 404)"""
        self.driver.get(self.base_url)
        time.sleep(2)  # Wait for JS to execute
        
        # Get browser console logs
        logs = self.driver.get_log('browser')
        # Filter out favicon 404 (cosmetic warning)
        errors = [log for log in logs if log['level'] == 'SEVERE' and 'favicon.ico' not in log['message']]
        
        assert len(errors) == 0, f"JavaScript errors found: {errors}"
        
    def test_logo_displays(self):
        """Test that the CORTEX logo displays"""
        self.driver.get(self.base_url)
        
        logo = self.driver.find_element(By.CLASS_NAME, "cortex-logo")
        assert logo.is_displayed()
        
        # Check logo size (should be 200px after consolidation)
        width = logo.size['width']
        assert width >= 200, f"Logo width is {width}px, expected 200px"
        
    def test_all_tabs_present(self):
        """Test that all 6 consolidated navigation tabs are present"""
        self.driver.get(self.base_url)
        
        expected_tabs = [
            "executive", "overview", "architecture",
            "quality", "security", "dependencies"
        ]
        
        for tab_id in expected_tabs:
            tab_link = self.driver.find_element(By.CSS_SELECTOR, f'a[data-tab="{tab_id}"]')
            assert tab_link.is_displayed(), f"Tab {tab_id} not found"
            
    def test_tab_switching(self):
        """Test that clicking tabs switches content"""
        self.driver.get(self.base_url)
        time.sleep(1)
        
        # Get all tab links (6 consolidated tabs)
        tabs = ["overview", "architecture", "quality", "security"]
        
        for tab_id in tabs:
            # Click tab
            tab_link = self.driver.find_element(By.CSS_SELECTOR, f'a[data-tab="{tab_id}"]')
            tab_link.click()
            time.sleep(0.5)
            
            # Verify tab is active
            assert "active" in tab_link.get_attribute("class"), f"Tab {tab_id} not activated"
            
            # Verify content section is visible
            content = self.driver.find_element(By.ID, tab_id)
            assert "active" in content.get_attribute("class"), f"Content {tab_id} not visible"
            
    def test_navigation_order(self):
        """Test that navigation tabs are in logical order"""
        self.driver.get(self.base_url)
        
        expected_order = [
            "Executive Summary", "Overview", "Architecture & Technical",
            "Quality & Testing", "Security", "Dependencies & Workflows"
        ]
        
        tab_texts = self.driver.find_elements(By.CLASS_NAME, "tab-text")
        actual_order = [tab.text for tab in tab_texts]
        
        assert actual_order == expected_order, f"Tab order mismatch. Expected: {expected_order}, Got: {actual_order}"
        
    def test_executive_summary_active_by_default(self):
        """Test that Executive Summary tab is active on page load"""
        self.driver.get(self.base_url)
        
        executive_tab = self.driver.find_element(By.CSS_SELECTOR, 'a[data-tab="executive"]')
        executive_content = self.driver.find_element(By.ID, "executive")
        
        assert "active" in executive_tab.get_attribute("class")
        assert "active" in executive_content.get_attribute("class")
        
    def test_theme_toggle(self):
        """Test that theme toggle button works"""
        self.driver.get(self.base_url)
        
        # Get initial theme
        html = self.driver.find_element(By.TAG_NAME, "html")
        initial_theme = html.get_attribute("data-theme")
        
        # Click theme toggle
        theme_button = self.driver.find_element(By.ID, "themeToggle")
        theme_button.click()
        time.sleep(0.5)
        
        # Verify theme changed
        new_theme = html.get_attribute("data-theme")
        assert new_theme != initial_theme, "Theme did not change"
        
    def test_collapsible_tiles_work(self):
        """Test that collapsible use case tiles expand/collapse"""
        self.driver.get(self.base_url)
        time.sleep(1)
        
        # Find first use case tile
        tile_headers = self.driver.find_elements(By.CLASS_NAME, "tile-header")
        assert len(tile_headers) >= 3, "Expected at least 3 use case tiles"
        
        # Click first tile header
        tile_headers[0].click()
        time.sleep(0.5)
        
        # Verify tile expanded
        tile = tile_headers[0].find_element(By.XPATH, "..")
        assert "expanded" in tile.get_attribute("class"), "Tile did not expand"
        

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
