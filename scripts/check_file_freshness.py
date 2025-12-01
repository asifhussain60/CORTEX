#!/usr/bin/env python3
"""
File Freshness Checker

Validates that critical CORTEX files have been updated within specified timeframe.
Part of Phase 2 Deliverable 2.2 - Key Files Inventory for Planning

Usage:
    python scripts/check_file_freshness.py --days 30
    python scripts/check_file_freshness.py --days 30 --fail-on-stale

Author: Asif Hussain
License: Source-Available (Use Allowed, No Contributions)
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple


# Critical files that must be updated within timeframe
CRITICAL_FILES = [
    "docs/ARCHITECTURE.md",
    "cortex-brain/capabilities.yaml",
    "CHANGELOG.md",
    "VERSION",
]

# Important files (warning only)
IMPORTANT_FILES = [
    "README.md",
    "cortex-brain/operations-config.yaml",
    "cortex-brain/brain-protection-rules.yaml",
    "cortex-brain/response-templates.yaml",
]


def check_file_age(file_path: Path, max_days: int) -> Tuple[bool, int, str]:
    """
    Check if file has been updated within max_days.
    
    Args:
        file_path: Path to file to check
        max_days: Maximum days since last update
    
    Returns:
        Tuple of (is_fresh, days_old, status_message)
    """
    if not file_path.exists():
        return False, -1, "File not found"
    
    try:
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        age = datetime.now() - mtime
        days_old = age.days
        
        if days_old <= max_days:
            return True, days_old, f"✅ Fresh ({days_old} days old)"
        else:
            return False, days_old, f"⚠️  Stale ({days_old} days old, limit: {max_days})"
    
    except Exception as e:
        return False, -1, f"❌ Error: {e}"


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Check file freshness for critical CORTEX files"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Maximum days since last update (default: 30)"
    )
    parser.add_argument(
        "--fail-on-stale",
        action="store_true",
        help="Exit with error code if any critical files are stale"
    )
    parser.add_argument(
        "--cortex-root",
        type=str,
        default=None,
        help="Path to CORTEX root (default: auto-detect)"
    )
    
    args = parser.parse_args()
    
    # Determine CORTEX root
    if args.cortex_root:
        cortex_root = Path(args.cortex_root)
    else:
        cortex_root = Path(__file__).parent.parent
    
    print("🔍 CORTEX File Freshness Check")
    print("=" * 70)
    print(f"Root: {cortex_root}")
    print(f"Max age: {args.days} days")
    print()
    
    # Check critical files
    print("📋 Critical Files (Must be fresh):")
    print("-" * 70)
    
    critical_stale = []
    for file_rel_path in CRITICAL_FILES:
        file_path = cortex_root / file_rel_path
        is_fresh, days_old, status = check_file_age(file_path, args.days)
        
        print(f"  {status:40} {file_rel_path}")
        
        if not is_fresh and file_path.exists():
            critical_stale.append((file_rel_path, days_old))
    
    print()
    
    # Check important files
    print("📌 Important Files (Warning only):")
    print("-" * 70)
    
    important_stale = []
    for file_rel_path in IMPORTANT_FILES:
        file_path = cortex_root / file_rel_path
        is_fresh, days_old, status = check_file_age(file_path, args.days)
        
        print(f"  {status:40} {file_rel_path}")
        
        if not is_fresh and file_path.exists():
            important_stale.append((file_rel_path, days_old))
    
    print()
    print("=" * 70)
    
    # Summary
    if critical_stale:
        print(f"❌ {len(critical_stale)} critical file(s) stale (>{args.days} days):")
        for file_path, days in critical_stale:
            print(f"  - {file_path} ({days} days old)")
        
        if args.fail_on_stale:
            print()
            print("🚨 FAILING: Critical files are stale")
            sys.exit(1)
    else:
        print("✅ All critical files are fresh")
    
    if important_stale:
        print(f"⚠️  {len(important_stale)} important file(s) stale (>{args.days} days):")
        for file_path, days in important_stale:
            print(f"  - {file_path} ({days} days old)")
    else:
        print("✅ All important files are fresh")
    
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
