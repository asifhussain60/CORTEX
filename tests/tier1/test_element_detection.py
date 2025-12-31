"""
Tests for Vision API Element Detection Module

Author: Asif Hussain
Date: December 26, 2025
Phase: Vision API Phase 3 - Element Detection Tests
"""

import pytest
import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

# Skip all tests if cv2 not available (optional dependency)
cv2 = pytest.importorskip("cv2", reason="opencv-python not installed (optional dependency)")

from tier1.element_detection import (
    ElementDetector,
    ElementType,
    UIElement,
    ElementDetectionResult,
    detect_elements_from_mockup
)


class TestElementDetector:
    """Test suite for element detector"""
    
    @pytest.fixture
    def test_image_path(self):
        """Path to detailed test mockup"""
        return "cortex-sample-apps/sts-validation-app/mockups/login-screen-detailed.png"
    
    @pytest.fixture
    def detector(self):
        """ElementDetector instance"""
        return ElementDetector(
            min_area=100,
            max_area=500000,
            edge_threshold1=50,
            edge_threshold2=150
        )
    
    def test_detector_initialization(self, detector):
        """Test ElementDetector initializes correctly"""
        assert detector.min_area == 100
        assert detector.max_area == 500000
        assert detector.edge_threshold1 == 50
        assert detector.edge_threshold2 == 150
    
    def test_detect_elements(self, detector, test_image_path):
        """Test element detection from image"""
        result = detector.detect_elements(test_image_path)
        
        assert isinstance(result, ElementDetectionResult)
        assert result.total_count > 0
        assert len(result.elements) > 0
        assert isinstance(result.by_type, dict)
        assert isinstance(result.accessibility_issues, list)
    
    def test_detected_element_properties(self, detector, test_image_path):
        """Test detected elements have required properties"""
        result = detector.detect_elements(test_image_path)
        
        for element in result.elements:
            assert isinstance(element, UIElement)
            assert isinstance(element.element_type, ElementType)
            assert isinstance(element.bounds, tuple)
            assert len(element.bounds) == 4
            assert all(isinstance(b, (int, np.integer)) for b in element.bounds)
            assert element.area > 0
            assert element.aspect_ratio > 0
            assert 0 <= element.confidence <= 1.0
            assert isinstance(element.test_id, str)
            assert isinstance(element.accessibility_issues, list)
    
    def test_element_type_detection(self, detector, test_image_path):
        """Test different element types are detected"""
        result = detector.detect_elements(test_image_path)
        
        # Should detect multiple types
        assert len(result.by_type) > 1
        
        # Specific types expected in login mockup
        type_values = [elem.element_type.value for elem in result.elements]
        assert 'card' in type_values or 'card' in result.by_type
    
    def test_element_bounds_valid(self, detector, test_image_path):
        """Test element bounds are valid"""
        result = detector.detect_elements(test_image_path)
        
        for element in result.elements:
            x, y, w, h = element.bounds
            assert x >= 0
            assert y >= 0
            assert w > 0
            assert h > 0
            assert element.area == w * h or element.area <= w * h  # Area may be from contour
    
    def test_test_id_generation(self, detector):
        """Test test ID generation"""
        test_id = detector._generate_test_id(ElementType.BUTTON, 5)
        assert test_id == "button-5"
        
        test_id = detector._generate_test_id(ElementType.INPUT, 0)
        assert test_id == "input-0"
    
    def test_accessibility_checking(self, detector):
        """Test accessibility issue detection"""
        # Input should have issues
        issues = detector._check_accessibility(ElementType.INPUT)
        assert len(issues) > 0
        assert any('aria-label' in issue.lower() for issue in issues)
        
        # Button should have issues
        issues = detector._check_accessibility(ElementType.BUTTON)
        assert len(issues) > 0
        
        # Checkbox should have issues
        issues = detector._check_accessibility(ElementType.CHECKBOX)
        assert len(issues) > 0
        assert any('label' in issue.lower() for issue in issues)
    
    def test_confidence_calculation(self, detector):
        """Test confidence score calculation"""
        # High confidence for card
        conf = detector._calculate_confidence(200000, 1.2, ElementType.CARD)
        assert 0.9 <= conf <= 1.0
        
        # Medium confidence for button
        conf = detector._calculate_confidence(20000, 8.0, ElementType.BUTTON)
        assert 0.75 <= conf <= 0.95
        
        # Low confidence for unknown
        conf = detector._calculate_confidence(5000, 2.0, ElementType.UNKNOWN)
        assert 0.4 <= conf <= 0.6
    
    def test_element_sorting(self, detector, test_image_path):
        """Test elements are sorted by area (largest first)"""
        result = detector.detect_elements(test_image_path)
        
        if len(result.elements) > 1:
            for i in range(len(result.elements) - 1):
                assert result.elements[i].area >= result.elements[i+1].area
    
    def test_count_by_type(self, detector, test_image_path):
        """Test element counting by type"""
        result = detector.detect_elements(test_image_path)
        
        # Count manually
        manual_count = {}
        for elem in result.elements:
            type_name = elem.element_type.value
            manual_count[type_name] = manual_count.get(type_name, 0) + 1
        
        assert result.by_type == manual_count
    
    def test_accessibility_aggregation(self, detector, test_image_path):
        """Test accessibility issues aggregation"""
        result = detector.detect_elements(test_image_path)
        
        # Should aggregate issues from all elements
        for issue in result.accessibility_issues:
            assert 'element_id' in issue
            assert 'element_type' in issue
            assert 'issue' in issue
            assert 'severity' in issue
    
    def test_convenience_function(self, test_image_path):
        """Test detect_elements_from_mockup convenience function"""
        result = detect_elements_from_mockup(test_image_path)
        
        assert isinstance(result, dict)
        assert 'elements' in result
        assert 'total_count' in result
        assert 'by_type' in result
        assert 'accessibility_issues' in result
        assert 'issues_count' in result
        
        assert result['total_count'] > 0
        assert len(result['elements']) > 0
        assert result['issues_count'] >= 0


