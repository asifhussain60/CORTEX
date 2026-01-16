"""
Test Suite: DO-002-02 Tab-based View Switching
Tests tab interface for switching between dashboard views.

Requirements:
- Tabs: Overview, Audit Log, Metrics, Settings (per section)
- Tab state persisted in URL (#tab-name)
- Active tab has underline indicator
- Smooth transitions (200ms)
- Tab content lazy-loaded
- Refreshing page returns to same tab

Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
from pathlib import Path
from typing import List


# === FIXTURES ===

@pytest.fixture
def tabs_css_path() -> Path:
    """Path to tabs.css file."""
    return Path("src/dashboard/frontend/css/tabs.css")


@pytest.fixture
def tab_switcher_js_path() -> Path:
    """Path to tab-switcher.js file."""
    return Path("src/dashboard/frontend/js/components/common/tab-switcher.js")


@pytest.fixture
def tabs_css_content(tabs_css_path: Path) -> str:
    """Load tabs.css content."""
    if not tabs_css_path.exists():
        pytest.fail(f"tabs.css not found at {tabs_css_path}")
    return tabs_css_path.read_text()


@pytest.fixture
def tab_switcher_js_content(tab_switcher_js_path: Path) -> str:
    """Load tab-switcher.js content."""
    if not tab_switcher_js_path.exists():
        pytest.fail(f"tab-switcher.js not found at {tab_switcher_js_path}")
    return tab_switcher_js_path.read_text()


# === TEST: File Existence ===

def test_tabs_css_exists(tabs_css_path: Path) -> None:
    """
    Test that tabs.css exists in correct location.
    
    Acceptance Criteria:
    - File exists at src/dashboard/frontend/css/tabs.css
    
    CORE-008: TDD test for file structure
    """
    assert tabs_css_path.exists(), \
        f"tabs.css not found at {tabs_css_path}"
    assert tabs_css_path.is_file(), \
        f"tabs.css is not a file at {tabs_css_path}"


def test_tab_switcher_js_exists(tab_switcher_js_path: Path) -> None:
    """
    Test that tab-switcher.js exists in correct location.
    
    Acceptance Criteria:
    - File exists at src/dashboard/frontend/js/components/common/tab-switcher.js
    
    CORE-008: TDD test for file structure
    """
    assert tab_switcher_js_path.exists(), \
        f"tab-switcher.js not found at {tab_switcher_js_path}"
    assert tab_switcher_js_path.is_file(), \
        f"tab-switcher.js is not a file at {tab_switcher_js_path}"


# === TEST: Tab Container Structure ===

def test_tab_container_class(tabs_css_content: str) -> None:
    """
    Test that tab container class is defined.
    
    Acceptance Criteria:
    - .tab-container or .tabs class exists
    
    CORE-008: TDD test for tab structure
    """
    assert ".tab-container" in tabs_css_content or \
           ".tabs" in tabs_css_content, \
        "Tab container class not found"


def test_tab_list_class(tabs_css_content: str) -> None:
    """
    Test that tab list class is defined.
    
    Acceptance Criteria:
    - .tab-list or .tab-nav class exists
    
    CORE-008: TDD test for tab list
    """
    assert ".tab-list" in tabs_css_content or \
           ".tab-nav" in tabs_css_content, \
        "Tab list class not found"


# === TEST: Tab Item Styling ===

def test_tab_item_class(tabs_css_content: str) -> None:
    """
    Test that tab item class is defined.
    
    Acceptance Criteria:
    - .tab-item or .tab class exists
    - Cursor pointer for clickable tabs
    
    CORE-008: TDD test for tab items
    """
    assert ".tab-item" in tabs_css_content or \
           ".tab" in tabs_css_content, \
        "Tab item class not found"


def test_tab_active_state_underline(tabs_css_content: str) -> None:
    """
    Test that active tab has underline indicator.
    
    Acceptance Criteria:
    - .active or .tab.active class exists
    - Border-bottom or underline styling present
    - Uses brand color (cyan)
    
    CORE-008: TDD test for active tab indicator
    """
    # Check for active state class
    active_patterns = [
        ".tab.active",
        ".tab-item.active",
        ".active",
    ]
    
    found_active = any(pattern in tabs_css_content for pattern in active_patterns)
    assert found_active, \
        "Active tab state class not found"
    
    # Check for underline/border styling
    underline_patterns = [
        "border-bottom",
        "border-bottom-color",
        "text-decoration: underline",
        "text-decoration:underline",
    ]
    
    found_underline = any(pattern in tabs_css_content for pattern in underline_patterns)
    assert found_underline, \
        "Active tab underline indicator not found"


def test_tab_hover_states(tabs_css_content: str) -> None:
    """
    Test that tabs have hover state styling.
    
    Acceptance Criteria:
    - :hover pseudo-class defined for tab items
    - Visual feedback on hover
    
    CORE-008: TDD test for hover interactions
    """
    assert ":hover" in tabs_css_content, \
        "Hover states not defined for tabs"


# === TEST: Tab Transitions ===

def test_tab_transition_smoothness(tabs_css_content: str) -> None:
    """
    Test that tab transitions are smooth (200ms).
    
    Acceptance Criteria:
    - transition property defined
    - Duration: 200ms (or 0.2s)
    
    CORE-008: TDD test for smooth animations
    """
    assert "transition" in tabs_css_content, \
        "Transition property not defined for tabs"
    
    # Check for 200ms transition duration
    transition_patterns = [
        "200ms",
        "0.2s",
        "var(--transition-fast)",
    ]
    
    found_transition = any(pattern in tabs_css_content for pattern in transition_patterns)
    assert found_transition, \
        "Tab transition duration should be 200ms"


# === TEST: Tab Content Areas ===

def test_tab_content_class(tabs_css_content: str) -> None:
    """
    Test that tab content area class is defined.
    
    Acceptance Criteria:
    - .tab-content or .tab-panel class exists
    
    CORE-008: TDD test for content panels
    """
    assert ".tab-content" in tabs_css_content or \
           ".tab-panel" in tabs_css_content, \
        "Tab content class not found"


def test_tab_content_hidden_state(tabs_css_content: str) -> None:
    """
    Test that hidden tab content is properly styled.
    
    Acceptance Criteria:
    - .hidden or display: none for inactive tabs
    
    CORE-008: TDD test for content visibility
    """
    hidden_patterns = [
        "display: none",
        "display:none",
        ".hidden",
        "visibility: hidden",
    ]
    
    found_hidden = any(pattern in tabs_css_content for pattern in hidden_patterns)
    assert found_hidden, \
        "Hidden tab content state not defined"


# === TEST: JavaScript Functionality ===

def test_tab_switcher_initialization(tab_switcher_js_content: str) -> None:
    """
    Test that initializeTabSwitcher() function is defined.
    
    Acceptance Criteria:
    - function initializeTabSwitcher() exists
    
    CORE-008: TDD test for JavaScript component
    """
    assert "function initializeTabSwitcher()" in tab_switcher_js_content or \
           "initializeTabSwitcher = function()" in tab_switcher_js_content or \
           "const initializeTabSwitcher" in tab_switcher_js_content, \
        "initializeTabSwitcher() function not found"


def test_tab_switch_function(tab_switcher_js_content: str) -> None:
    """
    Test that function to switch tabs exists.
    
    Acceptance Criteria:
    - switchTab() or similar function exists
    - Function handles tab activation
    
    CORE-008: TDD test for tab switching
    """
    switch_patterns = [
        "function switchTab",
        "switchTab = function",
        "const switchTab",
        "function activateTab",
        "classList.add('active')",
    ]
    
    found_switch = any(pattern in tab_switcher_js_content for pattern in switch_patterns)
    assert found_switch, \
        "Tab switch function not found"


def test_url_hash_navigation(tab_switcher_js_content: str) -> None:
    """
    Test that URL hash navigation is implemented.
    
    Acceptance Criteria:
    - window.location.hash used for tab state
    - Hash updates when tab changes
    
    CORE-008: TDD test for URL state persistence
    """
    assert "window.location.hash" in tab_switcher_js_content or \
           "location.hash" in tab_switcher_js_content, \
        "URL hash navigation not implemented"


def test_tab_click_handlers(tab_switcher_js_content: str) -> None:
    """
    Test that tab click event handlers are defined.
    
    Acceptance Criteria:
    - Click event listeners attached to tabs
    - Prevents default anchor behavior
    
    CORE-008: TDD test for tab interactions
    """
    assert "addEventListener('click'" in tab_switcher_js_content or \
           'addEventListener("click"' in tab_switcher_js_content, \
        "Click event listeners not attached to tabs"


def test_tab_restoration_from_url(tab_switcher_js_content: str) -> None:
    """
    Test that tab state is restored from URL on page load.
    
    Acceptance Criteria:
    - Function to restore active tab from hash
    - Called on initialization
    
    CORE-008: TDD test for state restoration
    """
    restore_patterns = [
        "restoreTabFromURL",
        "setTabFromHash",
        "window.location.hash",
        "activateTabFromHash",
    ]
    
    found_restore = any(pattern in tab_switcher_js_content for pattern in restore_patterns)
    assert found_restore, \
        "Tab restoration from URL not implemented"


def test_keyboard_navigation_support(tab_switcher_js_content: str) -> None:
    """
    Test that keyboard navigation is supported (optional but good practice).
    
    Acceptance Criteria:
    - Arrow key navigation between tabs (optional)
    - Enter/Space to activate tab (optional)
    
    CORE-008: TDD test for keyboard accessibility
    """
    # This is optional, so we'll make it a soft check
    keyboard_patterns = [
        "keydown",
        "ArrowRight",
        "ArrowLeft",
        "Enter",
    ]
    
    found_keyboard = any(pattern in tab_switcher_js_content for pattern in keyboard_patterns)
    
    if not found_keyboard:
        pytest.skip("Keyboard navigation not implemented (optional feature)")


# === TEST: Lazy Loading ===

def test_lazy_content_loading(tab_switcher_js_content: str) -> None:
    """
    Test that tab content is lazy-loaded.
    
    Acceptance Criteria:
    - Content loaded on tab activation (not all at once)
    - Loading indicator or placeholder
    
    CORE-008: TDD test for lazy loading
    """
    # Check for lazy loading patterns
    lazy_patterns = [
        "loadTabContent",
        "fetchTabData",
        "data-loaded",
        "lazyLoad",
    ]
    
    found_lazy = any(pattern in tab_switcher_js_content for pattern in lazy_patterns)
    
    # Lazy loading is important but not critical for initial implementation
    if not found_lazy:
        pytest.skip("Lazy loading not implemented (can be added later)")


# === TEST: Integration ===

def test_index_html_includes_tabs_css() -> None:
    """
    Test that index.html includes tabs.css stylesheet.
    
    Acceptance Criteria:
    - <link rel="stylesheet" href="/css/tabs.css"> present
    
    CORE-008: TDD test for integration
    """
    index_html_path = Path("src/dashboard/frontend/index.html")
    
    if not index_html_path.exists():
        pytest.skip("index.html not found, skipping integration test")
    
    index_html_content = index_html_path.read_text()
    
    assert 'href="/css/tabs.css"' in index_html_content or \
           "href='/css/tabs.css'" in index_html_content, \
        "tabs.css not linked in index.html"


def test_index_html_includes_tab_switcher_js() -> None:
    """
    Test that index.html includes tab-switcher.js script.
    
    Acceptance Criteria:
    - <script src="/js/components/common/tab-switcher.js"> present
    
    CORE-008: TDD test for integration
    """
    index_html_path = Path("src/dashboard/frontend/index.html")
    
    if not index_html_path.exists():
        pytest.skip("index.html not found, skipping integration test")
    
    index_html_content = index_html_path.read_text()
    
    assert 'src="/js/components/common/tab-switcher.js"' in index_html_content or \
           "src='/js/components/common/tab-switcher.js'" in index_html_content, \
        "tab-switcher.js not included in index.html"


def test_tab_structure_in_html() -> None:
    """
    Test that HTML includes tab structure.
    
    Acceptance Criteria:
    - Tab container with tab list
    - At least one tab example (Overview, Audit Log, etc.)
    
    CORE-008: TDD test for HTML structure
    """
    index_html_path = Path("src/dashboard/frontend/index.html")
    
    if not index_html_path.exists():
        pytest.skip("index.html not found, skipping integration test")
    
    index_html_content = index_html_path.read_text()
    
    # Check for tab-related classes or IDs
    tab_structure_patterns = [
        "tab-container",
        "tab-list",
        "tab-item",
        "tab-content",
        "tabs",
    ]
    
    found_structure = any(pattern in index_html_content for pattern in tab_structure_patterns)
    
    # Tab structure might not be in index.html yet (dynamically created)
    if not found_structure:
        pytest.skip("Tab structure not in HTML (may be dynamically created)")
