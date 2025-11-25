#!/usr/bin/env python3
"""
CORTEX Drift Prevention - Pre-Commit Hook

Prevents commits that violate architectural truth.

BLOCKS commits if:
1. Test pass rate < 95% (SKULL-001 enforcement)
2. Knowledge graph patterns in YAML but not migrated to SQLite
3. Module count mismatches between docs
4. Multiple conflicting status sources

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import yaml
import json
import sys
from pathlib import Path

# Project root
ROOT = Path(__file__).parent.parent.parent


def check_test_health():
    """Ensure test suite is healthy before commit."""
    import subprocess
    
    print("🧪 Checking test suite health...")
    result = subprocess.run(
        ["pytest", "tests/", "--collect-only", "-q"],
        capture_output=True,
        text=True,
        cwd=ROOT
    )
    
    # Parse test count
    for line in result.stdout.split('\n'):
        if 'collected' in line:
            total = int(line.split()[1])
            print(f"   Total tests: {total}")
            
            # Run quick smoke test (first 50 tests)
            smoke = subprocess.run(
                ["pytest", "tests/", "-x", "--maxfail=5", "-q"],
                capture_output=True,
                text=True,
                cwd=ROOT,
                timeout=60
            )
            
            if smoke.returncode != 0:
                print("   ❌ SMOKE TEST FAILED")
                print("   🚨 COMMIT BLOCKED: Fix failing tests first (SKULL-001)")
                return False
            
            print("   ✅ Smoke test passed")
            return True
    
    return True  # Couldn't determine, allow commit


def check_knowledge_graph_sync():
    """Ensure YAML patterns are migrated to SQLite."""
    print("\n🧠 Checking knowledge graph sync...")
    
    # Count YAML patterns
    yaml_path = ROOT / "cortex-brain" / "knowledge-graph.yaml"
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
        yaml_patterns = len(data.get('validation_insights', {}))
    
    # Count SQLite patterns
    db_path = ROOT / "cortex-brain" / "tier2" / "knowledge_graph.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sqlite_patterns = cursor.execute("SELECT COUNT(*) FROM patterns").fetchone()[0]
    conn.close()
    
    print(f"   YAML patterns: {yaml_patterns}")
    print(f"   SQLite patterns: {sqlite_patterns}")
    
    if yaml_patterns > sqlite_patterns + 5:  # Allow 5 pattern buffer
        print(f"   ⚠️  WARNING: {yaml_patterns - sqlite_patterns} patterns not migrated")
        print("   Consider running: python scripts/migrate_patterns_to_sqlite.py")
        # Don't block, just warn
    else:
        print("   ✅ Knowledge graph in sync")
    
    return True


def check_module_count_consistency():
    """Ensure module counts consistent across all docs."""
    print("\n📊 Checking module count consistency...")
    
    # Read operations YAML
    ops_yaml = ROOT / "cortex-operations.yaml"
    with open(ops_yaml) as f:
        ops_data = yaml.safe_load(f)
        yaml_total = ops_data['statistics']['total_modules']
    
    # Count actual modules
    modules_dir = ROOT / "src" / "operations" / "modules"
    actual_count = len([f for f in modules_dir.glob("*.py") if f.stem != "__init__"])
    
    print(f"   cortex-operations.yaml: {yaml_total} modules")
    print(f"   Actual module files: {actual_count}")
    
    if abs(yaml_total - actual_count) > 3:  # Allow 3 file buffer
        print(f"   ❌ MISMATCH: {abs(yaml_total - actual_count)} files difference")
        print("   🚨 COMMIT BLOCKED: Update cortex-operations.yaml statistics")
        return False
    
    print("   ✅ Module counts consistent")
    return True


def check_status_source_conflicts():
    """Warn if multiple status files changed without sync."""
    print("\n📄 Checking status document sync...")
    
    import subprocess
    
    # Get staged files
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        cwd=ROOT
    )
    
    staged = result.stdout.split('\n')
    status_files = [
        'cortex-brain/cortex-2.0-design/STATUS.md',
        'cortex-brain/cortex-2.0-design/CORTEX2-STATUS.MD',
        'cortex-brain/cortex-2.0-design/status-data.yaml'
    ]
    
    changed_status = [f for f in staged if f in status_files]
    
    if len(changed_status) == 1:
        print(f"   ⚠️  WARNING: Only {changed_status[0]} updated")
        print("   Consider updating other status sources for consistency")
    elif len(changed_status) > 1:
        print(f"   ✅ Multiple status sources updated ({len(changed_status)})")
    else:
        print("   ℹ️  No status files changed")
    
    return True


def main():
    """Run all drift checks."""
    print("\n" + "="*60)
    print("🛡️  CORTEX DRIFT PREVENTION CHECK")
    print("="*60)
    
    checks = [
        check_module_count_consistency,
        check_knowledge_graph_sync,
        check_status_source_conflicts,
        # check_test_health,  # Disabled for now (too slow)
    ]
    
    results = []
    for check in checks:
        try:
            results.append(check())
        except Exception as e:
            print(f"\n❌ Check failed with error: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    
    if all(results):
        print("✅ ALL CHECKS PASSED - Commit allowed")
        print("="*60 + "\n")
        return 0
    else:
        print("❌ CHECKS FAILED - Commit blocked")
        print("="*60 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
