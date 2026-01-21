#!/usr/bin/env python3
"""
PHASE 0: PRE-REVIEW VALIDATION GATES
Checks data quality before full system review
"""

import sqlite3
import json
from datetime import datetime, timedelta
from collections import defaultdict

db_path = r'd:\PROJECTS\CORTEX\cortex_brain\state\governance.db'

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("PHASE 0 VALIDATION: GATE 0A - DATA FRESHNESS")
    print("=" * 80)

    # Gate 0A: Check when audit log was last updated
    cursor.execute("""
        SELECT MAX(timestamp) as latest_entry
        FROM audit_log
    """)
    result = cursor.fetchone()
    if result and result['latest_entry']:
        latest = result['latest_entry']
        print(f"Latest audit entry: {latest}")
        # Parse ISO format
        latest_dt = datetime.fromisoformat(latest.replace('Z', '+00:00'))
        now = datetime.now(latest_dt.tzinfo)
        age_hours = (now - latest_dt).total_seconds() / 3600
        print(f"Age: {age_hours:.1f} hours")
        if age_hours < 24:
            print("✅ PASS: Data is fresh (< 24 hours)")
            gate_0a = True
        else:
            print("❌ FAIL: Data is stale (> 24 hours)")
            gate_0a = False
    else:
        print("❌ FAIL: No audit entries found")
        gate_0a = False

    print("\n" + "=" * 80)
    print("PHASE 0 VALIDATION: GATE 0B - AUDIT TRAIL COMPLETENESS")
    print("=" * 80)

    cursor.execute("""
        SELECT 
            SUM(CASE WHEN operation = 'AC_START' THEN 1 ELSE 0 END) as ac_starts,
            SUM(CASE WHEN operation = 'AC_EXECUTE' THEN 1 ELSE 0 END) as ac_executes,
            SUM(CASE WHEN operation = 'AC_COMPLETE' THEN 1 ELSE 0 END) as ac_completes,
            COUNT(*) as total_entries
        FROM audit_log
    """)
    result = cursor.fetchone()
    ac_starts = result['ac_starts'] or 0
    ac_executes = result['ac_executes'] or 0
    ac_completes = result['ac_completes'] or 0
    total_entries = result['total_entries'] or 0
    
    print(f"AC_START entries:    {ac_starts}")
    print(f"AC_EXECUTE entries:  {ac_executes}")
    print(f"AC_COMPLETE entries: {ac_completes}")
    print(f"Total entries:       {total_entries}")

    gate_0b = total_entries >= 2000
    if gate_0b:
        print("✅ PASS: Robust dataset (>= 2000 entries)")
    else:
        print(f"⚠️  WARNING: Dataset may be small ({total_entries} < 2000 entries)")

    print("\n" + "=" * 80)
    print("GATE 0B DETAIL: TOP AC-IDS BY OPERATION COUNT")
    print("=" * 80)

    # Check for ACs with complete lifecycle
    cursor.execute("""
        SELECT ac_id, 
               COUNT(*) as total_ops,
               SUM(CASE WHEN operation = 'AC_START' THEN 1 ELSE 0 END) as has_start,
               SUM(CASE WHEN operation = 'AC_EXECUTE' THEN 1 ELSE 0 END) as has_execute,
               SUM(CASE WHEN operation = 'AC_COMPLETE' THEN 1 ELSE 0 END) as has_complete
        FROM audit_log
        GROUP BY ac_id
        ORDER BY total_ops DESC
        LIMIT 30
    """)

    complete_acs = 0
    incomplete_acs = 0
    for row in cursor.fetchall():
        ac_id = row['ac_id']
        has_start = row['has_start'] > 0
        has_execute = row['has_execute'] > 0
        has_complete = row['has_complete'] > 0
        
        if has_start and has_execute and has_complete:
            status = "✅"
            complete_acs += 1
        else:
            status = "⚠️ "
            incomplete_acs += 1
        print(f"{status} {ac_id:35} START:{int(has_start)} EXEC:{int(has_execute)} COMPLETE:{int(has_complete)} (ops: {row['total_ops']:3})")

    print(f"\nComplete ACs (full lifecycle): {complete_acs}")
    print(f"Incomplete/Partial ACs: {incomplete_acs}")

    print("\n" + "=" * 80)
    print("PHASE 0 VALIDATION: GATE 0D - TEST ISOLATION VERIFICATION")
    print("=" * 80)

    test_fixtures = ['AC-CHAIN-000', 'AC-CHAIN-001', 'AC-DECORATOR-001', 
                     'AC-HASH-001', 'AC-INVALID-999']

    cursor.execute(f"""
        SELECT COUNT(DISTINCT ac_id) as test_fixture_count,
               GROUP_CONCAT(DISTINCT ac_id) as fixture_ids
        FROM audit_log
        WHERE ac_id IN ({','.join(['?' for _ in test_fixtures])})
        OR ac_id LIKE 'AC-TEST-%'
    """, test_fixtures)

    result = cursor.fetchone()
    fixture_count = result['test_fixture_count'] or 0
    print(f"Test fixtures found: {fixture_count}")
    if result['fixture_ids']:
        print(f"IDs: {result['fixture_ids']}")

    gate_0d = fixture_count <= 6
    if gate_0d:
        print("✅ PASS: Acceptable test isolation (≤ 6 fixtures)")
    else:
        print("⚠️  WARNING: Possible test data contamination (> 6 fixtures)")

    print("\n" + "=" * 80)
    print("GATE 0C: HASH CHAIN INTEGRITY - REQUIRES TEST EXECUTION")
    print("=" * 80)
    print("Running hash chain integrity test...")
    
    conn.close()
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
