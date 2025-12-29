"""
Context Repository - Tier 1-3 Context Items
Manages context item data persistence
"""

from typing import Optional, List
from datetime import datetime

from ..repository import BaseRepository, ISpecification


class ContextItem:
    """
    Context item entity for Tier 1-3 context storage.
    
    Represents contextual information with relevance scoring.
    """
    
    def __init__(
        self,
        context_id: str,
        content: str,
        relevance_score: float,
        namespace: str,
        tier: int,
        source_id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        self.context_id = context_id
        self.content = content
        self.relevance_score = relevance_score
        self.namespace = namespace
        self.tier = tier
        self.source_id = source_id
        self.created_at = created_at or datetime.now()
    
    @classmethod
    def from_db_row(cls, row) -> 'ContextItem':
        """Create ContextItem from database row"""
        return cls(
            context_id=row['context_id'],
            content=row['content'],
            relevance_score=row['relevance_score'],
            namespace=row['namespace'],
            tier=row['tier'],
            source_id=row['source_id'],
            created_at=datetime.fromisoformat(row['created_at'])
        )
    
    def to_db_dict(self) -> dict:
        """Convert ContextItem to database dictionary"""
        return {
            'context_id': self.context_id,
            'content': self.content,
            'relevance_score': self.relevance_score,
            'namespace': self.namespace,
            'tier': self.tier,
            'source_id': self.source_id,
            'created_at': self.created_at.isoformat()
        }


class ContextRepository(BaseRepository[ContextItem]):
    """
    Repository for managing context item persistence.
    
    Provides CRUD operations and specialized queries for context items.
    """
    
    async def get_by_id(self, id: str) -> Optional[ContextItem]:
        """
        Retrieve a context item by ID.
        
        Args:
            id: Context item identifier
            
        Returns:
            ContextItem if found, None otherwise
        """
        row = await self._db_context.fetch_one(
            "SELECT * FROM context_items WHERE context_id = ?",
            (id,)
        )
        
        if row:
            return ContextItem.from_db_row(row)
        return None
    
    async def get_all(self) -> List[ContextItem]:
        """
        Retrieve all context items.
        
        Returns:
            List of all context items
        """
        rows = await self._db_context.fetch_all(
            "SELECT * FROM context_items ORDER BY relevance_score DESC"
        )
        
        return [ContextItem.from_db_row(row) for row in rows]
    
    async def add(self, entity: ContextItem) -> None:
        """
        Add a new context item.
        
        Args:
            entity: ContextItem to add
        """
        await super().add(entity)
        
        data = entity.to_db_dict()
        await self._db_context.execute(
            """
            INSERT INTO context_items (
                context_id, content, relevance_score,
                namespace, tier, source_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data['context_id'],
                data['content'],
                data['relevance_score'],
                data['namespace'],
                data['tier'],
                data['source_id'],
                data['created_at']
            )
        )
    
    async def update(self, entity: ContextItem) -> None:
        """
        Update an existing context item.
        
        Args:
            entity: ContextItem to update
        """
        await super().update(entity)
        
        data = entity.to_db_dict()
        
        await self._db_context.execute(
            """
            UPDATE context_items
            SET content = ?, relevance_score = ?,
                namespace = ?, tier = ?, source_id = ?
            WHERE context_id = ?
            """,
            (
                data['content'],
                data['relevance_score'],
                data['namespace'],
                data['tier'],
                data['source_id'],
                data['context_id']
            )
        )
    
    async def delete(self, entity: ContextItem) -> None:
        """
        Delete a context item.
        
        Args:
            entity: ContextItem to delete
        """
        await super().delete(entity)
        
        await self._db_context.execute(
            "DELETE FROM context_items WHERE context_id = ?",
            (entity.context_id,)
        )
    
    async def get_by_tier(self, tier: int) -> List[ContextItem]:
        """
        Get all context items for a specific tier.
        
        Args:
            tier: Tier number (1, 2, or 3)
            
        Returns:
            List of context items for tier
        """
        rows = await self._db_context.fetch_all(
            """
            SELECT * FROM context_items 
            WHERE tier = ?
            ORDER BY relevance_score DESC
            """,
            (tier,)
        )
        
        return [ContextItem.from_db_row(row) for row in rows]
    
    async def get_by_relevance(self, min_score: float) -> List[ContextItem]:
        """
        Get context items above relevance threshold.
        
        Args:
            min_score: Minimum relevance score
            
        Returns:
            List of high relevance context items
        """
        rows = await self._db_context.fetch_all(
            """
            SELECT * FROM context_items 
            WHERE relevance_score >= ?
            ORDER BY relevance_score DESC
            """,
            (min_score,)
        )
        
        return [ContextItem.from_db_row(row) for row in rows]
    
    async def get_by_namespace(self, namespace: str) -> List[ContextItem]:
        """
        Get all context items in a namespace.
        
        Args:
            namespace: Namespace to filter by
            
        Returns:
            List of context items in namespace
        """
        rows = await self._db_context.fetch_all(
            """
            SELECT * FROM context_items 
            WHERE namespace = ?
            ORDER BY relevance_score DESC
            """,
            (namespace,)
        )
        
        return [ContextItem.from_db_row(row) for row in rows]
    
    async def count(self, spec: Optional[ISpecification[ContextItem]] = None) -> int:
        """
        Count context items, optionally filtered by specification.
        
        Args:
            spec: Optional specification to filter count
            
        Returns:
            Number of context items
        """
        if spec is None:
            row = await self._db_context.fetch_one(
                "SELECT COUNT(*) as count FROM context_items"
            )
            return row['count'] if row else 0
        else:
            # Fall back to base implementation for specification filtering
            return await super().count(spec)
