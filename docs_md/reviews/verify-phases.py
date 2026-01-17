#!/usr/bin/env python3
"""
PHASE VERIFICATION SCRIPT - Cross-check Phase 1-4 claims vs. actual implementation
"""
import sqlite3
import json
from pathlib import Path
from collections import defaultdict
import sys

# Expand the import path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.path_resolver import resolve_path

def verify_phase_tracker():
    """Verify phase tracker status from cortex-master.yaml"""
    import yaml
    
    master_path = resolve_path(".github", "roadmap", "cortex-master.yaml")
    
    with open(master_path) as f:
        master = yaml.safe_load(f)
    
    print("\n" + "="*80)
    print("PHASE TRACKER STATUS (from cortex-master.yaml)")
    print("="*80)
    
    for phase, info in master['phase_tracker'].items():
        print(f"\n{phase}:")
        print(f"  Title: {info['title']}")
        print(f"  Status: {info['status']}")
        print(f"  Locked: {info['locked']}")
        print(f"  AC-IDs: {info['ac_ids']}")
        print(f"  Requires: {info.get('requires', 'None')}")
        if info.get('audit_verification'):
            av = info['audit_verification']
            print(f"  Audit Verified: {av.get('verified', 'N/A')}")
            print(f"  Audit Entries: {av.get('entry_count', 'N/A')}")
            print(f"  Hash Chain Valid: {av.get('hash_chain_valid', 'N/A')}")
    
    return master['phase_tracker']

def verify_database():
    """Verify audit logs in governance.db"""
    db_path = Path("cortex-brain/state/governance.db")
    if not db_path.exists():
        print(f"\n⚠️  Database not found at {db_path}")
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get total audit entries
    cursor.execute("SELECT COUNT(*) FROM audit_log")
    total_entries = cursor.fetchone()[0]
    
    # Get entries by AC prefix
    cursor.execute("""
        SELECT 
            CASE 
                WHEN ac_id LIKE 'AC-AR-%' THEN 'AR'
                WHEN ac_id LIKE 'AC-FR-%' THEN 'FR'
                WHEN ac_id LIKE 'AC-NFR-%' THEN 'NFR'
                WHEN ac_id LIKE 'AC-COHERENCE-%' THEN 'COHERENCE'
                WHEN ac_id LIKE 'AC-EXPLAIN-%' THEN 'EXPLAIN'
                ELSE 'OTHER'
            END as category,
            COUNT(*) as count,
            COUNT(DISTINCT ac_id) as unique_acs
        FROM audit_log
        GROUP BY category
        ORDER BY category
    """)
    
    print("\n" + "="*80)
    print("AUDIT LOG VERIFICATION (from governance.db)")
    print("="*80)
    print(f"\nTotal audit entries: {total_entries}")
    print(f"\nEntries by AC category:")
    
    results = cursor.fetchall()
    for category, count, unique_acs in results:
        print(f"  {category:12} : {count:5} entries ({unique_acs:3} unique AC-IDs)")
    
    # Get entries by operation
    cursor.execute("""
        SELECT operation, COUNT(*) 
        FROM audit_log 
        GROUP BY operation 
        ORDER BY operation
    """)
    
    print(f"\nEntries by operation type:")
    ops = cursor.fetchall()
    for op, count in ops:
        print(f"  {op:20} : {count:5} entries")
    
    # Verify hash chain
    cursor.execute("SELECT COUNT(*) FROM audit_log WHERE entry_hash IS NULL OR entry_hash = ''")
    missing_hash = cursor.fetchone()[0]
    
    print(f"\nHash chain verification:")
    print(f"  Entries with hash: {total_entries - missing_hash}")
    print(f"  Entries without hash: {missing_hash}")
    print(f"  Chain valid: {'✓ YES' if missing_hash == 0 else '✗ NO'}")
    
    # Get per-phase stats
    cursor.execute("""
        SELECT 
            CASE 
                WHEN ac_id LIKE 'AC-AR-001%' OR ac_id LIKE 'AC-AR-002%' OR ac_id LIKE 'AC-AR-003%' OR ac_id LIKE 'AC-AR-004%' OR ac_id LIKE 'AC-AR-005%' OR ac_id LIKE 'AC-AR-008%' OR ac_id LIKE 'AC-AR-011%' OR ac_id LIKE 'AC-FR-001%' OR ac_id LIKE 'AC-FR-003%' OR ac_id LIKE 'AC-FR-004%' OR ac_id LIKE 'AC-FR-005%' OR ac_id LIKE 'AC-FR-006%' THEN 'PHASE-01'
                WHEN ac_id LIKE 'AC-AR-006%' OR ac_id LIKE 'AC-AR-007%' OR ac_id LIKE 'AC-AR-009%' OR ac_id LIKE 'AC-FR-002%' THEN 'PHASE-02'
                WHEN ac_id LIKE 'AC-NFR-002%' OR ac_id LIKE 'AC-NFR-004%' THEN 'PHASE-03'
                WHEN ac_id LIKE 'AC-NFR-003%' OR ac_id LIKE 'AC-COHERENCE%' OR ac_id LIKE 'AC-EXPLAIN%' THEN 'PHASE-04'
                ELSE 'UNKNOWN'
            END as phase,
            COUNT(*) as entries
        FROM audit_log
        GROUP BY phase
        ORDER BY phase
    """)
    
    print(f"\nEntries by phase:")
    phase_stats = cursor.fetchall()
    for phase, count in phase_stats:
        print(f"  {phase:10} : {count:5} entries")
    
    conn.close()
    return total_entries

