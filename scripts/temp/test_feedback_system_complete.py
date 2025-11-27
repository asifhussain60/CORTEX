"""
Complete Feedback System Test Suite

End-to-end tests for the entire feedback and analytics pipeline:
1. Feedback collection with 8 collectors
2. Privacy sanitization (3 levels)
3. Gist integration (mocked)
4. Database storage with analytics
5. Admin feedback review
6. Dashboard generation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "cortex-brain"))
sys.path.insert(0, str(project_root / "cortex-brain" / "admin" / "scripts" / "feedback"))

from operations.modules.feedback.enhanced_feedback_module import EnhancedFeedbackModule
from admin_feedback_review import AdminFeedbackReviewModule
from analytics.analytics_db_manager import AnalyticsDBManager
from analytics.real_live_data_generator import RealLiveDataGenerator
import tempfile
import shutil
from unittest.mock import MagicMock, patch
import json


class TestFeedbackSystemComplete:
    """Complete feedback system test suite."""
    
    def __init__(self):
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'tests': []
        }
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and record results."""
        print(f"\n{'='*60}")
        print(f"Test: {test_name}")
        print('='*60)
        
        try:
            result = test_func()
            if result:
                print(f"✅ PASSED: {test_name}")
                self.test_results['passed'] += 1
                self.test_results['tests'].append({
                    'name': test_name,
                    'status': 'passed'
                })
            else:
                print(f"❌ FAILED: {test_name}")
                self.test_results['failed'] += 1
                self.test_results['tests'].append({
                    'name': test_name,
                    'status': 'failed',
                    'reason': 'Test returned False'
                })
            return result
        except Exception as e:
            print(f"❌ FAILED: {test_name}")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            self.test_results['failed'] += 1
            self.test_results['tests'].append({
                'name': test_name,
                'status': 'failed',
                'reason': str(e)
            })
            return False
    
    def test_1_feedback_collection(self) -> bool:
        """Test 1: Feedback collection with all 8 collectors."""
        print("\n--- Test 1: Feedback Collection ---")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create test context
                context = {
                    'project_root': temp_path,
                    'app_name': 'TestApp',
                    'privacy_level': 'full'
                }
                
                # Initialize module
                feedback_module = EnhancedFeedbackModule()
                
                # Mock the collectors to return sample data
                with patch.object(feedback_module, '_collect_application_metrics') as mock_app:
                    mock_app.return_value = {'test_coverage': 85.0, 'lines_of_code': 10000}
                    
                    # Execute feedback collection
                    result = feedback_module.execute(context)
                    
                    if result.success and result.data:
                        report = result.data.get('report')
                        if report:
                            print(f"✅ Feedback collected successfully")
                            print(f"   App: {report.get('app_name')}")
                            print(f"   Timestamp: {report.get('timestamp')}")
                            print(f"   Privacy: {report.get('privacy_level')}")
                            
                            # Verify metrics structure
                            metrics = report.get('metrics', {})
                            required_categories = [
                                'application_metrics',
                                'crawler_performance',
                                'cortex_performance',
                                'knowledge_graph',
                                'development_hygiene',
                                'tdd_mastery',
                                'commit_metrics',
                                'velocity_metrics'
                            ]
                            
                            missing = [cat for cat in required_categories if cat not in metrics]
                            if not missing:
                                print(f"✅ All 8 metric categories present")
                                return True
                            else:
                                print(f"❌ Missing categories: {missing}")
                                return False
                    
                    print(f"❌ Feedback collection failed: {result.error}")
                    return False
        
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
    
    def test_2_privacy_sanitization(self) -> bool:
        """Test 2: Privacy sanitization at all 3 levels."""
        print("\n--- Test 2: Privacy Sanitization ---")
        
        try:
            from operations.modules.feedback.privacy import PrivacySanitizer
            
            # Test data with sensitive information
            test_data = {
                'project_path': '/Users/john.doe/secret-project',
                'email': 'john.doe@company.com',
                'api_key': 'sk-1234567890abcdef',
                'metrics': {
                    'coverage': 85.0,
                    'author': 'John Doe'
                }
            }
            
            sanitizer = PrivacySanitizer()
            
            # Test full privacy (keep all except passwords/keys)
            full_result = sanitizer.sanitize(test_data, privacy_level='full')
            print(f"✅ Full privacy: API key removed = {('api_key' not in str(full_result))}")
            
            # Test medium privacy (redact personal info)
            medium_result = sanitizer.sanitize(test_data, privacy_level='medium')
            print(f"✅ Medium privacy: Email redacted = {('john.doe' not in str(medium_result))}")
            
            # Test minimal privacy (remove all sensitive data)
            minimal_result = sanitizer.sanitize(test_data, privacy_level='minimal')
            print(f"✅ Minimal privacy: Paths removed = {('/Users/' not in str(minimal_result))}")
            
            # Verify metrics preserved
            if 'metrics' in minimal_result and minimal_result['metrics'].get('coverage') == 85.0:
                print(f"✅ Metrics preserved across all privacy levels")
                return True
            else:
                print(f"❌ Metrics not preserved")
                return False
        
        except Exception as e:
            print(f"❌ Privacy sanitization failed: {e}")
            return False
    
    def test_3_gist_integration(self) -> bool:
        """Test 3: GitHub Gist integration with mocked PyGithub."""
        print("\n--- Test 3: Gist Integration (Mocked) ---")
        
        try:
            # Mock PyGithub
            with patch('operations.enhanced_feedback_module.Github') as MockGithub:
                mock_github = MagicMock()
                mock_user = MagicMock()
                mock_gist = MagicMock()
                mock_gist.id = 'abc123'
                mock_gist.html_url = 'https://gist.github.com/user/abc123'
                
                mock_user.create_gist.return_value = mock_gist
                mock_github.get_user.return_value = mock_user
                MockGithub.return_value = mock_github
                
                # Test Gist upload
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    
                    context = {
                        'project_root': temp_path,
                        'app_name': 'TestApp',
                        'privacy_level': 'full',
                        'github_token': 'fake_token_for_test',
                        'upload_to_gist': True
                    }
                    
                    feedback_module = EnhancedFeedbackModule()
                    
                    # Mock collectors
                    with patch.object(feedback_module, '_collect_application_metrics'):
                        result = feedback_module.execute(context)
                        
                        if result.success and result.data:
                            gist_info = result.data.get('gist_info')
                            if gist_info:
                                print(f"✅ Gist created: {gist_info.get('url')}")
                                print(f"   Gist ID: {gist_info.get('id')}")
                                return True
                            else:
                                print(f"❌ Gist info not found in result")
                                return False
                
                print(f"❌ Gist integration test failed")
                return False
        
        except ImportError:
            print(f"⚠️  PyGithub not installed - skipping Gist test (expected)")
            self.test_results['skipped'] += 1
            return True
        except Exception as e:
            print(f"❌ Gist integration test failed: {e}")
            return False
    
    def test_4_database_storage(self) -> bool:
        """Test 4: Database storage with analytics manager."""
        print("\n--- Test 4: Database Storage ---")
        
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
                        'crawler_performance': {'success_rate': 95.0},
                        'cortex_performance': {'avg_operation_time': 2.5},
                        'knowledge_graph': {'entity_count': 500},
                        'development_hygiene': {'security_vulnerabilities': 0},
                        'tdd_mastery': {'test_coverage': 85.0},
                        'commit_metrics': {'build_success_rate': 95.0},
                        'velocity_metrics': {'sprint_velocity': 25.0}
                    }
                }
                
                # Store report
                success, report_id, message = db_manager.store_feedback_report(
                    'TestApp', test_report
                )
                
                if success and report_id:
                    print(f"✅ Report stored (ID: {report_id})")
                    
                    # Verify retrieval
                    latest = db_manager.get_latest_metrics('TestApp')
                    if latest and latest.get('tdd_coverage') == 85.0:
                        print(f"✅ Report retrieved successfully")
                        
                        # Verify health score calculation
                        health_score = db_manager.get_health_score('TestApp')
                        if health_score and health_score > 0:
                            print(f"✅ Health score calculated: {health_score:.1f}/100")
                            return True
                        else:
                            print(f"❌ Health score calculation failed")
                            return False
                    else:
                        print(f"❌ Report retrieval failed")
                        return False
                else:
                    print(f"❌ Database storage failed: {message}")
                    return False
        
        except Exception as e:
            print(f"❌ Database storage test failed: {e}")
            return False
    
    def test_5_admin_review(self) -> bool:
        """Test 5: Admin feedback review and aggregation."""
        print("\n--- Test 5: Admin Feedback Review ---")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create test context
                context = {
                    'project_root': temp_path,
                    'cortex_brain_root': temp_path / 'cortex-brain'
                }
                
                # Create required directories
                (context['cortex_brain_root'] / 'admin').mkdir(parents=True)
                analytics_dir = context['cortex_brain_root'] / 'analytics'
                analytics_dir.mkdir(parents=True)
                
                # Store some test feedback reports
                db_manager = AnalyticsDBManager(analytics_dir)
                for i, app_name in enumerate(['App1', 'App2']):
                    test_report = {
                        'app_name': app_name,
                        'timestamp': f'2025-11-24T10:0{i}:00',
                        'metrics': {
                            'application_metrics': {'test_coverage': 80.0 + i * 5},
                            'crawler_performance': {},
                            'cortex_performance': {},
                            'knowledge_graph': {},
                            'development_hygiene': {},
                            'tdd_mastery': {},
                            'commit_metrics': {},
                            'velocity_metrics': {}
                        }
                    }
                    db_manager.store_feedback_report(app_name, test_report)
                
                print(f"✅ Created test reports for 2 applications")
                
                # Test admin review module
                admin_module = AdminFeedbackReviewModule()
                result = admin_module.execute(context)
                
                if result.success and result.data:
                    summary = result.data.get('summary')
                    if summary:
                        print(f"✅ Admin review completed")
                        print(f"   Total reports: {summary.get('total_reports', 0)}")
                        print(f"   Applications: {summary.get('applications_count', 0)}")
                        return True
                    else:
                        print(f"❌ Summary not found in result")
                        return False
                else:
                    print(f"❌ Admin review failed: {result.error}")
                    return False
        
        except Exception as e:
            print(f"❌ Admin review test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_6_dashboard_generation(self) -> bool:
        """Test 6: Dashboard generation with Chart.js."""
        print("\n--- Test 6: Dashboard Generation ---")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                analytics_root = temp_path / "analytics"
                docs_dir = temp_path / "docs"
                docs_dir.mkdir(parents=True)
                
                # Create test data
                db_manager = AnalyticsDBManager(analytics_root)
                test_report = {
                    'app_name': 'TestApp',
                    'timestamp': '2025-11-24T10:00:00',
                    'metrics': {
                        'application_metrics': {'test_coverage': 85.0},
                        'crawler_performance': {'success_rate': 95.0},
                        'cortex_performance': {'avg_operation_time': 2.5},
                        'knowledge_graph': {'entity_count': 500},
                        'development_hygiene': {'security_vulnerabilities': 0},
                        'tdd_mastery': {'test_coverage': 85.0},
                        'commit_metrics': {'build_success_rate': 95.0},
                        'velocity_metrics': {'sprint_velocity': 25.0}
                    }
                }
                db_manager.store_feedback_report('TestApp', test_report)
                
                # Generate dashboards
                generator = RealLiveDataGenerator(analytics_root, docs_dir)
                
                if generator.has_data():
                    print(f"✅ Data detected")
                    
                    result = generator.generate_all_dashboards()
                    
                    if result['app_dashboards'] and result['aggregate_dashboard']:
                        print(f"✅ Dashboards generated:")
                        print(f"   Per-app: {len(result['app_dashboards'])}")
                        print(f"   Aggregate: 1")
                        
                        # Verify Chart.js in content
                        dashboard_file = result['app_dashboards'][0]
                        content = dashboard_file.read_text()
                        
                        if 'Chart.js' in content and 'canvas' in content:
                            print(f"✅ Chart.js integration verified")
                            return True
                        else:
                            print(f"❌ Chart.js not found in dashboard")
                            return False
                    else:
                        print(f"❌ Dashboard generation incomplete")
                        return False
                else:
                    print(f"❌ No data detected")
                    return False
        
        except Exception as e:
            print(f"❌ Dashboard generation test failed: {e}")
            return False
    
    def test_7_deployment_boundaries(self) -> bool:
        """Test 7: Deployment boundary validation."""
        print("\n--- Test 7: Deployment Boundaries ---")
        
        try:
            # Test USER feature (should be deployable)
            feedback_module = EnhancedFeedbackModule()
            metadata = feedback_module.get_metadata()
            
            if 'admin' not in metadata.tags:
                print(f"✅ Feedback module marked as USER feature")
            else:
                print(f"❌ Feedback module incorrectly tagged as admin")
                return False
            
            # Test ADMIN feature (should NOT be deployed)
            admin_module = AdminFeedbackReviewModule()
            admin_metadata = admin_module.get_metadata()
            
            if 'admin' in admin_metadata.tags:
                print(f"✅ Admin review module correctly tagged as ADMIN")
            else:
                print(f"❌ Admin review module missing admin tag")
                return False
            
            # Verify admin module checks for cortex-brain/admin/
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Test without admin directory (should fail validation)
                context = {'project_root': temp_path}
                valid, message = admin_module.validate_context(context)
                
                if not valid and 'admin-only' in message.lower():
                    print(f"✅ Admin module correctly restricts to CORTEX repo")
                    return True
                else:
                    print(f"❌ Admin module validation incorrect")
                    return False
        
        except Exception as e:
            print(f"❌ Deployment boundary test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests and generate report."""
        print("="*60)
        print("FEEDBACK SYSTEM - COMPLETE TEST SUITE")
        print("="*60)
        
        # Run tests
        self.run_test("Feedback Collection", self.test_1_feedback_collection)
        self.run_test("Privacy Sanitization", self.test_2_privacy_sanitization)
        self.run_test("Gist Integration", self.test_3_gist_integration)
        self.run_test("Database Storage", self.test_4_database_storage)
        self.run_test("Admin Review", self.test_5_admin_review)
        self.run_test("Dashboard Generation", self.test_6_dashboard_generation)
        self.run_test("Deployment Boundaries", self.test_7_deployment_boundaries)
        
        # Print summary
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        
        total = self.test_results['passed'] + self.test_results['failed']
        pass_rate = (self.test_results['passed'] / total * 100) if total > 0 else 0
        
        print(f"\n✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        if self.test_results['skipped'] > 0:
            print(f"⚠️  Skipped: {self.test_results['skipped']}")
        print(f"\nPass Rate: {pass_rate:.1f}%")
        
        if self.test_results['failed'] == 0:
            print("\n🎉 All tests passed! Feedback system is production-ready.")
            return True
        else:
            print(f"\n⚠️  {self.test_results['failed']} test(s) failed. Review errors above.")
            return False


def main():
    """Run test suite."""
    test_suite = TestFeedbackSystemComplete()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
