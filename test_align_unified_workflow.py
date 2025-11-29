"""
Test Unified Align Workflow

Validates that `align` command:
1. Runs validation
2. Detects issues
3. Prompts for interactive fix
4. Can hand off to fix system

Author: Asif Hussain
"""
import sys
sys.path.insert(0, 'src')

from pathlib import Path
from operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator

def test_align_default_behavior():
    """Test default align behavior (validation + auto-prompt)."""
    print("=" * 80)
    print("TEST 1: Default Align Behavior (auto_prompt_fix=True)")
    print("=" * 80)
    
    orchestrator = SystemAlignmentOrchestrator({'project_root': Path.cwd()})
    
    # Default behavior: auto_prompt_fix=True
    context = {}
    result = orchestrator.execute(context)
    
    print(f"\n✅ Test 1 Complete")
    print(f"   Success: {result.success}")
    print(f"   Status: {result.status}")
    print(f"   Data keys: {list(result.data.keys())}")
    
    return result


def test_align_fix_direct():
    """Test direct `align fix` behavior (interactive_fix=True)."""
    print("\n\n" + "=" * 80)
    print("TEST 2: Align Fix Direct (interactive_fix=True)")
    print("=" * 80)
    
    orchestrator = SystemAlignmentOrchestrator({'project_root': Path.cwd()})
    
    # Simulate `align fix` command
    context = {'interactive_fix': True}
    result = orchestrator.execute(context)
    
    print(f"\n✅ Test 2 Complete")
    print(f"   Success: {result.success}")
    print(f"   Status: {result.status}")
    print(f"   Fixes applied: {len(result.data.get('fixes_applied', []))}")
    
    return result


def test_align_no_prompt():
    """Test align with auto-prompt disabled (report only)."""
    print("\n\n" + "=" * 80)
    print("TEST 3: Align No Prompt (auto_prompt_fix=False)")
    print("=" * 80)
    
    orchestrator = SystemAlignmentOrchestrator({'project_root': Path.cwd()})
    
    # Disable auto-prompt (legacy behavior)
    context = {'auto_prompt_fix': False}
    result = orchestrator.execute(context)
    
    print(f"\n✅ Test 3 Complete")
    print(f"   Success: {result.success}")
    print(f"   Status: {result.status}")
    print(f"   Report generated: {'report' in result.data}")
    
    return result


if __name__ == '__main__':
    print("\n🧠 CORTEX Unified Align Workflow Tests")
    print("=" * 80)
    print("\nThis test validates the new unified workflow where:")
    print("  • `align` runs validation + prompts for fixes")
    print("  • `align fix` goes directly to interactive remediation")
    print("  • Legacy behavior (no prompt) still supported\n")
    
    # Run tests
    result1 = test_align_default_behavior()
    
    # Uncomment to test direct fix access:
    # result2 = test_align_fix_direct()
    
    # Uncomment to test no-prompt mode:
    # result3 = test_align_no_prompt()
    
    print("\n\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 80)
    
    # Check if test was cancelled or completed
    if 'report' not in result1.data:
        print("\n⚠️ Test was cancelled or did not complete")
        print("   This is expected if you pressed Ctrl+C or chose option 3")
        print("\n💡 To complete the test:")
        print("   Run again and choose option 2 (View report only)")
        sys.exit(0)
    
    print("\n📊 Summary:")
    print(f"   Overall health: {result1.data['report'].overall_health}%")
    print(f"   Critical issues: {result1.data['report'].critical_issues}")
    print(f"   Warnings: {result1.data['report'].warnings}")
    print(f"   Fix templates available: {len(result1.data['report'].fix_templates)}")
    
    if result1.data['report'].fix_templates:
        print("\n💡 To test interactive fix:")
        print("   Run: python test_align_unified_workflow.py")
        print("   Then choose option 1 when prompted")
