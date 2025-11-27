"""
Pattern Repository - Tier 2 Knowledge Graph
Manages pattern data persistence
"""

from typing import Optional, List
from datetime import datetime
import json

from ..repository import BaseRepository, ISpecification


class Pattern:
    """
    Pattern entity for Tier 2 knowledge graph.
    
    Represents learned patterns from conversations.
    """
    
    def __init__(
        self,
        pattern_id: str,
        pattern_name: str,
        pattern_type: str,
        pattern_content: str,
        confidence: float,
        source_conversation_id: str,
        observation_count: int = 1,
        success_rate: float = 1.0,
        tags: Optional[List[str]] = None,
        examples: Optional[List[str]] = None,
        related_patterns: Optional[List[str]] = None,
        learned_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.pattern_id = pattern_id
        self.pattern_name = pattern_name
        self.pattern_type = pattern_type
        self.pattern_content = pattern_content
        self.confidence = confidence
        self.source_conversation_id = source_conversation_id
        self.observation_count = observation_count
        self.success_rate = success_rate
        self.tags = tags or []
        self.examples = examples or []
        self.related_patterns = related_patterns or []
        self.learned_at = learned_at or datetime.now()
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @classmethod
    def from_db_row(cls, row) -> 'Pattern':
        """Create Pattern from database row"""
        # Note: sqlite3.Row doesn't have .get(), use direct access with try/except
        try:
            source_conv_id = row['source_conversation_id'] if 'source_conversation_id' in row.keys() else ''
        except:
            source_conv_id = ''
        
        try:
            observation_count = row['observation_count'] if 'observation_count' in row.keys() else 1
        except:
            observation_count = 1
            
        try:
            success_rate = row['success_rate'] if 'success_rate' in row.keys() else 1.0
        except:
            success_rate = 1.0
            
        try:
            tags = json.loads(row['tags']) if row['tags'] else []
        except:
            tags = []
            
        try:
            learned_at_str = row['learned_at'] if 'learned_at' in row.keys() else row['created_at']
        except:
            learned_at_str = row['created_at']
        
        return cls(
            pattern_id=row['pattern_id'],
            pattern_name=row['name'],
            pattern_type=row['pattern_type'],
            pattern_content=row['context'],
            confidence=row['confidence'],
            source_conversation_id=source_conv_id,
            observation_count=observation_count,
            success_rate=success_rate,
            tags=tags,
            examples=json.loads(row['examples']) if row['examples'] else [],
            related_patterns=json.loads(row['related_patterns']) if row['related_patterns'] else [],
            learned_at=datetime.fromisoformat(learned_at_str),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    def to_db_dict(self) -> dict:
        """Convert Pattern to database dictionary"""
        return {
            'pattern_id': self.pattern_id,
            'name': self.pattern_name,
            'pattern_type': self.pattern_type,
            'context': self.pattern_content,
            'confidence': self.confidence,
            'namespace': 'tier2',  # Patterns are always in Tier 2
            'examples': json.dumps(self.examples),
            'related_patterns': json.dumps(self.related_patterns),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class PatternRepository(BaseRepository[Pattern]):
    """
    Repository for managing pattern persistence.
    
    Provides CRUD operations and specialized queries for patterns.
    """
    
    async def get_by_id(self, id: str) -> Optional[Pattern]:
        """
        Retrieve a pattern by ID.
        
        Args:
            id: Pattern identifier
            
        Returns:
            Pattern if found, None otherwise
        """
        row = await self._db_context.fetch_one(
            "SELECT * FROM patterns WHERE pattern_id = ?",
            (id,)
        )
        
        if row:
            return Pattern.from_db_row(row)
        return None
    
    async def get_all(self) -> List[Pattern]:
        """
        Retrieve all patterns.
        
        Returns:
            List of all patterns
        """
        rows = await self._db_context.fetch_all(
            "SELECT * FROM patterns ORDER BY confidence DESC"
        )
        
        return [Pattern.from_db_row(row) for row in rows]
    
    async def add(self, entity: Pattern) -> None:
        """
        Add a new pattern.
        
        Args:
            entity: Pattern to add
        """
        await super().add(entity)
        
        data = entity.to_db_dict()
        await self._db_context.execute(
            """
            INSERT INTO patterns (
                pattern_id, name, pattern_type, context,
                confidence, namespace, examples, related_patterns,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data['pattern_id'],
                data['name'],
                data['pattern_type'],
                data['context'],
                data['confidence'],
                data['namespace'],
                data['examples'],
                data['related_patterns'],
                data['created_at'],
                data['updated_at']
            )
        )
    
    async def update(self, entity: Pattern) -> None:
        """
        Update an existing pattern.
        
        Args:
            entity: Pattern to update
        """
        await super().update(entity)
        
        entity.updated_at = datetime.now()
        data = entity.to_db_dict()
        
        await self._db_context.execute(
            """
            UPDATE patterns
            SET name = ?, pattern_type = ?, context = ?,
                confidence = ?, namespace = ?, examples = ?,
                related_patterns = ?, updated_at = ?
            WHERE pattern_id = ?
            """,
            (
                data['name'],
                data['pattern_type'],
                data['context'],
                data['confidence'],
                data['namespace'],
                data['examples'],
                data['related_patterns'],
                data['updated_at'],
                data['pattern_id']
            )
        )
    
    async def delete(self, entity: Pattern) -> None:
        """
        Delete a pattern.
        
        Args:
            entity: Pattern to delete
        """
        await super().delete(entity)
        
        await self._db_context.execute(
            "DELETE FROM patterns WHERE pattern_id = ?",
            (entity.pattern_id,)
        )
    
    async def get_by_namespace(self, namespace: str) -> List[Pattern]:
        """
        Get all patterns in a namespace.
        
        Args:
            namespace: Namespace to filter by
            
        Returns:
            List of patterns in namespace
        """
        rows = await self._db_context.fetch_all(
            """
            SELECT * FROM patterns 
            WHERE namespace = ?
            ORDER BY confidence DESC
            """,
            (namespace,)
        )
        
        return [Pattern.from_db_row(row) for row in rows]
    
    async def get_by_confidence(self, min_confidence: float) -> List[Pattern]:
        """
        Get patterns above confidence threshold.
        
        Args:
            min_confidence: Minimum confidence score
            
        Returns:
            List of high confidence patterns
        """
        rows = await self._db_context.fetch_all(
            """
            SELECT * FROM patterns 
            WHERE confidence >= ?
            ORDER BY confidence DESC
            """,
            (min_confidence,)
        )
        
        return [Pattern.from_db_row(row) for row in rows]
    
    async def get_by_type(self, pattern_type: str) -> List[Pattern]:
        """
        Get patterns by type.
        
        Args:
            pattern_type: Type of pattern to retrieve
            
        Returns:
            List of patterns of specified type
        """
        rows = await self._db_context.fetch_all(
            """
            SELECT * FROM patterns 
            WHERE pattern_type = ?
            ORDER BY confidence DESC
            """,
            (pattern_type,)
        )
        
        return [Pattern.from_db_row(row) for row in rows]
    
    async def count(self, spec: Optional[ISpecification[Pattern]] = None) -> int:
        """
        Count patterns, optionally filtered by specification.
        
        Args:
            spec: Optional specification to filter count
            
        Returns:
            Number of patterns
        """
        if spec is None:
            row = await self._db_context.fetch_one(
                "SELECT COUNT(*) as count FROM patterns"
            )
            return row['count'] if row else 0
        else:
            # Fall back to base implementation for specification filtering
            return await super().count(spec)
