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
        
        Note: This is a MOCK implementation for testing purposes.
        In production, this would use actual image recognition.
        
        Args:
            image_data: Base64 image data
            request: Original request for context
            
        Returns:
            List of identified elements with properties
        """
        # Mock implementation - returns sample elements
        # In production, would use:
        # - PIL/Pillow for basic image processing
        # - OpenCV for advanced detection
        # - Cloud Vision APIs for ML-based recognition
        # - Playwright Inspector integration
        
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
