"""
Vision API Element Detection Module

Provides contour-based UI element detection from mockup images.
Includes element classification, bounding box extraction, test ID generation,
and basic accessibility checking.

Author: Asif Hussain
Date: December 26, 2025
Phase: Vision API Phase 3 - Element Detection
"""

import cv2
import numpy as np
from PIL import Image
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ElementType(Enum):
    """UI element types"""
    BUTTON = "button"
    INPUT = "input"
    CARD = "card"
    TITLE = "title"
    CHECKBOX = "checkbox"
    TEXT = "text"
    IMAGE = "image"
    LINK = "link"
    UNKNOWN = "unknown"


@dataclass
class UIElement:
    """Detected UI element with properties"""
    element_type: ElementType
    bounds: Tuple[int, int, int, int]  # x, y, width, height
    test_id: str
    area: int
    aspect_ratio: float
    accessibility_issues: List[str]
    confidence: float  # Detection confidence (0.0 to 1.0)
    

@dataclass
class ElementDetectionResult:
    """Complete element detection result"""
    elements: List[UIElement]
    total_count: int
    by_type: Dict[str, int]
    accessibility_issues: List[Dict[str, any]]
    

class ElementDetector:
    """
    Detect and classify UI elements from mockup images using contour detection.
    
    Uses OpenCV's findContours with hierarchical detection to identify
    UI components, then classifies by size, aspect ratio, and position.
    """
    
    def __init__(
        self,
        min_area: int = 100,
        max_area: int = 500000,
        edge_threshold1: int = 50,
        edge_threshold2: int = 150
    ):
        """
        Initialize element detector.
        
        Args:
            min_area: Minimum contour area (filter noise)
            max_area: Maximum contour area (filter full-screen)
            edge_threshold1: Canny edge detection lower threshold
            edge_threshold2: Canny edge detection upper threshold
        """
        self.min_area = min_area
        self.max_area = max_area
        self.edge_threshold1 = edge_threshold1
        self.edge_threshold2 = edge_threshold2
        
    def detect_elements(self, image_path: str) -> ElementDetectionResult:
        """
        Detect UI elements from mockup image.
        
        Args:
            image_path: Path to mockup image
            
        Returns:
            ElementDetectionResult with detected elements
        """
        # Load image
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Preprocessing: Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, self.edge_threshold1, self.edge_threshold2)
        
        # Morphological closing to connect edge gaps
        kernel = np.ones((3, 3), np.uint8)
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Find contours
        contours, hierarchy = cv2.findContours(
            closed, 
            cv2.RETR_TREE, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter and classify contours
        elements = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            # Filter by area
            if area < self.min_area or area > self.max_area:
                continue
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calculate properties
            aspect_ratio = w / h if h > 0 else 0
            
            # Classify element type
            element_type = self._classify_element(area, aspect_ratio, w, h, i, hierarchy)
            
            # Generate test ID
            test_id = self._generate_test_id(element_type, i)
            
            # Check accessibility
            accessibility_issues = self._check_accessibility(element_type)
            
            # Calculate confidence (simple heuristic)
            confidence = self._calculate_confidence(area, aspect_ratio, element_type)
            
            elements.append(UIElement(
                element_type=element_type,
                bounds=(x, y, w, h),
                test_id=test_id,
                area=area,
                aspect_ratio=aspect_ratio,
                accessibility_issues=accessibility_issues,
                confidence=confidence
            ))
        
        # Sort by area (largest first)
        elements.sort(key=lambda e: e.area, reverse=True)
        
        # Filter duplicates/overlaps using NMS
        elements = self._filter_duplicates(elements)
        
        # Aggregate results
        total_count = len(elements)
        by_type = self._count_by_type(elements)
        accessibility_issues = self._aggregate_accessibility_issues(elements)
        
        return ElementDetectionResult(
            elements=elements,
            total_count=total_count,
            by_type=by_type,
            accessibility_issues=accessibility_issues
        )
    
    def _classify_element(
        self,
        area: int,
        aspect_ratio: float,
        width: int,
        height: int,
        index: int,
        hierarchy: np.ndarray
    ) -> ElementType:
        """
        Classify UI element based on geometric properties.
        
        Args:
            area: Contour area
            aspect_ratio: Width / height
            width: Bounding box width
            height: Bounding box height
            index: Contour index
            hierarchy: Contour hierarchy
            
        Returns:
            ElementType classification
        """
        # Card: Large area, roughly square or slightly wide
        if area > 100000 and 0.8 <= aspect_ratio <= 1.5:
            return ElementType.CARD
        
        # Button: Medium-large area, wide, height 40-80px
        if aspect_ratio > 6 and 40 < height < 80 and 15000 < area < 50000:
            return ElementType.BUTTON
        
        # Input field: Wide, height 40-60px, medium area
        if aspect_ratio > 6 and 40 < height < 65 and 10000 < area < 40000:
            return ElementType.INPUT
        
        # Title/Header: Very wide and short OR large wide rectangle
        if (aspect_ratio > 8 and height < 80 and area > 20000) or \
           (aspect_ratio > 5 and height < 100 and area > 25000):
            return ElementType.TITLE
        
        # Checkbox: Small, square-ish
        if area < 1000 and 0.7 <= aspect_ratio <= 1.3 and width < 40 and height < 40:
            return ElementType.CHECKBOX
        
        # Default
        return ElementType.UNKNOWN
    
    def _generate_test_id(self, element_type: ElementType, index: int) -> str:
        """
        Generate data-testid attribute for automated testing.
        
        Args:
            element_type: Type of UI element
            index: Element index
            
        Returns:
            Kebab-case test ID
        """
        type_name = element_type.value
        return f"{type_name}-{index}"
    
    def _check_accessibility(self, element_type: ElementType) -> List[str]:
        """
        Check for common accessibility issues.
        
        Args:
            element_type: Type of UI element
            
        Returns:
            List of accessibility issue descriptions
        """
        issues = []
        
        # Input fields should have labels/aria-labels
        if element_type == ElementType.INPUT:
            issues.append("Missing aria-label or associated label")
        
        # Buttons should have accessible text
        if element_type == ElementType.BUTTON:
            issues.append("Verify button has accessible text/aria-label")
        
        # Images should have alt text
        if element_type == ElementType.IMAGE:
            issues.append("Missing alt attribute")
        
        # Checkboxes should have labels
        if element_type == ElementType.CHECKBOX:
            issues.append("Missing label association (for/id)")
        
        return issues
    
    def _calculate_confidence(
        self,
        area: int,
        aspect_ratio: float,
        element_type: ElementType
    ) -> float:
        """
        Calculate detection confidence score.
        
        Args:
            area: Element area
            aspect_ratio: Element aspect ratio
            element_type: Classified type
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Simple heuristic based on element type
        confidence_map = {
            ElementType.CARD: 0.95,
            ElementType.BUTTON: 0.85,
            ElementType.INPUT: 0.85,
            ElementType.TITLE: 0.80,
            ElementType.CHECKBOX: 0.75,
            ElementType.UNKNOWN: 0.50
        }
        
        base_confidence = confidence_map.get(element_type, 0.5)
        
        # Adjust based on area (larger elements = higher confidence)
        area_factor = min(area / 50000, 1.0) * 0.1
        
        return min(base_confidence + area_factor, 1.0)
    
    def _count_by_type(self, elements: List[UIElement]) -> Dict[str, int]:
        """
        Count elements by type.
        
        Args:
            elements: List of detected elements
            
        Returns:
            Dictionary of type counts
        """
        counts = {}
        for element in elements:
            type_name = element.element_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts
    
    def _aggregate_accessibility_issues(
        self, 
        elements: List[UIElement]
    ) -> List[Dict[str, any]]:
        """
        Aggregate accessibility issues across all elements.
        
        Args:
            elements: List of detected elements
            
        Returns:
            List of accessibility issue dictionaries
        """
        issues = []
        for element in elements:
            if element.accessibility_issues:
                for issue_text in element.accessibility_issues:
                    issues.append({
                        'element_id': element.test_id,
                        'element_type': element.element_type.value,
                        'issue': issue_text,
                        'severity': 'warning'
                    })
        return issues
    
    def _filter_duplicates(
        self,
        elements: List[UIElement],
        iou_threshold: float = 0.5
    ) -> List[UIElement]:
        """
        Filter duplicate/overlapping elements using Non-Maximum Suppression (NMS).
        
        Elements are already sorted by area (largest first). For each element,
        we suppress (remove) any smaller elements that overlap significantly.
        
        Args:
            elements: List of elements sorted by area (largest first)
            iou_threshold: IoU threshold for considering elements as duplicates (0.5 = 50% overlap)
            
        Returns:
            Filtered list of elements with duplicates removed
        """
        if len(elements) <= 1:
            return elements
        
        # Keep track of elements to keep
        keep = []
        suppressed = set()
        
        for i, element in enumerate(elements):
            if i in suppressed:
                continue
            
            # Keep this element
            keep.append(element)
            
            # Suppress overlapping smaller elements
            for j in range(i + 1, len(elements)):
                if j in suppressed:
                    continue
                
                # Calculate IoU
                iou = self._calculate_iou(element.bounds, elements[j].bounds)
                
                # Suppress if overlap is significant
                if iou > iou_threshold:
                    suppressed.add(j)
        
        return keep
    
    def _calculate_iou(
        self,
        bounds1: Tuple[int, int, int, int],
        bounds2: Tuple[int, int, int, int]
    ) -> float:
        """
        Calculate Intersection over Union (IoU) between two bounding boxes.
        
        Args:
            bounds1: First bounding box (x, y, w, h)
            bounds2: Second bounding box (x, y, w, h)
            
        Returns:
            IoU value between 0 and 1
        """
        x1, y1, w1, h1 = bounds1
        x2, y2, w2, h2 = bounds2
        
        # Calculate intersection rectangle
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        # Check if there's no intersection
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        # Calculate intersection area
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        
        # Calculate union area
        area1 = w1 * h1
        area2 = w2 * h2
        union_area = area1 + area2 - intersection_area
        
        # Calculate IoU
        if union_area == 0:
            return 0.0
        
        return intersection_area / union_area


def detect_elements_from_mockup(image_path: str) -> Dict:
    """
    Convenience function to detect elements from mockup image.
    
    Args:
        image_path: Path to mockup image
        
    Returns:
        Dictionary with element detection data
    """
    detector = ElementDetector()
    result = detector.detect_elements(image_path)
    
    return {
        'elements': [
            {
                'type': elem.element_type.value,
                'bounds': {
                    'x': elem.bounds[0],
                    'y': elem.bounds[1],
                    'width': elem.bounds[2],
                    'height': elem.bounds[3]
                },
                'test_id': elem.test_id,
                'area': elem.area,
                'aspect_ratio': round(elem.aspect_ratio, 2),
                'confidence': round(elem.confidence, 2),
                'accessibility_issues': elem.accessibility_issues
            }
            for elem in result.elements
        ],
        'total_count': result.total_count,
        'by_type': result.by_type,
        'accessibility_issues': result.accessibility_issues,
        'issues_count': len(result.accessibility_issues)
    }
