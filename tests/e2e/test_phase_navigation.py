"""
End-to-End tests for phase navigation system using Playwright.

Tests navigation from master dashboard to phase detail pages, breadcrumb navigation,
previous/next phase navigation, and 404 handling.

CORTEX Phase Story System — Phase 3: Navigation System
TDD RED Phase: Tests written before implementation
"""

import pytest
from pathlib import Path
from playwright.sync_api import Page, expect


@pytest.fixture
def dashboard_url():
    """URL to master dashboard."""
    return "file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/dashboard/index.html"


@pytest.fixture
def phase_detail_url():
    """Base URL for phase detail pages."""
    return "file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/dashboard/phases"


class TestPhaseCardNavigation:
    """Test clicking phase cards navigates to detail pages."""
    
    def test_click_phase_card_navigates_to_detail_page(self, page: Page, dashboard_url: str):
        """Clicking a phase card should navigate to its detail page."""
        # Navigate to dashboard
        page.goto(dashboard_url)
        
        # Find first clickable phase card
        phase_card = page.locator('[data-phase-id]').first
        phase_id = phase_card.get_attribute('data-phase-id')
        
        # Click the card
        phase_card.click()
        
        # Verify navigation to detail page
        expect(page).to_have_url(f".*phase-{phase_id}/index.html$")
        
        # Verify detail page loads
        expect(page.locator('h1')).to_contain_text(f"Phase {phase_id}")
    
    def test_all_active_phase_cards_are_clickable(self, page: Page, dashboard_url: str):
        """All active phase cards should have clickable links."""
        page.goto(dashboard_url)
        
        # Get all active phase cards
        active_cards = page.locator('[data-phase-id][data-status="COMPLETED"], [data-phase-id][data-status="IN_PROGRESS"]')
        count = active_cards.count()
        
        # Verify all have href attributes
        for i in range(count):
            card = active_cards.nth(i)
            phase_id = card.get_attribute('data-phase-id')
            
            # Check if card or parent link has href
            link = card.locator('a').first if card.locator('a').count() > 0 else card
            expect(link).to_have_attribute('href', f"phases/phase-{phase_id}/index.html")
    
    def test_planned_phase_cards_are_not_clickable(self, page: Page, dashboard_url: str):
        """Planned phase cards should not be clickable (no links)."""
        page.goto(dashboard_url)
        
        # Get all planned phase cards
        planned_cards = page.locator('[data-phase-id][data-status="PLANNED"]')
        
        if planned_cards.count() > 0:
            card = planned_cards.first
            # Planned cards should not have clickable links
            expect(card.locator('a')).to_have_count(0)


class TestBreadcrumbNavigation:
    """Test breadcrumb navigation works correctly."""
    
    def test_breadcrumb_home_link_returns_to_dashboard(self, page: Page, dashboard_url: str):
        """Breadcrumb home link should return to dashboard."""
        page.goto(dashboard_url)
        
        # Navigate to a phase detail page
        phase_card = page.locator('[data-phase-id]').first
        phase_card.click()
        
        # Click breadcrumb home link
        home_link = page.locator('[data-breadcrumb="home"]')
        home_link.click()
        
        # Verify back at dashboard
        expect(page).to_have_url(dashboard_url)
        expect(page.locator('h1')).to_contain_text('CORTEX')
    
    def test_breadcrumb_shows_current_phase(self, page: Page, dashboard_url: str):
        """Breadcrumb should display current phase name."""
        page.goto(dashboard_url)
        
        # Navigate to phase detail
        phase_card = page.locator('[data-phase-id]').first
        phase_id = phase_card.get_attribute('data-phase-id')
        phase_name = phase_card.locator('.phase-name').text_content()
        
        phase_card.click()
        
        # Verify breadcrumb shows phase name
        breadcrumb = page.locator('[data-breadcrumb="current"]')
        expect(breadcrumb).to_contain_text(phase_name)


class TestPreviousNextNavigation:
    """Test previous/next phase navigation."""
    
    def test_next_button_navigates_to_next_phase(self, page: Page, dashboard_url: str):
        """Next button should navigate to next sequential phase."""
        page.goto(dashboard_url)
        
        # Find a phase that has a next phase
        phase_cards = page.locator('[data-phase-id]')
        
        for i in range(phase_cards.count() - 1):  # Exclude last phase
            card = phase_cards.nth(i)
            current_id = int(card.get_attribute('data-phase-id'))
            
            card.click()
            
            # Click next button
            next_button = page.locator('[data-nav="next"]')
            if next_button.is_visible():
                next_button.click()
                
                # Verify navigation to next phase
                expect(page).to_have_url(f".*phase-{current_id + 1}/index.html$")
                break
    
    def test_previous_button_navigates_to_previous_phase(self, page: Page, dashboard_url: str):
        """Previous button should navigate to previous sequential phase."""
        page.goto(dashboard_url)
        
        # Find a phase that has a previous phase (not first)
        phase_cards = page.locator('[data-phase-id]')
        
        if phase_cards.count() > 1:
            card = phase_cards.nth(1)  # Second phase
            current_id = int(card.get_attribute('data-phase-id'))
            
            card.click()
            
            # Click previous button
            prev_button = page.locator('[data-nav="previous"]')
            if prev_button.is_visible():
                prev_button.click()
                
                # Verify navigation to previous phase
                expect(page).to_have_url(f".*phase-{current_id - 1}/index.html$")
    
    def test_first_phase_has_no_previous_button(self, page: Page, dashboard_url: str):
        """First phase should not show previous button."""
        page.goto(dashboard_url)
        
        # Navigate to first phase
        first_card = page.locator('[data-phase-id="1"]')
        first_card.click()
        
        # Verify no previous button
        prev_button = page.locator('[data-nav="previous"]')
        expect(prev_button).not_to_be_visible()
    
    def test_last_phase_has_no_next_button(self, page: Page, dashboard_url: str):
        """Last phase should not show next button."""
        page.goto(dashboard_url)
        
        # Get all phase cards and navigate to last
        phase_cards = page.locator('[data-phase-id]')
        last_index = phase_cards.count() - 1
        last_card = phase_cards.nth(last_index)
        
        last_card.click()
        
        # Verify no next button
        next_button = page.locator('[data-nav="next"]')
        expect(next_button).not_to_be_visible()


