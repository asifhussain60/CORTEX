"""
CORTEX Tier 1: Working Memory
Short-term memory storage with FIFO queue (20 conversation limit).
"""

import sqlite3
import json
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
class Conversation:
    """Represents a conversation in working memory."""
    conversation_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    is_active: bool
    summary: Optional[str] = None
    tags: Optional[List[str]] = None


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


class WorkingMemory:
    """
    Tier 1: Working Memory (Short-Term Memory)
    
    Manages recent conversations with FIFO eviction when capacity (20) is reached.
    Stores conversations, messages, and extracted entities in SQLite.
    """
    
    MAX_CONVERSATIONS = 20
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize working memory.
        
        Args:
            db_path: Path to SQLite database. If None, uses default location.
        """
        if db_path is None:
            db_path = Path("cortex-brain/tier1/working_memory.db")
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 0,
                summary TEXT,
                tags TEXT
            )
        """)
        
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
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
                FOREIGN KEY (entity_id) REFERENCES entities(id)
            )
        """)
        
        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        """)
        
        # Create eviction log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eviction_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_created 
            ON conversations(created_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_active 
            ON conversations(is_active)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_entities_type 
            ON entities(entity_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_entities_accessed 
            ON entities(last_accessed DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation 
            ON messages(conversation_id)
        """)
        
        conn.commit()
        conn.close()
    
    def add_conversation(
        self,
        conversation_id: str,
        title: str,
        messages: List[Dict[str, str]],
        tags: Optional[List[str]] = None
    ) -> Conversation:
        """
        Add a new conversation to working memory.
        
        Args:
            conversation_id: Unique conversation identifier
            title: Conversation title
            messages: List of message dicts with 'role' and 'content'
            tags: Optional list of tags
        
        Returns:
            Created Conversation object
        """
        # Check if we need to evict (FIFO)
        self._enforce_fifo_limit()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert conversation with explicit timestamp for precision
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO conversations 
            (conversation_id, title, message_count, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            conversation_id,
            title,
            len(messages),
            json.dumps(tags) if tags else None,
            now,
            now
        ))
        
        # Insert messages
        for message in messages:
            cursor.execute("""
                INSERT INTO messages (conversation_id, role, content)
                VALUES (?, ?, ?)
            """, (conversation_id, message['role'], message['content']))
        
        conn.commit()
        
        # Retrieve and return conversation
        conversation = self.get_conversation(conversation_id)
        conn.close()
        
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: Conversation identifier
        
        Returns:
            Conversation object or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_id, title, created_at, updated_at, 
                   message_count, is_active, summary, tags
            FROM conversations
            WHERE conversation_id = ?
        """, (conversation_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return Conversation(
            conversation_id=row[0],
            title=row[1],
            created_at=datetime.fromisoformat(row[2]),
            updated_at=datetime.fromisoformat(row[3]),
            message_count=row[4],
            is_active=bool(row[5]),
            summary=row[6],
            tags=json.loads(row[7]) if row[7] else None
        )
    
    def get_recent_conversations(self, limit: int = 20) -> List[Conversation]:
        """
        Get recent conversations ordered by creation date (newest first).
        
        Args:
            limit: Maximum number of conversations to return
        
        Returns:
            List of Conversation objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_id, title, created_at, updated_at,
                   message_count, is_active, summary, tags
            FROM conversations
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        conversations = []
        for row in rows:
            conversations.append(Conversation(
                conversation_id=row[0],
                title=row[1],
                created_at=datetime.fromisoformat(row[2]),
                updated_at=datetime.fromisoformat(row[3]),
                message_count=row[4],
                is_active=bool(row[5]),
                summary=row[6],
                tags=json.loads(row[7]) if row[7] else None
            ))
        
        return conversations
    
    def set_active_conversation(self, conversation_id: str) -> None:
        """
        Mark a conversation as active.
        
        Args:
            conversation_id: Conversation to mark as active
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Deactivate all conversations first
        cursor.execute("UPDATE conversations SET is_active = 0")
        
        # Activate the specified conversation
        cursor.execute("""
            UPDATE conversations 
            SET is_active = 1, updated_at = CURRENT_TIMESTAMP
            WHERE conversation_id = ?
        """, (conversation_id,))
        
        conn.commit()
        conn.close()
    
    def update_conversation(
        self,
        conversation_id: str,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """
        Update conversation properties.
        
        Args:
            conversation_id: Conversation to update
            title: New title (if provided)
            summary: New summary (if provided)
            tags: New tags (if provided)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        
        if summary is not None:
            updates.append("summary = ?")
            params.append(summary)
        
        if tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps(tags))
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(conversation_id)
            
            sql = f"UPDATE conversations SET {', '.join(updates)} WHERE conversation_id = ?"
            cursor.execute(sql, params)
            conn.commit()
        
        conn.close()
    
    def get_conversation_count(self) -> int:
        """Get the total number of conversations in working memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def _enforce_fifo_limit(self) -> None:
        """
        Enforce FIFO limit of 20 conversations.
        Evicts oldest inactive conversation if at capacity.
        """
        count = self.get_conversation_count()
        
        if count < self.MAX_CONVERSATIONS:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find oldest inactive conversation
        cursor.execute("""
            SELECT conversation_id
            FROM conversations
            WHERE is_active = 0
            ORDER BY created_at ASC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        
        if row:
            oldest_id = row[0]
            
            # Log eviction event
            cursor.execute("""
                INSERT INTO eviction_log (conversation_id, event_type, details)
                VALUES (?, 'conversation_evicted', 'FIFO eviction - capacity reached')
            """, (oldest_id,))
            
            # Delete the conversation (cascade will handle related records)
            self._delete_conversation(oldest_id, cursor)
            
            conn.commit()
        
        conn.close()
    
    def _delete_conversation(self, conversation_id: str, cursor: sqlite3.Cursor) -> None:
        """
        Delete a conversation and all related data.
        
        Args:
            conversation_id: Conversation to delete
            cursor: Database cursor
        """
        # Delete messages
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        
        # Delete conversation-entity relationships
        cursor.execute("DELETE FROM conversation_entities WHERE conversation_id = ?", (conversation_id,))
        
        # Delete conversation
        cursor.execute("DELETE FROM conversations WHERE conversation_id = ?", (conversation_id,))
    
    def get_eviction_log(self) -> List[Dict[str, Any]]:
        """Get the eviction log."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_id, event_type, timestamp, details
            FROM eviction_log
            ORDER BY timestamp DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'conversation_id': row[0],
                'event_type': row[1],
                'timestamp': row[2],
                'details': row[3]
            }
            for row in rows
        ]
    
    def get_active_conversation(self) -> Optional[Conversation]:
        """Get the currently active conversation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_id
            FROM conversations
            WHERE is_active = 1
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self.get_conversation(row[0])
        return None
    
    def extract_entities(self, conversation_id: str) -> List[Entity]:
        """
        Extract entities from a conversation's messages.
        
        Args:
            conversation_id: Conversation to extract entities from
        
        Returns:
            List of extracted Entity objects
        """
        messages = self.get_messages(conversation_id)
        
        if not messages:
            return []
        
        # Combine all message content
        text = " ".join(msg['content'] for msg in messages)
        
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
    
    def search_conversations(self, keyword: str) -> List[Conversation]:
        """
        Search conversations by keyword in title or messages.
        
        Args:
            keyword: Search keyword
        
        Returns:
            List of matching Conversation objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Search in titles and message content
        cursor.execute("""
            SELECT DISTINCT c.conversation_id
            FROM conversations c
            LEFT JOIN messages m ON c.conversation_id = m.conversation_id
            WHERE c.title LIKE ? OR m.content LIKE ?
        """, (f'%{keyword}%', f'%{keyword}%'))
        
        conversation_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return [self.get_conversation(cid) for cid in conversation_ids]
    
    def find_conversations_with_entity(
        self,
        entity_type: EntityType,
        entity_name: str
    ) -> List[Conversation]:
        """
        Find conversations that mention a specific entity.
        
        Args:
            entity_type: Type of entity
            entity_name: Name of entity
        
        Returns:
            List of Conversation objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT ce.conversation_id
            FROM conversation_entities ce
            JOIN entities e ON ce.entity_id = e.id
            WHERE e.entity_type = ? AND e.entity_name = ?
        """, (entity_type.value, entity_name))
        
        conversation_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return [self.get_conversation(cid) for cid in conversation_ids]
    
    def get_conversations_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Conversation]:
        """
        Get conversations within a date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
        
        Returns:
            List of Conversation objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_id
            FROM conversations
            WHERE created_at BETWEEN ? AND ?
            ORDER BY created_at DESC
        """, (start_date.isoformat(), end_date.isoformat()))
        
        conversation_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return [self.get_conversation(cid) for cid in conversation_ids]
    
    def get_entity_statistics(self) -> List[Dict[str, Any]]:
        """
        Get statistics on entity usage.
        
        Returns:
            List of dicts with entity stats
        """
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
    
    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages for a conversation.
        
        Args:
            conversation_id: Conversation identifier
        
        Returns:
            List of message dicts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT role, content, timestamp
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
        """, (conversation_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'role': row[0],
                'content': row[1],
                'timestamp': row[2]
            }
            for row in rows
        ]
    
    def add_messages(
        self,
        conversation_id: str,
        messages: List[Dict[str, str]]
    ) -> None:
        """
        Append new messages to an existing conversation.
        
        Args:
            conversation_id: Conversation to append to
            messages: List of message dicts with 'role' and 'content'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert messages
        for message in messages:
            cursor.execute("""
                INSERT INTO messages (conversation_id, role, content)
                VALUES (?, ?, ?)
            """, (conversation_id, message['role'], message['content']))
        
        # Update message count and timestamp
        cursor.execute("""
            UPDATE conversations
            SET message_count = message_count + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE conversation_id = ?
        """, (len(messages), conversation_id))
        
        conn.commit()
        conn.close()
    
    def close(self) -> None:
        """Close any open connections (for cleanup in tests)."""
        # SQLite connections are per-operation, so nothing to close
        pass
