"""Run integration tests one by one with timeout to identify hanging tests.

Usage:
    python scripts/run_integration_tests_with_timeout.py
    python scripts/run_integration_tests_with_timeout.py --timeout 30
    python scripts/run_integration_tests_with_timeout.py --output hanging_tests.yaml
"""

import subprocess
import sys
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import List
import yaml


@dataclass
class TestResult:
    """Result of a single test execution."""
    test_id: str
    status: str  # PASSED, FAILED, TIMEOUT, ERROR
    duration: float
    error_message: str = ""


@dataclass
class TestReport:
    """Report of all test executions."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    timeout: int = 0
    error: int = 0
    hanging_tests: List[TestResult] = field(default_factory=list)
    slow_tests: List[TestResult] = field(default_factory=list)
    all_results: List[TestResult] = field(default_factory=list)


def collect_integration_tests(cwd: Path) -> List[str]:
    """Collect all integration tests using pytest --collect-only."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-qq", 
         "tests/", "-k", "integration"],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=120
    )
    
    tests = []
    for line in result.stdout.splitlines():
        line = line.strip()
        # Test lines look like: tests/unit/file.py::TestClass::test_method
        # Skip empty lines, lines with errors, and the [PYTEST] marker
        if "::" in line and ("tests/" in line or "tests\\" in line):
            # Clean up the line - remove any extra whitespace or control chars
            clean_line = line.split()[0] if line.split() else line
            tests.append(clean_line)
    
    return tests


def run_single_test(test_id: str, cwd: Path, timeout: int = 30) -> TestResult:
    """Run a single test with timeout."""
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-xvs", test_id, "--timeout=0"],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout
        )
        duration = time.time() - start_time
        
        if result.returncode == 0:
            status = "PASSED"
            error_msg = ""
        else:
            status = "FAILED"
            # Extract last 500 chars of stderr/stdout for error context
            error_msg = (result.stderr + result.stdout)[-500:]
        
        return TestResult(test_id, status, duration, error_msg)
        
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return TestResult(test_id, "TIMEOUT", duration, f"Test exceeded {timeout}s timeout")
        
    except Exception as e:
        duration = time.time() - start_time
        return TestResult(test_id, "ERROR", duration, str(e))


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run integration tests with timeout")
    parser.add_argument("--timeout", type=int, default=30,
                        help="Timeout per test in seconds (default: 30)")
    parser.add_argument("--slow-threshold", type=float, default=5.0,
                        help="Mark tests slower than this as slow (default: 5.0)")
    parser.add_argument("--output", type=str, default="hanging_tests.yaml",
                        help="Output file for results (default: hanging_tests.yaml)")
    parser.add_argument("--max-tests", type=int, default=None,
                        help="Maximum number of tests to run (for testing)")
    
    args = parser.parse_args()
    
    cwd = Path(__file__).parent.parent
    output_path = cwd / args.output
    
    print(f"🔍 Collecting integration tests...")
    tests = collect_integration_tests(cwd)
    print(f"📋 Found {len(tests)} integration tests")
    
    if args.max_tests:
        tests = tests[:args.max_tests]
        print(f"⚠️  Limited to first {args.max_tests} tests")
    
    report = TestReport(total=len(tests))
    
    print(f"\n🚀 Running tests with {args.timeout}s timeout each...\n")
    
    for i, test_id in enumerate(tests, 1):
        # Print progress
        short_id = test_id.split("::")[-1] if "::" in test_id else test_id
        print(f"[{i}/{len(tests)}] {short_id}...", end=" ", flush=True)
        
        result = run_single_test(test_id, cwd, args.timeout)
        report.all_results.append(result)
        
        # Update counters
        if result.status == "PASSED":
            report.passed += 1
            symbol = "✓"
        elif result.status == "FAILED":
            report.failed += 1
            symbol = "✗"
        elif result.status == "TIMEOUT":
            report.timeout += 1
            report.hanging_tests.append(result)
            symbol = "⏰"
        else:
            report.error += 1
            symbol = "⚠"
        
        # Track slow tests
        if result.duration > args.slow_threshold and result.status != "TIMEOUT":
            report.slow_tests.append(result)
        
        print(f"{symbol} ({result.duration:.1f}s)")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total:   {report.total}")
    print(f"Passed:  {report.passed}")
    print(f"Failed:  {report.failed}")
    print(f"Timeout: {report.timeout}")
    print(f"Error:   {report.error}")
    
    if report.hanging_tests:
        print(f"\n🚨 HANGING TESTS ({len(report.hanging_tests)}):")
        for t in report.hanging_tests:
            print(f"  - {t.test_id}")
    
    if report.slow_tests:
        print(f"\n⚠️  SLOW TESTS (>{args.slow_threshold}s): {len(report.slow_tests)}")
        for t in sorted(report.slow_tests, key=lambda x: -x.duration)[:10]:
            print(f"  - {t.duration:.1f}s: {t.test_id}")
    
    # Write YAML report
    report_data = {
        "summary": {
            "total": report.total,
            "passed": report.passed,
            "failed": report.failed,
            "timeout": report.timeout,
            "error": report.error,
            "timeout_threshold_seconds": args.timeout,
            "slow_threshold_seconds": args.slow_threshold,
        },
        "hanging_tests": [
            {"test_id": t.test_id, "duration": t.duration, "error": t.error_message}
            for t in report.hanging_tests
        ],
        "slow_tests": [
            {"test_id": t.test_id, "duration": round(t.duration, 2)}
            for t in sorted(report.slow_tests, key=lambda x: -x.duration)
        ],
        "failed_tests": [
            {"test_id": t.test_id, "duration": round(t.duration, 2), "error": t.error_message[:200]}
            for t in report.all_results if t.status == "FAILED"
        ],
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(report_data, f, default_flow_style=False, sort_keys=False)
    
    print(f"\n📄 Report saved to: {output_path}")
    
    return 0 if report.timeout == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
