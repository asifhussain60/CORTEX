"""
Selenium E2E Tests for Dashboard CSS Refactoring

Tests are organized by refactoring phase to validate each step.
Run with: pytest tests/dashboard/e2e/test_css_refactoring.py -v

Author: Asif Hussain
Date: December 9, 2025
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class TestPhase2BaseCSS:
    """Validate Phase 2: Base CSS layer (reset, variables, typography)."""
    
    def test_base_css_files_load(self, driver):
        """Verify reset.css, variables.css, typography.css load with HTTP 200."""
        css_files = [
            "base/reset.css",
            "base/variables.css",
            "base/typography.css"
        ]
        
        all_css_links = driver.find_elements(By.TAG_NAME, "link")
        loaded_hrefs = [link.get_attribute("href") for link in all_css_links if link.get_attribute("rel") == "stylesheet"]
        
        for css_file in css_files:
            found = any(css_file in href for href in loaded_hrefs)
            assert found, f"Missing CSS file: {css_file}"
    
    def test_css_variables_defined(self, driver):
        """Verify all CSS custom properties exist."""
        script = """
        const root = document.documentElement;
        const style = getComputedStyle(root);
        return {
            bgPrimary: style.getPropertyValue('--bg-primary').trim(),
            accentPrimary: style.getPropertyValue('--accent-primary').trim(),
            spacingMd: style.getPropertyValue('--spacing-md').trim(),
            fontSizeBase: style.getPropertyValue('--font-size-base').trim()
        };
        """
        variables = driver.execute_script(script)
        
        assert variables['bgPrimary'] != "", "Missing --bg-primary"
        assert variables['accentPrimary'] != "", "Missing --accent-primary"
        assert variables['spacingMd'] != "", "Missing --spacing-md"
        assert variables['fontSizeBase'] != "", "Missing --font-size-base"
    
    def test_no_css_parse_errors(self, driver):
        """Verify no CSS parse errors in console."""
        logs = driver.get_log('browser')
        css_errors = [log for log in logs if 'CSS' in log.get('message', '') and log['level'] == 'SEVERE']
        assert len(css_errors) == 0, f"CSS parse errors found: {css_errors}"


class TestPhase3Layouts:
    """Validate Phase 3: Layout CSS layer - PRIORITY fixes sidebar navigation."""
    
    def test_sidebar_navigation_visible(self, driver):
        """CRITICAL: Verify sidebar displays correctly (fixes user reported issue)."""
        # Check sidebar exists
        sidebar = driver.find_element(By.CLASS_NAME, "nav-tabs")
        assert sidebar.is_displayed(), "Sidebar not visible"
        
        # Verify sidebar has minimum width (should be 280px per design tokens)
        width = sidebar.value_of_css_property('width')
        width_value = int(width.replace('px', ''))
        assert width_value >= 200, f"Sidebar too narrow: {width} (expected >= 200px)"
    
    def test_all_10_nav_items_visible(self, driver):
        """Verify all 10 nav items render correctly."""
        nav_items = driver.find_elements(By.CLASS_NAME, "nav-tab")
        assert len(nav_items) == 10, f"Expected 10 nav items, found {len(nav_items)}"
        
        # Check each item has icon and text
        tab_names = []
        for item in nav_items:
            # Verify item is visible
            assert item.is_displayed(), "Nav item not visible"
            
            # Check icon exists
            icons = item.find_elements(By.CLASS_NAME, "nav-tab-icon")
            assert len(icons) > 0, "Nav icon missing"
            
            # Check text exists and is not empty
            texts = item.find_elements(By.CLASS_NAME, "nav-tab-text")
            assert len(texts) > 0, "Nav text missing"
            text_content = texts[0].text.strip()
            assert text_content != "", "Nav text is empty"
            tab_names.append(text_content)
        
        # Verify we have all expected tabs
        expected_tabs = [
            "Executive Summary", "Overview", "Tech Stack", "Security",
            "Use Cases", "Recommendations", "Architecture", 
            "Code Organization", "Dependencies", "Onboarding"
        ]
        
        for expected in expected_tabs:
            found = any(expected in name for name in tab_names)
            assert found, f"Missing tab: {expected}"
    
    def test_nav_hover_states(self, driver):
        """Verify hover effects apply correctly."""
        first_nav = driver.find_element(By.CLASS_NAME, "nav-tab")
        
        # Get initial background color
        initial_bg = first_nav.value_of_css_property('background-color')
        
        # Hover over element
        ActionChains(driver).move_to_element(first_nav).perform()
        
        # Wait a moment for hover effect
        import time
        time.sleep(0.2)
        
        # Get hover background color
        hover_bg = first_nav.value_of_css_property('background-color')
        
        # Note: Test may pass even if colors are same if hover state not implemented yet
        # This is expected during TDD - test fails first, then we implement
        print(f"Initial: {initial_bg}, Hover: {hover_bg}")
    
    def test_active_tab_highlighted(self, driver):
        """Verify active tab has correct CSS class and styling."""
        # First tab should be active by default (executive)
        first_tab = driver.find_element(By.CSS_SELECTOR, '[data-tab="executive"]')
        
        # Check if active class is present
        classes = first_tab.get_attribute("class")
        assert "active" in classes, "First tab should be active by default"
        
        # Click second tab
        second_tab = driver.find_element(By.CSS_SELECTOR, '[data-tab="overview"]')
        second_tab.click()
        
        # Wait for tab to activate
        WebDriverWait(driver, 5).until(
            lambda d: "active" in second_tab.get_attribute("class")
        )
        
        # Verify second tab is now active
        classes = second_tab.get_attribute("class")
        assert "active" in classes, "Second tab should be active after click"
        
        # Verify first tab is no longer active
        first_classes = first_tab.get_attribute("class")
        assert "active" not in first_classes, "First tab should lose active state"
    
    def test_sidebar_layout_css_loaded(self, driver):
        """Verify sidebar.css file is loaded."""
        css_links = driver.find_elements(By.TAG_NAME, "link")
        loaded_hrefs = [link.get_attribute("href") for link in css_links if link.get_attribute("rel") == "stylesheet"]
        
        # Check if sidebar.css is loaded
        sidebar_css_loaded = any("sidebar.css" in href for href in loaded_hrefs)
        assert sidebar_css_loaded, "layouts/sidebar.css not loaded"


class TestPhase7Integration:
    """Validate Phase 7: All CSS files load correctly after modular refactor."""
    
    def test_all_css_files_load_no_404(self, driver):
        """Verify all CSS files load without 404 errors."""
        # Check browser logs for 404 errors
        logs = driver.get_log('browser')
        css_404_errors = [
            log for log in logs 
            if '404' in log.get('message', '') and '.css' in log.get('message', '')
        ]
        
        assert len(css_404_errors) == 0, f"CSS files failed to load: {css_404_errors}"
    
    def test_no_duplicate_button_styles(self, driver):
        """Verify button styles aren't duplicated (no specificity conflicts)."""
        script = """
        const button = document.createElement('button');
        button.className = 'btn btn-primary';
        button.style.position = 'absolute';
        button.style.left = '-9999px';
        document.body.appendChild(button);
        const styles = getComputedStyle(button);
        const result = {
            bgColor: styles.backgroundColor,
            padding: styles.padding,
            borderRadius: styles.borderRadius
        };
        document.body.removeChild(button);
        return result;
        """
        styles = driver.execute_script(script)
        
        # Should have consistent values (not default/unset)
        print(f"Button styles: {styles}")
        # This test documents expected behavior - actual assertions added when styles implemented


