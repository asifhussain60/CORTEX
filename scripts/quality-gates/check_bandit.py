#!/usr/bin/env python3
"""
Check bandit security scan results against quality gate thresholds.

Usage:
    python check_bandit.py --report bandit-report.json --max-high 0 --max-critical 0
"""

import argparse
import json
import sys
from pathlib import Path


def check_bandit(report_path: Path, max_high: int, max_critical: int) -> tuple[bool, str]:
    """Check bandit scan results."""
    if not report_path.exists():
        return True, "⚠️  Bandit report not found, skipping check"
    
    with open(report_path) as f:
        report_data = json.load(f)
    
    metrics = report_data.get('metrics', {}).get('_totals', {})
    high_count = metrics.get('SEVERITY.HIGH', 0)
    critical_count = metrics.get('SEVERITY.CRITICAL', 0)
    
    messages = []
    messages.append(f"🔒 Bandit Security Scan:")
    messages.append(f"  Critical issues: {critical_count} (max: {max_critical})")
    messages.append(f"  High issues: {high_count} (max: {max_high})")
    
    passed = critical_count <= max_critical and high_count <= max_high
    
    if passed:
        messages.append(f"\n✅ Bandit security gate: PASSED")
    else:
        messages.append(f"\n❌ Bandit security gate: FAILED")
    
    return passed, "\n".join(messages)


def main():
    parser = argparse.ArgumentParser(description="Check bandit results")
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--max-high', type=int, default=0)
    parser.add_argument('--max-critical', type=int, default=0)
    
    args = parser.parse_args()
    
    passed, message = check_bandit(args.report, args.max_high, args.max_critical)
    print(message)
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
