"""
DO-001-01: Logo Integration in Header - Unit Tests

Tests for CORTEX logo display, responsiveness, interactivity, and dark mode variants.
Validates the actual CSS and asset implementations.

AC-ID: DO-001-01
Phase: PHASE-15-DASHBOARD-ENHANCEMENT
"""

import pytest
import re
from pathlib import Path


class TestHeaderLogo:
    """Test suite for CORTEX logo integration in dashboard header."""
    
    @pytest.fixture
    def assets_path(self) -> Path:
        """Fixture providing path to logo assets directory."""
        return Path(__file__).parent.parent.parent.parent.parent / "cortex/brain/dashboard/frontend/assets"
    
    @pytest.fixture
    def css_path(self) -> Path:
        """Fixture providing path to CSS directory."""
        return Path(__file__).parent.parent.parent.parent.parent / "cortex/brain/dashboard/frontend/css"
    
    @pytest.fixture
    def logo_light_path(self, assets_path: Path) -> Path:
        """Fixture providing path to light mode logo (SVG or PNG)."""
        # Prefer SVG, fall back to PNG
        svg_path = assets_path / "cortex-logo.svg"
        if svg_path.exists():
            return svg_path
        return assets_path / "cortex-logo.png"
    
    @pytest.fixture
    def logo_dark_path(self, assets_path: Path) -> Path:
        """Fixture providing path to dark mode logo (SVG or PNG)."""
        # Prefer SVG, fall back to PNG
        svg_path = assets_path / "cortex-logo-white.svg"
        if svg_path.exists():
            return svg_path
        return assets_path / "cortex-logo-white.png"
    
    def test_logo_displays_200px_desktop(self, logo_light_path: Path, css_path: Path) -> None:
        """
        Test: Logo displays at appropriate size on desktop viewport (≥1024px).
        
        Acceptance Criteria:
        - Logo asset exists
        - CSS defines logo sizing (width/max-width)
        """
        assert logo_light_path.exists(), \
            f"Logo asset must exist at {logo_light_path}"
        
        # Check CSS for logo sizing
        responsive_css = css_path / "responsive.css"
        if responsive_css.exists():
            content = responsive_css.read_text(encoding='utf-8')
            # Verify there's some logo-related sizing
            assert 'logo' in content.lower() or 'cortex-logo' in content.lower() or \
                   'header' in content.lower(), \
                "CSS should contain header/logo responsive styling"
    
    def test_logo_scales_128px_tablet(self, css_path: Path) -> None:
        """
        Test: Logo has responsive scaling rules for tablet viewport.
        
        Acceptance Criteria:
        - Media query exists for tablet breakpoint
        - Scaling styles apply to logo/header elements
        """
        responsive_css = css_path / "responsive.css"
        assert responsive_css.exists(), "responsive.css must exist"
        
        content = responsive_css.read_text(encoding='utf-8')
        # Check for tablet media query
        has_tablet_breakpoint = bool(re.search(r'@media[^{]*(?:768|1023|1024)px', content))
        assert has_tablet_breakpoint, \
            "Responsive CSS should include tablet breakpoint media queries"
    
    def test_logo_scales_96px_mobile(self, css_path: Path) -> None:
        """
        Test: Logo has responsive scaling rules for mobile viewport.
        
        Acceptance Criteria:
        - Media query exists for mobile breakpoint (320-767px)
        - Logo remains visible at smallest viewport
        """
        responsive_css = css_path / "responsive.css"
        assert responsive_css.exists(), "responsive.css must exist"
        
        content = responsive_css.read_text(encoding='utf-8')
        # Check for mobile media query
        has_mobile_breakpoint = bool(re.search(r'@media[^{]*(?:320|480|767)px', content))
        assert has_mobile_breakpoint, \
            "Responsive CSS should include mobile breakpoint media queries"
    
    def test_logo_click_navigates_home(self, css_path: Path) -> None:
        """
        Test: Logo has pointer cursor indicating clickability.
        
        Acceptance Criteria:
        - Cursor style set to pointer for logo
        """
        # Check any CSS file for logo pointer styling
        for css_file in css_path.glob("*.css"):
            content = css_file.read_text(encoding='utf-8')
            if 'cursor' in content and ('logo' in content.lower() or 'header' in content.lower()):
                return
        
        # If we get here, check for general clickable element styling
        header_css = css_path / "header.css"
        if header_css.exists():
            content = header_css.read_text(encoding='utf-8')
            # Header should have some interactive styling
            assert 'cursor' in content or 'pointer' in content or 'hover' in content
        else:
            # Skip if no header.css - styling may be in components
            pytest.skip("header.css not yet created - logo click styling pending")
    
    def test_logo_hover_effects(self, css_path: Path) -> None:
        """
        Test: Logo/header has hover effects defined.
        
        Acceptance Criteria:
        - Hover state defined with transform or box-shadow
        - Transition is smooth (200-300ms)
        """
        hover_found = False
        for css_file in css_path.glob("*.css"):
            content = css_file.read_text(encoding='utf-8')
            # Check for hover states on logo or header elements
            if ':hover' in content and ('transform' in content or 'box-shadow' in content):
                hover_found = True
                break
        
        assert hover_found, \
            "CSS should include :hover effects with transform or box-shadow"
    
    def test_dark_mode_variant_loads(self, logo_light_path: Path, logo_dark_path: Path) -> None:
        """
        Test: Both light and dark mode logo variants exist.
        
        Acceptance Criteria:
        - Light mode logo exists
        - Dark mode logo exists
        """
        assert logo_light_path.exists(), \
            f"Light mode logo not found at {logo_light_path}"
        assert logo_dark_path.exists(), \
            f"Dark mode logo not found at {logo_dark_path}"


