"""
CORTEX FIFO Queue Enforcement Test - Tier 0 Protection

Tests that the conversation tracking system correctly enforces the 50-conversation
limit by processing 60 conversations and verifying:
1. Oldest conversations are deleted first
2. Database never exceeds 50 conversations
3. No data corruption occurs
4. Session continuity is maintained

Rule #24: Conversation Tracking Must Work
Protected by: Brain Protector (Tier 0)
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import sqlite3
import time
from datetime import datetime
from CORTEX.src.session_manager import SessionManager
from CORTEX.src.config import config

# Colors for terminal output (pytest-friendly)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class TestFIFOEnforcement:
    """
    Brain Protector: FIFO Queue Enforcement
    
    CRITICAL: Ensures the 50-conversation limit is maintained
    """
    
    @pytest.fixture
    def clean_database(self):
        """Clear database before test"""
        db_path = config.brain_path / "tier1" / "conversations.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM working_memory_messages")
        cursor.execute("DELETE FROM working_memory_conversations")
        conn.commit()
        conn.close()
        yield
        # Cleanup after test (optional - keeps last test state)
    
    def get_conversation_count(self):
        """Get current count of conversations in working memory"""
        db_path = config.brain_path / "tier1" / "conversations.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM working_memory_conversations")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def conversation_exists(self, conv_id):
        """Check if a conversation exists"""
        db_path = config.brain_path / "tier1" / "conversations.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM working_memory_conversations 
            WHERE conversation_id = ?
        """, (conv_id,))
        exists = cursor.fetchone()[0] > 0
        
        conn.close()
        return exists
    
    def test_fifo_enforcement_60_conversations(self, clean_database):
        """
        Test FIFO queue enforcement with 60 conversations
        
        Expected behavior:
        - First 50 conversations should all be created
        - Conversations 51-60 should trigger FIFO deletion
        - Oldest 10 conversations should be deleted
        - Newest 50 conversations should remain
        """
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}{'CORTEX FIFO Queue Enforcement Test'.center(70)}{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
        # Track which conversations we create
        created_conversations = []
        
        # Create a SessionManager instance
        session_mgr = SessionManager()
        
        # Phase 1: Create 60 conversations
        print(f"{YELLOW}Phase 1: Creating 60 Conversations{RESET}")
        
        for i in range(1, 61):
            # Start a new session (this will trigger FIFO enforcement)
            conv_id = session_mgr.start_session(intent="test")
            created_conversations.append(conv_id)
            
            # End the session immediately
            session_mgr.end_session(conv_id)
            
            # Small delay to ensure timestamps are different
            time.sleep(0.001)
            
            # Check count periodically
            if i % 10 == 0 or i > 50:
                count = self.get_conversation_count()
                if i <= 50:
                    expected = i
                else:
                    expected = 50
                
                status = "✓" if count == expected else "✗"
                print(f"  {status} Conversation {i}: Count = {count}, Expected = {expected}")
                
                assert count == expected, f"Expected {expected} conversations, found {count}"
        
        # Phase 2: Verify FIFO enforcement
        print(f"\n{YELLOW}Phase 2: Verifying FIFO Enforcement{RESET}")
        
        final_count = self.get_conversation_count()
        print(f"  Final conversation count: {final_count}")
        
        assert final_count == 50, f"FIFO enforcement failed: Expected 50, found {final_count}"
        print(f"{GREEN}✓ FIFO limit enforced: {final_count} conversations{RESET}")
        
        # Phase 3: Verify oldest conversations were deleted
        print(f"\n{YELLOW}Phase 3: Verifying Oldest Conversations Deleted{RESET}")
        
        # Check that first 10 conversations were deleted
        deleted_count = 0
        for i in range(10):
            conv_id = created_conversations[i]
            if not self.conversation_exists(conv_id):
                deleted_count += 1
        
        print(f"  Oldest 10 conversations deleted: {deleted_count}/10")
        assert deleted_count == 10, f"Only {deleted_count}/10 oldest conversations were deleted"
        print(f"{GREEN}✓ All 10 oldest conversations correctly deleted{RESET}")
        
        # Phase 4: Verify newest conversations remain
        print(f"\n{YELLOW}Phase 4: Verifying Newest Conversations Remain{RESET}")
        
        # Check that last 50 conversations still exist
        remaining_count = 0
        for i in range(10, 60):
            conv_id = created_conversations[i]
            if self.conversation_exists(conv_id):
                remaining_count += 1
        
        print(f"  Newest 50 conversations remaining: {remaining_count}/50")
        assert remaining_count == 50, f"Expected 50 recent conversations, found {remaining_count}"
        print(f"{GREEN}✓ All 50 newest conversations correctly retained{RESET}")
        
        # Phase 5: Database integrity check
        print(f"\n{YELLOW}Phase 5: Database Integrity Check{RESET}")
        
        db_path = config.brain_path / "tier1" / "conversations.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check for orphaned messages
        cursor.execute("""
            SELECT COUNT(*) 
            FROM working_memory_messages 
            WHERE conversation_id NOT IN (
                SELECT conversation_id FROM working_memory_conversations
            )
        """)
        orphaned = cursor.fetchone()[0]
        
        conn.close()
        
        assert orphaned == 0, f"Found {orphaned} orphaned messages"
        print(f"{GREEN}✓ No orphaned messages found{RESET}")
        
        # Final summary
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}✅ FIFO ENFORCEMENT TEST PASSED{RESET}")
        print(f"{GREEN}{'='*70}{RESET}\n")


if __name__ == "__main__":
    """Run as standalone script for quick testing"""
    pytest.main([__file__, "-v", "-s"])

