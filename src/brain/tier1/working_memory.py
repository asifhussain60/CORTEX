"""
Tier 1: Working Memory for CORTEX 4.0

Manages short-term conversation history with FIFO enforcement.
- Storage: {workspace}/cortex-brain/tier1/conversations.db (per-repo)
- Capacity: 70 conversations max (configurable)
- Features: FIFO queue, conversation CRUD, message tracking

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from dataclasses import dataclass
import uuid
import json


@dataclass
class Conversation:
    """Conversation data model."""
    conversation_id: str
    agent_id: str
    start_time: datetime
    end_time: Optional[datetime]
    goal: Optional[str]
    outcome: Optional[str]
    status: str
    metadata: Dict[str, Any]


@dataclass
class Message:
    """Message data model."""
    message_id: str
    conversation_id: str
    role: str
    content: str
    timestamp: datetime
    tokens: int
    metadata: Dict[str, Any]


class WorkingMemory:
    """
    Tier 1: Working Memory - Short-term conversation storage
    
    Features:
    - FIFO queue (configurable max conversations)
    - Conversation lifecycle management
    - Message storage and retrieval
    - Automatic old conversation cleanup
    
    Usage:
        memory = WorkingMemory(db_path, max_conversations=70)
        
        # Create conversation
        conv_id = memory.create_conversation(agent_id="planning", goal="Implement feature X")
        
        # Add messages
        memory.add_message(conv_id, role="user", content="Let's start")
        
        # Retrieve
        conversations = memory.get_recent_conversations(limit=10)
    """
    
    def __init__(self, db_path: Path, max_conversations: int = 70):
        """
        Initialize working memory.
        
        Args:
            db_path: Path to conversations.db
            max_conversations: Maximum conversations to retain (FIFO)
        """
        self.db_path = Path(db_path)
        self.max_conversations = max_conversations
        self.logger = logging.getLogger(__name__)
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize schema
        self._initialize_schema()
        
        self.logger.debug(f"Working Memory initialized: {db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _initialize_schema(self):
        """Create database schema if it doesn't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    goal TEXT,
                    outcome TEXT,
                    status TEXT DEFAULT 'active',
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    tokens INTEGER DEFAULT 0,
                    metadata TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )
            """)
            
            # Indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_start_time 
                ON conversations(start_time DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation 
                ON messages(conversation_id, timestamp)
            """)
            
            conn.commit()
    
    def create_conversation(
        self,
        agent_id: str,
        goal: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new conversation.
        
        Args:
            agent_id: Agent identifier
            goal: Conversation goal
            metadata: Additional metadata
            
        Returns:
            Conversation ID
        """
        conversation_id = str(uuid.uuid4())
        start_time = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (conversation_id, agent_id, start_time, goal, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                conversation_id,
                agent_id,
                start_time,
                goal,
                json.dumps(metadata or {})
            ))
            conn.commit()
        
        # Enforce FIFO limit
        self._enforce_fifo_limit()
        
        self.logger.debug(f"Created conversation: {conversation_id}")
        return conversation_id
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tokens: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: Conversation ID
            role: Message role (user, assistant, system)
            content: Message content
            tokens: Token count
            metadata: Additional metadata
            
        Returns:
            Message ID
        """
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (message_id, conversation_id, role, content, timestamp, tokens, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                message_id,
                conversation_id,
                role,
                content,
                timestamp,
                tokens,
                json.dumps(metadata or {})
            ))
            conn.commit()
        
        return message_id
    
    def end_conversation(
        self,
        conversation_id: str,
        outcome: Optional[str] = None
    ):
        """
        Mark a conversation as ended.
        
        Args:
            conversation_id: Conversation ID
            outcome: Conversation outcome
        """
        end_time = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE conversations
                SET end_time = ?, outcome = ?, status = 'completed'
                WHERE conversation_id = ?
            """, (end_time, outcome, conversation_id))
            conn.commit()
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation object or None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM conversations WHERE conversation_id = ?
            """, (conversation_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return Conversation(
                conversation_id=row["conversation_id"],
                agent_id=row["agent_id"],
                start_time=datetime.fromisoformat(row["start_time"]),
                end_time=datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
                goal=row["goal"],
                outcome=row["outcome"],
                status=row["status"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else {}
            )
    
    def get_recent_conversations(self, limit: int = 10) -> List[Conversation]:
        """
        Get recent conversations.
        
        Args:
            limit: Maximum number of conversations
            
        Returns:
            List of conversations
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM conversations
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append(Conversation(
                    conversation_id=row["conversation_id"],
                    agent_id=row["agent_id"],
                    start_time=datetime.fromisoformat(row["start_time"]),
                    end_time=datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
                    goal=row["goal"],
                    outcome=row["outcome"],
                    status=row["status"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {}
                ))
            
            return conversations
    
    def get_messages(self, conversation_id: str) -> List[Message]:
        """
        Get all messages for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of messages
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
            """, (conversation_id,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append(Message(
                    message_id=row["message_id"],
                    conversation_id=row["conversation_id"],
                    role=row["role"],
                    content=row["content"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    tokens=row["tokens"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {}
                ))
            
            return messages
    
    def get_conversation_count(self) -> int:
        """
        Get total conversation count.
        
        Returns:
            Number of conversations
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversations")
            return cursor.fetchone()[0]
    
    def _enforce_fifo_limit(self):
        """Enforce FIFO limit by removing oldest conversations."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Count conversations
            cursor.execute("SELECT COUNT(*) FROM conversations")
            count = cursor.fetchone()[0]
            
            if count > self.max_conversations:
                # Get oldest conversation IDs to delete
                to_delete = count - self.max_conversations
                cursor.execute("""
                    SELECT conversation_id FROM conversations
                    ORDER BY start_time ASC
                    LIMIT ?
                """, (to_delete,))
                
                old_conversations = [row[0] for row in cursor.fetchall()]
                
                # Delete messages first (foreign key)
                cursor.execute(f"""
                    DELETE FROM messages
                    WHERE conversation_id IN ({','.join('?' * len(old_conversations))})
                """, old_conversations)
                
                # Delete conversations
                cursor.execute(f"""
                    DELETE FROM conversations
                    WHERE conversation_id IN ({','.join('?' * len(old_conversations))})
                """, old_conversations)
                
                conn.commit()
                self.logger.info(f"FIFO: Removed {to_delete} old conversations")
    
    def close(self):
        """Close working memory (cleanup)."""
        self.logger.debug("Working Memory closed")
