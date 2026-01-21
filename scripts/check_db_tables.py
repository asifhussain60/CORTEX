import sqlite3
from pathlib import Path

# Dynamic path resolution (CORE-005 compliance)
db_path = Path(__file__).parent.parent / "cortex_brain" / "state" / "governance.db"
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('Tables in database:')
for row in cursor.fetchall():
    print(f'  - {row[0]}')
    # Get row count for each table
    table_name = row[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f'    Row count: {count}')
conn.close()
