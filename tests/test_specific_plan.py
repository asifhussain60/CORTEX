"""
Test script for specific master plan file

Tests with the cortex-rearchitecture-v1 plan.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.plan_file_resolver import resolve_plan_file
import json


def main():
    """Test with specific plan file."""
    
    print("=" * 80)
    print("🧪 Testing with cortex-rearchitecture-v1/00-master-plan.md")
    print("=" * 80)
    print()
    
    brain_path = Path.cwd() / "cortex-brain"
    
    # Use path relative to documents/planning/
    plan_path = "active/cortex-rearchitecture-v1/00-master-plan.md"
    
    print(f"Testing: {plan_path}")
    print("-" * 80)
    
    try:
        result = resolve_plan_file(plan_path, brain_path)
        
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
                print(f"   Summary: {summary[:150]}...")
            
            if 'progress' in data:
                progress = data['progress']
                print(f"   Progress: {progress.get('percentage', 'N/A')}% ({progress.get('phases_complete', 'N/A')})")
                print(f"   Actual Time: {progress.get('actual_time', 'N/A')}")
                print(f"   Elapsed Time: {progress.get('elapsed_time', 'N/A')}")
            
            if 'phases' in data:
                phases = data['phases']
                print(f"   Phases: {len(phases)} total")
                print()
                
                # Show all phases
                for phase in phases:
                    status = phase.get('status', '❓')
                    print(f"      Phase {phase.get('id')}: {phase.get('name')}")
                    print(f"         Status: {status}")
                    print(f"         Time: {phase.get('actual_time')} actual / {phase.get('elapsed_time')} elapsed")
            
            if 'continuation_prompt' in data and data['continuation_prompt']:
                prompt = data['continuation_prompt']
                print()
                print(f"   🔄 Continuation Prompt:")
                print(f"      {prompt[:200]}...")
            
            print()
            print("=" * 80)
            print("✅ Can now use this in orchestrators!")
            print("=" * 80)
            print()
            print("Example usage in orchestrator:")
            print("```python")
            print('plan_data = self.resolve_plan_file("#file:00-master-plan.md")')
            print('current_phase = plan_data["phases"][3]  # Phase 1.5.7')
            print('progress = plan_data["progress"]["percentage"]  # 16%')
            print("```")
            
        else:
            print(f"❌ FAILED: {result.error_message}")
    
    except Exception as e:
        print(f"💥 EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
