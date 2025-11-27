"""
Investigation HTML ID Mapping Plugin for CORTEX 3.0

Dedicated plugin for HTML element analysis, ID mapping, and accessibility improvements
during investigation phases.

Features:
- Element-to-ID mapping analysis
- Missing ID detection with intelligent suggestions
- Accessibility compliance checking
- Testability improvements
- Button caption to ID mapping (e.g., "Submit" → btnSubmit)
- Semantic element analysis
- ARIA attribute recommendations

Integration with InvestigationRouter:
- Token-efficient HTML parsing
- Actionable ID generation suggestions
- Accessibility recommendations
- Testing-friendly element identification

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import logging
from datetime import datetime

from src.plugins.base_plugin import (
    BasePlugin,
    PluginMetadata,
    PluginCategory,
    PluginPriority,
    HookPoint
)

logger = logging.getLogger(__name__)


class ElementType(Enum):
    """HTML element types for ID mapping"""
    BUTTON = "button"
    INPUT = "input"
    SELECT = "select"
    TEXTAREA = "textarea"
    FORM = "form"
    HEADING = "heading"
    SECTION = "section"
    ARTICLE = "article"
    NAV = "nav"
    MAIN = "main"
    ASIDE = "aside"
    DIV = "div"
    SPAN = "span"
    LINK = "a"
    IMAGE = "img"
    TABLE = "table"
    LIST = "ul/ol"
    LIST_ITEM = "li"


class AccessibilityIssueType(Enum):
    """Types of accessibility issues"""
    MISSING_ID = "missing_id"
    MISSING_LABEL = "missing_label"
    MISSING_ALT_TEXT = "missing_alt_text"
    MISSING_ARIA_LABEL = "missing_aria_label"
    POOR_HEADING_STRUCTURE = "poor_heading_structure"
    MISSING_FORM_LABELS = "missing_form_labels"
    INSUFFICIENT_COLOR_CONTRAST = "insufficient_color_contrast"
    MISSING_FOCUS_INDICATORS = "missing_focus_indicators"
    KEYBOARD_NAVIGATION = "keyboard_navigation"


class IdMappingPriority(Enum):
    """Priority levels for ID mapping suggestions"""
    CRITICAL = "critical"  # Form controls, accessibility issues
    HIGH = "high"         # Interactive elements, navigation
    MEDIUM = "medium"     # Semantic elements, containers
    LOW = "low"          # Styling containers, decorative elements


@dataclass
class ElementAnalysis:
    """Analysis of an HTML element"""
    element_type: ElementType
    line_number: int
    element_tag: str
    current_id: Optional[str] = None
    suggested_id: Optional[str] = None
    text_content: Optional[str] = None
    attributes: Dict[str, str] = None
    accessibility_issues: List[AccessibilityIssueType] = None
    priority: IdMappingPriority = IdMappingPriority.MEDIUM
    reasoning: str = ""
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.accessibility_issues is None:
            self.accessibility_issues = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for investigation router"""
        return {
            "type": "element_analysis",
            "element_type": self.element_type.value,
            "line_number": self.line_number,
            "element_tag": self.element_tag,
            "current_id": self.current_id,
            "suggested_id": self.suggested_id,
            "text_content": self.text_content,
            "attributes": self.attributes,
            "accessibility_issues": [issue.value for issue in self.accessibility_issues],
            "priority": self.priority.value,
            "reasoning": self.reasoning,
            "timestamp": datetime.now().isoformat()
        }


