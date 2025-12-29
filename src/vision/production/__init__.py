"""
Production Computer Vision Utilities for UI Mockup Analysis

This package provides real image processing algorithms for Vision API production mode.

Modules:
- grid_detector: Edge detection + Hough line transform for grid detection
- color_extractor: K-means clustering for color palette extraction
- element_detector: Contour detection for UI element identification
- pattern_classifier: Rule-based layout pattern classification
- complexity_scorer: Weighted complexity scoring

Author: Asif Hussain
Date: December 26, 2025
"""

from .grid_detector import GridStructure, detect_grid
from .color_extractor import ColorInfo, extract_color_palette
from .element_detector import UIElement, detect_elements
from .pattern_classifier import LayoutPattern, classify_layout_pattern
from .complexity_scorer import ComplexityScore, calculate_complexity

__all__ = [
    'GridStructure',
    'detect_grid',
    'ColorInfo',
    'extract_color_palette',
    'UIElement',
    'detect_elements',
    'LayoutPattern',
    'classify_layout_pattern',
    'ComplexityScore',
    'calculate_complexity',
]
