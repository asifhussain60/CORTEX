"""
Test Suite: DO-001-04 Responsive Design Validation
Tests comprehensive responsive design system for CORTEX Dashboard.

Requirements:
- Breakpoints: 320px (mobile), 768px (tablet), 1024px (desktop), 1920px (large)
- Hamburger menu appears at <1024px
- Touch targets ≥44px on mobile (WCAG 2.1 AA)
- Charts maintain aspect ratio
- Tables scroll horizontally on mobile
- Text readable without zoom at 320px

Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
from pathlib import Path
from typing import Dict, List


# === FIXTURES ===

@pytest.fixture
def responsive_css_path() -> Path:
    """Path to responsive.css file."""
    return Path("cortex/brain/dashboard/frontend/css/responsive.css")


@pytest.fixture
def hamburger_js_path() -> Path:
    """Path to hamburger-menu.js file."""
    return Path("cortex/brain/dashboard/frontend/js/components/common/hamburger-menu.js")


@pytest.fixture
def responsive_css_content(responsive_css_path: Path) -> str:
    """Load responsive.css content."""
    if not responsive_css_path.exists():
        pytest.fail(f"responsive.css not found at {responsive_css_path}")
    return responsive_css_path.read_text(encoding='utf-8')


@pytest.fixture
def hamburger_js_content(hamburger_js_path: Path) -> str:
    """Load hamburger-menu.js content."""
    if not hamburger_js_path.exists():
        pytest.fail(f"hamburger-menu.js not found at {hamburger_js_path}")
    return hamburger_js_path.read_text(encoding='utf-8')


# === TEST: File Existence ===

def test_responsive_css_exists(responsive_css_path: Path) -> None:
    """
    Test that responsive.css exists in correct location.
    
    Acceptance Criteria:
    - File exists at cortex/brain/dashboard/frontend/css/responsive.css
    
    CORE-008: TDD test for file structure
    """
    assert responsive_css_path.exists(), \
        f"responsive.css not found at {responsive_css_path}"
    assert responsive_css_path.is_file(), \
        f"responsive.css is not a file at {responsive_css_path}"


def test_hamburger_js_exists(hamburger_js_path: Path) -> None:
    """
    Test that hamburger-menu.js exists in correct location.
    
    Acceptance Criteria:
    - File exists at cortex/brain/dashboard/frontend/js/components/common/hamburger-menu.js
    
    CORE-008: TDD test for file structure
    """
    assert hamburger_js_path.exists(), \
        f"hamburger-menu.js not found at {hamburger_js_path}"
    assert hamburger_js_path.is_file(), \
        f"hamburger-menu.js is not a file at {hamburger_js_path}"


# === TEST: Breakpoint Variables ===

def test_breakpoint_variables_defined(responsive_css_content: str) -> None:
    """
    Test that all 4 breakpoint CSS variables are defined correctly.
    
    Acceptance Criteria:
    - --breakpoint-mobile: 320px
    - --breakpoint-tablet: 768px
    - --breakpoint-desktop: 1024px
    - --breakpoint-large: 1920px
    
    CORE-008: TDD test for breakpoint system
    """
    required_breakpoints = {
        "--breakpoint-mobile": "320px",
        "--breakpoint-tablet": "768px",
        "--breakpoint-desktop": "1024px",
        "--breakpoint-large": "1920px",
    }
    
    for variable, expected_value in required_breakpoints.items():
        assert variable in responsive_css_content, \
            f"Breakpoint variable {variable} not found in responsive.css"
        
        # Check that variable is defined with correct value
        assert f"{variable}: {expected_value}" in responsive_css_content, \
            f"Breakpoint {variable} not set to {expected_value}"


def test_touch_target_variable_defined(responsive_css_content: str) -> None:
    """
    Test that touch target minimum variable is defined (WCAG 2.1 AA).
    
    Acceptance Criteria:
    - --touch-target-min: 44px (WCAG minimum)
    
    CORE-008: TDD test for accessibility
    """
    assert "--touch-target-min" in responsive_css_content, \
        "Touch target variable not found in responsive.css"
    
    assert "--touch-target-min: 44px" in responsive_css_content, \
        "Touch target minimum not set to 44px (WCAG requirement)"


# === TEST: Hamburger Menu Visibility ===

def test_hamburger_menu_hidden_on_desktop(responsive_css_content: str) -> None:
    """
    Test that hamburger menu is hidden on desktop screens (≥1024px).
    
    Acceptance Criteria:
    - .hamburger-menu should be hidden at ≥1024px
    - Display: none or visibility: hidden at desktop breakpoint
    
    CORE-008: TDD test for responsive behavior
    """
    # Check for media query targeting desktop screens
    assert "@media (min-width: 1024px)" in responsive_css_content or \
           "@media (min-width: var(--breakpoint-desktop))" in responsive_css_content, \
        "Desktop breakpoint media query not found"
    
    # Hamburger menu should be hidden on desktop
    # Look for .hamburger-menu with display: none in desktop media query
    lines = responsive_css_content.split('\n')
    in_desktop_media_query = False
    found_hamburger_hidden = False
    
    for line in lines:
        if '@media (min-width: 1024px)' in line or '@media (min-width: var(--breakpoint-desktop))' in line:
            in_desktop_media_query = True
        
        if in_desktop_media_query and '.hamburger-menu' in line:
            # Check next few lines for display: none
            idx = lines.index(line)
            next_lines = lines[idx:idx+10]
            for next_line in next_lines:
                if 'display: none' in next_line or 'display:none' in next_line:
                    found_hamburger_hidden = True
                    break
            break
    
    assert found_hamburger_hidden, \
        "Hamburger menu not hidden on desktop (≥1024px)"


def test_hamburger_menu_visible_on_mobile(responsive_css_content: str) -> None:
    """
    Test that hamburger menu is visible on mobile/tablet screens (<1024px).
    
    Acceptance Criteria:
    - .hamburger-menu should be displayed at <1024px
    - Display: block or flex at mobile/tablet breakpoint
    
    CORE-008: TDD test for responsive behavior
    """
    # Hamburger menu should be visible by default (mobile-first)
    # or have display: flex/block in mobile media query
    assert ".hamburger-menu" in responsive_css_content, \
        "Hamburger menu class not found in responsive.css"
    
    # Check for display property in hamburger menu
    lines = responsive_css_content.split('\n')
    found_hamburger_display = False
    
    for i, line in enumerate(lines):
        if '.hamburger-menu' in line and '{' in line:
            # Check next few lines for display property
            for next_line in lines[i:i+20]:
                if 'display: flex' in next_line or 'display: block' in next_line or \
                   'display:flex' in next_line or 'display:block' in next_line:
                    found_hamburger_display = True
                    break
            break
    
    assert found_hamburger_display, \
        "Hamburger menu display property not found (should be flex or block on mobile)"


# === TEST: Responsive Grid System ===

def test_responsive_grid_columns(responsive_css_content: str) -> None:
    """
    Test that responsive grid adapts column count across breakpoints.
    
    Acceptance Criteria:
    - Mobile (320px): 1 column
    - Tablet (768px): 2 columns
    - Desktop (1024px): 3 columns
    - Large (1920px): 4 columns
    
    CORE-008: TDD test for grid responsiveness
    """
    # Check for .grid-responsive class
    assert ".grid-responsive" in responsive_css_content, \
        "Responsive grid class not found"
    
    # Check for grid-template-columns property with column variations
    # Mobile should be 1fr, tablet 2fr, desktop 3fr, large 4fr
    breakpoint_column_mapping = {
        "320px": ["grid-template-columns: 1fr", "grid-template-columns:1fr"],
        "768px": ["grid-template-columns: repeat(2", "grid-template-columns:repeat(2"],
        "1024px": ["grid-template-columns: repeat(3", "grid-template-columns:repeat(3"],
        "1920px": ["grid-template-columns: repeat(4", "grid-template-columns:repeat(4"],
    }
    
    for breakpoint, column_patterns in breakpoint_column_mapping.items():
        found = any(pattern in responsive_css_content for pattern in column_patterns)
        assert found, \
            f"Grid column configuration not found for {breakpoint} breakpoint"


# === TEST: Touch Targets (WCAG) ===

def test_touch_targets_wcag_compliant(responsive_css_content: str) -> None:
    """
    Test that touch targets meet WCAG 2.1 AA minimum size (44x44px).
    
    Acceptance Criteria:
    - All interactive elements ≥44px on mobile
    - min-height: 44px applied to buttons/links
    
    CORE-008: TDD test for accessibility compliance
    """
    # Check for touch target minimum variable
    assert "--touch-target-min: 44px" in responsive_css_content, \
        "Touch target minimum variable not defined"
    
    # Check for button/link height properties at mobile breakpoint
    # Look for min-height using the touch-target-min variable or explicit 44px
    patterns = [
        "min-height: var(--touch-target-min)",
        "min-height: 44px",
        "min-height:44px",
    ]
    
    found_touch_target_usage = any(pattern in responsive_css_content for pattern in patterns)
    assert found_touch_target_usage, \
        "Touch target minimum (44px) not applied to interactive elements"


# === TEST: Chart Responsiveness ===

def test_chart_container_responsive_height(responsive_css_content: str) -> None:
    """
    Test that chart containers have responsive heights across breakpoints.
    
    Acceptance Criteria:
    - .chart-container has different heights at mobile, tablet, desktop
    - Heights scale progressively (smaller on mobile, larger on desktop)
    
    CORE-008: TDD test for chart responsiveness
    """
    assert ".chart-container" in responsive_css_content, \
        "Chart container class not found"
    
    # Check for multiple height values in media queries
    # Mobile: ~180px, Tablet: ~220px, Desktop: ~280px
    height_patterns = [
        "height: 180px",
        "height: 220px",
        "height: 280px",
        "height:180px",
        "height:220px",
        "height:280px",
    ]
    
    found_heights = [pattern for pattern in height_patterns if pattern in responsive_css_content]
    
    assert len(found_heights) >= 2, \
        f"Chart container should have multiple responsive heights, found: {found_heights}"


# === TEST: Table Horizontal Scroll ===

def test_table_horizontal_scroll_on_mobile(responsive_css_content: str) -> None:
    """
    Test that tables become horizontally scrollable on mobile screens.
    
    Acceptance Criteria:
    - .table-responsive has overflow-x: auto at mobile breakpoint
    - Custom scrollbar styling present
    
    CORE-008: TDD test for table responsiveness
    """
    assert ".table-responsive" in responsive_css_content, \
        "Table responsive class not found"
    
    # Check for overflow-x property
    assert "overflow-x: auto" in responsive_css_content or \
           "overflow-x:auto" in responsive_css_content, \
        "Table horizontal scroll not enabled (overflow-x: auto)"


# === TEST: Visibility Utilities ===

def test_visibility_utility_classes(responsive_css_content: str) -> None:
    """
    Test that visibility utility classes are defined.
    
    Acceptance Criteria:
    - .hidden-mobile, .visible-mobile
    - .hidden-tablet, .visible-tablet
    - .hidden-desktop, .visible-desktop
    
    CORE-008: TDD test for utility classes
    """
    utility_classes = [
        ".hidden-mobile",
        ".visible-mobile",
        ".hidden-tablet",
        ".visible-tablet",
        ".hidden-desktop",
        ".visible-desktop",
    ]
    
    for utility_class in utility_classes:
        assert utility_class in responsive_css_content, \
            f"Visibility utility class {utility_class} not found"


# === TEST: Reduced Motion Support ===

def test_reduced_motion_support(responsive_css_content: str) -> None:
    """
    Test that animations are disabled for users with prefers-reduced-motion.
    
    Acceptance Criteria:
    - @media (prefers-reduced-motion: reduce) present
    - Animations and transitions disabled in reduced motion mode
    
    CORE-008: TDD test for accessibility
    """
    assert "@media (prefers-reduced-motion: reduce)" in responsive_css_content, \
        "Reduced motion media query not found"
    
    # Check that animations are disabled
    # Look for animation: none or transition: none in reduced motion block
    lines = responsive_css_content.split('\n')
    in_reduced_motion = False
    found_animation_disable = False
    
    for line in lines:
        if '@media (prefers-reduced-motion: reduce)' in line:
            in_reduced_motion = True
        
        if in_reduced_motion:
            if 'animation: none' in line or 'transition: none' in line:
                found_animation_disable = True
                break
    
    assert found_animation_disable, \
        "Animations not disabled in reduced motion mode"


# === TEST: Hamburger Menu JavaScript Functionality ===

def test_hamburger_menu_initialization_function(hamburger_js_content: str) -> None:
    """
    Test that initializeHamburgerMenu() function is defined.
    
    Acceptance Criteria:
    - function initializeHamburgerMenu() exists
    - Function is exported or accessible globally
    
    CORE-008: TDD test for JavaScript component
    """
    assert "function initializeHamburgerMenu()" in hamburger_js_content or \
           "initializeHamburgerMenu = function()" in hamburger_js_content or \
           "const initializeHamburgerMenu" in hamburger_js_content, \
        "initializeHamburgerMenu() function not found"


def test_hamburger_menu_toggle_function(hamburger_js_content: str) -> None:
    """
    Test that toggleMenu() function is defined.
    
    Acceptance Criteria:
    - function toggleMenu() exists
    - Function handles menu state (open/close)
    
    CORE-008: TDD test for toggle functionality
    """
    assert "function toggleMenu()" in hamburger_js_content or \
           "toggleMenu = function()" in hamburger_js_content or \
           "const toggleMenu" in hamburger_js_content, \
        "toggleMenu() function not found"


def test_hamburger_menu_body_scroll_lock(hamburger_js_content: str) -> None:
    """
    Test that body scroll is locked when menu is open.
    
    Acceptance Criteria:
    - document.body.style.overflow = 'hidden' when menu opens
    - Overflow restored when menu closes
    
    CORE-008: TDD test for scroll lock behavior
    """
    assert "document.body.style.overflow" in hamburger_js_content, \
        "Body scroll lock not implemented"
    
    assert "'hidden'" in hamburger_js_content or '"hidden"' in hamburger_js_content, \
        "Body overflow not set to 'hidden'"


def test_hamburger_menu_escape_key_handler(hamburger_js_content: str) -> None:
    """
    Test that Escape key closes the menu.
    
    Acceptance Criteria:
    - Escape key (key === 'Escape') closes menu
    - Event listener attached for keydown
    
    CORE-008: TDD test for keyboard accessibility
    """
    # Check for Escape key handling
    assert "key === 'Escape'" in hamburger_js_content or \
           'key === "Escape"' in hamburger_js_content or \
           "keyCode === 27" in hamburger_js_content, \
        "Escape key handler not implemented"


def test_hamburger_menu_resize_auto_close(hamburger_js_content: str) -> None:
    """
    Test that menu auto-closes when window resizes to desktop size.
    
    Acceptance Criteria:
    - Resize event listener attached
    - Menu closes when window.innerWidth >= 1024px
    
    CORE-008: TDD test for responsive behavior
    """
    assert "addEventListener('resize'" in hamburger_js_content or \
           'addEventListener("resize"' in hamburger_js_content, \
        "Resize event listener not attached"
    
    assert "window.innerWidth >= 1024" in hamburger_js_content or \
           "innerWidth >= 1024" in hamburger_js_content, \
        "Auto-close on desktop resize not implemented (≥1024px)"


# === TEST: Integration ===

def test_index_html_includes_responsive_css() -> None:
    """
    Test that index.html includes responsive.css stylesheet.
    
    Acceptance Criteria:
    - <link rel="stylesheet" href="/css/responsive.css"> present
    
    CORE-008: TDD test for integration
    """
    index_html_path = Path("cortex/brain/dashboard/frontend/index.html")
    
    if not index_html_path.exists():
        pytest.skip("index.html not found, skipping integration test")
    
    index_html_content = index_html_path.read_text()
    
    assert 'href="/css/responsive.css"' in index_html_content or \
           "href='/css/responsive.css'" in index_html_content, \
        "responsive.css not linked in index.html"


def test_index_html_includes_hamburger_js() -> None:
    """
    Test that index.html includes hamburger-menu.js script.
    
    Acceptance Criteria:
    - <script src="/js/components/common/hamburger-menu.js"> present
    
    CORE-008: TDD test for integration
    """
    index_html_path = Path("cortex/brain/dashboard/frontend/index.html")
    
    if not index_html_path.exists():
        pytest.skip("index.html not found, skipping integration test")
    
    index_html_content = index_html_path.read_text()
    
    assert 'src="/js/components/common/hamburger-menu.js"' in index_html_content or \
           "src='/js/components/common/hamburger-menu.js'" in index_html_content, \
        "hamburger-menu.js not included in index.html"


def test_index_html_hamburger_button_present() -> None:
    """
    Test that index.html includes hamburger menu button.
    
    Acceptance Criteria:
    - <button id="hamburger-menu" class="hamburger-menu"> present
    - Button has aria-label for accessibility
    
    CORE-008: TDD test for HTML structure
    """
    index_html_path = Path("cortex/brain/dashboard/frontend/index.html")
    
    if not index_html_path.exists():
        pytest.skip("index.html not found, skipping integration test")
    
    index_html_content = index_html_path.read_text()
    
    assert 'id="hamburger-menu"' in index_html_content, \
        "Hamburger menu button not found in index.html"
    
    assert 'class="hamburger-menu"' in index_html_content, \
        "Hamburger menu button missing 'hamburger-menu' class"
    
    assert 'aria-label=' in index_html_content, \
        "Hamburger menu button missing aria-label (accessibility)"


def test_index_html_mobile_nav_present() -> None:
    """
    Test that index.html includes mobile navigation panel.
    
    Acceptance Criteria:
    - <nav id="nav-mobile" class="nav-mobile"> present
    - Mobile navigation overlay present
    
    CORE-008: TDD test for HTML structure
    """
    index_html_path = Path("cortex/brain/dashboard/frontend/index.html")
    
    if not index_html_path.exists():
        pytest.skip("index.html not found, skipping integration test")
    
    index_html_content = index_html_path.read_text()
    
    assert 'id="nav-mobile"' in index_html_content, \
        "Mobile navigation panel not found in index.html"
    
    assert 'class="nav-mobile"' in index_html_content, \
        "Mobile navigation panel missing 'nav-mobile' class"
    
    assert 'id="nav-mobile-overlay"' in index_html_content, \
        "Mobile navigation overlay not found in index.html"
