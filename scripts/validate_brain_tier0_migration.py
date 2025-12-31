"""
Validation script for BrainInterface.tier0 → BrainProtector migration

Tests that BrainInterface.tier0 properly loads BrainProtector.
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_brain_interface_tier0():
    """Test that BrainInterface.tier0 loads BrainProtector correctly."""
    from src.brain import BrainInterface
    from src.tier0.brain_protector import BrainProtector
    
    # Create brain interface
    workspace_root = Path(__file__).parent.parent
    brain = BrainInterface(workspace_root)
    
    # Test tier0 lazy loading
    tier0 = brain.tier0
    
    # Verify it's BrainProtector instance
    assert tier0 is not None, "tier0 should not be None"
    assert isinstance(tier0, BrainProtector), f"tier0 should be BrainProtector, got {type(tier0)}"
    
    # Verify BrainProtector is functional
    assert hasattr(tier0, 'check_protection'), "BrainProtector should have check_protection method"
    assert hasattr(tier0, 'rules'), "BrainProtector should have rules attribute"
    
    print("✅ BrainInterface.tier0 correctly loads BrainProtector")
    print(f"✅ BrainProtector loaded from: {tier0.brain_root}")
    print(f"✅ Total rules: {len(tier0.rules)}")
    
    return True

def test_brain_imports():
    """Test that imports work correctly."""
    from src.brain import BrainInterface, WorkingMemory, KnowledgeGraph, DevelopmentContext
    
    # Verify GovernanceEngine is NOT exported
    try:
        from src.brain import GovernanceEngine
        print("❌ GovernanceEngine should NOT be exported from src.brain")
        return False
    except ImportError:
        print("✅ GovernanceEngine correctly removed from exports")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("BrainInterface.tier0 Migration Validation")
    print("=" * 60)
    print()
    
    try:
        # Test imports
        if not test_brain_imports():
            sys.exit(1)
        
        print()
        
        # Test tier0 loading
        if not test_brain_interface_tier0():
            sys.exit(1)
        
        print()
        print("=" * 60)
        print("🎉 All validation tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Validation failed: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)
