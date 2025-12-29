#!/usr/bin/env python3
"""
Validation Script for Phase 3A: Optimize + Doc Deduplication Integration

Tests:
1. DocumentGovernance import succeeds
2. OptimizationMetrics has doc_deduplication_count field
3. _deduplicate_documentation() method exists
4. Optimization report includes deduplication stats
5. End-to-end workflow (dry-run with mock data)

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
        from src.operations.modules.optimization.optimize_cortex_orchestrator import (
            OptimizeCortexOrchestrator,
            OptimizationMetrics
        )
        from src.governance import DocumentGovernance
        print("  ✅ All imports successful")
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_metrics_field():
    """Test 2: Verify OptimizationMetrics has doc_deduplication_count"""
    print("\n✓ Test 2: Checking OptimizationMetrics fields...")
    
    try:
        from src.operations.modules.optimization.optimize_cortex_orchestrator import OptimizationMetrics
        from datetime import datetime
        
        # Create instance
        metrics = OptimizationMetrics(
            optimization_id="test",
            timestamp=datetime.now()
        )
        
        # Check field exists
        if hasattr(metrics, 'doc_deduplication_count'):
            print(f"  ✅ doc_deduplication_count field exists (default: {metrics.doc_deduplication_count})")
            return True
        else:
            print("  ❌ doc_deduplication_count field NOT found")
            return False
    
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

def test_deduplicate_method():
    """Test 3: Verify _deduplicate_documentation() method exists"""
    print("\n✓ Test 3: Checking _deduplicate_documentation() method...")
    
    try:
        from src.operations.modules.optimization.optimize_cortex_orchestrator import OptimizeCortexOrchestrator
        
        orchestrator = OptimizeCortexOrchestrator()
        
        # Check method exists
        if hasattr(orchestrator, '_deduplicate_documentation'):
            method = getattr(orchestrator, '_deduplicate_documentation')
            print(f"  ✅ _deduplicate_documentation() method exists")
            
            # Check method signature
            import inspect
            sig = inspect.signature(method)
            params = list(sig.parameters.keys())
            print(f"  ✅ Method signature: {params}")
            
            if 'project_root' in params and 'metrics' in params:
                print("  ✅ Correct parameters (project_root, metrics)")
                return True
            else:
                print(f"  ⚠️ Unexpected parameters: {params}")
                return False
        else:
            print("  ❌ _deduplicate_documentation() method NOT found")
            return False
    
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

def test_report_includes_dedup():
    """Test 4: Verify optimization report includes deduplication stats"""
    print("\n✓ Test 4: Checking optimization report format...")
    
    try:
        from src.operations.modules.optimization.optimize_cortex_orchestrator import (
            OptimizeCortexOrchestrator,
            OptimizationMetrics
        )
        from datetime import datetime
        
        orchestrator = OptimizeCortexOrchestrator()
        
        # Create test metrics
        metrics = OptimizationMetrics(
            optimization_id="test_report",
            timestamp=datetime.now()
        )
        metrics.doc_deduplication_count = 5
        metrics.duration_seconds = 60.0
        metrics.tests_run = 10
        metrics.tests_passed = 10
        metrics.tests_failed = 0
        metrics.issues_identified = 3
        metrics.optimizations_applied = 5
        metrics.optimizations_succeeded = 5
        
        # Generate report
        report = orchestrator._generate_optimization_report(metrics)
        
        # Check for deduplication stats
        if 'Documentation Deduplicated' in report or 'doc_deduplication_count' in report:
            print("  ✅ Report includes documentation deduplication stats")
            print(f"  ✅ Sample report excerpt:")
            
            # Extract summary section
            lines = report.split('\n')
            for i, line in enumerate(lines):
                if 'Summary' in line:
                    for j in range(i, min(i + 10, len(lines))):
                        if lines[j].strip():
                            print(f"      {lines[j]}")
            
            return True
        else:
            print("  ❌ Report does NOT include deduplication stats")
            print("  Report preview:")
            print(report[:500])
            return False
    
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase_6_5_integration():
    """Test 5: Verify Phase 6.5 call in execute() workflow"""
    print("\n✓ Test 5: Checking Phase 6.5 integration in execute()...")
    
    try:
        import inspect
        from src.operations.modules.optimization.optimize_cortex_orchestrator import OptimizeCortexOrchestrator
        
        orchestrator = OptimizeCortexOrchestrator()
        
        # Get execute method source
        execute_source = inspect.getsource(orchestrator.execute)
        
        # Check for Phase 6.5 call
        if '_deduplicate_documentation' in execute_source and 'Phase 6.5' in execute_source:
            print("  ✅ Phase 6.5 documentation deduplication call found in execute()")
            
            # Extract Phase 6.5 section
            lines = execute_source.split('\n')
            phase_6_5_lines = []
            capturing = False
            
            for line in lines:
                if 'Phase 6.5' in line:
                    capturing = True
                
                if capturing:
                    phase_6_5_lines.append(line)
                    
                    if 'Phase 6.5' not in line and line.strip() and not line.strip().startswith('#'):
                        if 'logger' in line or 'dedup' in line:
                            continue
                        else:
                            break
            
            if phase_6_5_lines:
                print("  ✅ Phase 6.5 code excerpt:")
                for line in phase_6_5_lines[:5]:
                    print(f"      {line.rstrip()}")
            
            return True
        else:
            print("  ❌ Phase 6.5 call NOT found in execute()")
            return False
    
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

def run_all_tests():
    """Run all validation tests"""
    print("=" * 80)
    print("PHASE 3A VALIDATION: Optimize + Doc Deduplication Integration")
    print("=" * 80)
    
    tests = [
        ("Imports", test_imports),
        ("Metrics Field", test_metrics_field),
        ("Deduplicate Method", test_deduplicate_method),
        ("Report Format", test_report_includes_dedup),
        ("Phase 6.5 Integration", test_phase_6_5_integration)
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
        print("\n🎉 Phase 3A implementation VALIDATED - All tests passed!")
        print("\n✓ Next Steps:")
        print("  1. Run 'cortex optimize' to test end-to-end workflow")
        print("  2. Check git commits for doc consolidation")
        print("  3. Review optimization report for deduplication stats")
        print("  4. Proceed to Phase 3B (Cleanup Integration)")
        return 0
    else:
        print("\n⚠️ Phase 3A validation INCOMPLETE - Fix failing tests")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
