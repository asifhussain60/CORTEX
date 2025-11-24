"""
Conversation Manager - Handles conversation CRUD and lifecycle operations.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass


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
    semantic_elements: Optional[str] = None  # JSON string containing semantic data


class ConversationManager:
    """Manages conversation CRUD operations and lifecycle."""
    
    def __init__(self, db_path: Path):
        """
        Initialize conversation manager.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Ensure database schema exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='conversations'
        """)
        
        if not cursor.fetchone():
            # Create schema
            cursor.execute("""
                CREATE TABLE conversations (
                    conversation_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    tags TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    summary TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE entities (
                    entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_value TEXT NOT NULL,
                    detected_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )
            """)
            
            conn.commit()
        
        conn.close()
    
    def add_conversation(
        self,
        conversation_id: str,
        title: str,
        message_count: int = 0,
        tags: Optional[List[str]] = None
    ) -> Conversation:
        """
        Add a new conversation.
        
        Args:
            conversation_id: Unique conversation identifier
            title: Conversation title
            message_count: Initial message count
            tags: Optional list of tags
        
        Returns:
            Created Conversation object
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO conversations 
            (conversation_id, title, message_count, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            conversation_id,
            title,
            message_count,
            json.dumps(tags) if tags else None,
            now,
            now
        ))
        
        conn.commit()
        conn.close()
        
        return self.get_conversation(conversation_id)
    
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
                   message_count, is_active, summary, tags, semantic_elements
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
                tags=json.loads(row[7]) if row[7] else None,
                semantic_elements=row[8] if len(row) > 8 else None
            ))
        
        return conversations
    
    def set_active_conversation(self, conversation_id: str) -> None:
        """
        Mark a conversation as active (deactivates all others).
        
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
    
    def increment_message_count(self, conversation_id: str, count: int = 1) -> None:
        """
        Increment the message count for a conversation.
        
        Args:
            conversation_id: Conversation to update
            count: Number to increment by
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE conversations
            SET message_count = message_count + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE conversation_id = ?
        """, (count, conversation_id))
        
        conn.commit()
        conn.close()
    
    def get_conversation_count(self) -> int:
        """Get the total number of conversations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def delete_conversation(self, conversation_id: str) -> None:
        """
        Delete a conversation and all related data.
        
        Args:
            conversation_id: Conversation to delete
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete messages
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        
        # Delete conversation-entity relationships
        cursor.execute("DELETE FROM conversation_entities WHERE conversation_id = ?", (conversation_id,))
        
        # Delete conversation
        cursor.execute("DELETE FROM conversations WHERE conversation_id = ?", (conversation_id,))
        
        conn.commit()
        conn.close()
