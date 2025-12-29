#!/usr/bin/env python3
"""
Sequential Test Runner for CORTEX
Runs each test file one at a time with immediate output display.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json

def get_test_files(test_dir: Path):
    """Discover all test files in the tests directory."""
    test_files = []
    for pattern in ["test_*.py", "*_test.py"]:
        test_files.extend(test_dir.rglob(pattern))
    return sorted(test_files)

def run_test_file(test_file: Path, index: int, total: int):
    """Run a single test file and display results."""
    relative_path = test_file.relative_to(Path.cwd())
    
    print("\n" + "="*80)
    print(f"TEST {index}/{total}: {relative_path}")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print("-"*80 + "\n")
    
    # Run pytest on single file WITHOUT coverage (much faster)
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "-v",           # Verbose
        "--tb=short",   # Short traceback format
        "--no-cov",     # Disable coverage collection
        "-m", "not slow",  # Skip slow tests
        "--color=yes",  # Colored output
    ]
    
    start_time = datetime.now()
    result = subprocess.run(cmd, capture_output=False, text=True)
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "-"*80)
    print(f"Completed: {end_time.strftime('%H:%M:%S')} | Duration: {duration:.2f}s")
    
    if result.returncode == 0:
        print("✅ PASSED")
    else:
        print("❌ FAILED")
    
    print("="*80 + "\n")
    
    return {
        "file": str(relative_path),
        "passed": result.returncode == 0,
        "duration": duration,
        "return_code": result.returncode
    }

def main():
    """Main test runner."""
    print("\n🧠 CORTEX Sequential Test Runner")
    print("="*80)
    
    # Find all test files
    test_dir = Path("tests")
    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        sys.exit(1)
    
    test_files = get_test_files(test_dir)
    
    if not test_files:
        print("❌ No test files found")
        sys.exit(1)
    
    print(f"Found {len(test_files)} test files")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    # Run each test file sequentially
    results = []
    start_time = datetime.now()
    
    for i, test_file in enumerate(test_files, 1):
        result = run_test_file(test_file, i, len(test_files))
        results.append(result)
    
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    # Summary report
    print("\n" + "="*80)
    print("📊 SUMMARY REPORT")
    print("="*80)
    
    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Total Duration: {total_duration:.2f}s")
    print(f"📅 Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if failed > 0:
        print("\n❌ Failed Tests:")
        for r in results:
            if not r["passed"]:
                print(f"  - {r['file']} (exit code: {r['return_code']})")
    
    print("\n" + "="*80 + "\n")
    
    # Save results to JSON
    results_file = Path("test_results_sequential.json")
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": end_time.isoformat(),
            "total_duration": total_duration,
            "total_tests": len(results),
            "passed": passed,
            "failed": failed,
            "results": results
        }, f, indent=2)
    
    print(f"📄 Detailed results saved to: {results_file}")
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
