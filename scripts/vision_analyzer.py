"""
Vision Analyzer for CORTEX ADO Planning System

Analyzes screenshots and images to automatically extract requirements, UI elements,
error messages, and other planning information.

Supports multiple analyzers:
- UI Mockup Analyzer: Extract buttons, inputs, labels for acceptance criteria
- Error Screenshot Analyzer: Extract error messages and stack traces for bug templates
- ADO Work Item Analyzer: Extract ADO#, title, description from screenshots
- Architecture Diagram Analyzer: Extract components and relationships

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import base64
import json
import mimetypes
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import platform


class ImageType(Enum):
    """Types of images that can be analyzed"""
    UI_MOCKUP = "ui_mockup"
    ERROR_SCREEN = "error_screen"
    ADO_WORK_ITEM = "ado_work_item"
    ARCHITECTURE_DIAGRAM = "architecture_diagram"
    UNKNOWN = "unknown"


class ConfidenceLevel(Enum):
    """Confidence level of extracted information"""
    HIGH = "high"  # 80-100% confidence
    MEDIUM = "medium"  # 50-79% confidence
    LOW = "low"  # 20-49% confidence
    UNCERTAIN = "uncertain"  # <20% confidence


@dataclass
class ExtractionResult:
    """Result of vision analysis with extracted information"""
    image_type: ImageType
    confidence: ConfidenceLevel
    raw_data: Dict[str, Any]
    structured_data: Dict[str, Any]
    suggestions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class UIElement:
    """Represents a UI element extracted from mockup"""
    element_type: str  # button, input, label, dropdown, checkbox, etc.
    text: str
    position: Optional[Tuple[int, int]] = None
    confidence: float = 0.0


@dataclass
class ErrorInfo:
    """Represents error information extracted from screenshot"""
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    error_code: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class ADOWorkItem:
    """Represents ADO work item information extracted from screenshot"""
    ado_number: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    work_item_type: Optional[str] = None  # Bug, Feature, User Story, Task
    assigned_to: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


@dataclass
class ArchitectureComponent:
    """Represents component extracted from architecture diagram"""
    name: str
    component_type: str  # service, database, API, UI, queue, etc.
    connections: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)


class VisionAnalyzer:
    """
    Main vision analyzer class for CORTEX ADO planning system.
    
    Provides fallback chain: GitHub Copilot → Mock (for development)
    
    Usage:
        analyzer = VisionAnalyzer()
        result = analyzer.analyze_image("screenshot.png", ImageType.UI_MOCKUP)
        print(result.structured_data)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Vision Analyzer.
        
        Args:
            config_path: Optional path to cortex.config.json
        """
        self.config = self._load_config(config_path)
        self.mode = self.config.get("vision_api", {}).get("mode", "mock")
        self.api_key = os.getenv("OPENAI_API_KEY") or self.config.get("vision_api", {}).get("api_key")
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from cortex.config.json"""
        if config_path is None:
            # Platform-aware path resolution
            hostname = platform.node().lower()
            if hostname in ["asifs-mbp", "asifs-macbook-pro"]:
                base_path = Path.home() / "PROJECTS" / "CORTEX"
            else:
                base_path = Path("D:/PROJECTS/CORTEX")
            
            config_path = base_path / "cortex.config.json"
        
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Default configuration
        return {
            "vision_api": {
                "mode": "mock",  # mock, openai, copilot
                "max_image_size_mb": 10,
                "supported_formats": ["png", "jpg", "jpeg", "gif", "bmp"],
                "cache_results": True,
                "cache_ttl_hours": 24
            }
        }
    
    def analyze_image(
        self,
        image_path: str,
        expected_type: Optional[ImageType] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ExtractionResult:
        """
        Analyze an image and extract relevant information.
        
        Args:
            image_path: Path to image file
            expected_type: Expected image type (auto-detect if None)
            context: Additional context for analysis
            
        Returns:
            ExtractionResult with extracted information
        """
        # Validate image (skip validation in mock mode for demo purposes)
        if self.mode != "mock" and not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Detect image type if not provided
        if expected_type is None:
            expected_type = self._detect_image_type(image_path, context)
        
        # Route to appropriate analyzer based on mode
        if self.mode == "mock":
            return self._mock_analyze(image_path, expected_type, context)
        elif self.mode == "openai":
            return self._openai_analyze(image_path, expected_type, context)
        elif self.mode == "copilot":
            return self._copilot_analyze(image_path, expected_type, context)
        else:
            raise ValueError(f"Unknown vision mode: {self.mode}")
    
    def _detect_image_type(
        self,
        image_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ImageType:
        """
        Auto-detect image type based on filename and context.
        
        Args:
            image_path: Path to image
            context: Additional context hints
            
        Returns:
            Detected ImageType
        """
        filename = Path(image_path).name.lower()
        
        # Check context hints first
        if context:
            if context.get("type"):
                try:
                    return ImageType(context["type"])
                except ValueError:
                    pass
        
        # Filename-based detection
        if any(word in filename for word in ["mockup", "ui", "design", "wireframe"]):
            return ImageType.UI_MOCKUP
        elif any(word in filename for word in ["error", "exception", "crash", "bug"]):
            return ImageType.ERROR_SCREEN
        elif any(word in filename for word in ["ado", "workitem", "ticket", "task"]):
            return ImageType.ADO_WORK_ITEM
        elif any(word in filename for word in ["architecture", "diagram", "system", "flow"]):
            return ImageType.ARCHITECTURE_DIAGRAM
        
        return ImageType.UNKNOWN
    
    def _mock_analyze(
        self,
        image_path: str,
        image_type: ImageType,
        context: Optional[Dict[str, Any]] = None
    ) -> ExtractionResult:
        """
        Mock analyzer for development and testing.
        Returns realistic sample data based on image type.
        """
        filename = Path(image_path).stem
        
        if image_type == ImageType.UI_MOCKUP:
            return self._mock_ui_mockup(filename)
        elif image_type == ImageType.ERROR_SCREEN:
            return self._mock_error_screen(filename)
        elif image_type == ImageType.ADO_WORK_ITEM:
            return self._mock_ado_work_item(filename)
        elif image_type == ImageType.ARCHITECTURE_DIAGRAM:
            return self._mock_architecture_diagram(filename)
        else:
            return ExtractionResult(
                image_type=ImageType.UNKNOWN,
                confidence=ConfidenceLevel.UNCERTAIN,
                raw_data={"error": "Unknown image type"},
                structured_data={},
                warnings=["Could not determine image type"]
            )
    
    def _mock_ui_mockup(self, filename: str) -> ExtractionResult:
        """Mock analyzer for UI mockups"""
        ui_elements = [
            UIElement("input", "Email Address", position=(100, 150), confidence=0.95),
            UIElement("input", "Password", position=(100, 200), confidence=0.95),
            UIElement("button", "Sign In", position=(100, 270), confidence=0.98),
            UIElement("link", "Forgot Password?", position=(250, 275), confidence=0.90),
            UIElement("checkbox", "Remember Me", position=(100, 240), confidence=0.85),
        ]
        
        # Generate acceptance criteria from UI elements
        acceptance_criteria = []
        for elem in ui_elements:
            if elem.element_type == "button":
                acceptance_criteria.append(f"User can click '{elem.text}' button")
            elif elem.element_type == "input":
                acceptance_criteria.append(f"User can enter text in '{elem.text}' field")
            elif elem.element_type == "checkbox":
                acceptance_criteria.append(f"User can toggle '{elem.text}' option")
            elif elem.element_type == "link":
                acceptance_criteria.append(f"User can click '{elem.text}' link")
        
        return ExtractionResult(
            image_type=ImageType.UI_MOCKUP,
            confidence=ConfidenceLevel.HIGH,
            raw_data={
                "elements_detected": len(ui_elements),
                "elements": [
                    {
                        "type": e.element_type,
                        "text": e.text,
                        "confidence": e.confidence
                    }
                    for e in ui_elements
                ]
            },
            structured_data={
                "ui_elements": ui_elements,
                "acceptance_criteria": acceptance_criteria,
                "suggested_test_cases": [
                    "Verify email validation",
                    "Verify password visibility toggle",
                    "Verify 'Remember Me' persistence",
                    "Verify 'Forgot Password' flow"
                ]
            },
            suggestions=[
                f"Found {len(ui_elements)} UI elements",
                f"Generated {len(acceptance_criteria)} acceptance criteria",
                "Consider adding error state validation",
                "Consider adding loading state handling"
            ]
        )
    
    def _mock_error_screen(self, filename: str) -> ExtractionResult:
        """Mock analyzer for error screenshots"""
        error_info = ErrorInfo(
            error_type="NullPointerException",
            error_message="Cannot read property 'id' of null",
            stack_trace="  at UserService.getUser (user-service.js:45)\n  at AuthController.login (auth-controller.js:23)",
            error_code="ERR_NULL_REFERENCE",
            file_path="src/services/user-service.js",
            line_number=45
        )
        
        return ExtractionResult(
            image_type=ImageType.ERROR_SCREEN,
            confidence=ConfidenceLevel.HIGH,
            raw_data={
                "error_detected": True,
                "error_type": error_info.error_type,
                "message": error_info.error_message,
                "stack_trace": error_info.stack_trace
            },
            structured_data={
                "error_info": error_info,
                "suggested_fix": "Add null check before accessing user.id",
                "affected_files": ["user-service.js", "auth-controller.js"],
                "bug_severity": "High",
                "bug_priority": "Critical"
            },
            suggestions=[
                f"Error found in {error_info.file_path} at line {error_info.line_number}",
                "Add null/undefined validation",
                "Consider adding defensive programming checks",
                "Add unit test to prevent regression"
            ],
            warnings=[
                "Production error - immediate attention required"
            ]
        )
    
    def _mock_ado_work_item(self, filename: str) -> ExtractionResult:
        """Mock analyzer for ADO work item screenshots"""
        ado_item = ADOWorkItem(
            ado_number="ADO-12345",
            title="Implement user authentication with OAuth2",
            description="Add OAuth2 authentication flow to support Google and Microsoft login",
            work_item_type="Feature",
            assigned_to="John Doe",
            status="In Progress",
            priority="High"
        )
        
        return ExtractionResult(
            image_type=ImageType.ADO_WORK_ITEM,
            confidence=ConfidenceLevel.MEDIUM,
            raw_data={
                "ado_detected": True,
                "ado_number": ado_item.ado_number,
                "title": ado_item.title,
                "type": ado_item.work_item_type
            },
            structured_data={
                "ado_work_item": ado_item,
                "template_type": "feature",
                "estimated_hours": 16,
                "suggested_tags": ["authentication", "oauth2", "security"]
            },
            suggestions=[
                f"Extracted ADO number: {ado_item.ado_number}",
                f"Work item type: {ado_item.work_item_type}",
                "Template pre-populated with extracted data",
                "Review and complete DoR/DoD sections"
            ]
        )
    
    def _mock_architecture_diagram(self, filename: str) -> ExtractionResult:
        """Mock analyzer for architecture diagrams"""
        components = [
            ArchitectureComponent(
                "Frontend",
                "UI",
                connections=["API Gateway"],
                technologies=["React", "TypeScript"]
            ),
            ArchitectureComponent(
                "API Gateway",
                "API",
                connections=["Auth Service", "User Service"],
                technologies=["Node.js", "Express"]
            ),
            ArchitectureComponent(
                "Auth Service",
                "Service",
                connections=["Database"],
                technologies=["Python", "FastAPI"]
            ),
            ArchitectureComponent(
                "Database",
                "Database",
                connections=[],
                technologies=["PostgreSQL"]
            )
        ]
        
        return ExtractionResult(
            image_type=ImageType.ARCHITECTURE_DIAGRAM,
            confidence=ConfidenceLevel.MEDIUM,
            raw_data={
                "components_detected": len(components),
                "components": [
                    {
                        "name": c.name,
                        "type": c.component_type,
                        "connections": c.connections
                    }
                    for c in components
                ]
            },
            structured_data={
                "components": components,
                "architecture_style": "Microservices",
                "integration_points": ["API Gateway → Services", "Services → Database"],
                "suggested_technologies": list(set([tech for c in components for tech in c.technologies]))
            },
            suggestions=[
                f"Found {len(components)} components",
                "Microservices architecture detected",
                "Consider adding message queue for async operations",
                "Add caching layer (Redis) for performance"
            ]
        )
    
    def _openai_analyze(
        self,
        image_path: str,
        image_type: ImageType,
        context: Optional[Dict[str, Any]] = None
    ) -> ExtractionResult:
        """
        Analyze image using OpenAI Vision API.
        
        Note: Requires OpenAI API key in environment or config.
        Currently returns mock data - full implementation pending.
        """
        # TODO: Implement OpenAI Vision API integration
        # For now, fall back to mock
        return self._mock_analyze(image_path, image_type, context)
    
    def _copilot_analyze(
        self,
        image_path: str,
        image_type: ImageType,
        context: Optional[Dict[str, Any]] = None
    ) -> ExtractionResult:
        """
        Analyze image using GitHub Copilot Vision API.
        
        Note: Requires GitHub Copilot subscription.
        Currently returns mock data - full implementation pending.
        """
        # TODO: Implement GitHub Copilot Vision API integration
        # For now, fall back to mock
        return self._mock_analyze(image_path, image_type, context)
    
    def extract_for_ado_template(
        self,
        image_path: str,
        template_type: str = "feature"
    ) -> Dict[str, Any]:
        """
        Extract information specifically formatted for ADO template population.
        
        Args:
            image_path: Path to image
            template_type: Type of ADO template (feature, bug, task, etc.)
            
        Returns:
            Dict ready for ADO Manager's create_ado() method
        """
        result = self.analyze_image(image_path)
        
        # Build template data based on image type
        template_data = {
            "confidence": result.confidence.value,
            "extraction_timestamp": result.timestamp
        }
        
        if result.image_type == ImageType.UI_MOCKUP:
            ui_data = result.structured_data.get("ui_elements", [])
            template_data.update({
                "title": f"Implement UI: {Path(image_path).stem}",
                "acceptance_criteria": result.structured_data.get("acceptance_criteria", []),
                "tags": ["ui", "frontend", "mockup"],
                "technical_notes": f"Extracted {len(ui_data)} UI elements from mockup"
            })
            
        elif result.image_type == ImageType.ERROR_SCREEN:
            error_info = result.structured_data.get("error_info")
            if error_info:
                template_data.update({
                    "title": f"Fix: {error_info.error_type}",
                    "description": error_info.error_message,
                    "acceptance_criteria": [
                        f"Fix error in {error_info.file_path}",
                        "Add unit test to prevent regression",
                        "Verify fix in staging environment"
                    ],
                    "tags": ["bug", "error", error_info.error_type.lower()],
                    "priority": "Critical",
                    "related_file_paths": [error_info.file_path] if error_info.file_path else []
                })
                
        elif result.image_type == ImageType.ADO_WORK_ITEM:
            ado_item = result.structured_data.get("ado_work_item")
            if ado_item:
                template_data.update({
                    "ado_number": ado_item.ado_number,
                    "title": ado_item.title,
                    "description": ado_item.description,
                    "priority": ado_item.priority,
                    "tags": result.structured_data.get("suggested_tags", [])
                })
                
        elif result.image_type == ImageType.ARCHITECTURE_DIAGRAM:
            components = result.structured_data.get("components", [])
            template_data.update({
                "title": f"Architecture: {Path(image_path).stem}",
                "technical_notes": f"Architecture with {len(components)} components",
                "tags": ["architecture", "design", "diagram"]
            })
        
        return template_data


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("CORTEX Vision Analyzer - Example Usage")
    print("=" * 80)
    print()
    
    # Initialize analyzer
    analyzer = VisionAnalyzer()
    print(f"✅ Vision Analyzer initialized (mode: {analyzer.mode})")
    print()
    
    # Example 1: UI Mockup Analysis
    print("📱 Example 1: UI Mockup Analysis")
    print("-" * 80)
    mock_image_path = "login-mockup.png"
    result = analyzer.analyze_image(mock_image_path, ImageType.UI_MOCKUP)
    
    print(f"Image Type: {result.image_type.value}")
    print(f"Confidence: {result.confidence.value}")
    print(f"UI Elements Found: {len(result.structured_data.get('ui_elements', []))}")
    print(f"Acceptance Criteria: {len(result.structured_data.get('acceptance_criteria', []))}")
    print()
    print("Acceptance Criteria:")
    for i, ac in enumerate(result.structured_data.get('acceptance_criteria', []), 1):
        print(f"  {i}. {ac}")
    print()
    
    # Example 2: Error Screenshot Analysis
    print("🐛 Example 2: Error Screenshot Analysis")
    print("-" * 80)
    result = analyzer.analyze_image("error-screenshot.png", ImageType.ERROR_SCREEN)
    
    error_info = result.structured_data.get('error_info')
    if error_info:
        print(f"Error Type: {error_info.error_type}")
        print(f"Message: {error_info.error_message}")
        print(f"File: {error_info.file_path}:{error_info.line_number}")
        print(f"Suggested Fix: {result.structured_data.get('suggested_fix')}")
    print()
    
    # Example 3: ADO Work Item Extraction
    print("📋 Example 3: ADO Work Item Extraction")
    print("-" * 80)
    result = analyzer.analyze_image("ado-screenshot.png", ImageType.ADO_WORK_ITEM)
    
    ado_item = result.structured_data.get('ado_work_item')
    if ado_item:
        print(f"ADO Number: {ado_item.ado_number}")
        print(f"Title: {ado_item.title}")
        print(f"Type: {ado_item.work_item_type}")
        print(f"Priority: {ado_item.priority}")
        print(f"Status: {ado_item.status}")
    print()
    
    # Example 4: Extract for ADO Template
    print("🎯 Example 4: Extract for ADO Template")
    print("-" * 80)
    template_data = analyzer.extract_for_ado_template("login-mockup.png", "feature")
    
    print("Template Data Ready for ADO Manager:")
    print(json.dumps(template_data, indent=2))
    print()
    
    print("=" * 80)
    print("✅ Vision Analyzer demo complete!")
    print("=" * 80)
