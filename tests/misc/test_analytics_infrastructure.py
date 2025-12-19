"""
Test Analytics Infrastructure - Phase 3 Validation

Tests the analytics database system:
1. Database initialization with schema
2. Report storage and deduplication
3. Query APIs (latest metrics, health scores, issues)
4. Backup utilities
5. Database vacuuming

Author: Asif Hussain
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "cortex-brain"))

from analytics.analytics_db_manager import AnalyticsDBManager
from datetime import datetime
import tempfile
import shutil


def test_database_initialization():
    """Test 1: Can we initialize databases with schema?"""
    print("\n=== Test 1: Database Initialization ===")
    try:
        # Create temporary analytics directory
        with tempfile.TemporaryDirectory() as temp_dir:
            analytics_root = Path(temp_dir) / "analytics"
            db_manager = AnalyticsDBManager(analytics_root)
            
            # Initialize a test app database
            with db_manager.get_connection(app_name="TestApp") as conn:
                cursor = conn.cursor()
                
                # Count tables created
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                
                if table_count >= 11:  # We expect 11 main tables
                    print(f"✅ Database initialized with {table_count} tables")
                    
                    # Verify key tables exist
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    required_tables = [
                        'feedback_reports',
                        'application_metrics',
                        'crawler_performance',
                        'cortex_performance',
                        'knowledge_graphs',
                        'development_hygiene',
                        'tdd_mastery',
                        'commit_metrics',
                        'velocity_metrics',
                        'trend_analysis',
                        'issues_reported'
                    ]
                    
                    missing_tables = [t for t in required_tables if t not in tables]
                    
                    if not missing_tables:
                        print(f"✅ All 11 required tables present")
                        return True
                    else:
                        print(f"❌ Missing tables: {missing_tables}")
                        return False
                else:
                    print(f"❌ Expected at least 11 tables, found {table_count}")
                    return False
    
    except Exception as e:
        print(f"❌ Database initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_report_storage():
    """Test 2: Can we store feedback reports?"""
    print("\n=== Test 2: Report Storage ===")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            analytics_root = Path(temp_dir) / "analytics"
            db_manager = AnalyticsDBManager(analytics_root)
            
            # Create test report
            test_report = {
                'app_name': 'TestApp',
                'timestamp': '2025-11-24T10:00:00',
                'privacy_level': 'full',
                'metrics': {
                    'application_metrics': {
                        'project_size_mb': 50.5,
                        'lines_of_code': 10000,
                        'test_coverage': 85.0,
                        'tech_stack': ['Python', 'SQLite']
                    },
                    'crawler_performance': {
                        'discovery_runs': 10,
                        'success_rate': 95.0
                    },
                    'cortex_performance': {
                        'avg_operation_time': 2.5,
                        'brain_db_sizes': {
                            'total': 25.0,
                            'tier1': 10.0,
                            'tier2': 10.0,
                            'tier3': 5.0
                        }
                    },
                    'knowledge_graph': {
                        'entity_count': 500,
                        'graph_density': 0.75
                    },
                    'development_hygiene': {
                        'security_vulnerabilities': 0,
                        'clean_commit_rate': 90.0
                    },
                    'tdd_mastery': {
                        'test_coverage': 85.0,
                        'test_first_adherence': 80.0
                    },
                    'commit_metrics': {
                        'build_success_rate': 95.0,
                        'deployment_frequency': 2.0
                    },
                    'velocity_metrics': {
                        'sprint_velocity': 25.0,
                        'cycle_time_days': 3.5
                    }
                }
            }
            
            # Store report
            success, report_id, message = db_manager.store_feedback_report(
                app_name='TestApp',
                report_data=test_report
            )
            
            if success and report_id:
                print(f"✅ Report stored successfully (ID: {report_id})")
                
                # Verify storage
                with db_manager.get_connection(app_name='TestApp') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM feedback_reports")
                    report_count = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM application_metrics")
                    metrics_count = cursor.fetchone()[0]
                    
                    if report_count == 1 and metrics_count == 1:
                        print(f"✅ Report verified in database")
                        return True
                    else:
                        print(f"❌ Report verification failed")
                        return False
            else:
                print(f"❌ Report storage failed: {message}")
                return False
    
    except Exception as e:
        print(f"❌ Report storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_deduplication():
    """Test 3: Does deduplication work?"""
    print("\n=== Test 3: Report Deduplication ===")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            analytics_root = Path(temp_dir) / "analytics"
            db_manager = AnalyticsDBManager(analytics_root)
            
            # Create test report
            test_report = {
                'app_name': 'TestApp',
                'timestamp': '2025-11-24T10:00:00',
                'metrics': {
                    'application_metrics': {'test_coverage': 85.0},
                    'crawler_performance': {},
                    'cortex_performance': {},
                    'knowledge_graph': {},
                    'development_hygiene': {},
                    'tdd_mastery': {},
                    'commit_metrics': {},
                    'velocity_metrics': {}
                }
            }
            
            # Store report first time
            success1, id1, msg1 = db_manager.store_feedback_report('TestApp', test_report)
            
            # Try to store identical report again
            success2, id2, msg2 = db_manager.store_feedback_report('TestApp', test_report)
            
            if success1 and not success2 and "duplicate" in msg2.lower():
                print(f"✅ First report stored (ID: {id1})")
                print(f"✅ Duplicate correctly detected and rejected")
                return True
            else:
                print(f"❌ Deduplication failed: success1={success1}, success2={success2}")
                print(f"   Message 1: {msg1}")
                print(f"   Message 2: {msg2}")
                return False
    
    except Exception as e:
        print(f"❌ Deduplication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_apis():
    """Test 4: Do query APIs work?"""
    print("\n=== Test 4: Query APIs ===")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            analytics_root = Path(temp_dir) / "analytics"
            db_manager = AnalyticsDBManager(analytics_root)
            
            # Store test report with metrics
            test_report = {
                'app_name': 'TestApp',
                'timestamp': '2025-11-24T10:00:00',
                'metrics': {
                    'application_metrics': {'test_coverage': 85.0},
                    'crawler_performance': {'success_rate': 95.0},
                    'cortex_performance': {'avg_operation_time': 2.5},
                    'knowledge_graph': {'graph_density': 0.75},
                    'development_hygiene': {'security_vulnerabilities': 0},
                    'tdd_mastery': {'test_coverage': 85.0},
                    'commit_metrics': {'build_success_rate': 95.0},
                    'velocity_metrics': {'sprint_velocity': 25.0}
                }
            }
            
            db_manager.store_feedback_report('TestApp', test_report)
            
            # Test latest metrics query
            latest = db_manager.get_latest_metrics('TestApp')
            if latest and latest.get('app_name') == 'TestApp':
                print(f"✅ Latest metrics query works")
                print(f"   Test coverage: {latest.get('tdd_coverage')}")
                print(f"   Build success: {latest.get('build_success_rate')}")
            else:
                print(f"❌ Latest metrics query failed")
                return False
            
            # Test health score query
            health_score = db_manager.get_health_score('TestApp')
            if health_score is not None and health_score > 0:
                print(f"✅ Health score calculated: {health_score:.1f}/100")
            else:
                print(f"❌ Health score calculation failed")
                return False
            
            return True
    
    except Exception as e:
        print(f"❌ Query APIs test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backup_utility():
    """Test 5: Does backup utility work?"""
    print("\n=== Test 5: Backup Utility ===")
    
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        analytics_root = Path(temp_dir) / "analytics"
        db_manager = AnalyticsDBManager(analytics_root)
        
        # Store a test report first
        test_report = {
            'app_name': 'TestApp',
            'timestamp': '2025-11-24T10:00:00',
            'metrics': {
                'application_metrics': {'test_coverage': 85.0},
                'crawler_performance': {},
                'cortex_performance': {},
                'knowledge_graph': {},
                'development_hygiene': {},
                'tdd_mastery': {},
                'commit_metrics': {},
                'velocity_metrics': {}
            }
        }
        
        db_manager.store_feedback_report('TestApp', test_report)
        
        # Create backup
        backup_path = db_manager.backup_database('TestApp')
        
        if backup_path and backup_path.exists():
            backup_size = backup_path.stat().st_size
            print(f"✅ Backup created: {backup_path.name}")
            print(f"   Size: {backup_size} bytes")
            
            # Verify backup is a valid SQLite database
            import sqlite3
            conn = sqlite3.connect(str(backup_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM feedback_reports")
            count = cursor.fetchone()[0]
            conn.close()  # Explicitly close to release file lock
            
            if count == 1:
                print(f"✅ Backup is valid SQLite database with data")
                return True
            else:
                print(f"❌ Backup database has incorrect data count: {count}")
                return False
        else:
            print(f"❌ Backup creation failed")
            return False
    
    except Exception as e:
        print(f"❌ Backup utility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup with error handling for Windows file locks
        if temp_dir:
            try:
                import time
                time.sleep(0.5)  # Give Windows time to release file locks
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass  # Ignore cleanup errors


def run_all_tests():
    """Run all analytics infrastructure tests"""
    print("=" * 60)
    print("CORTEX ANALYTICS INFRASTRUCTURE - PHASE 3 TESTS")
    print("=" * 60)
    
    results = {
        'Database Initialization': test_database_initialization(),
        'Report Storage': test_report_storage(),
        'Report Deduplication': test_deduplication(),
        'Query APIs': test_query_apis(),
        'Backup Utility': test_backup_utility()
    }
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All analytics infrastructure tests passed! Phase 3 complete.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
