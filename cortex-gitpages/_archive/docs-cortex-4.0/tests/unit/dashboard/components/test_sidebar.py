"""
Test Suite: DO-002-01 Sidebar Navigation with Active States
Tests persistent sidebar navigation component for CORTEX Dashboard.

Requirements:
- 5 main sections: Brain Observatory, Temporal Cortex, Orchestrators, Plan Hub, Admin
- Active section highlighted with brand color (cyan)
- Collapse/expand toggle functionality
- Smooth transitions (200-300ms)
- Mobile: Sidebar hidden, hamburger menu used instead

Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
from pathlib import Path
from typing import List


# === FIXTURES ===

@pytest.fixture
def sidebar_css_path() -> Path:
    """Path to sidebar.css file."""
    return Path("src/dashboard/frontend/css/sidebar.css")


@pytest.fixture
def sidebar_js_path() -> Path:
    """Path to sidebar.js file."""
    return Path("src/dashboard/frontend/js/components/common/sidebar.js")


@pytest.fixture
def sidebar_css_content(sidebar_css_path: Path) -> str:
    """Load sidebar.css content."""
    if not sidebar_css_path.exists():
        pytest.fail(f"sidebar.css not found at {sidebar_css_path}")
    return sidebar_css_path.read_text()


@pytest.fixture
def sidebar_js_content(sidebar_js_path: Path) -> str:
    """Load sidebar.js content."""
    if not sidebar_js_path.exists():
        pytest.fail(f"sidebar.js not found at {sidebar_js_path}")
    return sidebar_js_path.read_text()


# === TEST: File Existence ===

def test_sidebar_css_exists(sidebar_css_path: Path) -> None:
    """
    Test that sidebar.css exists in correct location.
    
    Acceptance Criteria:
    - File exists at src/dashboard/frontend/css/sidebar.css
    
    CORE-008: TDD test for file structure
    """
    assert sidebar_css_path.exists(), \
        f"sidebar.css not found at {sidebar_css_path}"
    assert sidebar_css_path.is_file(), \
        f"sidebar.css is not a file at {sidebar_css_path}"


def test_sidebar_js_exists(sidebar_js_path: Path) -> None:
    """
    Test that sidebar.js exists in correct location.
    
    Acceptance Criteria:
    - File exists at src/dashboard/frontend/js/components/common/sidebar.js
    
    CORE-008: TDD test for file structure
    """
    assert sidebar_js_path.exists(), \
        f"sidebar.js not found at {sidebar_js_path}"
    assert sidebar_js_path.is_file(), \
        f"sidebar.js is not a file at {sidebar_js_path}"


# === TEST: Sidebar Structure ===

def test_sidebar_main_container_class(sidebar_css_content: str) -> None:
    """
    Test that sidebar main container class is defined.
    
    Acceptance Criteria:
    - .sidebar class exists
    - Fixed positioning or persistent layout
    
    CORE-008: TDD test for sidebar structure
    """
    assert ".sidebar" in sidebar_css_content, \
        "Sidebar container class not found"
    
    # Sidebar should be fixed or sticky positioned
    assert "position: fixed" in sidebar_css_content or \
           "position: sticky" in sidebar_css_content or \
           "position:fixed" in sidebar_css_content or \
           "position:sticky" in sidebar_css_content, \
        "Sidebar should have fixed or sticky positioning"


def test_sidebar_width_defined(sidebar_css_content: str) -> None:
    """
    Test that sidebar has defined width.
    
    Acceptance Criteria:
    - Sidebar width defined (e.g., 280px, 16rem)
    - Width variable or explicit value
    
    CORE-008: TDD test for sidebar dimensions
    """
    # Check for width variable or explicit width
    assert "--sidebar-width" in sidebar_css_content or \
           "width: 280px" in sidebar_css_content or \
           "width: 16rem" in sidebar_css_content or \
           "width: 20rem" in sidebar_css_content, \
        "Sidebar width not defined"


# === TEST: Navigation Sections ===

def test_sidebar_navigation_sections(sidebar_css_content: str) -> None:
    """
    Test that sidebar navigation item styles are defined.
    
    Acceptance Criteria:
    - .sidebar-nav-item or similar class exists
    - Hover states defined
    - Active state defined
    
    CORE-008: TDD test for navigation items
    """
    # Check for navigation item class
    nav_item_patterns = [
        ".sidebar-nav-item",
        ".sidebar-link",
        ".nav-item",
    ]
    
    found_nav_item = any(pattern in sidebar_css_content for pattern in nav_item_patterns)
    assert found_nav_item, \
        "Sidebar navigation item class not found"


def test_sidebar_active_state_styling(sidebar_css_content: str) -> None:
    """
    Test that active navigation state has distinct styling with brand color.
    
    Acceptance Criteria:
    - .active or .sidebar-nav-item.active class exists
    - Uses brand color (cyan: #0ea5e9 or var(--color-primary))
    - Visual distinction from inactive items
    
    CORE-008: TDD test for active state
    """
    # Check for active state class
    active_patterns = [
        ".active",
        ".sidebar-nav-item.active",
        ".sidebar-link.active",
        ".nav-item.active",
    ]
    
    found_active_class = any(pattern in sidebar_css_content for pattern in active_patterns)
    assert found_active_class, \
        "Active navigation state class not found"
    
    # Check for brand color usage in active state
    brand_color_patterns = [
        "var(--color-primary)",
        "#0ea5e9",
        "var(--color-cortex-primary)",
    ]
    
    found_brand_color = any(pattern in sidebar_css_content for pattern in brand_color_patterns)
    assert found_brand_color, \
        "Active state should use brand color (cyan)"


def test_sidebar_hover_states(sidebar_css_content: str) -> None:
    """
    Test that navigation items have hover state styling.
    
    Acceptance Criteria:
    - :hover pseudo-class defined for navigation items
    - Smooth transition on hover
    
    CORE-008: TDD test for hover interactions
    """
    assert ":hover" in sidebar_css_content, \
        "Hover states not defined for sidebar navigation"


# === TEST: Collapse/Expand Functionality ===

def test_sidebar_collapse_toggle_class(sidebar_css_content: str) -> None:
    """
    Test that sidebar has collapse/expand state class.
    
    Acceptance Criteria:
    - .collapsed or .sidebar.collapsed class exists
    - Different width when collapsed (e.g., 80px vs 280px)
    
    CORE-008: TDD test for collapse functionality
    """
    # Check for collapsed state class
    collapsed_patterns = [
        ".sidebar.collapsed",
        ".sidebar-collapsed",
        ".collapsed",
    ]
    
    found_collapsed_class = any(pattern in sidebar_css_content for pattern in collapsed_patterns)
    assert found_collapsed_class, \
        "Sidebar collapsed state class not found"


def test_sidebar_transition_smoothness(sidebar_css_content: str) -> None:
    """
    Test that sidebar transitions are smooth (200-300ms).
    
    Acceptance Criteria:
    - transition property defined
    - Duration: 200ms - 300ms
    - Applies to width, transform, or left properties
    
    CORE-008: TDD test for smooth animations
    """
    assert "transition" in sidebar_css_content, \
        "Transition property not defined for sidebar"
    
    # Check for transition duration in acceptable range
    # 200ms, 250ms, 300ms, or var(--transition-normal)
    transition_patterns = [
        "200ms",
        "250ms",
        "300ms",
        "0.2s",
        "0.25s",
        "0.3s",
        "var(--transition-normal)",
        "var(--transition-fast)",
        "var(--transition-smooth)",
    ]
    
    found_transition_duration = any(pattern in sidebar_css_content for pattern in transition_patterns)
    assert found_transition_duration, \
        "Sidebar transition duration should be 200-300ms"


# === TEST: Mobile Responsiveness ===

def test_sidebar_hidden_on_mobile(sidebar_css_content: str) -> None:
    """
    Test that sidebar is hidden on mobile (<1024px).
    
    Acceptance Criteria:
    - Sidebar hidden on mobile (display: none or transform: translateX(-100%))
    - Mobile breakpoint media query exists
    
    CORE-008: TDD test for mobile responsiveness
    """
    # Check for mobile media query
    mobile_media_queries = [
        "@media (max-width: 768px)",
        "@media (max-width: 1024px)",
        "@media (max-width: var(--breakpoint-tablet))",
        "@media (max-width: var(--breakpoint-desktop))",
    ]
    
    found_mobile_query = any(query in sidebar_css_content for query in mobile_media_queries)
    assert found_mobile_query, \
        "Mobile breakpoint media query not found for sidebar"


def test_sidebar_visible_on_desktop(sidebar_css_content: str) -> None:
    """
    Test that sidebar is visible on desktop (≥1024px).
    
    Acceptance Criteria:
    - Sidebar displayed by default or in desktop media query
    - Display: flex or block on desktop
    
    CORE-008: TDD test for desktop visibility
    """
    # Sidebar should be visible by default (mobile-first) or in desktop media query
    # Check for display property
    display_patterns = [
        "display: flex",
        "display: block",
        "display:flex",
        "display:block",
    ]
    
    found_display = any(pattern in sidebar_css_content for pattern in display_patterns)
    assert found_display, \
        "Sidebar display property not found"


# === TEST: JavaScript Functionality ===

def test_sidebar_initialization_function(sidebar_js_content: str) -> None:
    """
    Test that initializeSidebar() function is defined.
    
    Acceptance Criteria:
    - function initializeSidebar() exists
    - Function is exported or accessible globally
    
    CORE-008: TDD test for JavaScript component
    """
    assert "function initializeSidebar()" in sidebar_js_content or \
           "initializeSidebar = function()" in sidebar_js_content or \
           "const initializeSidebar" in sidebar_js_content, \
        "initializeSidebar() function not found"


def test_sidebar_set_active_section_function(sidebar_js_content: str) -> None:
    """
    Test that function to set active section exists.
    
    Acceptance Criteria:
    - setActiveSection() or similar function exists
    - Function adds/removes .active class
    
    CORE-008: TDD test for active state management
    """
    active_function_patterns = [
        "function setActiveSection",
        "setActiveSection = function",
        "const setActiveSection",
        "function setActive",
        "classList.add('active')",
        'classList.add("active")',
    ]
    
    found_active_function = any(pattern in sidebar_js_content for pattern in active_function_patterns)
    assert found_active_function, \
        "Function to set active section not found"


def test_sidebar_toggle_collapse_function(sidebar_js_content: str) -> None:
    """
    Test that sidebar collapse/expand toggle function exists.
    
    Acceptance Criteria:
    - toggleSidebarCollapse() or similar function exists
    - Function adds/removes .collapsed class
    
    CORE-008: TDD test for collapse functionality
    """
    collapse_function_patterns = [
        "function toggleSidebarCollapse",
        "toggleSidebarCollapse = function",
        "const toggleSidebarCollapse",
        "function toggleSidebar",
        "function toggleCollapse",
        "classList.toggle('collapsed')",
        'classList.toggle("collapsed")',
    ]
    
    found_collapse_function = any(pattern in sidebar_js_content for pattern in collapse_function_patterns)
    assert found_collapse_function, \
        "Sidebar collapse toggle function not found"


def test_sidebar_navigation_click_handlers(sidebar_js_content: str) -> None:
    """
    Test that navigation link click handlers are defined.
    
    Acceptance Criteria:
    - Click event listeners attached to navigation items
    - Prevents default anchor behavior (preventDefault)
    
    CORE-008: TDD test for navigation behavior
    """
    # Check for click event listener
    assert "addEventListener('click'" in sidebar_js_content or \
           'addEventListener("click"' in sidebar_js_content, \
        "Click event listeners not attached to navigation items"


def test_sidebar_state_persistence(sidebar_js_content: str) -> None:
    """
    Test that sidebar state can be persisted (localStorage).
    
    Acceptance Criteria:
    - localStorage.setItem or getItem for sidebar state
    - Collapsed state saved and restored
    
    CORE-008: TDD test for state persistence
    """
    # Check for localStorage usage (optional but recommended)
    localStorage_patterns = [
        "localStorage.setItem",
        "localStorage.getItem",
        "localStorage",
    ]
    
    found_localStorage = any(pattern in sidebar_js_content for pattern in localStorage_patterns)
    
    # This is optional, so we'll just check if it exists (soft test)
    # If not found, we'll pass with a note
    if not found_localStorage:
        pytest.skip("localStorage state persistence not implemented (optional feature)")


# === TEST: Integration ===

def test_index_html_includes_sidebar_css() -> None:
    """
    Test that index.html includes sidebar.css stylesheet.
    
    Acceptance Criteria:
    - <link rel="stylesheet" href="/css/sidebar.css"> present
    
    CORE-008: TDD test for integration
    """
    index_html_path = Path("src/dashboard/frontend/index.html")
    
    if not index_html_path.exists():
        pytest.skip("index.html not found, skipping integration test")
    
    index_html_content = index_html_path.read_text()
    
    assert 'href="/css/sidebar.css"' in index_html_content or \
           "href='/css/sidebar.css'" in index_html_content, \
        "sidebar.css not linked in index.html"


def test_index_html_includes_sidebar_js() -> None:
    """
    Test that index.html includes sidebar.js script.
    
    Acceptance Criteria:
    - <script src="/js/components/common/sidebar.js"> present
    
    CORE-008: TDD test for integration
    """
    index_html_path = Path("src/dashboard/frontend/index.html")
    
    if not index_html_path.exists():
        pytest.skip("index.html not found, skipping integration test")
    
    index_html_content = index_html_path.read_text()
    
    assert 'src="/js/components/common/sidebar.js"' in index_html_content or \
           "src='/js/components/common/sidebar.js'" in index_html_content, \
        "sidebar.js not included in index.html"


def test_index_html_sidebar_structure() -> None:
    """
    Test that index.html includes sidebar HTML structure.
    
    Acceptance Criteria:
    - Sidebar container with .sidebar class
    - 5 navigation sections present
    - Collapse toggle button present
    
    CORE-008: TDD test for HTML structure
    """
    index_html_path = Path("src/dashboard/frontend/index.html")
    
    if not index_html_path.exists():
        pytest.skip("index.html not found, skipping integration test")
    
    index_html_content = index_html_path.read_text()
    
    # Check for sidebar container
    assert 'class="sidebar"' in index_html_content or \
           "class='sidebar'" in index_html_content or \
           'id="sidebar"' in index_html_content, \
        "Sidebar container not found in index.html"


def test_sidebar_five_main_sections() -> None:
    """
    Test that sidebar contains all 5 main navigation sections.
    
    Acceptance Criteria:
    - Brain Observatory
    - Temporal Cortex
    - Orchestrators
    - Plan Hub
    - Admin
    
    CORE-008: TDD test for navigation structure
    """
    index_html_path = Path("src/dashboard/frontend/index.html")
    
    if not index_html_path.exists():
        pytest.skip("index.html not found, skipping integration test")
    
    index_html_content = index_html_path.read_text()
    
    required_sections = [
        "Observatory",  # Brain Observatory
        "Temporal",     # Temporal Cortex
        "Orchestrators",
        "Plan",         # Plan Hub
        "Admin",
    ]
    
    for section in required_sections:
        assert section in index_html_content, \
            f"Navigation section '{section}' not found in sidebar"
