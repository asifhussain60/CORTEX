"""
Tests for VisionAnalyzer.

CORE-008: TDD - Tests BEFORE code (written alongside implementation)
Tests verify:
- URL extraction from images
- UI element detection
- Issue detection (visual bugs, errors)
- Base64 and URL input handling
- MCP tool integration

Author: Asif Hussain
"""

import base64
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from cortex.brain.analysis.vision_analyzer import (
    VisionAnalyzer,
    VisionAnalysisResult,
    UIElement,
    ExtractedURL,
    DetectedIssue,
    ImageType,
    AnalysisDepth,
    analyze_image,
)


class TestVisionAnalyzerInit:
    """Tests for VisionAnalyzer initialization."""
    
    def test_default_initialization(self):
        """Test default initialization without API key."""
        analyzer = VisionAnalyzer()
        assert analyzer.default_depth == AnalysisDepth.STANDARD
        assert analyzer.api_key is None
    
    def test_custom_api_key(self):
        """Test initialization with custom API key."""
        analyzer = VisionAnalyzer(api_key="test-key")
        assert analyzer.api_key == "test-key"
    
    def test_custom_depth(self):
        """Test initialization with custom default depth."""
        analyzer = VisionAnalyzer(default_depth=AnalysisDepth.THOROUGH)
        assert analyzer.default_depth == AnalysisDepth.THOROUGH


class TestImageTypeDetection:
    """Tests for image type detection from filename."""
    
    def test_detect_error_screenshot(self):
        """Detect error type from filename."""
        analyzer = VisionAnalyzer()
        assert analyzer._detect_image_type("error_500.png") == ImageType.ERROR
        assert analyzer._detect_image_type("exception-trace.jpg") == ImageType.ERROR
        assert analyzer._detect_image_type("crash_dump.png") == ImageType.ERROR
    
    def test_detect_diagram(self):
        """Detect diagram type from filename."""
        analyzer = VisionAnalyzer()
        assert analyzer._detect_image_type("architecture_diagram.png") == ImageType.DIAGRAM
        assert analyzer._detect_image_type("flow-chart.jpg") == ImageType.DIAGRAM
        assert analyzer._detect_image_type("uml_class.png") == ImageType.DIAGRAM
    
    def test_detect_mockup(self):
        """Detect mockup type from filename."""
        analyzer = VisionAnalyzer()
        assert analyzer._detect_image_type("dashboard_mockup.png") == ImageType.MOCKUP
        assert analyzer._detect_image_type("wireframe-v1.jpg") == ImageType.MOCKUP
        assert analyzer._detect_image_type("figma_design.png") == ImageType.MOCKUP
    
    def test_detect_screenshot(self):
        """Detect screenshot type from filename."""
        analyzer = VisionAnalyzer()
        assert analyzer._detect_image_type("screenshot_2024.png") == ImageType.SCREENSHOT
        assert analyzer._detect_image_type("screen-capture.jpg") == ImageType.SCREENSHOT
    
    def test_unknown_type(self):
        """Return unknown for unrecognizable filenames."""
        analyzer = VisionAnalyzer()
        assert analyzer._detect_image_type("image.png") == ImageType.UNKNOWN
        assert analyzer._detect_image_type("random123.jpg") == ImageType.UNKNOWN


class TestPromptBuilding:
    """Tests for analysis prompt construction."""
    
    def test_quick_depth_prompt(self):
        """Test prompt for quick analysis."""
        analyzer = VisionAnalyzer()
        prompt = analyzer._build_prompt(
            image_type=ImageType.SCREENSHOT,
            depth=AnalysisDepth.QUICK,
            extract_urls=True,
            extract_elements=True,
            detect_issues=True,
        )
        assert "quickly" in prompt.lower()
        assert "user interface" in prompt.lower()
    
    def test_thorough_depth_prompt(self):
        """Test prompt for thorough analysis."""
        analyzer = VisionAnalyzer()
        prompt = analyzer._build_prompt(
            image_type=ImageType.ERROR,
            depth=AnalysisDepth.THOROUGH,
            extract_urls=True,
            extract_elements=True,
            detect_issues=True,
        )
        assert "exhaustive" in prompt.lower()
        assert "error" in prompt.lower()
    
    def test_skip_url_extraction(self):
        """Test prompt skips URL extraction when disabled."""
        analyzer = VisionAnalyzer()
        prompt = analyzer._build_prompt(
            image_type=ImageType.SCREENSHOT,
            depth=AnalysisDepth.STANDARD,
            extract_urls=False,
            extract_elements=True,
            detect_issues=True,
        )
        assert "Skip URL extraction" in prompt


