"""
Conversation Search - Handles conversation search operations.
"""

import sqlite3
from pathlib import Path
from typing import List
from datetime import datetime
from .conversation_manager import Conversation, ConversationManager


class ConversationSearch:
    """Handles conversation search functionality."""
    
    def __init__(self, db_path: Path):
        """
        Initialize conversation search.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.conversation_manager = ConversationManager(db_path)
    
    def search_by_keyword(self, keyword: str) -> List[Conversation]:
        """
        Search conversations by keyword in title or messages.
        
        Args:
            keyword: Search keyword
        
        Returns:
            List of matching Conversation objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT c.conversation_id
            FROM conversations c
            LEFT JOIN messages m ON c.conversation_id = m.conversation_id
            WHERE c.title LIKE ? OR m.content LIKE ?
        """, (f'%{keyword}%', f'%{keyword}%'))
        
        conversation_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return [
            self.conversation_manager.get_conversation(cid) 
            for cid in conversation_ids
        ]
    
    def search_by_date_range(
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
        
        return [
            self.conversation_manager.get_conversation(cid) 
            for cid in conversation_ids
        ]
    
    def search_by_entity(
        self,
        entity_type: str,
        entity_name: str
    ) -> List[Conversation]:
        """
        Find conversations that mention a specific entity.
        
        Args:
            entity_type: Type of entity (file, class, method, etc.)
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
        """, (entity_type, entity_name))
        
        conversation_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return [
            self.conversation_manager.get_conversation(cid) 
            for cid in conversation_ids
        ]
