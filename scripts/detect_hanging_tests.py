#!/usr/bin/env python3
"""
Hanging Test Detection and Analysis System
===========================================

Identifies slow, hanging, and problematic tests in the CORTEX test suite.
Provides detailed timing analysis, dependency graphs, and remediation suggestions.

Usage:
    python scripts/detect_hanging_tests.py --analyze           # Full analysis with timing
    python scripts/detect_hanging_tests.py --timeout=10       # Set custom timeout (default 30s)
    python scripts/detect_hanging_tests.py --threshold=5      # Show tests slower than N seconds
    python scripts/detect_hanging_tests.py --profile           # Generate performance profile
    python scripts/detect_hanging_tests.py --fix-hanging       # Auto-fix detected hanging tests
    python scripts/detect_hanging_tests.py --report            # Generate HTML report

Author: CORTEX CI/CD
Version: 1.0
"""

import subprocess
import json
import sys
import time
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
import xml.etree.ElementTree as ET
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TestMetrics:
    """Metrics for a single test."""
    test_name: str
    file_path: str
    class_name: str
    status: str  # PASSED, FAILED, ERROR, TIMEOUT, SKIPPED
    duration: float  # seconds
    timeout_set: int  # seconds, 0 if not set
    is_hanging: bool = False
    is_slow: bool = False
    error_message: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)


