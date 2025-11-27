"""
CORTEX 3.0 - Smart Hint Generator

Purpose: Generate Smart Hint prompts for valuable conversations.
         Conditional display based on quality score threshold.

Architecture:
- Generates formatted Smart Hint section for response templates
- Shows only when conversation quality meets threshold (≥GOOD)
- Provides one-click capture trigger via /CORTEX commands
- Integrates with Quality Monitor for real-time decisions

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from src.tier1.conversation_quality import QualityScore


logger = logging.getLogger(__name__)


@dataclass
class SmartHint:
    """Smart Hint prompt for conversation capture."""
    should_display: bool
    content: str
    quality_score: int
    quality_level: str
    reasoning: str


class SmartHintGenerator:
    """
    Generates Smart Hint prompts for valuable conversations.
    
    Smart Hint Format (appears AFTER Response, BEFORE Next Steps):
    
    ---
    
    > ### 💡 CORTEX Learning Opportunity
    > 
    > **This conversation has exceptional strategic value:**
    > - Multi-phase planning with clear execution
    > - Design decisions documented
    > - Complete implementation with tests
    > 
    > **Quality Score: {score}/10 ({level})**
    > 
    > 📁 **Two-step capture:**  
    > 1. Say "/CORTEX Capture this conversation" to create empty file
    > 2. Paste conversation into file and save
    > 3. Say "/CORTEX Import this conversation" to import to brain
    > 
    > *Or dismiss: Say "skip" and I won't suggest this again*
    
    ---
    """
    
    def __init__(
        self,
        quality_threshold: str = "GOOD",
        enable_hints: bool = True
    ):
        """
        Initialize Smart Hint generator.
        
        Args:
            quality_threshold: Minimum quality level for hints (GOOD or EXCELLENT)
            enable_hints: Master switch to disable hints globally
        """
        self.quality_threshold = quality_threshold
        self.enable_hints = enable_hints
        
        # Map quality levels to numeric scores for user display
        self.level_to_score = {
            "EXCELLENT": 10,
            "GOOD": 7,
            "FAIR": 5,
            "LOW": 2
        }
        
        logger.info(
            f"SmartHintGenerator initialized: threshold={quality_threshold}, "
            f"enabled={enable_hints}"
        )
    
    def generate_hint(
        self,
        quality_score: QualityScore,
        hint_already_shown: bool = False
    ) -> SmartHint:
        """
        Generate Smart Hint based on conversation quality.
        
        Args:
            quality_score: Quality score from ConversationQualityAnalyzer
            hint_already_shown: Whether hint already shown in this session
            
        Returns:
            SmartHint with display decision and formatted content
        """
        # Determine if hint should be displayed
        should_display = self._should_display_hint(
            quality_score,
            hint_already_shown
        )
        
        if not should_display:
            return SmartHint(
                should_display=False,
                content="",
                quality_score=quality_score.total_score,
                quality_level=quality_score.level,
                reasoning=quality_score.reasoning
            )
        
        # Generate hint content
        content = self._format_hint_content(quality_score)
        
        logger.info(
            f"Generated Smart Hint: {quality_score.level} "
            f"({quality_score.total_score} points)"
        )
        
        return SmartHint(
            should_display=True,
            content=content,
            quality_score=quality_score.total_score,
            quality_level=quality_score.level,
            reasoning=quality_score.reasoning
        )
    
    def _should_display_hint(
        self,
        quality_score: QualityScore,
        hint_already_shown: bool
    ) -> bool:
        """
        Determine if hint should be displayed.
        
        Args:
            quality_score: Quality score object
            hint_already_shown: Whether hint shown in current session
            
        Returns:
            True if hint should be displayed
        """
        # Check master switch
        if not self.enable_hints:
            return False
        
        # Check if hint already shown
        if hint_already_shown:
            return False
        
        # Check quality threshold
        if not quality_score.should_show_hint:
            return False
        
        return True
    
    def _format_hint_content(self, quality_score: QualityScore) -> str:
        """
        Format Smart Hint content with quality details.
        
        Args:
            quality_score: Quality score object
            
        Returns:
            Formatted hint content (markdown)
        """
        # Build strategic value list
        value_items = self._build_value_items(quality_score)
        
        # Map internal score to user-friendly /10 scale
        display_score = self._map_score_to_ten(quality_score.total_score)
        
        hint_content = f"""---