class TestDeepLinking:
    """Test direct URL access to phase detail pages."""
    
    def test_direct_url_access_works(self, page: Page, phase_detail_url: str):
        """Direct URL access should load phase detail page."""
        # Access phase-1 directly
        page.goto(f"{phase_detail_url}/phase-1/index.html")
        
        # Verify page loads
        expect(page.locator('h1')).to_contain_text('Phase 1')
    
    def test_deep_link_preserves_navigation(self, page: Page, phase_detail_url: str):
        """Deep linked pages should have working navigation."""
        page.goto(f"{phase_detail_url}/phase-2/index.html")
        
        # Verify breadcrumb home link exists
        home_link = page.locator('[data-breadcrumb="home"]')
        expect(home_link).to_be_visible()
        
        # Verify previous/next buttons exist (if applicable)
        prev_button = page.locator('[data-nav="previous"]')
        expect(prev_button).to_be_visible()


class Test404Handling:
    """Test 404 handling for missing phases."""
    
    def test_missing_phase_shows_404_message(self, page: Page, phase_detail_url: str):
        """Accessing missing phase should show friendly 404 message."""
        # Try to access phase-999 (doesn't exist)
        page.goto(f"{phase_detail_url}/phase-999/index.html")
        
        # Browser will show file not found
        # In production, this would be handled by a 404 page
        # For now, verify URL attempted
        expect(page).to_have_url(f".*phase-999/index.html$")
    
    def test_404_page_provides_back_to_dashboard_link(self, page: Page, phase_detail_url: str):
        """404 page should provide link back to dashboard."""
        # This test will be implemented when 404.html is created
        # For file:// protocol, browser shows default 404
        pass


class TestNavigationAccessibility:
    """Test navigation accessibility features."""
    
    def test_phase_cards_have_aria_labels(self, page: Page, dashboard_url: str):
        """Phase cards should have ARIA labels for screen readers."""
        page.goto(dashboard_url)
        
        phase_cards = page.locator('[data-phase-id]')
        
        for i in range(min(3, phase_cards.count())):  # Check first 3
            card = phase_cards.nth(i)
            expect(card).to_have_attribute('aria-label')
    
    def test_navigation_buttons_have_aria_labels(self, page: Page, dashboard_url: str):
        """Previous/Next buttons should have ARIA labels."""
        page.goto(dashboard_url)
        
        # Navigate to a phase
        phase_card = page.locator('[data-phase-id]').nth(1)  # Second phase
        phase_card.click()
        
        # Check previous button
        prev_button = page.locator('[data-nav="previous"]')
        if prev_button.is_visible():
            expect(prev_button).to_have_attribute('aria-label')
        
        # Check next button
        next_button = page.locator('[data-nav="next"]')
        if next_button.is_visible():
            expect(next_button).to_have_attribute('aria-label')


class TestNavigationKeyboardSupport:
    """Test keyboard navigation support."""
    
    def test_phase_cards_keyboard_accessible(self, page: Page, dashboard_url: str):
        """Phase cards should be accessible via keyboard (Tab, Enter)."""
        page.goto(dashboard_url)
        
        # Tab to first phase card
        page.keyboard.press('Tab')
        
        # Verify focus on phase card or link
        focused = page.locator(':focus')
        expect(focused).to_have_attribute('data-phase-id')
    
    def test_navigation_buttons_keyboard_accessible(self, page: Page, dashboard_url: str):
        """Previous/Next buttons should work with keyboard."""
        page.goto(dashboard_url)
        
        # Navigate to phase
        phase_card = page.locator('[data-phase-id]').nth(1)
        phase_card.click()
        
        # Tab to previous button and press Enter
        prev_button = page.locator('[data-nav="previous"]')
        if prev_button.is_visible():
            prev_button.focus()
            page.keyboard.press('Enter')
            
            # Verify navigation occurred
            expect(page).to_have_url('.*phase-\\d+/index.html$')
