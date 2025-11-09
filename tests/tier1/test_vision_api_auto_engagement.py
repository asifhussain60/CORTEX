"""
Tests for automatic Vision API engagement when images are attached.

Validates that:
1. IntentRouter detects images in request context
2. Routes to SCREENSHOT intent type
3. ScreenshotAnalyzer receives image data
4. Vision API is called automatically
"""
import pytest
import base64
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.cortex_agents.intent_router import IntentRouter, IntentType
from src.cortex_agents.base_agent import AgentRequest
from src.cortex_agents.screenshot_analyzer import ScreenshotAnalyzer
from src.tier1.vision_api import VisionAPI


class TestVisionAPIAutoEngagement:
    """Test suite for automatic Vision API engagement."""
    
    @pytest.fixture
    def sample_image_base64(self):
        """Create a sample base64-encoded image."""
        # 1x1 red PNG
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    @pytest.fixture
    def intent_router(self):
        """Create IntentRouter instance."""
        tier1_api = Mock()
        tier2_api = Mock()
        tier3_api = Mock()
        return IntentRouter("Router", tier1_api, tier2_api, tier3_api)
    
    def test_intent_router_detects_image_base64(self, intent_router, sample_image_base64):
        """Test that IntentRouter detects base64 image in context."""
        request = AgentRequest(
            intent="analyze_screenshot",
            context={"image_base64": f"data:image/png;base64,{sample_image_base64}"},
            user_message="What's in this image?"
        )
        
        intent = intent_router._classify_intent(request)
        
        assert intent == IntentType.SCREENSHOT, \
            f"Expected SCREENSHOT intent, got {intent}"
    
    def test_intent_router_detects_image_path(self, intent_router):
        """Test that IntentRouter detects image file path in context."""
        request = AgentRequest(
            intent="analyze_screenshot",
            context={"image_path": "/path/to/screenshot.png"},
            user_message="What's in this image?"
        )
        
        intent = intent_router._classify_intent(request)
        
        assert intent == IntentType.SCREENSHOT, \
            f"Expected SCREENSHOT intent, got {intent}"
    
    def test_intent_router_detects_image_data(self, intent_router, sample_image_base64):
        """Test that IntentRouter detects raw image data in context."""
        request = AgentRequest(
            intent="analyze_screenshot",
            context={"image_data": base64.b64decode(sample_image_base64)},
            user_message="What's in this image?"
        )
        
        intent = intent_router._classify_intent(request)
        
        assert intent == IntentType.SCREENSHOT, \
            f"Expected SCREENSHOT intent, got {intent}"
    
    def test_intent_router_detects_screenshot_keyword(self, intent_router):
        """Test that IntentRouter detects 'screenshot' keyword in context."""
        request = AgentRequest(
            intent="analyze",
            context={"screenshot": True},
            user_message="Analyze this"
        )
        
        intent = intent_router._classify_intent(request)
        
        assert intent == IntentType.SCREENSHOT, \
            f"Expected SCREENSHOT intent, got {intent}"
    
    @patch('src.tier1.vision_api.VisionAPI._call_vision_api')
    def test_screenshot_analyzer_receives_image(self, mock_api, sample_image_base64):
        """Test that ScreenshotAnalyzer receives and processes image data."""
        # Mock Vision API response
        mock_api.return_value = {
            "analysis": "Button found at (100, 200)",
            "elements": ["button"],
            "colors": ["#3B82F6"]
        }
        
        # Create mocks
        tier1_api = Mock()
        tier2_api = Mock()
        tier3_api = Mock()
        
        # Create analyzer
        analyzer = ScreenshotAnalyzer("Analyzer", tier1_api, tier2_api, tier3_api)
        
        # Create request with image
        request = AgentRequest(
            intent="analyze_screenshot",
            context={"image_base64": f"data:image/png;base64,{sample_image_base64}"},
            user_message="Find buttons"
        )
        
        # Execute
        response = analyzer.execute(request)
        
        # Verify Vision API was called
        assert mock_api.called, "Vision API was not called"
        assert response.success, f"Analysis failed: {response.error}"
        assert "button" in str(response.result).lower(), \
            "Analysis result doesn't mention button"
    
    @patch('src.tier1.vision_api.VisionAPI._call_vision_api')
    def test_vision_api_auto_engagement_end_to_end(self, mock_api, sample_image_base64):
        """End-to-end test: Image attachment → IntentRouter → ScreenshotAnalyzer → Vision API."""
        # Mock Vision API response
        mock_api.return_value = {
            "analysis": "UI mockup with purple button",
            "elements": ["button", "header", "input"],
            "colors": ["#7C3AED", "#FFFFFF"],
            "test_ids": ["btn-submit", "header-title", "input-email"]
        }
        
        # Create system
        tier1_api = Mock()
        tier2_api = Mock()
        tier3_api = Mock()
        
        router = IntentRouter("Router", tier1_api, tier2_api, tier3_api)
        analyzer = ScreenshotAnalyzer("Analyzer", tier1_api, tier2_api, tier3_api)
        
        # Simulate user attaching screenshot
        user_request = AgentRequest(
            intent="fix_button_color",
            context={"image_base64": f"data:image/png;base64,{sample_image_base64}"},
            user_message="Fix the purple button color"
        )
        
        # Step 1: Router detects image
        detected_intent = router._classify_intent(user_request)
        assert detected_intent == IntentType.SCREENSHOT, \
            "Router failed to detect image attachment"
        
        # Step 2: Analyzer processes image
        analysis = analyzer.execute(user_request)
        
        # Step 3: Verify Vision API was auto-engaged
        assert mock_api.called, "Vision API was not automatically engaged"
        assert analysis.success, f"Analysis failed: {analysis.error}"
        
        # Step 4: Verify analysis contains useful data
        result_str = str(analysis.result).lower()
        assert "button" in result_str, "Analysis missing button detection"
        assert "purple" in result_str or "#7c3aed" in result_str, \
            "Analysis missing color detection"
    
    def test_vision_api_not_engaged_without_image(self, intent_router):
        """Test that Vision API is NOT engaged when no image is attached."""
        request = AgentRequest(
            intent="fix_button_color",
            context={},  # No image
            user_message="Fix the button color"
        )
        
        intent = intent_router._classify_intent(request)
        
        assert intent != IntentType.SCREENSHOT, \
            "Router incorrectly detected SCREENSHOT intent without image"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
