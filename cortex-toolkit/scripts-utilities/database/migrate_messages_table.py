import sqlite3
import os

db_path = 'cortex-brain/tier1/working_memory.db'

if not os.path.exists(db_path):
    print(f"ERROR: Database not found at {db_path}")
    exit(1)

print("Migrating messages table to match code expectations...")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check current messages table schema
    cursor.execute("PRAGMA table_info(messages)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    # Create new table with correct schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT UNIQUE NOT NULL,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            tokens INTEGER DEFAULT 0,
            model TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
        )
    """)
    
    # Copy data from old table to new table
    if 'message_id' in columns:
        # Already has message_id, just copy
        cursor.execute("""
            INSERT INTO messages_new 
            SELECT * FROM messages
        """)
    else:
        # Need to generate message_id - copy only columns that exist
        cursor.execute("""
            INSERT INTO messages_new (id, message_id, conversation_id, role, content, timestamp)
            SELECT 
                id, 
                'msg-' || id as message_id,
                conversation_id, 
                role, 
                content, 
                timestamp
            FROM messages
        """)
    
    # Drop old table
    cursor.execute("DROP TABLE messages")
    
    # Rename new table to messages
    cursor.execute("ALTER TABLE messages_new RENAME TO messages")
    
    conn.commit()
    print("✓ Successfully migrated messages table")
    
except Exception as e:
    print(f"✗ Migration failed: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
finally:
    conn.close()
