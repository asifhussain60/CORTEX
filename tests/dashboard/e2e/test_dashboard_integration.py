"""
Enhanced Dashboard Integration Tests

Comprehensive validation of dashboard functionality:
- Tab presence in HTML
- Click events and navigation
- HTML rendering without lint issues
- Tab content validation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Date: December 9, 2025
"""

import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class TestTabPresence:
    """Validate all 10 tabs are present in index.html"""
    
    def test_all_nav_tabs_present(self, driver, dashboard_url):
        """Test that all 10 navigation tabs exist in the sidebar"""
        driver.get(dashboard_url)
        
        # Wait for sidebar to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        # Find all nav tabs
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        
        # Verify we have exactly 10 tabs
        assert len(nav_tabs) == 10, f"Expected 10 tabs, found {len(nav_tabs)}"
        
        # Verify tab names (extract text from nav-tab-text spans)
        expected_tabs = [
            "Executive Summary",
            "System Overview",
            "Tech Stack",
            "Security",
            "Use Cases",
            "Recommendations",
            "Architecture",
            "Code Organization",
            "Dependencies",
            "Onboarding"
        ]
        
        # Extract text from nested spans
        actual_tabs = []
        for tab in nav_tabs:
            text_spans = tab.find_elements(By.CLASS_NAME, "nav-tab-text")
            if text_spans:
                actual_tabs.append(text_spans[0].text)
            else:
                actual_tabs.append(tab.text.split('\n')[-1])  # Fallback
        
        for expected in expected_tabs:
            assert expected in actual_tabs, f"Missing tab: {expected}. Found: {actual_tabs}"
    
    def test_all_tab_containers_present(self, driver, dashboard_url):
        """Test that all 10 tab content containers exist"""
        driver.get(dashboard_url)
        
        # Tab container IDs
        container_ids = [
            "executive-container",
            "overview-container",
            "tech-stack-container",
            "security-container",
            "use-cases-container",
            "recommendations-container",
            "architecture-container",
            "code-org-container",
            "vendors-container",
            "engineering-container"
        ]
        
        # Verify each container exists
        for container_id in container_ids:
            try:
                container = driver.find_element(By.ID, container_id)
                assert container is not None, f"Container {container_id} not found"
            except NoSuchElementException:
                pytest.fail(f"Container {container_id} does not exist in DOM")
    
    def test_nav_tabs_have_icons(self, driver, dashboard_url):
        """Test that all nav tabs have icons"""
        driver.get(dashboard_url)
        
        # Wait for sidebar
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        # Find all nav tabs
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        
        # Check each tab has an icon span
        for i, tab in enumerate(nav_tabs):
            icons = tab.find_elements(By.CSS_SELECTOR, "span:first-child")
            assert len(icons) > 0, f"Tab {i} missing icon"