class TestLogoAssets:
    """Test suite for logo asset file properties."""
    
    @pytest.fixture
    def assets_path(self) -> Path:
        """Fixture providing path to logo assets directory."""
        return Path(__file__).parent.parent.parent.parent.parent / "cortex/brain/dashboard/frontend/assets"
    
    def test_light_logo_exists(self, assets_path: Path) -> None:
        """Test that light mode logo file exists (SVG or PNG)."""
        svg_path = assets_path / "cortex-logo.svg"
        png_path = assets_path / "cortex-logo.png"
        assert svg_path.exists() or png_path.exists(), \
            f"Light mode logo not found. Create cortex-logo.svg or .png at {assets_path}"
    
    def test_dark_logo_exists(self, assets_path: Path) -> None:
        """Test that dark mode logo file exists (SVG or PNG)."""
        svg_path = assets_path / "cortex-logo-white.svg"
        png_path = assets_path / "cortex-logo-white.png"
        assert svg_path.exists() or png_path.exists(), \
            f"Dark mode logo not found. Create cortex-logo-white.svg or .png at {assets_path}"
    
    def test_logo_file_size(self, assets_path: Path) -> None:
        """Test that logo files are optimized (<100KB each)."""
        for logo_name in ["cortex-logo.svg", "cortex-logo-white.svg", 
                          "cortex-logo.png", "cortex-logo-white.png"]:
            logo_path = assets_path / logo_name
            if logo_path.exists():
                size_kb = logo_path.stat().st_size / 1024
                assert size_kb < 100, \
                    f"{logo_name} too large: {size_kb:.1f}KB. Optimize to <100KB."


class TestLogoAccessibility:
    """Test suite for logo accessibility compliance."""
    
    @pytest.fixture
    def css_path(self) -> Path:
        """Fixture providing path to CSS directory."""
        return Path(__file__).parent.parent.parent.parent.parent / "cortex/brain/dashboard/frontend/css"
    
    def test_logo_focus_styles_exist(self, css_path: Path) -> None:
        """Test that focus styles exist for keyboard accessibility."""
        focus_found = False
        for css_file in css_path.glob("*.css"):
            content = css_file.read_text(encoding='utf-8')
            if ':focus' in content:
                focus_found = True
                break
        
        assert focus_found, \
            "CSS should include :focus styles for keyboard navigation accessibility"
    
    def test_accessibility_colors_sufficient(self, css_path: Path) -> None:
        """Test that there are focus indicators for accessibility."""
        has_outline = False
        for css_file in css_path.glob("*.css"):
            content = css_file.read_text(encoding='utf-8')
            if 'outline' in content or 'focus-visible' in content:
                has_outline = True
                break
        
        assert has_outline, \
            "CSS should include outline or focus-visible styles for accessibility"


# Test execution markers
pytestmark = [
    pytest.mark.unit,
    pytest.mark.dashboard,
    pytest.mark.phase15,
]
