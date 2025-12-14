import sqlite3
import os

db_path = 'cortex-brain/tier1/working_memory.db'

if not os.path.exists(db_path):
    print(f"ERROR: Database not found at {db_path}")
    exit(1)

print("Migrating conversations table to match code expectations...")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Create new table with correct schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT UNIQUE NOT NULL,
            agent_id TEXT,
            start_time TEXT,
            goal TEXT,
            status TEXT DEFAULT 'active',
            context TEXT,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 0,
            summary TEXT,
            tags TEXT,
            session_id TEXT,
            last_activity TIMESTAMP,
            workflow_state TEXT,
            conversation_type TEXT DEFAULT 'interactive',
            import_source TEXT,
            quality_score REAL DEFAULT 0.0,
            semantic_elements TEXT DEFAULT '{}'
        )
    """)
    
    # Copy data from old table to new table
    cursor.execute("""
        INSERT INTO conversations_new 
        SELECT 
            id, conversation_id, NULL as agent_id, NULL as start_time, 
            NULL as goal, 'active' as status, NULL as context,
            title, created_at, updated_at, message_count, is_active,
            summary, tags, session_id, last_activity, workflow_state,
            conversation_type, import_source, quality_score, semantic_elements
        FROM conversations
    """)
    
    # Drop old table
    cursor.execute("DROP TABLE conversations")
    
    # Rename new table to conversations
    cursor.execute("ALTER TABLE conversations_new RENAME TO conversations")
    
    conn.commit()
    print("✓ Successfully migrated conversations table")
    
except Exception as e:
    print(f"✗ Migration failed: {e}")
    conn.rollback()
finally:
    conn.close()
