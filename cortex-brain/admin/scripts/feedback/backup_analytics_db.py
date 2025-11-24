"""
Analytics Database Backup Utility

Creates backups of CORTEX analytics databases:
- Per-application databases
- Aggregate database
- Supports full and incremental backups
- Automatic retention management

Usage:
    python backup_analytics_db.py [--app-name AppName] [--retention-days 90]

Author: Asif Hussain
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import shutil

# Add parent directories to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir.parent.parent.parent))

from analytics.analytics_db_manager import AnalyticsDBManager


def backup_databases(
    analytics_root: Path,
    app_name: str = None,
    retention_days: int = 90
) -> dict:
    """
    Backup analytics databases.
    
    Args:
        analytics_root: Root analytics directory
        app_name: Specific app to backup, or None for all
        retention_days: Number of days to retain backups
    
    Returns:
        Backup report dictionary
    """
    print("=" * 60)
    print("CORTEX ANALYTICS DATABASE BACKUP")
    print("=" * 60)
    
    db_manager = AnalyticsDBManager(analytics_root)
    
    report = {
        'started_at': datetime.now().isoformat(),
        'analytics_root': str(analytics_root),
        'backups_created': [],
        'backups_cleaned': 0,
        'errors': []
    }
    
    try:
        if app_name:
            # Backup specific app
            print(f"\nBacking up database for: {app_name}")
            
            backup_path = db_manager.backup_database(app_name)
            
            if backup_path:
                backup_size = backup_path.stat().st_size / (1024 * 1024)  # MB
                print(f"  ✓ Backup created: {backup_path.name}")
                print(f"  ✓ Size: {backup_size:.2f} MB")
                
                report['backups_created'].append({
                    'app_name': app_name,
                    'backup_path': str(backup_path),
                    'size_mb': round(backup_size, 2)
                })
            else:
                print(f"  ❌ Backup failed for {app_name}")
                report['errors'].append(f"Backup failed: {app_name}")
        
        else:
            # Backup all app databases
            per_app_dir = analytics_root / "per-app"
            
            if per_app_dir.exists():
                app_dirs = [d for d in per_app_dir.iterdir() if d.is_dir()]
                print(f"\nFound {len(app_dirs)} application databases")
                
                for app_dir in app_dirs:
                    app = app_dir.name
                    print(f"\n  Backing up: {app}")
                    
                    backup_path = db_manager.backup_database(app)
                    
                    if backup_path:
                        backup_size = backup_path.stat().st_size / (1024 * 1024)  # MB
                        print(f"    ✓ Backup created: {backup_path.name}")
                        print(f"    ✓ Size: {backup_size:.2f} MB")
                        
                        report['backups_created'].append({
                            'app_name': app,
                            'backup_path': str(backup_path),
                            'size_mb': round(backup_size, 2)
                        })
                    else:
                        print(f"    ❌ Backup failed")
                        report['errors'].append(f"Backup failed: {app}")
            
            # Backup aggregate database
            print("\n  Backing up aggregate database...")
            aggregate_db = analytics_root / "aggregate" / "cross-app-metrics.db"
            
            if aggregate_db.exists():
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                backup_dir = analytics_root / "backups" / "aggregate"
                backup_dir.mkdir(parents=True, exist_ok=True)
                
                backup_path = backup_dir / f"cross-app-metrics-backup-{timestamp}.db"
                shutil.copy2(aggregate_db, backup_path)
                
                backup_size = backup_path.stat().st_size / (1024 * 1024)  # MB
                print(f"    ✓ Backup created: {backup_path.name}")
                print(f"    ✓ Size: {backup_size:.2f} MB")
                
                report['backups_created'].append({
                    'app_name': 'AGGREGATE',
                    'backup_path': str(backup_path),
                    'size_mb': round(backup_size, 2)
                })
        
        # Clean old backups based on retention
        if retention_days > 0:
            print(f"\nCleaning backups older than {retention_days} days...")
            cleaned_count = cleanup_old_backups(analytics_root, retention_days)
            report['backups_cleaned'] = cleaned_count
            print(f"  ✓ Cleaned {cleaned_count} old backup(s)")
        
        report['completed_at'] = datetime.now().isoformat()
        report['success'] = True
        
        print("\n" + "=" * 60)
        print(f"✅ BACKUP COMPLETE")
        print(f"   Backups created: {len(report['backups_created'])}")
        print(f"   Old backups cleaned: {report['backups_cleaned']}")
        print("=" * 60)
        
        return report
    
    except Exception as e:
        print(f"\n❌ BACKUP FAILED: {e}")
        import traceback
        traceback.print_exc()
        
        report['completed_at'] = datetime.now().isoformat()
        report['success'] = False
        report['errors'].append(str(e))
        
        return report


def cleanup_old_backups(analytics_root: Path, retention_days: int) -> int:
    """
    Clean up backups older than retention period.
    
    Returns:
        Number of backups deleted
    """
    backup_dir = analytics_root / "backups"
    if not backup_dir.exists():
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    deleted_count = 0
    
    # Recursively find all backup files
    for backup_file in backup_dir.rglob("*-backup-*.db"):
        if backup_file.is_file():
            file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            
            if file_mtime < cutoff_date:
                try:
                    backup_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"  ⚠️  Failed to delete {backup_file.name}: {e}")
    
    return deleted_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Backup CORTEX analytics databases"
    )
    parser.add_argument(
        '--app-name',
        type=str,
        help='Specific application to backup (optional)'
    )
    parser.add_argument(
        '--retention-days',
        type=int,
        default=90,
        help='Number of days to retain backups (default: 90, 0 to skip cleanup)'
    )
    parser.add_argument(
        '--analytics-root',
        type=str,
        default='cortex-brain/analytics',
        help='Analytics root directory (default: cortex-brain/analytics)'
    )
    
    args = parser.parse_args()
    
    # Resolve analytics root
    if Path(args.analytics_root).is_absolute():
        analytics_root = Path(args.analytics_root)
    else:
        # Relative to project root
        project_root = Path(__file__).parent.parent.parent.parent
        analytics_root = project_root / args.analytics_root
    
    # Backup databases
    report = backup_databases(
        analytics_root=analytics_root,
        app_name=args.app_name,
        retention_days=args.retention_days
    )
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_file = analytics_root / "backups" / f"backup-report-{timestamp}.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Backup report saved: {report_file}")
    
    sys.exit(0 if report['success'] else 1)


if __name__ == "__main__":
    main()
