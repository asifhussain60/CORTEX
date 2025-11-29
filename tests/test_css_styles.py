"""
Tests to verify CSS styles are correctly applied to the documentation site.

This test suite validates:
1. Custom CSS file exists in built site
2. Color styles are present in the CSS
3. Navigation styles are defined
4. Main title gradient is configured
5. Code block styles use dark grey
"""

import pytest
from pathlib import Path
import re


class TestCSSStyles:
    """Test suite for verifying CSS styles in the built documentation."""
    
    @pytest.fixture
    def site_css_path(self):
        """Path to the built custom CSS file."""
        return Path("d:/PROJECTS/CORTEX/site/stylesheets/custom.css")
    
    @pytest.fixture
    def css_content(self, site_css_path):
        """Load the CSS file content."""
        if not site_css_path.exists():
            pytest.skip(f"CSS file not found: {site_css_path}. Run 'mkdocs build' first.")
        return site_css_path.read_text(encoding='utf-8')
    
    def test_css_file_exists(self, site_css_path):
        """Verify custom.css was copied to the built site."""
        if not site_css_path.exists():
            pytest.skip(f"CSS file not found at {site_css_path}. Run 'mkdocs build'.")
        assert site_css_path.exists()
    
    def test_sidebar_gradient_background(self, css_content):
        """Verify sidebar has gradient background."""
        pattern = r'\.md-sidebar--primary\s*\{[^}]*background:\s*linear-gradient\(180deg,\s*#F8F9FA'
        assert re.search(pattern, css_content, re.DOTALL), \
            "Sidebar gradient background not found"
    
    def test_navigation_link_color(self, css_content):
        """Verify navigation links use dark grey (#374151)."""
        pattern = r'\.md-nav__link\s*\{[^}]*color:\s*#374151\s*!important'
        assert re.search(pattern, css_content, re.DOTALL), \
            "Navigation link color #374151 not found"
    
    def test_active_link_purple_gradient(self, css_content):
        """Verify active navigation items have purple gradient background."""
        pattern = r'\.md-nav__link--active\s*\{[^}]*background:\s*linear-gradient.*99,\s*102,\s*241'
        assert re.search(pattern, css_content, re.DOTALL), \
            "Active link purple gradient not found"
    
    def test_main_title_gradient(self, css_content):
        """Verify main title has colorful gradient."""
        # Check for gradient text effect
        pattern = r'background:\s*linear-gradient\(135deg,\s*var\(--cortex-primary\),\s*var\(--cortex-accent\),\s*#A855F7\)'
        assert re.search(pattern, css_content), \
            "Main title gradient not found"
        
        # Check for background-clip for text gradient
        assert '-webkit-background-clip: text' in css_content, \
            "Text gradient clip not found"
    
    def test_brain_emoji_in_title(self, css_content):
        """Verify brain emoji is added to title."""
        pattern = r'\.md-typeset h1:first-of-type::before\s*\{[^}]*content:\s*"🧠\s*"'
        assert re.search(pattern, css_content, re.DOTALL), \
            "Brain emoji for title not found"
    
    def test_code_block_dark_grey(self, css_content):
        """Verify code blocks use dark grey (#1F2937) instead of black."""
        pattern = r'background-color:\s*#1F2937\s*!important'
        matches = re.findall(pattern, css_content)
        assert len(matches) >= 3, \
            f"Expected at least 3 instances of dark grey code blocks, found {len(matches)}"
    
    def test_hover_effect_purple(self, css_content):
        """Verify hover effects use purple accent color."""
        pattern = r'\.md-nav__link:hover\s*\{[^}]*background:\s*linear-gradient.*139,\s*92,\s*246'
        assert re.search(pattern, css_content, re.DOTALL), \
            "Hover effect purple gradient not found"
    
    def test_navigation_title_style(self, css_content):
        """Verify navigation titles have colorful styling."""
        pattern = r'\.md-nav__title\s*\{[^}]*color:\s*var\(--cortex-primary\)\s*!important'
        assert re.search(pattern, css_content, re.DOTALL), \
            "Navigation title color not found"
    
    def test_no_pure_black_in_navigation(self, css_content):
        """Verify navigation doesn't use pure black (#000000)."""
        # Extract navigation section
        nav_section_match = re.search(
            r'/\*.*NAVIGATION.*\*/.*?/\*.*?HOME PAGE',
            css_content,
            re.DOTALL | re.IGNORECASE
        )
        
        if nav_section_match:
            nav_section = nav_section_match.group(0)
            # Check for pure black in color properties (but allow in other contexts)
            pure_black_pattern = r'color:\s*#000000\s*!important'
            assert not re.search(pure_black_pattern, nav_section), \
                "Found pure black (#000000) in navigation section - should use dark grey"


class TestHTMLIntegration:
    """Test suite for verifying HTML includes CSS correctly."""
    
    @pytest.fixture
    def index_html_path(self):
        """Path to the built index.html file."""
        return Path("d:/PROJECTS/CORTEX/site/index.html")
    
    @pytest.fixture
    def html_content(self, index_html_path):
        """Load the HTML file content."""
        if not index_html_path.exists():
            pytest.skip(f"HTML file not found: {index_html_path}. Run 'mkdocs build' first.")
        return index_html_path.read_text(encoding='utf-8')
    
    def test_html_file_exists(self, index_html_path):
        """Verify index.html was built."""
        if not index_html_path.exists():
            pytest.skip(f"HTML file not found at {index_html_path}. Run 'mkdocs build'.")
        assert index_html_path.exists()
    
    def test_custom_css_linked(self, html_content):
        """Verify custom.css is linked in the HTML."""
        pattern = r'<link[^>]*href="[^"]*stylesheets/custom\.css"[^>]*>'
        assert re.search(pattern, html_content), \
            "custom.css not linked in HTML"
    
    def test_google_fonts_loaded(self, html_content):
        """Verify Google Fonts are loaded for ancient rules styling."""
        assert 'fonts.googleapis.com' in html_content, \
            "Google Fonts not loaded"
        
        # Check for Cinzel font
        assert 'Cinzel' in html_content or 'cinzel' in html_content.lower(), \
            "Cinzel font not loaded"


class TestColorConsistency:
    """Test suite for verifying color consistency across the site."""
    
    @pytest.fixture
    def css_content(self):
        """Load the CSS file content."""
        css_path = Path("d:/PROJECTS/CORTEX/site/stylesheets/custom.css")
        if not css_path.exists():
            pytest.skip("CSS file not found. Run 'mkdocs build' first.")
        return css_path.read_text(encoding='utf-8')
    
    def test_cortex_primary_color_defined(self, css_content):
        """Verify CORTEX primary brand color is defined."""
        pattern = r'--cortex-primary:\s*#6366F1'
        assert re.search(pattern, css_content), \
            "CORTEX primary color not defined in CSS variables"
    
    def test_cortex_accent_color_defined(self, css_content):
        """Verify CORTEX accent color is defined."""
        pattern = r'--cortex-accent:\s*#8B5CF6'
        assert re.search(pattern, css_content), \
            "CORTEX accent color not defined in CSS variables"
    
    def test_color_variables_used(self, css_content):
        """Verify CSS color variables are actually used."""
        # Count usage of color variables
        primary_usage = len(re.findall(r'var\(--cortex-primary\)', css_content))
        accent_usage = len(re.findall(r'var\(--cortex-accent\)', css_content))
        
        assert primary_usage >= 5, \
            f"Expected at least 5 uses of --cortex-primary, found {primary_usage}"
        assert accent_usage >= 3, \
            f"Expected at least 3 uses of --cortex-accent, found {accent_usage}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
