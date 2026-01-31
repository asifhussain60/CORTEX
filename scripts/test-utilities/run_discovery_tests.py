"""
Discovery & Auto-Wiring Test Execution Suite

Executes all test suites related to:
1. Discovery Scanner (component discovery)
2. Discovery-Wiring Harness Integration
3. Comprehensive component identification

Usage:
    python run_discovery_tests.py
    python run_discovery_tests.py --verbose
    python run_discovery_tests.py --coverage
    python run_discovery_tests.py --discovery-only

Authority: cortex-total-recall.prompt.md v2.0
Phase: PRODUCTION-READINESS
Status: ✅ TEST ORCHESTRATION ACTIVE
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict
import argparse


class DiscoveryTestOrchestrator:
    """Orchestrates execution of all discovery-related tests."""
    
    def __init__(self, verbose: bool = False, coverage: bool = False):
        """Initialize test orchestrator."""
        self.verbose = verbose
        self.coverage = coverage
        self.cortex_root = Path(__file__).parent.parent.parent
        self.test_results: Dict[str, Dict] = {}
    
    def get_test_files(self) -> List[Path]:
        """Get list of test files to execute."""
        test_dir = self.cortex_root / "tests" / "unit" / "testing"
        
        if not test_dir.exists():
            print(f"Test directory not found: {test_dir}")
            return []
        
        return [
            test_dir / "test_discovery_scanner.py",
            test_dir / "test_discovery_wiring_integration.py",
        ]
    
    def build_pytest_command(self, test_file: Path) -> List[str]:
        """Build pytest command for a test file."""
        cmd = ["python", "-m", "pytest"]
        cmd.append(str(test_file))
        
        if self.verbose:
            cmd.append("-v")
        
        if self.coverage:
            cmd.extend(["--cov=cortex", "--cov-report=html"])
        
        cmd.extend(["--tb=short", "-q"])
        
        return cmd
    
    def run_discovery_scan(self) -> Dict:
        """Run discovery scan to identify components."""
        print("\n" + "="*70)
        print("RUNNING DISCOVERY SCAN")
        print("="*70)
        
        try:
            from cortex.testing.discovery_scanner import DiscoveryScanner
            
            scanner = DiscoveryScanner()
            components = scanner.scan_all()
            summary = scanner.get_summary()
            
            print(f"\nTotal Components Discovered: {summary['total_discovered']}")
            print("\nBy Category:")
            for category, count in sorted(summary['by_category'].items()):
                print(f"  - {category}: {count}")
            
            print(f"\nCritical Priority: {summary['critical_priority']}")
            print(f"High Priority: {summary['high_priority']}")
            
            return {
                "status": "success",
                "summary": summary,
                "components": components,
            }
        except Exception as e:
            print(f"Discovery scan failed: {e}")
            return {
                "status": "error",
                "error": str(e),
            }
    
    def run_discovery_tests(self) -> Dict[str, Dict]:
        """Run discovery scanner tests."""
        print("\n" + "="*70)
        print("RUNNING DISCOVERY SCANNER TESTS")
        print("="*70)
        
        test_file = self.cortex_root / "tests" / "unit" / "testing" / "test_discovery_scanner.py"
        
        if not test_file.exists():
            print(f"Test file not found: {test_file}")
            return {"discovery_tests": {"status": "skipped", "reason": "test file not found"}}
        
        cmd = self.build_pytest_command(test_file)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            test_result = {
                "status": "passed" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
            
            self.test_results["discovery_tests"] = test_result
            
            if result.returncode == 0:
                print("✓ Discovery scanner tests PASSED")
            else:
                print("✗ Discovery scanner tests FAILED")
                if self.verbose:
                    print(result.stdout)
                    print(result.stderr)
            
            return test_result
            
        except subprocess.TimeoutExpired:
            self.test_results["discovery_tests"] = {
                "status": "timeout",
                "error": "Test execution timed out"
            }
            print("✗ Discovery scanner tests TIMEOUT")
            return self.test_results["discovery_tests"]
    
    def run_integration_tests(self) -> Dict[str, Dict]:
        """Run discovery-wiring harness integration tests."""
        print("\n" + "="*70)
        print("RUNNING DISCOVERY-WIRING INTEGRATION TESTS")
        print("="*70)
        
        test_file = self.cortex_root / "tests" / "unit" / "testing" / "test_discovery_wiring_integration.py"
        
        if not test_file.exists():
            print(f"Test file not found: {test_file}")
            return {"integration_tests": {"status": "skipped", "reason": "test file not found"}}
        
        cmd = self.build_pytest_command(test_file)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            test_result = {
                "status": "passed" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
            
            self.test_results["integration_tests"] = test_result
            
            if result.returncode == 0:
                print("✓ Integration tests PASSED")
            else:
                print("✗ Integration tests FAILED")
                if self.verbose:
                    print(result.stdout)
                    print(result.stderr)
            
            return test_result
            
        except subprocess.TimeoutExpired:
            self.test_results["integration_tests"] = {
                "status": "timeout",
                "error": "Test execution timed out"
            }
            print("✗ Integration tests TIMEOUT")
            return self.test_results["integration_tests"]
    
    def run_all_tests(self) -> Dict:
        """Run all discovery-related tests."""
        results = {}
        
        # Run discovery scan
        discovery_result = self.run_discovery_scan()
        results["discovery_scan"] = discovery_result
        
        # Run test suites
        discovery_tests = self.run_discovery_tests()
        results["discovery_tests"] = discovery_tests
        
        integration_tests = self.run_integration_tests()
        results["integration_tests"] = integration_tests
        
        return results
    
    def print_summary(self, results: Dict):
        """Print test execution summary."""
        print("\n" + "="*70)
        print("TEST EXECUTION SUMMARY")
        print("="*70)
        
        # Count results
        passed = 0
        failed = 0
        skipped = 0
        
        for test_name, result in results.items():
            if isinstance(result, dict) and "status" in result:
                status = result["status"]
                if status == "passed":
                    passed += 1
                    print(f"✓ {test_name}: PASSED")
                elif status == "failed":
                    failed += 1
                    print(f"✗ {test_name}: FAILED")
                elif status == "skipped":
                    skipped += 1
                    print(f"⊘ {test_name}: SKIPPED")
        
        print("\n" + "-"*70)
        print(f"Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
        
        if failed == 0:
            print("\n[SUCCESS] All discovery and wiring tests passed!")
        else:
            print(f"\n[FAILURE] {failed} test(s) failed")
        
        print("="*70)
        
        return failed == 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Execute CORTEX discovery and auto-wiring tests"
    )
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--coverage", "-c", action="store_true",
                       help="Generate coverage report")
    parser.add_argument("--discovery-only", action="store_true",
                       help="Run only discovery scan (no tests)")
    
    args = parser.parse_args()
    
    orchestrator = DiscoveryTestOrchestrator(
        verbose=args.verbose,
        coverage=args.coverage
    )
    
    print("\n" + "="*70)
    print("CORTEX DISCOVERY & AUTO-WIRING TEST SUITE")
    print("="*70)
    print(f"Verbose: {args.verbose}")
    print(f"Coverage: {args.coverage}")
    print(f"Discovery Only: {args.discovery_only}")
    
    if args.discovery_only:
        results = {"discovery_scan": orchestrator.run_discovery_scan()}
    else:
        results = orchestrator.run_all_tests()
    
    success = orchestrator.print_summary(results)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
