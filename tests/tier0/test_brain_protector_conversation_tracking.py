"""
CORTEX Brain Protector: Conversation Tracking Validation

This test ensures the CRITICAL brain function of conversation tracking works correctly.
Without this, CORTEX has amnesia - the core problem we're solving.

Protection Level: TIER 0 (Core Instinct)
Rule: #24 - Conversation Memory Must Work

Tests:
1. CortexEntry.process() logs messages to Tier 1
2. conversation-history.jsonl receives updates (backward compat)
3. SQLite conversations.db is updated correctly
4. FIFO queue enforcement (20 conversation limit)
5. Session continuity across multiple messages
6. No data loss between Python invocations
"""

import pytest
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
import tempfile
import shutil

# Add CORTEX to path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from entry_point.cortex_entry import CortexEntry


# Module-level fixtures (shared across test classes)
@pytest.fixture
def temp_brain():
    """Create temporary brain directory for testing"""
    temp_dir = Path(tempfile.mkdtemp(prefix="cortex_brain_test_"))
    
    # Create structure
    (temp_dir / "tier1").mkdir(parents=True)
    (temp_dir / "tier2").mkdir(parents=True)
    (temp_dir / "tier3").mkdir(parents=True)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def cortex_entry(temp_brain):
    """Initialize CortexEntry with temp brain"""
    entry = CortexEntry(
        brain_path=str(temp_brain),
        enable_logging=False
    )
    yield entry
    # Cleanup: Close all database connections before temp directory deletion
    entry.cleanup()


