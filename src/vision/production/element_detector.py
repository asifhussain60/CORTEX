"""
UI Element Detection using Contour Analysis

Detects UI elements (buttons, inputs, cards, etc.) using contour detection and shape analysis.

Algorithm:
1. Preprocess image (grayscale, blur, threshold)
2. Find contours (connected regions)
3. Filter by size (remove noise)
4. Classify by shape/aspect ratio
5. Generate test IDs

Author: Asif Hussain
Date: December 26, 2025
"""

import cv2
import numpy as np
from typing import List, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class UIElement:
    """
    Detected UI element with bounding box and metadata.
    
    Attributes:
        type: Element type (button, input, card, image, container)
        bounding_box: (x, y, width, height) in pixels
        test_id: Generated test ID (e.g., 'button-1', 'input-email')
        confidence: Detection confidence (0.0-1.0)
    """
    type: str
    bounding_box: Tuple[int, int, int, int]
    test_id: str
    confidence: float


def detect_elements(image_path: str) -> List[UIElement]:
    """
    Detect UI elements using contour detection and shape analysis.
    
    Algorithm:
    1. Preprocess image (grayscale, blur, threshold)
    2. Find contours (connected regions)
    3. Filter by size (remove noise)
    4. Classify by shape/aspect ratio
    5. Generate test IDs
    
    Args:
        image_path: Path to mockup image (PNG/JPG)
        
    Returns:
        List of detected UI elements with bounding boxes
        
    Example:
        >>> elements = detect_elements("mockups/login.png")
        >>> for elem in elements:
        ...     print(f"{elem.type}: {elem.test_id}")
        input: email-input
        input: password-input
        button: login-button
    """
    # Validate path
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Preprocessing
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Threshold (binary image - white elements on black background)
    _, thresh = cv2.threshold(blurred, 240, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    elements = []
    element_counts = {}  # Track counts for test ID generation
    
    for contour in contours:
        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        # Filter by size (remove noise - too small or too large)
        area = w * h
        image_area = img.shape[0] * img.shape[1]
        
        if area < 1000 or area > image_area * 0.5:
            continue
        
        # Classify element by shape
        element_type = _classify_element(w, h, area)
        
        # Generate test ID
        element_counts[element_type] = element_counts.get(element_type, 0) + 1
        test_id = f"{element_type}-{element_counts[element_type]}"
        
        # Confidence based on contour properties
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
        confidence = min(circularity + 0.5, 1.0)  # Boost confidence
        
        elements.append(UIElement(
            type=element_type,
            bounding_box=(x, y, w, h),
            test_id=test_id,
            confidence=confidence
        ))
    
    return elements


def _classify_element(width: int, height: int, area: int) -> str:
    """
    Classify UI element type based on dimensions.
    
    Heuristics:
    - Small square/rectangle (100-300px width) → button
    - Wide rectangle (>500px width, thin) → input
    - Large rectangle (>10k area) → card
    - Square (aspect ratio ~1:1) → image/icon
    
    Args:
        width: Element width in pixels
        height: Element height in pixels
        area: Element area in pixels²
        
    Returns:
        Element type string
    """
    aspect_ratio = width / height if height > 0 else 1
    
    # Button: small, roughly rectangular
    if 100 <= width <= 300 and 0.3 <= aspect_ratio <= 3:
        return 'button'
    
    # Input: wide, thin
    if width > 300 and aspect_ratio > 4:
        return 'input'
    
    # Card: large rectangle
    if area > 50000:
        return 'card'
    
    # Image/Icon: square-ish
    if 0.8 <= aspect_ratio <= 1.2:
        return 'image'
    
    # Default
    return 'container'


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python element_detector.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        elements = detect_elements(image_path)
        print(f"✅ UI Element Detection Results:")
        print(f"   Total Elements: {len(elements)}")
        print()
        
        # Group by type
        by_type = {}
        for elem in elements:
            if elem.type not in by_type:
                by_type[elem.type] = []
            by_type[elem.type].append(elem)
        
        for elem_type, elems in sorted(by_type.items()):
            print(f"   {elem_type.upper()}: {len(elems)} detected")
            for elem in elems[:3]:  # Show first 3
                x, y, w, h = elem.bounding_box
                print(f"      - {elem.test_id}: ({x}, {y}) {w}x{h}px [confidence: {elem.confidence:.2f}]")
            if len(elems) > 3:
                print(f"      ... and {len(elems) - 3} more")
            print()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