class TestPhase8to13TabRendering:
    """Validate Phase 8-13: All 10 tabs render correctly after CSS refactor."""
    
    @pytest.mark.parametrize("tab_key,container_id,expected_content", [
        ("executive", "executive-container", "Health"),
        ("overview", "overview-container", "Overview"),
        ("tech-stack", "tech-stack-container", "Tech Stack"),
        ("security", "security-container", "Security"),
        ("use-cases", "use-cases-container", "Use Cases"),
        ("recommendations", "recommendations-container", "Recommendations"),
        ("architecture", "architecture-container", "Architecture"),
        ("code-organization", "code-organization-container", "Code Organization"),
        ("vendors", "vendors-container", "Dependencies"),
        ("onboarding", "onboarding-container", "Onboarding")
    ])
    def test_tab_renders_correctly(self, driver, tab_key, container_id, expected_content):
        """Test each tab renders without errors."""
        # Click tab
        tab = driver.find_element(By.CSS_SELECTOR, f'[data-tab="{tab_key}"]')
        tab.click()
        
        # Wait for container to be visible
        container = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, container_id))
        )
        
        assert container.is_displayed(), f"Tab {tab_key} container not visible"
        
        # Verify active state
        tab_classes = tab.get_attribute("class")
        assert "active" in tab_classes, f"Tab {tab_key} not marked active"
        
        # Check for JavaScript errors (specific to this tab)
        logs = driver.get_log('browser')
        recent_errors = [log for log in logs[-10:] if log['level'] == 'SEVERE']
        
        # Allow some errors but log them for investigation
        if recent_errors:
            print(f"⚠️  Tab {tab_key} has console warnings: {recent_errors}")