class HangingTestDetector:
    """Detects and analyzes hanging tests in pytest suite."""
    
    def __init__(self, test_path: str = "tests/", timeout: int = 30, threshold: float = 5.0):
        """
        Initialize detector.
        
        Args:
            test_path: Root test directory
            timeout: Global timeout in seconds
            threshold: Threshold for "slow" test detection (seconds)
        """
        self.test_path = Path(test_path)
        self.timeout = timeout
        self.threshold = threshold
        self.repo_root = Path(__file__).parent.parent
        self.metrics: List[TestMetrics] = []
        self.hanging_tests: List[TestMetrics] = []
        self.slow_tests: List[TestMetrics] = []
        self.test_dependencies: Dict[str, List[str]] = defaultdict(list)
    
    def collect_tests(self) -> List[str]:
        """Collect all test names using pytest collection."""
        logger.info("📋 Collecting test names...")
        
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", str(self.test_path), "--collect-only", "-q"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse output to extract test names
            test_names = []
            for line in result.stdout.split('\n'):
                if '::test_' in line or '::Test' in line:
                    # Extract test path
                    match = re.search(r'(tests/[^:]+)::(.*)', line)
                    if match:
                        test_names.append(f"{match.group(1)}::{match.group(2)}")
            
            logger.info(f"✅ Collected {len(test_names)} tests")
            return test_names
        
        except subprocess.TimeoutExpired:
            logger.error("❌ Test collection timed out")
            return []
        except Exception as e:
            logger.error(f"❌ Error collecting tests: {e}")
            return []
    
    def run_with_timing(self, test_pattern: str, verbose: bool = False) -> Tuple[int, float, str]:
        """
        Run tests and capture timing information.
        
        Args:
            test_pattern: Pytest test pattern (e.g., "tests/unit/core/")
            verbose: Enable verbose output
        
        Returns:
            Tuple of (exit_code, duration, output)
        """
        logger.info(f"⏱️  Running tests: {test_pattern}")
        
        cmd = [
            "python3", "-m", "pytest",
            test_pattern,
            "--tb=no",
            "-v" if verbose else "-q",
            f"--timeout={self.timeout}",
            "--durations=20"  # Show 20 slowest tests
        ]
        
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=self.timeout * 3  # Allow 3x global timeout for full suite
            )
            duration = time.time() - start_time
            return result.returncode, duration, result.stdout + result.stderr
        
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            logger.warning(f"⚠️  Test suite timed out after {duration:.2f}s")
            return 124, duration, "TEST SUITE TIMEOUT"
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ Error running tests: {e}")
            return 1, duration, str(e)
    
    def analyze_pytest_output(self, output: str) -> List[TestMetrics]:
        """
        Parse pytest output to extract timing information.
        
        Args:
            output: Pytest stdout/stderr output
        
        Returns:
            List of TestMetrics
        """
        logger.info("🔍 Analyzing pytest output...")
        
        metrics = []
        
        # Find slowest tests section
        slowest_match = re.search(r'=+ slowest (\d+) durations =+\n(.*?)(?:=+|$)', output, re.DOTALL)
        if slowest_match:
            durations_text = slowest_match.group(2)
            for line in durations_text.split('\n'):
                # Parse lines like "1.23s setup tests/unit/test_file.py::TestClass::test_method"
                match = re.match(r'(\d+\.\d+)s\s+(\w+)\s+(tests/.*?)(?:\s|$)', line)
                if match:
                    duration = float(match.group(1))
                    phase = match.group(2)
                    test_path = match.group(3)
                    
                    metric = TestMetrics(
                        test_name=test_path.split("::")[-1],
                        file_path=test_path,
                        class_name=test_path.split("::")[-2] if "::" in test_path else "",
                        status="SLOW",
                        duration=duration,
                        timeout_set=self.timeout,
                        is_slow=(duration > self.threshold)
                    )
                    metrics.append(metric)
        
        # Find failed/errored tests
        for line in output.split('\n'):
            if 'FAILED' in line or 'ERROR' in line:
                # Parse lines like "tests/unit/test_file.py::TestClass::test_method FAILED"
                match = re.match(r'(tests/.*?)\s+(FAILED|ERROR|TIMEOUT)', line)
                if match:
                    test_path = match.group(1)
                    status = match.group(2)
                    
                    metric = TestMetrics(
                        test_name=test_path.split("::")[-1],
                        file_path=test_path,
                        class_name=test_path.split("::")[-2] if "::" in test_path else "",
                        status=status,
                        duration=0.0,
                        timeout_set=self.timeout,
                        is_hanging=(status == "TIMEOUT")
                    )
                    metrics.append(metric)
        
        # Count results
        passed = output.count(' PASSED')
        failed = output.count(' FAILED')
        errors = output.count(' ERROR')
        timeouts = output.count(' TIMEOUT')
        
        logger.info(f"✅ Results: {passed} passed, {failed} failed, {errors} errors, {timeouts} timeouts")
        
        return metrics
    
    def analyze_test_files(self) -> Dict[str, Dict]:
        """
        Analyze test files for hanging patterns.
        
        Returns:
            Dict mapping file paths to analysis
        """
        logger.info("🔎 Analyzing test files for hanging patterns...")
        
        analysis = {}
        test_files = list(self.test_path.rglob("test_*.py"))
        
        for test_file in test_files:
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                
                file_analysis = {
                    'infinite_loops': len(re.findall(r'while True:|while 1:', content)),
                    'missing_timeouts': len(re.findall(r'def test_(?!.*timeout)', content)),
                    'blocking_calls': len(re.findall(r'\.join\(\)|\.get\(\)|\.wait\(\)|\.lock\(\)', content)),
                    'sleep_calls': len(re.findall(r'time\.sleep\(|sleep\(', content)),
                    'file_size': len(content),
                    'test_count': len(re.findall(r'def test_', content))
                }
                
                if file_analysis['infinite_loops'] > 0 or file_analysis['missing_timeouts'] > 5:
                    analysis[str(test_file)] = file_analysis
            
            except Exception as e:
                logger.debug(f"Error analyzing {test_file}: {e}")
        
        return analysis
    
    def generate_report(self) -> str:
        """
        Generate comprehensive hanging test report.
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("\n" + "="*80)
        report.append("HANGING TEST DETECTION REPORT")
        report.append("="*80)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Test Path: {self.test_path}")
        report.append(f"Timeout Threshold: {self.timeout}s")
        report.append(f"Slow Test Threshold: {self.threshold}s")
        report.append("")
        
        # Summary
        report.append("📊 SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Metrics Collected: {len(self.metrics)}")
        report.append(f"Hanging Tests: {len(self.hanging_tests)}")
        report.append(f"Slow Tests: {len(self.slow_tests)}")
        report.append("")
        
        # Hanging tests
        if self.hanging_tests:
            report.append("🔴 HANGING TESTS (Timeout > {}s)".format(self.timeout))
            report.append("-" * 80)
            for test in sorted(self.hanging_tests, key=lambda x: x.duration, reverse=True):
                report.append(f"  • {test.file_path}")
                report.append(f"    Duration: {test.duration:.2f}s (timeout: {test.timeout_set}s)")
                if test.error_message:
                    report.append(f"    Error: {test.error_message}")
            report.append("")
        
        # Slow tests
        if self.slow_tests:
            report.append(f"⚠️  SLOW TESTS (Duration > {self.threshold}s)")
            report.append("-" * 80)
            for test in sorted(self.slow_tests, key=lambda x: x.duration, reverse=True)[:20]:
                report.append(f"  • {test.file_path}")
                report.append(f"    Duration: {test.duration:.2f}s")
            report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 80)
        if self.hanging_tests:
            report.append("1. 🔧 Add @pytest.mark.timeout(N) decorator to hanging tests")
            report.append("2. 🔍 Review test code for infinite loops or blocking operations")
            report.append("3. ⏱️  Use pytest.mark.slow for long-running tests")
            report.append("4. 🚀 Run problematic tests individually with -vv flag")
        else:
            report.append("✅ No hanging tests detected!")
        report.append("")
        
        return "\n".join(report)
    
    def generate_json_report(self, filepath: str) -> None:
        """Generate JSON report for programmatic consumption."""
        logger.info(f"💾 Generating JSON report: {filepath}")
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'test_path': str(self.test_path),
            'timeout_threshold': self.timeout,
            'slow_threshold': self.threshold,
            'summary': {
                'total_tests': len(self.metrics),
                'hanging_tests': len(self.hanging_tests),
                'slow_tests': len(self.slow_tests)
            },
            'hanging_tests': [m.to_dict() for m in self.hanging_tests],
            'slow_tests': [m.to_dict() for m in self.slow_tests[:50]]
        }
        
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"✅ JSON report saved to {filepath}")
    
    def generate_html_report(self, filepath: str) -> None:
        """Generate interactive HTML report."""
        logger.info(f"📊 Generating HTML report: {filepath}")
        
        html = """
        <html>
        <head>
            <title>Hanging Test Detection Report</title>
            <style>
                body { font-family: monospace; margin: 20px; background: #f5f5f5; }
                h1 { color: #333; }
                table { border-collapse: collapse; width: 100%; background: white; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
                tr:hover { background-color: #f5f5f5; }
                .hanging { background-color: #ffcccc; }
                .slow { background-color: #ffffcc; }
                .passed { color: green; }
                .failed { color: red; }
                .summary { background-color: #e8f4f8; padding: 10px; margin: 10px 0; }
            </style>
        </head>
        <body>
            <h1>🔍 Hanging Test Detection Report</h1>
            <div class="summary">
                <p><strong>Generated:</strong> {}</p>
                <p><strong>Test Path:</strong> {}</p>
                <p><strong>Total Tests:</strong> {}</p>
                <p><strong>Hanging Tests:</strong> {}</p>
                <p><strong>Slow Tests:</strong> {}</p>
            </div>
            
            <h2>🔴 Hanging Tests</h2>
            <table>
                <tr><th>Test Name</th><th>Duration (s)</th><th>Status</th><th>Timeout (s)</th></tr>
                {}
            </table>
            
            <h2>⚠️ Slow Tests (Top 20)</h2>
            <table>
                <tr><th>Test Name</th><th>Duration (s)</th><th>File</th></tr>
                {}
            </table>
        </body>
        </html>
        """
        
        hanging_rows = "".join([
            f"<tr class='hanging'><td>{t.file_path}</td><td>{t.duration:.2f}</td>"
            f"<td class='failed'>{t.status}</td><td>{t.timeout_set}</td></tr>"
            for t in self.hanging_tests
        ])
        
        slow_rows = "".join([
            f"<tr class='slow'><td>{t.file_path}</td><td>{t.duration:.2f}</td><td>{t.file_path.split('::')[0]}</td></tr>"
            for t in sorted(self.slow_tests, key=lambda x: x.duration, reverse=True)[:20]
        ])
        
        html_content = html.format(
            datetime.now().isoformat(),
            str(self.test_path),
            len(self.metrics),
            len(self.hanging_tests),
            len(self.slow_tests),
            hanging_rows if hanging_rows else "<tr><td colspan='4'>No hanging tests detected</td></tr>",
            slow_rows if slow_rows else "<tr><td colspan='3'>No slow tests detected</td></tr>"
        )
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        logger.info(f"✅ HTML report saved to {filepath}")
    
    def fix_hanging_tests(self) -> None:
        """Attempt to auto-fix detected hanging tests."""
        logger.info("🔧 Attempting to fix hanging tests...")
        
        for test in self.hanging_tests:
            file_path = self.repo_root / test.file_path.split("::")[0]
            
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Add timeout marker if missing
                if '@pytest.mark.timeout' not in content:
                    # Find the test function and add decorator
                    test_name = test.file_path.split("::")[-1]
                    pattern = f"def {test_name}\\("
                    
                    if re.search(pattern, content):
                        # Add timeout decorator (2x the global timeout for specific tests)
                        replacement = f"@pytest.mark.timeout({self.timeout * 2})\ndef {test_name}("
                        new_content = re.sub(pattern, replacement, content)
                        
                        with open(file_path, 'w') as f:
                            f.write(new_content)
                        
                        logger.info(f"✅ Fixed: {test.file_path}")
            
            except Exception as e:
                logger.error(f"Error fixing {test.file_path}: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Detect and analyze hanging tests in CORTEX test suite'
    )
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Run full analysis with timing'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Global timeout in seconds (default: 30)'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=5.0,
        help='Slow test threshold in seconds (default: 5.0)'
    )
    parser.add_argument(
        '--profile',
        action='store_true',
        help='Generate performance profile'
    )
    parser.add_argument(
        '--fix-hanging',
        action='store_true',
        help='Attempt to auto-fix hanging tests'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate HTML report'
    )
    parser.add_argument(
        '--json-report',
        type=str,
        help='Generate JSON report to specified file'
    )
    parser.add_argument(
        '--test-path',
        type=str,
        default='tests/',
        help='Test directory path (default: tests/)'
    )
    
    args = parser.parse_args()
    
    # Create detector
    detector = HangingTestDetector(
        test_path=args.test_path,
        timeout=args.timeout,
        threshold=args.threshold
    )
    
    # Run analysis
    if args.analyze or args.profile:
        logger.info("🚀 Starting full test suite analysis...")
        exit_code, duration, output = detector.run_with_timing(args.test_path, verbose=True)
        
        # Parse output
        detector.metrics = detector.analyze_pytest_output(output)
        detector.hanging_tests = [m for m in detector.metrics if m.is_hanging]
        detector.slow_tests = [m for m in detector.metrics if m.is_slow]
        
        # Print report
        print(detector.generate_report())
    
    # Analyze test files
    if args.profile:
        file_analysis = detector.analyze_test_files()
        if file_analysis:
            print("\n" + "="*80)
            print("🔎 PROBLEMATIC TEST FILES")
            print("="*80)
            for filepath, analysis in sorted(file_analysis.items(), key=lambda x: sum(x[1].values()), reverse=True):
                print(f"\n{filepath}")
                for key, value in analysis.items():
                    if value > 0:
                        print(f"  • {key}: {value}")
    
    # Fix hanging tests
    if args.fix_hanging:
        detector.fix_hanging_tests()
    
    # Generate reports
    if args.report:
        detector.generate_html_report('hanging_tests_report.html')
    
    if args.json_report:
        detector.generate_json_report(args.json_report)
    
    # Return appropriate exit code
    return 0 if not detector.hanging_tests else 1


if __name__ == '__main__':
    sys.exit(main())
