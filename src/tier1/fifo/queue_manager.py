"""
Queue Manager - Handles FIFO queue enforcement for conversations.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any


class QueueManager:
    """Manages FIFO queue enforcement (20-conversation limit)."""
    
    MAX_CONVERSATIONS = 20
    
    def __init__(self, db_path: Path):
        """
        Initialize queue manager.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
    
    def enforce_fifo_limit(self) -> None:
        """
        Enforce FIFO limit of 20 conversations.
        Evicts oldest inactive conversation if at capacity.
        """
        count = self._get_conversation_count()
        
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