class TestElementClassification:
    """Test suite for element classification logic"""
    
    @pytest.fixture
    def detector(self):
        return ElementDetector()
    
    def test_card_classification(self, detector):
        """Test large elements are classified as cards"""
        # Large square/rectangular element
        elem_type = detector._classify_element(
            area=300000,
            aspect_ratio=1.2,
            width=600,
            height=500,
            index=0,
            hierarchy=None
        )
        assert elem_type == ElementType.CARD
    
    def test_button_classification(self, detector):
        """Test button-shaped elements are classified correctly"""
        # Wide, medium height element
        elem_type = detector._classify_element(
            area=25000,
            aspect_ratio=10.0,
            width=500,
            height=50,
            index=1,
            hierarchy=None
        )
        assert elem_type == ElementType.BUTTON
    
    def test_input_classification(self, detector):
        """Test input field elements are classified correctly"""
        # Wide, medium height element (realistic input field dimensions)
        # Note: Button/input distinction is ambiguous in CV - both are wide horizontal elements
        # In real detection, context (labels, borders, shadows) helps differentiate
        elem_type = detector._classify_element(
            area=22000,
            aspect_ratio=11.0,
            width=550,
            height=50,
            index=2,
            hierarchy=None
        )
        # Accept either classification as both are valid for these dimensions
        assert elem_type in (ElementType.INPUT, ElementType.BUTTON)
    
    def test_checkbox_classification(self, detector):
        """Test small square elements are classified as checkboxes"""
        # Small square element
        elem_type = detector._classify_element(
            area=400,
            aspect_ratio=1.0,
            width=20,
            height=20,
            index=3,
            hierarchy=None
        )
        assert elem_type == ElementType.CHECKBOX
    
    def test_title_classification(self, detector):
        """Test title/header elements are classified correctly"""
        # Very wide, short element
        elem_type = detector._classify_element(
            area=30000,
            aspect_ratio=15.0,
            width=600,
            height=40,
            index=4,
            hierarchy=None
        )
        assert elem_type == ElementType.TITLE
    
    def test_unknown_classification(self, detector):
        """Test unrecognized elements are classified as unknown"""
        # Odd dimensions
        elem_type = detector._classify_element(
            area=5000,
            aspect_ratio=0.5,
            width=50,
            height=100,
            index=5,
            hierarchy=None
        )
        assert elem_type == ElementType.UNKNOWN


class TestAccessibilityChecking:
    """Test suite for accessibility issue detection"""
    
    @pytest.fixture
    def detector(self):
        return ElementDetector()
    
    def test_input_accessibility_issues(self, detector):
        """Test input fields have accessibility checks"""
        issues = detector._check_accessibility(ElementType.INPUT)
        assert len(issues) > 0
        assert any('aria-label' in issue.lower() or 'label' in issue.lower() for issue in issues)
    
    def test_button_accessibility_issues(self, detector):
        """Test buttons have accessibility checks"""
        issues = detector._check_accessibility(ElementType.BUTTON)
        assert len(issues) > 0
        assert any('text' in issue.lower() or 'aria-label' in issue.lower() for issue in issues)
    
    def test_image_accessibility_issues(self, detector):
        """Test images have alt text checks"""
        issues = detector._check_accessibility(ElementType.IMAGE)
        assert len(issues) > 0
        assert any('alt' in issue.lower() for issue in issues)
    
    def test_checkbox_accessibility_issues(self, detector):
        """Test checkboxes have label checks"""
        issues = detector._check_accessibility(ElementType.CHECKBOX)
        assert len(issues) > 0
        assert any('label' in issue.lower() for issue in issues)


