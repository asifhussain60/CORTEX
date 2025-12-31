"""
Tests for Vision API Color Extraction Module

Author: Asif Hussain
Date: December 26, 2025
Phase: Vision API Phase 2 - Color Extraction Tests
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

# Skip all tests if cv2 not available (optional dependency)
cv2 = pytest.importorskip("cv2", reason="opencv-python not installed (optional dependency)")

from tier1.color_extraction import (
    ColorExtractor,
    extract_colors_from_mockup,
    ExtractedColor,
    ColorPalette
)


class TestColorExtraction:
    """Test suite for color extraction functionality"""
    
    @pytest.fixture
    def test_image_path(self):
        """Path to test mockup image"""
        return "cortex-sample-apps/sts-validation-app/mockups/login-screen.png"
    
    @pytest.fixture
    def extractor(self):
        """ColorExtractor instance"""
        return ColorExtractor(n_colors=5, wcag_target_ratio=4.5)
    
    def test_extractor_initialization(self, extractor):
        """Test ColorExtractor initializes correctly"""
        assert extractor.n_colors == 5
        assert extractor.wcag_target_ratio == 4.5
    
    def test_extract_palette(self, extractor, test_image_path):
        """Test palette extraction from image"""
        palette = extractor.extract_palette(test_image_path)
        
        assert isinstance(palette, ColorPalette)
        assert len(palette.colors) == 5
        assert palette.dominant_color is not None
        assert isinstance(palette.contrast_issues, list)
    
    def test_extracted_color_properties(self, extractor, test_image_path):
        """Test extracted colors have required properties"""
        palette = extractor.extract_palette(test_image_path)
        
        for color in palette.colors:
            assert isinstance(color, ExtractedColor)
            assert isinstance(color.rgb, tuple)
            assert len(color.rgb) == 3
            assert all(0 <= c <= 255 for c in color.rgb)
            assert color.hex.startswith('#')
            assert len(color.hex) == 7
            assert 0 <= color.percentage <= 100
            assert color.role in ['Primary', 'Background', 'Text', 'Accent', 'Neutral']
            assert color.css_var.startswith('--color-')
    
    def test_dominant_color(self, extractor, test_image_path):
        """Test dominant color is most prevalent"""
        palette = extractor.extract_palette(test_image_path)
        
        # Dominant color should have highest percentage
        assert palette.dominant_color == palette.colors[0]
        assert palette.dominant_color.percentage == max(c.percentage for c in palette.colors)
    
    def test_percentage_sum(self, extractor, test_image_path):
        """Test color percentages sum to ~100%"""
        palette = extractor.extract_palette(test_image_path)
        
        total_percentage = sum(c.percentage for c in palette.colors)
        assert 99.0 <= total_percentage <= 100.1  # Allow small floating-point error
    
    def test_rgb_to_hex_conversion(self, extractor):
        """Test RGB to hex conversion"""
        assert extractor._rgb_to_hex((255, 0, 0)) == "#ff0000"
        assert extractor._rgb_to_hex((0, 255, 0)) == "#00ff00"
        assert extractor._rgb_to_hex((0, 0, 255)) == "#0000ff"
        assert extractor._rgb_to_hex((236, 240, 241)) == "#ecf0f1"
    
    def test_contrast_ratio_calculation(self, extractor):
        """Test WCAG 2.1 contrast ratio calculation"""
        # White vs Black should be 21:1
        ratio_wb = extractor._calculate_contrast_ratio((255, 255, 255), (0, 0, 0))
        assert 20.9 <= ratio_wb <= 21.1
        
        # White vs White should be 1:1
        ratio_ww = extractor._calculate_contrast_ratio((255, 255, 255), (255, 255, 255))
        assert 0.9 <= ratio_ww <= 1.1
    
    def test_relative_luminance(self, extractor):
        """Test relative luminance calculation"""
        # White should have luminance ~1.0
        assert 0.99 <= extractor._relative_luminance((255, 255, 255)) <= 1.01
        
        # Black should have luminance ~0.0
        assert extractor._relative_luminance((0, 0, 0)) <= 0.01
    
    def test_contrast_issues_detection(self, extractor, test_image_path):
        """Test contrast issues are detected"""
        palette = extractor.extract_palette(test_image_path)
        
        # Should detect issues with similar background colors
        assert len(palette.contrast_issues) > 0
        
        for issue in palette.contrast_issues:
            assert 'color1' in issue
            assert 'color2' in issue
            assert 'ratio' in issue
            assert 'target' in issue
            assert issue['ratio'] < issue['target']
    
    def test_css_variable_generation(self, extractor):
        """Test CSS variable name generation"""
        assert extractor._generate_css_var('Primary') == '--color-primary'
        assert extractor._generate_css_var('Background') == '--color-background'
        assert extractor._generate_css_var('Text') == '--color-text'
        assert extractor._generate_css_var('Accent') == '--color-accent'
        assert extractor._generate_css_var('Neutral') == '--color-neutral'
    
    def test_convenience_function(self, test_image_path):
        """Test extract_colors_from_mockup convenience function"""
        result = extract_colors_from_mockup(test_image_path)
        
        assert isinstance(result, dict)
        assert 'colors' in result
        assert 'dominant_color' in result
        assert 'contrast_issues' in result
        assert 'total_colors' in result
        assert 'issues_count' in result
        
        assert result['total_colors'] == 5
        assert len(result['colors']) == 5
        assert result['issues_count'] == len(result['contrast_issues'])


class TestColorClassification:
    """Test suite for color role classification"""
    
    @pytest.fixture
    def extractor(self):
        return ColorExtractor()
    
    def test_background_classification(self, extractor):
        """Test light colors are classified as Background"""
        # Very light gray (high value, low saturation)
        role = extractor._classify_role((240, 240, 240), 30.0, 0)
        assert role == "Background"
    
    def test_text_classification(self, extractor):
        """Test dark low-saturation colors are classified as Text"""
        # Dark gray (low value, low saturation)
        role = extractor._classify_role((50, 50, 50), 10.0, 2)
        assert role == "Text"
    
    def test_accent_classification(self, extractor):
        """Test saturated colors are classified as Accent"""
        # Bright red (high saturation, decent value)
        role = extractor._classify_role((230, 75, 60), 5.0, 1)
        assert role == "Accent"
    
    def test_primary_classification(self, extractor):
        """Test dominant saturated colors are classified as Primary"""
        # Blue with high coverage (dominant, high saturation)
        role = extractor._classify_role((41, 128, 185), 35.0, 0)
        assert role == "Primary"


class TestWCAGCompliance:
    """Test suite for WCAG 2.1 AA compliance checking"""
    
    @pytest.fixture
    def extractor(self):
        return ColorExtractor(wcag_target_ratio=4.5)
    
    def test_passing_contrast(self, extractor):
        """Test high-contrast colors pass WCAG"""
        # Black on white should pass
        ratio = extractor._calculate_contrast_ratio((0, 0, 0), (255, 255, 255))
        assert ratio >= 4.5
    
    def test_failing_contrast(self, extractor):
        """Test low-contrast colors fail WCAG"""
        # Light gray on white should fail
        ratio = extractor._calculate_contrast_ratio((220, 220, 220), (255, 255, 255))
        assert ratio < 4.5
    
    def test_wcag_aa_minimum(self, extractor):
        """Test WCAG AA minimum (4.5:1) enforcement"""
        assert extractor.wcag_target_ratio == 4.5


@pytest.mark.integration
class TestIntegration:
    """Integration tests for full color extraction workflow"""
    
    def test_end_to_end_extraction(self):
        """Test complete extraction workflow"""
        image_path = "cortex-sample-apps/sts-validation-app/mockups/login-screen.png"
        
        # Extract colors
        result = extract_colors_from_mockup(image_path, n_colors=5)
        
        # Validate structure
        assert result['total_colors'] == 5
        assert len(result['colors']) == 5
        assert result['dominant_color']['hex'].startswith('#')
        
        # Validate color data
        for color in result['colors']:
            assert 'rgb' in color
            assert 'hex' in color
            assert 'percentage' in color
            assert 'role' in color
            assert 'css_var' in color
        
        # Validate contrast checking
        assert isinstance(result['contrast_issues'], list)
        assert result['issues_count'] >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
