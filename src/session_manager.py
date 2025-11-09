"""
CORTEX Session Manager

Manages conversation sessions and boundaries:
- Track active conversations
- Detect conversation boundaries (30-min idle per Rule #11)
- Coordinate with Tier 1 FIFO queue
- Session metadata (start, end, intent)

Author: CORTEX Development Team
Version: 1.0
"""

import sqlite3
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import uuid
from pathlib import Path


class SessionManager:
    """
    Manage conversation sessions
    
    Responsibilities:
    - Track active conversations
    - Detect conversation boundaries (30-min idle per Rule #11)
    - Coordinate with Tier 1 FIFO queue
    - Session metadata (start, end, intent)
    
    Conversation Boundary Rule:
    - 30 minutes of inactivity = new conversation
    - Active conversation never deleted (even if oldest)
    - When 51st conversation starts, oldest completed deleted (FIFO)
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize session manager
        
        Args:
            db_path: Path to SQLite database (uses Tier 1 DB if None)
        """
        # Import here to avoid circular dependency
        if db_path is None:
            from .config import config
            db_path = config.brain_path / "tier1" / "conversations.db"
        
        self.db_path = Path(db_path) if isinstance(db_path, str) else db_path
        
        # Ensure schema exists
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Ensure session management tables exist"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create working_memory_conversations table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS working_memory_conversations (
                conversation_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                intent TEXT,
                status TEXT DEFAULT 'active',
                last_activity TEXT
            )
        """)
        
        # Create working_memory_messages table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS working_memory_messages (
                message_id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES working_memory_conversations(conversation_id)
            )
        """)
        
        # Create indices for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_wm_conv_status 
            ON working_memory_conversations(status, start_time)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_wm_msg_conv 
            ON working_memory_messages(conversation_id, timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def start_session(self, intent: Optional[str] = None, conversation_id: Optional[str] = None) -> str:
        """
        Start new conversation session
        
        Args:
            intent: Detected intent (PLAN, EXECUTE, TEST, etc.)
            conversation_id: Optional conversation ID (generated if not provided)
        
        Returns:
            conversation_id (UUID)
        """
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO working_memory_conversations 
            (conversation_id, start_time, intent, status, last_activity)
            VALUES (?, ?, ?, 'active', ?)
        """, (conversation_id, datetime.now().isoformat(), intent, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        # Check FIFO queue limit (50 conversations)
        self._enforce_fifo_limit()
        
        return conversation_id
    
    def end_session(self, conversation_id: str) -> None:
        """
        End conversation session
        
        Args:
            conversation_id: UUID of conversation to end
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE working_memory_conversations
            SET end_time = ?, status = 'completed'
            WHERE conversation_id = ?
        """, (datetime.now().isoformat(), conversation_id))
        
        conn.commit()
        conn.close()
    
    def get_active_session(self) -> Optional[str]:
        """
        Get active session if exists
        
        Returns None if:
        - No active session
        - Last activity >30 min ago (conversation boundary per Rule #11)
        
        Returns:
            conversation_id or None
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get most recent active conversation
        cursor.execute("""
            SELECT conversation_id, start_time
            FROM working_memory_conversations
            WHERE status = 'active'
            ORDER BY start_time DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        conversation_id, start_time = row
        
        # Check if conversation boundary reached (30 min idle per Rule #11)
        last_activity = self._get_last_activity_time(conversation_id)
        
        if datetime.now() - last_activity > timedelta(minutes=30):
            # Conversation boundary reached - end this session
            self.end_session(conversation_id)
            return None
        
        return conversation_id
    
    def _get_last_activity_time(self, conversation_id: str) -> datetime:
        """
        Get timestamp of last message in conversation
        
        Args:
            conversation_id: UUID of conversation
        
        Returns:
            datetime of last activity
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT MAX(timestamp)
            FROM working_memory_messages
            WHERE conversation_id = ?
        """, (conversation_id,))
        
        result = cursor.fetchone()[0]
        conn.close()
        
        if result:
            return datetime.fromisoformat(result)
        
        # No messages yet, use conversation start time
        return datetime.now()
    
    def _enforce_fifo_limit(self) -> None:
        """
        Enforce FIFO queue limit (50 conversations)
        
        When total exceeds 50:
        - Delete oldest COMPLETED conversations until count <= 50
        - Never delete active conversations
        - Preserve patterns (extracted before deletion)
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Count total conversations
        cursor.execute("""
            SELECT COUNT(*) FROM working_memory_conversations
        """)
        total_count = cursor.fetchone()[0]
        
        if total_count > 50:
            # Calculate how many to delete
            to_delete = total_count - 50
            
            # Get oldest completed conversations
            cursor.execute("""
                SELECT conversation_id
                FROM working_memory_conversations
                WHERE status = 'completed'
                ORDER BY start_time ASC
                LIMIT ?
            """, (to_delete,))
            
            rows_to_delete = cursor.fetchall()
            
            for row in rows_to_delete:
                oldest_id = row[0]
                
                # Delete messages first (foreign key)
                cursor.execute("""
                    DELETE FROM working_memory_messages
                    WHERE conversation_id = ?
                """, (oldest_id,))
                
                # Delete conversation from working_memory_conversations
                cursor.execute("""
                    DELETE FROM working_memory_conversations
                    WHERE conversation_id = ?
                """, (oldest_id,))
                
                # Log deletion event
                print(f"[SessionManager] FIFO: Deleted conversation {oldest_id}")
            
            conn.commit()
        
        conn.close()
    
    def get_session_info(self, conversation_id: str) -> Optional[Dict]:
        """
        Get session metadata
        
        Args:
            conversation_id: UUID of conversation
        
        Returns:
            {
                'conversation_id': 'uuid',
                'start_time': 'ISO datetime',
                'end_time': 'ISO datetime' or None,
                'intent': 'PLAN',
                'status': 'active' or 'completed',
                'message_count': 5
            }
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get conversation metadata
        cursor.execute("""
            SELECT conversation_id, start_time, end_time, intent, status
            FROM working_memory_conversations
            WHERE conversation_id = ?
        """, (conversation_id,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        conversation_id, start_time, end_time, intent, status = row
        
        # Get message count
        cursor.execute("""
            SELECT COUNT(*)
            FROM working_memory_messages
            WHERE conversation_id = ?
        """, (conversation_id,))
        
        message_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            'conversation_id': conversation_id,
            'start_time': start_time,
            'end_time': end_time,
            'intent': intent,
            'status': status,
            'message_count': message_count
        }
    
    def get_all_sessions(self, limit: int = 10) -> List[Dict]:
        """
        Get recent sessions (for monitoring/debugging)
        
        Args:
            limit: Maximum number of sessions to return
        
        Returns:
            List of session info dicts
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_id, start_time, end_time, intent, status
            FROM working_memory_conversations
            ORDER BY start_time DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            conversation_id, start_time, end_time, intent, status = row
            sessions.append({
                'conversation_id': conversation_id,
                'start_time': start_time,
                'end_time': end_time,
                'intent': intent,
                'status': status
            })
        
        return sessions
