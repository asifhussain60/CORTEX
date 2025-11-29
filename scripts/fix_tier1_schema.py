#!/usr/bin/env python3
"""Fix Tier 1 database schema - Add messages table"""

import sqlite3
from pathlib import Path

db_path = Path("cortex-brain/conversation-history.db")

print("🔧 Tier 1 Database Migration")
print("=" * 60)

# Connect to database
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check current tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cur.fetchall()]
print(f"\nCurrent tables: {tables}")

# Create messages table if it doesn't exist
if 'messages' not in tables:
    print("\n Creating messages table...")
    cur.execute("""
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            metadata TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)
    
    # Create index for faster lookups
    cur.execute("""
        CREATE INDEX idx_messages_conversation 
        ON messages(conversation_id)
    """)
    
    conn.commit()
    print("✅ Messages table created successfully")
else:
    print("✅ Messages table already exists")

# Verify schema
cur.execute("PRAGMA table_info(messages)")
columns = cur.fetchall()
print(f"\nMessages table columns: {len(columns)}")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()

print("\n" + "=" * 60)
print("✅ Database migration complete!")
