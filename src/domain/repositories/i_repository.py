"""
Generic repository interface.

Defines the contract for all repositories in the system.
Provides CRUD operations and specification-based querying.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional
from domain.specifications import ISpecification

T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    """
    Generic repository interface for entity persistence.
    
    All concrete repositories should implement this interface to provide
    consistent data access patterns across the application.
    """
    
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            entity_id: Unique identifier of the entity
            
        Returns:
            Entity instance if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """
        Get all entities.
        
        Returns:
            List of all entities in the repository
        """
        pass
    
    @abstractmethod
    def find(self, spec: ISpecification[T]) -> List[T]:
        """
        Find entities matching specification.
        
        Uses Phase 4 specification pattern for flexible querying.
        
        Args:
            spec: Specification defining the filter criteria
            
        Returns:
            List of entities satisfying the specification
        """
        pass
    
    @abstractmethod
    def add(self, entity: T) -> None:
        """
        Add new entity.
        
        Registers entity for insertion in the unit of work.
        Entity will be persisted when unit of work commits.
        
        Args:
            entity: Entity instance to add
        """
        pass
    
    @abstractmethod
    def update(self, entity: T) -> None:
        """
        Update existing entity.
        
        Registers entity as modified in the unit of work.
        Changes will be persisted when unit of work commits.
        
        Args:
            entity: Entity instance to update
        """
        pass
    
    @abstractmethod
    def delete(self, entity: T) -> None:
        """
        Delete entity.
        
        Registers entity for deletion in the unit of work.
        Entity will be removed when unit of work commits.
        
        Args:
            entity: Entity instance to delete
        """
        pass
    
    @abstractmethod
    def count(self, spec: Optional[ISpecification[T]] = None) -> int:
        """
        Count entities matching specification.
        
        Args:
            spec: Optional specification. If None, counts all entities.
            
        Returns:
            Number of entities satisfying the specification
        """
        pass
    
    @abstractmethod
    def exists(self, spec: ISpecification[T]) -> bool:
        """
        Check if any entity matches specification.
        
        Args:
            spec: Specification defining the criteria
            
        Returns:
            True if at least one entity matches, False otherwise
        """
        pass
    
    @abstractmethod
    def first(self, spec: ISpecification[T]) -> Optional[T]:
        """
        Get first entity matching specification.
        
        Args:
            spec: Specification defining the criteria
            
        Returns:
            First matching entity or None if not found
        """
        pass
