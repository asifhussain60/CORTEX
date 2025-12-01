"""Quick test for TDD Mastery validation integration."""
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator

def test_tdd_validation():
    """Test TDD Mastery validation checks."""
    print("\n🧪 Testing TDD Mastery Validation Integration\n")
    print("="*80)
    
    # Create orchestrator
    orchestrator = SystemAlignmentOrchestrator()
    
    # Run TDD validation
    print("\nRunning TDD validation checks...")
    tdd_validation = orchestrator._validate_tdd_mastery_integration()
    
    # Display results
    print(f"\n{'='*80}")
    print("📊 TDD Mastery Validation Results")
    print(f"{'='*80}\n")
    print(f"✅ All Passed: {tdd_validation['all_passed']}")
    print(f"📋 Total Issues: {len(tdd_validation['issues'])}\n")
    
    if tdd_validation['issues']:
        print("Issues Found:")
        print("-"*80)
        for idx, issue in enumerate(tdd_validation['issues'], 1):
            severity_icon = "❌" if issue['severity'] == 'critical' else "⚠️"
            print(f"\n{idx}. {severity_icon} [{issue['severity'].upper()}]")
            print(f"   Message: {issue['message']}")
            print(f"   Fix: {issue.get('fix', 'Manual review required')}")
    else:
        print("✅ No issues found - TDD Mastery is fully integrated!")
    
    print(f"\n{'='*80}")
    print("✅ Test Complete")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    test_tdd_validation()
