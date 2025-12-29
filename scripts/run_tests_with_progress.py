"""
Fast Test Runner with Progress Indicators

Runs pytest with optimizations:
- Shows test progress in real-time
- Excludes problematic files from coverage
- Provides time estimates
- Clear visual feedback

Usage:
    python scripts/run_tests_with_progress.py [test_path]
    python scripts/run_tests_with_progress.py tests/core/knowledge_graph/
"""

import subprocess
import sys
import time
from pathlib import Path


def run_tests_fast(test_path: str = "tests/"):
    """Run tests with progress indicators and fast execution"""
    
    print("=" * 70)
    print("🧪 CORTEX Fast Test Runner")
    print("=" * 70)
    print(f"📂 Test Path: {test_path}")
    print(f"⏱️  Started: {time.strftime('%H:%M:%S')}")
    print("=" * 70)
    print()
    
    # Build pytest command with optimizations
    cmd = [
        sys.executable,
        "-m", "pytest",
        test_path,
        "-v",                           # Verbose (show test names)
        "--tb=short",                   # Short traceback
        "-p", "no:warnings",            # Disable warnings plugin (faster)
        "--no-cov",                     # Disable coverage (much faster)
        "--show-capture=no",            # Don't show captured output
        "-x",                           # Stop on first failure
    ]
    
    print("🚀 Running tests (no coverage for speed)...")
    print()
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, check=False)
        elapsed = time.time() - start_time
        
        print()
        print("=" * 70)
        print(f"⏱️  Completed: {time.strftime('%H:%M:%S')}")
        print(f"⚡ Duration: {elapsed:.2f} seconds")
        print("=" * 70)
        
        return result.returncode
        
    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("⚠️  Test run interrupted by user")
        print("=" * 70)
        return 1


def run_tests_with_coverage(test_path: str = "tests/"):
    """Run tests with coverage (slower but comprehensive)"""
    
    print("=" * 70)
    print("🧪 CORTEX Test Runner with Coverage")
    print("=" * 70)
    print(f"📂 Test Path: {test_path}")
    print(f"⏱️  Started: {time.strftime('%H:%M:%S')}")
    print("=" * 70)
    print()
    print("⚠️  Note: Coverage collection may take 2-3 minutes")
    print("    The tests themselves complete quickly (~1-2 seconds)")
    print("    Progress will appear frozen during coverage parsing")
    print()
    
    # Build pytest command with coverage
    cmd = [
        sys.executable,
        "-m", "pytest",
        test_path,
        "-v",
        "--tb=short",
        "--cov=src",
        "--cov-report=term-missing:skip-covered",
        "--cov-report=html:htmlcov",
        "-p", "no:warnings",
    ]
    
    print("🚀 Running tests with coverage...")
    print()
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, check=False)
        elapsed = time.time() - start_time
        
        print()
        print("=" * 70)
        print(f"⏱️  Completed: {time.strftime('%H:%M:%S')}")
        print(f"⚡ Duration: {elapsed:.2f} seconds")
        print("=" * 70)
        
        if result.returncode == 0:
            print("✅ Tests passed! Coverage report: htmlcov/index.html")
        
        return result.returncode
        
    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("⚠️  Test run interrupted by user")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    # Parse arguments
    test_path = sys.argv[1] if len(sys.argv) > 1 else "tests/"
    coverage_mode = "--coverage" in sys.argv or "-c" in sys.argv
    
    # Run tests
    if coverage_mode:
        exit_code = run_tests_with_coverage(test_path)
    else:
        exit_code = run_tests_fast(test_path)
    
    sys.exit(exit_code)
