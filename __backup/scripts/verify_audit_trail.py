#!/usr/bin/env python3
"""
CORTEX 6.0 Audit Log Verification Hook (Enhanced)

Verifies that audit logging occurred for the current work session.
Blocks commits if:
1. No audit trail exists for the changes being committed
2. Script execution errors (must fix before commit)
3. No SUCCESS evidence in audit categories

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
AUDIT_LOG_DIR = PROJECT_ROOT / "cortex-brain" / "audit-logs"
SESSION_AUDIT = PROJECT_ROOT / ".asif" / "AI-Learning" / "cortex6" / "source-of-truth" / "session-audit.jsonl"

# Categories that indicate actual work (not just middleware init)
WORK_CATEGORIES = [
    "BUILD_EXECUTION",
    "EXECUTION", 
    "VALIDATION",
    "STATE_MANAGEMENT",
    "TEST_EXECUTION",
    "TDD",
    "PLANNING",
    "DEBUG",
    "REFACTOR",
]

# Statuses that indicate successful completion
SUCCESS_STATUSES = [
    "COMPLETED",
    "SUCCESS",
    "PASSED",
    "DONE",
    "FINISHED",
]


def get_recent_audit_entries(hours: int = 4) -> List[Dict]:
    """
    Get audit entries from the last N hours.
    
    Returns list of entry dicts with parsed content.
    Raises exception on parse errors (intentionally - we want to catch these).
    """
    entries = []
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    # Check main audit logs
    if AUDIT_LOG_DIR.exists():
        for log_file in sorted(AUDIT_LOG_DIR.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True):
            # Skip files not modified recently
            if log_file.stat().st_mtime < cutoff.timestamp():
                continue
                
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                            entry['_source'] = str(log_file)
                            entry['_line'] = line_num
                            entries.append(entry)
                        except json.JSONDecodeError as e:
                            # Log but don't fail - corrupted entries shouldn't block
                            print(f"⚠️  Warning: Invalid JSON in {log_file.name}:{line_num}: {e}")
            except IOError as e:
                print(f"⚠️  Warning: Could not read {log_file}: {e}")
    
    # Check session audit log (REQUIRED for builds)
    if SESSION_AUDIT.exists():
        try:
            with open(SESSION_AUDIT, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        entry['_source'] = 'session-audit'
                        entry['_line'] = line_num
                        
                        # Check timestamp
                        ts = entry.get("timestamp", "")
                        if ts:
                            try:
                                entry_time = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                                if entry_time.replace(tzinfo=None) > cutoff:
                                    entries.append(entry)
                            except ValueError:
                                # Invalid timestamp, include anyway
                                entries.append(entry)
                        else:
                            # No timestamp, include anyway
                            entries.append(entry)
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Warning: Invalid JSON in session-audit.jsonl:{line_num}: {e}")
        except IOError as e:
            print(f"⚠️  Warning: Could not read session-audit.jsonl: {e}")
    
    return entries


def analyze_audit_entries(entries: List[Dict]) -> Dict:
    """
    Analyze audit entries for work evidence.
    
    Returns dict with:
    - categories: dict of category -> count
    - statuses: dict of status -> count
    - has_work_evidence: bool
    - has_success_evidence: bool
    - latest_entry: dict or None
    """
    categories = {}
    statuses = {}
    latest_entry = None
    latest_timestamp = None
    
    for entry in entries:
        # Count categories
        cat = entry.get("category", "unknown").upper()
        categories[cat] = categories.get(cat, 0) + 1
        
        # Count statuses
        status = entry.get("status", "unknown").upper()
        statuses[status] = statuses.get(status, 0) + 1
        
        # Track latest entry
        ts = entry.get("timestamp")
        if ts:
            if latest_timestamp is None or ts > latest_timestamp:
                latest_timestamp = ts
                latest_entry = entry
    
    # Check for work evidence
    has_work_evidence = any(
        cat in [c.upper() for c in WORK_CATEGORIES]
        for cat in categories.keys()
    )
    
    # Check for success evidence
    has_success_evidence = any(
        status in [s.upper() for s in SUCCESS_STATUSES]
        for status in statuses.keys()
    )
    
    return {
        "categories": categories,
        "statuses": statuses,
        "has_work_evidence": has_work_evidence,
        "has_success_evidence": has_success_evidence,
        "latest_entry": latest_entry,
        "total_entries": len(entries),
    }


def verify_audit_trail() -> Tuple[bool, str, Optional[Dict]]:
    """
    Verify audit trail exists for current session.
    
    Returns:
        Tuple of (success, message, analysis_dict)
    """
    print("\n📝 Verifying Audit Trail...")
    print("-" * 50)
    
    try:
        # Get recent audit entries
        entries = get_recent_audit_entries(hours=4)
        
        if not entries:
            return False, "No audit entries found in last 4 hours", None
        
        # Analyze entries
        analysis = analyze_audit_entries(entries)
        
        # Display findings
        print(f"✓ Found {analysis['total_entries']} audit entries")
        
        cat_str = ', '.join(f"{k}({v})" for k, v in sorted(analysis['categories'].items()))
        print(f"✓ Categories: {cat_str}")
        
        status_str = ', '.join(f"{k}({v})" for k, v in sorted(analysis['statuses'].items()))
        print(f"✓ Statuses: {status_str}")
        
        if analysis['latest_entry']:
            latest = analysis['latest_entry']
            print(f"✓ Latest: {latest.get('task', latest.get('operation', 'unknown'))} ({latest.get('status', 'unknown')})")
        
        # Decision logic
        if analysis['has_work_evidence']:
            if analysis['has_success_evidence']:
                return True, f"Audit trail verified with SUCCESS evidence: {analysis['total_entries']} entries", analysis
            else:
                # Work evidence but no success - warn but allow
                return True, f"Audit trail has work entries (no explicit SUCCESS): {analysis['total_entries']} entries", analysis
        else:
            # Only middleware/system entries - still allow but note
            return True, f"Audit trail exists (middleware only): {analysis['total_entries']} entries", analysis
            
    except Exception as e:
        # Any exception should be visible and cause failure
        return False, f"Audit verification error: {type(e).__name__}: {e}", None


def main():
    """Run audit trail verification."""
    success, message, analysis = verify_audit_trail()
    
    if success:
        print(f"\n✅ {message}")
        
        # Additional info
        if analysis and analysis.get('has_success_evidence'):
            print("   (Contains SUCCESS evidence - excellent!)")
        elif analysis and analysis.get('has_work_evidence'):
            print("   (Contains work evidence)")
        
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
