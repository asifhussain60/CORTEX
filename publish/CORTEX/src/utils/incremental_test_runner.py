"""
Incremental Test Runner for Large Test Suites

Runs pytest tests in small batches to provide visible progress feedback
and prevent apparent hangs with large test suites.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import re


class IncrementalTestRunner:
    """Runs pytest tests in batches with progress feedback."""
    
    def __init__(self, test_dir: str = "tests/", batch_size: int = 50):
        """
        Initialize the incremental test runner.
        
        Args:
            test_dir: Directory containing tests
            batch_size: Number of tests to run per batch
        """
        self.test_dir = Path(test_dir)
        self.batch_size = batch_size
        self.results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "total": 0
        }
        
    def collect_test_files(self) -> List[Path]:
        """
        Collect all test files instead of individual tests.
        This is simpler and faster than collecting individual test node IDs.
        
        Returns:
            List of test file paths
        """
        print(f"[*] Collecting test files from {self.test_dir}...")
        
        test_files = []
        for test_file in Path(self.test_dir).rglob("test_*.py"):
            test_files.append(test_file)
        
        print(f"[+] Found {len(test_files)} test files\n")
        return test_files
    
    def count_tests_in_files(self, files: List[Path]) -> int:
        """Quick count of tests across files."""
        cmd = [sys.executable, "-m", "pytest"] + [str(f) for f in files] + ["--collect-only", "-q"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            # Look for "collected N items"
            for line in result.stdout.split('\n'):
                if 'collected' in line and 'item' in line:
                    match = re.search(r'(\d+)\s+item', line)
                    if match:
                        return int(match.group(1))
            return 0
        except:
            return 0
        """
        Collect all test paths using pytest --collect-only.
        
        Returns:
            List of test node IDs
        """
        print(f"[*] Collecting tests from {self.test_dir}...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "--collect-only", "-q"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse test node IDs from output
            # Format: <Function test_name> appears on its own line
            tests = []
            current_file = None
            current_class = None
            
            for line in result.stdout.split('\n'):
                line_stripped = line.strip()
                
                # Skip headers and empty lines
                if not line_stripped or 'test session starts' in line_stripped:
                    continue
                if line_stripped.startswith('===') or line_stripped.startswith('collected'):
                    continue
                
                # Track current module/file
                if '<Module ' in line_stripped and '.py>' in line_stripped:
                    # Extract: <Module test_file.py>
                    module_match = re.search(r'<Module\s+([^>]+)>', line_stripped)
                    if module_match:
                        filename = module_match.group(1)
                        # Need to track the path - look for previous <Package> or <Dir> lines
                        # For now, we'll construct the node ID when we see <Function>
                        current_file = filename.replace('.py>', '.py')
                
                # Track current class
                if '<Class ' in line_stripped:
                    class_match = re.search(r'<Class\s+([^>]+)>', line_stripped)
                    if class_match:
                        current_class = class_match.group(1)
                
                # Found a test function
                if '<Function ' in line_stripped:
                    func_match = re.search(r'<Function\s+([^>]+)>', line_stripped)
                    if func_match and current_file:
                        func_name = func_match.group(1)
                        # Build node ID: tests/path/test_file.py::ClassName::test_name
                        # Since we don't have full path yet, just collect function names
                        # We'll run tests by directory later
                        tests.append(func_name)
            
            # If we got function names but need full paths, use a different approach
            # Let's use pytest --collect-only with less formatting
            if not tests or len(tests) < 100:  # Sanity check
                # Try again with plain output
                cmd2 = [
                    sys.executable, "-m", "pytest",
                    str(self.test_dir),
                    "--collect-only", "--quiet", "--quiet"
                ]
                result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=30)
                
                # Parse simpler format
                tests = []
                for line in result2.stdout.split('\n'):
                    line = line.strip()
                    if '::test_' in line and not line.startswith('<'):
                        # Direct node ID format: tests/path/file.py::test_name
                        tests.append(line)
            
            print(f"[+] Collected {len(tests)} tests\n")
            return tests
            
        except subprocess.TimeoutExpired:
            print("[X] Test collection timed out after 30 seconds")
            return []
        except Exception as e:
            print(f"[X] Error collecting tests: {e}")
            return []
    
    def run_batch(self, batch: List[str], batch_num: int, total_batches: int) -> Dict[str, int]:
        """
        Run a single batch of tests.
        
        Args:
            batch: List of test node IDs to run
            batch_num: Current batch number (1-indexed)
            total_batches: Total number of batches
            
        Returns:
            Dictionary with pass/fail/skip counts
        """
        print(f"[Batch {batch_num}/{total_batches}] {len(batch)} tests...", end=" ", flush=True)
        
        cmd = [
            sys.executable, "-m", "pytest",
            "-v", "--tb=no", "-q",
            "--no-header"
        ] + batch
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes per batch
            )
            
            # Parse results from output
            batch_results = self._parse_pytest_output(result.stdout)
            
            # Print batch summary
            status_icon = "[+]" if batch_results["failed"] == 0 else "[!]"
            print(f"{status_icon} {batch_results['passed']} passed, {batch_results['failed']} failed, {batch_results['skipped']} skipped")
            
            return batch_results
            
        except subprocess.TimeoutExpired:
            print("[X] TIMEOUT (>2min)")
            return {"passed": 0, "failed": len(batch), "skipped": 0, "errors": 1}
        except Exception as e:
            print(f"[X] ERROR: {e}")
            return {"passed": 0, "failed": 0, "skipped": 0, "errors": 1}
    
    def _parse_pytest_output(self, output: str) -> Dict[str, int]:
        """
        Parse pytest output to extract test results.
        
        Args:
            output: pytest stdout text
            
        Returns:
            Dictionary with counts
        """
        results = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}
        
        # Look for pytest summary line like:
        # "10 passed, 2 failed, 1 skipped in 5.23s"
        summary_pattern = r'(\d+)\s+passed|(\d+)\s+failed|(\d+)\s+skipped|(\d+)\s+error'
        
        for match in re.finditer(summary_pattern, output):
            if match.group(1):  # passed
                results["passed"] = int(match.group(1))
            elif match.group(2):  # failed
                results["failed"] = int(match.group(2))
            elif match.group(3):  # skipped
                results["skipped"] = int(match.group(3))
            elif match.group(4):  # errors
                results["errors"] = int(match.group(4))
        
        # If no summary found, count PASSED/FAILED/SKIPPED markers
        if results["passed"] == 0 and results["failed"] == 0:
            results["passed"] = output.count(" PASSED")
            results["failed"] = output.count(" FAILED")
            results["skipped"] = output.count(" SKIPPED")
            results["errors"] = output.count(" ERROR")
        
        return results
    
    def run_all(self) -> Dict[str, int]:
        """
        Run all tests in batches with progress feedback.
        Works with test files as batches for simplicity.
        
        Returns:
            Dictionary with total counts
        """
        print("=" * 70)
        print("INCREMENTAL TEST RUNNER")
        print("=" * 70)
        
        # Collect all test files
        test_files = self.collect_test_files()
        if not test_files:
            print("[X] No test files found")
            return self.results
        
        # Quick count of total tests
        total_tests = self.count_tests_in_files(test_files)
        print(f"[*] Found ~{total_tests} tests across {len(test_files)} files")
        print(f"[*] Running files in batches of {self.batch_size}")
        print("=" * 70)
        print()
        
        # Split files into batches
        batches = [
            test_files[i:i + self.batch_size]
            for i in range(0, len(test_files), self.batch_size)
        ]
        total_batches = len(batches)
        
        # Run each batch
        for batch_num, batch in enumerate(batches, 1):
            batch_results = self.run_file_batch(batch, batch_num, total_batches)
            
            # Accumulate results
            self.results["passed"] += batch_results["passed"]
            self.results["failed"] += batch_results["failed"]
            self.results["skipped"] += batch_results["skipped"]
            self.results["errors"] += batch_results["errors"]
        
        self.results["total"] = self.results["passed"] + self.results["failed"] + self.results["skipped"]
        
        # Print final summary
        print()
        print("=" * 70)
        print("FINAL RESULTS")
        print("=" * 70)
        print(f"Total Tests:  {self.results['total']}")
        print(f"[+] Passed:   {self.results['passed']} ({self._percentage(self.results['passed'])}%)")
        print(f"[-] Failed:   {self.results['failed']} ({self._percentage(self.results['failed'])}%)")
        print(f"[o] Skipped:  {self.results['skipped']} ({self._percentage(self.results['skipped'])}%)")
        if self.results['errors'] > 0:
            print(f"[!] Errors:   {self.results['errors']}")
        print("=" * 70)
        
        return self.results
    
    def run_file_batch(self, files: List[Path], batch_num: int, total_batches: int) -> Dict[str, int]:
        """
        Run a batch of test files, showing progress for each file.
        
        Args:
            files: List of test file paths
            batch_num: Current batch number (1-indexed)
            total_batches: Total number of batches
            
        Returns:
            Dictionary with pass/fail/skip counts
        """
        print(f"\n[Batch {batch_num}/{total_batches}] Running {len(files)} files:")
        print("-" * 70)
        
        batch_results = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}
        
        # Run each file individually to show per-file progress
        for file_num, file_path in enumerate(files, 1):
            file_name = file_path.name
            print(f"  [{file_num}/{len(files)}] {file_name:50s} ", end="", flush=True)
            
            cmd = [
                sys.executable, "-m", "pytest",
                str(file_path),
                "-v", "--tb=no", "-q"
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60  # 1 minute per file
                )
                
                # Parse results from this file
                file_results = self._parse_pytest_output(result.stdout)
                
                # Accumulate into batch totals
                batch_results["passed"] += file_results["passed"]
                batch_results["failed"] += file_results["failed"]
                batch_results["skipped"] += file_results["skipped"]
                batch_results["errors"] += file_results["errors"]
                
                # Show per-file result
                if file_results["failed"] > 0 or file_results["errors"] > 0:
                    status = "[FAIL]"
                else:
                    status = "[ OK ]"
                
                print(f"{status} {file_results['passed']}p {file_results['failed']}f {file_results['skipped']}s")
                
            except subprocess.TimeoutExpired:
                print("[TIMEOUT]")
                batch_results["errors"] += 1
            except Exception as e:
                print(f"[ERROR: {str(e)[:30]}]")
                batch_results["errors"] += 1
        
        # Print batch summary
        print("-" * 70)
        status_icon = "[+]" if batch_results["failed"] == 0 else "[!]"
        print(f"{status_icon} Batch Total: {batch_results['passed']} passed, {batch_results['failed']} failed, {batch_results['skipped']} skipped\n")
        
        return batch_results
    
    def _percentage(self, count: int) -> str:
        """Calculate percentage with 1 decimal place."""
        if self.results['total'] == 0:
            return "0.0"
        return f"{(count / self.results['total'] * 100):.1f}"
    
    def get_summary_line(self) -> str:
        """Get one-line summary for status updates."""
        return (
            f"{self.results['total']} tests: "
            f"{self.results['passed']} passed, "
            f"{self.results['failed']} failed, "
            f"{self.results['skipped']} skipped"
        )


def main():
    """CLI entry point for incremental test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run pytest tests in batches with progress feedback"
    )
    parser.add_argument(
        "--test-dir",
        default="tests/",
        help="Directory containing tests (default: tests/)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Number of tests per batch (default: 50)"
    )
    
    args = parser.parse_args()
    
    runner = IncrementalTestRunner(
        test_dir=args.test_dir,
        batch_size=args.batch_size
    )
    
    results = runner.run_all()
    
    # Exit with appropriate code
    if results["failed"] > 0 or results["errors"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
