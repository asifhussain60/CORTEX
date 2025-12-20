"""Test SKULL test discovery phase in isolation."""
from pathlib import Path
from src.operations.modules.system.optimize_system_orchestrator import OptimizeSystemOrchestrator

if __name__ == '__main__':
    print("Testing SKULL Test Discovery & Validation")
    print("=" * 80)
    
    orchestrator = OptimizeSystemOrchestrator(project_root=Path('.'))
    
    # Call the method directly
    result = orchestrator._discover_and_validate_skull_tests({})
    
    print("\n=== SKULL TEST DISCOVERY RESULTS ===")
    print(f"Coverage: {result['coverage_percent']:.1f}%")
    print(f"Total Tests: {result['tests_total']}")
    print(f"Passing: {result['tests_passing']}")
    print(f"Failing: {result['tests_failing']}")
    print(f"Tests Needed: {result['tests_needed']}")
    
    if result['missing_tests']:
        print(f"\nMissing Tests ({len(result['missing_tests'])}):")
        for missing in result['missing_tests'][:10]:  # First 10
            print(f"  - {missing}")
    
    if result.get('error'):
        print(f"\nError: {result['error']}")
