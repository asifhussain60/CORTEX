"""
Data models for Vision Analyzer atomic analysis mode.

Provides atomic-level visual decomposition models:
- PixelGrid: RGB matrix for visual debugging
- BoundingBox: Precise element coordinates with confidence
- TextSegment: OCR text with metadata
- ColorInfo: Color palette extraction
- FontInfo: Font detection from visual

Phase: 99 Stage 1
Author: Asif Hussain
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class PixelGrid:
    """
    RGB matrix for visual debugging and pixel-level analysis.

    Attributes:
        width: Grid width in pixels.
        height: Grid height in pixels.
        data: 2D list of RGB tuples [(R, G, B), ...] where each value is 0-255.

    Example:
        ```python
        grid = PixelGrid(
            width=3,
            height=2,
            data=[
                [(255, 0, 0), (0, 255, 0), (0, 0, 255)],  # Row 1
                [(128, 128, 128), (255, 255, 0), (0, 255, 255)],  # Row 2
            ]
        )
        ```
    """

    width: int
    height: int
    data: List[List[Tuple[int, int, int]]]  # RGB tuples (0-255)


@dataclass
class FontInfo:
    """
    Font detection metadata from visual analysis.

    Attributes:
        family: Font family name (e.g., "Inter", "Helvetica").
        size: Font size in pixels.
        weight: Font weight (e.g., "normal", "bold", "600").
        style: Font style (e.g., "normal", "italic").

    Example:
        ```python
        font = FontInfo(
            family="Inter",
            size=16,
            weight="600",
            style="normal"
        )
        ```
    """

    family: str
    size: int
    weight: str  # "normal", "bold", "100"-"900"
    style: str  # "normal", "italic", "oblique"


@dataclass
class BoundingBox:
    """
    Precise element coordinates with confidence score.

    Provides pixel-level element positioning with semantic type
    and optional cortex-id linking for bidirectional screenshot ↔ DOM mapping.

    Attributes:
        x: X coordinate of top-left corner.
        y: Y coordinate of top-left corner.
        width: Element width in pixels.
        height: Element height in pixels.
        confidence: Detection confidence score (0.0-1.0).
        semantic_type: Element semantic type (e.g., "button", "input", "nav").
        cortex_id: Optional data-cortex-id attribute for DOM mapping.

    Example:
        ```python
        bbox = BoundingBox(
            x=100,
            y=200,
            width=300,
            height=150,
            confidence=0.95,
            semantic_type="button",
            cortex_id="hero-cta-001"
        )
        ```
    """

    x: int
    y: int
    width: int
    height: int
    confidence: float  # 0.0-1.0
    semantic_type: str  # button, input, nav, content, etc.
    cortex_id: Optional[str] = None  # data-cortex-id if present


@dataclass
class TextSegment:
    """
    OCR text segment with font detection metadata.

    Provides extracted text with positioning, confidence, and optional
    font detection for typography analysis.

    Attributes:
        text: Extracted text content.
        confidence: OCR confidence score (0.0-1.0).
        bbox: BoundingBox for text location.
        font_family: Optional detected font family.
        font_size: Optional detected font size in pixels.
        font_weight: Optional detected font weight.
        font_style: Optional detected font style.

    Example:
        ```python
        segment = TextSegment(
            text="Get Started",
            confidence=0.92,
            bbox=BoundingBox(x=10, y=20, width=100, height=30, confidence=0.9, semantic_type="text", cortex_id=None),
            font_family="Inter",
            font_size=16,
            font_weight="600",
            font_style="normal"
        )
        ```
    """

    text: str
    confidence: float  # 0.0-1.0
    bbox: BoundingBox
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    font_weight: Optional[str] = None  # "normal", "bold", "100"-"900"
    font_style: Optional[str] = None  # "normal", "italic", "oblique"


@dataclass
class ColorInfo:
    """
    Color palette extraction with location metadata.

    Provides hex codes, RGB values, color distribution percentage,
    and location context for visual design analysis.

    Attributes:
        hex_code: Color in hex format (e.g., "#FF5733").
        rgb: RGB tuple (0-255 for each channel).
        percentage: Percentage of image covered by this color (0.0-100.0).
        location: Region description (e.g., "top-left quadrant", "header").

    Example:
        ```python
        color = ColorInfo(
            hex_code="#FF5733",
            rgb=(255, 87, 51),
            percentage=12.5,
            location="top-left quadrant"
        )
        ```
    """

    hex_code: str  # "#RRGGBB"
    rgb: Tuple[int, int, int]  # (R, G, B) where each is 0-255
    percentage: float  # 0.0-100.0
    location: str  # Region description
