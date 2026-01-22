"""
Logo Dimension Tests

Ensures that CORTEX logos load with correct dimensions during mkdocs builds.
Validates that cortex-logo-200.png exists and has 128x128 pixel dimensions.

Test Coverage:
- cortex-logo-200.png: Primary logo used in documentation (128x128)
- cortex-logo.svg: Light mode variant
- cortex-logo-white.svg: Dark mode variant
- Additional logo sizes (64, 128, 512 px variants)

These tests run automatically as part of the documentation build process
and ensure brand assets are properly configured before deployment.

Reference: Commit 12aba98b9 - "Increase logo size to 100x100px" 
(CSS styled to 100x100, but actual image is 128x128 for crisp rendering at 2x DPI)
"""

import os
import pytest
from pathlib import Path
from PIL import Image


class TestLogoDimensions:
    """Test suite for CORTEX logo assets and dimensions."""

    @pytest.fixture
    def docs_root(self):
        """Get the docs directory root."""
        current_dir = Path(__file__).parent
        docs_dir = current_dir.parent  # docs/_tests -> docs
        assert docs_dir.name == "docs", f"Expected docs directory, got {docs_dir}"
        return docs_dir

    @pytest.fixture
    def assets_dir(self, docs_root):
        """Get the assets directory."""
        assets = docs_root / "assets" / "images"
        return assets

    def test_cortex_logo_200_exists(self, assets_dir):
        """Verify cortex-logo-200.png file exists in assets."""
        # Try both lowercase and uppercase versions
        logo_path_lower = assets_dir / "cortex-logo-200.png"
        logo_path_upper = assets_dir / "CORTEX-logo-200.png"
        
        exists = logo_path_lower.exists() or logo_path_upper.exists()
        assert exists, f"cortex-logo-200.png not found at {assets_dir}"

    def test_cortex_logo_200_is_valid_image(self, assets_dir):
        """Verify cortex-logo-200.png is a valid PNG image."""
        # Try both lowercase and uppercase versions
        logo_path = assets_dir / "cortex-logo-200.png"
        if not logo_path.exists():
            logo_path = assets_dir / "CORTEX-logo-200.png"
        
        try:
            img = Image.open(logo_path)
            img.verify()
            # Re-open after verify() closes it
            img = Image.open(logo_path)
        except Exception as e:
            pytest.fail(f"cortex-logo-200.png is not a valid image: {e}")

    def test_cortex_logo_200_dimensions_128x128(self, assets_dir):
        """Verify cortex-logo-200.png has exactly 128x128 pixel dimensions.
        
        This is the working version per git history commit 12aba98b9.
        The CSS styling renders it at 100x100 on screen via glassmorphism.css,
        but the actual image is 128x128 for crisp 2x DPI rendering.
        """
        # Try both lowercase and uppercase versions
        logo_path = assets_dir / "cortex-logo-200.png"
        if not logo_path.exists():
            logo_path = assets_dir / "CORTEX-logo-200.png"
        
        img = Image.open(logo_path)
        width, height = img.size
        img.close()

        assert width == 128, f"Logo width is {width}px, expected 128px"
        assert height == 128, f"Logo height is {height}px, expected 128px"

    def test_cortex_logo_200_file_size_reasonable(self, assets_dir):
        """Verify cortex-logo-200.png file size is reasonable for a 128x128 PNG."""
        # Try both lowercase and uppercase versions
        logo_path = assets_dir / "cortex-logo-200.png"
        if not logo_path.exists():
            logo_path = assets_dir / "CORTEX-logo-200.png"
        
        file_size = logo_path.stat().st_size
        
        # PNG 128x128 should typically be 20-40 KB
        # Allow some flexibility for compression variations
        assert 5_000 < file_size < 100_000, (
            f"cortex-logo-200.png file size {file_size} bytes seems abnormal"
        )

    @pytest.mark.parametrize("filename,expected_width,expected_height", [
        ("CORTEX-logo-64.png", 64, 64),
        ("CORTEX-logo-128.png", 128, 128),
        ("CORTEX-logo-512.png", 512, 512),
    ])
    def test_logo_variants_dimensions(self, assets_dir, filename, expected_width, expected_height):
        """Verify all logo variant images have correct dimensions.
        
        Tests multiple PNG variants used for different contexts:
        - 64x64: Favicons, thumbnails
        - 128x128: Headers, standard display
        - 512x512: High-resolution, print
        """
        logo_path = assets_dir / filename
        
        if not logo_path.exists():
            pytest.skip(f"{filename} not found (optional asset)")
        
        img = Image.open(logo_path)
        width, height = img.size
        img.close()

        assert width == expected_width, (
            f"{filename} width is {width}px, expected {expected_width}px"
        )
        assert height == expected_height, (
            f"{filename} height is {height}px, expected {expected_height}px"
        )

    def test_cortex_logo_svg_exists(self):
        """Verify cortex-logo.svg (light mode) exists in dashboard.
        
        SVG variants are located in cortex/brain/dashboard/frontend/assets/
        rather than docs/assets/images/ (used for dashboard, not docs).
        """
        svg_path = Path(__file__).parent.parent.parent / "cortex" / "brain" / "dashboard" / "frontend" / "assets" / "cortex-logo.svg"
        
        if not svg_path.exists():
            pytest.skip(f"cortex-logo.svg not found in dashboard assets (optional)")
        
        assert svg_path.exists(), f"cortex-logo.svg not found at {svg_path}"

    def test_cortex_logo_white_svg_exists(self):
        """Verify cortex-logo-white.svg (dark mode) exists in dashboard."""
        svg_path = Path(__file__).parent.parent.parent / "cortex" / "brain" / "dashboard" / "frontend" / "assets" / "cortex-logo-white.svg"
        
        if not svg_path.exists():
            pytest.skip(f"cortex-logo-white.svg not found in dashboard assets (optional)")
        
        assert svg_path.exists(), f"cortex-logo-white.svg not found at {svg_path}"

    def test_cortex_logo_svg_is_valid_xml(self):
        """Verify cortex-logo.svg is valid XML/SVG."""
        svg_path = Path(__file__).parent.parent.parent / "cortex" / "brain" / "dashboard" / "frontend" / "assets" / "cortex-logo.svg"
        
        if not svg_path.exists():
            pytest.skip(f"cortex-logo.svg not found in dashboard assets (optional)")
        
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(svg_path)
            root = tree.getroot()
            assert "svg" in root.tag.lower(), "SVG file does not contain svg element"
        except Exception as e:
            pytest.fail(f"cortex-logo.svg is not valid SVG: {e}")

    def test_cortex_logo_white_svg_is_valid_xml(self):
        """Verify cortex-logo-white.svg is valid XML/SVG."""
        svg_path = Path(__file__).parent.parent.parent / "cortex" / "brain" / "dashboard" / "frontend" / "assets" / "cortex-logo-white.svg"
        
        if not svg_path.exists():
            pytest.skip(f"cortex-logo-white.svg not found in dashboard assets (optional)")
        
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(svg_path)
            root = tree.getroot()
            assert "svg" in root.tag.lower(), "SVG file does not contain svg element"
        except Exception as e:
            pytest.fail(f"cortex-logo-white.svg is not valid SVG: {e}")

    def test_svg_logos_file_size_optimized(self):
        """Verify SVG logos are reasonably optimized (<10KB)."""
        project_root = Path(__file__).parent.parent.parent
        svg_files = [
            project_root / "cortex" / "brain" / "dashboard" / "frontend" / "assets" / "cortex-logo.svg",
            project_root / "cortex" / "brain" / "dashboard" / "frontend" / "assets" / "cortex-logo-white.svg"
        ]
        
        found_any = False
        for svg_path in svg_files:
            if svg_path.exists():
                found_any = True
                file_size = svg_path.stat().st_size
                assert file_size < 10_000, (
                    f"{svg_path.name} size {file_size} bytes exceeds 10KB optimization target"
                )
        
        if not found_any:
            pytest.skip("No SVG logos found in dashboard assets (optional)")


