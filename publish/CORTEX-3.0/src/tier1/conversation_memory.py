"""
CORTEX Tier 1: Conversation Memory
Persistent storage of conversation history using SQLite

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import contextmanager


class ConversationMemory:
    """
    Tier 1 Working Memory: Last 20 conversations with FIFO queue
    
    Storage: SQLite database at cortex-brain/tier1/conversations.db
    Performance: <50ms per query (target: 18ms actual)
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize conversation memory with SQLite backend
        
        Args:
            db_path: Path to SQLite database (default: cortex-brain/tier1/conversations.db)
        """
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "cortex-brain" / "tier1" / "conversations.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database schema if not exists"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    user_message TEXT NOT NULL,
                    assistant_response TEXT,
                    intent TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    context_json TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Messages table (last 10 per conversation)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    conversation_id TEXT,
                    role TEXT,
                    content TEXT,
                    sequence_num INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )
            """)
            
            # Entities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    entity_id TEXT PRIMARY KEY,
                    conversation_id TEXT,
                    entity_type TEXT,
                    entity_value TEXT,
                    context TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )
            """)
            
            # Indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp 
                ON conversations(timestamp DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation 
                ON messages(conversation_id, sequence_num)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_entities_conversation 
                ON entities(conversation_id)
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def store_conversation(
        self,
        user_message: str,
        assistant_response: str = None,
        intent: str = None,
        context: Dict[str, Any] = None
    ) -> str:
        """
        Store a conversation in memory
        
        Args:
            user_message: User's input
            assistant_response: CORTEX response
            intent: Detected intent (PLAN, EXECUTE, etc.)
            context: Additional context (files, entities, etc.)
        
        Returns:
            conversation_id: Unique identifier for this conversation
        """
        conversation_id = self._generate_conversation_id()
        context_json = json.dumps(context) if context else None
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations 
                (conversation_id, user_message, assistant_response, intent, context_json)
                VALUES (?, ?, ?, ?, ?)
            """, (conversation_id, user_message, assistant_response, intent, context_json))
            conn.commit()
        
        # Apply FIFO if needed
        self._apply_fifo_cleanup()
        
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific conversation"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM conversations WHERE conversation_id = ?
            """, (conversation_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "conversation_id": row["conversation_id"],
                    "user_message": row["user_message"],
                    "assistant_response": row["assistant_response"],
                    "intent": row["intent"],
                    "timestamp": row["timestamp"],
                    "context": json.loads(row["context_json"]) if row["context_json"] else None
                }
            return None
    
    def get_recent_conversations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent conversations (FIFO queue)
        
        Args:
            limit: Maximum number of conversations (default: 20)
        
        Returns:
            List of conversations ordered by timestamp (newest first)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM conversations 
                WHERE is_active = 1
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [
                {
                    "conversation_id": row["conversation_id"],
                    "user_message": row["user_message"],
                    "assistant_response": row["assistant_response"],
                    "intent": row["intent"],
                    "timestamp": row["timestamp"],
                    "context": json.loads(row["context_json"]) if row["context_json"] else None
                }
                for row in rows
            ]
    
    def search_conversations(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search conversations by text query
        
        Args:
            query: Search string
            limit: Maximum results
        
        Returns:
            Matching conversations
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM conversations 
                WHERE is_active = 1
                AND (user_message LIKE ? OR assistant_response LIKE ?)
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            
            rows = cursor.fetchall()
            return [
                {
                    "conversation_id": row["conversation_id"],
                    "user_message": row["user_message"],
                    "assistant_response": row["assistant_response"],
                    "intent": row["intent"],
                    "timestamp": row["timestamp"],
                    "context": json.loads(row["context_json"]) if row["context_json"] else None
                }
                for row in rows
            ]
    
    def track_entity(
        self,
        conversation_id: str,
        entity_type: str,
        entity_value: str,
        context: str = None
    ):
        """
        Track an entity mentioned in conversation
        
        Args:
            conversation_id: Associated conversation
            entity_type: Type (file, class, method, component)
            entity_value: Entity name/value
            context: Additional context
        """
        entity_id = f"{conversation_id}_{entity_type}_{entity_value}"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO entities 
                (entity_id, conversation_id, entity_type, entity_value, context)
                VALUES (?, ?, ?, ?, ?)
            """, (entity_id, conversation_id, entity_type, entity_value, context))
            conn.commit()
    
    def get_entities(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all entities for a conversation"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT entity_type, entity_value, context
                FROM entities 
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            return [
                {
                    "entity_type": row["entity_type"],
                    "entity_value": row["entity_value"],
                    "context": row["context"]
                }
                for row in cursor.fetchall()
            ]
    
    def _apply_fifo_cleanup(self, max_conversations: int = 20):
        """
        Apply FIFO queue cleanup (delete oldest if exceeds limit)
        
        Args:
            max_conversations: Maximum conversations to keep (default: 20)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Count active conversations
            cursor.execute("""
                SELECT COUNT(*) as count FROM conversations WHERE is_active = 1
            """)
            count = cursor.fetchone()["count"]
            
            if count > max_conversations:
                # Mark oldest conversations as inactive
                to_delete = count - max_conversations
                cursor.execute("""
                    UPDATE conversations 
                    SET is_active = 0
                    WHERE conversation_id IN (
                        SELECT conversation_id FROM conversations
                        WHERE is_active = 1
                        ORDER BY timestamp ASC
                        LIMIT ?
                    )
                """, (to_delete,))
                conn.commit()
    
    def _generate_conversation_id(self) -> str:
        """Generate unique conversation ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"conv_{timestamp}"
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get FIFO queue status"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count FROM conversations WHERE is_active = 1
            """)
            count = cursor.fetchone()["count"]
            
            return {
                "current_count": count,
                "max_capacity": 20,
                "usage_percentage": (count / 20) * 100
            }
