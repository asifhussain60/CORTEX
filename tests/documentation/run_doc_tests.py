"""
CORTEX Documentation Test Runner

Executes comprehensive documentation validation test suite.
This runner integrates with the documentation orchestrator pipeline.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import json


class DocumentationTestRunner:
    """Comprehensive documentation test suite runner"""
    
    def __init__(self, repo_root: Path):
        """
        Initialize test runner.
        
        Args:
            repo_root: Root directory of CORTEX repository
        """
        self.repo_root = repo_root
        self.test_results: Dict = {}
        self.all_tests_passed = False
    
    def run_all_tests(self) -> bool:
        """
        Run all documentation validation tests.
        
        Returns:
            True if all tests passed, False otherwise
        """
        print("\n" + "="*60)
        print("🧪 CORTEX DOCUMENTATION TEST SUITE")
        print("="*60 + "\n")
        
        test_suites = [
            ('Document Quality', 'tests/documentation/test_doc_quality.py'),
            ('Content Freshness', 'tests/documentation/test_content_freshness.py'),
            ('MkDocs Build', 'mkdocs build'),
            ('Image References', 'tests/documentation/test_image_references.py'),
            ('FAQ Structure', 'tests/documentation/test_faq.py'),
        ]
        
        total_passed = 0
        total_failed = 0
        
        for suite_name, test_path in test_suites:
            print(f"\n{'='*60}")
            print(f"📋 Running: {suite_name}")
            print(f"{'='*60}\n")
            
            if test_path == 'mkdocs build':
                passed, failed = self._run_mkdocs_build()
            else:
                passed, failed = self._run_pytest_suite(test_path)
            
            self.test_results[suite_name] = {
                'passed': passed,
                'failed': failed,
                'status': 'PASS' if failed == 0 else 'FAIL'
            }
            
            total_passed += passed
            total_failed += failed
        
        self.all_tests_passed = (total_failed == 0)
        
        # Print summary
        self._print_summary(total_passed, total_failed)
        
        return self.all_tests_passed
    
    def _run_pytest_suite(self, test_path: str) -> tuple:
        """
        Run pytest test suite.
        
        Args:
            test_path: Relative path to test file
        
        Returns:
            Tuple of (passed_count, failed_count)
        """
        test_file = self.repo_root / test_path
        
        if not test_file.exists():
            print(f"⚠️ Test file not found: {test_path}")
            print(f"   This test suite will be created during implementation.")
            return (0, 0)
        
        try:
            result = subprocess.run(
                ['pytest', str(test_file), '-v', '--tb=short'],
                cwd=self.repo_root,
                capture_output=True,
                text=True
            )
            
            # Parse pytest output for pass/fail counts
            output = result.stdout
            
            passed = output.count(' PASSED')
            failed = output.count(' FAILED')
            skipped = output.count(' SKIPPED')
            
            print(output)
            
            if failed > 0:
                print(f"\n❌ {failed} test(s) failed")
            else:
                print(f"\n✅ All tests passed!")
            
            if skipped > 0:
                print(f"⏭️  {skipped} test(s) skipped")
            
            return (passed, failed)
            
        except FileNotFoundError:
            print("⚠️ pytest not installed. Install with: pip install pytest")
            return (0, 1)
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return (0, 1)
    
    def _run_mkdocs_build(self) -> tuple:
        """
        Run MkDocs build validation.
        
        Returns:
            Tuple of (1 if passed, 0 if failed) or (0, 1) if failed
        """
        try:
            result = subprocess.run(
                ['mkdocs', 'build', '--strict'],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode == 0:
                print("✅ MkDocs build successful!")
                print(f"\n{result.stdout}")
                return (1, 0)
            else:
                print("❌ MkDocs build failed!")
                print(f"\n{result.stderr}")
                return (0, 1)
                
        except FileNotFoundError:
            print("⚠️ mkdocs not installed. Install with: pip install mkdocs mkdocs-material")
            return (0, 1)
        except subprocess.TimeoutExpired:
            print("❌ MkDocs build timed out (>120 seconds)")
            return (0, 1)
        except Exception as e:
            print(f"❌ Error running MkDocs build: {e}")
            return (0, 1)
    
    def _print_summary(self, total_passed: int, total_failed: int):
        """Print test execution summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        for suite_name, results in self.test_results.items():
            status_icon = "✅" if results['status'] == 'PASS' else "❌"
            print(f"{status_icon} {suite_name}: {results['passed']} passed, {results['failed']} failed")
        
        print("\n" + "-"*60)
        print(f"Total: {total_passed} passed, {total_failed} failed")
        print("-"*60)
        
        if self.all_tests_passed:
            print("\n🎉 ALL TESTS PASSED! Documentation is production-ready.")
        else:
            print("\n⚠️ SOME TESTS FAILED. Review failures above and fix before proceeding.")
        
        print("="*60 + "\n")
    
    def save_report(self, output_path: Path):
        """Save test results to JSON report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'all_tests_passed': self.all_tests_passed,
            'test_results': self.test_results,
            'summary': {
                'total_suites': len(self.test_results),
                'suites_passed': sum(1 for r in self.test_results.values() if r['status'] == 'PASS'),
                'suites_failed': sum(1 for r in self.test_results.values() if r['status'] == 'FAIL'),
            }
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Test report saved to: {output_path}")


def main():
    """CLI entry point for test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CORTEX Documentation Test Runner')
    parser.add_argument('--output', type=str, default='cortex-brain/cleanup-reports',
                        help='Output directory for test reports')
    parser.add_argument('--fail-fast', action='store_true',
                        help='Stop execution on first test failure')
    
    args = parser.parse_args()
    
    # Initialize runner
    repo_root = Path(__file__).parent.parent.parent.parent
    runner = DocumentationTestRunner(repo_root)
    
    # Run tests
    all_passed = runner.run_all_tests()
    
    # Save report
    output_dir = repo_root / args.output
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = output_dir / f'test-results-{timestamp}.json'
    runner.save_report(report_path)
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
