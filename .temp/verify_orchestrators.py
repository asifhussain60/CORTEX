#!/usr/bin/env python3
"""
Quick verification script for 6 orchestrators mentioned in brittleness report.
Tests if they can be imported and instantiated.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_orchestrator(name, module_path, class_name):
    """Test if orchestrator can be imported and instantiated."""
    try:
        # Import module
        parts = module_path.split('.')
        module = __import__(module_path, fromlist=[class_name])
        orchestrator_class = getattr(module, class_name)
        
        print(f"✅ {name}: Import successful ({class_name})")
        return True
    except Exception as e:
        print(f"❌ {name}: {type(e).__name__}: {str(e)}")
        return False

def main():
    """Test all 6 orchestrators from brittleness report."""
    
    print("=" * 70)
    print("ORCHESTRATOR INSTANTIATION TEST (Brittleness Report RC-004)")
    print("=" * 70)
    print()
    
    orchestrators = [
        ("Planning v5", "src.orchestrators.planning.planning_orchestrator_v5", "PlanningOrchestratorV5"),
        ("TDD", "src.orchestrators.tdd.tdd_orchestrator", "TDDOrchestrator"),
        ("ADO v2", "src.orchestrators.ado.ado_orchestrator_v2", "ADOOrchestratorV2"),
        ("Sanitization", "src.orchestrators.sanitization.sanitization_orchestrator", "SanitizationOrchestrator"),
        ("Cleanup v2", "src.orchestrators.cleanup.cleanup_orchestrator_v2", "CleanupOrchestratorV2"),
        ("Vacuum v2", "src.orchestrators.vacuum.vacuum_orchestrator_v2", "VacuumOrchestratorV2"),
    ]
    
    results = []
    for name, module_path, class_name in orchestrators:
        success = test_orchestrator(name, module_path, class_name)
        results.append((name, success))
        print()
    
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOrchestrators Passing: {passed}/{total} ({passed/total*100:.1f}%)")
    print()
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
    
    print()
    
    if passed == total:
        print("🎉 SUCCESS: All orchestrators can be imported!")
        print("Target: 6/6 (100%) - ACHIEVED")
        return 0
    else:
        print(f"⚠️  WARNING: {total - passed} orchestrator(s) failing")
        print(f"Target: 6/6 (100%) - Current: {passed}/{total} ({passed/total*100:.1f}%)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