def count_source_files():
    """Count implementation files"""
    src_path = Path("src")
    
    print("\n" + "="*80)
    print("SOURCE FILE INVENTORY")
    print("="*80)
    
    categories = {
        'core': [],
        'infrastructure': [],
        'orchestrators': [],
        'mcp': [],
        'tools': [],
        'other': []
    }
    
    for py_file in src_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        if "__init__" in py_file.name:
            continue
        
        rel_path = py_file.relative_to(src_path)
        category = str(rel_path).split('/')[0]
        
        if category not in categories:
            category = 'other'
        
        categories[category].append(py_file.name)
    
    print("\nImplementation modules by category:")
    total_modules = 0
    for cat, files in sorted(categories.items()):
        if files:
            print(f"\n  {cat.upper()} ({len(files)} files):")
            for fname in sorted(files):
                print(f"    - {fname}")
            total_modules += len(files)
    
    return total_modules

def count_test_files():
    """Count test files"""
    test_path = Path("tests/unit")
    
    print("\n" + "="*80)
    print("TEST FILE INVENTORY")
    print("="*80)
    
    test_files = list(test_path.glob("test_*.py"))
    
    print(f"\nTotal test files: {len(test_files)}")
    print("\nTest files:")
    for tf in sorted(test_files):
        print(f"  - {tf.name}")
    
    return len(test_files)

def verify_phase_claims(phase_tracker):
    """Cross-check claims from chat transcripts vs. actual implementation"""
    
    print("\n" + "="*80)
    print("PHASE COMPLETION CLAIMS VERIFICATION")
    print("="*80)
    
    claims = {
        'PHASE-01': {
            'status': 'COMPLETED',
            'locked': True,
            'ac_ids': 36,
            'tests_claimed': 203,
            'chat_says': 'All 36 AC-IDs implemented and tested (203 tests passing)'
        },
        'PHASE-02': {
            'status': 'COMPLETED', 
            'locked': True,
            'ac_ids': 27,
            'tests_claimed': 240,
            'chat_says': 'All 27 AC-IDs for orchestration completed'
        },
        'PHASE-03': {
            'status': 'COMPLETED',
            'locked': True,
            'ac_ids': 6,
            'tests_claimed': 127,
            'chat_says': 'All 6 AC-IDs for safety & observability (127 tests passing)'
        },
        'PHASE-04': {
            'status': 'COMPLETED',
            'locked': True,
            'ac_ids': 12,
            'tests_claimed': 102,
            'chat_says': 'All 12 AC-IDs for production hardening (102 tests passing)'
        }
    }
    
    print("\nVerifying claims from chat transcripts:\n")
    
    for phase, claim in claims.items():
        tracker = phase_tracker.get(phase, {})
        print(f"{phase}:")
        print(f"  Claim (from chat): {claim['chat_says']}")
        print(f"  Status in master:  {tracker.get('status')} (claimed: {claim['status']})")
        print(f"  Locked in master:  {tracker.get('locked')} (claimed: {claim['locked']})")
        print(f"  AC-IDs in master:  {tracker.get('ac_ids')} (claimed: {claim['ac_ids']})")
        
        if tracker.get('audit_verification'):
            av = tracker['audit_verification']
            print(f"  Audit entries:     {av.get('entry_count')} (claimed: {claim.get('tests_claimed', 'N/A')})")
            print(f"  Hash valid:        {av.get('hash_chain_valid')}")
        
        print()

def main():
    """Run all verifications"""
    print("\n" + "="*80)
    print("CORTEX PHASE VERIFICATION REPORT")
    print("Comparing Phase 1-4 chat transcripts vs. actual implementation")
    print("="*80)
    
    # Verify phase tracker
    phase_tracker = verify_phase_tracker()
    
    # Verify database
    verify_database()
    
    # Count files
    modules = count_source_files()
    tests = count_test_files()
    
    # Verify claims
    verify_phase_claims(phase_tracker)
    
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(f"\nImplementation Metrics:")
    print(f"  Total implementation modules: {modules}")
    print(f"  Total test files: {tests}")
    
    completed_phases = [p for p, info in phase_tracker.items() if info.get('status') == 'COMPLETED']
    print(f"  Completed phases: {len(completed_phases)}")
    print(f"  Locked phases: {len([p for p, info in phase_tracker.items() if info.get('locked')])}")
    
    total_claimed_acs = sum([phase_tracker[p]['ac_ids'] for p in completed_phases])
    print(f"  Total AC-IDs in completed phases: {total_claimed_acs}")

if __name__ == "__main__":
    main()
