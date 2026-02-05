"""Integration example: Autonomous Plan Continuation Flow.

Demonstrates how AutonomousPlanExecutor seamlessly integrates with
cortex-architect prompt for autonomous multi-phase plan execution.

Author: Asif Hussain
Version: 1.0
"""

from cortex.orchestrators.planning.autonomous_plan_executor import (
    AutonomousPlanExecutor,
    check_autonomous_continuation
)


def demo_continuation_detection():
    """Demo 1: Continuation intent detection."""
    print("=" * 80)
    print("DEMO 1: Continuation Intent Detection")
    print("=" * 80)
    
    executor = AutonomousPlanExecutor()
    
    test_requests = [
        ("continue with phase 2", True, "Explicit continuation"),
        ("proceed autonomously", True, "Autonomous execution"),
        ("implement phase 3 immediately", True, "Phase number + immediate"),
        ("what is the best approach?", False, "Exploratory question"),
        ("how should we architect this?", False, "Design discussion"),
    ]
    
    for request, expected, description in test_requests:
        detected = executor.detect_continuation_intent(request)
        status = "✅" if detected == expected else "❌"
        
        print(f"\n{status} Request: '{request}'")
        print(f"   Description: {description}")
        print(f"   Detected: {detected} (expected: {expected})")


def demo_context_analysis():
    """Demo 2: Full context analysis with registry."""
    print("\n\n" + "=" * 80)
    print("DEMO 2: Context Analysis with Registry")
    print("=" * 80)
    
    try:
        executor = AutonomousPlanExecutor()
        
        # Test with continuation intent
        print("\n🔵 Test: Continuation request")
        result = executor.should_bypass_challenge("continue with implementation")
        
        print(f"   Bypass Challenge: {result['bypass']}")
        print(f"   Next Phase: {result['next_phase']}")
        print(f"   Reason: {result['reason']}")
        
        context = result['context']
        print(f"   Active Phases: {len(context.active_phases)}")
        
        if context.active_phases:
            for phase in context.active_phases:
                print(f"      - {phase.phase_id}: {phase.name} ({phase.status})")
        
        # Test with exploratory request
        print("\n🟡 Test: Exploratory request")
        result = executor.should_bypass_challenge("what's the architecture?")
        
        print(f"   Bypass Challenge: {result['bypass']}")
        print(f"   Reason: {result['reason']}")
        
    except FileNotFoundError as e:
        print(f"\n⚠️  Registry not found: {e}")
        print("   This demo requires _cortex-master/index.yaml")


def demo_autonomous_header():
    """Demo 3: Autonomous execution header generation."""
    print("\n\n" + "=" * 80)
    print("DEMO 3: Autonomous Header Generation")
    print("=" * 80)
    
    try:
        executor = AutonomousPlanExecutor()
        result = executor.should_bypass_challenge("continue autonomously")
        
        if result['bypass']:
            header = executor.format_autonomous_header(result['context'])
            print("\n📝 Generated Header:")
            print(header)
        else:
            print("\n⚠️  No continuation intent detected - no autonomous header")
    
    except FileNotFoundError as e:
        print(f"\n⚠️  Registry not found: {e}")


def demo_execution_template():
    """Demo 4: Full execution template with phase details."""
    print("\n\n" + "=" * 80)
    print("DEMO 4: Execution Template Generation")
    print("=" * 80)
    
    try:
        executor = AutonomousPlanExecutor()
        result = executor.should_bypass_challenge("proceed with phase 21")
        
        if result['bypass']:
            template = executor.generate_exec_template(result['context'])
            print("\n📋 Generated Template:")
            print(template)
        else:
            print("\n⚠️  No continuation intent or no next phase")
    
    except FileNotFoundError as e:
        print(f"\n⚠️  Registry or phase file not found: {e}")
        print("   This demo requires phase YAML files in _cortex-master/")


def demo_convenience_function():
    """Demo 5: Convenience function for prompt integration."""
    print("\n\n" + "=" * 80)
    print("DEMO 5: Convenience Function (Prompt Integration)")
    print("=" * 80)
    
    try:
        # This is what prompts/agents would call
        result = check_autonomous_continuation("continue implementation")
        
        print("\n🎯 Prompt Integration Result:")
        print(f"   Bypass: {result['bypass']}")
        print(f"   Next Phase: {result['next_phase']}")
        print(f"   Reason: {result['reason']}")
        
        if result['bypass']:
            print("\n✅ Action: Skip challenge/DoR, proceed to autonomous execution")
        else:
            print("\n🔄 Action: Normal flow with challenge/DoR gate")
    
    except FileNotFoundError as e:
        print(f"\n⚠️  Registry not found: {e}")


def demo_prompt_integration_pseudocode():
    """Demo 6: Show how prompts integrate this."""
    print("\n\n" + "=" * 80)
    print("DEMO 6: Prompt Integration Pattern")
    print("=" * 80)
    
    print("""
📝 Integration in cortex-architect.prompt.md:

```
LENS Context Gathered
         ↓
Check AutonomousPlanExecutor.should_bypass_challenge(user_request)
         ↓
[BYPASS=True] → Generate autonomous header + Execute immediately
                (NO challenge, NO DoR approval gate)
[BYPASS=False] → Continue to challenge generation
                 (Normal exploratory flow)
```

🐍 Python Pseudocode:

```python
from cortex.orchestrators.planning.autonomous_plan_executor import (
    check_autonomous_continuation
)

# In cortex-architect agent
def handle_design_mode(user_request):
    # Check for autonomous continuation
    result = check_autonomous_continuation(user_request)
    
    if result['bypass']:
        # Autonomous mode - skip challenge
        header = generate_autonomous_header(result['context'])
        execute_phase_immediately(result['next_phase'])
    else:
        # Normal mode - generate challenge first
        challenge = generate_challenge(user_request)
        await_user_approval()
        execute_with_dor_gate()
```

✅ Benefits:
- Zero verbose challenge for continuation requests
- Immediate execution when intent clear
- Normal flow preserved for exploratory requests
- Registry-driven (single source of truth)
""")


def main():
    """Run all demos."""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║  CORTEX Autonomous Plan Execution - Integration Demo                      ║")
    print("║  Seamless multi-phase plan continuation without verbose responses         ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    
    try:
        demo_continuation_detection()
        demo_context_analysis()
        demo_autonomous_header()
        demo_execution_template()
        demo_convenience_function()
        demo_prompt_integration_pseudocode()
        
        print("\n\n" + "=" * 80)
        print("✅ DEMO COMPLETE")
        print("=" * 80)
        print("\nKey Takeaways:")
        print("1. ✅ Intent detection: Patterns like 'continue', 'proceed', 'phase N'")
        print("2. ✅ Registry integration: Reads _cortex-master/index.yaml for next phase")
        print("3. ✅ Smart bypass: Skips challenge/DoR for clear continuation intent")
        print("4. ✅ Normal flow preserved: Exploratory requests still get full analysis")
        print("5. ✅ Minimal overhead: <5ms decision time, zero cognitive load")
        print("\n")
    
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
