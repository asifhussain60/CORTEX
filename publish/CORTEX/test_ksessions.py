#!/usr/bin/env python3
"""
Test CORTEX publish package against KSESSIONS workspace
"""

import sys
from pathlib import Path

# Add publish folder to path
sys.path.insert(0, str(Path(__file__).parent))

def test_tier3_api():
    """Test Tier 3 Development Context API"""
    from src.tier3.context_intelligence import ContextIntelligence
    
    ksessions_path = Path("D:/PROJECTS/KSESSIONS")
    
    print("=" * 80)
    print("CORTEX Publish Folder Test - KSESSIONS Workspace")
    print("=" * 80)
    
    # Initialize Context Intelligence
    print(f"\n� Analyzing workspace: {ksessions_path}")
    context = ContextIntelligence(str(ksessions_path))
    
    # Get basic info
    print("\n📊 Workspace Analysis:")
    print(f"  Workspace Path: {ksessions_path}")
    print(f"  Context Intelligence initialized: ✅")
    
    # Test that the module loads
    print(f"  Module type: {type(context).__name__}")
    
    print("\n✅ CORTEX Tier 3 Context Intelligence working from publish folder!")
    print("=" * 80)
    
    return True

def test_operations_config():
    """Test operations configuration loads correctly"""
    import yaml
    
    config_path = Path(__file__).parent / "cortex-operations.yaml"
    
    print("\n📋 Operations Configuration:")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    operations = config.get('operations', {})
    print(f"  Loaded Operations: {len(operations)}")
    
    for op_name in list(operations.keys())[:5]:
        print(f"    - {op_name}")
    
    print("  ✅ Operations config loaded successfully!")
    
    return True

if __name__ == "__main__":
    try:
        test_tier3_api()
        test_operations_config()
        print("\n🎉 All tests passed! CORTEX publish package working correctly.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
