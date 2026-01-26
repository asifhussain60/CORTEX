#!/usr/bin/env python3
"""
CORTEX Test Optimization Suite v2.0

Comprehensive test analysis, categorization, and execution strategy.
Provides: test health analysis, performance profiling, parallel execution guidance,
and obsolete test identification.

Usage:
    # Analyze full test suite
    python scripts/test_optimization_suite.py analyze --all
    
    # Identify and remove obsolete tests
    python scripts/test_optimization_suite.py cleanup
    
    # Run with optimal strategies
    python scripts/test_optimization_suite.py run --strategy fast
    python scripts/test_optimization_suite.py run --strategy standard
    python scripts/test_optimization_suite.py run --strategy comprehensive
    
    # Generate test performance report
    python scripts/test_optimization_suite.py profile
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
import re




@dataclass
class TestMetrics:
    """Track test performance metrics."""
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    slow_tests: int = 0  # >5s
    very_slow_tests: int = 0  # >10s
    avg_duration: float = 0.0
    estimated_serial_time: float = 0.0
    estimated_parallel_4x: float = 0.0
    estimated_parallel_8x: float = 0.0


class TestOptimizer:
    """Main test optimization orchestrator."""

    def __init__(self):
        """Initialize optimizer."""
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = self.project_root / "tests"
        self.audit_log = self.project_root / "cortex" / "test_audit_trail.log"

    def analyze_test_suite(self, verbose: bool = False) -> TestMetrics:
        """Analyze full test suite for performance characteristics."""
        print("🔍 Analyzing test suite...")

        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/unit", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            cwd=str(self.project_root),
        )

        # Count collected tests
        output = result.stdout + result.stderr
        collected_match = re.search(r"(\d+)\s+tests?(?:\s+collected|\s+in)", output)
        total_tests = int(collected_match.group(1)) if collected_match else 0

        # Read audit trail if available
        metrics = TestMetrics(total_tests=total_tests)

        if self.audit_log.exists():
            try:
                with open(self.audit_log, 'r') as f:
                    lines = f.readlines()
                    # Parse audit entries (simplified)
                    for line in lines:
                        if "PASSED" in line:
                            metrics.passed += 1
                        elif "FAILED" in line:
                            metrics.failed += 1
                        elif "SKIPPED" in line:
                            metrics.skipped += 1
            except Exception as e:
                if verbose:
                    print(f"  Warning: Could not read audit log: {e}")

        # Estimate timing
        metrics.estimated_serial_time = metrics.total_tests * 0.01  # 10ms avg per test
        metrics.estimated_parallel_4x = metrics.estimated_serial_time / 4
        metrics.estimated_parallel_8x = metrics.estimated_serial_time / 8

        return metrics

    def identify_obsolete_tests(self) -> List[str]:
        """Identify tests that are no longer valid or required."""
        print("🧹 Scanning for obsolete tests...")

        obsolete = []
        patterns_to_remove = [
            (r"cortex_toolkit", "Folder deleted per CORE-028"),
            (r"src\.", "Old module structure (migrated to cortex/)"),
            (r"cortex_brain\.", "Old module reference (migrated to cortex/brain/)"),
            (r"from src import", "Old import path"),
        ]

        for py_file in self.tests_dir.rglob("test_*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Check for import patterns from deleted/migrated modules
                for pattern, reason in patterns_to_remove:
                    if re.search(pattern, content):
                        obsolete.append((str(py_file.relative_to(self.project_root)), reason))
                        break
            except Exception:
                pass

        return obsolete

    def generate_strategies(self) -> Dict[str, str]:
        """Generate pytest commands for each strategy."""
        strategies = {
            ExecutionStrategy.SMOKE.value[0]: (
                "python3 -m pytest tests/unit -m smoke -n auto --tb=line -q"
            ),
            ExecutionStrategy.FAST.value[0]: (
                "python3 -m pytest tests/unit -m 'not slow and not integration' -n auto --tb=line"
            ),
            ExecutionStrategy.STANDARD.value[0]: (
                "python3 -m pytest tests/unit -n auto --dist loadscope"
            ),
            ExecutionStrategy.COMPREHENSIVE.value[0]: (
                "python3 -m pytest tests/ -n auto --dist loadscope"
            ),
            ExecutionStrategy.SERIAL.value[0]: (
                "python3 -m pytest tests/unit -n 0 -x --tb=short"
            ),
            ExecutionStrategy.AC_ONLY.value[0]: (
                "python3 -m pytest tests/ -m ac -v --tb=short"
            ),
            ExecutionStrategy.MCP_ONLY.value[0]: (
                "python3 -m pytest tests/unit/mcp -n auto --dist loadscope"
            ),
            ExecutionStrategy.GOVERNANCE.value[0]: (
                "python3 -m pytest tests/unit/domain_brain -m 'ac or governance' -n auto --tb=short"
            ),
        }
        return strategies

    def run_strategy(self, strategy: str) -> int:
        """Execute tests using specified strategy."""
        strategies = self.generate_strategies()

        if strategy not in strategies:
            print(f"❌ Unknown strategy: {strategy}")
            print(f"Available: {', '.join(strategies.keys())}")
            return 1

        cmd = strategies[strategy]
        strategy_obj = ExecutionStrategy[strategy.upper()]
        print(f"\n{'='*70}")
        print(f"▶️  {strategy_obj.value[1]}")
        print(f"{'='*70}")
        print(f"$ {cmd}\n")

        result = subprocess.run(
            cmd,
            shell=True,
            cwd=str(self.project_root),
        )

        return result.returncode

    def profile_tests(self) -> None:
        """Generate test performance profile."""
        print("\n📊 Generating test performance profile...")

        # Run tests with performance collection
        cmd = (
            "python3 -m pytest tests/unit --tb=no -q "
            "--durations=20 --durations-min=0.1"
        )

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=str(self.project_root),
        )

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

    def print_report(self, metrics: TestMetrics) -> None:
        """Print comprehensive test analysis report."""
        print("\n" + "=" * 70)
        print("📈 TEST SUITE ANALYSIS REPORT")
        print("=" * 70)
        print(f"\n📦 Test Inventory:")
        print(f"  Total Tests Collected:    {metrics.total_tests:,}")
        print(f"  Passed (from last run):   {metrics.passed}")
        print(f"  Failed (from last run):   {metrics.failed}")
        print(f"  Skipped (from last run):  {metrics.skipped}")

        print(f"\n⏱️  Performance Estimates (assuming {metrics.total_tests} tests):")
        print(f"  Serial execution:         {metrics.estimated_serial_time:.1f}s")
        print(f"  Parallel 4x (4 cores):    {metrics.estimated_parallel_4x:.1f}s")
        print(f"  Parallel 8x (8 cores):    {metrics.estimated_parallel_8x:.1f}s")
        print(f"  Expected speedup (4x):    ~{4:.1f}x faster")

        print(f"\n💡 Recommended Strategies:")
        for strategy in ExecutionStrategy:
            print(f"  • {strategy.value[0]:<15} - {strategy.value[1]}")

        print(f"\n🔧 Usage Examples:")
        print(f"  # Run smoke tests (fastest, <30s)")
        print(f"  pytest tests/unit -m smoke -n auto --tb=line -q")
        print(f"")
        print(f"  # Run fast tests (essential only, ~2-3min on 4 cores)")
        print(f"  pytest tests/unit -m 'not slow and not integration' -n auto")
        print(f"")
        print(f"  # Run with full parallelization")
        print(f"  pytest tests/unit -n auto --dist loadscope")
        print(f"")
        print(f"  # Debug single test (serial, verbose)")
        print(f"  pytest tests/unit/some_test.py::TestClass::test_method -n 0 -vv")

    def print_strategies(self) -> None:
        """Print all available execution strategies."""
        print("\n" + "=" * 70)
        print("🎯 TEST EXECUTION STRATEGIES")
        print("=" * 70)

        strategies = self.generate_strategies()
        for i, (name, cmd) in enumerate(strategies.items(), 1):
            strategy_obj = ExecutionStrategy[name.upper()]
            print(f"\n{i}. {strategy_obj.value[0].upper()}: {strategy_obj.value[1]}")
            print(f"   $ {cmd}")


def main():
    """Main entry point."""
    import argparse
from cortex.models.canonical_enums import ExecutionStrategy

    parser = argparse.ArgumentParser(
        description="CORTEX Test Optimization Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze test suite
  %(prog)s analyze --all
  
  # Run smoke tests
  %(prog)s run --strategy smoke
  
  # Profile performance
  %(prog)s profile
  
  # List all strategies
  %(prog)s strategies
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze test suite")
    analyze_parser.add_argument("--all", action="store_true", help="Full analysis")
    analyze_parser.add_argument("--verbose", "-v", action="store_true")

    # Cleanup command
    subparsers.add_parser("cleanup", help="Identify obsolete tests")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run tests with strategy")
    run_parser.add_argument(
        "--strategy",
        choices=[s.value[0] for s in ExecutionStrategy],
        default="standard",
        help="Execution strategy (default: standard)",
    )

    # Profile command
    subparsers.add_parser("profile", help="Profile test performance")

    # Strategies command
    subparsers.add_parser("strategies", help="Show all strategies")

    args = parser.parse_args()
    optimizer = TestOptimizer()

    if args.command == "analyze":
        metrics = optimizer.analyze_test_suite(verbose=args.verbose)
        optimizer.print_report(metrics)
        return 0

    elif args.command == "cleanup":
        obsolete = optimizer.identify_obsolete_tests()
        if obsolete:
            print("\n" + "=" * 70)
            print("🗑️  POTENTIALLY OBSOLETE TESTS")
            print("=" * 70)
            for file, reason in obsolete:
                print(f"  • {file}")
                print(f"    Reason: {reason}")
        else:
            print("✅ No obviously obsolete tests detected")
        return 0

    elif args.command == "run":
        return optimizer.run_strategy(args.strategy)

    elif args.command == "profile":
        optimizer.profile_tests()
        return 0

    elif args.command == "strategies":
        optimizer.print_strategies()
        return 0

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
