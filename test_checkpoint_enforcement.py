"""
Test Git Checkpoint Deployment Gate

Validates that the deployment gate properly enforces checkpoint system requirements.

Version: 1.0.0
Author: Asif Hussain
"""

import sys
from pathlib import Path

# Add src to path - test is at project root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.deployment.deployment_gates import DeploymentGates


def test_checkpoint_gate():
    """Test Git Checkpoint System deployment gate."""
    print("\n" + "=" * 60)
    print("GIT CHECKPOINT DEPLOYMENT GATE VALIDATION")
    print("=" * 60)
    
    gates = DeploymentGates(project_root)
    
    print("\n🔍 Running Git Checkpoint System validation gate...")
    gate_result = gates._validate_git_checkpoint_system()
    
    print("\n📋 Gate Results:")
    print(f"   Name: {gate_result['name']}")
    print(f"   Passed: {'✅' if gate_result['passed'] else '❌'} {gate_result['passed']}")
    print(f"   Severity: {gate_result['severity']}")
    print(f"   Message: {gate_result['message']}")
    
    if gate_result['details']:
        details = gate_result['details']
        checks = details.get('checks', {})
        issues = details.get('issues', [])
        
        print("\n🔎 Detailed Checks:")
        for check_name, check_passed in checks.items():
            status = "✅" if check_passed else "❌"
            print(f"   {status} {check_name}: {check_passed}")
        
        print(f"\n   Summary: {details['passed_checks']}/{details['total_checks']} checks passed")
        
        if issues:
            print(f"\n⚠️  Issues Found ({len(issues)}):")
            for issue in issues:
                print(f"   - {issue}")
    
    print("\n" + "=" * 60)
    if gate_result['passed']:
        print("✅ GIT CHECKPOINT GATE PASSED")
        print("=" * 60)
        print("\n🎉 Checkpoint system ready for deployment!\n")
        return 0
    else:
        print("❌ GIT CHECKPOINT GATE FAILED")
        print("=" * 60)
        print(f"\n🚨 Severity: {gate_result['severity']}")
        print(f"💬 {gate_result['message']}\n")
        return 1


def test_full_deployment_gates():
    """Test all deployment gates including checkpoint."""
    print("\n" + "=" * 60)
    print("FULL DEPLOYMENT GATES VALIDATION")
    print("=" * 60)
    
    gates = DeploymentGates(project_root)
    
    print("\n🔍 Running all deployment gates...")
    results = gates.validate_all_gates()
    
    print("\n📋 Overall Results:")
    print(f"   Passed: {'✅' if results['passed'] else '❌'} {results['passed']}")
    print(f"   Errors: {len(results['errors'])}")
    print(f"   Warnings: {len(results['warnings'])}")
    
    print("\n🔎 Individual Gates:")
    for gate in results['gates']:
        status = "✅" if gate['passed'] else "❌"
        print(f"   {status} {gate['name']}: {gate['message']}")
    
    if results['errors']:
        print(f"\n❌ Errors ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"   - {error}")
    
    if results['warnings']:
        print(f"\n⚠️  Warnings ({len(results['warnings'])}):")
        for warning in results['warnings']:
            print(f"   - {warning}")
    
    print("\n" + "=" * 60)
    if results['passed']:
        print("✅ ALL DEPLOYMENT GATES PASSED")
        print("=" * 60)
        print("\n🎉 System ready for deployment!\n")
        return 0
    else:
        print("❌ DEPLOYMENT GATES FAILED")
        print("=" * 60)
        print(f"\n🚨 Fix {len(results['errors'])} errors before deployment\n")
        return 1


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print(" " * 20 + "CHECKPOINT ENFORCEMENT VALIDATION")
    print("=" * 80)
    
    try:
        # Test 1: Checkpoint gate specifically
        print("\n\n" + "─" * 80)
        print("TEST 1: Git Checkpoint Deployment Gate")
        print("─" * 80)
        result1 = test_checkpoint_gate()
        
        # Test 2: All gates together
        print("\n\n" + "─" * 80)
        print("TEST 2: Full Deployment Gates")
        print("─" * 80)
        result2 = test_full_deployment_gates()
        
        # Summary
        print("\n\n" + "=" * 80)
        print(" " * 30 + "SUMMARY")
        print("=" * 80)
        print(f"\n   Test 1 (Checkpoint Gate): {'✅ PASSED' if result1 == 0 else '❌ FAILED'}")
        print(f"   Test 2 (Full Gates):      {'✅ PASSED' if result2 == 0 else '❌ FAILED'}")
        
        if result1 == 0 and result2 == 0:
            print("\n✅ ALL TESTS PASSED - Checkpoint enforcement operational!\n")
            return 0
        else:
            print("\n❌ SOME TESTS FAILED - Fix issues before deployment\n")
            return 1
            
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
