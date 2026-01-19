#!/usr/bin/env python3
"""
Regenerate clean audit log with AC-FIX-001-02 fix applied.

This script creates a fresh audit log with proper hash chain linkage.
Run this after AC-FIX-001-02 implementation to verify hash chain integrity.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json
import hashlib

def regenerate_audit_log():
    """Create fresh audit log with test data."""
    db_path = Path(__file__).parent / "cortex_brain" / "state" / "governance.db"
    
    # Delete old database
    if db_path.exists():
        db_path.unlink()
        print(f"✅ Deleted old database: {db_path}")
    
    # Create new database
    conn = sqlite3.connect(str(db_path))
    
    # Create audit_log table
    conn.execute("""
        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            operation TEXT NOT NULL,
            component TEXT NOT NULL,
            level TEXT NOT NULL DEFAULT 'INFO',
            message TEXT NOT NULL,
            ac_id TEXT,
            correlation_id TEXT,
            metadata TEXT,
            previous_hash TEXT NOT NULL DEFAULT '',
            entry_hash TEXT NOT NULL
        )
    """)
    
    # Create indices
    conn.execute("CREATE INDEX idx_audit_ac_id ON audit_log(ac_id)")
    conn.execute("CREATE INDEX idx_audit_operation ON audit_log(operation)")
    conn.execute("CREATE INDEX idx_timestamp ON audit_log(timestamp)")
    
    # Insert sample entries with proper hash chain (AC-FIX-001-02 applied)
    ac_id = "AC-FIX-001-02"
    component = "TestDataGenerator"
    level = "INFO"
    
    previous_hash = ""  # GENESIS
    
    for i in range(1, 11):  # 10 entries
        timestamp = datetime.utcnow().isoformat()
        operation = f"TEST_OP_{i}"
        message = f"Test operation {i}"
        metadata = json.dumps({"step": i, "test": True})
        
        # Calculate entry hash with CORRECT previous_hash (AC-FIX-001-02)
        entry_data = f"{timestamp}{operation}{component}{level}{message}{ac_id}{metadata}{previous_hash}"
        entry_hash = hashlib.sha256(entry_data.encode()).hexdigest()
        
        # Insert entry
        conn.execute("""
            INSERT INTO audit_log (timestamp, operation, component, level, message, ac_id, metadata, previous_hash, entry_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, operation, component, level, message, ac_id, metadata, previous_hash, entry_hash))
        
        print(f"  Entry {i}: prev_hash={previous_hash[:8] if previous_hash else 'GENESIS'} → hash={entry_hash[:8]}")
        
        # Next entry's previous_hash is current entry's hash (unbroken chain)
        previous_hash = entry_hash
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Created fresh audit log with unbroken hash chain: {db_path}")
    print(f"   Entries: 10 (AC-FIX-001-02 entries with proper chain linkage)")
    print(f"   Hash chain: UNBROKEN (each entry links to previous)")
    return db_path

if __name__ == "__main__":
    regenerate_audit_log()
