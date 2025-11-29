"""
Tests for CORTEX Vision Extraction Formatter

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import pytest
from src.vision.extraction_formatter import (
    VisionExtractionFormatter,
    ExtractedElement,
    VisionAnalysisResult,
    ConfidenceLevel
)


@pytest.fixture
def sample_elements():
    """Create sample extracted elements"""
    return [
        ExtractedElement(
            element_type='input',
            label='Email Input',
            confidence=0.95,
            attributes={'placeholder': 'Enter email', 'required': True}
        ),
        ExtractedElement(
            element_type='input',
            label='Password Input',
            confidence=0.98,
            attributes={'placeholder': 'Enter password', 'required': True}
        ),
        ExtractedElement(
            element_type='button',
            label='Sign In',
            confidence=0.78,
            attributes={'color': '#4A90E2'}
        ),
        ExtractedElement(
            element_type='logo',
            label='Company Logo',
            confidence=0.42
        ),
        ExtractedElement(
            element_type='checkbox',
            label='Remember Me',
            confidence=0.92
        )
    ]


@pytest.fixture
def sample_result(sample_elements):
    """Create sample vision analysis result"""
    return VisionAnalysisResult(
        image_path='login-mockup.png',
        image_width=1920,
        image_height=1080,
        image_size_kb=245.0,
        extracted_elements=sample_elements,
        inferred_requirements=[
            'User authentication with email/password',
            '"Remember me" session persistence',
            'Password reset flow required',
            'Responsive design (mobile-friendly)'
        ],
        processing_time_ms=2300.0
    )


class TestConfidenceLevels:
    """Test confidence level determination"""
    
    def test_high_confidence(self):
        """Test high confidence threshold"""
        element = ExtractedElement('button', 'Test', 0.95)
        assert element.confidence_level == ConfidenceLevel.HIGH
    
    def test_medium_confidence(self):
        """Test medium confidence threshold"""
        element = ExtractedElement('button', 'Test', 0.75)
        assert element.confidence_level == ConfidenceLevel.MEDIUM
    
    def test_low_confidence(self):
        """Test low confidence threshold"""
        element = ExtractedElement('button', 'Test', 0.45)
        assert element.confidence_level == ConfidenceLevel.LOW
    
    def test_boundary_cases(self):
        """Test exact threshold boundaries"""
        # Exactly 85% should be HIGH
        element_85 = ExtractedElement('button', 'Test', 0.85)
        assert element_85.confidence_level == ConfidenceLevel.HIGH
        
        # Exactly 70% should be MEDIUM
        element_70 = ExtractedElement('button', 'Test', 0.70)
        assert element_70.confidence_level == ConfidenceLevel.MEDIUM


class TestVisionExtractionFormatter:
    """Test vision extraction formatting"""
    
    def test_format_response_header(self, sample_result):
        """Test response header formatting"""
        formatter = VisionExtractionFormatter()
        header = formatter.format_response_header(sample_result)
        
        # Should contain key information
        assert "CORTEX Interactive Planning" in header
        assert "Vision API Active" in header
        assert "login-mockup.png" in header
        assert "1920x1080" in header
        assert "245 KB" in header
    
    def test_format_extracted_elements_with_confidence(self, sample_result):
        """Test element formatting with confidence indicators"""
        formatter = VisionExtractionFormatter()
        elements_str = formatter.format_extracted_elements(sample_result)
        
        # Should contain extracted elements
        assert "Email Input" in elements_str
        assert "Password Input" in elements_str
        assert "Sign In" in elements_str
        
        # Should show confidence indicators
        assert "✅" in elements_str  # High confidence
        assert "⚠️" in elements_str  # Medium confidence
        assert "❓" in elements_str  # Low confidence (logo)
        
        # Should show confidence percentages
        assert "95%" in elements_str
        assert "42%" in elements_str
    
    def test_format_inferred_requirements(self, sample_result):
        """Test requirements formatting"""
        formatter = VisionExtractionFormatter()
        requirements_str = formatter.format_inferred_requirements(sample_result.inferred_requirements)
        
        assert "Inferred Requirements" in requirements_str
        assert "User authentication with email/password" in requirements_str
        assert "Remember me" in requirements_str
        assert "1." in requirements_str  # Numbered list
        assert "2." in requirements_str
    
    def test_format_complete_vision_section(self, sample_result):
        """Test complete vision section formatting"""
        formatter = VisionExtractionFormatter()
        complete = formatter.format_complete_vision_section(sample_result)
        
        # Should contain all sections
        assert "Vision API Active" in complete
        assert "Extracted Elements" in complete
        assert "Inferred Requirements" in complete
        assert "Email Input" in complete
        assert "User authentication" in complete
    
    def test_format_debug_info(self, sample_result):
        """Test debug information formatting"""
        formatter = VisionExtractionFormatter()
        debug = formatter.format_debug_info(sample_result)
        
        # Should contain debug details
        assert "Vision API Debug Info" in debug
        assert "GitHub Copilot Vision API" in debug
        assert "2300" in debug  # Processing time
        assert "Total elements detected: 5" in debug
        
        # Should show confidence breakdown
        assert "High confidence" in debug
        assert "Medium confidence" in debug
        assert "Low confidence" in debug
        
        # Should show warnings for low confidence
        assert "Warnings" in debug
        assert "Company Logo" in debug
    
    def test_format_failure_notice_with_fallback(self):
        """Test failure notice formatting with fallback inference"""
        formatter = VisionExtractionFormatter()
        notice = formatter.format_failure_notice(
            'login-screen.png',
            'API rate limit exceeded',
            'Login functionality'
        )
        
        assert "Vision API Notice" in notice
        assert "currently unavailable" in notice
        assert "Fallback Mode" in notice
        assert "login-screen.png" in notice
        assert "Login functionality" in notice
        assert "Tip:" in notice
    
    def test_format_failure_notice_without_fallback(self):
        """Test failure notice without fallback inference"""
        formatter = VisionExtractionFormatter()
        notice = formatter.format_failure_notice(
            'diagram.png',
            'Service temporarily unavailable'
        )
        
        assert "Vision API Notice" in notice
        assert "Unable to analyze contents automatically" in notice
        assert "manual planning workflow" in notice
    
    def test_element_categorization(self, sample_elements):
        """Test element categorization by type"""
        formatter = VisionExtractionFormatter()
        categorized = formatter._categorize_elements(sample_elements)
        
        # Should group by category
        assert 'Text Fields' in categorized
        assert 'Buttons' in categorized
        assert 'Checkboxes' in categorized
        assert 'Branding' in categorized
        
        # Should have correct counts
        assert len(categorized['Text Fields']) == 2  # Email, Password
        assert len(categorized['Buttons']) == 1  # Sign In
        assert len(categorized['Checkboxes']) == 1  # Remember Me
    
    def test_attribute_formatting(self):
        """Test attribute formatting for elements"""
        formatter = VisionExtractionFormatter()
        
        # Test with placeholder and required
        attrs1 = {'placeholder': 'Enter text', 'required': True}
        formatted1 = formatter._format_attributes(attrs1)
        assert 'placeholder: "Enter text"' in formatted1
        assert 'required' in formatted1
        
        # Test with color
        attrs2 = {'color': '#FF0000'}
        formatted2 = formatter._format_attributes(attrs2)
        assert 'color: #FF0000' in formatted2
        
        # Test empty attributes
        attrs3 = {}
        formatted3 = formatter._format_attributes(attrs3)
        assert formatted3 == ""
    
    def test_confidence_indicators_mapping(self):
        """Test that confidence indicators are correctly mapped"""
        formatter = VisionExtractionFormatter()
        
        indicators = formatter.CONFIDENCE_INDICATORS
        assert indicators[ConfidenceLevel.HIGH] == "✅"
        assert indicators[ConfidenceLevel.MEDIUM] == "⚠️"
        assert indicators[ConfidenceLevel.LOW] == "❓"
    
    def test_element_categories_mapping(self):
        """Test element type to category mapping"""
        formatter = VisionExtractionFormatter()
        
        categories = formatter.ELEMENT_CATEGORIES
        assert categories['button'] == 'Buttons'
        assert categories['input'] == 'Text Fields'
        assert categories['checkbox'] == 'Checkboxes'
        assert categories['logo'] == 'Branding'


class TestExtractedElement:
    """Test ExtractedElement dataclass"""
    
    def test_element_creation(self):
        """Test element creation with all fields"""
        element = ExtractedElement(
            element_type='button',
            label='Submit',
            confidence=0.88,
            attributes={'color': 'blue'}
        )
        
        assert element.element_type == 'button'
        assert element.label == 'Submit'
        assert element.confidence == 0.88
        assert element.attributes['color'] == 'blue'
        assert element.confidence_level == ConfidenceLevel.HIGH


class TestVisionAnalysisResult:
    """Test VisionAnalysisResult dataclass"""
    
    def test_result_creation(self, sample_elements):
        """Test result creation with all fields"""
        result = VisionAnalysisResult(
            image_path='test.png',
            image_width=800,
            image_height=600,
            image_size_kb=150.5,
            extracted_elements=sample_elements,
            inferred_requirements=['Requirement 1'],
            processing_time_ms=1500.0
        )
        
        assert result.image_path == 'test.png'
        assert result.image_width == 800
        assert result.image_height == 600
        assert len(result.extracted_elements) == 5
        assert result.processing_time_ms == 1500.0
        assert result.api_version == "GitHub Copilot Vision API v2.1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
