"""
Conversation Repository - Tier 1 Working Memory
Manages conversation data persistence
"""

from typing import Optional, List
from datetime import datetime
import json

from ..repository import BaseRepository, ISpecification


class Conversation:
    """
    Conversation entity for Tier 1 working memory.
    
    Represents a captured conversation with quality metrics.
    """
    
    def __init__(
        self,
        conversation_id: str,
        title: str,
        content: str,
        quality: float,
        participant_count: int,
        entity_count: int,
        captured_at: datetime,
        namespace: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.conversation_id = conversation_id
        self.title = title
        self.content = content
        self.quality = quality
        self.participant_count = participant_count
        self.entity_count = entity_count
        self.captured_at = captured_at
        self.namespace = namespace
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @classmethod
    def from_db_row(cls, row) -> 'Conversation':
        """Create Conversation from database row"""
        return cls(
            conversation_id=row['conversation_id'],
            title=row['title'],
            content=row['content'],
            quality=row['quality'],
            participant_count=row['participant_count'],
            entity_count=row['entity_count'],
            captured_at=datetime.fromisoformat(row['captured_at']),
            namespace=row['namespace'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    def to_db_dict(self) -> dict:
        """Convert Conversation to database dictionary"""
        return {
            'conversation_id': self.conversation_id,
            'title': self.title,
            'content': self.content,
            'quality': self.quality,
            'participant_count': self.participant_count,
            'entity_count': self.entity_count,
            'captured_at': self.captured_at.isoformat(),
            'namespace': self.namespace,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ConversationRepository(BaseRepository[Conversation]):
    """
    Repository for managing conversation persistence.
    
    Provides CRUD operations and specialized queries for conversations.
    """
    
    async def get_by_id(self, id: str) -> Optional[Conversation]:
        """
        Retrieve a conversation by ID.
        
        Args:
            id: Conversation identifier
            
        Returns:
            Conversation if found, None otherwise
        """
        row = await self._db_context.fetch_one(
            "SELECT * FROM conversations WHERE conversation_id = ?",
            (id,)
        )
        
        if row:
            return Conversation.from_db_row(row)
        return None
    
    async def get_all(self) -> List[Conversation]:
        """
        Retrieve all conversations.
        
        Returns:
            List of all conversations
        """
        rows = await self._db_context.fetch_all(
            "SELECT * FROM conversations ORDER BY captured_at DESC"
        )
        
        return [Conversation.from_db_row(row) for row in rows]
    
    async def add(self, entity: Conversation) -> None:
        """
        Add a new conversation.
        
        Args:
            entity: Conversation to add
        """
        await super().add(entity)
        
        data = entity.to_db_dict()
        await self._db_context.execute(
            """
            INSERT INTO conversations (
                conversation_id, title, content, quality,
                participant_count, entity_count, captured_at,
                namespace, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data['conversation_id'],
                data['title'],
                data['content'],
                data['quality'],
                data['participant_count'],
                data['entity_count'],
                data['captured_at'],
                data['namespace'],
                data['created_at'],
                data['updated_at']
            )
        )
    
    async def update(self, entity: Conversation) -> None:
        """
        Update an existing conversation.
        
        Args:
            entity: Conversation to update
        """
        await super().update(entity)
        
        entity.updated_at = datetime.now()
        data = entity.to_db_dict()
        
        await self._db_context.execute(
            """
            UPDATE conversations
            SET title = ?, content = ?, quality = ?,
                participant_count = ?, entity_count = ?,
                captured_at = ?, namespace = ?, updated_at = ?
            WHERE conversation_id = ?
            """,
            (
                data['title'],
                data['content'],
                data['quality'],
                data['participant_count'],
                data['entity_count'],
                data['captured_at'],
                data['namespace'],
                data['updated_at'],
                data['conversation_id']
            )
        )
    
    async def delete(self, entity: Conversation) -> None:
        """
        Delete a conversation.
        
        Args:
            entity: Conversation to delete
        """
        await super().delete(entity)
        
        await self._db_context.execute(
            "DELETE FROM conversations WHERE conversation_id = ?",
            (entity.conversation_id,)
        )
    
    async def get_by_namespace(self, namespace: str) -> List[Conversation]:
        """
        Get all conversations in a namespace.
        
        Args:
            namespace: Namespace to filter by
            
        Returns:
            List of conversations in namespace
        """
        rows = await self._db_context.fetch_all(
            """
            SELECT * FROM conversations 
            WHERE namespace = ?
            ORDER BY captured_at DESC
            """,
            (namespace,)
        )
        
        return [Conversation.from_db_row(row) for row in rows]
    
    async def get_high_quality(self, threshold: float = 0.70) -> List[Conversation]:
        """
        Get high quality conversations above threshold.
        
        Args:
            threshold: Minimum quality score (default: 0.70)
            
        Returns:
            List of high quality conversations
        """
        rows = await self._db_context.fetch_all(
            """
            SELECT * FROM conversations 
            WHERE quality >= ?
            ORDER BY quality DESC, captured_at DESC
            """,
            (threshold,)
        )
        
        return [Conversation.from_db_row(row) for row in rows]
    
    async def count(self, spec: Optional[ISpecification[Conversation]] = None) -> int:
        """
        Count conversations, optionally filtered by specification.
        
        Args:
            spec: Optional specification to filter count
            
        Returns:
            Number of conversations
        """
        if spec is None:
            row = await self._db_context.fetch_one(
                "SELECT COUNT(*) as count FROM conversations"
            )
            return row['count'] if row else 0
        else:
            # Fall back to base implementation for specification filtering
            return await super().count(spec)
