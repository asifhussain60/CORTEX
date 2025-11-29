"""
Enhancement Catalog Schema Migration Script

Adds missing Enhancement Catalog tables to existing context.db databases.
Handles cross-platform database initialization issue where Architecture Health
Store created database first without Enhancement Catalog schema.

Usage:
    python scripts/migrate_enhancement_catalog_schema.py

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add CORTEX root to path
cortex_root = Path(__file__).parent.parent
sys.path.insert(0, str(cortex_root))

from src.config import config


def check_tables_exist(db_path: Path) -> dict:
    """Check which tables exist in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cursor.fetchall()}
    
    conn.close()
    
    return {
        'cortex_features': 'cortex_features' in existing_tables,
        'cortex_review_log': 'cortex_review_log' in existing_tables,
        'architecture_health_history': 'architecture_health_history' in existing_tables
    }


def migrate_enhancement_catalog_schema(db_path: Path):
    """Add Enhancement Catalog tables to existing database."""
    
    print(f"\n🔍 Checking database: {db_path}")
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    # Check existing tables
    table_status = check_tables_exist(db_path)
    print(f"\n📋 Current Tables:")
    for table, exists in table_status.items():
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"   {table}: {status}")
    
    # Check if migration needed
    if table_status['cortex_features'] and table_status['cortex_review_log']:
        print(f"\n✅ Enhancement Catalog schema already exists - no migration needed")
        return True
    
    print(f"\n🔧 Migration needed - adding Enhancement Catalog tables...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add cortex_features table if missing
        if not table_status['cortex_features']:
            print(f"   Creating cortex_features table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cortex_features (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feature_hash TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    feature_type TEXT NOT NULL CHECK(feature_type IN 
                        ('operation', 'agent', 'orchestrator', 'workflow', 
                         'template', 'documentation', 'integration', 'utility')),
                    description TEXT NOT NULL,
                    first_seen TIMESTAMP NOT NULL,
                    last_updated TIMESTAMP NOT NULL,
                    source TEXT NOT NULL CHECK(source IN 
                        ('git', 'yaml', 'codebase', 'template', 'documentation', 'manual')),
                    acceptance_status TEXT NOT NULL DEFAULT 'discovered' 
                        CHECK(acceptance_status IN ('discovered', 'accepted', 'deprecated', 'removed')),
                    acceptance_notes TEXT
                )
            """)
            
            # Add indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_features_type ON cortex_features(feature_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_features_status ON cortex_features(acceptance_status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_features_first_seen ON cortex_features(first_seen)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_features_last_updated ON cortex_features(last_updated)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_features_source ON cortex_features(source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_features_hash ON cortex_features(feature_hash)")
            
            print(f"   ✅ cortex_features table created with 6 indexes")
        
        # Add cortex_review_log table if missing
        if not table_status['cortex_review_log']:
            print(f"   Creating cortex_review_log table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cortex_review_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    review_timestamp TIMESTAMP NOT NULL,
                    review_type TEXT NOT NULL,
                    features_reviewed INTEGER NOT NULL DEFAULT 0,
                    new_features_found INTEGER NOT NULL DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Add indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_timestamp ON cortex_review_log(review_timestamp DESC)")
            
            print(f"   ✅ cortex_review_log table created with 1 index")
        
        conn.commit()
        print(f"\n✅ Migration successful!")
        
        # Verify migration
        print(f"\n🔍 Verifying migration...")
        table_status_after = check_tables_exist(db_path)
        print(f"📋 Tables After Migration:")
        for table, exists in table_status_after.items():
            status = "✅ EXISTS" if exists else "❌ MISSING"
            print(f"   {table}: {status}")
        
        if table_status_after['cortex_features'] and table_status_after['cortex_review_log']:
            print(f"\n✅ ALL TABLES VERIFIED - Enhancement Catalog ready to use")
            return True
        else:
            print(f"\n❌ VERIFICATION FAILED - Some tables still missing")
            return False
            
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def main():
    """Run Enhancement Catalog schema migration."""
    
    print("=" * 80)
    print("Enhancement Catalog Schema Migration")
    print("=" * 80)
    print(f"CORTEX Root: {config.root_path}")
    print(f"Brain Path: {config.brain_path}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Determine database path
    tier3_dir = config.brain_path / "tier3"
    db_path = tier3_dir / "context.db"
    
    print(f"\n🎯 Target Database: {db_path}")
    
    # Run migration
    success = migrate_enhancement_catalog_schema(db_path)
    
    if success:
        print(f"\n" + "=" * 80)
        print("✅ MIGRATION COMPLETE - Enhancement Catalog schema ready")
        print("=" * 80)
        print(f"\nNext Steps:")
        print(f"1. Run 'align' command to test cross-platform temporal tracking")
        print(f"2. Commit and push changes to git")
        print(f"3. Pull on other machine and verify alignment persists")
        return 0
    else:
        print(f"\n" + "=" * 80)
        print("❌ MIGRATION FAILED - Manual intervention required")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