class TestVisionAnalysisResult:
    """Tests for VisionAnalysisResult dataclass."""
    
    def test_to_dict_conversion(self):
        """Test conversion to dict."""
        result = VisionAnalysisResult(
            status="success",
            image_type=ImageType.SCREENSHOT,
            analysis_depth=AnalysisDepth.STANDARD,
            urls=[ExtractedURL(url="https://example.com", context="address bar", url_type="navigation")],
            ui_elements=[UIElement(element_type="button", text="Submit", confidence=0.95)],
            issues=[DetectedIssue(issue_type="visual_bug", severity="medium", description="Misaligned button")],
            text_content=["Welcome to the app"],
        )
        
        d = result.to_dict()
        
        assert d["status"] == "success"
        assert d["image_type"] == "screenshot"
        assert d["analysis_depth"] == "standard"
        assert len(d["urls"]) == 1
        assert d["urls"][0]["url"] == "https://example.com"
        assert len(d["ui_elements"]) == 1
        assert d["ui_elements"][0]["type"] == "button"
        assert len(d["issues"]) == 1
        assert d["issues"][0]["severity"] == "medium"
    
    def test_empty_result(self):
        """Test empty result conversion."""
        result = VisionAnalysisResult(
            status="success",
            image_type=ImageType.UNKNOWN,
            analysis_depth=AnalysisDepth.QUICK,
        )
        
        d = result.to_dict()
        
        assert d["urls"] == []
        assert d["ui_elements"] == []
        assert d["issues"] == []


class TestResponseParsing:
    """Tests for Vision API response parsing."""
    
    def test_parse_urls_as_strings(self):
        """Parse URLs when returned as simple strings."""
        analyzer = VisionAnalyzer()
        
        response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "urls": ["https://example.com", "https://api.example.com/v1"],
                        "elements": [],
                        "issues": [],
                        "text": [],
                    })
                }
            }],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        }
        
        result = analyzer._parse_response(response, ImageType.SCREENSHOT, AnalysisDepth.STANDARD)
        
        assert result.status == "success"
        assert len(result.urls) == 2
        assert result.urls[0].url == "https://example.com"
    
    def test_parse_urls_as_dicts(self):
        """Parse URLs when returned as objects."""
        analyzer = VisionAnalyzer()
        
        response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "urls": [
                            {"url": "https://example.com", "context": "address bar", "type": "navigation"},
                        ],
                        "elements": [],
                        "issues": [],
                        "text": [],
                    })
                }
            }],
            "usage": {},
        }
        
        result = analyzer._parse_response(response, ImageType.SCREENSHOT, AnalysisDepth.STANDARD)
        
        assert len(result.urls) == 1
        assert result.urls[0].url == "https://example.com"
        assert result.urls[0].context == "address bar"
        assert result.urls[0].url_type == "navigation"
    
    def test_parse_ui_elements(self):
        """Parse UI elements from response."""
        analyzer = VisionAnalyzer()
        
        response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "urls": [],
                        "elements": [
                            {"type": "button", "text": "Submit", "id": "submit-btn", "confidence": 0.95},
                            {"type": "input", "text": "", "id": "email-input"},
                        ],
                        "issues": [],
                        "text": [],
                    })
                }
            }],
            "usage": {},
        }
        
        result = analyzer._parse_response(response, ImageType.SCREENSHOT, AnalysisDepth.STANDARD)
        
        assert len(result.ui_elements) == 2
        assert result.ui_elements[0].element_type == "button"
        assert result.ui_elements[0].text == "Submit"
        assert result.ui_elements[0].element_id == "submit-btn"
        assert result.ui_elements[0].confidence == 0.95
    
    def test_parse_issues(self):
        """Parse detected issues from response."""
        analyzer = VisionAnalyzer()
        
        response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "urls": [],
                        "elements": [],
                        "issues": [
                            {
                                "type": "visual_bug",
                                "severity": "high",
                                "description": "Button overflow",
                                "location": "top-right",
                                "suggestion": "Reduce padding",
                            },
                        ],
                        "text": [],
                    })
                }
            }],
            "usage": {},
        }
        
        result = analyzer._parse_response(response, ImageType.SCREENSHOT, AnalysisDepth.STANDARD)
        
        assert len(result.issues) == 1
        assert result.issues[0].issue_type == "visual_bug"
        assert result.issues[0].severity == "high"
        assert result.issues[0].suggestion == "Reduce padding"
    
    def test_parse_error_on_invalid_json(self):
        """Handle invalid JSON in response."""
        analyzer = VisionAnalyzer()
        
        response = {
            "choices": [{
                "message": {
                    "content": "not valid json"
                }
            }],
            "usage": {},
        }
        
        result = analyzer._parse_response(response, ImageType.SCREENSHOT, AnalysisDepth.STANDARD)
        
        assert "parse_error" in result.status


