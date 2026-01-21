"""Hanging Test Detection - Analyze test_audit_trail.log for slow/hanging tests.

Usage:
    python scripts/detect_hanging_tests.py
    python scripts/detect_hanging_tests.py --threshold 5.0
    python scripts/detect_hanging_tests.py --top 10
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class SlowTest:
    """Slow test data."""
    duration: float
    status: str
    test_id: str
    
    def __str__(self) -> str:
        return f"{self.duration:7.3f}s | {self.status:8s} | {self.test_id}"


def parse_audit_log(log_path: Path) -> List[SlowTest]:
    """Parse test audit log for slow tests.
    
    Args:
        log_path: Path to test_audit_trail.log
        
    Returns:
        List of SlowTest instances.
    """
    slow_tests = []
    
    if not log_path.exists():
        print(f"⚠️  Log file not found: {log_path}")
        return slow_tests
    
    # Pattern: duration:7.3f}s | {status} | {test_id}
    pattern = r'(\d+\.\d+)s \| (PASSED|FAILED|SKIPPED|ERROR) \| (.+)'
    
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                duration = float(match.group(1))
                status = match.group(2)
                test_id = match.group(3).strip()
                slow_tests.append(SlowTest(duration, status, test_id))
    
    return slow_tests


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Detect hanging/slow tests")
    parser.add_argument("--threshold", type=float, default=3.0,
                        help="Duration threshold in seconds (default: 3.0)")
    parser.add_argument("--top", type=int, default=20,
                        help="Show top N slowest tests (default: 20)")
    parser.add_argument("--log", type=str, default=None,
                        help="Path to test_audit_trail.log")
    
    args = parser.parse_args()
    
    # Find log file
    if args.log:
        log_path = Path(args.log)
    else:
        log_path = Path(__file__).parent.parent / "cortex" / "test_audit_trail.log"
    
    # Parse log
    slow_tests = parse_audit_log(log_path)
    
    if not slow_tests:
        print("No test execution data found.")
        return 0
    
    # Filter by threshold
    hanging = [t for t in slow_tests if t.duration >= args.threshold]
    
    # Sort by duration
    hanging_sorted = sorted(hanging, key=lambda x: x.duration, reverse=True)
    
    # Display results
    print(f"\n{'='*80}")
    print(f"HANGING/SLOW TEST DETECTION REPORT")
    print(f"{'='*80}")
    print(f"Threshold: {args.threshold}s")
    print(f"Total tests analyzed: {len(slow_tests)}")
    print(f"Tests exceeding threshold: {len(hanging)}")
    print(f"\nTop {min(args.top, len(hanging_sorted))} slowest tests:\n")
    
    for test in hanging_sorted[:args.top]:
        print(f"  {test}")
    
    print(f"\n{'='*80}\n")
    
    # Return exit code based on hanging tests
    return 1 if len(hanging) > 0 else 0


if __name__ == "__main__":
    sys.exit(main())