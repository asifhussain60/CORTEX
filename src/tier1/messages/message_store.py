"""
Message Store - Handles message storage and retrieval operations.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any


class MessageStore:
    """Manages message storage and retrieval."""
    
    def __init__(self, db_path: Path):
        """
        Initialize message store.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
    
    def add_messages(
        self,
        conversation_id: str,
        messages: List[Dict[str, str]]
    ) -> None:
        """
        Add messages to a conversation.
        
        Args:
            conversation_id: Conversation to add messages to
            messages: List of message dicts with 'role' and 'content'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for message in messages:
            cursor.execute("""
                INSERT INTO messages (conversation_id, role, content)
                VALUES (?, ?, ?)
            """, (conversation_id, message['role'], message['content']))
        
        conn.commit()
        conn.close()
    
    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages for a conversation.
        
        Args:
            conversation_id: Conversation identifier
        
        Returns:
            List of message dicts with role, content, timestamp
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
    
    def get_message_count(self, conversation_id: str) -> int:
        """
        Get the number of messages in a conversation.
        
        Args:
            conversation_id: Conversation identifier
        
        Returns:
            Number of messages
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM messages WHERE conversation_id = ?
        """, (conversation_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def delete_messages(self, conversation_id: str) -> None:
        """
        Delete all messages for a conversation.
        
        Args:
            conversation_id: Conversation identifier
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        
        conn.commit()
        conn.close()
