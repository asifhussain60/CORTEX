"""
Unit Tests for SessionManager

Tests:
1. test_start_session() - Sessions started correctly
2. test_end_session() - Sessions ended correctly
3. test_conversation_boundary() - 30-min idle detected (Rule #11)
4. test_active_session_retrieval() - Active session retrieved

Author: CORTEX Development Team
Version: 1.0
"""

import unittest
from unittest.mock import Mock, patch
import sqlite3
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.session_manager import SessionManager


class TestSessionManager(unittest.TestCase):
    """Unit tests for SessionManager"""
    
    def setUp(self):
        """Set up test database"""
        self.db_path = ":memory:"
        self._create_test_schema()
        self.manager = SessionManager(self.db_path)
    
    def _create_test_schema(self):
        """Create test database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS working_memory_conversations (
                conversation_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                intent TEXT,
                status TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS working_memory_messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES working_memory_conversations(conversation_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def test_start_session(self):
        """Test: Sessions started correctly"""
        # Execute
        conv_id = self.manager.start_session(intent='PLAN')
        
        # Verify
        self.assertIsNotNone(conv_id)
        self.assertTrue(len(conv_id) > 0)
        
        # Verify in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT conversation_id, intent, status
            FROM working_memory_conversations
            WHERE conversation_id = ?
        """, (conv_id,))
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[0], conv_id)
        self.assertEqual(row[1], 'PLAN')
        self.assertEqual(row[2], 'active')
    
    def test_end_session(self):
        """Test: Sessions ended correctly"""
        # Setup - create active session
        conv_id = self.manager.start_session(intent='EXECUTE')
        
        # Execute
        self.manager.end_session(conv_id)
        
        # Verify
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT status, end_time
            FROM working_memory_conversations
            WHERE conversation_id = ?
        """, (conv_id,))
        row = cursor.fetchone()
        conn.close()
        
        self.assertEqual(row[0], 'completed')
        self.assertIsNotNone(row[1])
    
    def test_conversation_boundary_30min(self):
        """Test: 30-min idle triggers conversation boundary (Rule #11)"""
        # Setup - create session with old timestamp
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        old_time = datetime.now() - timedelta(minutes=35)
        conv_id = 'test-old-conversation'
        
        cursor.execute("""
            INSERT INTO working_memory_conversations
            (conversation_id, start_time, intent, status)
            VALUES (?, ?, 'TEST', 'active')
        """, (conv_id, old_time.isoformat()))
        
        # Add old message
        cursor.execute("""
            INSERT INTO working_memory_messages
            (conversation_id, role, content, timestamp)
            VALUES (?, 'user', 'Test message', ?)
        """, (conv_id, old_time.isoformat()))
        
        conn.commit()
        conn.close()
        
        # Execute
        active_id = self.manager.get_active_session()
        
        # Verify - should be None due to 30-min boundary
        self.assertIsNone(active_id,
                         "Session should be None after 30-min idle")
        
        # Verify session was ended
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT status FROM working_memory_conversations
            WHERE conversation_id = ?
        """, (conv_id,))
        status = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(status, 'completed')
    
    def test_active_session_retrieval(self):
        """Test: Active session retrieved correctly"""
        # Setup - create recent session
        conv_id = self.manager.start_session(intent='QUERY')
        
        # Add recent message
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO working_memory_messages
            (conversation_id, role, content, timestamp)
            VALUES (?, 'user', 'Recent message', ?)
        """, (conv_id, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        # Execute
        active_id = self.manager.get_active_session()
        
        # Verify
        self.assertEqual(active_id, conv_id)
    
    def test_fifo_limit_enforcement(self):
        """Test: FIFO queue enforced at 50 conversations"""
        # Create 51 completed conversations
        for i in range(51):
            conv_id = f"conv-{i}"
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO working_memory_conversations
                (conversation_id, start_time, end_time, intent, status)
                VALUES (?, ?, ?, 'TEST', 'completed')
            """, (
                conv_id,
                (datetime.now() - timedelta(hours=51-i)).isoformat(),
                (datetime.now() - timedelta(hours=50-i)).isoformat()
            ))
            conn.commit()
            conn.close()
        
        # Trigger FIFO enforcement
        self.manager._enforce_fifo_limit()
        
        # Verify total count <= 50
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM working_memory_conversations")
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertLessEqual(count, 50,
                            "FIFO should limit to 50 conversations")
        
        # Verify oldest was deleted
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT conversation_id FROM working_memory_conversations
            WHERE conversation_id = 'conv-0'
        """)
        oldest = cursor.fetchone()
        conn.close()
        
        self.assertIsNone(oldest,
                         "Oldest conversation should be deleted")


if __name__ == '__main__':
    unittest.main()
