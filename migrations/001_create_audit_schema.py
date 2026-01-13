#!/usr/bin/env python3
"""
Audit Database Schema Migration - AC-BRITTLE-002
Creates required tables for governance audit trail
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timezone

def create_audit_schema(db_path):
    """Create audit schema with all required tables"""
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Enable WAL mode for concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        
        # Create audit_logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                correlation_id TEXT,
                category TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT,
                ac_id TEXT,
                orchestrator TEXT,
                phase TEXT,
                user TEXT,
                metadata TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ac_id ON audit_logs(ac_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_logs(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON audit_logs(category)")
        print("✅ Created table: audit_logs")
        
        # Create rule_violations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rule_violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                rule_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT,
                file_path TEXT,
                line_number INTEGER,
                resolution TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rule_id ON rule_violations(rule_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_vio_timestamp ON rule_violations(timestamp)")
        print("✅ Created table: rule_violations")
        
        # Create evidence_bundles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence_bundles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ac_id TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                test_count INTEGER,
                passing_count INTEGER,
                coverage_percent REAL,
                bundle_path TEXT,
                status TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bundle_ac_id ON evidence_bundles(ac_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bundle_created ON evidence_bundles(created_at)")
        print("✅ Created table: evidence_bundles")
        
        # Create orchestrator_trace table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orchestrator_trace (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                correlation_id TEXT,
                orchestrator_name TEXT NOT NULL,
                phase TEXT,
                status TEXT,
                duration_ms INTEGER,
                error TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orch_name ON orchestrator_trace(orchestrator_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orch_timestamp ON orchestrator_trace(timestamp)")
        print("✅ Created table: orchestrator_trace")
        
        # Create phase_transitions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phase_transitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                from_phase TEXT,
                to_phase TEXT,
                ac_ids_completed INTEGER,
                ac_ids_total INTEGER,
                reason TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_phase_timestamp ON phase_transitions(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_from_phase ON phase_transitions(from_phase)")
        print("✅ Created table: phase_transitions")
        
        # Create metadata table for schema versioning
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        """)
        print("✅ Created table: schema_metadata")
        
        # Record schema version
        cursor.execute("""
            INSERT OR REPLACE INTO schema_metadata (key, value, updated_at)
            VALUES ('schema_version', '1.0', ?)
        """, (datetime.now(timezone.utc).isoformat(),))
        
        cursor.execute("""
            INSERT OR REPLACE INTO schema_metadata (key, value, updated_at)
            VALUES ('created_at', ?, ?)
        """, (datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat()))
        
        conn.commit()
        print("\n✅ FIXED AC-BRITTLE-002: Audit schema initialized with 6 tables")
        return True
        
    except Exception as e:
        print(f"❌ Error creating audit schema: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    db_path = Path("cortex-brain/database/governance.db")
    create_audit_schema(db_path)
