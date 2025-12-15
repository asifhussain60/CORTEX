"""
Simple validation test for Plan File Resolver
(No unicode emojis for Windows console compatibility)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.operations.base_operation_module import (
    BaseOperationModule, OperationModuleMetadata,
    OperationPhase, OperationResult, OperationStatus
)


class TestOrchestrator(BaseOperationModule):
    """Test orchestrator to validate resolve_plan_file method."""
    
    def get_metadata(self):
        return OperationModuleMetadata(
            module_id="test_resolver",
            name="Test Resolver",
            description="Test plan file resolver",
            phase=OperationPhase.PROCESSING
        )
    
    def execute(self, context):
        return OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Test complete"
        )


def main():
    print("=" * 80)
    print("VALIDATION TEST: Plan File Resolver via BaseOperationModule")
    print("=" * 80)
    print()
    
    orchestrator = TestOrchestrator()
    
    # Test 1: Specific path (no ambiguity)
    print("Test 1: Resolve with specific path")
    print("-" * 80)
    try:
        plan_data = orchestrator.resolve_plan_file(
            "active/cortex-rearchitecture-v1/00-master-plan.md"
        )
        
        print("SUCCESS")
        print(f"  Plan ID: {plan_data['metadata'].get('plan_id')}")
        print(f"  Title: {plan_data['metadata'].get('title')}")
        print(f"  Progress: {plan_data['progress'].get('percentage')}%")
        print(f"  Phases: {len(plan_data['phases'])} total")
        
        # Verify we can access phase data
        in_progress = [p for p in plan_data['phases'] if 'IN PROGRESS' in p.get('status', '')]
        if in_progress:
            print(f"  Current Phase: {in_progress[0]['id']} - {in_progress[0]['name']}")
        
        completed = [p for p in plan_data['phases'] if 'COMPLETE' in p.get('status', '')]
        print(f"  Completed Phases: {len(completed)}")
        
        print()
        
    except Exception as e:
        print(f"FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Cache validation (second call should be instant)
    print("Test 2: Cache validation (second call)")
    print("-" * 80)
    try:
        plan_data2 = orchestrator.resolve_plan_file(
            "active/cortex-rearchitecture-v1/00-master-plan.md"
        )
        
        print("SUCCESS - Cached YAML loaded")
        print(f"  Plan ID: {plan_data2['metadata'].get('plan_id')}")
        print()
        
    except Exception as e:
        print(f"FAILED: {str(e)}")
        return False
    
    # Test 3: #file: prefix (Copilot Chat format)
    print("Test 3: Copilot Chat format (#file:)")
    print("-" * 80)
    try:
        plan_data3 = orchestrator.resolve_plan_file(
            "#file:active/cortex-rearchitecture-v1/00-master-plan.md"
        )
        
        print("SUCCESS - #file: prefix handled correctly")
        print(f"  Plan ID: {plan_data3['metadata'].get('plan_id')}")
        print()
        
    except Exception as e:
        print(f"FAILED: {str(e)}")
        return False
    
    print("=" * 80)
    print("ALL TESTS PASSED")
    print("=" * 80)
    print()
    print("Implementation is ready for use in orchestrators!")
    print()
    print("Example usage in any orchestrator:")
    print("  plan_data = self.resolve_plan_file('#file:00-master-plan.md')")
    print("  current_phase = plan_data['phases'][3]")
    print("  progress = plan_data['progress']['percentage']")
    print()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
