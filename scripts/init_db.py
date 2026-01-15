#!/usr/bin/env python3
"""
Initialize and Sync Governance Database

This script manages the SQLite governance database state:
- Creates database if missing
- Syncs phase locks from cortex-master.yaml
- Syncs AC index from roadmap
- Preserves local audit logs (idempotent)

Usage:
    python scripts/init_db.py           # Full initialization
    python scripts/init_db.py --sync    # Sync from YAML only
    python scripts/init_db.py --reset   # Reset and reinitialize
    python scripts/init_db.py --status  # Show current state

Multi-Machine Strategy:
    - YAML files are the source of truth (git tracked)
    - SQLite is derived cache (regenerable)
    - Audit logs are local context (don't need sync)
    
Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.database import DatabaseManager
from src.tools.ac_populator import ACPopulator
from src.core.path_resolver import resolve_path


def load_phase_tracker():
    """Load phase_tracker from cortex-master.yaml."""
    import yaml
    
    master_path = resolve_path(".github", "roadmap", "cortex-master.yaml")
    if not master_path.exists():
        print(f"Warning: {master_path} not found")
        return {}
    
    with open(master_path, 'r') as f:
        data = yaml.safe_load(f)
    
    return data.get('phase_tracker', {})


def sync_phase_locks(db: DatabaseManager, phase_tracker: dict) -> dict:
    """
    Sync phase locks from YAML to database.
    
    Returns dict with sync statistics.
    """
    stats = {'updated': 0, 'inserted': 0, 'unchanged': 0}
    
    for phase_id, phase_data in phase_tracker.items():
        is_locked = phase_data.get('locked', False)
        locked_at = phase_data.get('completed_at')
        locked_by = 'cortex-master.yaml'
        
        # Check if exists
        result = db.execute(
            "SELECT locked FROM phase_locks WHERE phase_id = ?",
            (phase_id,)
        )
        
        if result.is_ok():
            rows = result.unwrap()
            if rows:
                # Update if different
                current_locked = bool(rows[0]['locked'])
                if current_locked != is_locked:
                    db.execute(
                        "UPDATE phase_locks SET locked = ?, locked_at = ?, locked_by = ? WHERE phase_id = ?",
                        (is_locked, locked_at, locked_by, phase_id)
                    )
                    stats['updated'] += 1
                else:
                    stats['unchanged'] += 1
            else:
                # Insert new
                db.execute(
                    "INSERT INTO phase_locks (phase_id, locked, locked_at, locked_by) VALUES (?, ?, ?, ?)",
                    (phase_id, is_locked, locked_at, locked_by)
                )
                stats['inserted'] += 1
    
    db._connection.commit()
    return stats


def get_database_status(db: DatabaseManager) -> dict:
    """Get current database status."""
    status = {}
    
    # Audit log count
    result = db.execute("SELECT COUNT(*) as count FROM audit_log")
    if result.is_ok():
        rows = result.unwrap()
        status['audit_log_count'] = rows[0]['count'] if rows else 0
    
    # AC index count
    result = db.execute("SELECT COUNT(*) as count FROM ac_index")
    if result.is_ok():
        rows = result.unwrap()
        status['ac_index_count'] = rows[0]['count'] if rows else 0
    
    # Phase locks
    result = db.execute("SELECT phase_id, locked FROM phase_locks ORDER BY phase_id")
    if result.is_ok():
        rows = result.unwrap()
        status['phase_locks'] = {row['phase_id']: bool(row['locked']) for row in rows}
    
    # Database file info
    db_path = db.config.db_path
    if db_path.exists():
        status['db_size_kb'] = db_path.stat().st_size // 1024
        status['db_path'] = str(db_path)
    
    return status


def main():
    parser = argparse.ArgumentParser(
        description='Initialize and sync CORTEX governance database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/init_db.py           # Full initialization (after clone)
  python scripts/init_db.py --sync    # Sync after git pull
  python scripts/init_db.py --status  # Check current state
  python scripts/init_db.py --reset   # Reset everything (caution!)
        """
    )
    parser.add_argument('--sync', action='store_true', 
                        help='Sync from YAML without full reinitialization')
    parser.add_argument('--reset', action='store_true',
                        help='Reset database (WARNING: clears audit logs)')
    parser.add_argument('--status', action='store_true',
                        help='Show current database status')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("CORTEX Governance Database Manager")
    print("=" * 60)
    print()
    
    # Initialize database manager
    db = DatabaseManager()
    
    if args.status:
        # Status only
        print("📊 Current Database Status")
        print("-" * 40)
        status = get_database_status(db)
        print(f"  Database: {status.get('db_path', 'Not found')}")
        print(f"  Size: {status.get('db_size_kb', 0)} KB")
        print(f"  Audit Logs: {status.get('audit_log_count', 0)} entries")
        print(f"  AC Index: {status.get('ac_index_count', 0)} entries")
        print()
        print("  Phase Locks:")
        for phase_id, locked in status.get('phase_locks', {}).items():
            icon = "🔒" if locked else "🔓"
            print(f"    {icon} {phase_id}: {'LOCKED' if locked else 'UNLOCKED'}")
        db.close()
        return
    
    if args.reset:
        # Full reset (dangerous!)
        print("⚠️  WARNING: This will reset the database!")
        confirm = input("Type 'RESET' to confirm: ")
        if confirm != 'RESET':
            print("Aborted.")
            db.close()
            return
        
        # Delete and recreate
        db_path = db.config.db_path
        db.close()
        
        for ext in ['', '-shm', '-wal']:
            p = Path(str(db_path) + ext)
            if p.exists():
                p.unlink()
                print(f"  Deleted: {p.name}")
        
        # Reinitialize
        db = DatabaseManager()
    
    # Initialize schema (idempotent)
    print("🔧 Initializing database schema...")
    result = db.initialize()
    if result.is_err():
        print(f"  ❌ Error: {result.error}")
        db.close()
        sys.exit(1)
    print(f"  ✅ Schema ready at: {db.config.db_path}")
    
    # Sync phase locks from YAML
    print()
    print("🔄 Syncing phase locks from cortex-master.yaml...")
    phase_tracker = load_phase_tracker()
    if phase_tracker:
        stats = sync_phase_locks(db, phase_tracker)
        print(f"  ✅ Phases synced: {stats['inserted']} new, {stats['updated']} updated, {stats['unchanged']} unchanged")
    else:
        print("  ⚠️  No phase_tracker found in cortex-master.yaml")
    
    # Populate AC index (only if not sync-only)
    if not args.sync:
        print()
        print("📝 Populating AC index...")
        populator = ACPopulator(db)
        result = populator.populate()
        
        if result.is_ok():
            stats = result.unwrap()
            print(f"  ✅ ACs populated: {stats['inserted']} new, {stats['skipped']} existing")
            if stats['errors']:
                print(f"  ⚠️  Errors: {len(stats['errors'])}")
        else:
            print(f"  ❌ Error: {result.error}")
    
    # Show final status
    print()
    print("📊 Final Status")
    print("-" * 40)
    status = get_database_status(db)
    print(f"  Audit Logs: {status.get('audit_log_count', 0)} entries")
    print(f"  AC Index: {status.get('ac_index_count', 0)} entries")
    locked_count = sum(1 for v in status.get('phase_locks', {}).values() if v)
    total_phases = len(status.get('phase_locks', {}))
    print(f"  Phase Locks: {locked_count}/{total_phases} locked")
    
    db.close()
    
    print()
    print("=" * 60)
    print("✅ Database initialization complete!")
    print()
    print("Next steps:")
    print("  - Run tests: pytest")
    print("  - Check status: python scripts/init_db.py --status")
    print("=" * 60)


if __name__ == "__main__":
    main()
