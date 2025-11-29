"""
Base repository implementation.

Provides generic repository functionality that concrete repositories can inherit.
"""

from typing import TypeVar, Generic, List, Optional, Type
from domain.repositories import IRepository
from domain.specifications import ISpecification
from infrastructure.database.sqlite_connection import get_connection

T = TypeVar('T')


class RepositoryBase(IRepository[T], Generic[T]):
    """
    Base implementation of repository pattern.
    
    Provides common CRUD operations and specification-based querying.
    Concrete repositories should inherit from this class and provide
    entity-specific implementations.
    """
    
    def __init__(self, entity_type: Type[T], table_name: str, unit_of_work: 'IUnitOfWork' = None):
        """
        Initialize repository.
        
        Args:
            entity_type: Type of entity managed by this repository
            table_name: Database table name for the entity
            unit_of_work: Optional unit of work for change tracking
        """
        self._entity_type = entity_type
        self._table_name = table_name
        self._unit_of_work = unit_of_work
    
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {self._table_name} WHERE id = ?", (entity_id,))
        row = cursor.fetchone()
        
        if row:
            return self._map_to_entity(row)
        return None
    
    def get_all(self) -> List[T]:
        """Get all entities."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {self._table_name}")
        rows = cursor.fetchall()
        
        return [self._map_to_entity(row) for row in rows]
    
    def find(self, spec: ISpecification[T]) -> List[T]:
        """
        Find entities matching specification.
        
        This implementation retrieves all entities and filters in memory.
        Concrete repositories can override for SQL-based filtering.
        """
        all_entities = self.get_all()
        return [entity for entity in all_entities if spec.is_satisfied_by(entity)]
    
    def add(self, entity: T) -> None:
        """Add new entity."""
        if self._unit_of_work:
            self._unit_of_work.register_new(entity)
        else:
            # Direct insert if no unit of work
            self._insert_entity(entity)
    
    def update(self, entity: T) -> None:
        """Update existing entity."""
        if self._unit_of_work:
            self._unit_of_work.register_dirty(entity)
        else:
            # Direct update if no unit of work
            self._update_entity(entity)
    
    def delete(self, entity: T) -> None:
        """Delete entity."""
        if self._unit_of_work:
            self._unit_of_work.register_deleted(entity)
        else:
            # Direct delete if no unit of work
            self._delete_entity(entity)
    
    def count(self, spec: Optional[ISpecification[T]] = None) -> int:
        """Count entities matching specification."""
        if spec is None:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {self._table_name}")
            return cursor.fetchone()[0]
        else:
            # Filter in memory
            return len(self.find(spec))
    
    def exists(self, spec: ISpecification[T]) -> bool:
        """Check if any entity matches specification."""
        return self.first(spec) is not None
    
    def first(self, spec: ISpecification[T]) -> Optional[T]:
        """Get first entity matching specification."""
        matching = self.find(spec)
        return matching[0] if matching else None
    
    def _map_to_entity(self, row) -> T:
        """
        Map database row to entity.
        
        Must be implemented by concrete repositories.
        
        Args:
            row: Database row tuple or dict
            
        Returns:
            Entity instance
        """
        raise NotImplementedError("Concrete repository must implement _map_to_entity")
    
    def _insert_entity(self, entity: T) -> None:
        """
        Insert entity into database.
        
        Must be implemented by concrete repositories.
        
        Args:
            entity: Entity to insert
        """
        raise NotImplementedError("Concrete repository must implement _insert_entity")
    
    def _update_entity(self, entity: T) -> None:
        """
        Update entity in database.
        
        Must be implemented by concrete repositories.
        
        Args:
            entity: Entity to update
        """
        raise NotImplementedError("Concrete repository must implement _update_entity")
    
    def _delete_entity(self, entity: T) -> None:
        """
        Delete entity from database.
        
        Must be implemented by concrete repositories.
        
        Args:
            entity: Entity to delete
        """
        raise NotImplementedError("Concrete repository must implement _delete_entity")