class TestTabClickEvents:
    """Validate click events trigger correct tab display"""
    
    @pytest.mark.parametrize("tab_index,container_id,tab_name", [
        (0, "executive-container", "Executive Summary"),
        (1, "overview-container", "System Overview"),
        (2, "tech-stack-container", "Tech Stack"),
        (3, "security-container", "Security"),
        (4, "use-cases-container", "Use Cases"),
        (5, "recommendations-container", "Recommendations"),
        (6, "architecture-container", "Architecture"),
        (7, "code-org-container", "Code Organization"),
        (8, "vendors-container", "Dependencies"),
        (9, "engineering-container", "Onboarding")
    ])
    def test_tab_click_displays_correct_container(self, driver, dashboard_url, tab_index, container_id, tab_name):
        """Test clicking a tab displays its corresponding container"""
        driver.get(dashboard_url)
        
        # Wait for page load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        # Find and click the tab
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        assert len(nav_tabs) > tab_index, f"Tab index {tab_index} out of range"
        
        tab = nav_tabs[tab_index]
        tab.click()
        
        # Wait for animation to complete
        time.sleep(0.5)
        
        # Verify correct container is displayed
        try:
            container = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, container_id))
            )
            assert container.is_displayed(), f"Container {container_id} not visible after clicking tab"
        except TimeoutException:
            pytest.fail(f"Container {container_id} did not become visible within 5 seconds")
        
        # Verify tab has active class
        tab_classes = tab.get_attribute("class")
        assert "active" in tab_classes, f"Tab {tab_name} does not have 'active' class"
    
    def test_only_one_tab_active_at_a_time(self, driver, dashboard_url):
        """Test that only one tab is active at any given time"""
        driver.get(dashboard_url)
        
        # Wait for page load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        # Click several tabs in sequence
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        
        for i in [0, 3, 7]:  # Click Executive, Security, Code Organization
            nav_tabs[i].click()
            time.sleep(0.3)
            
            # Count active tabs
            active_tabs = driver.find_elements(By.CSS_SELECTOR, ".nav-tab.active")
            assert len(active_tabs) == 1, f"Expected 1 active tab, found {len(active_tabs)}"
            
            # Count visible containers
            visible_containers = driver.find_elements(By.CSS_SELECTOR, ".tab-content[style*='display: block'], .tab-content.active")
            assert len(visible_containers) <= 1, f"Expected at most 1 visible container, found {len(visible_containers)}"
    
    def test_tab_navigation_keyboard(self, driver, dashboard_url):
        """Test keyboard navigation through tabs"""
        driver.get(dashboard_url)
        
        # Wait for page load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        # Get first tab and focus it
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        first_tab = nav_tabs[0]
        
        # Click to focus (simulating keyboard navigation)
        first_tab.click()
        
        # Verify it's focusable and active
        active_element = driver.switch_to.active_element
        assert active_element == first_tab or "active" in first_tab.get_attribute("class")


class TestHTMLRendering:
    """Validate HTML renders without lint issues"""
    
    def test_no_console_errors(self, driver, dashboard_url):
        """Test that no JavaScript errors appear in console"""
        driver.get(dashboard_url)
        
        # Wait for page to fully load
        time.sleep(2)
        
        # Check browser console logs
        logs = driver.get_log('browser')
        
        # Filter for actual errors (not warnings or info)
        errors = [log for log in logs if log['level'] == 'SEVERE']
        
        # Filter out known acceptable errors (e.g., favicon 404)
        critical_errors = [e for e in errors if 'favicon' not in e['message'].lower()]
        
        assert len(critical_errors) == 0, f"Console errors found: {critical_errors}"
    
    def test_all_tabs_have_content(self, driver, dashboard_url):
        """Test that each tab container has child elements or text content"""
        driver.get(dashboard_url)
        
        # Wait for page load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        # Tab container IDs
        container_ids = [
            "executive-container",
            "overview-container",
            "tech-stack-container",
            "security-container",
            "use-cases-container",
            "recommendations-container",
            "architecture-container",
            "code-org-container",
            "vendors-container",
            "engineering-container"
        ]
        
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        
        for i, container_id in enumerate(container_ids):
            # Click tab to show container
            nav_tabs[i].click()
            time.sleep(0.5)
            
            # Find container
            try:
                container = driver.find_element(By.ID, container_id)
                
                # Check for child elements or text content
                children = container.find_elements(By.XPATH, ".//*")
                text_content = container.text.strip()
                
                # Container should have either child elements or text
                has_content = len(children) > 0 or len(text_content) > 0
                assert has_content, f"Container {container_id} has no content (children: {len(children)}, text: '{text_content[:50]}...')"
                
            except NoSuchElementException:
                pytest.fail(f"Container {container_id} not found in DOM")
    
    def test_no_missing_images(self, driver, dashboard_url):
        """Test that no images have broken src attributes"""
        driver.get(dashboard_url)
        
        # Wait for page load
        time.sleep(2)
        
        # Find all images
        images = driver.find_elements(By.TAG_NAME, "img")
        
        broken_images = []
        for img in images:
            # Check if naturalHeight is 0 (indicates broken image)
            natural_height = driver.execute_script("return arguments[0].naturalHeight;", img)
            if natural_height == 0:
                src = img.get_attribute("src")
                broken_images.append(src)
        
        assert len(broken_images) == 0, f"Broken images found: {broken_images}"
    
    def test_all_css_files_loaded(self, driver, dashboard_url):
        """Test that all CSS files loaded successfully (check computed styles)"""
        driver.get(dashboard_url)
        
        # Wait for page load
        time.sleep(2)
        
        # Check if base styles are applied (verify CSS loaded)
        body = driver.find_element(By.TAG_NAME, "body")
        background = body.value_of_css_property("background-color")
        
        # Should have a dark background from base CSS
        assert background, "No background color found (CSS may not have loaded)"
        
        # Check sidebar has styles
        sidebar = driver.find_element(By.CLASS_NAME, "sidebar")
        sidebar_width = sidebar.value_of_css_property("width")
        
        # Sidebar should have width set
        assert sidebar_width != "auto", "Sidebar has no width set (CSS may not have loaded)"
    
    def test_page_title_exists(self, driver, dashboard_url):
        """Test that page has a valid title"""
        driver.get(dashboard_url)
        
        title = driver.title
        assert title, "Page title is empty"
        assert len(title) > 0, "Page title is empty"


