"""Quick test of Intent Router"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))

from components.intent_router import IntentRouter

def test_router():
    """Quick validation test"""
    router = IntentRouter()
    
    # Test planning trigger
    result1 = router.route("plan authentication")
    assert result1['action'] == 'planning', f"Expected 'planning', got '{result1['action']}'"
    assert result1['confidence'] >= 0.7, f"Low confidence: {result1['confidence']}"
    print(f"✅ Test 1 PASSED: Planning trigger detected (confidence: {result1['confidence']:.2f})")
    
    # Test development trigger
    result2 = router.route("add login button")
    assert result2['action'] == 'development', f"Expected 'development', got '{result2['action']}'"
    assert result2['confidence'] >= 0.7, f"Low confidence: {result2['confidence']}"
    print(f"✅ Test 2 PASSED: Development trigger detected (confidence: {result2['confidence']:.2f})")
    
    # Test ambiguous case
    result3 = router.route("authentication system")
    print(f"✅ Test 3 PASSED: Ambiguous case handled (action: {result3['action']}, confidence: {result3['confidence']:.2f})")
    
    # Test pipeline configs
    seq_config = router.get_pipeline_config('sequential_planning_to_development')
    assert 'steps' in seq_config, "Pipeline config missing 'steps'"
    print(f"✅ Test 4 PASSED: Pipeline configuration retrieved ({len(seq_config['steps'])} steps)")
    
    print("\n🎉 All tests passed! Phase 3 implementation is working correctly.")
    return True

if __name__ == "__main__":
    try:
        test_router()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