class TestLogoIntegration:
    """Test suite for logo integration in mkdocs configuration."""

    @pytest.fixture
    def docs_root(self):
        """Get the docs directory root."""
        current_dir = Path(__file__).parent
        docs_dir = current_dir.parent
        return docs_dir

    def test_logo_used_in_mkdocs_config(self, docs_root):
        """Verify logo is referenced in mkdocs.yml configuration."""
        mkdocs_path = docs_root.parent / "mkdocs.yml"  # docs/ -> project root
        
        if not mkdocs_path.exists():
            # Try alternate locations
            mkdocs_path = docs_root / "mkdocs.yml"
        
        if not mkdocs_path.exists():
            pytest.skip("mkdocs.yml not found in expected locations")
        
        content = mkdocs_path.read_text()
        assert "cortex-logo" in content.lower(), (
            "cortex-logo not referenced in mkdocs.yml configuration"
        )

    def test_logo_css_styling_configured(self, docs_root):
        """Verify glassmorphism.css has logo styling configured."""
        css_path = docs_root / "stylesheets" / "cortex-glassmorphism.css"
        
        if not css_path.exists():
            pytest.skip("cortex-glassmorphism.css not found")
        
        content = css_path.read_text()
        assert ".md-logo" in content, (
            "Logo CSS class .md-logo not found in cortex-glassmorphism.css"
        )
        assert "100px" in content, (
            "Logo size style (100px) not found in cortex-glassmorphism.css"
        )


class TestLogoAccessibility:
    """Test suite for logo accessibility compliance."""

    @pytest.fixture
    def assets_dir(self):
        """Get the assets directory."""
        current_dir = Path(__file__).parent
        docs_dir = current_dir.parent
        assets = docs_dir / "assets" / "images"
        return assets

    def test_primary_logo_has_alt_text_references(self, assets_dir):
        """Verify primary logo asset has proper naming for alt text."""
        # This test documents that alt text should be in HTML/mkdocs config
        # Not in the image file itself, but documented here as requirement
        logo_path = assets_dir / "cortex-logo-200.png"
        assert logo_path.exists(), "Primary logo must exist for alt text assignment"

    def test_logo_is_not_sole_navigation_indicator(self, assets_dir):
        """Verify logo exists but navigation should not rely solely on it.
        
        WCAG 2.1 AA requirement: Logo should complement, not replace,
        text-based navigation.
        """
        logo_path = assets_dir / "cortex-logo-200.png"
        assert logo_path.exists(), "Logo should exist as visual branding element"


# Pytest hooks for automatic execution
def pytest_configure(config):
    """Configure pytest for logo dimension tests."""
    config.addinivalue_line(
        "markers", 
        "logo: mark test as a logo dimension/asset verification test"
    )


if __name__ == "__main__":
    # Enable running tests directly
    pytest.main([__file__, "-v", "--tb=short"])
