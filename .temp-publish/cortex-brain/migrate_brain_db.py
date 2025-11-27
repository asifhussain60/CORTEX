#!/usr/bin/env python3
"""
CORTEX Brain Database Migration Script

Purpose: Initialize CORTEX Brain SQLite database with schema v1.0
Author: CORTEX Development Team
Version: 1.0

Usage:
    python migrate_brain_db.py [--db-path cortex-brain.db]

Features:
- Creates database if it doesn't exist
- Applies schema.sql
- Validates schema integrity
- Reports statistics
- Idempotent (safe to run multiple times)
"""

import sqlite3
import argparse
import os
from pathlib import Path
from datetime import datetime


def get_script_dir() -> Path:
    """Get directory where this script is located"""
    return Path(__file__).parent.absolute()


def load_schema_sql() -> str:
    """Load schema.sql from cortex-brain directory"""
    schema_path = get_script_dir() / "schema.sql"
    
    if not schema_path.exists():
        raise FileNotFoundError(
            f"Schema file not found: {schema_path}\n"
            f"Expected location: cortex-brain/schema.sql"
        )
    
    with open(schema_path, 'r') as f:
        return f.read()


def initialize_database(db_path: str) -> dict:
    """
    Initialize CORTEX Brain database
    
    Args:
        db_path: Path to SQLite database file
    
    Returns:
        Dictionary with migration statistics
    """
    print(f"🧠 CORTEX Brain Database Migration")
    print(f"=" * 60)
    print(f"Database: {db_path}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Check if database exists
    db_exists = os.path.exists(db_path)
    if db_exists:
        print(f"✓ Database file exists (will update schema)")
    else:
        print(f"✓ Creating new database")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(f"✓ Connected to database")
    
    # Load and execute schema
    print(f"\n📋 Applying schema...")
    schema_sql = load_schema_sql()
    
    # Execute schema (handles CREATE IF NOT EXISTS gracefully)
    try:
        cursor.executescript(schema_sql)
        conn.commit()
        print(f"✓ Schema applied successfully")
    except sqlite3.Error as e:
        print(f"✗ Schema application failed: {e}")
        conn.rollback()
        raise
    
    # Validate schema
    print(f"\n🔍 Validating schema...")
    stats = validate_schema(cursor)
    
    # Print statistics
    print(f"\n📊 Database Statistics:")
    print(f"  Tables: {stats['tables']}")
    print(f"  Indexes: {stats['indexes']}")
    print(f"  Views: {stats['views']}")
    print(f"  Triggers: {stats['triggers']}")
    print(f"  FTS5 Tables: {stats['fts5_tables']}")
    
    # Check schema version
    cursor.execute("SELECT version, applied_at FROM schema_version")
    version_row = cursor.fetchone()
    if version_row:
        print(f"\n✅ Schema Version: {version_row['version']}")
        print(f"   Applied: {version_row['applied_at']}")
    
    # Check configuration
    cursor.execute("SELECT COUNT(*) as count FROM configuration")
    config_count = cursor.fetchone()['count']
    print(f"\n⚙️  Configuration: {config_count} settings loaded")
    
    conn.close()
    print(f"\n✅ Migration complete!")
    print(f"=" * 60)
    
    return stats


def validate_schema(cursor: sqlite3.Cursor) -> dict:
    """
    Validate database schema integrity
    
    Args:
        cursor: SQLite cursor
    
    Returns:
        Dictionary with schema statistics
    """
    stats = {}
    
    # Count tables
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
    """)
    stats['tables'] = cursor.fetchone()['count']
    
    # Count indexes
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM sqlite_master 
        WHERE type='index' AND name NOT LIKE 'sqlite_%'
    """)
    stats['indexes'] = cursor.fetchone()['count']
    
    # Count views
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM sqlite_master 
        WHERE type='view'
    """)
    stats['views'] = cursor.fetchone()['count']
    
    # Count triggers
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM sqlite_master 
        WHERE type='trigger'
    """)
    stats['triggers'] = cursor.fetchone()['count']
    
    # Count FTS5 tables
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM sqlite_master 
        WHERE type='table' AND name LIKE '%_fts'
    """)
    stats['fts5_tables'] = cursor.fetchone()['count']
    
    # Validate expected tables exist
    expected_tables = [
        'tier0_rules',
        'tier1_conversations',
        'tier1_messages',
        'tier2_patterns',
        'tier2_file_relationships',
        'tier2_intent_patterns',
        'tier2_corrections',
        'tier2_pattern_searches',
        'tier3_git_commits',
        'tier3_file_metrics',
        'tier3_velocity_metrics',
        'tier3_test_activity',
        'tier3_work_patterns',
        'events',
        'configuration',
        'schema_version'
    ]
    
    for table in expected_tables:
        cursor.execute(f"""
            SELECT COUNT(*) as count 
            FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table,))
        
        if cursor.fetchone()['count'] == 0:
            raise ValueError(f"Expected table missing: {table}")
    
    print(f"  ✓ All {len(expected_tables)} core tables validated")
    
    # Validate FTS5 tables
    expected_fts5 = [
        'tier1_conversations_fts',
        'tier1_messages_fts',
        'tier2_patterns_fts'
    ]
    
    for fts_table in expected_fts5:
        cursor.execute(f"""
            SELECT COUNT(*) as count 
            FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (fts_table,))
        
        if cursor.fetchone()['count'] == 0:
            raise ValueError(f"Expected FTS5 table missing: {fts_table}")
    
    print(f"  ✓ All {len(expected_fts5)} FTS5 tables validated")
    
    # Validate views
    expected_views = [
        'view_active_conversations',
        'view_top_patterns',
        'view_pattern_reuse_stats',
        'view_git_velocity_weekly',
        'view_file_hotspots'
    ]
    
    for view in expected_views:
        cursor.execute(f"""
            SELECT COUNT(*) as count 
            FROM sqlite_master 
            WHERE type='view' AND name=?
        """, (view,))
        
        if cursor.fetchone()['count'] == 0:
            raise ValueError(f"Expected view missing: {view}")
    
    print(f"  ✓ All {len(expected_views)} views validated")
    
    return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Initialize CORTEX Brain SQLite database'
    )
    parser.add_argument(
        '--db-path',
        default='cortex-brain.db',
        help='Path to SQLite database file (default: cortex-brain.db)'
    )
    
    args = parser.parse_args()
    
    try:
        stats = initialize_database(args.db_path)
        return 0
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
