"""
Test Real Live Data Generation with Sample Data

Creates sample feedback reports and tests dashboard generation.

Author: Asif Hussain
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "cortex-brain"))

from analytics.analytics_db_manager import AnalyticsDBManager
from analytics.real_live_data_generator import RealLiveDataGenerator
import shutil


def create_sample_data():
    """Create sample feedback reports for testing."""
    print("\n=== Creating Sample Data ===")
    
    analytics_root = Path("cortex-brain/analytics")
    db_manager = AnalyticsDBManager(analytics_root)
    
    # Sample reports for two applications
    apps = ["MyWebApp", "MobileApp"]
    
    for app_name in apps:
        report = {
            'app_name': app_name,
            'timestamp': '2025-11-24T10:00:00',
            'privacy_level': 'full',
            'metrics': {
                'application_metrics': {
                    'project_size_mb': 75.5 if app_name == "MyWebApp" else 45.2,
                    'lines_of_code': 15000 if app_name == "MyWebApp" else 8500,
                    'test_coverage': 88.5 if app_name == "MyWebApp" else 72.0,
                    'tech_stack': ['Python', 'React', 'PostgreSQL'] if app_name == "MyWebApp" else ['React Native', 'Firebase']
                },
                'crawler_performance': {
                    'discovery_runs': 15,
                    'success_rate': 96.5 if app_name == "MyWebApp" else 89.0
                },
                'cortex_performance': {
                    'avg_operation_time': 2.1 if app_name == "MyWebApp" else 3.5,
                    'brain_db_sizes': {
                        'total': 30.5 if app_name == "MyWebApp" else 18.2,
                        'tier1': 12.0 if app_name == "MyWebApp" else 7.0,
                        'tier2': 12.0 if app_name == "MyWebApp" else 7.2,
                        'tier3': 6.5 if app_name == "MyWebApp" else 4.0
                    }
                },
                'knowledge_graph': {
                    'entity_count': 650 if app_name == "MyWebApp" else 320,
                    'graph_density': 0.82 if app_name == "MyWebApp" else 0.68
                },
                'development_hygiene': {
                    'security_vulnerabilities': 0 if app_name == "MyWebApp" else 2,
                    'clean_commit_rate': 92.5 if app_name == "MyWebApp" else 85.0
                },
                'tdd_mastery': {
                    'test_coverage': 88.5 if app_name == "MyWebApp" else 72.0,
                    'test_first_adherence': 85.0 if app_name == "MyWebApp" else 65.0
                },
                'commit_metrics': {
                    'build_success_rate': 97.0 if app_name == "MyWebApp" else 91.0,
                    'deployment_frequency': 3.5 if app_name == "MyWebApp" else 2.0
                },
                'velocity_metrics': {
                    'sprint_velocity': 32.0 if app_name == "MyWebApp" else 22.0,
                    'cycle_time_days': 2.8 if app_name == "MyWebApp" else 4.5
                }
            }
        }
        
        success, report_id, message = db_manager.store_feedback_report(app_name, report)
        if success:
            print(f"✅ Created sample data for {app_name} (ID: {report_id})")
        else:
            print(f"❌ Failed to create data for {app_name}: {message}")
    
    return apps


def test_dashboard_generation():
    """Test dashboard generation with sample data."""
    print("\n=== Testing Dashboard Generation ===")
    
    analytics_root = Path("cortex-brain/analytics")
    docs_output_dir = Path("docs")
    
    generator = RealLiveDataGenerator(analytics_root, docs_output_dir)
    
    # Check data exists
    has_data = generator.has_data()
    print(f"\nData exists: {has_data}")
    
    if not has_data:
        print("❌ No data found after sample creation")
        return False
    
    # Get applications
    apps = generator.get_applications()
    print(f"Applications: {apps}")
    
    # Generate dashboards
    print("\nGenerating dashboards...")
    result = generator.generate_all_dashboards()
    
    print(f"\n✅ Generated {len(result['app_dashboards'])} app dashboards:")
    for path in result['app_dashboards']:
        print(f"   - {path.name}")
    
    if result['aggregate_dashboard']:
        print(f"✅ Generated aggregate dashboard: {result['aggregate_dashboard'].name}")
    
    # Get navigation structure
    nav = generator.get_navigation_structure()
    if nav:
        print("\n✅ Navigation structure created:")
        import json
        print(json.dumps(nav, indent=2))
    
    # Verify files exist
    print("\n=== Verifying Generated Files ===")
    for path in result['app_dashboards']:
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {path.name} ({size} bytes)")
        else:
            print(f"❌ {path.name} not found")
    
    if result['aggregate_dashboard'] and result['aggregate_dashboard'].exists():
        size = result['aggregate_dashboard'].stat().st_size
        print(f"✅ {result['aggregate_dashboard'].name} ({size} bytes)")
    
    return True


def cleanup_test_data():
    """Clean up test analytics data."""
    print("\n=== Cleanup ===")
    
    analytics_root = Path("cortex-brain/analytics")
    
    # Remove per-app databases
    per_app_dir = analytics_root / "per-app"
    if per_app_dir.exists():
        for app_dir in per_app_dir.iterdir():
            if app_dir.is_dir() and app_dir.name in ["MyWebApp", "MobileApp"]:
                shutil.rmtree(app_dir)
                print(f"✅ Removed test data for {app_dir.name}")
    
    # Remove generated dashboards
    docs_dir = Path("docs/real-live-data")
    if docs_dir.exists():
        for dashboard_file in docs_dir.glob("*.md"):
            if dashboard_file.name in ["mywebapp.md", "mobileapp.md", "overview.md"]:
                dashboard_file.unlink()
                print(f"✅ Removed dashboard: {dashboard_file.name}")


def main():
    """Run complete test."""
    print("=" * 60)
    print("REAL LIVE DATA - INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Create sample data
        apps = create_sample_data()
        
        # Test dashboard generation
        success = test_dashboard_generation()
        
        if success:
            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED")
            print("=" * 60)
            print("\nReal Live Data dashboards generated successfully!")
            print("View them at: docs/real-live-data/")
            print("\nTo see in MkDocs, run: mkdocs serve")
        else:
            print("\n❌ TESTS FAILED")
        
        # Cleanup
        cleanup_input = input("\nCleanup test data? (y/n): ")
        if cleanup_input.lower() == 'y':
            cleanup_test_data()
        
        return success
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