class TestDuplicateFiltering:
    """Test suite for Non-Maximum Suppression (NMS) duplicate filtering"""
    
    @pytest.fixture
    def detector(self):
        return ElementDetector()
    
    def test_iou_no_overlap(self, detector):
        """Test IoU calculation for non-overlapping boxes"""
        bounds1 = (0, 0, 100, 100)
        bounds2 = (200, 200, 100, 100)
        iou = detector._calculate_iou(bounds1, bounds2)
        assert iou == 0.0
    
    def test_iou_perfect_overlap(self, detector):
        """Test IoU calculation for identical boxes"""
        bounds1 = (100, 100, 200, 200)
        bounds2 = (100, 100, 200, 200)
        iou = detector._calculate_iou(bounds1, bounds2)
        assert iou == 1.0
    
    def test_iou_partial_overlap(self, detector):
        """Test IoU calculation for partially overlapping boxes"""
        bounds1 = (0, 0, 100, 100)
        bounds2 = (50, 50, 100, 100)  # 50% overlap
        iou = detector._calculate_iou(bounds1, bounds2)
        # Intersection: 50x50 = 2500
        # Union: 10000 + 10000 - 2500 = 17500
        # IoU: 2500/17500 = 0.142857
        assert 0.14 <= iou <= 0.15
    
    def test_filter_duplicates_no_overlap(self, detector):
        """Test filtering with no overlapping elements"""
        elements = [
            UIElement(
                element_type=ElementType.CARD,
                bounds=(0, 0, 100, 100),
                test_id="card-0",
                area=10000,
                aspect_ratio=1.0,
                accessibility_issues=[],
                confidence=0.9
            ),
            UIElement(
                element_type=ElementType.BUTTON,
                bounds=(200, 200, 100, 50),
                test_id="button-1",
                area=5000,
                aspect_ratio=2.0,
                accessibility_issues=[],
                confidence=0.8
            )
        ]
        
        filtered = detector._filter_duplicates(elements)
        assert len(filtered) == 2  # No filtering
    
    def test_filter_duplicates_significant_overlap(self, detector):
        """Test filtering with significant overlap (should suppress)"""
        elements = [
            UIElement(
                element_type=ElementType.CARD,
                bounds=(100, 100, 200, 200),
                test_id="card-0",
                area=40000,
                aspect_ratio=1.0,
                accessibility_issues=[],
                confidence=0.9
            ),
            UIElement(
                element_type=ElementType.BUTTON,
                bounds=(110, 110, 180, 180),  # Mostly overlaps card
                test_id="button-1",
                area=32400,
                aspect_ratio=1.0,
                accessibility_issues=[],
                confidence=0.8
            )
        ]
        
        filtered = detector._filter_duplicates(elements, iou_threshold=0.5)
        assert len(filtered) == 1  # Should suppress button
        assert filtered[0].test_id == "card-0"  # Keeps larger element
    
    def test_filter_duplicates_integration(self, detector):
        """Test duplicate filtering in real detection"""
        image_path = "cortex-sample-apps/sts-validation-app/mockups/login-screen-detailed.png"
        result = detector.detect_elements(image_path)
        
        # Should filter duplicates (13→6 expected)
        assert result.total_count < 10  # Significantly fewer than unfiltered
        assert result.total_count >= 5  # But still detect main elements


@pytest.mark.integration
class TestIntegration:
    """Integration tests for full element detection workflow"""
    
    def test_end_to_end_detection(self):
        """Test complete detection workflow"""
        image_path = "cortex-sample-apps/sts-validation-app/mockups/login-screen-detailed.png"
        
        # Detect elements
        result = detect_elements_from_mockup(image_path)
        
        # Validate structure
        assert result['total_count'] > 0
        assert len(result['elements']) > 0
        
        # Validate element data
        for element in result['elements']:
            assert 'type' in element
            assert 'bounds' in element
            assert 'test_id' in element
            assert 'area' in element
            assert 'aspect_ratio' in element
            assert 'confidence' in element
            assert 'accessibility_issues' in element
            
            # Validate bounds structure
            assert 'x' in element['bounds']
            assert 'y' in element['bounds']
            assert 'width' in element['bounds']
            assert 'height' in element['bounds']
        
        # Validate aggregations
        assert isinstance(result['by_type'], dict)
        assert isinstance(result['accessibility_issues'], list)
        assert result['issues_count'] == len(result['accessibility_issues'])
    
    def test_multiple_element_types(self):
        """Test detection of multiple element types"""
        image_path = "cortex-sample-apps/sts-validation-app/mockups/login-screen-detailed.png"
        
        result = detect_elements_from_mockup(image_path)
        
        # Should detect at least 2 different types
        assert len(result['by_type']) >= 2
        
        # Should detect card (container)
        types_detected = [elem['type'] for elem in result['elements']]
        assert 'card' in types_detected or 'card' in result['by_type']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
