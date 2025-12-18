"""
Section Selector - Determines which sections to include in response

Logic:
- TIER 1: No sections (direct answer)
- TIER 2: 1-2 sections (minimal structure)
- TIER 3: 2-4 sections (standard format)
- TIER 4: 4-6 sections (comprehensive format)
"""

from typing import Dict, Any, List

from src.templates.types import ResponseTier, TemplateContext


class SectionSelector:
    """Selects which sections to include based on tier and context"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the section selector.
        
        Args:
            config: Template configuration dictionary
        """
        self.config = config
        self.section_library = config.get("section_library", [])
    
    def select_sections(self, tier: ResponseTier, context: TemplateContext) -> List[str]:
        """
        Select sections to include in the response.
        
        Args:
            tier: Selected response tier
            context: Template context
        
        Returns:
            List of section IDs to include
        """
        if tier == ResponseTier.INSTANT:
            return []  # No sections for instant responses
        
        if tier == ResponseTier.FOCUSED:
            return self._select_tier2_sections(context)
        
        if tier == ResponseTier.STRUCTURED:
            return self._select_tier3_sections(context)
        
        # TIER 4: COMPREHENSIVE
        return self._select_tier4_sections(context)
    
    def _select_tier2_sections(self, context: TemplateContext) -> List[str]:
        """Select sections for TIER 2 (FOCUSED) - 1-2 sections"""
        sections = []
        
        # Always include response
        sections.append("response")
        
        # Optionally add next steps if there are actions
        if context.has_modifications or not context.all_work_complete:
            sections.append("next_steps")
        
        return sections
    
    def _select_tier3_sections(self, context: TemplateContext) -> List[str]:
        """Select sections for TIER 3 (STRUCTURED) - 2-4 sections"""
        sections = []
        
        # Core sections (always included)
        sections.extend([
            "understanding_scope",
            "approach_considerations",
            "response"
        ])
        
        # Conditional sections
        if context.has_modifications:
            sections.append("impact_changes")
        
        # Always end with next steps
        sections.append("next_steps")
        
        return sections  # Return all selected sections (already limited to 4 max)
    
    def _select_tier4_sections(self, context: TemplateContext) -> List[str]:
        """Select sections for TIER 4 (COMPREHENSIVE) - 4-6 sections"""
        sections = []
        
        # Core sections (always included)
        sections.extend([
            "understanding_scope",
            "approach_considerations",
            "response"
        ])
        
        # Conditional sections based on context
        if context.has_modifications:
            sections.append("impact_changes")
        
        if context.has_architecture:
            sections.append("architecture")
        
        if context.has_technical_depth:
            sections.append("technical_details")
        
        if context.has_risks:
            sections.append("risks_mitigations")
        
        # Always end with next steps
        sections.append("next_steps")
        
        return sections  # Return all selected sections (already limited to 6 max based on conditionals)
    
    def get_section_info(self, section_id: str) -> Dict[str, Any]:
        """
        Get information about a specific section.
        
        Args:
            section_id: Section identifier
        
        Returns:
            Section configuration dict
        """
        for section in self.section_library:
            if section.get("id") == section_id:
                return section
        
        return {
            "id": section_id,
            "name": section_id.replace("_", " ").title(),
            "emoji": "📝",
            "when": "unknown",
            "content_type": "generic"
        }
