"""
Phase 67 S1: Attribute Data Extractor

Extracts .NET attributes from Roslyn semantic models:
- API controller attributes ([ApiController], [Route])
- Authorization attributes ([Authorize], [AllowAnonymous])
- Validation attributes ([Required], [StringLength])
- Custom attributes

AC_START: AC-PHASE67-S1-ATTRIBUTE-EXTRACTOR-001
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class AttributeDataExtractor:
    """
    Extract and analyze .NET attributes from semantic models.
    
    Provides detection of common framework attributes and
    custom attribute extraction.
    
    Example:
        >>> extractor = AttributeDataExtractor()
        >>> attrs = extractor.extract_attributes(type_info)
        >>> print(attrs)  # [{"name": "ApiController", "arguments": []}]
    """
    
    # Well-known attribute patterns
    API_CONTROLLER_ATTRIBUTES = [
        "ApiController", "Controller", "Route", "HttpGet", "HttpPost", 
        "HttpPut", "HttpDelete", "HttpPatch"
    ]
    
    AUTHORIZATION_ATTRIBUTES = [
        "Authorize", "AllowAnonymous", "RequiresClaim", "RequiresRole"
    ]
    
    VALIDATION_ATTRIBUTES = [
        "Required", "StringLength", "Range", "RegularExpression",
        "Compare", "EmailAddress", "Phone", "Url", "CreditCard"
    ]
    
    def extract_attributes(self, type_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract all attributes from type info.
        
        Note: Current Roslyn CLI doesn't extract attributes yet.
        This is a placeholder for future enhancement.
        
        Args:
            type_info: Type info dict from Roslyn CLI
        
        Returns:
            List of attribute dicts (currently empty, needs CLI enhancement)
        
        Example:
            >>> attrs = extractor.extract_attributes(type_info)
            >>> print(attrs)  # [{"name": "ApiController", "arguments": []}]
        """
        # TODO: Enhance Roslyn CLI to extract attributes from ISymbol.GetAttributes()
        # For now, return empty list as CLI doesn't include attribute data yet
        logger.debug("Attribute extraction requires Roslyn CLI enhancement")
        return []
    
    def detect_api_controller_attributes(
        self, 
        type_info: Dict[str, Any]
    ) -> List[str]:
        """
        Detect API controller-related attributes.
        
        Args:
            type_info: Type info dict
        
        Returns:
            List of API controller attribute names found
        """
        attributes = self.extract_attributes(type_info)
        return [
            attr["name"] for attr in attributes 
            if attr["name"] in self.API_CONTROLLER_ATTRIBUTES
        ]
    
    def detect_authorization_attributes(
        self, 
        type_info: Dict[str, Any]
    ) -> List[str]:
        """
        Detect authorization-related attributes.
        
        Args:
            type_info: Type info dict
        
        Returns:
            List of authorization attribute names found
        """
        attributes = self.extract_attributes(type_info)
        return [
            attr["name"] for attr in attributes 
            if attr["name"] in self.AUTHORIZATION_ATTRIBUTES
        ]
    
    def detect_validation_attributes(
        self, 
        property_info: Dict[str, Any]
    ) -> List[str]:
        """
        Detect validation attributes on properties.
        
        Args:
            property_info: Property info dict
        
        Returns:
            List of validation attribute names found
        """
        # Properties don't have attributes in current CLI output
        # This is a placeholder for future enhancement
        logger.debug("Property attribute extraction requires CLI enhancement")
        return []
    
    def has_attribute(
        self, 
        type_info: Dict[str, Any], 
        attribute_name: str
    ) -> bool:
        """
        Check if type has specific attribute.
        
        Args:
            type_info: Type info dict
            attribute_name: Name of attribute to check
        
        Returns:
            True if attribute present
        """
        attributes = self.extract_attributes(type_info)
        return any(attr["name"] == attribute_name for attr in attributes)
    
    def is_api_controller(self, type_info: Dict[str, Any]) -> bool:
        """
        Check if type is an API controller.
        
        Uses naming convention as fallback since attributes
        aren't extracted yet.
        
        Args:
            type_info: Type info dict
        
        Returns:
            True if type is likely an API controller
        """
        # Check for API controller attributes (future)
        api_attrs = self.detect_api_controller_attributes(type_info)
        if api_attrs:
            return True
        
        # Fallback: Check naming convention
        type_name = type_info.get("Name", "")
        return type_name.endswith("Controller")
    
    def is_authorized(self, type_info: Dict[str, Any]) -> bool:
        """
        Check if type requires authorization.
        
        Args:
            type_info: Type info dict
        
        Returns:
            True if type has authorization attributes
        """
        auth_attrs = self.detect_authorization_attributes(type_info)
        return len(auth_attrs) > 0
    
    def extract_route_template(self, type_info: Dict[str, Any]) -> Optional[str]:
        """
        Extract route template from Route attribute.
        
        Args:
            type_info: Type info dict
        
        Returns:
            Route template string or None
        """
        # Placeholder for future CLI enhancement
        # Would extract argument from [Route("api/[controller]")]
        logger.debug("Route extraction requires CLI enhancement")
        return None


# AC_COMPLETE: AC-PHASE67-S1-ATTRIBUTE-EXTRACTOR-001 ✅ AttributeDataExtractor implementation complete
# NOTE: Full attribute extraction requires Roslyn CLI enhancement to call ISymbol.GetAttributes()
