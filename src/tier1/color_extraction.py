"""
Vision API Color Extraction Module

Provides K-means clustering-based color palette extraction from UI mockup images.
Includes color role classification, WCAG 2.1 contrast checking, and CSS variable generation.

Author: Asif Hussain
Date: December 26, 2025
Phase: Vision API Phase 2 - Color Extraction
"""

import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import colorsys


@dataclass
class ExtractedColor:
    """Single color extracted from image"""
    rgb: Tuple[int, int, int]
    hex: str
    percentage: float
    role: str  # Primary, Background, Text, Accent, Neutral
    css_var: str  # CSS variable name
    
    
@dataclass
class ColorPalette:
    """Complete color palette extracted from image"""
    colors: List[ExtractedColor]
    dominant_color: ExtractedColor
    contrast_issues: List[Dict[str, any]]
    

class ColorExtractor:
    """
    Extract and analyze color palettes from UI mockup images.
    
    Uses K-means clustering to identify dominant colors, then classifies
    by role (Primary, Background, Text, Accent, Neutral) based on HSV analysis.
    """
    
    def __init__(self, n_colors: int = 5, wcag_target_ratio: float = 4.5):
        """
        Initialize color extractor.
        
        Args:
            n_colors: Number of colors to extract (default: 5)
            wcag_target_ratio: WCAG 2.1 contrast ratio target (default: 4.5 for AA)
        """
        self.n_colors = n_colors
        self.wcag_target_ratio = wcag_target_ratio
        
    def extract_palette(self, image_path: str) -> ColorPalette:
        """
        Extract color palette from image using K-means clustering.
        
        Args:
            image_path: Path to image file
            
        Returns:
            ColorPalette with extracted colors and contrast analysis
        """
        # Load image
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Reshape to pixel array
        pixels = image.reshape(-1, 3)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=self.n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Get colors and their frequencies
        colors = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_
        counts = np.bincount(labels)
        percentages = (counts / counts.sum()) * 100
        
        # Sort by percentage (descending)
        sorted_indices = np.argsort(-percentages)
        
        # Extract colors with classification
        extracted_colors = []
        for idx in sorted_indices:
            rgb = tuple(colors[idx])
            hex_color = self._rgb_to_hex(rgb)
            percentage = percentages[idx]
            role = self._classify_role(rgb, percentage, len(extracted_colors))
            css_var = self._generate_css_var(role)
            
            extracted_colors.append(ExtractedColor(
                rgb=rgb,
                hex=hex_color,
                percentage=percentage,
                role=role,
                css_var=css_var
            ))
        
        # Identify dominant color
        dominant_color = extracted_colors[0]
        
        # Check contrast ratios
        contrast_issues = self._check_contrast(extracted_colors)
        
        return ColorPalette(
            colors=extracted_colors,
            dominant_color=dominant_color,
            contrast_issues=contrast_issues
        )
    
    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex string"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def _classify_role(self, rgb: Tuple[int, int, int], percentage: float, index: int) -> str:
        """
        Classify color role based on HSV properties and dominance.
        
        Args:
            rgb: RGB color tuple
            percentage: Percentage of image pixels
            index: Position in sorted color list (0 = most dominant)
            
        Returns:
            Role string: Primary, Background, Text, Accent, or Neutral
        """
        # Convert to HSV
        r, g, b = [x / 255.0 for x in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        
        # Classification logic
        if index == 0 and percentage > 20:
            # Most dominant color with >20% coverage
            if s < 0.2 and v > 0.8:
                return "Background"  # Low saturation, high value = light background
            else:
                return "Primary"  # High saturation or darker = primary color
        
        elif s < 0.15 and v > 0.85:
            # Very light, low saturation = background/neutral
            return "Background"
        
        elif s < 0.2 and v < 0.3:
            # Low saturation, low value = text/dark neutral
            return "Text"
        
        elif s > 0.5 and v > 0.4:
            # High saturation, decent value = accent color
            return "Accent"
        
        else:
            # Everything else
            return "Neutral"
    
    def _generate_css_var(self, role: str) -> str:
        """Generate CSS variable name from role"""
        role_lower = role.lower().replace(" ", "-")
        return f"--color-{role_lower}"
    
    def _check_contrast(self, colors: List[ExtractedColor]) -> List[Dict[str, any]]:
        """
        Check WCAG 2.1 contrast ratios between color pairs.
        
        Args:
            colors: List of extracted colors
            
        Returns:
            List of contrast issues (ratio < target)
        """
        issues = []
        
        # Check common pairings (background vs text, primary vs background)
        for i, color1 in enumerate(colors):
            for j, color2 in enumerate(colors[i+1:], start=i+1):
                ratio = self._calculate_contrast_ratio(color1.rgb, color2.rgb)
                
                # Flag if below target ratio
                if ratio < self.wcag_target_ratio:
                    issues.append({
                        'color1': color1.hex,
                        'color1_role': color1.role,
                        'color2': color2.hex,
                        'color2_role': color2.role,
                        'ratio': round(ratio, 2),
                        'target': self.wcag_target_ratio,
                        'passes': False
                    })
        
        return issues
    
    def _calculate_contrast_ratio(
        self, 
        rgb1: Tuple[int, int, int], 
        rgb2: Tuple[int, int, int]
    ) -> float:
        """
        Calculate WCAG 2.1 contrast ratio between two colors.
        
        Formula: (L1 + 0.05) / (L2 + 0.05) where L1 > L2
        L = relative luminance
        
        Args:
            rgb1: First RGB color
            rgb2: Second RGB color
            
        Returns:
            Contrast ratio (1:1 to 21:1)
        """
        l1 = self._relative_luminance(rgb1)
        l2 = self._relative_luminance(rgb2)
        
        # Ensure L1 is lighter
        if l2 > l1:
            l1, l2 = l2, l1
        
        return (l1 + 0.05) / (l2 + 0.05)
    
    def _relative_luminance(self, rgb: Tuple[int, int, int]) -> float:
        """
        Calculate relative luminance (WCAG 2.1 formula).
        
        Args:
            rgb: RGB color tuple
            
        Returns:
            Relative luminance (0.0 to 1.0)
        """
        # Convert to 0-1 range
        r, g, b = [x / 255.0 for x in rgb]
        
        # Apply gamma correction
        def adjust(c):
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        
        r = adjust(r)
        g = adjust(g)
        b = adjust(b)
        
        # Calculate luminance
        return 0.2126 * r + 0.7152 * g + 0.0722 * b


def extract_colors_from_mockup(image_path: str, n_colors: int = 5) -> Dict:
    """
    Convenience function to extract colors from mockup image.
    
    Args:
        image_path: Path to mockup image
        n_colors: Number of colors to extract (default: 5)
        
    Returns:
        Dictionary with color palette data
    """
    extractor = ColorExtractor(n_colors=n_colors)
    palette = extractor.extract_palette(image_path)
    
    return {
        'colors': [
            {
                'rgb': color.rgb,
                'hex': color.hex,
                'percentage': round(color.percentage, 1),
                'role': color.role,
                'css_var': color.css_var
            }
            for color in palette.colors
        ],
        'dominant_color': {
            'rgb': palette.dominant_color.rgb,
            'hex': palette.dominant_color.hex,
            'role': palette.dominant_color.role
        },
        'contrast_issues': palette.contrast_issues,
        'total_colors': len(palette.colors),
        'issues_count': len(palette.contrast_issues)
    }
