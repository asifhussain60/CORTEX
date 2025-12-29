"""
Unit of Work Pattern Implementation
Coordinates multiple repository operations in a single transaction
"""

from typing import Protocol
from abc import abstractmethod


class IUnitOfWork(Protocol):
    """
    Unit of Work interface for transactional data access.
    
    Provides access to repositories and transaction management.
    Use as a context manager to ensure proper commit/rollback.
    
    Example:
        async with unit_of_work as uow:
            conv = await uow.conversations.get_by_id("conv_123")
            conv.quality = ConversationQuality(0.95)
            await uow.conversations.update(conv)
            
            pattern = Pattern(...)
            await uow.patterns.add(pattern)
            
            await uow.commit()  # Commits both operations atomically
    """
    
    @property
    @abstractmethod
    def conversations(self):
        """Get the conversations repository"""
        ...
    
    @property
    @abstractmethod
    def patterns(self):
        """Get the patterns repository"""
        ...
    
    @property
    @abstractmethod
    def context_items(self):
        """Get the context items repository"""
        ...
    
    @abstractmethod
    async def commit(self) -> None:
        """
        Commit all changes made through repositories.
        
        All operations (add, update, delete) are persisted atomically.
        If any operation fails, all changes are rolled back.
        
        Raises:
            Exception: If commit fails (triggers automatic rollback)
        """
        ...
    
    @abstractmethod
    async def rollback(self) -> None:
        """
        Rollback all pending changes.
        
        Discards all operations performed through repositories
        since the last commit.
        """
        ...
    
    @abstractmethod
    async def __aenter__(self):
        """Enter context manager (start transaction)"""
        ...
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context manager (commit or rollback).
        
        If an exception occurred, rollback is performed automatically.
        Otherwise, changes are committed.
        """
        ...


class UnitOfWork:
    """
    Concrete Unit of Work implementation.
    
    Coordinates database operations across multiple repositories
    within a single transaction boundary.
    """
    
    def __init__(self, db_context):
        """
        Initialize Unit of Work with database context.
        
        Args:
            db_context: Database context/session for transaction management
        """
        self._db_context = db_context
        self._conversations_repo = None
        self._patterns_repo = None
        self._context_items_repo = None
        self._is_committed = False
    
    @property
    def conversations(self):
        """Get the conversations repository (lazy initialization)"""
        if self._conversations_repo is None:
            from .repositories.conversation_repository import ConversationRepository
            self._conversations_repo = ConversationRepository(self._db_context)
        return self._conversations_repo
    
    @property
    def patterns(self):
        """Get the patterns repository (lazy initialization)"""
        if self._patterns_repo is None:
            from .repositories.pattern_repository import PatternRepository
            self._patterns_repo = PatternRepository(self._db_context)
        return self._patterns_repo
    
    @property
    def context_items(self):
        """Get the context items repository (lazy initialization)"""
        if self._context_items_repo is None:
            from .repositories.context_repository import ContextRepository
            self._context_items_repo = ContextRepository(self._db_context)
        return self._context_items_repo
    
    async def commit(self) -> None:
        """Commit all changes to the database"""
        try:
            await self._db_context.commit()
            self._is_committed = True
        except Exception as ex:
            await self.rollback()
            raise Exception(f"Commit failed: {str(ex)}") from ex
    
    async def rollback(self) -> None:
        """Rollback all pending changes"""
        await self._db_context.rollback()
        self._is_committed = False
    
    async def __aenter__(self):
        """Start transaction"""
        await self._db_context.begin()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """End transaction (commit or rollback)"""
        if exc_type is not None:
            # Exception occurred - rollback
            await self.rollback()
        elif not self._is_committed:
            # No explicit commit - rollback by default
            await self.rollback()
        
        await self._db_context.close()
