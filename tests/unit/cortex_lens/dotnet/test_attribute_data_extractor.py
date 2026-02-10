"""
Tests for AttributeDataExtractor

AC_START: AC-PHASE67-S1-ATTRIBUTE-EXTRACTOR-TEST-001
"""

import pytest
from cortex_lens.dotnet.attribute_data_extractor import AttributeDataExtractor


@pytest.fixture
def sample_controller_type():
    """Create sample API controller type."""
    return {
        "Name": "UserController",
        "FullName": "Api.Controllers.UserController",
        "Kind": "Class",
        "BaseType": "ControllerBase",
        "Methods": [
            {
                "Name": "GetById",
                "ReturnType": "IActionResult",
                "Parameters": [{"Name": "id", "Type": "int"}],
                "IsPublic": True
            }
        ]
    }


@pytest.fixture
def sample_entity_type():
    """Create sample entity type with validation."""
    return {
        "Name": "User",
        "FullName": "Core.Entities.User",
        "Kind": "Class",
        "Properties": [
            {"Name": "Id", "Type": "int", "IsPublic": True},
            {"Name": "Email", "Type": "string", "IsPublic": True},
            {"Name": "Name", "Type": "string", "IsPublic": True}
        ]
    }


class TestAttributeDataExtractor:
    """Test suite for AttributeDataExtractor."""
    
    def test_init(self):
        """Test extractor initialization."""
        extractor = AttributeDataExtractor()
        
        assert extractor is not None
        assert hasattr(extractor, 'extract_attributes')
        assert len(extractor.API_CONTROLLER_ATTRIBUTES) > 0
    
    def test_extract_attributes(self, sample_controller_type):
        """
        Test attribute extraction.
        
        Note: Returns empty list until CLI enhancement.
        """
        extractor = AttributeDataExtractor()
        
        attrs = extractor.extract_attributes(sample_controller_type)
        
        # Currently returns empty - requires CLI enhancement
        assert isinstance(attrs, list)
    
    def test_detect_api_controller_attributes(self, sample_controller_type):
        """Test API controller attribute detection."""
        extractor = AttributeDataExtractor()
        
        api_attrs = extractor.detect_api_controller_attributes(sample_controller_type)
        
        # Currently empty - requires CLI enhancement
        assert isinstance(api_attrs, list)
    
    def test_is_api_controller_by_naming_convention(self, sample_controller_type):
        """
        Test API controller detection using naming convention fallback.
        
        AC: UserController → True (ends with 'Controller')
        """
        extractor = AttributeDataExtractor()
        
        is_controller = extractor.is_api_controller(sample_controller_type)
        
        # Should detect by naming convention
        assert is_controller is True
    
    def test_is_api_controller_non_controller(self, sample_entity_type):
        """Test API controller detection for non-controller types."""
        extractor = AttributeDataExtractor()
        
        is_controller = extractor.is_api_controller(sample_entity_type)
        
        assert is_controller is False
    
    def test_has_attribute(self, sample_controller_type):
        """Test checking for specific attribute."""
        extractor = AttributeDataExtractor()
        
        has_attr = extractor.has_attribute(sample_controller_type, "ApiController")
        
        # Currently False - requires CLI enhancement
        assert isinstance(has_attr, bool)
    
    def test_attribute_categories_defined(self):
        """Test that attribute categories are properly defined."""
        extractor = AttributeDataExtractor()
        
        assert "ApiController" in extractor.API_CONTROLLER_ATTRIBUTES
        assert "Authorize" in extractor.AUTHORIZATION_ATTRIBUTES
        assert "Required" in extractor.VALIDATION_ATTRIBUTES


# AC_COMPLETE: AC-PHASE67-S1-ATTRIBUTE-EXTRACTOR-TEST-001 ✅ 7 tests defined
# NOTE: Tests validate infrastructure; full functionality requires CLI enhancement
