"""Base class for value objects following DDD patterns"""
from abc import ABC, abstractmethod
from typing import Any, Tuple


class ValueObject(ABC):
    """Base class for value objects (immutable domain concepts)
    
    Value objects are:
    - Immutable (use @dataclass(frozen=True))
    - Compared by value not identity
    - Have no identity
    
    Example:
        @dataclass(frozen=True)
        class RelevanceScore(ValueObject):
            value: float
            
            def get_equality_components(self) -> Tuple[Any, ...]:
                return (self.value,)
    """
    
    @abstractmethod
    def get_equality_components(self) -> Tuple[Any, ...]:
        """Return tuple of components used for equality comparison"""
        pass
    
    def __eq__(self, other: object) -> bool:
        """Value objects are equal if all components are equal"""
        if not isinstance(other, self.__class__):
            return False
        return self.get_equality_components() == other.get_equality_components()
    
    def __hash__(self) -> int:
        """Hash based on equality components"""
        return hash(self.get_equality_components())
    
    def __ne__(self, other: object) -> bool:
        """Not equal if any component differs"""
        return not self.__eq__(other)