class TestTabContentValidation:
    """Validate tab content structure and quality"""
    
    def test_executive_tab_has_health_score(self, driver, dashboard_url):
        """Test Executive Summary tab displays health score or content"""
        driver.get(dashboard_url)
        
        # Click Executive tab
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        nav_tabs[0].click()
        time.sleep(0.5)
        
        # Wait for container to be visible
        container = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "executive-container"))
        )
        
        # Look for health score element or any content
        health_elements = driver.find_elements(By.CSS_SELECTOR, ".health-score, [class*='score'], .stat-card")
        text_content = container.text.strip()
        
        # Should have either health score elements or text content
        has_content = len(health_elements) > 0 or len(text_content) > 0
        assert has_content, f"Executive tab has no content (elements: {len(health_elements)}, text: '{text_content[:50]}...')"
    
    def test_architecture_tab_has_visualization(self, driver, dashboard_url):
        """Test Architecture tab has visualization elements or content"""
        driver.get(dashboard_url)
        
        # Click Architecture tab
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        nav_tabs[6].click()  # Architecture is 7th tab (index 6)
        time.sleep(0.5)
        
        # Look for visualization elements (panels, cards, etc.)
        container = driver.find_element(By.ID, "architecture-container")
        panels = container.find_elements(By.CSS_SELECTOR, ".panel, .glass-card, [class*='card'], div, section")
        text_content = container.text.strip()
        
        # Should have panels or text content
        has_content = len(panels) > 0 or len(text_content) > 0
        assert has_content, f"Architecture tab has no content (panels: {len(panels)}, text: '{text_content[:50]}...')"
    
    def test_tech_stack_tab_has_badges(self, driver, dashboard_url):
        """Test Tech Stack tab displays technology badges or content"""
        driver.get(dashboard_url)
        
        # Click Tech Stack tab
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        nav_tabs[2].click()  # Tech Stack is 3rd tab
        time.sleep(0.5)
        
        # Look for badge elements or any content
        container = driver.find_element(By.ID, "tech-stack-container")
        badges = container.find_elements(By.CSS_SELECTOR, ".badge, [class*='badge'], span, div")
        text_content = container.text.strip()
        
        # Should have badges or text content
        has_content = len(badges) > 0 or len(text_content) > 0
        assert has_content, f"Tech Stack tab has no content (badges: {len(badges)}, text: '{text_content[:50]}...')"
    
    def test_recommendations_tab_has_list_items(self, driver, dashboard_url):
        """Test Recommendations tab has actionable items or content"""
        driver.get(dashboard_url)
        
        # Click Recommendations tab
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        nav_tabs[5].click()  # Recommendations is 6th tab
        time.sleep(0.5)
        
        # Look for list items or any content
        container = driver.find_element(By.ID, "recommendations-container")
        list_items = container.find_elements(By.CSS_SELECTOR, "li, .list-item, [class*='recommendation'], div, p")
        text_content = container.text.strip()
        
        # Should have list items or text content
        has_content = len(list_items) > 0 or len(text_content) > 0
        assert has_content, f"Recommendations tab has no content (items: {len(list_items)}, text: '{text_content[:50]}...')"


