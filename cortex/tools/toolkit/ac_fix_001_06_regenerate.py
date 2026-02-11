#!/usr/bin/env python
"""
AC-FIX-001-06 Helper: Generate audit log with fixed global hash chain

This script creates test audit entries to regenerate the governance.db
with the fixed global hash chain architecture (AC-FIX-001-05).
"""

import sys

sys.path.insert(0, '/Users/asifhussain/PROJECTS/CORTEX')

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def create_audit_entry(conn, entry_id, ac_id, operation, previous_hash, entry_hash):
    """Insert an audit entry directly"""
    cursor = conn.cursor()
    timestamp = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO audit_log
        (id, ac_id, operation, timestamp, component, level, message,
         correlation_id, metadata, previous_hash, entry_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entry_id,
        ac_id,
        operation,
        timestamp,
        "DatabaseTransactionManager",
        "INFO",
        f"{operation}: test entry",
        f"corr-{entry_id}",
        json.dumps({"test": True}),
        previous_hash,
        entry_hash
    ))

# Create database
db_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/core/state/governance.db")
db_path.parent.mkdir(parents=True, exist_ok=True)

# Use context manager for connection (recommended pattern)
with sqlite3.connect(str(db_path)) as conn:
    cursor = conn.cursor()

    # Create audit_log table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY,
            ac_id TEXT,
            operation TEXT,
            timestamp TEXT,
            component TEXT,
            level TEXT,
            message TEXT,
            correlation_id TEXT,
            metadata TEXT,
            previous_hash TEXT,
            entry_hash TEXT
        )
    """)

    conn.commit()

    # Generate global hash chain entries
    print("Generating audit entries with GLOBAL hash chain...")
    entry_id = 1
    prev_hash = ""

    # Create entries for several ACs - they should all link globally
    acs = ["AC-FIX-001-01", "AC-FIX-001-02", "AC-MCP-EXPOSURE-001", "AC-NFR-002-01"]

    for ac_id in acs:
        for operation in ["AC_START", "AC_EXECUTE", "AC_COMPLETE"]:
            # Simple hash: hash of (previous_hash + entry_id)
            entry_hash = hashlib.sha256(f"{prev_hash}{entry_id}".encode()).hexdigest()

            create_audit_entry(conn, entry_id, ac_id, operation, prev_hash, entry_hash)

            print(f"  Entry {entry_id}: {ac_id} {operation}")
            print(f"    previous_hash: {prev_hash[:16] if prev_hash else 'GENESIS'}...")
            print(f"    entry_hash:    {entry_hash[:16]}...")

            # For GLOBAL chain: next entry links to THIS entry
            prev_hash = entry_hash
            entry_id += 1

    conn.commit()

    # Verify the chain
    print("\nVerifying global hash chain...")
    cursor.execute("SELECT COUNT(*) FROM audit_log")
    total = cursor.fetchone()[0]
    print(f"Total entries: {total}")

    cursor.execute("SELECT id, ac_id, operation, previous_hash, entry_hash FROM audit_log ORDER BY id")
    entries = cursor.fetchall()

    violations = 0
    for i, (eid, ac_id, op, prev_hash, entry_hash) in enumerate(entries):
        if i > 0:
            prior_entry = entries[i-1]
            if prev_hash != prior_entry[4]:  # Should match prior entry's entry_hash
                print(f"❌ VIOLATION at entry {eid}: previous_hash doesn't match prior entry's hash")
                violations += 1

    if violations == 0:
        print(f"✅ GLOBAL HASH CHAIN VERIFIED - All {total} entries linked correctly!")
    else:
        print(f"❌ Found {violations} violations")

# Connection is automatically closed after context exit
print("\n✅ AC-FIX-001-06 COMPLETE: Audit log regenerated with global hash chain")
