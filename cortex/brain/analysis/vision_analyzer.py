"""
Vision Analyzer for CORTEX LENS.

Analyzes images via Vision API to extract UI elements, URLs, issues,
and structural mappings. Supports screenshots, diagrams, mockups, and
error messages.

MCP Tool: cortex_vision_analyze
Author: Asif Hussain
ARCH-007: MCP-first architecture enforcement
"""

import base64
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class ImageType(Enum):
    """Type of image being analyzed."""
    SCREENSHOT = "screenshot"
    DIAGRAM = "diagram"
    MOCKUP = "mockup"
    ERROR = "error"
    UNKNOWN = "unknown"


class AnalysisDepth(Enum):
    """Depth of analysis to perform."""
    QUICK = "quick"       # Fast, high-level extraction
    STANDARD = "standard" # Balanced analysis
    THOROUGH = "thorough" # Deep, comprehensive analysis


@dataclass
class UIElement:
    """Extracted UI element from image."""
    element_type: str           # button, input, label, icon, link, etc.
    text: Optional[str] = None  # Visible text content
    element_id: Optional[str] = None  # HTML/CSS id if visible
    coordinates: Optional[Dict[str, int]] = None  # x, y, width, height
    confidence: float = 0.0     # Detection confidence (0.0-1.0)
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedURL:
    """URL extracted from image."""
    url: str
    context: str  # Where in the image (address bar, link text, etc.)
    url_type: str  # navigation, api, resource, etc.


@dataclass
class DetectedIssue:
    """Issue detected in image."""
    issue_type: str     # visual_bug, accessibility, layout, error_message
    severity: str       # critical, high, medium, low
    description: str
    location: Optional[str] = None  # Region description
    suggestion: Optional[str] = None


@dataclass
class VisionAnalysisResult:
    """Complete vision analysis result."""
    status: str
    image_type: ImageType
    analysis_depth: AnalysisDepth
    
    # Extracted data
    urls: List[ExtractedURL] = field(default_factory=list)
    ui_elements: List[UIElement] = field(default_factory=list)
    issues: List[DetectedIssue] = field(default_factory=list)
    text_content: List[str] = field(default_factory=list)
    structural_map: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    raw_response: Optional[str] = None
    processing_time_ms: int = 0
    token_usage: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for MCP response."""
        return {
            "status": self.status,
            "image_type": self.image_type.value,
            "analysis_depth": self.analysis_depth.value,
            "urls": [
                {"url": u.url, "context": u.context, "type": u.url_type}
                for u in self.urls
            ],
            "ui_elements": [
                {
                    "type": e.element_type,
                    "text": e.text,
                    "id": e.element_id,
                    "coordinates": e.coordinates,
                    "confidence": e.confidence,
                    "attributes": e.attributes,
                }
                for e in self.ui_elements
            ],
            "issues": [
                {
                    "type": i.issue_type,
                    "severity": i.severity,
                    "description": i.description,
                    "location": i.location,
                    "suggestion": i.suggestion,
                }
                for i in self.issues
            ],
            "text_content": self.text_content,
            "structural_map": self.structural_map,
            "_metadata": {
                "processing_time_ms": self.processing_time_ms,
                "token_usage": self.token_usage,
            },
        }


class VisionAnalyzer:
    """
    Analyzer for image content using Vision API.
    
    Extracts UI elements, URLs, issues, and structural information
    from screenshots, diagrams, mockups, and error messages.
    
    Features:
    - URL extraction (address bar, links, API endpoints)
    - UI element detection (buttons, inputs, labels, icons)
    - Element ID extraction (HTML ids, data attributes, aria labels)
    - Issue detection (visual bugs, accessibility, layout problems)
    - Text/OCR extraction (all visible text)
    - Structural mapping (component hierarchy)
    - Error detection (stack traces, error messages)
    
    Example:
        ```python
        analyzer = VisionAnalyzer()
        
        # Analyze from file
        result = analyzer.analyze_file(Path("screenshot.png"))
        
        # Analyze from base64
        result = analyzer.analyze_base64(base64_data)
        
        # Access results
        for url in result.urls:
            print(f"Found URL: {url.url}")
        
        for element in result.ui_elements:
            print(f"Element: {element.element_type} - {element.text}")
        ```
    
    Attributes:
        api_key: Vision API key (optional, uses env var if not provided)
        default_depth: Default analysis depth
    """
    
    # Vision analysis prompt templates
    ANALYSIS_PROMPTS = {
        AnalysisDepth.QUICK: """Analyze this image quickly. Extract:
