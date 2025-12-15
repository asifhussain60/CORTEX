"""
Test script for Plan File Resolver

Tests automatic MD → YAML translation for orchestrators.
User references: "00-master-plan.md"
Internal processing: YAML (efficient)

Author: Asif Hussain
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.plan_file_resolver import resolve_plan_file
import json


def test_plan_file_resolver():
    """Test plan file resolver with actual master plan."""
    
    print("=" * 80)
    print("🧪 Testing Plan File Resolver")
    print("=" * 80)
    print()
    
    # Test cases
    test_cases = [
        "#file:00-master-plan.md",
        "00-master-plan.md",
        "cortex-brain/documents/planning/active/cortex-rearchitecture-v1/00-master-plan.md"
    ]
    
    brain_path = Path.cwd() / "cortex-brain"
    
    for i, test_ref in enumerate(test_cases, 1):
        print(f"Test Case {i}: {test_ref}")
        print("-" * 80)
        
        try:
            result = resolve_plan_file(test_ref, brain_path)
            
            if result.success:
                print(f"✅ SUCCESS")
                print(f"   Source Format: {result.source_format}")
                print(f"   Source Path: {result.source_path}")
                print(f"   YAML Path: {result.yaml_path}")
                print(f"   Cached: {'Yes' if result.cached else 'No'}")
                print(f"   Conversion Time: {result.conversion_time:.3f}s")
                print()
                
                # Show parsed data
                print("📊 Parsed Data:")
                data = result.data
                
                if 'metadata' in data:
                    print(f"   Plan ID: {data['metadata'].get('plan_id', 'N/A')}")
                    print(f"   Title: {data['metadata'].get('title', 'N/A')}")
                    print(f"   Date: {data['metadata'].get('date', 'N/A')}")
                    print(f"   Complexity: {data['metadata'].get('complexity_tier', 'N/A')}")
                
                if 'summary' in data:
                    summary = data['summary']
                    print(f"   Summary: {summary[:100]}..." if len(summary) > 100 else f"   Summary: {summary}")
                
                if 'progress' in data:
                    progress = data['progress']
                    print(f"   Progress: {progress.get('percentage', 'N/A')}% ({progress.get('phases_complete', 'N/A')})")
                    print(f"   Actual Time: {progress.get('actual_time', 'N/A')}")
                    print(f"   Elapsed Time: {progress.get('elapsed_time', 'N/A')}")
                
                if 'phases' in data:
                    phases = data['phases']
                    print(f"   Phases: {len(phases)} total")
                    
                    # Show first 3 phases
                    for phase in phases[:3]:
                        status_icon = {
                            '✅ COMPLETE': '✅',
                            '⏳ IN PROGRESS': '⏳',
                            '⏸️ PENDING': '⏸️',
                            '🆕 PLANNED': '🆕'
                        }.get(phase.get('status', ''), '❓')
                        
                        print(f"      {status_icon} Phase {phase.get('id')}: {phase.get('name')} - {phase.get('status')}")
                    
                    if len(phases) > 3:
                        print(f"      ... and {len(phases) - 3} more phases")
                
                if 'continuation_prompt' in data and data['continuation_prompt']:
                    prompt = data['continuation_prompt']
                    print(f"   Continuation: {prompt[:80]}..." if len(prompt) > 80 else f"   Continuation: {prompt}")
                
                print()
                
                # Show full YAML structure (for debugging)
                print("📄 Full YAML Structure:")
                print(json.dumps(data, indent=2, default=str)[:500] + "..." if len(json.dumps(data, default=str)) > 500 else json.dumps(data, indent=2, default=str))
                
            else:
                print(f"❌ FAILED: {result.error_message}")
        
        except Exception as e:
            print(f"💥 EXCEPTION: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print()
        print()
    
    print("=" * 80)
    print("✅ Testing Complete")
    print("=" * 80)


def test_with_base_operation_module():
    """Test resolver via BaseOperationModule interface."""
    
    print("=" * 80)
    print("🧪 Testing via BaseOperationModule")
    print("=" * 80)
    print()
    
    from src.operations.base_operation_module import (
        BaseOperationModule, OperationResult, OperationStatus,
        OperationPhase, OperationModuleMetadata
    )
    
    # Create a dummy module to test the resolve_plan_file method
    class TestModule(BaseOperationModule):
        def get_metadata(self):
            return OperationModuleMetadata(
                module_id="test_resolver",
                name="Test Resolver Module",
                description="Tests plan file resolver",
                phase=OperationPhase.PROCESSING
            )
        
        def execute(self, context):
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message="Test complete"
            )
    
    module = TestModule()
    
    try:
        print("Resolving: #file:00-master-plan.md")
        plan_data = module.resolve_plan_file("#file:00-master-plan.md")
        
        print(f"✅ Resolved successfully!")
        print(f"   Plan ID: {plan_data['metadata'].get('plan_id', 'N/A')}")
        print(f"   Progress: {plan_data['progress'].get('percentage', 'N/A')}%")
        print(f"   Phases: {len(plan_data['phases'])} total")
        print()
        
        # Test second call (should use cache)
        print("Resolving again (should use cache)...")
        plan_data2 = module.resolve_plan_file("#file:00-master-plan.md")
        print(f"✅ Resolved from cache!")
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("✅ BaseOperationModule Test Complete")
    print("=" * 80)


if __name__ == "__main__":
    test_plan_file_resolver()
    print("\n\n")
    test_with_base_operation_module()
