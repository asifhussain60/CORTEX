"""
CORTEX Brain - Tier 1: ConversationManager

Purpose: Core CRUD operations for managing conversations in SQLite database

Features:
- Create, read, update, delete conversations
- FIFO queue management (max 20 conversations)
- Message threading and sequencing
- Context resolution support
- Performance optimized (<100ms queries)

Database Tables:
- tier1_conversations: Conversation metadata
- tier1_messages: Individual messages within conversations
- tier1_conversations_fts: Full-text search index

Author: CORTEX Development Team
Version: 1.0.0
"""

import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


class ConversationManager:
    """
    Manages conversations in the CORTEX Brain Tier 1 database.
    
    Implements FIFO queue (max 20 conversations), message threading,
    and context resolution for natural language continuity.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize ConversationManager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._ensure_connection()
    
    def _ensure_connection(self) -> None:
        """Ensure database file exists and schema is initialized"""
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found: {self.db_path}\n"
                f"Run migration scripts first to initialize database."
            )
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ========================================================================
    # CONVERSATION CRUD OPERATIONS
    # ========================================================================
    
    def create_conversation(
        self,
        topic: str,
        intent: Optional[str] = None,
        primary_entity: Optional[str] = None
    ) -> str:
        """
        Create a new conversation and manage FIFO queue
        
        Args:
            topic: Conversation topic (auto-generated from first message)
            intent: Primary intent (PLAN, EXECUTE, TEST, etc.)
            primary_entity: Main entity being discussed
        
        Returns:
            conversation_id: UUID of created conversation
        
        Raises:
            sqlite3.Error: If database operation fails
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Generate conversation ID
            conversation_id = f"conv-{uuid.uuid4().hex[:12]}"
            
            # Check current conversation count
            cursor.execute("SELECT COUNT(*) FROM tier1_conversations WHERE status = 'active'")
            active_count = cursor.fetchone()[0]
            
            # If at capacity (20), delete oldest conversation (FIFO)
            if active_count >= 20:
                self._enforce_fifo_queue(cursor)
            
            # Get next queue position
            cursor.execute("SELECT COALESCE(MAX(queue_position), 0) + 1 FROM tier1_conversations")
            queue_position = cursor.fetchone()[0]
            
            # Insert conversation
            cursor.execute("""
                INSERT INTO tier1_conversations (
                    conversation_id, topic, status, intent, primary_entity, queue_position
                ) VALUES (?, ?, 'active', ?, ?, ?)
            """, (conversation_id, topic, intent, primary_entity, queue_position))
            
            conn.commit()
            return conversation_id
        
        finally:
            conn.close()
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation by ID
        
        Args:
            conversation_id: Conversation UUID
        
        Returns:
            Dictionary with conversation data, or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM tier1_conversations
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return dict(row)
        
        finally:
            conn.close()
    
    def get_active_conversation(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent active conversation
        
        Returns:
            Dictionary with conversation data, or None if no active conversations
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM tier1_conversations
                WHERE status = 'active'
                ORDER BY updated_at DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return dict(row)
        
        finally:
            conn.close()
    
    def get_recent_conversations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent conversations (FIFO queue)
        
        Args:
            limit: Maximum number of conversations to return (default: 20)
        
        Returns:
            List of conversation dictionaries, ordered by creation date (newest first)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM tier1_conversations
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
        
        finally:
            conn.close()
    
    def update_conversation(
        self,
        conversation_id: str,
        status: Optional[str] = None,
        outcome: Optional[str] = None,
        duration_seconds: Optional[int] = None,
        related_files: Optional[List[str]] = None,
        associated_commits: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Update conversation metadata
        
        Args:
            conversation_id: Conversation UUID
            status: New status ('active', 'complete', 'archived')
            outcome: Outcome ('success', 'failure', 'cancelled')
            duration_seconds: Total conversation duration
            related_files: List of file paths
            associated_commits: List of commit metadata
        
        Returns:
            True if updated, False if conversation not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Build dynamic UPDATE query
            updates = []
            params = []
            
            if status is not None:
                updates.append("status = ?")
                params.append(status)
                if status == 'complete':
                    updates.append("completed_at = ?")
                    params.append(datetime.now().isoformat())
            
            if outcome is not None:
                updates.append("outcome = ?")
                params.append(outcome)
            
            if duration_seconds is not None:
                updates.append("duration_seconds = ?")
                params.append(duration_seconds)
            
            if related_files is not None:
                import json
                updates.append("related_files = ?")
                params.append(json.dumps(related_files))
            
            if associated_commits is not None:
                import json
                updates.append("associated_commits = ?")
                params.append(json.dumps(associated_commits))
            
            # Always update updated_at
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            
            if not updates:
                return True  # Nothing to update
            
            # Add conversation_id to params
            params.append(conversation_id)
            
            # Execute update
            query = f"""
                UPDATE tier1_conversations
                SET {', '.join(updates)}
                WHERE conversation_id = ?
            """
            
            cursor.execute(query, params)
            conn.commit()
            
            return cursor.rowcount > 0
        
        finally:
            conn.close()
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete conversation and all associated messages
        
        Args:
            conversation_id: Conversation UUID
        
        Returns:
            True if deleted, False if conversation not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM tier1_conversations
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            conn.commit()
            return cursor.rowcount > 0
        
        finally:
            conn.close()
    
    # ========================================================================
    # MESSAGE CRUD OPERATIONS
    # ========================================================================
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        intent_detected: Optional[str] = None,
        resolved_references: Optional[Dict[str, str]] = None,
        agent_used: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> str:
        """
        Add message to conversation
        
        Args:
            conversation_id: Parent conversation UUID
            role: Message role ('user', 'assistant', 'system')
            content: Message text
            intent_detected: Detected intent for this message
            resolved_references: Dictionary of resolved references {"it": "FAB button"}
            agent_used: Which agent processed this message
            confidence: Confidence score (0.0-1.0)
        
        Returns:
            message_id: UUID of created message
        
        Raises:
            ValueError: If conversation not found or role invalid
        """
        # Validate role
        if role not in ('user', 'assistant', 'system'):
            raise ValueError(f"Invalid role: {role}. Must be 'user', 'assistant', or 'system'")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Verify conversation exists
            cursor.execute("SELECT 1 FROM tier1_conversations WHERE conversation_id = ?", (conversation_id,))
            if not cursor.fetchone():
                raise ValueError(f"Conversation not found: {conversation_id}")
            
            # Get next sequence number
            cursor.execute("""
                SELECT COALESCE(MAX(sequence_number), 0) + 1
                FROM tier1_messages
                WHERE conversation_id = ?
            """, (conversation_id,))
            sequence_number = cursor.fetchone()[0]
            
            # Generate message ID
            message_id = f"msg-{uuid.uuid4().hex[:12]}"
            
            # Convert resolved_references to JSON
            import json
            resolved_json = json.dumps(resolved_references) if resolved_references else None
            
            # Insert message
            cursor.execute("""
                INSERT INTO tier1_messages (
                    message_id, conversation_id, sequence_number, role, content,
                    intent_detected, resolved_references, agent_used, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message_id, conversation_id, sequence_number, role, content,
                intent_detected, resolved_json, agent_used, confidence
            ))
            
            # Update conversation message count and updated_at
            cursor.execute("""
                UPDATE tier1_conversations
                SET message_count = message_count + 1,
                    updated_at = ?
                WHERE conversation_id = ?
            """, (datetime.now().isoformat(), conversation_id))
            
            conn.commit()
            return message_id
        
        finally:
            conn.close()
    
    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages in conversation (ordered by sequence)
        
        Args:
            conversation_id: Conversation UUID
        
        Returns:
            List of message dictionaries, ordered by sequence_number
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM tier1_messages
                WHERE conversation_id = ?
                ORDER BY sequence_number ASC
            """, (conversation_id,))
            
            return [dict(row) for row in cursor.fetchall()]
        
        finally:
            conn.close()
    
    def get_recent_messages(self, conversation_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent messages in conversation
        
        Args:
            conversation_id: Conversation UUID
            limit: Maximum number of messages to return (default: 10)
        
        Returns:
            List of message dictionaries, ordered by sequence_number (newest first)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM tier1_messages
                WHERE conversation_id = ?
                ORDER BY sequence_number DESC
                LIMIT ?
            """, (conversation_id, limit))
            
            # Reverse to get chronological order
            return list(reversed([dict(row) for row in cursor.fetchall()]))
        
        finally:
            conn.close()
    
    # ========================================================================
    # SEARCH & QUERY OPERATIONS
    # ========================================================================
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Full-text search across conversations
        
        Args:
            query: Search query (supports FTS5 syntax)
            limit: Maximum number of results (default: 10)
        
        Returns:
            List of conversation dictionaries, ordered by relevance
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT c.* FROM tier1_conversations c
                JOIN tier1_conversations_fts fts ON c.conversation_id = fts.conversation_id
                WHERE tier1_conversations_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit))
            
            return [dict(row) for row in cursor.fetchall()]
        
        finally:
            conn.close()
    
    def find_conversations_by_entity(self, entity: str) -> List[Dict[str, Any]]:
        """
        Find conversations that mention a specific entity
        
        Args:
            entity: Entity name (file, feature, etc.)
        
        Returns:
            List of conversation dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM tier1_conversations
                WHERE primary_entity = ?
                   OR related_files LIKE ?
                ORDER BY created_at DESC
            """, (entity, f'%{entity}%'))
            
            return [dict(row) for row in cursor.fetchall()]
        
        finally:
            conn.close()
    
    # ========================================================================
    # FIFO QUEUE MANAGEMENT
    # ========================================================================
    
    def _enforce_fifo_queue(self, cursor: sqlite3.Cursor) -> None:
        """
        Enforce FIFO queue by deleting oldest conversation
        
        Args:
            cursor: Active database cursor (within transaction)
        """
        # Find oldest conversation (lowest queue_position)
        cursor.execute("""
            SELECT conversation_id FROM tier1_conversations
            ORDER BY queue_position ASC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        if row:
            oldest_id = row[0]
            
            # Delete oldest conversation (CASCADE deletes messages)
            cursor.execute("""
                DELETE FROM tier1_conversations
                WHERE conversation_id = ?
            """, (oldest_id,))
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get FIFO queue status
        
        Returns:
            Dictionary with queue statistics
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_conversations,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_conversations,
                    SUM(message_count) as total_messages,
                    MAX(queue_position) as max_queue_position
                FROM tier1_conversations
            """)
            
            row = cursor.fetchone()
            return {
                'total_conversations': row[0] or 0,
                'active_conversations': row[1] or 0,
                'total_messages': row[2] or 0,
                'max_queue_position': row[3] or 0,
                'capacity': 20,
                'slots_available': 20 - (row[1] or 0)
            }
        
        finally:
            conn.close()
    
    # ========================================================================
    # CONTEXT RESOLUTION SUPPORT
    # ========================================================================
    
    def get_context_for_resolution(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get context for resolving ambiguous references
        
        Args:
            conversation_id: Conversation UUID
        
        Returns:
            Dictionary with context information:
            - recent_messages: Last 5 messages
            - primary_entity: Main entity being discussed
            - related_files: Files modified in conversation
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get conversation metadata
            cursor.execute("""
                SELECT primary_entity, related_files FROM tier1_conversations
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            row = cursor.fetchone()
            if not row:
                return {}
            
            # Get recent messages
            recent_messages = self.get_recent_messages(conversation_id, limit=5)
            
            import json
            return {
                'conversation_id': conversation_id,
                'primary_entity': row[0],
                'related_files': json.loads(row[1]) if row[1] else [],
                'recent_messages': recent_messages
            }
        
        finally:
            conn.close()