1. All visible URLs (address bar, links, API endpoints)
2. Main UI elements (buttons, inputs, major labels)
3. Any obvious errors or issues
4. Key text content

Return as JSON with keys: urls, elements, issues, text""",

        AnalysisDepth.STANDARD: """Analyze this image thoroughly. Extract:
1. ALL visible URLs (address bar, links, API endpoints, resource URLs)
2. ALL UI elements with details:
   - Type (button, input, label, icon, link, dropdown, etc.)
   - Visible text
   - Element IDs if visible (HTML id, data-*, aria-*)
   - Approximate position (top-left, center, etc.)
3. Issues and problems:
   - Visual bugs (misalignment, overflow, broken layouts)
   - Accessibility issues (missing labels, contrast)
   - Error messages, warnings, stack traces
4. All visible text content (OCR)
5. Component hierarchy/structure

Return as JSON with keys: urls, elements, issues, text, structure""",

        AnalysisDepth.THOROUGH: """Perform exhaustive analysis of this image. Extract EVERYTHING:

1. URLs (complete extraction):
   - Browser address bar URLs
   - Visible hyperlinks and their text
   - API endpoint URLs in code/logs
   - Resource URLs (images, scripts, stylesheets)
   - Partial/truncated URLs (mark as incomplete)

2. UI Elements (complete inventory):
   - Type: button, input, textarea, select, checkbox, radio, label, icon, link, image, table, list, card, modal, dropdown, tab, accordion, tooltip, badge, alert, progress, spinner
   - Text content (exact)
   - Element IDs (HTML id, name, data-testid, data-*, aria-label, aria-labelledby)
   - CSS classes if visible
   - State (enabled/disabled, selected, focused, error)
   - Coordinates (approximate bounding box if determinable)

3. Issues (comprehensive detection):
   - Visual bugs: misalignment, overflow, clipping, z-index, spacing
   - Accessibility: missing alt text, low contrast, missing labels
   - UX issues: confusing layout, unclear hierarchy
   - Errors: stack traces, error messages, warnings, 404s, validation errors
   - Performance indicators: loading spinners, skeleton screens

4. Text Content (complete OCR):
   - All visible text, organized by region
   - Code snippets
   - Log output
   - Form labels and values

5. Structural Map:
   - Component hierarchy (parent-child relationships)
   - Layout structure (header, sidebar, main, footer)
   - Navigation elements
   - Content sections

