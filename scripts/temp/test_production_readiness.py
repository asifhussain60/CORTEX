"""
Feedback System - Production Readiness Validation

Validates the feedback and analytics system for production deployment.
Tests core functionality without mocking complex internal methods.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "cortex-brain"))

from analytics.analytics_db_manager import AnalyticsDBManager
from analytics.real_live_data_generator import RealLiveDataGenerator
import tempfile
import json


def test_analytics_pipeline():
    """Test complete analytics pipeline: storage → query → dashboard."""
    print("\n" + "="*60)
    print("TEST 1: Analytics Pipeline")
    print("="*60)
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            analytics_root = Path(temp_dir) / "analytics"
            docs_dir = Path(temp_dir) / "docs"
            docs_dir.mkdir(parents=True)
            
            # Step 1: Store feedback reports
            print("\n[1/4] Storing feedback reports...")
            db_manager = AnalyticsDBManager(analytics_root)
            
            apps = ["WebApp", "MobileApp"]
            for i, app_name in enumerate(apps):
                report = {
                    'app_name': app_name,
                    'timestamp': f'2025-11-24T10:0{i}:00',
                    'privacy_level': 'full',
                    'metrics': {
                        'application_metrics': {'test_coverage': 80.0 + i * 10},
                        'crawler_performance': {'success_rate': 90.0 + i * 5},
                        'cortex_performance': {'avg_operation_time': 3.0 - i * 0.5},
                        'knowledge_graph': {'entity_count': 400 + i * 100},
                        'development_hygiene': {'security_vulnerabilities': i},
                        'tdd_mastery': {'test_coverage': 80.0 + i * 10},
                        'commit_metrics': {'build_success_rate': 92.0 + i * 3},
                        'velocity_metrics': {'sprint_velocity': 20.0 + i * 5}
                    }
                }
                
                success, report_id, message = db_manager.store_feedback_report(app_name, report)
                if success:
                    print(f"   ✅ {app_name}: Report stored (ID: {report_id})")
                else:
                    print(f"   ❌ {app_name}: Storage failed - {message}")
                    return False
            
            # Step 2: Query analytics
            print("\n[2/4] Querying analytics...")
            for app_name in apps:
                latest = db_manager.get_latest_metrics(app_name)
                if latest:
                    print(f"   ✅ {app_name}: Latest metrics retrieved")
                    print(f"      Coverage: {latest.get('tdd_coverage')}%")
                else:
                    print(f"   ❌ {app_name}: Query failed")
                    return False
                
                health = db_manager.get_health_score(app_name)
                if health is not None:
                    print(f"      Health: {health:.1f}/100")
                else:
                    print(f"   ❌ {app_name}: Health score calculation failed")
                    return False
            
            # Step 3: Generate dashboards
            print("\n[3/4] Generating dashboards...")
            generator = RealLiveDataGenerator(analytics_root, docs_dir)
            
            if not generator.has_data():
                print("   ❌ Data detection failed")
                return False
            
            result = generator.generate_all_dashboards()
            
            if len(result['app_dashboards']) == 2 and result['aggregate_dashboard']:
                print(f"   ✅ Generated {len(result['app_dashboards'])} app dashboards")
                print(f"   ✅ Generated aggregate dashboard")
            else:
                print(f"   ❌ Dashboard generation incomplete")
                return False
            
            # Step 4: Validate navigation
            print("\n[4/4] Validating navigation...")
            nav = generator.get_navigation_structure()
            if nav and 'Real Live Data' in nav:
                app_count = len(nav['Real Live Data']) - 1  # -1 for overview
                print(f"   ✅ Navigation structure created")
                print(f"      Apps in nav: {app_count}")
                if app_count == 2:
                    print("\n✅ PASSED: Analytics Pipeline")
                    return True
                else:
                    print(f"   ❌ Expected 2 apps in navigation, got {app_count}")
                    return False
            else:
                print("   ❌ Navigation structure creation failed")
                return False
    
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_deduplication():
    """Test SHA256 deduplication prevents duplicate reports."""
    print("\n" + "="*60)
    print("TEST 2: Database Deduplication")
    print("="*60)
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            analytics_root = Path(temp_dir) / "analytics"
            db_manager = AnalyticsDBManager(analytics_root)
            
            report = {
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
            
            # Store first time
            success1, id1, msg1 = db_manager.store_feedback_report('TestApp', report)
            print(f"\n[1] First store: {msg1}")
            
            # Try duplicate
            success2, id2, msg2 = db_manager.store_feedback_report('TestApp', report)
            print(f"[2] Second store: {msg2}")
            
            if success1 and not success2 and "duplicate" in msg2.lower():
                print("\n✅ PASSED: Deduplication works correctly")
                return True
            else:
                print(f"\n❌ FAILED: Deduplication not working")
                print(f"   success1={success1}, success2={success2}")
                return False
    
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        return False


def test_conditional_navigation():
    """Test that navigation is hidden when no data exists."""
    print("\n" + "="*60)
    print("TEST 3: Conditional Navigation")
    print("="*60)
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            analytics_root = Path(temp_dir) / "analytics"
            docs_dir = Path(temp_dir) / "docs"
            docs_dir.mkdir(parents=True)
            
            generator = RealLiveDataGenerator(analytics_root, docs_dir)
            
            # Test 1: No data
            print("\n[1] Testing with no data...")
            if not generator.has_data():
                print("   ✅ has_data() returns False")
            else:
                print("   ❌ has_data() returned True with no data")
                return False
            
            nav = generator.get_navigation_structure()
            if nav is None:
                print("   ✅ get_navigation_structure() returns None")
            else:
                print(f"   ❌ Navigation returned when it shouldn't: {nav}")
                return False
            
            # Test 2: With data
            print("\n[2] Testing with data...")
            db_manager = AnalyticsDBManager(analytics_root)
            test_report = {
                'app_name': 'TestApp',
                'timestamp': '2025-11-24T10:00:00',
                'metrics': {
                    'application_metrics': {},
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
            
            if generator.has_data():
                print("   ✅ has_data() returns True")
            else:
                print("   ❌ has_data() returned False with data")
                return False
            
            nav = generator.get_navigation_structure()
            if nav and 'Real Live Data' in nav:
                print("   ✅ get_navigation_structure() returns navigation")
                print("\n✅ PASSED: Conditional Navigation")
                return True
            else:
                print(f"   ❌ Invalid navigation structure: {nav}")
                return False
    
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_health_score_calculation():
    """Test health score calculation with different metrics."""
    print("\n" + "="*60)
    print("TEST 4: Health Score Calculation")
    print("="*60)
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            analytics_root = Path(temp_dir) / "analytics"
            db_manager = AnalyticsDBManager(analytics_root)
            
            test_cases = [
                {
                    'name': 'Perfect App',
                    'metrics': {
                        'tdd_mastery': {'test_coverage': 100.0},
                        'commit_metrics': {'build_success_rate': 100.0},
                        'crawler_performance': {'success_rate': 100.0},
                        'development_hygiene': {'security_vulnerabilities': 0},
                        'velocity_metrics': {'sprint_velocity': 50.0},
                        'knowledge_graph': {'graph_density': 1.0}
                    },
                    'expected_min': 90.0
                },
                {
                    'name': 'Good App',
                    'metrics': {
                        'tdd_mastery': {'test_coverage': 85.0},
                        'commit_metrics': {'build_success_rate': 95.0},
                        'crawler_performance': {'success_rate': 90.0},
                        'development_hygiene': {'security_vulnerabilities': 0},
                        'velocity_metrics': {'sprint_velocity': 40.0},
                        'knowledge_graph': {'graph_density': 0.8}
                    },
                    'expected_min': 75.0
                },
                {
                    'name': 'Needs Improvement',
                    'metrics': {
                        'tdd_mastery': {'test_coverage': 50.0},
                        'commit_metrics': {'build_success_rate': 70.0},
                        'crawler_performance': {'success_rate': 60.0},
                        'development_hygiene': {'security_vulnerabilities': 5},
                        'velocity_metrics': {'sprint_velocity': 15.0},
                        'knowledge_graph': {'graph_density': 0.5}
                    },
                    'expected_min': 40.0
                }
            ]
            
            print()
            for test_case in test_cases:
                report = {
                    'app_name': test_case['name'],
                    'timestamp': '2025-11-24T10:00:00',
                    'metrics': {
                        'application_metrics': {},
                        'crawler_performance': test_case['metrics'].get('crawler_performance', {}),
                        'cortex_performance': {},
                        'knowledge_graph': test_case['metrics'].get('knowledge_graph', {}),
                        'development_hygiene': test_case['metrics'].get('development_hygiene', {}),
                        'tdd_mastery': test_case['metrics'].get('tdd_mastery', {}),
                        'commit_metrics': test_case['metrics'].get('commit_metrics', {}),
                        'velocity_metrics': test_case['metrics'].get('velocity_metrics', {})
                    }
                }
                
                db_manager.store_feedback_report(test_case['name'], report)
                health = db_manager.get_health_score(test_case['name'])
                
                if health is not None and health >= test_case['expected_min']:
                    print(f"   ✅ {test_case['name']}: {health:.1f}/100 (>= {test_case['expected_min']})")
                else:
                    print(f"   ❌ {test_case['name']}: {health}/100 (expected >= {test_case['expected_min']})")
                    return False
            
            print("\n✅ PASSED: Health Score Calculation")
            return True
    
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run production readiness validation."""
    print("="*60)
    print("FEEDBACK SYSTEM - PRODUCTION READINESS VALIDATION")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Analytics Pipeline", test_analytics_pipeline()))
    results.append(("Database Deduplication", test_database_deduplication()))
    results.append(("Conditional Navigation", test_conditional_navigation()))
    results.append(("Health Score Calculation", test_health_score_calculation()))
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print()
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    pass_rate = (passed / total * 100) if total > 0 else 0
    print(f"\nPass Rate: {passed}/{total} ({pass_rate:.1f}%)")
    
    if passed == total:
        print("\n🎉 System is production-ready!")
        print("\nValidated:")
        print("  • Analytics pipeline (storage → query → dashboards)")
        print("  • SHA256 deduplication")
        print("  • Conditional navigation (hidden when no data)")
        print("  • Health score calculation")
        return True
    else:
        print(f"\n⚠️  {total - passed} validation(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
