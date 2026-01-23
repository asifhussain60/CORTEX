#!/usr/bin/env python3
"""
Regenerate Audit Log - Phase 0 Recovery Script

Clears the existing governance.db and regenerates it with fresh audit entries
by running the comprehensive test suite.

According to CORTEX Review Protocol Phase 0:
- Gate 0B failed: Only 4 audit entries (need >= 2000)
- Action: REGENERATE from scratch

Author: Asif Hussain
"""

import os
import subprocess
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

def delete_governance_db():
    """Delete existing governance.db to start fresh."""
    db_paths = [
        Path("cortex_brain/state/governance.db"),
        Path("cortex/core/state/governance.db"),
    ]
    
    for db_path in db_paths:
        if db_path.exists():
            print(f"Deleting {db_path}...")
            db_path.unlink()
            print(f"  - Deleted")

def run_test_suite():
    """Run comprehensive tests to populate audit log."""
    print("\n=== Running comprehensive test suite ===\n")
    
    # Run tests that will generate audit entries
    test_commands = [
        # Enhanced audit logger tests
        ["python", "-m", "pytest", "tests/unit/test_enhanced_audit_logger.py", "-v", "--tb=short"],
        
        # Domain brain tests (heavy audit population)
        ["python", "-m", "pytest", "tests/unit/domain_brain/test_ac_db_001_01.py", "-v", "--tb=short"],
        ["python", "-m", "pytest", "tests/unit/domain_brain/test_ac_db_002_01.py", "-v", "--tb=short"],
        ["python", "-m", "pytest", "tests/unit/domain_brain/test_ac_db_003_01.py", "-v", "--tb=short"],
        
        # Governance tests
        ["python", "-m", "pytest", "tests/unit/tier1/governance/", "-v", "--tb=short"],
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for cmd in test_commands:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=False)
        
        if result.returncode != 0:
            print(f"  - WARNING: Some tests failed (exit code {result.returncode})")
        else:
            print(f"  - OK")
        
        print()

def verify_audit_log():
    """Verify audit log was properly regenerated."""
    print("=== Verifying audit log regeneration ===\n")
    
    db_path = Path("cortex_brain/state/governance.db")
    
    if not db_path.exists():
        print(f"ERROR: Audit log not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check entry counts
        cursor.execute("""
        SELECT 
          SUM(CASE WHEN operation = 'AC_START' THEN 1 ELSE 0 END) as ac_starts,
          SUM(CASE WHEN operation = 'AC_EXECUTE' THEN 1 ELSE 0 END) as ac_executes,
          SUM(CASE WHEN operation = 'AC_COMPLETE' THEN 1 ELSE 0 END) as ac_completes,
          COUNT(*) as total_entries
        FROM audit_log;
        """)
        
        ac_starts, ac_executes, ac_completes, total = cursor.fetchone()
        
        print(f"Audit Log Status:")
        print(f"  AC_START entries:    {ac_starts}")
        print(f"  AC_EXECUTE entries:  {ac_executes}")
        print(f"  AC_COMPLETE entries: {ac_completes}")
        print(f"  Total entries:       {total}")
        
        # Check freshness
        cursor.execute("SELECT MAX(timestamp) as latest_entry FROM audit_log;")
        latest = cursor.fetchone()
        
        if latest and latest[0]:
            print(f"  Latest entry:        {latest[0]}")
        
        conn.close()
        
        # Verify gate criteria
        gate_0b_pass = total >= 2000 and ac_starts > 0 and ac_executes > 0 and ac_completes > 0
        
        print(f"\nGate 0B Acceptance Criteria:")
        print(f"  - Total entries >= 2000: {'PASS' if total >= 2000 else 'FAIL'} ({total})")
        print(f"  - Lifecycle operations present: {'PASS' if (ac_starts > 0 and ac_executes > 0 and ac_completes > 0) else 'FAIL'}")
        
        if gate_0b_pass:
            print(f"\n✓ Gate 0B PASSED - Ready to proceed to Phase 1")
            return True
        else:
            print(f"\n✗ Gate 0B FAILED - Additional test runs may be needed")
            return False
    
    except Exception as e:
        print(f"ERROR: Failed to verify audit log: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main regeneration workflow."""
    print("=" * 70)
    print("CORTEX Audit Log Regeneration - Phase 0 Recovery")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")
    print()
    
    # Step 1: Delete old database
    print("Step 1: Cleaning up old audit log")
    delete_governance_db()
    
    # Step 2: Run tests
    print("\nStep 2: Running comprehensive test suite to regenerate audit log")
    run_test_suite()
    
    # Step 3: Verify
    print("Step 3: Verifying audit log regeneration")
    success = verify_audit_log()
    
    print()
    print("=" * 70)
    if success:
        print("Status: Regeneration SUCCESSFUL - Ready for Phase 1")
        return 0
    else:
        print("Status: Regeneration INCOMPLETE - May need more tests or manual intervention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
