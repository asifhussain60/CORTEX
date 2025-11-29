"""
CORTEX Vision API Extraction Formatter
Formats Vision API extraction results for display in responses

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence level thresholds for vision extraction"""
    HIGH = "HIGH"      # ≥85%
    MEDIUM = "MEDIUM"  # 70-84%
    LOW = "LOW"        # <70%


@dataclass
class ExtractedElement:
    """Individual element extracted from image"""
    element_type: str
    label: str
    confidence: float
    attributes: Optional[Dict[str, Any]] = None
    
    @property
    def confidence_level(self) -> ConfidenceLevel:
        """Determine confidence level from score"""
        if self.confidence >= 0.85:
            return ConfidenceLevel.HIGH
        elif self.confidence >= 0.70:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW


@dataclass
class VisionAnalysisResult:
    """Complete vision analysis result"""
    image_path: str
    image_width: int
    image_height: int
    image_size_kb: float
    extracted_elements: List[ExtractedElement]
    inferred_requirements: List[str]
    processing_time_ms: float
    api_version: str = "GitHub Copilot Vision API v2.1"


class VisionExtractionFormatter:
    """
    Formats Vision API extraction results for user-facing display
    
    Categories:
    - UI Elements: buttons, inputs, labels, checkboxes, dropdowns
    - Text Content: headings, body text, error messages, tooltips
    - Layout: positioning, spacing, alignment, grouping
    - Colors: primary, secondary, accent, backgrounds
    - Branding: logos, icons, typography
    - Technical: form structure, validation hints, API endpoints
    """
    
    # Element type mappings for display
    ELEMENT_CATEGORIES = {
        'button': 'Buttons',
        'input': 'Text Fields',
        'label': 'Labels',
        'checkbox': 'Checkboxes',
        'radio': 'Radio Buttons',
        'dropdown': 'Dropdowns',
        'link': 'Links',
        'heading': 'Headings',
        'text': 'Text Content',
        'logo': 'Branding',
        'icon': 'Icons',
        'image': 'Images',
        'container': 'Layout Containers'
    }
    
    # Confidence indicators
    CONFIDENCE_INDICATORS = {
        ConfidenceLevel.HIGH: "✅",
        ConfidenceLevel.MEDIUM: "⚠️",
        ConfidenceLevel.LOW: "❓"
    }
    
    def format_response_header(self, result: VisionAnalysisResult) -> str:
        """
        Format Vision API response header for chat display
        
        Args:
            result: Vision analysis result
        
        Returns:
            Formatted header string
        """
        return (
            f"# CORTEX Interactive Planning 🖼️ [Vision API Active]\n"
            f"**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX\n\n"
            f"---\n\n"
            f"## Vision Analysis\n\n"
            f"Analyzing attached image: `{result.image_path}` "
            f"({result.image_width}x{result.image_height}, {result.image_size_kb:.0f} KB)\n"
        )
    
    def format_extracted_elements(self, result: VisionAnalysisResult) -> str:
        """
        Format extracted elements by category with confidence indicators
        
        Args:
            result: Vision analysis result
        
        Returns:
            Formatted elements string
        """
        # Group elements by category
        categorized = self._categorize_elements(result.extracted_elements)
        
        lines = ["   🔍 **Extracted Elements:**"]
        
        for category, elements in categorized.items():
            if not elements:
                continue
            
            # Category header
            lines.append(f"   {category}:")
            
            # Elements with confidence indicators
            for element in elements:
                indicator = self.CONFIDENCE_INDICATORS[element.confidence_level]
                confidence_pct = f"{element.confidence * 100:.0f}%"
                
                if element.confidence_level == ConfidenceLevel.LOW:
                    note = f" ({confidence_pct} - low confidence, verify manually)"
                elif element.confidence_level == ConfidenceLevel.MEDIUM:
                    note = f" ({confidence_pct} - verify accuracy)"
                else:
                    note = f" ({confidence_pct})"
                
                # Format element with attributes if present
                if element.attributes:
                    attr_str = self._format_attributes(element.attributes)
                    lines.append(f"   {indicator} {element.label}{note} {attr_str}")
                else:
                    lines.append(f"   {indicator} {element.label}{note}")
        
        return "\n".join(lines)
    
    def format_inferred_requirements(self, requirements: List[str]) -> str:
        """
        Format inferred requirements from vision analysis
        
        Args:
            requirements: List of inferred requirements
        
        Returns:
            Formatted requirements string
        """
        if not requirements:
            return ""
        
        lines = ["   🎯 **Inferred Requirements:**"]
        for i, req in enumerate(requirements, 1):
            lines.append(f"   {i}. {req}")
        
        return "\n".join(lines)
    
    def format_complete_vision_section(self, result: VisionAnalysisResult) -> str:
        """
        Format complete vision section for response
        
        Args:
            result: Vision analysis result
        
        Returns:
            Complete formatted vision section
        """
        sections = [
            self.format_response_header(result),
            self.format_extracted_elements(result),
            "",
            self.format_inferred_requirements(result.inferred_requirements)
        ]
        
        return "\n".join(sections)
    
    def format_debug_info(self, result: VisionAnalysisResult) -> str:
        """
        Format detailed debug information for Vision API
        
        Args:
            result: Vision analysis result
        
        Returns:
            Formatted debug string
        """
        lines = [
            "🐛 **Vision API Debug Info:**",
            "",
            f"🔌 API Used: {result.api_version}",
            f"⏱️ Processing Time: {result.processing_time_ms:.1f}ms",
            f"🖼️ Image Preprocessing: {result.image_width}x{result.image_height}",
            "",
            "📊 Raw Extraction Results:",
            f"   - Total elements detected: {len(result.extracted_elements)}",
            f"   - High confidence (≥85%): {sum(1 for e in result.extracted_elements if e.confidence_level == ConfidenceLevel.HIGH)}",
            f"   - Medium confidence (70-84%): {sum(1 for e in result.extracted_elements if e.confidence_level == ConfidenceLevel.MEDIUM)}",
            f"   - Low confidence (<70%): {sum(1 for e in result.extracted_elements if e.confidence_level == ConfidenceLevel.LOW)}",
            "",
            "🧠 Classification Confidence:"
        ]
        
        # Show confidence for each element type
        for element in result.extracted_elements:
            status = "PASS" if element.confidence >= 0.70 else "FAIL - flagged"
            lines.append(
                f"   - {element.element_type.capitalize()}: {element.confidence:.2f} "
                f"(threshold: 0.70, {status})"
            )
        
        # Warnings for low confidence items
        low_conf = [e for e in result.extracted_elements if e.confidence_level == ConfidenceLevel.LOW]
        if low_conf:
            lines.extend([
                "",
                "⚠️ Warnings:"
            ])
            for element in low_conf:
                lines.append(f"   - Low confidence detected: {element.label}")
            lines.append("   - Recommend manual verification for flagged items")
        
        return "\n".join(lines)
    
    def format_failure_notice(self, 
                            image_path: str, 
                            error_message: str,
                            fallback_inference: Optional[str] = None) -> str:
        """
        Format graceful failure message when Vision API unavailable
        
        Args:
            image_path: Path to image that failed
            error_message: Error message from API
            fallback_inference: Optional filename-based inference
        
        Returns:
            Formatted failure notice
        """
        lines = [
            "⚠️ **Vision API Notice:**",
            "",
            f"Vision API is currently unavailable ({error_message}).",
            "",
            "📋 Fallback Mode:"
        ]
        
        if fallback_inference:
            lines.extend([
                f"   - Detected image: `{image_path}`",
                f"   - Inferred from filename: {fallback_inference}",
                "   - Proceeding with standard planning workflow"
            ])
        else:
            lines.extend([
                f"   - Image detected: `{image_path}`",
                "   - Unable to analyze contents automatically",
                "   - Proceeding with manual planning workflow"
            ])
        
        lines.extend([
            "",
            "💡 Tip: You can manually describe the screenshot:",
            '   "The mockup shows email/password fields with a blue sign-in button"'
        ])
        
        return "\n".join(lines)
    
    def _categorize_elements(self, elements: List[ExtractedElement]) -> Dict[str, List[ExtractedElement]]:
        """
        Group elements by category for organized display
        
        Args:
            elements: List of extracted elements
        
        Returns:
            Dictionary mapping category names to element lists
        """
        categorized = {}
        
        for element in elements:
            category = self.ELEMENT_CATEGORIES.get(element.element_type, 'Other')
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(element)
        
        # Sort categories by importance
        category_order = [
            'Text Fields', 'Buttons', 'Checkboxes', 'Radio Buttons',
            'Dropdowns', 'Links', 'Labels', 'Headings', 'Text Content',
            'Branding', 'Icons', 'Images', 'Layout Containers', 'Other'
        ]
        
        ordered = {}
        for cat in category_order:
            if cat in categorized:
                ordered[cat] = categorized[cat]
        
        return ordered
    
    def _format_attributes(self, attributes: Dict[str, Any]) -> str:
        """
        Format element attributes for display
        
        Args:
            attributes: Dictionary of attributes
        
        Returns:
            Formatted attribute string
        """
        parts = []
        
        # Common attributes to display
        if 'placeholder' in attributes:
            parts.append(f"placeholder: \"{attributes['placeholder']}\"")
        if 'color' in attributes:
            parts.append(f"color: {attributes['color']}")
        if 'required' in attributes and attributes['required']:
            parts.append("required")
        if 'disabled' in attributes and attributes['disabled']:
            parts.append("disabled")
        
        return f"[{', '.join(parts)}]" if parts else ""
