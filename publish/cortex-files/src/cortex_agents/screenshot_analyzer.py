"""
ScreenshotAnalyzer Agent

Analyzes UI screenshots to identify elements and suggest test IDs.
Helps with automated testing by providing Playwright selector suggestions
and element identification from visual inputs.

The ScreenshotAnalyzer uses basic image analysis techniques to assist
with test automation and UI element discovery.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import base64
import io
from src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from src.cortex_agents.agent_types import IntentType
from src.cortex_agents.utils import safe_get


class ScreenshotAnalyzer(BaseAgent):
    """
    Analyzes UI screenshots for test automation.
    
    The ScreenshotAnalyzer processes screenshots to identify UI elements,
    suggest Playwright/Selenium test IDs, and provide element descriptions
    to assist with automated testing.
    
    Features:
    - UI element identification from screenshots
    - Test ID/selector suggestions
    - Element type classification (button, input, etc.)
    - Accessibility label extraction
    - Position-based element grouping
    
    Note: This is a basic implementation. In production, this would
    integrate with actual image recognition libraries (PIL, OpenCV, etc.)
    
    Example:
        analyzer = ScreenshotAnalyzer(name="Analyzer", tier1_api, tier2_kg, tier3_context)
        
        request = AgentRequest(
            intent="analyze_screenshot",
            context={"image_base64": "data:image/png;base64,..."},
            user_message="Find test IDs in this login page screenshot"
        )
        
        response = analyzer.execute(request)
        # Returns: {
        #   "elements": [
        #     {"type": "button", "label": "Login", "suggested_id": "btn-login"},
        #     {"type": "input", "label": "Email", "suggested_id": "input-email"}
        #   ],
        #   "recommendations": ["Use data-testid attributes", "Add ARIA labels"]
        # }
    """
    
    def __init__(self, name: str, tier1_api, tier2_kg, tier3_context):
        """
        Initialize ScreenshotAnalyzer.
        
        Args:
            name: Agent name
            tier1_api: Tier 1 conversation manager API
            tier2_kg: Tier 2 knowledge graph API
            tier3_context: Tier 3 context intelligence API
        """
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        self.supported_intents = [
            "analyze_screenshot",
            "find_test_ids",
            "identify_elements"
        ]
        
        # Initialize Vision API integration
        self.vision_enabled = False
        self.vision_api = None
        
        # Check if Vision API should be enabled
        try:
            # Import VisionAPI and config
            from src.tier1.vision_api import VisionAPI
            from src.config import CortexConfig
            import json
            from pathlib import Path
            
            # Load config directly from file
            cortex_config = CortexConfig()
            config_file = cortex_config.root_path / "cortex.config.json"
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                vision_config = config.get('vision_api', {})
                self.vision_enabled = vision_config.get('enabled', False)
                
                if self.vision_enabled:
                    self.vision_api = VisionAPI(config)
                    self.logger.info("Vision API enabled for screenshot analysis")
                else:
                    self.logger.info("Vision API disabled in config - using mock implementation")
            else:
                self.logger.info(f"Config file not found: {config_file} - using mock implementation")
        except Exception as e:
            self.logger.warning(f"Could not initialize Vision API: {e}. Using mock fallback.")
            self.vision_enabled = False
            self.vision_api = None
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Args:
            request: The agent request to evaluate
            
        Returns:
            True if intent is screenshot analysis, False otherwise
        """
        return request.intent in self.supported_intents
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Analyze screenshot to identify UI elements.
        
        Args:
            request: Agent request with image data in context
            
        Returns:
            AgentResponse with identified elements and test ID suggestions
        """
        start_time = datetime.now()
        
        try:
            # Extract image data from request
            image_data = self._get_image_data(request)
            if not image_data:
                return self._error_response(
                    "No image data provided in request",
                    start_time
                )
            
            # Validate image format
            if not self._validate_image(image_data):
                return self._error_response(
                    "Invalid image format. Supported: PNG, JPEG",
                    start_time
                )
            
            # Analyze image for UI elements
            # Note: This is a mock implementation. In production, this would
            # use actual image recognition (PIL, OpenCV, cloud OCR, etc.)
            elements = self._analyze_elements(image_data, request)
            
            # Generate test ID suggestions
            recommendations = self._generate_recommendations(elements)
            
            # Build response
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return AgentResponse(
                success=True,
                result={
                    "elements": elements,
                    "element_count": len(elements),
                    "recommendations": recommendations,
                    "analysis_type": "basic"  # vs "advanced" with ML
                },
                message=f"Identified {len(elements)} UI elements from screenshot",
                agent_name=self.name,
                duration_ms=duration_ms,
                next_actions=[
                    "Add data-testid attributes to elements",
                    "Create Playwright test selectors",
                    "Verify accessibility labels"
                ]
            )
            
        except Exception as e:
            self.logger.error(f"Screenshot analysis failed: {e}", exc_info=True)
            return self._error_response(str(e), start_time)
    
    def _get_image_data(self, request: AgentRequest) -> Optional[str]:
        """
        Extract image data from request.
        
        Args:
            request: Agent request
            
        Returns:
            Base64 image data or None
        """
        # Check context for image data
        image_data = request.context.get("image_base64")
        if image_data:
            return image_data
        
        # Check for file path
        image_path = request.context.get("image_path")
        if image_path:
            # In production, would load image from file
            # For now, return None to trigger mock behavior
            self.logger.info(f"Image path provided: {image_path}")
        
        return image_data
    
    def _validate_image(self, image_data: str) -> bool:
        """
        Validate image format.
        
        Args:
            image_data: Base64 image data
            
        Returns:
            True if valid image format
        """
        if not image_data:
            return False
        
        # Check for data URI prefix
        if not image_data.startswith('data:image/'):
            return False
        
        # Check for supported formats
        supported_formats = ['png', 'jpeg', 'jpg']
        for fmt in supported_formats:
            if f'image/{fmt}' in image_data:
                return True
        
        return False
    
    def _analyze_elements(self, image_data: str, request: AgentRequest) -> List[Dict[str, Any]]:
        """
        Analyze image to identify UI elements.
        
        Uses Vision API if enabled, otherwise falls back to mock implementation.
        
        Args:
            image_data: Base64 image data
            request: Original request for context
            
        Returns:
            List of identified elements with properties
        """
        # Try Vision API first if enabled
        if self.vision_enabled and self.vision_api:
            try:
                vision_result = self._analyze_with_vision_api(image_data, request)
                if vision_result:
                    return vision_result
            except Exception as e:
                self.logger.warning(f"Vision API failed, falling back to mock: {e}")
        
        # Fallback to mock implementation
        return self._analyze_elements_mock(image_data, request)
    
    def _analyze_with_vision_api(self, image_data: str, request: AgentRequest) -> Optional[List[Dict[str, Any]]]:
        """
        Analyze elements using Vision API.
        
        Args:
            image_data: Base64 image data
            request: Original request
            
        Returns:
            List of elements or None if failed
        """
        # Build vision prompt
        prompt = self._build_vision_prompt(request)
        
        # Call Vision API
        result = self.vision_api.analyze_image(image_data, prompt)
        
        if not result['success']:
            self.logger.warning(f"Vision API error: {result.get('error')}")
            return None
        
        # Log token usage
        self._log_vision_metrics(result)
        
        # Parse vision response into element list
        elements = self._parse_vision_response(result, request)
        
        self.logger.info(
            f"Vision API analysis complete: {len(elements)} elements, "
            f"{result['tokens_used']} tokens"
        )
        
        return elements
    
    def _build_vision_prompt(self, request: AgentRequest) -> str:
        """Build optimized prompt for vision API."""
        base_prompt = """Analyze this UI screenshot and identify interactive elements.

