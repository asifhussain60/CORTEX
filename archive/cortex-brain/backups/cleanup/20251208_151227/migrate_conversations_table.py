import sqlite3
import os

db_path = 'cortex-brain/tier1/working_memory.db'

if not os.path.exists(db_path):
    print(f"ERROR: Database not found at {db_path}")
    exit(1)

print("Adding agent_id column to conversations table...")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if column already exists
    cursor.execute("PRAGMA table_info(conversations)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'agent_id' in columns:
        print("✓ agent_id column already exists")
    else:
        # Add the agent_id column
        cursor.execute("ALTER TABLE conversations ADD COLUMN agent_id TEXT")
        conn.commit()
        print("✓ Successfully added agent_id column")
    
    # Check if goal column exists
    if 'goal' not in columns:
        cursor.execute("ALTER TABLE conversations ADD COLUMN goal TEXT")
        conn.commit()
        print("✓ Successfully added goal column")
    else:
        print("✓ goal column already exists")
    
    # Check if start_time column exists
    if 'start_time' not in columns:
        cursor.execute("ALTER TABLE conversations ADD COLUMN start_time TEXT")
        conn.commit()
        print("✓ Successfully added start_time column")
    else:
        print("✓ start_time column already exists")
    
    # Check if status column exists
    if 'status' not in columns:
        cursor.execute("ALTER TABLE conversations ADD COLUMN status TEXT DEFAULT 'active'")
        conn.commit()
        print("✓ Successfully added status column")
    else:
        print("✓ status column already exists")
    
    # Check if context column exists
    if 'context' not in columns:
        cursor.execute("ALTER TABLE conversations ADD COLUMN context TEXT")
        conn.commit()
        print("✓ Successfully added context column")
    else:
        print("✓ context column already exists")
    
    print("\n✓ Migration completed successfully")
    
except Exception as e:
    print(f"✗ Migration failed: {e}")
    conn.rollback()
finally:
    conn.close()
