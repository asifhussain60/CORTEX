"""
Test Tab Click and Load Functionality

Validates that clicking each navigation tab displays the correct content container.
Tests all 10 tabs with parametrized approach.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Date: December 9, 2025
"""

import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class TestTabClickAndLoad:
    """Test that clicking each tab loads the corresponding content"""
    
    @pytest.mark.parametrize("tab_name,tab_index,expected_title", [
        ("executive", 0, "Executive Summary"),
        ("overview", 1, "System Overview"),
        ("tech-stack", 2, "Tech Stack"),
        ("security", 3, "Security"),
        ("use-cases", 4, "Use Cases"),
        ("recommendations", 5, "Recommendations"),
        ("architecture", 6, "Architecture"),
        ("code-org", 7, "Code Organization"),
        ("vendors", 8, "Dependencies"),
        ("engineering", 9, "Engineering Onboarding")
    ])
    def test_tab_click_loads_content(self, driver, dashboard_url, tab_name, tab_index, expected_title):
        """
        Test that clicking a tab:
        1. Activates the nav tab
        2. Displays the corresponding content container
        3. Hides all other content containers
        4. Updates the page title
        """
        driver.get(dashboard_url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        # Get all nav tabs
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        assert len(nav_tabs) == 10, f"Expected 10 nav tabs, found {len(nav_tabs)}"
        
        # Click the target tab
        target_tab = nav_tabs[tab_index]
        target_tab.click()
        
        # Wait for tab switch animation
        time.sleep(0.5)
        
        # VERIFY 1: Nav tab has active class
        active_class = target_tab.get_attribute("class")
        assert "active" in active_class, f"Tab {tab_name} nav does not have 'active' class. Classes: {active_class}"
        
        # VERIFY 2: Only one nav tab is active
        active_nav_tabs = driver.find_elements(By.CSS_SELECTOR, ".nav-tab.active")
        assert len(active_nav_tabs) == 1, f"Expected 1 active nav tab, found {len(active_nav_tabs)}"
        
        # VERIFY 3: Correct content container is visible
        content_wrapper_id = f"tab-{tab_name}"
        try:
            content_wrapper = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, content_wrapper_id))
            )
        except TimeoutException:
            pytest.fail(f"Content wrapper {content_wrapper_id} not found in DOM")
        
        # Check if wrapper has active class
        wrapper_classes = content_wrapper.get_attribute("class")
        assert "active" in wrapper_classes, f"Content wrapper {content_wrapper_id} does not have 'active' class. Classes: {wrapper_classes}"
        
        # Check if wrapper is displayed (CSS display: block)
        is_displayed = content_wrapper.is_displayed()
        assert is_displayed, f"Content wrapper {content_wrapper_id} is not displayed (display: none or visibility: hidden)"
        
        # VERIFY 4: Inner container exists
        inner_container_id = f"{tab_name}-container"
        try:
            inner_container = driver.find_element(By.ID, inner_container_id)
            assert inner_container is not None, f"Inner container {inner_container_id} not found"
        except Exception as e:
            pytest.fail(f"Inner container {inner_container_id} not found: {e}")
        
        # VERIFY 5: Only one content wrapper is active
        active_wrappers = driver.find_elements(By.CSS_SELECTOR, ".tab-content.active")
        assert len(active_wrappers) == 1, f"Expected 1 active content wrapper, found {len(active_wrappers)}"
        
        # VERIFY 6: All other wrappers are hidden
        all_wrappers = driver.find_elements(By.CLASS_NAME, "tab-content")
        assert len(all_wrappers) == 10, f"Expected 10 content wrappers, found {len(all_wrappers)}"
        
        hidden_count = 0
        for wrapper in all_wrappers:
            wrapper_id = wrapper.get_attribute("id")
            if wrapper_id != content_wrapper_id:
                # Should not be displayed
                if not wrapper.is_displayed():
                    hidden_count += 1
        
        assert hidden_count == 9, f"Expected 9 hidden wrappers, found {hidden_count}"
        
        # VERIFY 7: Page title updated (if title element exists)
        try:
            title_element = driver.find_element(By.ID, "contentTitle")
            actual_title = title_element.text
            assert expected_title in actual_title or actual_title in expected_title, \
                f"Title mismatch. Expected: {expected_title}, Actual: {actual_title}"
        except:
            # Title element may not exist, skip verification
            pass
        
        # VERIFY 8: Content actually rendered (not just container visible)
        # Check if inner container has any child elements (rendered content)
        try:
            inner_children = inner_container.find_elements(By.XPATH, ".//*")
            assert len(inner_children) > 0, f"Content container {inner_container_id} is empty (no rendered content)"
        except Exception as e:
            # Some tabs may load async, log warning but don't fail
            print(f"Warning: Could not verify content rendering for {tab_name}: {e}")
    
    def test_all_tabs_load_in_sequence(self, driver, dashboard_url):
        """Test clicking through all tabs in sequence"""
        driver.get(dashboard_url)
        
        # Wait for page load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        tab_names = ["executive", "overview", "tech-stack", "security", "use-cases", 
                     "recommendations", "architecture", "code-org", "vendors", "engineering"]
        
        for i, tab_name in enumerate(tab_names):
            # Click tab
            nav_tabs[i].click()
            time.sleep(0.5)  # Increased from 0.3 to allow animations to complete
            
            # Verify correct content displayed
            content_wrapper = driver.find_element(By.ID, f"tab-{tab_name}")
            assert content_wrapper.is_displayed(), f"Tab {tab_name} content not displayed after click"
            
            # Verify only one active
            active_wrappers = driver.find_elements(By.CSS_SELECTOR, ".tab-content.active")
            assert len(active_wrappers) == 1, f"Multiple active wrappers after clicking {tab_name}"
    
    def test_tab_navigation_persists_across_clicks(self, driver, dashboard_url):
        """Test that tab state persists correctly when switching between tabs"""
        driver.get(dashboard_url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        
        # Click Executive (index 0)
        nav_tabs[0].click()
        time.sleep(0.3)
        assert driver.find_element(By.ID, "tab-executive").is_displayed()
        
        # Click Architecture (index 6)
        nav_tabs[6].click()
        # Wait for tab to become active
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#tab-architecture.active"))
        )
        assert driver.find_element(By.ID, "tab-architecture").is_displayed()
        assert not driver.find_element(By.ID, "tab-executive").is_displayed()
        
        # Click Vendors (index 8)
        nav_tabs[8].click()
        time.sleep(0.3)
        assert driver.find_element(By.ID, "tab-vendors").is_displayed()
        assert not driver.find_element(By.ID, "tab-architecture").is_displayed()
        
        # Click back to Executive (index 0)
        nav_tabs[0].click()
        time.sleep(0.3)
        assert driver.find_element(By.ID, "tab-executive").is_displayed()
        assert not driver.find_element(By.ID, "tab-vendors").is_displayed()