@dataclass
class IdMappingResult:
    """Result of HTML ID mapping analysis"""
    file_path: str
    total_elements: int
    elements_with_ids: int
    elements_missing_ids: int
    element_analyses: List[ElementAnalysis]
    accessibility_score: float  # 0-100
    accessibility_recommendations: List[str]
    testability_improvements: List[str]
    
    @property
    def id_coverage_percentage(self) -> float:
        """Calculate percentage of elements that have IDs"""
        if self.total_elements == 0:
            return 100.0
        return (self.elements_with_ids / self.total_elements) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for investigation router"""
        return {
            "type": "id_mapping_result",
            "file_path": self.file_path,
            "total_elements": self.total_elements,
            "elements_with_ids": self.elements_with_ids,
            "elements_missing_ids": self.elements_missing_ids,
            "id_coverage_percentage": self.id_coverage_percentage,
            "accessibility_score": self.accessibility_score,
            "element_analyses": [analysis.to_dict() for analysis in self.element_analyses],
            "accessibility_recommendations": self.accessibility_recommendations,
            "testability_improvements": self.testability_improvements,
            "timestamp": datetime.now().isoformat()
        }


class IdGenerator:
    """Intelligent ID generator for HTML elements"""
    
    def __init__(self):
        self.used_ids = set()
        self.naming_conventions = {
            ElementType.BUTTON: ["btn", "button"],
            ElementType.INPUT: ["input", "field", "txt"],
            ElementType.SELECT: ["select", "dropdown", "ddl"],
            ElementType.TEXTAREA: ["textarea", "txt"],
            ElementType.FORM: ["form", "frm"],
            ElementType.HEADING: ["heading", "title"],
            ElementType.SECTION: ["section", "sec"],
            ElementType.NAV: ["nav", "navigation"],
            ElementType.MAIN: ["main", "content"],
            ElementType.DIV: ["container", "wrapper", "div"],
        }
    
    def generate_id(self, element_analysis: ElementAnalysis, context: Dict[str, str] = None) -> str:
        """
        Generate intelligent ID for an element
        
        Args:
            element_analysis: Analysis of the element
            context: Additional context (page name, section, etc.)
            
        Returns:
            Suggested ID
        """
        # Extract meaningful information
        element_type = element_analysis.element_type
        text_content = element_analysis.text_content or ""
        attributes = element_analysis.attributes
        
        # Priority order for ID generation:
        # 1. Existing 'name' attribute
        # 2. Text content (for buttons, headings)
        # 3. 'placeholder' or 'title' attributes
        # 4. 'class' attribute
        # 5. Element type with context
        
        suggested_id = None
        
        # Check for existing 'name' attribute
        if 'name' in attributes and attributes['name']:
            base_name = self._clean_name(attributes['name'])
            suggested_id = self._add_type_suffix(base_name, element_type)
        
        # Use text content for buttons and headings
        elif text_content and element_type in [ElementType.BUTTON, ElementType.HEADING, ElementType.LINK]:
            clean_text = self._clean_text_content(text_content)
            if clean_text:
                suggested_id = self._add_type_suffix(clean_text, element_type)
        
        # Check for placeholder or title attributes
        elif 'placeholder' in attributes and attributes['placeholder']:
            clean_placeholder = self._clean_text_content(attributes['placeholder'])
            suggested_id = self._add_type_suffix(clean_placeholder, element_type)
        
        elif 'title' in attributes and attributes['title']:
            clean_title = self._clean_text_content(attributes['title'])
            suggested_id = self._add_type_suffix(clean_title, element_type)
        
        # Use class attribute as fallback
        elif 'class' in attributes and attributes['class']:
            first_class = attributes['class'].split()[0]
            clean_class = self._clean_name(first_class)
            suggested_id = self._add_type_suffix(clean_class, element_type)
        
        # Generate generic ID with context
        else:
            base_name = self._generate_generic_name(element_type, context)
            suggested_id = base_name
        
        # Ensure uniqueness
        suggested_id = self._ensure_unique_id(suggested_id)
        
        return suggested_id
    
    def _clean_name(self, name: str) -> str:
        """Clean and normalize a name for use as ID"""
        # Remove special characters, keep alphanumeric and underscores
        clean = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Remove multiple underscores
        clean = re.sub(r'_+', '_', clean)
        # Remove leading/trailing underscores
        clean = clean.strip('_')
        # Convert to camelCase
        return self._to_camel_case(clean)
    
    def _clean_text_content(self, text: str) -> str:
        """Clean text content for use in ID"""
        # Remove extra whitespace and special characters
        clean = re.sub(r'[^a-zA-Z0-9\s]', '', text.strip())
        # Split into words and join with underscore
        words = clean.split()
        if not words:
            return ""
        # Take first 3 words maximum
        words = words[:3]
        return self._to_camel_case('_'.join(words))
    
    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase"""
        words = text.split('_')
        if not words:
            return ""
        
        # First word lowercase, rest title case
        result = words[0].lower()
        for word in words[1:]:
            if word:
                result += word.capitalize()
        
        return result
    
    def _add_type_suffix(self, base_name: str, element_type: ElementType) -> str:
        """Add type-specific suffix to base name"""
        if not base_name:
            return self._generate_generic_name(element_type)
        
        # Get preferred prefixes/suffixes for element type
        conventions = self.naming_conventions.get(element_type, ["element"])
        
        # Choose most appropriate convention
        if element_type == ElementType.BUTTON:
            if not base_name.lower().startswith('btn'):
                return f"btn{base_name.capitalize()}"
        elif element_type == ElementType.INPUT:
            input_type = ""  # Could be extracted from type attribute
            if not any(base_name.lower().startswith(conv) for conv in conventions):
                return f"txt{base_name.capitalize()}"
        elif element_type == ElementType.SELECT:
            if not any(base_name.lower().startswith(conv) for conv in conventions):
                return f"ddl{base_name.capitalize()}"
        elif element_type == ElementType.FORM:
            if not base_name.lower().startswith('frm'):
                return f"frm{base_name.capitalize()}"
        
        return base_name
    
    def _generate_generic_name(self, element_type: ElementType, context: Dict[str, str] = None) -> str:
        """Generate generic name for element type"""
        conventions = self.naming_conventions.get(element_type, ["element"])
        base = conventions[0]
        
        # Add context if available
        if context and context.get('section'):
            section = self._clean_name(context['section'])
            return f"{base}{section.capitalize()}"
        
        # Add counter for uniqueness
        counter = 1
        while f"{base}{counter}" in self.used_ids:
            counter += 1
        
        return f"{base}{counter}"
    
    def _ensure_unique_id(self, suggested_id: str) -> str:
        """Ensure ID is unique by adding counter if necessary"""
        if suggested_id not in self.used_ids:
            self.used_ids.add(suggested_id)
            return suggested_id
        
        counter = 1
        while f"{suggested_id}{counter}" in self.used_ids:
            counter += 1
        
        unique_id = f"{suggested_id}{counter}"
        self.used_ids.add(unique_id)
        return unique_id


