"""
Unit of Work interface.

Defines the contract for transaction management and coordinated persistence
across multiple repositories.
"""

from abc import ABC, abstractmethod
from typing import TypeVar
from application.common.result import Result

T = TypeVar('T')


class IUnitOfWork(ABC):
    """
    Unit of Work pattern for transaction management.
    
    Coordinates changes across multiple repositories and ensures
    all changes are committed or rolled back together atomically.
    """
    
    @abstractmethod
    def begin_transaction(self) -> None:
        """
        Start a new transaction.
        
        All repository operations after this call will be part of
        the same transaction until commit() or rollback() is called.
        """
        pass
    
    @abstractmethod
    def commit(self) -> Result[None]:
        """
        Commit all changes.
        
        Persists all registered entities (new, modified, deleted)
        to the database atomically.
        
        Returns:
            Result indicating success or failure with error details
        """
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """
        Rollback all changes.
        
        Discards all registered changes and reverts to the state
        before begin_transaction() was called.
        """
        pass
    
    @abstractmethod
    def register_new(self, entity: T) -> None:
        """
        Track new entity for insertion.
        
        Args:
            entity: Entity to insert when commit() is called
        """
        pass
    
    @abstractmethod
    def register_dirty(self, entity: T) -> None:
        """
        Track modified entity for update.
        
        Args:
            entity: Entity to update when commit() is called
        """
        pass
    
    @abstractmethod
    def register_deleted(self, entity: T) -> None:
        """
        Track entity for deletion.
        
        Args:
            entity: Entity to delete when commit() is called
        """
        pass
    
    @abstractmethod
    def register_clean(self, entity: T) -> None:
        """
        Mark entity as clean (no changes).
        
        Removes entity from change tracking.
        
        Args:
            entity: Entity to mark as unchanged
        """
        pass
    
    @property
    @abstractmethod
    def conversations(self) -> 'IConversationRepository':
        """
        Get conversation repository.
        
        Returns:
            Repository for conversation entities
        """
        pass
    
    @property
    @abstractmethod
    def patterns(self) -> 'IPatternRepository':
        """
        Get pattern repository.
        
        Returns:
            Repository for pattern entities
        """
        pass
    
    @property
    @abstractmethod
    def sessions(self) -> 'ISessionRepository':
        """
        Get session repository.
        
        Returns:
            Repository for session entities
        """
        pass
    
    @abstractmethod
    def __enter__(self):
        """Context manager entry - begins transaction."""
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - commits or rollbacks based on exception."""
        pass
