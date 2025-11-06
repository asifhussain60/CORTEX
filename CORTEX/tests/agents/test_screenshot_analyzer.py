"""
Tests for ScreenshotAnalyzer Agent

Validates screenshot analysis, UI element identification,
and test ID suggestion functionality.
"""

import pytest
from datetime import datetime
from CORTEX.src.cortex_agents.screenshot_analyzer import ScreenshotAnalyzer
from CORTEX.src.cortex_agents.base_agent import AgentRequest, AgentResponse
from CORTEX.src.cortex_agents.agent_types import IntentType


class TestScreenshotAnalyzerBasics:
    """Test basic ScreenshotAnalyzer functionality"""
    
    def test_analyzer_initialization(self, mock_tier_apis):
        """Test ScreenshotAnalyzer initialization"""
        analyzer = ScreenshotAnalyzer("Analyzer", **mock_tier_apis)
        
        assert analyzer.name == "Analyzer"
        assert analyzer.tier1 is not None
        assert analyzer.tier2 is not None
        assert analyzer.tier3 is not None
        assert len(analyzer.supported_intents) > 0
    
    def test_analyzer_can_handle_screenshot_intent(self, mock_tier_apis):
        """Test ScreenshotAnalyzer handles analyze_screenshot intents"""
        analyzer = ScreenshotAnalyzer("Analyzer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="analyze_screenshot",
            context={"image_base64": "data:image/png;base64,abc123"},
            user_message="Analyze this screenshot"
        )
        
        assert analyzer.can_handle(request) is True
    
    def test_analyzer_can_handle_find_test_ids_intent(self, mock_tier_apis):
        """Test ScreenshotAnalyzer handles find_test_ids intents"""
        analyzer = ScreenshotAnalyzer("Analyzer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="find_test_ids",
            context={"image_base64": "data:image/png;base64,abc123"},
            user_message="Find test IDs"
        )
        
        assert analyzer.can_handle(request) is True
    
    def test_analyzer_rejects_invalid_intent(self, mock_tier_apis):
        """Test ScreenshotAnalyzer rejects non-screenshot intents"""
        analyzer = ScreenshotAnalyzer("Analyzer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="code",
            context={},
            user_message="Write some code"
        )
        
        assert analyzer.can_handle(request) is False


class TestElementIdentification:
    """Test UI element identification"""
    
    def test_identify_login_page_elements(self, mock_tier_apis):
        """Test identification of login page elements"""
        analyzer = ScreenshotAnalyzer("Analyzer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="analyze_screenshot",
            context={"image_base64": "data:image/png;base64,abc123"},
            user_message="Analyze this login page screenshot"
        )
        
        response = analyzer.execute(request)
        
        assert response.success is True
        assert len(response.result["elements"]) > 0
        
        # Check for typical login elements
        element_types = [elem["type"] for elem in response.result["elements"]]
        assert "input" in element_types
        assert "button" in element_types
        
        # Check for suggested IDs
        suggested_ids = [elem["suggested_id"] for elem in response.result["elements"]]
        assert any("email" in id_str for id_str in suggested_ids)
        assert any("password" in id_str for id_str in suggested_ids)
        assert any("login" in id_str for id_str in suggested_ids)
    
    def test_identify_form_elements(self, mock_tier_apis):
        """Test identification of form elements"""
        analyzer = ScreenshotAnalyzer("Analyzer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="analyze_screenshot",
            context={"image_base64": "data:image/png;base64,xyz789"},
            user_message="Analyze this form screenshot"
        )
        
        response = analyzer.execute(request)
        
        assert response.success is True
        assert response.result["element_count"] > 0
        
        elements = response.result["elements"]
        assert any(elem["type"] == "input" for elem in elements)
        assert any(elem["type"] == "button" for elem in elements)
    
    def test_generic_element_identification(self, mock_tier_apis):
        """Test generic element identification"""
        analyzer = ScreenshotAnalyzer("Analyzer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="analyze_screenshot",
            context={"image_base64": "data:image/png;base64,generic"},
            user_message="Analyze this UI screenshot"
        )
        
        response = analyzer.execute(request)
        
        assert response.success is True
        assert len(response.result["elements"]) > 0


class TestTestIDGeneration:
    """Test test ID and selector generation"""
    
    def test_generate_test_ids(self, mock_tier_apis):
        """Test generation of test ID suggestions"""
        analyzer = ScreenshotAnalyzer("Analyzer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="find_test_ids",
            context={"image_base64": "data:image/png;base64,test123"},
            user_message="Find test IDs in login page"
        )
        
        response = analyzer.execute(request)
        
        assert response.success is True
        
        elements = response.result["elements"]
        for elem in elements:
            assert "suggested_id" in elem
            assert "selector" in elem
            # Check that suggested_id contains element type (btn, input, etc.)
            elem_type = elem["type"]
            suggested_id = elem["suggested_id"]
            assert elem_type in suggested_id or suggested_id.startswith("btn") or suggested_id.startswith("inp")
    
    def test_generate_playwright_selectors(self, mock_tier_apis):
        """Test Playwright selector generation"""
        analyzer = ScreenshotAnalyzer("Analyzer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="analyze_screenshot",
            context={"image_base64": "data:image/jpeg;base64,test456"},
            user_message="Generate Playwright selectors for login form"
        )
        
        response = analyzer.execute(request)
        
        assert response.success is True
        
        elements = response.result["elements"]
        for elem in elements:
            assert "selector" in elem
            # Check valid CSS selector format
            assert isinstance(elem["selector"], str)
            assert len(elem["selector"]) > 0
    
    def test_generate_recommendations(self, mock_tier_apis):
        """Test testing recommendations generation"""
        analyzer = ScreenshotAnalyzer("Analyzer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="analyze_screenshot",
            context={"image_base64": "data:image/png;base64,rec123"},
            user_message="Analyze form and give recommendations"
        )
        
        response = analyzer.execute(request)
        
        assert response.success is True
        assert "recommendations" in response.result
        assert len(response.result["recommendations"]) > 0
        assert isinstance(response.result["recommendations"], list)


class TestErrorHandling:
    """Test error handling"""
    
    def test_missing_image_data(self, mock_tier_apis):
        """Test handling of missing image data"""
        analyzer = ScreenshotAnalyzer("Analyzer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="analyze_screenshot",
            context={},  # No image data
            user_message="Analyze screenshot"
        )
        
        response = analyzer.execute(request)
        
        assert response.success is False
        assert "no image data" in response.message.lower()
    
    def test_invalid_image_format(self, mock_tier_apis):
        """Test handling of invalid image format"""
        analyzer = ScreenshotAnalyzer("Analyzer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="analyze_screenshot",
            context={"image_base64": "invalid_data"},
            user_message="Analyze screenshot"
        )
        
        response = analyzer.execute(request)
        
        assert response.success is False
        assert "invalid image format" in response.message.lower()
    
    def test_unsupported_image_type(self, mock_tier_apis):
        """Test handling of unsupported image type"""
        analyzer = ScreenshotAnalyzer("Analyzer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="analyze_screenshot",
            context={"image_base64": "data:image/gif;base64,abc123"},
            user_message="Analyze GIF screenshot"
        )
        
        response = analyzer.execute(request)
        
        assert response.success is False
        assert "invalid image format" in response.message.lower()