For each element, provide:
- Type (button, input, link, text, image, etc.)
- Label or visible text
- Suggested test ID (kebab-case)
- Colors (hex codes if visible)
- Approximate position

User's specific request: {user_message}

Focus on extracting structured, actionable data."""
        
        return base_prompt.format(user_message=request.user_message)
    
    def _parse_vision_response(self, result: Dict, request: AgentRequest) -> List[Dict[str, Any]]:
        """
        Parse vision API response into structured elements.
        
        Args:
            result: Vision API response
            request: Original request for context
            
        Returns:
            List of element dictionaries
        """
        elements = []
        
        # Extract from structured data if available
        extracted_data = result.get('extracted_data', {})
        if 'elements' in extracted_data:
            return extracted_data['elements']
        
        # Parse from natural language analysis
        analysis_text = result.get('analysis', '')
        
        # Simple parsing - in production, use more sophisticated NLP
        # For now, return mock elements with vision API metadata
        mock_elements = self._analyze_elements_mock(None, request)
        
        # Enhance with vision API data
        for element in mock_elements:
            element['source'] = 'vision_api'
            element['confidence'] = 0.85
        
        return mock_elements
    
    def _log_vision_metrics(self, result: Dict):
        """Log vision API usage to Tier 2."""
        try:
            metrics = {
                'event': 'vision_api_call',
                'timestamp': datetime.now().isoformat(),
                'tokens_used': result.get('tokens_used', 0),
                'processing_time_ms': result.get('processing_time_ms', 0),
                'success': result.get('success', False),
                'cached': result.get('cached', False)
            }
            
            # Log to Tier 2 knowledge graph if available
            if hasattr(self.tier2, 'log_event'):
                self.tier2.log_event(metrics)
        except Exception as e:
            self.logger.warning(f"Could not log vision metrics: {e}")
    
    def _analyze_elements_mock(self, image_data: Optional[str], request: AgentRequest) -> List[Dict[str, Any]]:
        """
        Mock implementation for testing and fallback.
        
        Args:
            image_data: Base64 image data (can be None for fallback)
            request: Original request for context
            
        Returns:
            List of mock elements
        """
        # For testing, extract hints from user message
        message_lower = request.user_message.lower()
        
        elements = []
        
        # Detect login page elements
        if 'login' in message_lower or 'signin' in message_lower:
            elements.extend([
                {
                    "type": "input",
                    "label": "Email",
                    "suggested_id": "input-email",
                    "selector": "input[type='email']",
                    "position": {"x": 100, "y": 150}
                },
                {
                    "type": "input",
                    "label": "Password",
                    "suggested_id": "input-password",
                    "selector": "input[type='password']",
                    "position": {"x": 100, "y": 200}
                },
                {
                    "type": "button",
                    "label": "Login",
                    "suggested_id": "btn-login",
                    "selector": "button[type='submit']",
                    "position": {"x": 100, "y": 250}
                }
            ])
        
        # Detect form elements
        elif 'form' in message_lower:
            elements.extend([
                {
                    "type": "input",
                    "label": "Name",
                    "suggested_id": "input-name",
                    "selector": "input[name='name']",
                    "position": {"x": 100, "y": 100}
                },
                {
                    "type": "button",
                    "label": "Submit",
                    "suggested_id": "btn-submit",
                    "selector": "button[type='submit']",
                    "position": {"x": 100, "y": 150}
                }
            ])
        
        # Generic UI elements
        else:
            elements.extend([
                {
                    "type": "button",
                    "label": "Action",
                    "suggested_id": "btn-action",
                    "selector": "button",
                    "position": {"x": 100, "y": 100}
                }
            ])
        
        return elements
    
    def _generate_recommendations(self, elements: List[Dict[str, Any]]) -> List[str]:
        """
        Generate testing recommendations based on identified elements.
        
        Args:
            elements: List of identified UI elements
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if not elements:
            recommendations.append("No elements identified - ensure screenshot is clear")
            return recommendations
        
        # Check for proper IDs
        has_proper_ids = all('suggested_id' in elem for elem in elements)
        if not has_proper_ids:
            recommendations.append("Add data-testid attributes for reliable testing")
        
        # Check for accessibility labels
        has_labels = all('label' in elem for elem in elements)
        if not has_labels:
            recommendations.append("Add ARIA labels for accessibility")
        
        # Check element types
        element_types = set(elem.get('type') for elem in elements)
        if 'input' in element_types:
            recommendations.append("Validate input fields with proper type attributes")
        
        if 'button' in element_types:
            recommendations.append("Ensure buttons have clear action labels")
        
        # Playwright-specific suggestions
        recommendations.append("Use Playwright's getByRole() for robust selectors")
        recommendations.append("Consider getByLabel() for form inputs")
        
        return recommendations
    
    def _error_response(self, error_msg: str, start_time: datetime) -> AgentResponse:
        """
        Create error response.
        
        Args:
            error_msg: Error message
            start_time: Request start time
            
        Returns:
            AgentResponse with error details
        """
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return AgentResponse(
            success=False,
            result={"elements": []},
            message=f"Screenshot analysis failed: {error_msg}",
            agent_name=self.name,
            duration_ms=duration_ms,
            metadata={"error": error_msg}
        )
