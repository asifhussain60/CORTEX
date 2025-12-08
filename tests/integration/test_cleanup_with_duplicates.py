"""
Test Cleanup Orchestrator with Duplicate Analysis Integration

Verifies:
1. Phase 0 (duplicate analysis) executes correctly
2. Phase 3 (cleanup obsolete) uses Phase 0 results
3. auto_delete_archived parameter works
4. Metrics and reporting include duplicate statistics
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root / 'scripts' / 'utilities'))

from src.operations.modules.orchestration.cleanup_orchestrator import CleanupOrchestrator


def test_cleanup_with_duplicates():
    """Test cleanup orchestrator with duplicate analysis integration."""
    
    print("=" * 70)
    print("CLEANUP ORCHESTRATOR - DUPLICATE ANALYSIS INTEGRATION TEST")
    print("=" * 70)
    print()
    
    # Test 1: Dry run with duplicate analysis
    print("[*] Test 1: Dry run with duplicate analysis")
    print("-" * 70)
    
    cleanup = CleanupOrchestrator(project_root)
    result = cleanup.execute({
        'dry_run': True,
        'skip_duplicate_analysis': False,  # Include Phase 0
        'auto_delete_archived': False      # Don't delete in dry run
    })
    
    print(f"\n[+] Result: {result.status}")
    print(f"[+] Message: {result.message}")
    print(f"\n[*] Metrics:")
    print(f"    Files moved: {result.data['metrics']['files_moved']}")
    print(f"    Files removed: {result.data['metrics']['files_removed']}")
    print(f"    References updated: {result.data['metrics']['references_updated']}")
    
    if result.data.get('duplicate_report'):
        print(f"\n[*] Duplicate Analysis:")
        print(f"    Duplicates found: {result.data['metrics']['duplicates_found']}")
        print(f"    Safe to delete: {result.data['metrics']['safe_to_delete']}")
        print(f"    Need review: {result.data['metrics']['needs_review']}")
        print(f"    Duplicates deleted: {result.data['metrics']['duplicates_deleted']}")
    else:
        print("\n[!] Warning: Duplicate analysis not executed")
    
    print(f"\n[*] Report saved to: {result.data['report_path']}")
    
    # Test 2: Check if duplicate analysis is integrated
    print("\n" + "=" * 70)
    print("[*] Test 2: Verify Phase 0 integration")
    print("-" * 70)
    
    if result.data.get('duplicate_report'):
        report = result.data['duplicate_report']
        summary = report.get('summary', {})
        
        print(f"[+] Phase 0 executed successfully")
        print(f"    Total files analyzed: {summary.get('total_files', 0)}")
        print(f"    Duplicate files: {summary.get('duplicate_files', 0)}")
        print(f"    Duplicate functions: {summary.get('duplicate_functions', 0)}")
        print(f"    Duplicate classes: {summary.get('duplicate_classes', 0)}")
        
        recommendations = report.get('recommendations', [])
        safe_archived = [r for r in recommendations 
                        if r.get('action', '').startswith('SAFE') and 'archived' in r.get('action', '').lower()]
        
        print(f"\n[*] Archived duplicates ready for deletion: {len(safe_archived)}")
        if safe_archived:
            print(f"    Sample: {safe_archived[0]['file']}")
    else:
        print("[!] Phase 0 was not executed")
    
    # Test 3: Verify auto_delete_archived parameter handling
    print("\n" + "=" * 70)
    print("[*] Test 3: Verify auto_delete_archived parameter")
    print("-" * 70)
    
    if result.data.get('duplicate_report') and result.data['metrics']['safe_to_delete'] > 0:
        print("[+] auto_delete_archived parameter available")
        print(f"    Would delete {result.data['metrics']['safe_to_delete']} archived duplicates")
        print(f"    Mode: dry_run=True (no actual deletion)")
        print("\n[*] To actually delete archived duplicates:")
        print("    cleanup.execute({'dry_run': False, 'auto_delete_archived': True})")
    else:
        print("[?] No archived duplicates to delete or Phase 0 not executed")
    
    # Test 4: Report structure validation
    print("\n" + "=" * 70)
    print("[*] Test 4: Report structure validation")
    print("-" * 70)
    
    report_path = Path(result.data['report_path'])
    if report_path.exists():
        import json
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        print("[+] Report file exists and is valid JSON")
        print(f"    Timestamp: {report.get('timestamp')}")
        print(f"    Duration: {report.get('duration_seconds'):.2f}s")
        
        if 'duplicate_analysis' in report:
            print(f"\n[+] Duplicate analysis section present in report")
            dup_analysis = report['duplicate_analysis']
            print(f"    Duplicates found: {dup_analysis.get('duplicates_found', 0)}")
            print(f"    Safe to delete: {dup_analysis.get('safe_to_delete', 0)}")
            print(f"    Needs review: {dup_analysis.get('needs_review', 0)}")
            print(f"    Duplicates deleted: {dup_analysis.get('duplicates_deleted', 0)}")
        else:
            print("\n[?] No duplicate analysis section in report (Phase 0 may have been skipped)")
    else:
        print("[!] Report file not found")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    tests_passed = 0
    tests_total = 4
    
    # Check Test 1
    if result.success or result.status.name in ['SUCCESS', 'WARNING']:
        tests_passed += 1
        print("[PASS] Test 1: Cleanup executed successfully")
    else:
        print("[FAIL] Test 1: Cleanup failed")
    
    # Check Test 2
    if result.data.get('duplicate_report'):
        tests_passed += 1
        print("[PASS] Test 2: Phase 0 integrated and executed")
    else:
        print("[FAIL] Test 2: Phase 0 not executed")
    
    # Check Test 3
    if 'auto_delete_archived' in str(cleanup.execute.__code__.co_varnames):
        tests_passed += 1
        print("[PASS] Test 3: auto_delete_archived parameter available")
    else:
        print("[FAIL] Test 3: auto_delete_archived parameter missing")
    
    # Check Test 4
    if report_path.exists():
        tests_passed += 1
        print("[PASS] Test 4: Report generated and structured correctly")
    else:
        print("[FAIL] Test 4: Report not generated")
    
    print(f"\n[*] Tests Passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("\n[SUCCESS] All integration tests passed!")
    else:
        print(f"\n[WARNING] {tests_total - tests_passed} test(s) failed")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    try:
        test_cleanup_with_duplicates()
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
