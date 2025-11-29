"""
Entity Extractor - Handles entity extraction from conversation content.
"""

import sqlite3
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class EntityType(Enum):
    """Types of entities that can be extracted."""
    FILE = "file"
    CLASS = "class"
    METHOD = "method"
    VARIABLE = "variable"
    CONCEPT = "concept"


@dataclass
class Entity:
    """Represents an extracted entity."""
    id: int
    entity_type: EntityType
    entity_name: str
    file_path: Optional[str]
    first_seen: datetime
    last_accessed: datetime
    access_count: int


class EntityExtractor:
    """Extracts and manages entities from conversations."""
    
    def __init__(self, db_path: Path):
        """
        Initialize entity extractor.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Ensure database schema exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_name TEXT NOT NULL,
                file_path TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 1,
                UNIQUE(entity_type, entity_name, file_path)
            )
        """)
        
        # Create conversation-entity relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_entities (
                conversation_id TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                relevance_score REAL DEFAULT 1.0,
                PRIMARY KEY (conversation_id, entity_id),
                FOREIGN KEY (entity_id) REFERENCES entities(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def extract_entities(self, conversation_id: str, text: str) -> List[Entity]:
        """
        Extract entities from text.
        
        Args:
            conversation_id: Conversation to link entities to
            text: Text to extract entities from
        
        Returns:
            List of extracted Entity objects
        """
        entities = []
        
        # Extract file entities (files with extensions in backticks)
        file_pattern = r'`([a-zA-Z0-9_\-/\\\.]+\.(py|yaml|md|json|txt|js|ts|css|html))`'
        for match in re.finditer(file_pattern, text):
            entity = self._add_or_update_entity(
                entity_type=EntityType.FILE,
                entity_name=match.group(1),
                file_path=None
            )
            self._link_entity_to_conversation(conversation_id, entity.id)
            entities.append(entity)
        
        # Extract class entities (PascalCase in backticks)
        class_pattern = r'`([A-Z][a-zA-Z0-9_]*)`'
        for match in re.finditer(class_pattern, text):
            entity = self._add_or_update_entity(
                entity_type=EntityType.CLASS,
                entity_name=match.group(1),
                file_path=None
            )
            self._link_entity_to_conversation(conversation_id, entity.id)
            entities.append(entity)
        
        # Extract method entities (snake_case with parentheses)
        method_pattern = r'`([a-z_][a-z0-9_]*)\(\)`'
        for match in re.finditer(method_pattern, text):
            entity = self._add_or_update_entity(
                entity_type=EntityType.METHOD,
                entity_name=match.group(1),
                file_path=None
            )
            self._link_entity_to_conversation(conversation_id, entity.id)
            entities.append(entity)
        
        return entities
    
    def _add_or_update_entity(
        self,
        entity_type: EntityType,
        entity_name: str,
        file_path: Optional[str]
    ) -> Entity:
        """Add entity or update if exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Try to get existing entity
        cursor.execute("""
            SELECT id, first_seen, access_count
            FROM entities
            WHERE entity_type = ? AND entity_name = ? AND (file_path = ? OR (file_path IS NULL AND ? IS NULL))
        """, (entity_type.value, entity_name, file_path, file_path))
        
        row = cursor.fetchone()
        
        if row:
            # Update existing entity
            entity_id = row[0]
            cursor.execute("""
                UPDATE entities
                SET last_accessed = CURRENT_TIMESTAMP, access_count = access_count + 1
                WHERE id = ?
            """, (entity_id,))
            conn.commit()
        else:
            # Insert new entity
            cursor.execute("""
                INSERT INTO entities (entity_type, entity_name, file_path)
                VALUES (?, ?, ?)
            """, (entity_type.value, entity_name, file_path))
            entity_id = cursor.lastrowid
            conn.commit()
        
        # Get full entity
        cursor.execute("""
            SELECT id, entity_type, entity_name, file_path, first_seen, last_accessed, access_count
            FROM entities
            WHERE id = ?
        """, (entity_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return Entity(
            id=row[0],
            entity_type=EntityType(row[1]),
            entity_name=row[2],
            file_path=row[3],
            first_seen=datetime.fromisoformat(row[4]),
            last_accessed=datetime.fromisoformat(row[5]),
            access_count=row[6]
        )
    
    def _link_entity_to_conversation(self, conversation_id: str, entity_id: int) -> None:
        """Link an entity to a conversation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO conversation_entities (conversation_id, entity_id)
            VALUES (?, ?)
        """, (conversation_id, entity_id))
        
        conn.commit()
        conn.close()
    
    def get_conversation_entities(self, conversation_id: str) -> List[Entity]:
        """Get all entities associated with a conversation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.id, e.entity_type, e.entity_name, e.file_path, 
                   e.first_seen, e.last_accessed, e.access_count
            FROM entities e
            JOIN conversation_entities ce ON e.id = ce.entity_id
            WHERE ce.conversation_id = ?
        """, (conversation_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            Entity(
                id=row[0],
                entity_type=EntityType(row[1]),
                entity_name=row[2],
                file_path=row[3],
                first_seen=datetime.fromisoformat(row[4]),
                last_accessed=datetime.fromisoformat(row[5]),
                access_count=row[6]
            )
            for row in rows
        ]
    
    def get_entity_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics on entity usage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.entity_type, e.entity_name, e.access_count, 
                   COUNT(DISTINCT ce.conversation_id) as conversation_count
            FROM entities e
            LEFT JOIN conversation_entities ce ON e.id = ce.entity_id
            GROUP BY e.id
            ORDER BY conversation_count DESC, e.access_count DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'entity_type': row[0],
                'entity_name': row[1],
                'access_count': row[2],
                'conversation_count': row[3]
            }
            for row in rows
        ]