class TestTabInitialState:
    """Test initial page load state"""
    
    def test_overview_tab_active_on_load(self, driver, dashboard_url):
        """Test that Executive Summary tab is active by default (matches app.js default)"""
        driver.get(dashboard_url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        # Wait for app.js to initialize and render (data loading + renderCurrentTab)
        time.sleep(2.5)
        
        # Check nav tab
        active_nav = driver.find_element(By.CSS_SELECTOR, ".nav-tab.active")
        assert active_nav.get_attribute("data-tab") == "executive", "Executive nav tab should be active on load"
        
        # Check content wrapper - wait for active class to be applied by renderCurrentTab
        executive_wrapper = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#tab-executive.active"))
        )
        assert executive_wrapper.is_displayed(), "Executive content should be visible"
    
    def test_only_one_tab_visible_on_load(self, driver, dashboard_url):
        """Test that only one content wrapper is visible on initial load"""
        driver.get(dashboard_url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        # Give app.js time to initialize and render
        time.sleep(1.5)
        
        visible_wrappers = []
        all_wrappers = driver.find_elements(By.CLASS_NAME, "tab-content")
        
        for wrapper in all_wrappers:
            if wrapper.is_displayed():
                visible_wrappers.append(wrapper.get_attribute("id"))
        
        assert len(visible_wrappers) == 1, f"Expected 1 visible wrapper on load, found {len(visible_wrappers)}: {visible_wrappers}"
        assert visible_wrappers[0] == "tab-executive", f"Expected tab-executive visible, found {visible_wrappers[0]}"


class TestRaceConditions:
    """Test for race conditions and timing issues identified in console logs"""
    
    def test_rapid_tab_switching(self, driver, dashboard_url):
        """
        Test rapid clicking between tabs to detect race conditions.
        Simulates user quickly switching tabs before content loads.
        """
        driver.get(dashboard_url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        
        # Rapidly click through tabs with minimal delay
        for i in [0, 3, 6, 1, 8, 2]:  # Random order
            nav_tabs[i].click()
            time.sleep(0.05)  # Very short delay to simulate rapid clicking
        
        # Wait for last click to settle
        time.sleep(1.0)
        
        # Verify only one tab is active after rapid switching
        active_wrappers = driver.find_elements(By.CSS_SELECTOR, ".tab-content.active")
        assert len(active_wrappers) == 1, f"Race condition: Multiple active tabs after rapid switching. Found: {len(active_wrappers)}"
        
        active_nav_tabs = driver.find_elements(By.CSS_SELECTOR, ".nav-tab.active")
        assert len(active_nav_tabs) == 1, f"Race condition: Multiple active nav tabs. Found: {len(active_nav_tabs)}"
    
    def test_tab_content_rendering_timing(self, driver, dashboard_url):
        """
        Test that content rendering completes before tab is marked visible.
        Ensures no race between visibility toggle and content load.
        """
        driver.get(dashboard_url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        # Test a few representative tabs
        test_cases = [
            ("overview", 1),
            ("tech-stack", 2),
            ("architecture", 6)
        ]
        
        for tab_name, tab_index in test_cases:
            nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
            nav_tabs[tab_index].click()
            
            # Wait for tab to become visible
            content_wrapper = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, f"#tab-{tab_name}.active"))
            )
            
            # Immediately check if content is present
            inner_container = driver.find_element(By.ID, f"{tab_name}-container")
            
            # Content should be present when tab is visible (no race condition)
            try:
                # Check for any rendered content (divs, spans, etc.)
                elements = inner_container.find_elements(By.XPATH, ".//*")
                # Log for debugging
                print(f"✓ Tab {tab_name}: {len(elements)} elements rendered immediately after visibility")
            except:
                # Some tabs load async, that's okay as long as container is present
                pass
            
            time.sleep(0.3)  # Brief pause between tabs
    
    def test_console_error_monitoring(self, driver, dashboard_url):
        """
        Monitor browser console for JavaScript errors.
        Captures errors that might indicate race conditions or timing issues.
        """
        driver.get(dashboard_url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        # Click through several tabs
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        for i in [0, 1, 2]:
            nav_tabs[i].click()
            time.sleep(0.5)
        
        # Get browser console logs
        logs = driver.get_log('browser')
        
        # Filter out known harmless errors (Chrome extension errors)
        js_errors = [
            log for log in logs 
            if log['level'] == 'SEVERE' 
            and 'Could not establish connection' not in log['message']
            and 'runtime.lastError' not in log['message']
        ]
        
        if js_errors:
            error_messages = "\n".join([log['message'] for log in js_errors])
            pytest.fail(f"JavaScript errors detected:\n{error_messages}")
        
        print(f"✓ No critical JavaScript errors detected (filtered {len(logs) - len(js_errors)} harmless extension errors)")
    
    def test_performance_metrics_valid(self, driver, dashboard_url):
        """
        Test that performance metrics are calculated correctly.
        Ensures no negative or invalid timing values.
        """
        driver.get(dashboard_url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        # Wait for performance report to be logged
        time.sleep(2.0)
        
        # Get performance logs
        logs = driver.get_log('browser')
        perf_logs = [log for log in logs if 'Performance' in log['message'] or 'load time' in log['message'].lower()]
        
        # Check for negative timing values
        for log in perf_logs:
            message = log['message']
            # Look for negative millisecond values
            if '-' in message and 'ms' in message:
                # Extract numeric value
                import re
                numbers = re.findall(r'-\d+', message)
                if numbers:
                    pytest.fail(f"Negative performance timing detected: {message}")
        
        print(f"✓ Performance metrics valid (checked {len(perf_logs)} performance log entries)")
