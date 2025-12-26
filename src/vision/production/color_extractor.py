"""
Color Palette Extraction using K-means Clustering

Extracts dominant colors from UI mockups and calculates WCAG contrast ratios.

Algorithm:
1. Load image and resize for performance
2. Apply K-means clustering to find dominant colors
3. Calculate color percentages
4. Classify color roles (primary, secondary, accent, neutral, text)
5. Calculate WCAG 2.1 contrast ratios

Author: Asif Hussain
Date: December 26, 2025
"""

import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from typing import List, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ColorInfo:
    """
    Information about an extracted color.
    
    Attributes:
        hex: Color in hexadecimal format (#RRGGBB)
        rgb: Color as RGB tuple (R, G, B)
        role: Color role (primary, secondary, accent, neutral, text)
        percentage: Percentage of image pixels (0-100)
        wcag_contrast: WCAG 2.1 contrast ratio vs white (1.0-21.0)
    """
    hex: str
    rgb: Tuple[int, int, int]
    role: str
    percentage: float
    wcag_contrast: float


def extract_color_palette(image_path: str, n_colors: int = 6) -> List[ColorInfo]:
    """
    Extract dominant color palette using K-means clustering.
    
    Args:
        image_path: Path to mockup image (PNG/JPG)
        n_colors: Number of colors to extract (default: 6)
        
    Returns:
        List of ColorInfo objects (sorted by percentage descending)
        
    Example:
        >>> colors = extract_color_palette("mockups/dashboard.png")
        >>> for color in colors[:3]:
        ...     print(f"{color.hex} ({color.role}): {color.percentage:.1f}%")
        #1A73E8 (primary): 35.2%
        #FFFFFF (neutral): 28.7%
        #202124 (text): 15.3%
    """
    # Validate path
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Load image
    img = Image.open(image_path)
    img = img.convert('RGB')
    
    # Resize for performance (K-means on full image is slow)
    img_small = img.resize((150, 150))
    
    # Convert to numpy array and reshape to 2D (pixels × RGB)
    pixels = np.array(img_small).reshape(-1, 3)
    
    # K-means clustering
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # Get cluster centers (dominant colors)
    colors = kmeans.cluster_centers_.astype(int)
    
    # Calculate percentage of pixels for each color
    labels = kmeans.labels_
    percentages = np.bincount(labels) / len(labels) * 100
    
    # Sort by percentage (descending)
    sorted_indices = np.argsort(percentages)[::-1]
    
    # Build ColorInfo objects
    palette = []
    for i in sorted_indices:
        rgb = tuple(colors[i])
        hex_color = '#%02x%02x%02x' % rgb
        role = _classify_color_role(rgb, i)
        contrast = _calculate_contrast(rgb, (255, 255, 255))
        
        palette.append(ColorInfo(
            hex=hex_color,
            rgb=rgb,
            role=role,
            percentage=percentages[i],
            wcag_contrast=contrast
        ))
    
    return palette


def _classify_color_role(rgb: Tuple[int, int, int], rank: int) -> str:
    """
    Classify color role based on RGB values and dominance rank.
    
    Heuristics:
    - rank 0 (most dominant) → primary or neutral
    - Dark colors (low brightness) → text or neutral
    - Saturated colors → accent
    - Light colors → secondary or neutral
    
    Args:
        rgb: RGB color tuple (R, G, B)
        rank: Dominance rank (0 = most dominant)
        
    Returns:
        Color role string
    """
    r, g, b = rgb
    
    # Calculate brightness (0-255)
    brightness = (r + g + b) / 3
    
    # Calculate saturation (distance from grayscale)
    avg = brightness
    saturation = max(abs(r - avg), abs(g - avg), abs(b - avg))
    
    # Most dominant color
    if rank == 0:
        return 'primary' if saturation > 30 else 'neutral'
    
    # Dark colors
    if brightness < 60:
        return 'text'
    
    # Saturated colors
    if saturation > 50:
        return 'accent'
    
    # Light colors
    if brightness > 200:
        return 'secondary'
    
    return 'neutral'


def _calculate_contrast(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    """
    Calculate WCAG 2.1 contrast ratio between two colors.
    
    Formula: (L1 + 0.05) / (L2 + 0.05)
    Where L = relative luminance (0.0 - 1.0)
    
    WCAG AA requires:
    - ≥4.5:1 for normal text
    - ≥3:1 for large text
    
    Args:
        rgb1: First color as RGB tuple
        rgb2: Second color as RGB tuple
        
    Returns:
        Contrast ratio (1.0 - 21.0)
    """
    def _relative_luminance(rgb):
        r, g, b = [x / 255.0 for x in rgb]
        
        # sRGB to linear RGB conversion
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    L1 = _relative_luminance(rgb1)
    L2 = _relative_luminance(rgb2)
    
    lighter = max(L1, L2)
    darker = min(L1, L2)
    
    return (lighter + 0.05) / (darker + 0.05)


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python color_extractor.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        colors = extract_color_palette(image_path)
        print(f"✅ Color Palette Extraction Results:")
        print(f"   Total Colors: {len(colors)}")
        print()
        for i, color in enumerate(colors, 1):
            print(f"   {i}. {color.hex}")
            print(f"      Role: {color.role}")
            print(f"      RGB: {color.rgb}")
            print(f"      Coverage: {color.percentage:.1f}%")
            print(f"      Contrast: {color.wcag_contrast:.2f}:1")
            wcag_aa = "✅ PASS" if color.wcag_contrast >= 4.5 else "❌ FAIL"
            print(f"      WCAG AA: {wcag_aa}")
            print()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
