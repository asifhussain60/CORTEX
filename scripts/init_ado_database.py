"""
ADO Work Items Database Initialization Script

Creates SQLite database with FTS5 full-text search for scalable ADO planning.
Supports 10,000+ work items with instant search and efficient filtering.

Database: cortex-brain/ado-work-items.db
Tables:
- ado_work_items: Main table with work item data
- ado_search: FTS5 virtual table for full-text search
- ado_activity_log: Complete audit trail

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json
import sys
import platform


def get_brain_path() -> str:
    """
    Get the cortex-brain path based on the current machine
    
    Returns:
        str: Path to cortex-brain directory
    """
    # Try to read from config first
    config_path = Path(__file__).parent.parent / "cortex.config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Get machine-specific config
            hostname = platform.node()
            if hostname in config.get('machines', {}):
                brain_path = config['machines'][hostname].get('brainPath')
                if brain_path:
                    return brain_path
        except Exception:
            pass  # Fall through to default
    
    # Default: assume cortex-brain is in parent directory
    return str(Path(__file__).parent.parent / "cortex-brain")


def init_ado_database(db_path: str = None) -> sqlite3.Connection:
    """
    Initialize ADO work items database with schema and indexes
    
    Args:
        db_path: Optional custom database path. Defaults to cortex-brain/ado-work-items.db
    
    Returns:
        sqlite3.Connection: Database connection
    """
    if db_path is None:
        brain_path = get_brain_path()
        db_path = Path(brain_path) / "ado-work-items.db"
    else:
        db_path = Path(db_path)
    
    # Create cortex-brain directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database (creates if doesn't exist)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = conn.cursor()
    
    print(f"Initializing ADO database: {db_path}")
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # ========================================
    # 1. ADO Work Items Table (Main Storage)
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ado_work_items (
            ado_number TEXT PRIMARY KEY,
            type TEXT NOT NULL CHECK (type IN ('Bug', 'User Story', 'Feature', 'Task', 'Epic')),
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'planning' 
                CHECK (status IN ('planning', 'ready', 'in_progress', 'done', 'blocked', 'cancelled')),
            priority TEXT CHECK (priority IS NULL OR priority IN ('Critical', 'High', 'Medium', 'Low')),
            
            -- Template file location
            template_file_path TEXT NOT NULL UNIQUE,
            
            -- DoR/DoD tracking (0-100 percentage)
            dor_completed INTEGER NOT NULL DEFAULT 0 CHECK (dor_completed >= 0 AND dor_completed <= 100),
            dod_completed INTEGER NOT NULL DEFAULT 0 CHECK (dod_completed >= 0 AND dod_completed <= 100),
            
            -- Timestamps
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            last_accessed TEXT NOT NULL DEFAULT (datetime('now')),
            completed_at TEXT,
            
            -- Context integration (JSON arrays)
            conversation_ids TEXT,  -- ["conv-001", "conv-002"]
            related_file_paths TEXT,  -- ["src/auth.py", "src/login.tsx"]
            commit_shas TEXT,  -- ["abc123", "def456"]
            
            -- Metadata
            assigned_to TEXT,
            tags TEXT,  -- ["authentication", "security"]
            estimated_hours REAL CHECK (estimated_hours IS NULL OR estimated_hours >= 0),
            actual_hours REAL CHECK (actual_hours IS NULL OR actual_hours >= 0)
        )
    """)
    
    # Create indexes for fast filtering and sorting
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ado_status ON ado_work_items(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ado_type ON ado_work_items(type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ado_priority ON ado_work_items(priority)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ado_updated ON ado_work_items(updated_at DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ado_assigned ON ado_work_items(assigned_to)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ado_status_priority ON ado_work_items(status, priority)")
    
    print("✓ Created ado_work_items table with indexes")
    
    # ========================================
    # 2. FTS5 Full-Text Search Table
    # ========================================
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS ado_search USING fts5(
            ado_number UNINDEXED,
            title,
            tags,
            content='ado_work_items',
            content_rowid='rowid'
        )
    """)
    
    # Triggers to keep FTS5 in sync
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS ado_fts_insert AFTER INSERT ON ado_work_items BEGIN
            INSERT INTO ado_search(rowid, ado_number, title, tags)
            VALUES (new.rowid, new.ado_number, new.title, new.tags);
        END
    """)
    
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS ado_fts_update AFTER UPDATE ON ado_work_items BEGIN
            UPDATE ado_search 
            SET title = new.title, tags = new.tags
            WHERE rowid = new.rowid;
        END
    """)
    
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS ado_fts_delete AFTER DELETE ON ado_work_items BEGIN
            DELETE FROM ado_search WHERE rowid = old.rowid;
        END
    """)
    
    print("✓ Created ado_search FTS5 table with sync triggers")
    
    # ========================================
    # 3. Activity Log Table (Audit Trail)
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ado_activity_log (
            activity_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            ado_number TEXT NOT NULL,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            action TEXT NOT NULL CHECK (action IN (
                'created', 'updated', 'status_changed', 'accessed', 'imported', 
                'exported', 'archived', 'deleted', 'restored', 'commented'
            )),
            old_value TEXT,
            new_value TEXT,
            changed_by TEXT DEFAULT 'cortex',
            notes TEXT,
            
            FOREIGN KEY (ado_number) REFERENCES ado_work_items(ado_number) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_ado ON ado_activity_log(ado_number, timestamp DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_action ON ado_activity_log(action)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON ado_activity_log(timestamp DESC)")
    
    print("✓ Created ado_activity_log table with indexes")
    
    # ========================================
    # 4. Trigger for Updated Timestamp
    # ========================================
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS ado_update_timestamp 
        AFTER UPDATE ON ado_work_items
        FOR EACH ROW
        BEGIN
            UPDATE ado_work_items 
            SET updated_at = datetime('now')
            WHERE ado_number = NEW.ado_number;
        END
    """)
    
    print("✓ Created auto-update timestamp trigger")
    
    # ========================================
    # 5. Database Metadata
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ado_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    
    # Insert metadata
    metadata = [
        ('schema_version', '1.0.0'),
        ('created_at', datetime.now().isoformat()),
        ('last_migration', 'none'),
        ('cortex_version', '3.0'),
        ('description', 'ADO Planning System Database with FTS5 Search')
    ]
    
    for key, value in metadata:
        cursor.execute("""
            INSERT OR REPLACE INTO ado_metadata (key, value, updated_at)
            VALUES (?, ?, datetime('now'))
        """, (key, value))
    
    print("✓ Inserted database metadata")
    
    # Commit all changes
    conn.commit()
    
    # ========================================
    # 6. Verify Setup
    # ========================================
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = [
        'ado_work_items', 'ado_search', 'ado_activity_log', 'ado_metadata'
    ]
    
    missing_tables = set(expected_tables) - set(tables)
    if missing_tables:
        print(f"⚠ Warning: Missing tables: {missing_tables}")
    else:
        print("✓ All tables created successfully")
    
    # Verify FTS5
    cursor.execute("SELECT COUNT(*) FROM ado_search")
    print(f"✓ FTS5 search table operational (0 entries)")
    
    # Display statistics
    cursor.execute("SELECT COUNT(*) FROM ado_work_items")
    item_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ado_activity_log")
    activity_count = cursor.fetchone()[0]
    
    print(f"\n{'='*60}")
    print(f"ADO Database Initialized Successfully")
    print(f"{'='*60}")
    print(f"Database Path: {db_path}")
    print(f"Schema Version: 1.0.0")
    print(f"Tables: {len(tables)} ({', '.join(tables)})")
    print(f"ADO Work Items: {item_count}")
    print(f"Activity Log Entries: {activity_count}")
    print(f"FTS5 Search: Enabled")
    print(f"Performance: Optimized for 10,000+ items")
    print(f"{'='*60}\n")
    
    return conn


def add_sample_data(conn: sqlite3.Connection):
    """
    Add sample ADO work items for testing
    
    Args:
        conn: Database connection
    """
    cursor = conn.cursor()
    
    sample_items = [
        {
            'ado_number': '12345',
            'type': 'Feature',
            'title': 'User Authentication System',
            'status': 'in_progress',
            'priority': 'High',
            'template_file_path': 'cortex-brain/documents/planning/ado/active/ADO-12345-in-progress-user-authentication.md',
            'dor_completed': 100,
            'dod_completed': 40,
            'tags': json.dumps(['authentication', 'security', 'user-management']),
            'estimated_hours': 16.0,
            'assigned_to': 'developer1'
        },
        {
            'ado_number': '12346',
            'type': 'Bug',
            'title': 'Login page crash on Safari',
            'status': 'blocked',
            'priority': 'Critical',
            'template_file_path': 'cortex-brain/documents/planning/ado/blocked/ADO-12346-blocked-login-crash.md',
            'dor_completed': 100,
            'dod_completed': 0,
            'tags': json.dumps(['bug', 'safari', 'login']),
            'estimated_hours': 4.0,
            'assigned_to': 'developer2'
        },
        {
            'ado_number': '12347',
            'type': 'User Story',
            'title': 'As a user I want to reset my password',
            'status': 'ready',
            'priority': 'Medium',
            'template_file_path': 'cortex-brain/documents/planning/ado/active/ADO-12347-ready-password-reset.md',
            'dor_completed': 100,
            'dod_completed': 0,
            'tags': json.dumps(['user-story', 'password', 'security']),
            'estimated_hours': 8.0
        }
    ]
    
    for item in sample_items:
        try:
            cursor.execute("""
                INSERT INTO ado_work_items (
                    ado_number, type, title, status, priority, template_file_path,
                    dor_completed, dod_completed, tags, estimated_hours, assigned_to
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item['ado_number'], item['type'], item['title'], item['status'],
                item['priority'], item['template_file_path'], item['dor_completed'],
                item['dod_completed'], item['tags'], item['estimated_hours'],
                item.get('assigned_to')
            ))
            
            # Log creation activity
            cursor.execute("""
                INSERT INTO ado_activity_log (ado_number, action, new_value, notes)
                VALUES (?, 'created', ?, 'Sample data for testing')
            """, (item['ado_number'], item['status']))
            
            print(f"✓ Added sample ADO-{item['ado_number']}: {item['title']}")
            
        except sqlite3.IntegrityError as e:
            print(f"⚠ ADO-{item['ado_number']} already exists, skipping")
    
    conn.commit()
    print(f"\n✓ Sample data added successfully")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize ADO Work Items Database")
    parser.add_argument("--db-path", help="Custom database path", default=None)
    parser.add_argument("--sample-data", action="store_true", help="Add sample work items for testing")
    parser.add_argument("--reset", action="store_true", help="Reset database (WARNING: deletes all data)")
    
    args = parser.parse_args()
    
    # Handle reset
    if args.reset:
        if args.db_path:
            db_path = Path(args.db_path)
        else:
            brain_path = get_brain_path()
            db_path = Path(brain_path) / "ado-work-items.db"
        
        if db_path.exists():
            confirm = input(f"⚠ WARNING: This will delete {db_path}. Continue? (yes/no): ")
            if confirm.lower() == 'yes':
                db_path.unlink()
                print(f"✓ Deleted {db_path}")
            else:
                print("Reset cancelled")
                sys.exit(0)
    
    # Initialize database
    conn = init_ado_database(args.db_path)
    
    # Add sample data if requested
    if args.sample_data:
        print("\nAdding sample data...")
        add_sample_data(conn)
    
    conn.close()
    print("\n✅ Database initialization complete")
