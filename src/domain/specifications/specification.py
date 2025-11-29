"""
Specification Pattern for complex domain queries and business rules.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')


class ISpecification(ABC, Generic[T]):
    """
    Interface for specifications that encapsulate business rules and query logic.
    
    Specifications can be combined using logical operators (And, Or, Not) to create
    complex filtering rules while keeping business logic separate from data access.
    
    Example:
        high_quality = HighQualityConversationSpec()
        recent = RecentConversationSpec(days=7)
        
        # Compose specifications
        spec = high_quality.and_(recent)
        
        # Use for filtering
        filtered = [c for c in conversations if spec.is_satisfied_by(c)]
    """
    
    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """
        Check if the candidate entity satisfies this specification.
        
        Args:
            candidate: The entity to check
            
        Returns:
            True if the candidate satisfies the specification, False otherwise
        """
        pass
    
    def and_(self, other: "ISpecification[T]") -> "ISpecification[T]":
        """
        Combine this specification with another using AND logic.
        
        Args:
            other: The specification to combine with
            
        Returns:
            A new specification that requires both to be satisfied
        """
        from .composite_specification import AndSpecification
        return AndSpecification(self, other)
    
    def or_(self, other: "ISpecification[T]") -> "ISpecification[T]":
        """
        Combine this specification with another using OR logic.
        
        Args:
            other: The specification to combine with
            
        Returns:
            A new specification that requires either to be satisfied
        """
        from .composite_specification import OrSpecification
        return OrSpecification(self, other)
    
    def not_(self) -> "ISpecification[T]":
        """
        Negate this specification.
        
        Returns:
            A new specification that requires this to NOT be satisfied
        """
        from .composite_specification import NotSpecification
        return NotSpecification(self)
    
    def __and__(self, other: "ISpecification[T]") -> "ISpecification[T]":
        """Support & operator for composition."""
        return self.and_(other)
    
    def __or__(self, other: "ISpecification[T]") -> "ISpecification[T]":
        """Support | operator for composition."""
        return self.or_(other)
    
    def __invert__(self) -> "ISpecification[T]":
        """Support ~ operator for negation."""
        return self.not_()


class Specification(ISpecification[T], ABC):
    """
    Base class for specifications providing default operator implementations.
    """
    pass
