import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent.parent / "cortex-brain" / "tier1" / "conversations.db"

if not db_path.exists():
    print(f"❌ Database not found: {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"📊 Tables in database: {[t[0] for t in tables]}")

# Check conversation count
cursor.execute("SELECT COUNT(*) FROM conversations")
count = cursor.fetchone()[0]
print(f"\n💬 Total conversations: {count}")

# Get schema first
cursor.execute("PRAGMA table_info(conversations)")
columns = cursor.fetchall()
print(f"\n📋 Conversations table schema:")
for col in columns:
    print(f"  • {col[1]} ({col[2]})")

# Get recent conversations
cursor.execute("""
    SELECT * 
    FROM conversations 
    ORDER BY created_at DESC 
    LIMIT 10
""")

print("\n📝 Recent conversations:")
for row in cursor.fetchall():
    print(f"  • {row}")

# Check for roadmap-related conversations
cursor.execute("""
    SELECT * 
    FROM conversations 
    WHERE 1=1
    ORDER BY created_at DESC
    LIMIT 5
""")

print("\n🗺️  All conversations in database:")
results = cursor.fetchall()
if results:
    for row in results:
        print(f"  • {row}")
else:
    print("  ❌ No conversations found")

conn.close()
