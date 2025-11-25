"""
Composite specifications for combining specifications with logical operators.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

from typing import TypeVar
from .specification import ISpecification

T = TypeVar('T')


class AndSpecification(ISpecification[T]):
    """
    Specification that combines two specifications with AND logic.
    Both specifications must be satisfied for this to be satisfied.
    """
    
    def __init__(self, left: ISpecification[T], right: ISpecification[T]):
        """
        Initialize AND specification.
        
        Args:
            left: First specification
            right: Second specification
        """
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if candidate satisfies both specifications."""
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"({self.left} AND {self.right})"


class OrSpecification(ISpecification[T]):
    """
    Specification that combines two specifications with OR logic.
    Either specification must be satisfied for this to be satisfied.
    """
    
    def __init__(self, left: ISpecification[T], right: ISpecification[T]):
        """
        Initialize OR specification.
        
        Args:
            left: First specification
            right: Second specification
        """
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if candidate satisfies either specification."""
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"({self.left} OR {self.right})"


class NotSpecification(ISpecification[T]):
    """
    Specification that negates another specification.
    The wrapped specification must NOT be satisfied for this to be satisfied.
    """
    
    def __init__(self, wrapped: ISpecification[T]):
        """
        Initialize NOT specification.
        
        Args:
            wrapped: Specification to negate
        """
        self.wrapped = wrapped
    
    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if candidate does NOT satisfy the wrapped specification."""
        return not self.wrapped.is_satisfied_by(candidate)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"(NOT {self.wrapped})"
