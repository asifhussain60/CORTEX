"""
Protocol Compliance Verification Module (AC-IKP-001-02).

Provides utilities for verifying that knowledge provider implementations
satisfy the KnowledgeProvider Protocol interface.

Governance:
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
"""

from typing import Type, Any, List, Dict, Tuple, Optional
from src.core.knowledge.protocols import KnowledgeProvider


class ProtocolComplianceError(Exception):
    """Raised when a class does not satisfy the KnowledgeProvider Protocol."""
    pass


class ProtocolComplianceChecker:
    """
    Verifies that classes satisfy the KnowledgeProvider Protocol.
    
    Uses structural inspection to check for required attributes and methods.
    """

    REQUIRED_PROPERTIES = ['is_loaded', 'entry_count', 'domains']
    REQUIRED_METHODS = ['query', 'get_by_domain', 'get_relevant_knowledge']
    REQUIRED_ATTRIBUTES = REQUIRED_PROPERTIES + REQUIRED_METHODS

    @classmethod
    def verify_class(cls, target_class: Type) -> bool:
        """
        Verify that a class satisfies the KnowledgeProvider Protocol.
        
        Args:
            target_class: Class to verify.
            
        Returns:
            bool: True if class satisfies protocol, False otherwise.
            
        Raises:
            TypeError: If target_class is not a class.
        """
        if not isinstance(target_class, type):
            raise TypeError(f"Expected class, got {type(target_class)}")
        
        return cls._check_all_attributes(target_class)

    @classmethod
    def verify_instance(cls, instance: Any) -> bool:
        """
        Verify that an instance satisfies the KnowledgeProvider Protocol.
        
        Args:
            instance: Object instance to verify.
            
        Returns:
            bool: True if instance satisfies protocol, False otherwise.
        """
        return cls._check_all_attributes(instance.__class__)

    @classmethod
    def check_compliance_details(cls, target_class: Type) -> Dict[str, Any]:
        """
        Check compliance and return detailed report.
        
        Args:
            target_class: Class to check.
            
        Returns:
            Dict with compliance details:
            - 'is_compliant': bool
            - 'missing_attributes': List[str]
            - 'missing_properties': List[str]
            - 'missing_methods': List[str]
            - 'errors': List[str]
        """
        result = {
            'is_compliant': False,
            'missing_attributes': [],
            'missing_properties': [],
            'missing_methods': [],
            'errors': [],
        }

        # Check for required properties
        for prop in cls.REQUIRED_PROPERTIES:
            if not hasattr(target_class, prop):
                result['missing_attributes'].append(prop)
                result['missing_properties'].append(prop)
            else:
                # Check if it's actually a property or can act like one
                attr = getattr(target_class, prop, None)
                if attr is None and not hasattr(target_class, f'_{prop}'):
                    result['errors'].append(f"Property {prop} not properly defined")

        # Check for required methods
        for method in cls.REQUIRED_METHODS:
            if not hasattr(target_class, method):
                result['missing_attributes'].append(method)
                result['missing_methods'].append(method)
            else:
                attr = getattr(target_class, method, None)
                if not callable(attr):
                    result['errors'].append(f"Method {method} is not callable")

        result['is_compliant'] = (
            len(result['missing_attributes']) == 0 and
            len(result['errors']) == 0
        )

        return result

    @classmethod
    def _check_all_attributes(cls, target: Any) -> bool:
        """
        Internal method to check all required attributes.
        
        Args:
            target: Class or instance to check.
            
        Returns:
            bool: True if all required attributes present.
        """
        for attr in cls.REQUIRED_ATTRIBUTES:
            if not hasattr(target, attr):
                return False
        return True


def assert_protocol_compliance(target_class: Type) -> None:
    """
    Assert that a class complies with KnowledgeProvider Protocol.
    
    Args:
        target_class: Class to verify.
        
    Raises:
        ProtocolComplianceError: If class does not comply.
    """
    details = ProtocolComplianceChecker.check_compliance_details(target_class)
    
    if not details['is_compliant']:
        error_msg = f"Class {target_class.__name__} does not satisfy KnowledgeProvider Protocol\n"
        if details['missing_attributes']:
            error_msg += f"  Missing: {', '.join(details['missing_attributes'])}\n"
        if details['errors']:
            error_msg += f"  Errors: {', '.join(details['errors'])}"
        raise ProtocolComplianceError(error_msg)


__all__ = [
    'ProtocolComplianceChecker',
    'ProtocolComplianceError',
    'assert_protocol_compliance',
]
