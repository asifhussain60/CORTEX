"""
Expression-based specifications using lambda functions.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

from typing import TypeVar, Callable
from .specification import Specification

T = TypeVar('T')


class ExpressionSpecification(Specification[T]):
    """
    Specification based on a lambda expression or callable.
    
    Provides a simple way to create specifications without creating new classes.
    
    Example:
        # Create specification from lambda
        is_adult = ExpressionSpecification(lambda person: person.age >= 18)
        
        # Use in filtering
        adults = [p for p in people if is_adult.is_satisfied_by(p)]
    """
    
    def __init__(self, expression: Callable[[T], bool], description: str = ""):
        """
        Initialize expression specification.
        
        Args:
            expression: Callable that takes an entity and returns bool
            description: Optional description of what the specification checks
        """
        self.expression = expression
        self.description = description
    
    def is_satisfied_by(self, candidate: T) -> bool:
        """
        Check if candidate satisfies the expression.
        
        Args:
            candidate: Entity to check
            
        Returns:
            Result of evaluating the expression
        """
        try:
            return self.expression(candidate)
        except Exception:
            # If expression throws, specification is not satisfied
            return False
    
    def __repr__(self) -> str:
        """String representation."""
        if self.description:
            return f"ExpressionSpec({self.description})"
        return "ExpressionSpec"
