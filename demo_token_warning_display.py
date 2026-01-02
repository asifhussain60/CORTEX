#!/usr/bin/env python3
"""
Demo: User-Facing Token Warning Display

Demonstrates how token warnings are now displayed to users in chat responses
when approaching the 80k token threshold.

Author: Asif Hussain
Created: 2026-01-02
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from orchestration_4_0.base.base_orchestrator import BaseOrchestrator
from orchestration_4_0.base.phase_manager import PhaseManager


def demo_token_warning_display():
    """Demonstrate token warning user display functionality."""
    
    print("=" * 70)
    print("🧪 Token Warning Display Demo")
    print("=" * 70)
    print()
    
    # Create mock orchestrator
    class MockOrchestrator(BaseOrchestrator):
        def execute(self, user_request: str, **kwargs):
            pass
        
        def _setup(self, context: dict):
            pass
        
        def _teardown(self):
            pass
        
        def _register_phases(self):
            pass
        
        def _execute_phase(self, phase_name: str, context: dict):
            pass
    
    # Initialize with low threshold for testing
    orchestrator = MockOrchestrator(
        name="demo_orchestrator",
        config={"token_warning_threshold": 5000}
    )
    
    # Simulate completing phases
    phase_manager = orchestrator.phase_manager
    
    print("📊 Simulating phase execution with token monitoring...\n")
    
    # Add phases
    for i in range(6):
        phase_name = f"Phase {i+1}"
        phase_manager.register_phase(phase_name, f"Demo phase {i+1} description")
        phase_manager.start_phase(phase_name)
        phase_manager.complete_phase(phase_name)
        
        # Check token usage
        token_status = orchestrator.check_token_usage()
        
        print(f"✓ Completed {phase_name}")
        print(f"  Tokens: {token_status['estimated_tokens']:,} / {token_status['threshold']:,} ({token_status['percentage']:.1f}%)")
        
        # Display user-facing message if warning triggered
        if token_status['should_warn'] and token_status['user_message']:
            print(f"\n{'=' * 70}")
            print("🎯 USER-FACING WARNING (displayed in chat):")
            print(f"{'=' * 70}")
            print(token_status['user_message'])
            print(f"{'=' * 70}\n")
            break
        
        print()
    
    print("\n" + "=" * 70)
    print("✅ Demo Complete")
    print("=" * 70)
    print()
    print("📝 Key Points:")
    print("  • Token warnings now include user_message in return dict")
    print("  • Orchestrators can display warning in chat responses")
    print("  • Users see formatted message with continuation prompt link")
    print("  • Logging continues for debugging (logger.warning)")
    print()
    print("🔧 Implementation:")
    print("  • BaseOrchestrator.check_token_usage() returns user_message")
    print("  • Orchestrators check token status and append to response")
    print("  • Example in: src/orchestrators/planning/planning_orchestrator_v5.py")
    print()


if __name__ == "__main__":
    demo_token_warning_display()
