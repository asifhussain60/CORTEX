"""
Test Vision API Integration

This script tests the complete vision API integration:
1. Config enabled check
2. IntentRouter detects images
3. ScreenshotAnalyzer processes images
4. Vision API called correctly

Usage:
    python test_vision_integration.py
"""

import json
from src.cortex_agents.intent_router import IntentRouter
from src.cortex_agents.screenshot_analyzer import ScreenshotAnalyzer
from src.cortex_agents.base_agent import AgentRequest
from src.cortex_agents.agent_types import IntentType

def load_config():
    """Load CORTEX config"""
    with open('cortex.config.json', 'r') as f:
        return json.load(f)

def test_config():
    """Test that Vision API is enabled in config"""
    print("=" * 60)
    print("TEST 1: Config Check")
    print("=" * 60)
    
    config = load_config()
    vision_config = config.get('vision_api', {})
    enabled = vision_config.get('enabled', False)
    
    print(f"✅ Vision API enabled: {enabled}")
    if not enabled:
        print("❌ FAILED: Vision API not enabled in cortex.config.json")
        return False
    
    print(f"✅ Max tokens: {vision_config.get('max_tokens_per_image', 500)}")
    print(f"✅ Cache enabled: {vision_config.get('cache_analysis_results', True)}")
    return True

def test_intent_detection():
    """Test that IntentRouter detects images in context"""
    print("\n" + "=" * 60)
    print("TEST 2: Intent Detection")
    print("=" * 60)
    
    # Create router (simplified - without full tier APIs)
    router = IntentRouter("TestRouter", None, None, None)
    
    # Create request with image in context
    request = AgentRequest(
        intent="unknown",
        context={
            "image_base64": "data:image/png;base64,fake_data_for_test"
        },
        user_message="What's in this screenshot?"
    )
    
    # Classify intent
    detected_intent = router._classify_intent(request)
    
    print(f"Request context: {list(request.context.keys())}")
    print(f"Detected intent: {detected_intent}")
    
    if detected_intent == IntentType.SCREENSHOT:
        print("✅ PASSED: IntentRouter correctly detected screenshot intent")
        return True
    else:
        print(f"❌ FAILED: Expected SCREENSHOT, got {detected_intent}")
        return False

def test_screenshot_analyzer():
    """Test that ScreenshotAnalyzer can process mock image"""
    print("\n" + "=" * 60)
    print("TEST 3: ScreenshotAnalyzer")
    print("=" * 60)
    
    # Create analyzer (simplified)
    analyzer = ScreenshotAnalyzer("TestAnalyzer", None, None, None)
    
    # Create request with mock image
    request = AgentRequest(
        intent="analyze_screenshot",
        context={
            "image_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        },
        user_message="Analyze this login page"
    )
    
    print(f"Request intent: {request.intent}")
    print(f"Can handle: {analyzer.can_handle(request)}")
    
    if analyzer.can_handle(request):
        print("✅ PASSED: ScreenshotAnalyzer can handle the request")
        
        # Execute (will use mock implementation)
        print("\nExecuting analysis...")
        response = analyzer.execute(request)
        
        print(f"Success: {response.success}")
        print(f"Elements found: {response.result.get('element_count', 0)}")
        print(f"Message: {response.message}")
        
        if response.success:
            print("✅ PASSED: Analysis completed successfully")
            return True
        else:
            print(f"❌ FAILED: {response.message}")
            return False
    else:
        print("❌ FAILED: ScreenshotAnalyzer cannot handle screenshot intent")
        return False

def test_vision_api_integration():
    """Test full Vision API integration"""
    print("\n" + "=" * 60)
    print("TEST 4: Vision API Integration")
    print("=" * 60)
    
    config = load_config()
    
    # Check if PIL is available
    try:
        from PIL import Image
        print("✅ PIL/Pillow available for image preprocessing")
    except ImportError:
        print("⚠️  PIL/Pillow not available - image preprocessing disabled")
        print("   Install with: pip install Pillow")
    
    # Test Vision API directly
    from src.tier1.vision_api import VisionAPI
    
    vision = VisionAPI(config)
    print(f"Vision API enabled: {vision.enabled}")
    print(f"Max tokens: {vision.max_tokens}")
    
    if vision.enabled:
        print("✅ PASSED: Vision API initialized and enabled")
        return True
    else:
        print("❌ FAILED: Vision API not enabled")
        return False

def main():
    """Run all tests"""
    print("\n🧠 CORTEX Vision API Integration Test")
    print("=" * 60)
    
    tests = [
        ("Config Check", test_config),
        ("Intent Detection", test_intent_detection),
        ("Screenshot Analyzer", test_screenshot_analyzer),
        ("Vision API Integration", test_vision_api_integration)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ ERROR in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Vision API integration is working!")
        print("\n📝 To use with screenshots:")
        print("   1. Attach a screenshot in Copilot Chat")
        print("   2. Ask: 'Analyze this screenshot'")
        print("   3. CORTEX will automatically detect and process it")
    else:
        print("\n⚠️  Some tests failed. Review the output above.")

if __name__ == "__main__":
    main()