> ### 💡 CORTEX Learning Opportunity
> 
> **This conversation has strategic value:**
{value_items}> 
> **Quality Score: {display_score}/10 ({quality_score.level})**
> 
> 📁 **Two-step capture:**  
> 1. Say "/CORTEX Capture this conversation" to create empty file
> 2. Paste conversation into file and save
> 3. Say "/CORTEX Import this conversation" to import to brain
> 
> *Or dismiss: Say "skip" and I won't suggest this again*

---"""
        
        return hint_content
    
    def _build_value_items(self, quality_score: QualityScore) -> str:
        """
        Build list of strategic value items.
        
        Args:
            quality_score: Quality score object
            
        Returns:
            Formatted bullet list of value items
        """
        items = []
        elements = quality_score.elements
        
        if elements.multi_phase_planning:
            items.append(f"> - Multi-phase planning ({elements.phase_count} phases)")
        
        if elements.challenge_accept_flow:
            items.append("> - Challenge/Accept reasoning documented")
        
        if elements.design_decisions:
            items.append("> - Design decisions and trade-offs discussed")
        
        if elements.code_implementation:
            items.append("> - Code implementation included")
        
        if elements.architectural_discussion:
            items.append("> - Architectural patterns discussed")
        
        if elements.file_references > 0:
            items.append(f"> - {elements.file_references} file reference(s)")
        
        if elements.next_steps_provided:
            items.append("> - Clear next steps provided")
        
        # If no specific items, use generic message
        if not items:
            items.append("> - Strategic conversation with learning value")
        
        return "\n".join(items) + "\n"
    
    def _map_score_to_ten(self, internal_score: int) -> int:
        """
        Map internal scoring (0-30+) to user-friendly /10 scale.
        
        Internal scores:
        - EXCELLENT: 19+ points
        - GOOD: 10-18 points
        - FAIR: 2-9 points
        - LOW: 0-1 points
        
        Mapped to /10:
        - EXCELLENT (19+): 9-10
        - GOOD (10-18): 7-8
        - FAIR (2-9): 4-6
        - LOW (0-1): 1-3
        
        Args:
            internal_score: Internal quality score
            
        Returns:
            Score on /10 scale
        """
        if internal_score >= 19:
            # EXCELLENT: Map 19-30+ to 9-10
            return min(10, 9 + (internal_score - 19) // 6)
        elif internal_score >= 10:
            # GOOD: Map 10-18 to 7-8
            if internal_score >= 14:
                return 8
            else:
                return 7
        elif internal_score >= 2:
            # FAIR: Map 2-9 to 4-6
            return min(6, 4 + (internal_score - 2) // 3)
        else:
            # LOW: 0-1 to 1-3
            return max(1, internal_score + 1)
    
    def generate_dismissal_response(self) -> str:
        """
        Generate response when user dismisses hint.
        
        Returns:
            Confirmation message
        """
        return (
            "Noted. I won't suggest saving this conversation again. "
            "You can always manually capture conversations by saying "
            "\"/CORTEX Capture this conversation\" anytime."
        )


def create_hint_generator(config: Optional[Dict[str, Any]] = None) -> SmartHintGenerator:
    """
    Factory function to create Smart Hint generator.
    
    Args:
        config: Optional configuration dict
            - quality_threshold: str (default: "GOOD")
            - enable_hints: bool (default: True)
            
    Returns:
        Configured SmartHintGenerator instance
    """
    if not config:
        config = {}
    
    threshold = config.get('quality_threshold', 'GOOD')
    enabled = config.get('enable_hints', True)
    
    return SmartHintGenerator(
        quality_threshold=threshold,
        enable_hints=enabled
    )
