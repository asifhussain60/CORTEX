#!/usr/bin/env python3
"""
Validation Script for Phase 3B: Cleanup + Doc Archive Management

Tests:
1. DocumentGovernance import succeeds in cleanup module
2. CleanupMetrics has archived_docs_removed field
3. _cleanup_doc_archives() method exists
4. Cleanup report includes archived docs stats
5. Phase 5.5 integration in execute() workflow

Author: GitHub Copilot
Date: November 27, 2025
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_imports():
    """Test 1: Verify imports work"""
    print("✓ Test 1: Verifying imports...")
    
    try:
        from src.operations.modules.cleanup.cleanup_orchestrator import (
            CleanupOrchestrator,
            CleanupMetrics
        )
        from src.governance import DocumentGovernance
        print("  ✅ All imports successful")
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_metrics_field():
    """Test 2: Verify CleanupMetrics has archived_docs_removed"""
    print("\n✓ Test 2: Checking CleanupMetrics fields...")
    
    try:
        from src.operations.modules.cleanup.cleanup_orchestrator import CleanupMetrics
        from datetime import datetime
        
        # Create instance
        metrics = CleanupMetrics(timestamp=datetime.now())
        
        # Check field exists
        if hasattr(metrics, 'archived_docs_removed'):
            print(f"  ✅ archived_docs_removed field exists (default: {metrics.archived_docs_removed})")
            return True
        else:
            print("  ❌ archived_docs_removed field NOT found")
            return False
    
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

def test_cleanup_archives_method():
    """Test 3: Verify _cleanup_doc_archives() method exists"""
    print("\n✓ Test 3: Checking _cleanup_doc_archives() method...")
    
    try:
        from src.operations.modules.cleanup.cleanup_orchestrator import CleanupOrchestrator
        
        orchestrator = CleanupOrchestrator()
        
        # Check method exists
        if hasattr(orchestrator, '_cleanup_doc_archives'):
            method = getattr(orchestrator, '_cleanup_doc_archives')
            print(f"  ✅ _cleanup_doc_archives() method exists")
            
            # Check method signature
            import inspect
            sig = inspect.signature(method)
            params = list(sig.parameters.keys())
            print(f"  ✅ Method signature: {params}")
            
            if 'dry_run' in params:
                print("  ✅ Correct parameters (dry_run)")
                return True
            else:
                print(f"  ⚠️ Unexpected parameters: {params}")
                return False
        else:
            print("  ❌ _cleanup_doc_archives() method NOT found")
            return False
    
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

def test_git_commit_message():
    """Test 4: Verify git commit message includes archived docs"""
    print("\n✓ Test 4: Checking git commit message format...")
    
    try:
        import inspect
        from src.operations.modules.cleanup.cleanup_orchestrator import CleanupOrchestrator
        
        orchestrator = CleanupOrchestrator()
        
        # Get _git_commit_cleanup method source
        commit_source = inspect.getsource(orchestrator._git_commit_cleanup)
        
        # Check for archived_docs_removed in commit message
        if 'archived_docs_removed' in commit_source:
            print("  ✅ Git commit message includes archived_docs_removed")
            
            # Extract commit message template
            lines = commit_source.split('\n')
            for i, line in enumerate(lines):
                if 'Archived docs removed' in line or 'archived_docs_removed' in line:
                    print(f"  ✅ Found in commit message:")
                    print(f"      {line.strip()}")
                    break
            
            return True
        else:
            print("  ❌ Git commit message does NOT include archived_docs_removed")
            return False
    
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

def test_phase_5_5_integration():
    """Test 5: Verify Phase 5.5 call in execute() workflow"""
    print("\n✓ Test 5: Checking Phase 5.5 integration in execute()...")
    
    try:
        import inspect
        from src.operations.modules.cleanup.cleanup_orchestrator import CleanupOrchestrator
        
        orchestrator = CleanupOrchestrator()
        
        # Get execute method source
        execute_source = inspect.getsource(orchestrator.execute)
        
        # Check for Phase 5.5 call
        if '_cleanup_doc_archives' in execute_source and 'Phase 5.5' in execute_source:
            print("  ✅ Phase 5.5 documentation archive cleanup call found in execute()")
            
            # Extract Phase 5.5 section
            lines = execute_source.split('\n')
            phase_5_5_lines = []
            capturing = False
            
            for line in lines:
                if 'Phase 5.5' in line:
                    capturing = True
                
                if capturing:
                    phase_5_5_lines.append(line)
                    
                    if 'Phase 5.5' not in line and line.strip() and not line.strip().startswith('#'):
                        if 'logger' in line or 'cleanup' in line or 'archived' in line:
                            continue
                        else:
                            break
            
            if phase_5_5_lines:
                print("  ✅ Phase 5.5 code excerpt:")
                for line in phase_5_5_lines[:5]:
                    print(f"      {line.rstrip()}")
            
            return True
        else:
            print("  ❌ Phase 5.5 call NOT found in execute()")
            return False
    
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

def run_all_tests():
    """Run all validation tests"""
    print("=" * 80)
    print("PHASE 3B VALIDATION: Cleanup + Doc Archive Management")
    print("=" * 80)
    
    tests = [
        ("Imports", test_imports),
        ("Metrics Field", test_metrics_field),
        ("Cleanup Archives Method", test_cleanup_archives_method),
        ("Git Commit Message", test_git_commit_message),
        ("Phase 5.5 Integration", test_phase_5_5_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'✅' if passed == total else '⚠️'} Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 Phase 3B implementation VALIDATED - All tests passed!")
        print("\n✓ Next Steps:")
        print("  1. Create test archived documents (>30 days old)")
        print("  2. Run 'cortex cleanup' to test end-to-end workflow")
        print("  3. Verify archived docs removed from archive directories")
        print("  4. Check git commit includes archived_docs_removed count")
        print("  5. Proceed to Phase 3C (Healthcheck Integration)")
        return 0
    else:
        print("\n⚠️ Phase 3B validation INCOMPLETE - Fix failing tests")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
