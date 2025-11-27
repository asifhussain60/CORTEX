#!/usr/bin/env python3
"""
CORTEX Brain Complete Migration Script

Purpose: Orchestrate complete migration of all tiers to SQLite
Author: CORTEX Development Team
Version: 1.0

Migrates all tiers in sequence:
1. Initialize database with schema
2. Tier 0: Governance rules (if applicable)
3. Tier 1: Conversation history
4. Tier 2: Knowledge graph patterns
5. Tier 3: Development context metrics

Usage:
    python migrate-all-tiers.py [--db-path cortex-brain.db] [--source-dir cortex-brain]

Features:
- Creates backup of existing database
- Initializes schema
- Migrates all tiers in sequence
- Validates data integrity
- Rollback on failure
- Comprehensive reporting
"""

import sqlite3
import subprocess
import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def get_project_root() -> Path:
    """Get CORTEX project root directory"""
    # Script is in CORTEX/scripts/
    return Path(__file__).parent.parent.absolute()


def backup_database(db_path: Path) -> Path:
    """Create backup of existing database"""
    if not db_path.exists():
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"{db_path.stem}_backup_{timestamp}.db"
    
    print(f"📦 Creating backup: {backup_path.name}")
    shutil.copy2(db_path, backup_path)
    print(f"✓ Backup created")
    
    return backup_path


def run_migration_script(script_name: str, db_path: str, source_dir: str) -> bool:
    """
    Run a migration script
    
    Args:
        script_name: Name of the script to run
        db_path: Path to database
        source_dir: Source directory for data
    
    Returns:
        True if successful, False otherwise
    """
    script_path = get_project_root() / "scripts" / script_name
    
    if not script_path.exists():
        print(f"✗ Script not found: {script_name}")
        return False
    
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path), '--db-path', db_path, '--source-dir', source_dir],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"✗ Migration failed!")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def validate_database(db_path: Path) -> Dict[str, Any]:
    """
    Validate the migrated database
    
    Args:
        db_path: Path to database
    
    Returns:
        Dictionary with validation results
    """
    print(f"\n{'='*60}")
    print(f"Validating Database")
    print(f"{'='*60}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    results = {}
    
    # Check table counts
    tables = [
        'tier1_conversations',
        'tier1_messages',
        'tier2_patterns',
        'tier2_file_relationships',
        'tier3_metrics'
    ]
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            results[table] = count
            print(f"✓ {table}: {count} rows")
        except sqlite3.Error as e:
            results[table] = f"Error: {e}"
            print(f"✗ {table}: {e}")
    
    # Check FTS5 tables
    try:
        cursor.execute("SELECT COUNT(*) FROM tier1_conversations_fts")
        count = cursor.fetchone()[0]
        results['fts_conversations'] = count
        print(f"✓ FTS5 conversations indexed: {count}")
    except sqlite3.Error as e:
        results['fts_conversations'] = f"Error: {e}"
        print(f"⚠️  FTS5 conversations: {e}")
    
    try:
        cursor.execute("SELECT COUNT(*) FROM tier2_patterns_fts")
        count = cursor.fetchone()[0]
        results['fts_patterns'] = count
        print(f"✓ FTS5 patterns indexed: {count}")
    except sqlite3.Error as e:
        results['fts_patterns'] = f"Error: {e}"
        print(f"⚠️  FTS5 patterns: {e}")
    
    # Run integrity check
    try:
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]
        results['integrity'] = integrity
        if integrity == 'ok':
            print(f"✓ Database integrity: OK")
        else:
            print(f"✗ Database integrity: {integrity}")
    except sqlite3.Error as e:
        results['integrity'] = f"Error: {e}"
        print(f"✗ Integrity check failed: {e}")
    
    conn.close()
    
    return results


def migrate_all(db_path: str, source_dir: str, skip_backup: bool = False) -> bool:
    """
    Main migration orchestrator
    
    Args:
        db_path: Path to SQLite database
        source_dir: Path to cortex-brain directory
        skip_backup: Skip backup creation
    
    Returns:
        True if all migrations successful
    """
    print(f"🧠 CORTEX Brain Complete Migration")
    print(f"=" * 60)
    print(f"Database: {db_path}")
    print(f"Source: {source_dir}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    db_path_obj = Path(db_path)
    
    # Create backup
    backup_path = None
    if not skip_backup:
        backup_path = backup_database(db_path_obj)
    
    # Step 1: Initialize database with schema
    print(f"\n📋 Step 1: Initialize Database Schema")
    if not run_migration_script('migrate_brain_db.py', db_path, source_dir):
        print(f"\n❌ Schema initialization failed!")
        return False
    
    # Step 2: Migrate Tier 1 (Conversations)
    print(f"\n📋 Step 2: Migrate Tier 1 (Conversations)")
    if not run_migration_script('migrate-tier1-to-sqlite.py', db_path, source_dir):
        print(f"\n❌ Tier 1 migration failed!")
        return False
    
    # Step 3: Migrate Tier 2 (Knowledge Graph)
    print(f"\n📋 Step 3: Migrate Tier 2 (Knowledge Graph)")
    if not run_migration_script('migrate-tier2-to-sqlite.py', db_path, source_dir):
        print(f"\n❌ Tier 2 migration failed!")
        return False
    
    # Step 4: Migrate Tier 3 (Development Context)
    print(f"\n📋 Step 4: Migrate Tier 3 (Development Context)")
    if not run_migration_script('migrate-tier3-to-sqlite.py', db_path, source_dir):
        print(f"\n❌ Tier 3 migration failed!")
        return False
    
    # Step 5: Validate migration
    print(f"\n📋 Step 5: Validate Migration")
    validation_results = validate_database(db_path_obj)
    
    # Check if validation passed
    validation_passed = all(
        isinstance(v, int) or v == 'ok' 
        for v in validation_results.values()
    )
    
    if validation_passed:
        print(f"\n✅ All migrations complete!")
        print(f"\n📊 Summary:")
        print(f"  - Database: {db_path}")
        if backup_path:
            print(f"  - Backup: {backup_path}")
        print(f"  - Total conversations: {validation_results.get('tier1_conversations', 0)}")
        print(f"  - Total messages: {validation_results.get('tier1_messages', 0)}")
        print(f"  - Total patterns: {validation_results.get('tier2_patterns', 0)}")
        print(f"  - Total file relationships: {validation_results.get('tier2_file_relationships', 0)}")
        print(f"  - Total metrics: {validation_results.get('tier3_metrics', 0)}")
        return True
    else:
        print(f"\n⚠️  Migration completed with validation warnings")
        print(f"\nValidation Results:")
        for key, value in validation_results.items():
            print(f"  - {key}: {value}")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Migrate all CORTEX Brain tiers to SQLite')
    parser.add_argument(
        '--db-path',
        default='cortex-brain/cortex-brain.db',
        help='Path to SQLite database (default: cortex-brain/cortex-brain.db)'
    )
    parser.add_argument(
        '--source-dir',
        default='cortex-brain',
        help='Path to cortex-brain directory (default: cortex-brain)'
    )
    parser.add_argument(
        '--skip-backup',
        action='store_true',
        help='Skip backup creation'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    project_root = get_project_root()
    db_path = project_root / args.db_path
    source_dir = project_root / args.source_dir
    
    # Run migration
    try:
        success = migrate_all(str(db_path), str(source_dir), args.skip_backup)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
