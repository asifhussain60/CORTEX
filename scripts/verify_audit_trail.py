#!/usr/bin/env python3
"""
CORTEX 6.0 Audit Log Verification Hook

Verifies that audit logging occurred for the current work session.
Blocks commits if no audit trail exists for the changes being committed.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
AUDIT_LOG_DIR = PROJECT_ROOT / "cortex-brain" / "audit-logs"
SESSION_AUDIT = PROJECT_ROOT / ".asif" / "AI-Learning" / "cortex6" / "source-of-truth" / "session-audit.jsonl"


def get_recent_audit_entries(hours: int = 4) -> List[dict]:
    """Get audit entries from the last N hours."""
    entries = []
    cutoff = datetime.now() - timedelta(hours=hours)
    
    # Check main audit logs
    if AUDIT_LOG_DIR.exists():
        for log_file in AUDIT_LOG_DIR.glob("*.jsonl"):
            if log_file.stat().st_mtime > cutoff.timestamp():
                try:
                    with open(log_file) as f:
                        for line in f:
                            if line.strip():
                                entry = json.loads(line)
                                entries.append(entry)
                except (json.JSONDecodeError, IOError):
                    pass
    
    # Check session audit log
    if SESSION_AUDIT.exists():
        try:
            with open(SESSION_AUDIT) as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        # Check timestamp
                        entry_time = datetime.fromisoformat(entry.get("timestamp", "2000-01-01"))
                        if entry_time > cutoff:
                            entries.append(entry)
        except (json.JSONDecodeError, IOError):
            pass
    
    return entries


def verify_audit_trail() -> Tuple[bool, str]:
    """
    Verify audit trail exists for current session.
    
    Returns:
        Tuple of (success, message)
    """
    print("\n📝 Verifying Audit Trail...")
    print("-" * 50)
    
    # Get recent audit entries
    entries = get_recent_audit_entries(hours=4)
    
    if not entries:
        return False, "No audit entries found in last 4 hours. Run your work through CORTEX orchestrators or use session audit logging."
    
    # Categorize entries
    categories = {}
    for entry in entries:
        cat = entry.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"✓ Found {len(entries)} audit entries")
    print(f"✓ Categories: {', '.join(f'{k}({v})' for k, v in categories.items())}")
    
    # Check for execution/validation entries (indicates actual work)
    work_categories = ["EXECUTION", "VALIDATION", "BUILD_EXECUTION", "STATE_MANAGEMENT"]
    has_work_entries = any(cat.upper() in [c.upper() for c in categories.keys()] for cat in work_categories)
    
    if not has_work_entries:
        # Check session audit specifically
        if SESSION_AUDIT.exists():
            with open(SESSION_AUDIT) as f:
                session_entries = [json.loads(l) for l in f if l.strip()]
            if session_entries:
                print(f"✓ Session audit has {len(session_entries)} entries")
                has_work_entries = True
    
    if has_work_entries:
        return True, f"Audit trail verified: {len(entries)} entries across {len(categories)} categories"
    else:
        return True, f"Audit trail exists (middleware only) - {len(entries)} entries"  # Allow middleware-only


def main():
    """Run audit trail verification."""
    success, message = verify_audit_trail()
    
    if success:
        print(f"\n✅ {message}")
        sys.exit(0)
    else:
        print(f"\n❌ AUDIT VERIFICATION FAILED")
        print(f"   {message}")
        print("\n💡 To generate audit entries:")
        print("   1. Run: python3 .asif/AI-Learning/cortex6/source-of-truth/update_session.py --log 'your message'")
        print("   2. Or use CORTEX orchestrators which auto-log")
        print("\n⚠️  To bypass (EMERGENCY ONLY): git commit --no-verify")
        sys.exit(1)


if __name__ == "__main__":
    main()
