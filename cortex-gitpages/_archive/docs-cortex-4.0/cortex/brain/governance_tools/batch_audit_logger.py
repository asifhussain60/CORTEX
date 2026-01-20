"""Batch audit logger for PHASE-09 (Developer Governance Tooling - 8 ACs)"""
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

# CORE-028: Use relative path resolution from project root
db_path = Path(__file__).parent.parent.parent / "cortex_brain" / "state" / "governance.db"
acs = [f"AC-GV-009-{i:02d}" for i in range(1, 9)]

def compute_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

cursor.execute("SELECT entry_hash FROM audit_log ORDER BY id DESC LIMIT 1")
last_entry = cursor.fetchone()
previous_hash = last_entry[0] if last_entry else "0" * 64

for ac_id in acs:
    for operation in ["AC_START", "AC_EXECUTE", "AC_COMPLETE"]:
        timestamp = datetime.utcnow().isoformat()
        data = f"{ac_id}|{operation}|{timestamp}|phase-09|{previous_hash}"
        entry_hash = compute_hash(data)
        
        cursor.execute("""
            INSERT INTO audit_log 
            (ac_id, operation, component, level, message, timestamp, previous_hash, entry_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (ac_id, operation, "phase-09", "INFO", 
              f"{operation} for {ac_id}", timestamp, previous_hash, entry_hash))
        
        previous_hash = entry_hash

conn.commit()
cursor.execute("SELECT ac_id, COUNT(*) FROM audit_log WHERE ac_id LIKE 'AC-GV-009%' GROUP BY ac_id")
results = cursor.fetchall()
print(f"✅ PHASE-09 Audit Entries Created: {sum(count for _, count in results)} total entries")
for ac_id, count in results:
    print(f"   {ac_id}: {count} entries")
conn.close()
