#!/usr/bin/env python3
"""
Validate CORTEX publish package - Test module imports and config loading
"""

import sys
from pathlib import Path

# Add publish folder to path
sys.path.insert(0, str(Path(__file__).parent))

def test_module_imports():
    """Test that core CORTEX modules can be imported"""
    
    print("=" * 80)
    print("CORTEX Publish Folder Validation")
    print("=" * 80)
    
    modules_to_test = [
        ("Tier 0 Brain Protector", "src.tier0.brain_protector", "BrainProtector"),
        ("Tier 1 Conversation API", "src.tier1.conversation_api", "ConversationAPI"),
        ("Tier 2 Knowledge Graph", "src.tier2.knowledge_graph_api", "KnowledgeGraphAPI"),
        ("Operations Orchestrator", "src.operations.operations_orchestrator", "OperationsOrchestrator"),
        ("Plugin Registry", "src.plugins.plugin_registry", "PluginRegistry"),
        ("Cleanup Orchestrator", "src.plugins.cleanup_orchestrator", "CleanupOrchestrator"),
        ("Base Operation Module", "src.operations.base_operation_module", "ExecutionMode"),
    ]
    
    print("\n📦 Testing Module Imports:")
    passed = 0
    failed = 0
    
    for name, module_path, class_name in modules_to_test:
        try:
            parts = module_path.rsplit('.', 1)
            module = __import__(parts[0], fromlist=[parts[1]])
            submodule = getattr(module, parts[1])
            cls = getattr(submodule, class_name)
            print(f"  ✅ {name}: {class_name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            failed += 1
    
    print(f"\n  Results: {passed} passed, {failed} failed")
    
    return failed == 0

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

def test_execution_mode():
    """Verify ExecutionMode enum only has LIVE (no DRY_RUN)"""
    from src.operations.base_operation_module import ExecutionMode
    
    print("\n⚙️  Execution Mode Validation:")
    modes = [m for m in dir(ExecutionMode) if not m.startswith('_')]
    print(f"  Available modes: {modes}")
    
    if 'LIVE' in modes:
        print("  ✅ LIVE mode available")
    if 'DRY_RUN' in modes:
        print("  ❌ DRY_RUN mode still exists (should be removed!)")
        return False
    else:
        print("  ✅ DRY_RUN mode removed (live-only mode confirmed)")
    
    return True

def test_ksessions_detection():
    """Test that KSESSIONS directory is accessible"""
    ksessions = Path("D:/PROJECTS/KSESSIONS")
    
    print("\n🔍 KSESSIONS Workspace Detection:")
    print(f"  Path: {ksessions}")
    
    if ksessions.exists():
        print(f"  Status: ✅ EXISTS")
        
        # Count some files
        py_files = list(ksessions.rglob("*.py"))
        md_files = list(ksessions.rglob("*.md"))
        
        print(f"  Python files: {len(py_files)}")
        print(f"  Markdown files: {len(md_files)}")
        return True
    else:
        print(f"  Status: ❌ NOT FOUND")
        return False

if __name__ == "__main__":
    try:
        results = []
        
        results.append(test_module_imports())
        results.append(test_operations_config())
        results.append(test_execution_mode())
        results.append(test_ksessions_detection())
        
        print("\n" + "=" * 80)
        
        if all(results):
            print("🎉 All validation tests passed!")
            print("✅ CORTEX publish package working correctly")
            print("✅ Live-only mode confirmed (no DRY_RUN)")
            print("✅ KSESSIONS workspace accessible")
            print("=" * 80)
            sys.exit(0)
        else:
            print("⚠️  Some tests failed - see details above")
            print("=" * 80)
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
