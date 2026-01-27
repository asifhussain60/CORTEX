#!/usr/bin/env python3
"""
CORTEX Health Check Command

Usage:
    cortex-health-check              # Run basic health check
    cortex-health-check --verbose    # Detailed output
    cortex-health-check --remediate  # Auto-fix issues
    cortex-health-check --reset      # Clear cache, force full re-check

Exit codes:
    0  - ✅ System healthy
    1  - ⚠️  Warnings detected (non-blocking)
    2  - ❌ Critical issues detected
    3  - 🔧 Issues auto-remediated

AC-PERMANENT-FIX-015: Provide user-facing health check command
for quick validation and auto-remediation.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from cortex.infrastructure.startup_validator import (
    get_startup_validator,
    StartupValidationStatus,
)


def main():
    """Main entry point for health check command."""
    parser = argparse.ArgumentParser(
        description="CORTEX System Health Check",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cortex-health-check              # Quick health check
  cortex-health-check --verbose    # Detailed diagnostics
  cortex-health-check --remediate  # Auto-fix detected issues
  cortex-health-check --reset      # Force full re-check
        """,
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed diagnostics"
    )
    parser.add_argument(
        "--remediate", "-r",
        action="store_true",
        help="Automatically fix detected issues"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear cache and force full re-check"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Reset cache if requested
    if args.reset:
        validator = get_startup_validator()
        try:
            if validator.cache_file.exists():
                validator.cache_file.unlink()
            if validator.cache_dir.exists():
                validator.cache_dir.rmdir()
            print("✅ Cache cleared, running full re-check...")
        except Exception as e:
            print(f"⚠️  Failed to clear cache: {e}")

    # Run validation
    validator = get_startup_validator()
    result = validator.validate_and_remediate()

    # Handle results
    if result.is_err():
        error_msg = result.error
        if args.json:
            print(json.dumps({"status": "error", "message": error_msg}))
        else:
            print(f"❌ Validation error: {error_msg}")
        return 2

    if result.is_ok():
        status: StartupValidationStatus = result.unwrap()

        if args.json:
            print(json.dumps({
                "status": "healthy" if status.is_healthy else "unhealthy",
                "timestamp": status.timestamp,
                "critical_issues": status.critical_issues,
                "auto_remediated": status.auto_remediated_issues,
                "warnings": status.warnings,
                "duration_ms": status.validation_duration_ms,
            }))
        else:
            # Format text output
            print_health_report(status, args.verbose)

        # Determine exit code
        if status.is_healthy:
            if status.auto_remediated_issues:
                return 3  # Issues auto-remediated
            return 0  # Fully healthy
        else:
            return 2  # Critical issues


def print_health_report(
    status: StartupValidationStatus,
    verbose: bool = False
) -> None:
    """Print formatted health report."""
    # Header
    health_icon = "✅" if status.is_healthy else "❌"
    print(f"\n{health_icon} CORTEX System Health Report")
    print(f"   Timestamp: {status.timestamp}")
    print(f"   Duration:  {status.validation_duration_ms:.1f}ms\n")

    # Critical issues
    if status.critical_issues:
        print(f"🔴 CRITICAL ISSUES ({len(status.critical_issues)}):")
        for i, issue in enumerate(status.critical_issues, 1):
            print(f"   {i}. {issue}")
        print()

    # Auto-remediated
    if status.auto_remediated_issues:
        print(f"🔧 AUTO-REMEDIATED ({len(status.auto_remediated_issues)}):")
        if verbose:
            for i, item in enumerate(status.auto_remediated_issues, 1):
                print(f"   {i}. {item}")
        else:
            print(f"   {len(status.auto_remediated_issues)} issues automatically fixed")
        print()

    # Warnings
    if status.warnings:
        print(f"⚠️  WARNINGS ({len(status.warnings)}):")
        for i, warning in enumerate(status.warnings, 1):
            print(f"   {i}. {warning}")
        print()

    # Summary
    if status.is_healthy:
        print("✅ System is healthy and ready for use!")
    else:
        print(f"❌ System has {len(status.critical_issues)} blocking issue(s)")
        print("   Run: cortex-health-check --remediate")

    print()


if __name__ == "__main__":
    sys.exit(main())
