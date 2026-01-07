import sqlite3
import os

db_path = 'cortex-brain/tier1/working_memory.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='conversations'")
    result = cursor.fetchone()
    if result:
        print("Current conversations table schema:")
        print(result[0])
    else:
        print("No 'conversations' table found")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("\nAvailable tables:")
        for table in tables:
            print(f"  - {table[0]}")
    conn.close()