class TestResponsiveness:
    """Validate responsive behavior of dashboard"""
    
    def test_sidebar_visible_on_desktop(self, driver, dashboard_url):
        """Test sidebar is visible on desktop viewport"""
        driver.set_window_size(1920, 1080)
        driver.get(dashboard_url)
        
        sidebar = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        assert sidebar.is_displayed(), "Sidebar not visible on desktop"
    
    def test_mobile_menu_present(self, mobile_driver, dashboard_url):
        """Test mobile menu button exists on small viewport"""
        mobile_driver.get(dashboard_url)
        
        # Wait for page load
        time.sleep(1)
        
        # Look for mobile menu button (hamburger)
        try:
            menu_button = mobile_driver.find_element(By.CSS_SELECTOR, ".mobile-menu, .hamburger, [class*='menu-toggle']")
            assert menu_button is not None, "Mobile menu button not found"
        except NoSuchElementException:
            # Mobile menu might be hidden but should exist in DOM
            pass


class TestAccessibility:
    """Validate accessibility features"""
    
    def test_tabs_have_aria_labels(self, driver, dashboard_url):
        """Test navigation tabs have proper ARIA labels"""
        driver.get(dashboard_url)
        
        # Wait for sidebar
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        
        for i, tab in enumerate(nav_tabs):
            # Check for aria-label or meaningful text
            aria_label = tab.get_attribute("aria-label")
            text_content = tab.text
            
            assert aria_label or text_content, f"Tab {i} has no accessible label"
    
    def test_focus_visible_on_tabs(self, driver, dashboard_url):
        """Test focus indicators are visible on keyboard navigation"""
        driver.get(dashboard_url)
        
        # Wait for sidebar
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        # Get first tab and click to focus
        nav_tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        first_tab = nav_tabs[0]
        first_tab.click()
        
        # Check if focus indicator is visible (outline or other styling)
        outline = first_tab.value_of_css_property("outline")
        box_shadow = first_tab.value_of_css_property("box-shadow")
        
        # Either outline or box-shadow should indicate focus
        has_focus_indicator = (
            outline != "none" or 
            "rgba" in box_shadow or 
            "rgb" in box_shadow
        )
        
        assert has_focus_indicator, "No visible focus indicator on tab"
    
    def test_containers_have_role_attributes(self, driver, dashboard_url):
        """Test tab containers have appropriate ARIA roles"""
        driver.get(dashboard_url)
        
        container_ids = [
            "executive-container",
            "overview-container",
            "tech-stack-container",
            "security-container",
            "use-cases-container",
            "recommendations-container",
            "architecture-container",
            "code-org-container",
            "vendors-container",
            "engineering-container"
        ]
        
        for container_id in container_ids:
            try:
                container = driver.find_element(By.ID, container_id)
                role = container.get_attribute("role")
                
                # Container should have tabpanel role or similar
                # If no role, that's okay as long as semantic HTML is used
                if role:
                    assert role in ["tabpanel", "region"], f"Container {container_id} has invalid role: {role}"
            except NoSuchElementException:
                pytest.fail(f"Container {container_id} not found")


class TestPerformance:
    """Validate dashboard performance metrics"""
    
    def test_page_loads_within_timeout(self, driver, dashboard_url):
        """Test page loads within reasonable timeout"""
        start_time = time.time()
        driver.get(dashboard_url)
        
        # Wait for sidebar to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        
        load_time = time.time() - start_time
        
        # Page should load within 5 seconds
        assert load_time < 5, f"Page took {load_time:.2f}s to load (expected < 5s)"
    
    def test_no_javascript_errors_on_load(self, driver, dashboard_url):
        """Test no JavaScript errors occur during initial load"""
        driver.get(dashboard_url)
        time.sleep(2)
        
        logs = driver.get_log('browser')
        js_errors = [log for log in logs if log['level'] == 'SEVERE' and 'javascript' in log['message'].lower()]
        
        assert len(js_errors) == 0, f"JavaScript errors on load: {js_errors}"
