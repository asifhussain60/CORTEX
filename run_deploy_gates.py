"""
Deployment Gates Validation Script
Executes all 16 validation gates before production deployment
"""
from pathlib import Path
from src.orchestrators.publish_branch_orchestrator import PublishBranchOrchestrator

def main():
    print("=" * 60)
    print("CORTEX Deployment Validation Gates")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = PublishBranchOrchestrator(Path('.'))
    
    # Execute validation gates
    print("\nExecuting all 16 validation gates...\n")
    result = orchestrator.execute_validation_gates()
    
    # Display results
    print("\n" + "=" * 60)
    print("VALIDATION RESULT")
    print("=" * 60)
    print(f"All Passed: {result['all_passed']}")
    print(f"Total Gates: {result['total_gates']}")
    print(f"Passed Gates: {result['passed_gates']}")
    print(f"Failed Gates: {result['failed_gates']}")
    print("=" * 60)
    
    if result['all_passed']:
        print("\n✅ All gates passed! Ready for production deployment.")
        return 0
    else:
        print("\n❌ Some gates failed. Review failures before deployment.")
        return 1

if __name__ == "__main__":
    exit(main())
