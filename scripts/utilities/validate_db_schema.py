"""
Quick validation test for database schema fixes
Tests that all required columns exist and can be used
"""
import sqlite3
import sys

def test_database_schema():
    """Validate database schema has all required columns."""
    db_path = 'cortex-brain/tier1/working_memory.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test 1: Conversations table columns
        print("✓ Testing conversations table...")
        required_conv_cols = ['conversation_id', 'agent_id', 'start_time', 'goal', 'status', 'context', 'end_time']
        cursor.execute("PRAGMA table_info(conversations)")
        conv_cols = [col[1] for col in cursor.fetchall()]
        
        for col in required_conv_cols:
            if col not in conv_cols:
                print(f"  ✗ Missing column: {col}")
                return False
        print(f"  ✓ All {len(required_conv_cols)} required columns present")
        
        # Test 2: Messages table columns
        print("✓ Testing messages table...")
        required_msg_cols = ['message_id', 'conversation_id', 'role', 'content', 'timestamp']
        cursor.execute("PRAGMA table_info(messages)")
        msg_cols = [col[1] for col in cursor.fetchall()]
        
        for col in required_msg_cols:
            if col not in msg_cols:
                print(f"  ✗ Missing column: {col}")
                return False
        print(f"  ✓ All {len(required_msg_cols)} required columns present")
        
        # Test 3: Entities table columns
        print("✓ Testing entities table...")
        required_ent_cols = ['entity_value', 'conversation_id']
        cursor.execute("PRAGMA table_info(entities)")
        ent_cols = [col[1] for col in cursor.fetchall()]
        
        for col in required_ent_cols:
            if col not in ent_cols:
                print(f"  ✗ Missing column: {col}")
                return False
        print(f"  ✓ All {len(required_ent_cols)} required columns present")
        
        # Test 4: Try inserting test data (then rollback)
        print("✓ Testing data operations...")
        try:
            cursor.execute("""
                INSERT INTO conversations (conversation_id, agent_id, goal, status)
                VALUES ('test-conv-123', 'TestAgent', 'Test goal', 'active')
            """)
            cursor.execute("""
                INSERT INTO messages (message_id, conversation_id, role, content, timestamp)
                VALUES ('test-msg-123', 'test-conv-123', 'user', 'Test message', datetime('now'))
            """)
            conn.rollback()  # Don't actually save test data
            print("  ✓ Insert operations successful (rolled back)")
        except Exception as e:
            print(f"  ✗ Insert operation failed: {e}")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Database validation failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Database Schema Validation")
    print("=" * 60)
    
    if test_database_schema():
        print("\n✅ All tests passed - Database schema is valid")
        sys.exit(0)
    else:
        print("\n❌ Tests failed - Database schema has issues")
        sys.exit(1)