class TestMCPToolIntegration:
    """Tests for MCP tool integration."""
    
    def test_cortex_vision_analyze_missing_input(self):
        """Test error when no image input provided."""
        from cortex.mcp.tools.lens_tools import cortex_vision_analyze
        
        result = cortex_vision_analyze()
        
        assert result["status"] == "error"
        assert "Must provide" in result["error"]
    
    @patch("cortex.brain.analysis.vision_analyzer.VisionAnalyzer.analyze_base64")
    def test_cortex_vision_analyze_base64(self, mock_analyze):
        """Test MCP tool with base64 input."""
        from cortex.mcp.tools.lens_tools import cortex_vision_analyze
        
        mock_result = VisionAnalysisResult(
            status="success",
            image_type=ImageType.SCREENSHOT,
            analysis_depth=AnalysisDepth.STANDARD,
        )
        mock_analyze.return_value = mock_result
        
        result = cortex_vision_analyze(
            image_data="base64encodeddata",
            image_type="screenshot",
            analysis_depth="standard",
        )
        
        assert result["status"] == "success"
        mock_analyze.assert_called_once()
    
    @patch("cortex.brain.analysis.vision_analyzer.VisionAnalyzer.analyze_url")
    def test_cortex_vision_analyze_url(self, mock_analyze):
        """Test MCP tool with URL input."""
        from cortex.mcp.tools.lens_tools import cortex_vision_analyze
        
        mock_result = VisionAnalysisResult(
            status="success",
            image_type=ImageType.SCREENSHOT,
            analysis_depth=AnalysisDepth.STANDARD,
        )
        mock_analyze.return_value = mock_result
        
        result = cortex_vision_analyze(
            image_url="https://example.com/image.png",
            image_type="screenshot",
        )
        
        assert result["status"] == "success"
        mock_analyze.assert_called_once()


class TestLENSOrchestratorVisionIntegration:
    """Tests for LENSOrchestrator vision integration."""
    
    def test_analyze_image_method_exists(self):
        """Verify analyze_image method exists on LENSOrchestrator."""
        from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
        
        orchestrator = LENSOrchestrator(repo_path=Path("."))
        assert hasattr(orchestrator, "analyze_image")
        assert callable(orchestrator.analyze_image)
    
    def test_analyze_with_vision_method_exists(self):
        """Verify analyze_with_vision method exists."""
        from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
        
        orchestrator = LENSOrchestrator(repo_path=Path("."))
        assert hasattr(orchestrator, "analyze_with_vision")
        assert callable(orchestrator.analyze_with_vision)
    
    def test_lens_context_has_vision_field(self):
        """Verify LENSContext includes vision_analysis field."""
        from cortex.orchestrators.support.lens_orchestrator import LENSContext
        
        context = LENSContext()
        assert hasattr(context, "vision_analysis")
    
    def test_lens_context_to_dict_includes_vision(self):
        """Verify to_dict includes vision_analysis when present."""
        from cortex.orchestrators.support.lens_orchestrator import LENSContext
        
        context = LENSContext(
            vision_analysis={"urls": [{"url": "https://example.com"}]}
        )
        
        d = context.to_dict()
        assert "vision_analysis" in d
        assert d["vision_analysis"]["urls"][0]["url"] == "https://example.com"
    
    def test_lens_context_to_dict_excludes_empty_vision(self):
        """Verify to_dict excludes vision_analysis when empty."""
        from cortex.orchestrators.support.lens_orchestrator import LENSContext
        
        context = LENSContext()
        d = context.to_dict()
        assert "vision_analysis" not in d


class TestConvenienceFunction:
    """Tests for analyze_image convenience function."""
    
    @patch("cortex.brain.analysis.vision_analyzer.VisionAnalyzer.analyze_base64")
    def test_analyze_image_base64(self, mock_analyze):
        """Test convenience function with base64 input."""
        mock_result = VisionAnalysisResult(
            status="success",
            image_type=ImageType.UNKNOWN,
            analysis_depth=AnalysisDepth.STANDARD,
        )
        mock_analyze.return_value = mock_result
        
        result = analyze_image("notapathorurlsobase64", depth="standard")
        
        assert result["status"] == "success"
        mock_analyze.assert_called_once()
    
    @patch("cortex.brain.analysis.vision_analyzer.VisionAnalyzer.analyze_url")
    def test_analyze_image_url(self, mock_analyze):
        """Test convenience function with URL input."""
        mock_result = VisionAnalysisResult(
            status="success",
            image_type=ImageType.UNKNOWN,
            analysis_depth=AnalysisDepth.QUICK,
        )
        mock_analyze.return_value = mock_result
        
        result = analyze_image("https://example.com/img.png", depth="quick")
        
        assert result["status"] == "success"
        mock_analyze.assert_called_once()