class HTMLElementAnalyzer:
    """Analyzes HTML elements for ID mapping and accessibility"""
    
    def __init__(self):
        self.logger = logging.getLogger("html.analyzer")
        self.id_generator = IdGenerator()
    
    def analyze_html_file(self, file_path: str, content: str) -> IdMappingResult:
        """
        Comprehensive analysis of HTML file for ID mapping
        
        Args:
            file_path: Path to HTML file
            content: HTML content
            
        Returns:
            Complete ID mapping analysis
        """
        lines = content.split('\n')
        element_analyses = []
        
        # Track existing IDs to avoid duplicates
        existing_ids = self._extract_existing_ids(content)
        self.id_generator.used_ids.update(existing_ids)
        
        # Analyze each line for HTML elements
        for line_num, line in enumerate(lines, 1):
            analyses = self._analyze_line_elements(line, line_num)
            element_analyses.extend(analyses)
        
        # Calculate metrics
        total_elements = len(element_analyses)
        elements_with_ids = sum(1 for analysis in element_analyses if analysis.current_id)
        elements_missing_ids = total_elements - elements_with_ids
        
        # Calculate accessibility score
        accessibility_score = self._calculate_accessibility_score(element_analyses)
        
        # Generate recommendations
        accessibility_recommendations = self._generate_accessibility_recommendations(element_analyses)
        testability_improvements = self._generate_testability_improvements(element_analyses)
        
        return IdMappingResult(
            file_path=file_path,
            total_elements=total_elements,
            elements_with_ids=elements_with_ids,
            elements_missing_ids=elements_missing_ids,
            element_analyses=element_analyses,
            accessibility_score=accessibility_score,
            accessibility_recommendations=accessibility_recommendations,
            testability_improvements=testability_improvements
        )
    
    def _extract_existing_ids(self, content: str) -> Set[str]:
        """Extract all existing IDs from HTML content"""
        id_pattern = r'id=["\']([^"\']+)["\']'
        matches = re.findall(id_pattern, content, re.IGNORECASE)
        return set(matches)
    
    def _analyze_line_elements(self, line: str, line_num: int) -> List[ElementAnalysis]:
        """Analyze a line for HTML elements requiring IDs"""
        analyses = []
        
        # Define element patterns that should have IDs
        element_patterns = {
            ElementType.BUTTON: r'<button([^>]*)>(.*?)</button>|<input[^>]*type=["\']button["\'][^>]*>',
            ElementType.INPUT: r'<input([^>]*)>',
            ElementType.SELECT: r'<select([^>]*)>',
            ElementType.TEXTAREA: r'<textarea([^>]*)>',
            ElementType.FORM: r'<form([^>]*)>',
            ElementType.HEADING: r'<h([1-6])([^>]*)>(.*?)</h[1-6]>',
            ElementType.SECTION: r'<section([^>]*)>',
            ElementType.ARTICLE: r'<article([^>]*)>',
            ElementType.NAV: r'<nav([^>]*)>',
            ElementType.MAIN: r'<main([^>]*)>',
            ElementType.DIV: r'<div([^>]*class[^>]*)>',  # Only divs with classes
        }
        
        for element_type, pattern in element_patterns.items():
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                analysis = self._create_element_analysis(element_type, match, line_num, line)
                if analysis:
                    analyses.append(analysis)
        
        return analyses
    
    def _create_element_analysis(self, element_type: ElementType, match: re.Match, line_num: int, full_line: str) -> Optional[ElementAnalysis]:
        """Create element analysis from regex match"""
        try:
            full_element = match.group(0)
            attributes_str = match.group(1) if match.groups() else ""
            
            # Extract text content for certain elements
            text_content = ""
            if len(match.groups()) > 1 and match.groups()[-1]:
                text_content = match.groups()[-1].strip()
            
            # Parse attributes
            attributes = self._parse_attributes(attributes_str)
            
            # Check if element already has ID
            current_id = attributes.get('id')
            
            # Skip if element already has an ID (unless we want to validate it)
            # For now, we'll analyze all elements
            
            analysis = ElementAnalysis(
                element_type=element_type,
                line_number=line_num,
                element_tag=full_element,
                current_id=current_id,
                text_content=text_content,
                attributes=attributes,
                priority=self._determine_priority(element_type, attributes, text_content)
            )
            
            # Generate suggested ID if missing
            if not current_id:
                analysis.suggested_id = self.id_generator.generate_id(analysis)
                analysis.reasoning = self._explain_id_suggestion(analysis)
            
            # Check for accessibility issues
            analysis.accessibility_issues = self._check_accessibility_issues(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.warning(f"Error analyzing element at line {line_num}: {e}")
            return None
    
    def _parse_attributes(self, attributes_str: str) -> Dict[str, str]:
        """Parse HTML attributes string into dictionary"""
        attributes = {}
        
        # Simple attribute parsing (handles most common cases)
        attr_pattern = r'(\w+)=["\']([^"\']*)["\']'
        matches = re.findall(attr_pattern, attributes_str)
        
        for attr_name, attr_value in matches:
            attributes[attr_name.lower()] = attr_value
        
        return attributes
    
    def _determine_priority(self, element_type: ElementType, attributes: Dict[str, str], text_content: str) -> IdMappingPriority:
        """Determine priority for ID mapping based on element characteristics"""
        # Critical: Form controls and interactive elements
        if element_type in [ElementType.BUTTON, ElementType.INPUT, ElementType.SELECT, ElementType.TEXTAREA]:
            return IdMappingPriority.CRITICAL
        
        # High: Navigation and important structural elements
        if element_type in [ElementType.FORM, ElementType.NAV, ElementType.MAIN]:
            return IdMappingPriority.HIGH
        
        # High: Elements with important text content
        if text_content and len(text_content) > 5:
            return IdMappingPriority.HIGH
        
        # Medium: Semantic elements
        if element_type in [ElementType.SECTION, ElementType.ARTICLE, ElementType.HEADING]:
            return IdMappingPriority.MEDIUM
        
        # Low: Styling containers
        return IdMappingPriority.LOW
    
    def _explain_id_suggestion(self, analysis: ElementAnalysis) -> str:
        """Generate explanation for ID suggestion"""
        if analysis.text_content:
            return f"Based on text content: '{analysis.text_content}'"
        elif 'name' in analysis.attributes:
            return f"Based on name attribute: '{analysis.attributes['name']}'"
        elif 'class' in analysis.attributes:
            return f"Based on CSS class: '{analysis.attributes['class']}'"
        else:
            return f"Generic ID for {analysis.element_type.value} element"
    
    def _check_accessibility_issues(self, analysis: ElementAnalysis) -> List[AccessibilityIssueType]:
        """Check element for accessibility issues"""
        issues = []
        
        # Missing ID for form controls
        if not analysis.current_id and analysis.element_type in [ElementType.INPUT, ElementType.SELECT, ElementType.TEXTAREA]:
            issues.append(AccessibilityIssueType.MISSING_ID)
        
        # Form controls without labels
        if analysis.element_type in [ElementType.INPUT, ElementType.SELECT, ElementType.TEXTAREA]:
            if not any(attr in analysis.attributes for attr in ['aria-label', 'aria-labelledby']):
                issues.append(AccessibilityIssueType.MISSING_LABEL)
        
        # Images without alt text
        if analysis.element_type == ElementType.IMAGE and 'alt' not in analysis.attributes:
            issues.append(AccessibilityIssueType.MISSING_ALT_TEXT)
        
        # Buttons without accessible names
        if analysis.element_type == ElementType.BUTTON and not analysis.text_content and 'aria-label' not in analysis.attributes:
            issues.append(AccessibilityIssueType.MISSING_ARIA_LABEL)
        
        return issues
    
    def _calculate_accessibility_score(self, analyses: List[ElementAnalysis]) -> float:
        """Calculate overall accessibility score (0-100)"""
        if not analyses:
            return 100.0
        
        total_points = len(analyses) * 100
        deducted_points = 0
        
        for analysis in analyses:
            # Deduct points for missing IDs on critical elements
            if not analysis.current_id and analysis.priority == IdMappingPriority.CRITICAL:
                deducted_points += 20
            elif not analysis.current_id and analysis.priority == IdMappingPriority.HIGH:
                deducted_points += 10
            
            # Deduct points for accessibility issues
            for issue in analysis.accessibility_issues:
                if issue == AccessibilityIssueType.MISSING_LABEL:
                    deducted_points += 15
                elif issue == AccessibilityIssueType.MISSING_ALT_TEXT:
                    deducted_points += 10
                else:
                    deducted_points += 5
        
        score = max(0, ((total_points - deducted_points) / total_points) * 100)
        return round(score, 1)
    
    def _generate_accessibility_recommendations(self, analyses: List[ElementAnalysis]) -> List[str]:
        """Generate accessibility recommendations"""
        recommendations = []
        
        critical_missing = sum(1 for a in analyses if not a.current_id and a.priority == IdMappingPriority.CRITICAL)
        if critical_missing > 0:
            recommendations.append(f"🎯 Add IDs to {critical_missing} critical form controls for accessibility")
        
        missing_labels = sum(1 for a in analyses if AccessibilityIssueType.MISSING_LABEL in a.accessibility_issues)
        if missing_labels > 0:
            recommendations.append(f"🏷️  Add labels or aria-labels to {missing_labels} form controls")
        
        missing_alt = sum(1 for a in analyses if AccessibilityIssueType.MISSING_ALT_TEXT in a.accessibility_issues)
        if missing_alt > 0:
            recommendations.append(f"🖼️  Add alt text to {missing_alt} images")
        
        if not recommendations:
            recommendations.append("✅ Good accessibility practices detected")
        
        return recommendations
    
    def _generate_testability_improvements(self, analyses: List[ElementAnalysis]) -> List[str]:
        """Generate testability improvement suggestions"""
        improvements = []
        
        elements_needing_ids = [a for a in analyses if not a.current_id]
        if elements_needing_ids:
            improvements.append(f"🧪 Add IDs to {len(elements_needing_ids)} elements to improve automated testing")
        
        buttons_without_ids = [a for a in analyses if a.element_type == ElementType.BUTTON and not a.current_id]
        if buttons_without_ids:
            improvements.append(f"🔘 Add IDs to {len(buttons_without_ids)} buttons for better UI testing")
        
        forms_without_ids = [a for a in analyses if a.element_type == ElementType.FORM and not a.current_id]
        if forms_without_ids:
            improvements.append(f"📝 Add IDs to {len(forms_without_ids)} forms for form testing")
        
        if not improvements:
            improvements.append("✅ Elements are well-identified for testing")
        
        return improvements


class InvestigationHtmlIdMappingPlugin(BasePlugin):
    """HTML element ID mapping plugin for investigation router"""
    
    def __init__(self):
        super().__init__()
        self.analyzer = HTMLElementAnalyzer()
    
    def _get_metadata(self) -> PluginMetadata:
        """Get plugin metadata"""
        return PluginMetadata(
            plugin_id="investigation_html_mapping",
            name="Investigation HTML ID Mapping",
            version="1.0.0",
            category=PluginCategory.ANALYSIS,
            priority=PluginPriority.MEDIUM,
            description="HTML element ID mapping and accessibility analysis for investigation router",
            author="Asif Hussain",
            dependencies=[],
            hooks=[HookPoint.ON_INVESTIGATION_ANALYSIS.value],
            natural_language_patterns=[
                "html element mapping",
                "element id analysis",
                "accessibility check",
                "html id suggestions",
                "element identification"
            ]
        )
    
    def initialize(self) -> bool:
        """Initialize HTML ID mapping plugin"""
        try:
            self.logger.info("Initializing Investigation HTML ID Mapping Plugin")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize HTML mapping plugin: {e}")
            return False
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute HTML ID mapping analysis during investigation
        
        Args:
            context: Investigation context
            
        Returns:
            HTML analysis results
        """
        try:
            target_entity = context.get('target_entity')
            entity_type = context.get('entity_type', 'unknown')
            budget_remaining = context.get('budget_remaining', 0)
            
            # Only analyze HTML files
            if not (entity_type == 'file' and target_entity and 
                    Path(target_entity).suffix.lower() in ['.html', '.htm']):
                return {
                    "success": False,
                    "error": "Not an HTML file - HTML ID mapping not applicable",
                    "plugin_id": self.metadata.plugin_id
                }
            
            # Estimate token cost
            estimated_tokens = 300  # HTML analysis is relatively lightweight
            
            if estimated_tokens > budget_remaining:
                return {
                    "success": False,
                    "error": "Insufficient budget for HTML analysis",
                    "estimated_tokens": estimated_tokens,
                    "budget_remaining": budget_remaining
                }
            
            # Get HTML content
            file_content = context.get('file_content', '')
            if not file_content:
                return {
                    "success": False,
                    "error": "No file content available for analysis",
                    "plugin_id": self.metadata.plugin_id
                }
            
            # Perform HTML analysis
            mapping_result = self.analyzer.analyze_html_file(target_entity, file_content)
            
            return {
                "success": True,
                "plugin_id": self.metadata.plugin_id,
                "analysis_type": "html_id_mapping",
                "target_entity": target_entity,
                "result": mapping_result.to_dict(),
                "tokens_consumed": estimated_tokens,
                "summary": {
                    "total_elements": mapping_result.total_elements,
                    "id_coverage": f"{mapping_result.id_coverage_percentage:.1f}%",
                    "accessibility_score": f"{mapping_result.accessibility_score}/100",
                    "critical_issues": len([a for a in mapping_result.element_analyses 
                                           if a.priority == IdMappingPriority.CRITICAL and not a.current_id])
                }
            }
            
        except Exception as e:
            self.logger.error(f"HTML ID mapping analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "plugin_id": self.metadata.plugin_id
            }
    
    def cleanup(self) -> bool:
        """Cleanup HTML mapping plugin"""
        try:
            self.logger.info("Cleaning up Investigation HTML ID Mapping Plugin")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cleanup HTML mapping plugin: {e}")
            return False


def register() -> BasePlugin:
    """Register the investigation HTML ID mapping plugin"""
    return InvestigationHtmlIdMappingPlugin()