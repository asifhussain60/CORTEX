"""
Dashboard Test Suite Runner

Executes all dashboard-related tests in a single run with comprehensive reporting.

Usage:
    python tests/dashboard/run_all_dashboard_tests.py
    
    Options:
    --fast      : Skip performance tests
    --mock-only : Only test mock data validation
    --no-collect: Skip collector tests (only validate mock data)
    
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import pytest


def print_header():
    """Print test suite header"""
    print("=" * 80)
    print("CORTEX DASHBOARD TEST SUITE")
    print("=" * 80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Suite: All Dashboard Tabs Data Contract Validation")
    print("=" * 80)
    print()


def print_coverage_summary():
    """Print test coverage summary"""
    print("\n" + "=" * 80)
    print("TEST COVERAGE SUMMARY")
    print("=" * 80)
    print("""
Dashboard Tabs Tested:
  * Executive Summary - Purpose, History, Composition
  * Overview - Health data, metrics, status
  * Tech Stack - Technologies, summary, status counts
  * Security - Score, vulnerabilities, OWASP Top 10
  * Architecture - Layers, tiers, components
  * Code Organization - File metrics, structure
  * Vendors - Third-party dependencies (if available)
  * Team Metrics - Contributor stats (if available)

Validation Types:
  * Schema validation (required keys)
  * Data type validation
  * Mock data compatibility
  * Integration testing (all collectors together)
  * Performance testing (3s per collector limit)
    """)


def run_all_tests(skip_generation=False):
    """
    Run complete dashboard test suite with two-phase approach.
    
    Phase 1: Generate test data from all collectors (with progress feedback)
    Phase 2: Run fast integration tests against generated data
    
    Args:
        skip_generation: Skip data generation phase (use existing data)
    
    Returns:
        Exit code (0 = success, non-zero = failure)
    """
    print_header()
    
    # Phase 1: Generate test data (unless skipped)
    if not skip_generation:
        print("Phase 1: Generating Test Data from All Collectors")
        print("-" * 80)
        print("(This will take 60-120 seconds with progress updates...)\n")
        
        import subprocess
        result = subprocess.run(
            [sys.executable, 'tests/dashboard/generate_test_data.py'],
            capture_output=False
        )
        
        if result.returncode != 0:
            print("\n[FAIL] Data generation failed\n")
            return result.returncode
        
        print("\n" + "=" * 80)
    else:
        print("Phase 1: SKIPPED (using existing generated data)")
        print("-" * 80)
        print()
    
    # Phase 2: Run integration tests
    print("\nPhase 2: Running Integration Tests on Generated Data")
    print("-" * 80)
    print()
    
    pytest_args = [
        'tests/dashboard/test_all_tabs_data_contract.py',
        '-v',
        '--tb=short',
        '--color=yes',
        '-m', 'dashboard'
    ]
    
    exit_code = pytest.main(pytest_args)
    
    # Print summary
    print_coverage_summary()
    
    if exit_code == 0:
        print("\n[PASS] ALL DASHBOARD TESTS PASSED\n")
    else:
        print("\n[FAIL] SOME DASHBOARD TESTS FAILED\n")
    
    return exit_code


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='CORTEX Dashboard Test Suite Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full run: Generate data + run tests (default)
  python tests/dashboard/run_all_dashboard_tests.py
  
  # Quick run: Use existing generated data
  python tests/dashboard/run_all_dashboard_tests.py --quick
  
  # Only generate data (no tests)
  python tests/dashboard/run_all_dashboard_tests.py --generate-only
  
  # Only run tests (skip generation)
  python tests/dashboard/run_all_dashboard_tests.py --skip-generation
        """
    )
    
    parser.add_argument(
        '--skip-generation',
        action='store_true',
        help='Skip data generation phase (use existing data)'
    )
    
    parser.add_argument(
        '--generate-only',
        action='store_true',
        help='Only generate data, do not run tests'
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick validation (run tests on existing data without regenerating)'
    )
    
    parser.add_argument(
        '--integration',
        action='store_true',
        help='Run integration tests only (same as --skip-generation)'
    )
    
    args = parser.parse_args()
    
    # Route to appropriate test mode
    if args.generate_only:
        # Just generate data, don't run tests
        import subprocess
        result = subprocess.run(
            [sys.executable, 'tests/dashboard/generate_test_data.py']
        )
        sys.exit(result.returncode)
    elif args.quick or args.integration or args.skip_generation:
        # Run tests without regenerating data
        exit_code = run_all_tests(skip_generation=True)
    else:
        # Full run: generate data + run tests
        exit_code = run_all_tests(skip_generation=False)
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
