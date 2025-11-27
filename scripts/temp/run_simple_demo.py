"""
Simple TDD Demo: Shows Code Without Execution

Demonstrates the TDD Demo System by displaying code for each phase
without requiring pytest plugins.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.tdd import TDDDemoEngine, DemoPhase


def main():
    """Display JWT authentication demo code."""
    
    print("\n" + "="*70)
    print("🧠 CORTEX TDD Demo System - JWT Authentication")
    print("="*70)
    
    # Create demo engine
    engine = TDDDemoEngine()
    
    # Get scenario
    scenario = engine.get_scenario('auth_jwt')
    
    print(f"\n📋 Scenario: {scenario.name}")
    print(f"   Category: {scenario.category}")
    print(f"   Estimated Time: {scenario.estimated_time} minutes")
    print(f"   Description: {scenario.description}")
    
    # RED Phase
    print("\n" + "="*70)
    print("🔴 PHASE 1: RED - Write Failing Test")
    print("="*70)
    print("\nIn this phase, we write a test BEFORE any implementation exists.")
    print("The test defines the behavior we want to implement.")
    print("\n📝 Test Code:")
    print("-" * 70)
    red_code = engine.get_phase_code('auth_jwt', DemoPhase.RED)
    print(red_code)
    print("-" * 70)
    print("\n❌ Expected Result: Test FAILS (no implementation yet)")
    
    # GREEN Phase
    print("\n" + "="*70)
    print("🟢 PHASE 2: GREEN - Minimal Implementation")
    print("="*70)
    print("\nIn this phase, we write MINIMAL code to make the test pass.")
    print("We don't worry about perfect code yet - just make it work.")
    print("\n💚 Implementation Code:")
    print("-" * 70)
    green_code = engine.get_phase_code('auth_jwt', DemoPhase.GREEN)
    print(green_code)
    print("-" * 70)
    print("\n✅ Expected Result: Tests PASS (minimal implementation works)")
    
    print("\n📊 Key Points in GREEN Phase:")
    print("   • Hardcoded user: {'alice': 'secret123'} - simplest approach")
    print("   • No password hashing - not needed to pass test")
    print("   • Minimal JWT generation - just enough to pass")
    
    # REFACTOR Phase
    print("\n" + "="*70)
    print("♻️  PHASE 3: REFACTOR - Improve Code")
    print("="*70)
    print("\nIn this phase, we improve the code while keeping tests green.")
    print("Add production features like password hashing and validation.")
    print("\n🔧 Refactored Code:")
    print("-" * 70)
    refactor_code = engine.get_phase_code('auth_jwt', DemoPhase.REFACTOR)
    print(refactor_code)
    print("-" * 70)
    print("\n✅ Expected Result: Tests STILL PASS (refactoring preserved behavior)")
    
    print("\n📊 Improvements in REFACTOR Phase:")
    print("   • Added User class with password hashing (SHA256)")
    print("   • Proper user storage with dictionary")
    print("   • Enhanced JWT payload (user_id, iat timestamp)")
    print("   • Added verify_token() method for validation")
    print("   • Production-ready error handling")
    
    # Summary
    print("\n" + "="*70)
    print("📊 RED→GREEN→REFACTOR Summary")
    print("="*70)
    print("\n✨ This demonstrates TDD methodology in action:")
    print("   1. RED: Write test first (defines requirements)")
    print("   2. GREEN: Minimal code to pass (fastest path to working)")
    print("   3. REFACTOR: Improve code (add production features)")
    print("\n🎯 Key TDD Principle:")
    print("   Tests protect refactoring - you can improve code")
    print("   confidently because tests verify behavior unchanged.")
    
    # Show other scenarios
    print("\n" + "="*70)
    print("📋 Other Available Demo Scenarios")
    print("="*70)
    
    scenarios = engine.list_scenarios()
    for s in scenarios:
        if s.id != 'auth_jwt':
            print(f"\n• {s.name}")
            print(f"  Category: {s.category}")
            print(f"  Time: {s.estimated_time} min")
            print(f"  Description: {s.description}")
    
    print("\n" + "="*70)
    print("✅ Demo Complete!")
    print("="*70)
    print("\nTo run full demos with test execution, install dependencies:")
    print("   pip install pytest PyJWT")


if __name__ == '__main__':
    main()
