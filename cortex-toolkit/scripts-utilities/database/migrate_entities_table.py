import sqlite3
import os

db_path = 'cortex-brain/tier1/working_memory.db'

if not os.path.exists(db_path):
    print(f"ERROR: Database not found at {db_path}")
    exit(1)

print("Migrating entities table to match code expectations...")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if entities table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entities'")
    if not cursor.fetchone():
        print("Creating entities table...")
        cursor.execute("""
            CREATE TABLE entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_value TEXT NOT NULL,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_conversation ON entities(conversation_id)")
        print("✓ Successfully created entities table")
    else:
        # Check current columns
        cursor.execute("PRAGMA table_info(entities)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Add missing columns
        if 'entity_value' not in columns:
            cursor.execute("ALTER TABLE entities ADD COLUMN entity_value TEXT")
            print("✓ Successfully added entity_value column")
        else:
            print("✓ entity_value column already exists")
        
        if 'conversation_id' not in columns:
            cursor.execute("ALTER TABLE entities ADD COLUMN conversation_id TEXT")
            print("✓ Successfully added conversation_id column")
        else:
            print("✓ conversation_id column already exists")
    
    # Add end_time column to conversations if missing
    cursor.execute("PRAGMA table_info(conversations)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'end_time' not in columns:
        cursor.execute("ALTER TABLE conversations ADD COLUMN end_time TEXT")
        print("✓ Successfully added end_time column to conversations")
    else:
        print("✓ end_time column already exists in conversations")
    
    conn.commit()
    print("\n✓ Migration completed successfully")
    
except Exception as e:
    print(f"✗ Migration failed: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
finally:
    conn.close()
