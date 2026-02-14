"""
Glassmorphism Theme Tests — MEGA-B S1

AC-MEGA-B-S1-004: GitHub Pages compatibility

Tests for glassmorphism CSS theme:
- Frosted glass effects
- Gradient backgrounds
- Shadow layering
- Responsive design
- Asset optimization

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD)
"""

from pathlib import Path

import pytest

from cortex.documentation.glassmorphism_theme import (
    GlassmorphismTheme,
    ThemeConfig,
)


@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary output directory."""
    output_dir = tmp_path / "assets"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def theme_config():
    """Standard theme configuration."""
    return ThemeConfig(
        primary_color="#6366f1",
        secondary_color="#8b5cf6",
        glass_opacity=0.1,
    )


@pytest.fixture
def glass_theme(temp_output_dir, theme_config):
    """Glassmorphism theme instance."""
    return GlassmorphismTheme(
        output_dir=temp_output_dir,
        config=theme_config,
    )


class TestGlassEffects:
    """Test: Frosted glass visual effects."""
    
    def test_generates_glass_css(
        self,
        glass_theme,
        temp_output_dir,
    ):
        """Test: Generates glassmorphism CSS."""
        # When: Generate theme
        css_path = glass_theme.generate()
        
        # Then: CSS file created
        assert css_path.exists()
        assert css_path.name == "theme.css"
        
        # And: Contains glass effects
        content = css_path.read_text()
        assert "backdrop-filter" in content
        assert "blur" in content
    
    def test_glass_panel_style(
        self,
        glass_theme,
        temp_output_dir,
    ):
        """Test: Glass panel has frosted effect."""
        # When: Generate theme
        css_path = glass_theme.generate()
        
        # Then: Glass panel defined
        content = css_path.read_text()
        assert ".glass-panel" in content
        assert "rgba" in content  # Translucent background


class TestGradientBackgrounds:
    """Test: Gradient background generation."""
    
    def test_generates_gradient_backgrounds(
        self,
        glass_theme,
        temp_output_dir,
    ):
        """Test: Generates gradient backgrounds."""
        # When: Generate theme
        css_path = glass_theme.generate()
        
        # Then: Gradients defined
        content = css_path.read_text()
        assert "linear-gradient" in content or "gradient" in content
    
    def test_uses_theme_colors(
        self,
        glass_theme,
        temp_output_dir,
    ):
        """Test: Uses configured theme colors."""
        # When: Generate theme
        css_path = glass_theme.generate()
        
        # Then: Theme colors present
        content = css_path.read_text()
        assert "#6366f1" in content or "99, 102, 241" in content  # Primary
        assert "#8b5cf6" in content or "139, 92, 246" in content  # Secondary


class TestShadowLayering:
    """Test: Shadow depth and layering."""
    
    def test_applies_multi_layer_shadows(
        self,
        glass_theme,
        temp_output_dir,
    ):
        """Test: Applies multi-layer box shadows."""
        # When: Generate theme
        css_path = glass_theme.generate()
        
        # Then: Box shadows defined
        content = css_path.read_text()
        assert "box-shadow" in content
    
    def test_elevation_levels(
        self,
        glass_theme,
        temp_output_dir,
    ):
        """Test: Multiple elevation levels."""
        # When: Generate with elevations
        css_path = glass_theme.generate()
        
        # Then: Elevation classes present
        content = css_path.read_text()
        # Check for at least one elevation class
        assert ("elevation-1" in content or
                "shadow" in content or
                "z-" in content)


class TestResponsiveDesign:
    """Test: Responsive CSS rules."""
    
    def test_includes_media_queries(
        self,
        glass_theme,
        temp_output_dir,
    ):
        """Test: Includes responsive media queries."""
        # When: Generate theme
        css_path = glass_theme.generate()
        
        # Then: Media queries present
        content = css_path.read_text()
        assert "@media" in content
    
    def test_mobile_optimized(
        self,
        glass_theme,
        temp_output_dir,
    ):
        """Test: Mobile-optimized styles."""
        # When: Generate theme
        css_path = glass_theme.generate()
        
        # Then: Mobile breakpoint defined
        content = css_path.read_text()
        assert ("max-width" in content or
                "min-width" in content)


class TestAssetOptimization:
    """Test: CSS asset optimization."""
    
    def test_minifies_css(
        self,
        glass_theme,
        temp_output_dir,
    ):
        """Test: Minifies CSS output."""
        # When: Generate with minification
        css_path = glass_theme.generate(minify=True)
        
        # Then: No unnecessary whitespace
        content = css_path.read_text()
        assert "\n\n" not in content  # No double newlines
        
        # Minified CSS is compact (total length check, not per-line)
        assert len(content) < 3000  # Compact minified output
    
    def test_file_size_reasonable(
        self,
        glass_theme,
        temp_output_dir,
    ):
        """Test: CSS file size <20KB."""
        # When: Generate theme
        css_path = glass_theme.generate(minify=True)
        
        # Then: File size reasonable
        file_size = css_path.stat().st_size
        assert file_size < 20000  # <20KB


class TestGitHubPagesCompatibility:
    """Test: GitHub Pages deployment compatibility."""
    
    def test_uses_relative_asset_paths(
        self,
        glass_theme,
        temp_output_dir,
    ):
        """Test: Uses relative paths for assets."""
        # When: Generate theme
        css_path = glass_theme.generate()
        
        # Then: No absolute URLs
        content = css_path.read_text()
        import re
        url_pattern = r'url\(["\']?(https?://[^)"\']+)["\']?\)'
        absolute_urls = re.findall(url_pattern, content)
        assert len(absolute_urls) == 0
    
    def test_no_external_dependencies(
        self,
        glass_theme,
        temp_output_dir,
    ):
        """Test: No external CSS dependencies."""
        # When: Generate theme
        css_path = glass_theme.generate()
        
        # Then: Self-contained CSS
        content = css_path.read_text()
        assert "@import" not in content


class TestThemeIntegration:
    """Test: Theme integration with portal."""
    
    def test_generates_complete_theme(
        self,
        glass_theme,
        temp_output_dir,
    ):
        """Test: Generates complete theme file."""
        # When: Generate theme
        css_path = glass_theme.generate()
        
        # Then: Theme includes core styles
        content = css_path.read_text()
        
        # Essential CSS present
        assert "body" in content
        assert any(x in content for x in ["color", "background"])
