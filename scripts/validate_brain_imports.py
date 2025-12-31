"""
Simple validation that BrainInterface imports are correct.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_imports():
    """Test that imports work correctly."""
    # Should work
    from src.brain import BrainInterface, WorkingMemory, KnowledgeGraph, DevelopmentContext
    print("✅ BrainInterface, WorkingMemory, KnowledgeGraph, DevelopmentContext imported")
    
    # Should fail
    try:
        from src.brain import GovernanceEngine
        print("❌ FAIL: GovernanceEngine should NOT be exported")
        return False
    except ImportError:
        print("✅ GovernanceEngine correctly removed from exports")
    
    # Verify BrainInterface has tier0 property
    assert hasattr(BrainInterface, 'tier0'), "BrainInterface should have tier0 property"
    print("✅ BrainInterface has tier0 property")
    
    # Verify tier0 imports BrainProtector internally (check source)
    import inspect
    tier0_source = inspect.getsource(BrainInterface.tier0.fget)
    assert 'BrainProtector' in tier0_source, "tier0 should use BrainProtector"
    assert 'GovernanceEngine' not in tier0_source, "tier0 should NOT use GovernanceEngine"
    print("✅ tier0 property uses BrainProtector (not GovernanceEngine)")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("BrainInterface Import Validation")
    print("=" * 60)
    print()
    
    try:
        if test_imports():
            print()
            print("=" * 60)
            print("🎉 All import validations passed!")
            print("=" * 60)
        else:
            sys.exit(1)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Validation failed: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)
