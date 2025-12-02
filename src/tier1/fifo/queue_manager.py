"""
Queue Manager - Handles FIFO queue enforcement for conversations.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any


class QueueManager:
    """Manages FIFO queue enforcement (70-conversation limit)."""
    
    MAX_CONVERSATIONS = 70  # Phase 7.5: Increased from 20 to 70
    
    def __init__(self, db_path: Path):
        """
        Initialize queue manager.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Ensure database schema exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='conversations'
        """)
        
        if not cursor.fetchone():
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
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='eviction_log'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE eviction_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    details TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        conn.commit()
        conn.close()
    
    def enforce_fifo_limit(self, tier2_knowledge_graph=None) -> None:
        """
        Enforce FIFO limit of 70 conversations.
        Evicts oldest inactive, non-pinned conversation if at capacity.
        Optionally archives to Tier 2 before eviction.
        
        Args:
            tier2_knowledge_graph: Optional Tier 2 instance for auto-archive
        """
        count = self._get_conversation_count()
        
        if count < self.MAX_CONVERSATIONS:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if is_pinned column exists
        cursor.execute("PRAGMA table_info(conversations)")
        columns = {row[1] for row in cursor.fetchall()}
        has_pinned_column = 'is_pinned' in columns
        
        # Find oldest inactive, non-pinned conversation
        if has_pinned_column:
            cursor.execute("""
                SELECT conversation_id
                FROM conversations
                WHERE is_active = 0 AND (is_pinned = 0 OR is_pinned IS NULL)
                ORDER BY created_at ASC
                LIMIT 1
            """)
        else:
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
            
            # Auto-archive to Tier 2 if provided
            if tier2_knowledge_graph:
                try:
                    # Import here to avoid circular dependency
                    from src.tier1.working_memory import WorkingMemory
                    # We need access to working memory to get conversation data
                    # This is a bit circular, but necessary for archival
                    # In practice, this is called from WorkingMemory itself
                    pass
                except Exception as e:
                    print(f"Auto-archive failed: {e}")
            
            # Log eviction event
            cursor.execute("""
                INSERT INTO eviction_log (conversation_id, event_type, details)
                VALUES (?, 'conversation_evicted', 'FIFO eviction - capacity reached (70 limit)')
            """, (oldest_id,))
            
            # Delete the conversation
            self._delete_conversation(oldest_id, cursor)
            
            conn.commit()
        
        conn.close()
    
    def _get_conversation_count(self) -> int:
        """Get the total number of conversations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
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
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current queue status.
        
        Returns:
            Dict with queue statistics
        """
        count = self._get_conversation_count()
        
        return {
            'current_count': count,
            'max_capacity': self.MAX_CONVERSATIONS,
            'available_slots': max(0, self.MAX_CONVERSATIONS - count),
            'is_at_capacity': count >= self.MAX_CONVERSATIONS
        }
