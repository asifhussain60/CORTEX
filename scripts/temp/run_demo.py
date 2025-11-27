"""
Quick Demo: TDD Demo System in Action

Demonstrates JWT Authentication scenario with RED→GREEN→REFACTOR workflow.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.tdd import DemoOrchestrator


def main():
    """Run JWT authentication demo."""
    
    print("\n" + "="*70)
    print("🧠 CORTEX TDD Demo System - JWT Authentication")
    print("="*70)
    
    # Create orchestrator
    orchestrator = DemoOrchestrator()
    
    # List available scenarios
    print("\n📋 Available Demo Scenarios:")
    scenarios = orchestrator.list_scenarios()
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']} ({scenario['category']}) - {scenario['estimated_time']} min")
    
    # Start JWT auth demo
    print("\n🚀 Starting JWT Authentication Demo...")
    session_id = orchestrator.start_demo('auth_jwt')
    print(f"Session ID: {session_id}")
    
    # Run complete demo
    print("\n" + "="*70)
    print("Running Complete RED→GREEN→REFACTOR Workflow")
    print("="*70)
    
    try:
        session = orchestrator.run_complete_demo(session_id)
        
        # Display summary
        print("\n" + "="*70)
        print("📊 Demo Summary")
        print("="*70)
        
        summary = orchestrator.get_session_summary(session_id)
        
        print(f"\n✅ Status: {summary['status']}")
        print(f"⏱️  Total Time: {summary['total_time']}")
        print(f"📈 Phases Completed: {summary['phases_completed']}/3")
        
        if summary['red_phase']:
            print(f"\n🔴 RED Phase:")
            print(f"   Success: {summary['red_phase']['success']} (test should fail)")
            print(f"   Time: {summary['red_phase']['time']}")
        
        if summary['green_phase']:
            print(f"\n🟢 GREEN Phase:")
            print(f"   Success: {summary['green_phase']['success']} (tests should pass)")
            print(f"   Time: {summary['green_phase']['time']}")
        
        if summary['refactor_phase']:
            print(f"\n♻️  REFACTOR Phase:")
            print(f"   Success: {summary['refactor_phase']['success']} (tests should still pass)")
            print(f"   Time: {summary['refactor_phase']['time']}")
        
        print("\n" + "="*70)
        print("✅ Demo Complete!")
        print("="*70)
        
        # Cleanup
        orchestrator.cleanup()
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        orchestrator.cleanup()
        sys.exit(1)


if __name__ == '__main__':
    main()
