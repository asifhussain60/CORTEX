import sqlite3
conn = sqlite3.connect(r'd:\PROJECTS\CORTEX\cortex_brain\state\governance.db')
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
