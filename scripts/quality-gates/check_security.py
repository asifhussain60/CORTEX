#!/usr/bin/env python3
"""
Check security vulnerabilities against quality gate thresholds.

Usage:
    python check_security.py --safety-report safety-report.json --max-severity high
"""

import argparse
import json
import sys
from pathlib import Path


def check_security(safety_report: Path, max_severity: str) -> tuple[bool, str]:
    """Check security vulnerabilities from safety report."""
    if not safety_report.exists():
        return True, "⚠️  Safety report not found, skipping security check"
    
    with open(safety_report) as f:
        report_data = json.load(f)
    
    # Count vulnerabilities by severity
    high_count = 0
    critical_count = 0
    
    for vuln in report_data.get('vulnerabilities', []):
        severity = vuln.get('severity', 'unknown').lower()
        if severity == 'high':
            high_count += 1
        elif severity == 'critical':
            critical_count += 1
    
    messages = []
    messages.append(f"🔒 Security Report:")
    messages.append(f"  Critical vulnerabilities: {critical_count}")
    messages.append(f"  High vulnerabilities: {high_count}")
    
    passed = critical_count == 0 and (max_severity != 'high' or high_count == 0)
    
    if passed:
        messages.append(f"\n✅ Security quality gate: PASSED")
    else:
        messages.append(f"\n❌ Security quality gate: FAILED")
        messages.append(f"   Fix {critical_count + high_count} vulnerabilities")
    
    return passed, "\n".join(messages)


def main():
    parser = argparse.ArgumentParser(description="Check security vulnerabilities")
    parser.add_argument('--safety-report', type=Path, required=True)
    parser.add_argument('--max-severity', type=str, default='high')
    
    args = parser.parse_args()
    
    passed, message = check_security(args.safety_report, args.max_severity)
    print(message)
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