Return comprehensive JSON with: urls, elements, issues, text, structure, metadata""",
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_depth: AnalysisDepth = AnalysisDepth.STANDARD,
    ):
        """
        Initialize VisionAnalyzer.
        
        Args:
            api_key: Vision API key (uses OPENAI_API_KEY env var if not provided)
            default_depth: Default analysis depth
        """
        self.api_key = api_key
        self.default_depth = default_depth
    
    def analyze_file(
        self,
        file_path: Path,
        image_type: ImageType = ImageType.UNKNOWN,
        depth: Optional[AnalysisDepth] = None,
        extract_urls: bool = True,
        extract_elements: bool = True,
        detect_issues: bool = True,
    ) -> VisionAnalysisResult:
        """
        Analyze image from file path.
        
        Args:
            file_path: Path to image file
            image_type: Type of image (auto-detected if UNKNOWN)
            depth: Analysis depth (uses default if not specified)
            extract_urls: Extract URLs from image
            extract_elements: Extract UI elements
            detect_issues: Detect issues and problems
            
        Returns:
            VisionAnalysisResult with extracted data
        """
        if not file_path.exists():
            return VisionAnalysisResult(
                status="error",
                image_type=image_type,
                analysis_depth=depth or self.default_depth,
            )
        
        # Read and encode file
        with open(file_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # Detect image type from extension
        if image_type == ImageType.UNKNOWN:
            image_type = self._detect_image_type(file_path.name)
        
        return self.analyze_base64(
            image_data=image_data,
            image_type=image_type,
            depth=depth,
            extract_urls=extract_urls,
            extract_elements=extract_elements,
            detect_issues=detect_issues,
        )
    
    def analyze_base64(
        self,
        image_data: str,
        image_type: ImageType = ImageType.UNKNOWN,
        depth: Optional[AnalysisDepth] = None,
        extract_urls: bool = True,
        extract_elements: bool = True,
        detect_issues: bool = True,
    ) -> VisionAnalysisResult:
        """
        Analyze image from base64-encoded data.
        
        Args:
            image_data: Base64-encoded image data
            image_type: Type of image
            depth: Analysis depth
            extract_urls: Extract URLs
            extract_elements: Extract UI elements
            detect_issues: Detect issues
            
        Returns:
            VisionAnalysisResult with extracted data
        """
        import time
        start_time = time.time()
        
        depth = depth or self.default_depth
        
        # Build analysis request
        prompt = self._build_prompt(
            image_type=image_type,
            depth=depth,
            extract_urls=extract_urls,
            extract_elements=extract_elements,
            detect_issues=detect_issues,
        )
        
        # Call Vision API
        try:
            response = self._call_vision_api(image_data, prompt)
            result = self._parse_response(response, image_type, depth)
        except Exception as e:
            result = VisionAnalysisResult(
                status=f"error: {str(e)}",
                image_type=image_type,
                analysis_depth=depth,
            )
        
        # Record timing
        result.processing_time_ms = int((time.time() - start_time) * 1000)
        
        return result
    
    def analyze_url(
        self,
        image_url: str,
        image_type: ImageType = ImageType.UNKNOWN,
        depth: Optional[AnalysisDepth] = None,
        extract_urls: bool = True,
        extract_elements: bool = True,
        detect_issues: bool = True,
    ) -> VisionAnalysisResult:
        """
        Analyze image from URL.
        
        Args:
            image_url: URL to image
            image_type: Type of image
            depth: Analysis depth
            extract_urls: Extract URLs
            extract_elements: Extract UI elements
            detect_issues: Detect issues
            
        Returns:
            VisionAnalysisResult with extracted data
        """
        import time
        start_time = time.time()
        
        depth = depth or self.default_depth
        
        prompt = self._build_prompt(
            image_type=image_type,
            depth=depth,
            extract_urls=extract_urls,
            extract_elements=extract_elements,
            detect_issues=detect_issues,
        )
        
        try:
            response = self._call_vision_api_url(image_url, prompt)
            result = self._parse_response(response, image_type, depth)
        except Exception as e:
            result = VisionAnalysisResult(
                status=f"error: {str(e)}",
                image_type=image_type,
                analysis_depth=depth,
            )
        
        result.processing_time_ms = int((time.time() - start_time) * 1000)
        
        return result
    
    def _build_prompt(
        self,
        image_type: ImageType,
        depth: AnalysisDepth,
        extract_urls: bool,
        extract_elements: bool,
        detect_issues: bool,
    ) -> str:
        """Build analysis prompt based on parameters."""
        base_prompt = self.ANALYSIS_PROMPTS[depth]
        
        # Add image-type specific instructions
        type_instructions = {
            ImageType.SCREENSHOT: "This is a screenshot of a user interface. Focus on interactive elements and navigation.",
            ImageType.DIAGRAM: "This is a technical diagram. Focus on component relationships and data flow.",
            ImageType.MOCKUP: "This is a UI mockup/wireframe. Focus on layout structure and placeholder elements.",
            ImageType.ERROR: "This shows an error state. Prioritize extracting error messages, stack traces, and error codes.",
            ImageType.UNKNOWN: "Analyze this image and determine its type (screenshot, diagram, error, etc.).",
        }
        
        prompt_parts = [base_prompt, type_instructions[image_type]]
        
        # Add filter instructions
        if not extract_urls:
            prompt_parts.append("Skip URL extraction.")
        if not extract_elements:
            prompt_parts.append("Skip UI element extraction.")
        if not detect_issues:
            prompt_parts.append("Skip issue detection.")
        
        return "\n\n".join(prompt_parts)
    
    def _call_vision_api(self, image_data: str, prompt: str) -> Dict[str, Any]:
        """
        Call Vision API with base64 image.
        
        Uses OpenAI GPT-4 Vision API format.
        """
        import os
        import httpx
        
        api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No API key provided. Set OPENAI_API_KEY or pass api_key.")
        
        # Determine media type from base64 header or default to PNG
        media_type = "image/png"
        if image_data.startswith("/9j/"):
            media_type = "image/jpeg"
        elif image_data.startswith("R0lGOD"):
            media_type = "image/gif"
        elif image_data.startswith("UklGR"):
            media_type = "image/webp"
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            "max_tokens": 4096,
            "response_format": {"type": "json_object"},
        }
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            return response.json()
    
    def _call_vision_api_url(self, image_url: str, prompt: str) -> Dict[str, Any]:
        """Call Vision API with image URL."""
        import os
        import httpx
        
        api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No API key provided. Set OPENAI_API_KEY or pass api_key.")
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            "max_tokens": 4096,
            "response_format": {"type": "json_object"},
        }
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            return response.json()
    
    def _parse_response(
        self,
        response: Dict[str, Any],
        image_type: ImageType,
        depth: AnalysisDepth,
    ) -> VisionAnalysisResult:
        """Parse Vision API response into structured result."""
        result = VisionAnalysisResult(
            status="success",
            image_type=image_type,
            analysis_depth=depth,
        )
        
        # Extract usage info
        if "usage" in response:
            result.token_usage = {
                "prompt_tokens": response["usage"].get("prompt_tokens", 0),
                "completion_tokens": response["usage"].get("completion_tokens", 0),
                "total_tokens": response["usage"].get("total_tokens", 0),
            }
        
        # Parse content
        try:
            content = response["choices"][0]["message"]["content"]
            result.raw_response = content
            
            data = json.loads(content)
            
            # Parse URLs
            for url_data in data.get("urls", []):
                if isinstance(url_data, str):
                    result.urls.append(ExtractedURL(
                        url=url_data,
                        context="extracted",
                        url_type="unknown",
                    ))
                elif isinstance(url_data, dict):
                    result.urls.append(ExtractedURL(
                        url=url_data.get("url", ""),
                        context=url_data.get("context", "extracted"),
                        url_type=url_data.get("type", "unknown"),
                    ))
            
            # Parse elements
            for elem_data in data.get("elements", []):
                if isinstance(elem_data, dict):
                    result.ui_elements.append(UIElement(
                        element_type=elem_data.get("type", "unknown"),
                        text=elem_data.get("text"),
                        element_id=elem_data.get("id"),
                        coordinates=elem_data.get("coordinates"),
                        confidence=elem_data.get("confidence", 0.8),
                        attributes=elem_data.get("attributes", {}),
                    ))
            
            # Parse issues
            for issue_data in data.get("issues", []):
                if isinstance(issue_data, dict):
                    result.issues.append(DetectedIssue(
                        issue_type=issue_data.get("type", "unknown"),
                        severity=issue_data.get("severity", "medium"),
                        description=issue_data.get("description", ""),
                        location=issue_data.get("location"),
                        suggestion=issue_data.get("suggestion"),
                    ))
            
            # Parse text content
            text_data = data.get("text", [])
            if isinstance(text_data, list):
                result.text_content = text_data
            elif isinstance(text_data, str):
                result.text_content = [text_data]
            
            # Parse structure
            result.structural_map = data.get("structure", {})
            
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            result.status = f"parse_error: {str(e)}"
        
        return result
    
    def _detect_image_type(self, filename: str) -> ImageType:
        """Detect image type from filename patterns."""
        filename_lower = filename.lower()
        
        if any(x in filename_lower for x in ["error", "exception", "crash", "fail"]):
            return ImageType.ERROR
        if any(x in filename_lower for x in ["diagram", "flow", "arch", "uml"]):
            return ImageType.DIAGRAM
        if any(x in filename_lower for x in ["mockup", "wireframe", "design", "figma"]):
            return ImageType.MOCKUP
        if any(x in filename_lower for x in ["screenshot", "screen", "capture", "snap"]):
            return ImageType.SCREENSHOT
        
        return ImageType.UNKNOWN


# Convenience function for quick analysis
def analyze_image(
    image: Union[str, Path],
    depth: str = "standard",
) -> Dict[str, Any]:
    """
    Quick image analysis function.
    
    Args:
        image: Path, URL, or base64 data
        depth: Analysis depth (quick/standard/thorough)
        
    Returns:
        Analysis result as dict
    """
    analyzer = VisionAnalyzer()
    depth_enum = AnalysisDepth(depth)
    
    if isinstance(image, Path) or (isinstance(image, str) and Path(image).exists()):
        result = analyzer.analyze_file(Path(image), depth=depth_enum)
    elif isinstance(image, str) and image.startswith(("http://", "https://")):
        result = analyzer.analyze_url(image, depth=depth_enum)
    else:
        result = analyzer.analyze_base64(image, depth=depth_enum)
    
    return result.to_dict()
