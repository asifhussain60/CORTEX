"""
Analytics Database Initialization Script

Initializes analytics databases for CORTEX feedback system:
- Creates schema in all per-app databases
- Creates aggregate database
- Validates schema integrity
- Generates initialization report

Usage:
    python initialize_analytics_db.py [--app-name AppName] [--recreate]

Author: Asif Hussain
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directories to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir.parent.parent.parent))

from analytics.analytics_db_manager import AnalyticsDBManager


def initialize_databases(
    analytics_root: Path, 
    app_name: str = None, 
    recreate: bool = False
) -> dict:
    """
    Initialize analytics databases.
    
    Args:
        analytics_root: Root analytics directory
        app_name: Specific app to initialize, or None for all
        recreate: If True, drop and recreate existing databases
    
    Returns:
        Initialization report dictionary
    """
    print("=" * 60)
    print("CORTEX ANALYTICS DATABASE INITIALIZATION")
    print("=" * 60)
    
    db_manager = AnalyticsDBManager(analytics_root)
    
    report = {
        'started_at': datetime.now().isoformat(),
        'analytics_root': str(analytics_root),
        'databases_initialized': [],
        'errors': []
    }
    
    try:
        if app_name:
            # Initialize specific app database
            print(f"\nInitializing database for application: {app_name}")
            
            if recreate:
                app_db_path = analytics_root / "per-app" / app_name / "metrics.db"
                if app_db_path.exists():
                    app_db_path.unlink()
                    print(f"  ✓ Dropped existing database")
            
            with db_manager.get_connection(app_name=app_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                
                print(f"  ✓ Database initialized with {table_count} tables")
                report['databases_initialized'].append({
                    'app_name': app_name,
                    'table_count': table_count,
                    'type': 'per-app'
                })
        
        else:
            # Initialize all app databases found in per-app directory
            per_app_dir = analytics_root / "per-app"
            
            if per_app_dir.exists():
                app_dirs = [d for d in per_app_dir.iterdir() if d.is_dir()]
                print(f"\nFound {len(app_dirs)} application directories")
                
                for app_dir in app_dirs:
                    app = app_dir.name
                    print(f"\n  Initializing: {app}")
                    
                    if recreate:
                        app_db_path = app_dir / "metrics.db"
                        if app_db_path.exists():
                            app_db_path.unlink()
                            print(f"    ✓ Dropped existing database")
                    
                    with db_manager.get_connection(app_name=app) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                        table_count = cursor.fetchone()[0]
                        
                        print(f"    ✓ Database initialized with {table_count} tables")
                        report['databases_initialized'].append({
                            'app_name': app,
                            'table_count': table_count,
                            'type': 'per-app'
                        })
            else:
                print("\n  No per-app directories found. Skipping per-app initialization.")
        
        # Initialize aggregate database
        print("\nInitializing aggregate database...")
        
        if recreate:
            aggregate_db_path = analytics_root / "aggregate" / "cross-app-metrics.db"
            if aggregate_db_path.exists():
                aggregate_db_path.unlink()
                print("  ✓ Dropped existing aggregate database")
        
        with db_manager.get_connection(aggregate=True) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            print(f"  ✓ Aggregate database initialized with {table_count} tables")
            report['databases_initialized'].append({
                'app_name': 'AGGREGATE',
                'table_count': table_count,
                'type': 'aggregate'
            })
        
        report['completed_at'] = datetime.now().isoformat()
        report['success'] = True
        
        print("\n" + "=" * 60)
        print(f"✅ INITIALIZATION COMPLETE")
        print(f"   Databases initialized: {len(report['databases_initialized'])}")
        print("=" * 60)
        
        return report
    
    except Exception as e:
        print(f"\n❌ INITIALIZATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        
        report['completed_at'] = datetime.now().isoformat()
        report['success'] = False
        report['errors'].append(str(e))
        
        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Initialize CORTEX analytics databases"
    )
    parser.add_argument(
        '--app-name',
        type=str,
        help='Specific application to initialize (optional)'
    )
    parser.add_argument(
        '--recreate',
        action='store_true',
        help='Drop and recreate existing databases'
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
    
    # Initialize databases
    report = initialize_databases(
        analytics_root=analytics_root,
        app_name=args.app_name,
        recreate=args.recreate
    )
    
    # Save report
    report_file = analytics_root / "initialization-report.json"
    import json
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Initialization report saved: {report_file}")
    
    sys.exit(0 if report['success'] else 1)


if __name__ == "__main__":
    main()
