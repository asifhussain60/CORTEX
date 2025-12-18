"""
Section Selector for CORTEX 4.0

Dynamic section composition for adaptive minimalist responses.
Selects relevant sections based on context rather than using static templates.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass


class SectionType(Enum):
    """Available section types."""
    UNDERSTANDING = "understanding"
    APPROACH = "approach"
    RESPONSE = "response"
    CHANGES = "changes"
    NEXT_STEPS = "next_steps"
    CONTEXT = "context"
    ANALYSIS = "analysis"
    DETAILS = "details"
    RESULTS = "results"
    ACTIONS = "actions"
    CAUTIONS = "cautions"
    ARCHITECTURE = "architecture"
    STRATEGY = "strategy"
    IMPLEMENTATION = "implementation"
    ACHIEVEMENTS = "achievements"
    TECHNICAL = "technical"


@dataclass
class Section:
    """Section metadata."""
    type: SectionType
    emoji: str
    title: str
    required: bool


class SectionSelector:
    """
    Dynamic section selector for CORTEX 4.0 responses.
    
    Selects sections based on:
    - Response tier (INSTANT/FOCUSED/STRUCTURED/COMPREHENSIVE)
    - Context flags (has_discovery, has_challenge, etc.)
    - Content requirements
    
    Usage:
        selector = SectionSelector()
        sections = selector.select_sections(
            tier=ResponseTier.TIER3_STRUCTURED,
            context={
                "has_discovery": True,
                "has_technical_challenge": True,
                "user_action_required": True
            }
        )
    """
    
    # Section metadata
    SECTIONS = {
        SectionType.UNDERSTANDING: Section(
            type=SectionType.UNDERSTANDING,
            emoji="🎯",
            title="Understanding & Scope",
            required=False
        ),
        SectionType.APPROACH: Section(
            type=SectionType.APPROACH,
            emoji="⚡",
            title="Approach & Considerations",
            required=False
        ),
        SectionType.RESPONSE: Section(
            type=SectionType.RESPONSE,
            emoji="💬",
            title="Response",
            required=True  # Always required
        ),
        SectionType.CHANGES: Section(
            type=SectionType.CHANGES,
            emoji="📊",
            title="Impact & Changes",
            required=False
        ),
        SectionType.NEXT_STEPS: Section(
            type=SectionType.NEXT_STEPS,
            emoji="🔍",
            title="Next Steps",
            required=False
        ),
        SectionType.CONTEXT: Section(
            type=SectionType.CONTEXT,
            emoji="🎯",
            title="Context",
            required=False
        ),
        SectionType.ANALYSIS: Section(
            type=SectionType.ANALYSIS,
            emoji="⚡",
            title="Analysis",
            required=False
        ),
        SectionType.DETAILS: Section(
            type=SectionType.DETAILS,
            emoji="💬",
            title="Details",
            required=False
        ),
        SectionType.RESULTS: Section(
            type=SectionType.RESULTS,
            emoji="📊",
            title="Results",
            required=False
        ),
        SectionType.ACTIONS: Section(
            type=SectionType.ACTIONS,
            emoji="🔍",
            title="Actions",
            required=False
        ),
        SectionType.CAUTIONS: Section(
            type=SectionType.CAUTIONS,
            emoji="⚠️",
            title="Cautions",
            required=False
        ),
        SectionType.ARCHITECTURE: Section(
            type=SectionType.ARCHITECTURE,
            emoji="🏗️",
            title="Architecture",
            required=False
        ),
        SectionType.STRATEGY: Section(
            type=SectionType.STRATEGY,
            emoji="⚡",
            title="Strategy & Approach",
            required=False
        ),
        SectionType.IMPLEMENTATION: Section(
            type=SectionType.IMPLEMENTATION,
            emoji="💬",
            title="Implementation",
            required=False
        ),
        SectionType.ACHIEVEMENTS: Section(
            type=SectionType.ACHIEVEMENTS,
            emoji="🎉",
            title="Achievements",
            required=False
        ),
        SectionType.TECHNICAL: Section(
            type=SectionType.TECHNICAL,
            emoji="🔧",
            title="Technical Details",
            required=False
        ),
    }
    
    def __init__(self):
        """Initialize section selector."""
        self.logger = logging.getLogger(__name__)
    
    def select_sections(
        self,
        tier: str,  # "tier1_instant", "tier2_focused", etc.
        context: Optional[Dict] = None
    ) -> List[Section]:
        """
        Select sections for response based on tier and context.
        
        Args:
            tier: Response tier (from ResponseTierSelector)
            context: Context flags dictionary
                - has_discovery: bool
                - has_technical_challenge: bool
                - user_action_required: bool
                - multi_phase: bool
                - files_modified: bool
                - has_metrics: bool
                - system_design: bool
                - milestones_reached: bool
                - risks_present: bool
        
        Returns:
            List of Section objects in order
        """
        context = context or {}
        
        if tier == "tier1_instant":
            return self._tier1_sections(context)
        elif tier == "tier2_focused":
            return self._tier2_sections(context)
        elif tier == "tier3_structured":
            return self._tier3_sections(context)
        elif tier == "tier4_comprehensive":
            return self._tier4_sections(context)
        else:
            self.logger.warning(f"Unknown tier: {tier}, using tier3 default")
            return self._tier3_sections(context)
    
    def _tier1_sections(self, context: Dict) -> List[Section]:
        """
        TIER 1 (INSTANT): No sections needed.
        
        Direct answer only.
        """
        return []
    
    def _tier2_sections(self, context: Dict) -> List[Section]:
        """
        TIER 2 (FOCUSED): 1-2 sections.
        
        Always: response
        Conditional: context, analysis, actions
        """
        sections = []
        
        # Always include response
        sections.append(self.SECTIONS[SectionType.RESPONSE])
        
        # Add context if discovery performed
        if context.get("has_discovery"):
            sections.append(self.SECTIONS[SectionType.CONTEXT])
        
        # Add analysis if technical challenge
        if context.get("has_technical_challenge"):
            sections.append(self.SECTIONS[SectionType.ANALYSIS])
        
        # Add actions if user action required
        if context.get("user_action_required"):
            sections.append(self.SECTIONS[SectionType.ACTIONS])
        
        # Limit to 2 sections max for TIER2
        return sections[:2]
    
    def _tier3_sections(self, context: Dict) -> List[Section]:
        """
        TIER 3 (STRUCTURED): 2-4 sections (standard 5-part when complete).
        
        Always: understanding, response, changes
        Conditional: approach, next_steps
        """
        sections = []
        
        # Always include core sections
        sections.append(self.SECTIONS[SectionType.UNDERSTANDING])
        
        # Add approach if technical challenge
        if context.get("has_technical_challenge"):
            sections.append(self.SECTIONS[SectionType.APPROACH])
        
        # Always include response
        sections.append(self.SECTIONS[SectionType.RESPONSE])
        
        # Add changes if files modified or metrics available
        if context.get("files_modified") or context.get("has_metrics"):
            sections.append(self.SECTIONS[SectionType.CHANGES])
        
        # Add next steps if user action required or multi-phase
        if context.get("user_action_required") or context.get("multi_phase"):
            sections.append(self.SECTIONS[SectionType.NEXT_STEPS])
        
        return sections
    
    def _tier4_sections(self, context: Dict) -> List[Section]:
        """
        TIER 4 (COMPREHENSIVE): 4-6 sections.
        
        Always: understanding, approach, response, changes, next_steps
        Conditional: architecture, results, achievements, cautions
        """
        sections = []
        
        # Always include core 5-part structure
        sections.append(self.SECTIONS[SectionType.UNDERSTANDING])
        sections.append(self.SECTIONS[SectionType.APPROACH])
        
        # Add architecture if system design
        if context.get("system_design"):
            sections.append(self.SECTIONS[SectionType.ARCHITECTURE])
        
        sections.append(self.SECTIONS[SectionType.RESPONSE])
        
        # Add results if metrics available
        if context.get("has_metrics"):
            sections.append(self.SECTIONS[SectionType.RESULTS])
        
        sections.append(self.SECTIONS[SectionType.CHANGES])
        
        # Add achievements if milestones reached
        if context.get("milestones_reached"):
            sections.append(self.SECTIONS[SectionType.ACHIEVEMENTS])
        
        # Add cautions if risks present
        if context.get("risks_present"):
            sections.append(self.SECTIONS[SectionType.CAUTIONS])
        
        sections.append(self.SECTIONS[SectionType.NEXT_STEPS])
        
        return sections
    
    def get_section_titles(self, sections: List[Section]) -> List[str]:
        """
        Get formatted section titles with emojis.
        
        Args:
            sections: List of Section objects
        
        Returns:
            List of formatted titles (e.g., "### 🎯 Understanding & Scope")
        """
        return [f"### {s.emoji} {s.title}" for s in sections]
    
    def validate_section_count(
        self,
        tier: str,
        sections: List[Section]
    ) -> bool:
        """
        Validate section count is appropriate for tier.
        
        Args:
            tier: Response tier
            sections: Selected sections
        
        Returns:
            True if count is valid
        """
        count = len(sections)
        
        if tier == "tier1_instant":
            return count == 0
        elif tier == "tier2_focused":
            return 1 <= count <= 2
        elif tier == "tier3_structured":
            return 2 <= count <= 5  # Allow 5-part structure
        elif tier == "tier4_comprehensive":
            return 4 <= count <= 6
        
        return False
