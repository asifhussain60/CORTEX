"""Validator Registry - Maps request types to validators"""
from typing import Dict, Type, Optional
from src.application.common.interfaces import IRequest
from src.application.validation.validator import Validator
from src.application.validation.conversation_validators import (
    CaptureConversationValidator,
    LearnPatternValidator,
    UpdateContextRelevanceValidator,
    UpdatePatternConfidenceValidator
)
from src.application.validation.conversation_query_validators import (
    SearchContextQueryValidator,
    GetConversationQualityQueryValidator,
    FindSimilarPatternsQueryValidator
)


class ValidatorRegistry:
    """Central registry for request validators
    
    This registry maps request types to their corresponding validators.
    Used by ValidationBehavior to automatically find and execute validators.
    
    Benefits:
    - Decouples ValidationBehavior from specific validator implementations
    - Makes it easy to add new validators without modifying pipeline code
    - Provides type-safe validator lookup
    - Enables validator reuse across different contexts
    
    Usage:
        registry = ValidatorRegistry()
        validator = registry.get_validator(CaptureConversationCommand)
        if validator:
            result = validator.validate(command)
    """
    
    def __init__(self):
        """Initialize validator registry with default validators"""
        self._validators: Dict[str, Validator] = {}
        self._register_default_validators()
    
    def _register_default_validators(self):
        """Register all built-in validators"""
        # Command validators
        self.register('CaptureConversationCommand', CaptureConversationValidator())
        self.register('LearnPatternCommand', LearnPatternValidator())
        self.register('UpdateContextRelevanceCommand', UpdateContextRelevanceValidator())
        self.register('UpdatePatternConfidenceCommand', UpdatePatternConfidenceValidator())
        
        # Query validators
        self.register('SearchContextQuery', SearchContextQueryValidator())
        self.register('GetConversationQualityQuery', GetConversationQualityQueryValidator())
        self.register('FindSimilarPatternsQuery', FindSimilarPatternsQueryValidator())
    
    def register(self, request_type_name: str, validator: Validator):
        """Register a validator for a request type
        
        Args:
            request_type_name: Name of the request type (e.g., 'CaptureConversationCommand')
            validator: Validator instance for that request type
        """
        self._validators[request_type_name] = validator
    
    def get_validator(self, request: IRequest) -> Optional[Validator]:
        """Get validator for a request
        
        Args:
            request: Request instance to find validator for
            
        Returns:
            Validator instance if registered, None otherwise
        """
        request_type_name = request.__class__.__name__
        return self._validators.get(request_type_name)
    
    def has_validator(self, request: IRequest) -> bool:
        """Check if validator exists for request type
        
        Args:
            request: Request instance to check
            
        Returns:
            True if validator registered, False otherwise
        """
        request_type_name = request.__class__.__name__
        return request_type_name in self._validators
    
    def unregister(self, request_type_name: str):
        """Remove validator for a request type
        
        Args:
            request_type_name: Name of the request type to unregister
        """
        if request_type_name in self._validators:
            del self._validators[request_type_name]
    
    def clear(self):
        """Remove all registered validators"""
        self._validators.clear()
    
    def get_registered_types(self) -> list[str]:
        """Get list of registered request type names
        
        Returns:
            List of request type names that have validators
        """
        return list(self._validators.keys())


# Global validator registry instance
_global_registry = ValidatorRegistry()


def get_validator_registry() -> ValidatorRegistry:
    """Get the global validator registry instance
    
    Returns:
        Global ValidatorRegistry instance
    """
    return _global_registry
