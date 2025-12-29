"""
Generic Repository Interface
Based on Repository Pattern from Domain-Driven Design
"""

from typing import Protocol, TypeVar, Optional, List, Generic
from abc import abstractmethod

T = TypeVar('T')


class ISpecification(Protocol[T]):
    """Specification interface for query filtering"""
    
    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if candidate satisfies this specification"""
        ...


class IRepository(Protocol[T]):
    """
    Generic repository interface for data access.
    
    Type Parameters:
        T: The entity type this repository manages
    
    Example:
        class IConversationRepository(IRepository[Conversation]):
            async def get_by_namespace(self, namespace: str) -> List[Conversation]:
                ...
    """
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """
        Retrieve an entity by its unique identifier.
        
        Args:
            id: The entity's unique identifier
            
        Returns:
            The entity if found, None otherwise
        """
        ...
    
    @abstractmethod
    async def get_all(self) -> List[T]:
        """
        Retrieve all entities of this type.
        
        Returns:
            List of all entities (may be empty)
        """
        ...
    
    @abstractmethod
    async def find(self, spec: ISpecification[T]) -> List[T]:
        """
        Find entities matching a specification.
        
        Args:
            spec: Specification defining search criteria
            
        Returns:
            List of matching entities (may be empty)
            
        Example:
            high_quality = HighQualityConversationSpec()
            conversations = await repo.find(high_quality)
        """
        ...
    
    @abstractmethod
    async def add(self, entity: T) -> None:
        """
        Add a new entity to the repository.
        
        Args:
            entity: The entity to add
            
        Note:
            Changes are not persisted until commit() is called on the Unit of Work
        """
        ...
    
    @abstractmethod
    async def update(self, entity: T) -> None:
        """
        Update an existing entity.
        
        Args:
            entity: The entity to update
            
        Note:
            Changes are not persisted until commit() is called on the Unit of Work
        """
        ...
    
    @abstractmethod
    async def delete(self, entity: T) -> None:
        """
        Delete an entity from the repository.
        
        Args:
            entity: The entity to delete
            
        Note:
            Changes are not persisted until commit() is called on the Unit of Work
        """
        ...
    
    @abstractmethod
    async def count(self, spec: Optional[ISpecification[T]] = None) -> int:
        """
        Count entities, optionally filtered by specification.
        
        Args:
            spec: Optional specification to filter count
            
        Returns:
            Number of entities (matching specification if provided)
            
        Example:
            total = await repo.count()
            high_quality_count = await repo.count(HighQualityConversationSpec())
        """
        ...


class BaseRepository(Generic[T]):
    """
    Base repository implementation with common functionality.
    
    Concrete repositories should inherit from this and implement
    entity-specific methods.
    """
    
    def __init__(self, db_context):
        """
        Initialize repository with database context.
        
        Args:
            db_context: Database context/session for data access
        """
        self._db_context = db_context
        self._entities: List[T] = []  # In-memory tracking for Unit of Work
    
    async def get_by_id(self, id: str) -> Optional[T]:
        """Default implementation - override in concrete repositories"""
        raise NotImplementedError("Concrete repository must implement get_by_id")
    
    async def get_all(self) -> List[T]:
        """Default implementation - override in concrete repositories"""
        raise NotImplementedError("Concrete repository must implement get_all")
    
    async def find(self, spec: ISpecification[T]) -> List[T]:
        """Default implementation using in-memory filtering"""
        all_entities = await self.get_all()
        return [e for e in all_entities if spec.is_satisfied_by(e)]
    
    async def add(self, entity: T) -> None:
        """Track entity for insertion"""
        self._entities.append(entity)
    
    async def update(self, entity: T) -> None:
        """Track entity for update"""
        # In a real implementation, this would mark the entity as modified
        pass
    
    async def delete(self, entity: T) -> None:
        """Track entity for deletion"""
        if entity in self._entities:
            self._entities.remove(entity)
    
    async def count(self, spec: Optional[ISpecification[T]] = None) -> int:
        """Count entities, optionally filtered"""
        if spec is None:
            all_entities = await self.get_all()
            return len(all_entities)
        else:
            matching = await self.find(spec)
            return len(matching)