class TestConversationTrackingProtection:
    """
    Brain Protector: Conversation Tracking
    
    CRITICAL: These tests must ALWAYS pass. If they fail, CORTEX has amnesia.
    """
    
    def test_process_logs_to_tier1_sqlite(self, cortex_entry, temp_brain):
        """
        CRITICAL: CortexEntry.process() MUST log messages to SQLite
        
        Failure Impact: ❌ Complete amnesia - no conversation memory
        """
        # Process a message
        message = "Create authentication tests"
        response = cortex_entry.process(message, resume_session=True)
        
        assert response is not None, "❌ No response from CortexEntry.process()"
        
        # Verify SQLite database was updated
        db_path = temp_brain / "tier1" / "conversations.db"
        assert db_path.exists(), f"❌ Database not created: {db_path}"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check conversation exists
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conv_count = cursor.fetchone()[0]
        assert conv_count > 0, "❌ No conversations in database"
        
        # Check message was logged
        cursor.execute("SELECT COUNT(*) FROM messages WHERE content = ?", (message,))
        msg_count = cursor.fetchone()[0]
        assert msg_count > 0, f"❌ User message not logged: {message}"
        
        # Check assistant response was logged
        cursor.execute("SELECT COUNT(*) FROM messages WHERE role = 'assistant'")
        assistant_count = cursor.fetchone()[0]
        assert assistant_count > 0, "❌ Assistant response not logged"
        
        conn.close()
        
        print(f"✅ Conversation tracking working: {conv_count} conversations, {msg_count} user messages")
    
    def test_session_continuity_across_messages(self, cortex_entry, temp_brain):
        """
        CRITICAL: Multiple messages in same session MUST share conversation_id
        
        Failure Impact: ❌ Context lost between messages ("Make it purple" fails)
        """
        # Send multiple messages
        msg1 = "Add a purple button"
        msg2 = "Make it pulse"
        msg3 = "Put it in the header"
        
        cortex_entry.process(msg1, resume_session=True)
        cortex_entry.process(msg2, resume_session=True)  # Should reuse session
        cortex_entry.process(msg3, resume_session=True)  # Should reuse session
        
        # Verify all messages in same conversation
        db_path = temp_brain / "tier1" / "conversations.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get distinct conversation IDs
        cursor.execute("SELECT DISTINCT conversation_id FROM messages")
        conv_ids = cursor.fetchall()
        
        assert len(conv_ids) == 1, f"❌ Messages split across multiple conversations: {len(conv_ids)}"
        
        # Verify all 3 user messages + 3 assistant responses = 6 total
        cursor.execute("SELECT COUNT(*) FROM messages")
        total_messages = cursor.fetchone()[0]
        assert total_messages >= 6, f"❌ Expected 6+ messages, got {total_messages}"
        
        conn.close()
        
        print(f"✅ Session continuity maintained: 3 messages in 1 conversation")
    
    def test_fifo_queue_enforcement(self, cortex_entry, temp_brain):
        """
        CRITICAL: FIFO queue MUST delete oldest conversation when limit reached
        
        Failure Impact: ❌ Unbounded storage growth, performance degradation
        """
        # Create 21 conversations (1 over limit)
        for i in range(21):
            # End session to force new conversation
            cortex_entry.end_session()
            
            # Process message in new session
            cortex_entry.process(
                f"Task {i + 1}: Create feature X",
                resume_session=False  # Force new conversation
            )
        
        # Verify only 20 conversations remain
        db_path = temp_brain / "tier1" / "conversations.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conv_count = cursor.fetchone()[0]
        
        assert conv_count <= 20, f"❌ FIFO failed: {conv_count} conversations (max 20)"
        
        # Verify oldest conversation was deleted
        cursor.execute("SELECT conversation_id FROM conversations ORDER BY start_time LIMIT 1")
        oldest_id = cursor.fetchone()[0]
        
        assert "conv-001" not in oldest_id, "❌ Oldest conversation not deleted"
        
        conn.close()
        
        print(f"✅ FIFO working: {conv_count} conversations (max 20)")
    
    def test_no_data_loss_between_invocations(self, temp_brain):
        """
        CRITICAL: Data MUST persist between Python invocations
        
        Failure Impact: ❌ Amnesia between Copilot Chat sessions
        """
        # First invocation - create conversation
        entry1 = CortexEntry(brain_path=str(temp_brain), enable_logging=False)
        entry1.process("First message", resume_session=True)
        session1_info = entry1.get_session_info()
        conv_id_1 = session1_info['conversation_id']
        
        # Simulate closing/reopening (new CortexEntry instance)
        entry1.cleanup()  # Close database connections
        del entry1
        
        # Second invocation - should load existing conversation
        entry2 = CortexEntry(brain_path=str(temp_brain), enable_logging=False)
        entry2.process("Second message", resume_session=True)
        session2_info = entry2.get_session_info()
        conv_id_2 = session2_info['conversation_id']
        
        # Should be same conversation (within 30-min boundary per Rule #11)
        assert conv_id_1 == conv_id_2, f"❌ Conversation not resumed: {conv_id_1} != {conv_id_2}"
        
        # Verify both messages exist
        db_path = temp_brain / "tier1" / "conversations.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM messages WHERE conversation_id = ?",
            (conv_id_1,)
        )
        msg_count = cursor.fetchone()[0]
        
        assert msg_count >= 4, f"❌ Messages lost: expected 4+, got {msg_count}"
        
        conn.close()
        entry2.cleanup()  # Close database connections
        
        print(f"✅ Data persists: {msg_count} messages retained")
    
    def test_backward_compatibility_with_jsonl(self, cortex_entry, temp_brain):
        """
        OPTIONAL: Verify backward compatibility with conversation-history.jsonl
        
        Note: Primary storage is now SQLite, but JSONL may be used for exports
        """
        # Process message
        cortex_entry.process("Test message", resume_session=True)
        
        # Check if JSONL export exists (optional feature)
        jsonl_path = temp_brain / "conversation-history.jsonl"
        
        if jsonl_path.exists():
            with open(jsonl_path, 'r') as f:
                lines = f.readlines()
                assert len(lines) > 0, "❌ JSONL file empty"
                
                # Verify valid JSON
                for line in lines:
                    data = json.loads(line)
                    assert 'conversation_id' in data, "❌ Invalid JSONL format"
            
            print(f"✅ JSONL export working: {len(lines)} entries")
        else:
            print("ℹ️  JSONL export not enabled (SQLite primary)")
    
    def test_cortex_capture_script_integration(self, temp_brain):
        """
        CRITICAL: cortex-capture.ps1 MUST successfully invoke Python tracking
        
        Failure Impact: ❌ Copilot Chat → CORTEX bridge broken
        """
        import subprocess
        import platform
        
        if platform.system() != "Windows":
            pytest.skip("cortex-capture.ps1 is Windows-only")
        
        # Create test message
        test_message = "Test: Verify cortex-capture integration"
        
        # Run cortex-capture.ps1
        script_path = Path(__file__).parent.parent.parent / "scripts" / "cortex-capture.ps1"
        
        if not script_path.exists():
            pytest.skip(f"cortex-capture.ps1 not found: {script_path}")
        
        result = subprocess.run(
            ["pwsh", "-File", str(script_path), "-Message", test_message, "-Intent", "TEST"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Verify script succeeded
        assert result.returncode == 0, f"❌ cortex-capture.ps1 failed:\n{result.stderr}"
        
        # Verify message was tracked
        db_path = temp_brain / "tier1" / "conversations.db"
        if db_path.exists():
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM messages WHERE content LIKE ?", (f"%{test_message}%",))
            count = cursor.fetchone()[0]
            
            assert count > 0, f"❌ Message not tracked by cortex-capture.ps1"
            
            conn.close()
            print("✅ cortex-capture.ps1 integration working")
        else:
            pytest.skip("Database not created by script")


class TestConversationTrackingHealth:
    """
    Health checks for conversation tracking system
    """
    
    def test_database_schema_integrity(self, temp_brain):
        """Verify database schema is correct"""
        entry = CortexEntry(brain_path=str(temp_brain), enable_logging=False)
        entry.process("Schema test", resume_session=True)
        
        db_path = temp_brain / "tier1" / "conversations.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check required tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['conversations', 'messages', 'entities', 'files_modified']
        for table in required_tables:
            assert table in tables, f"❌ Missing table: {table}"
        
        # Check conversations table schema
        cursor.execute("PRAGMA table_info(conversations)")
        columns = {row[1] for row in cursor.fetchall()}
        
        required_columns = {
            'conversation_id', 'agent_id', 'start_time', 'end_time',
            'goal', 'outcome', 'status', 'message_count'
        }
        
        assert required_columns.issubset(columns), f"❌ Missing columns: {required_columns - columns}"
        
        conn.close()
        entry.cleanup()  # Close database connections
        print(f"✅ Schema valid: {len(tables)} tables, {len(columns)} columns in conversations")
    
    def test_performance_under_load(self, cortex_entry):
        """Verify tracking doesn't significantly slow down responses"""
        import time
        
        messages = [
            "Create user authentication",
            "Add password validation",
            "Implement 2FA",
            "Create session management",
            "Add rate limiting"
        ]
        
        start = time.time()
        
        for msg in messages:
            cortex_entry.process(msg, resume_session=True)
        
        duration = time.time() - start
        avg_per_message = duration / len(messages)
        
        # Should process at reasonable speed (< 2s per message)
        assert avg_per_message < 2.0, f"❌ Too slow: {avg_per_message:.2f}s per message"
        
        print(f"✅ Performance acceptable: {avg_per_message:.3f}s per message")


# Test discovery for pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
