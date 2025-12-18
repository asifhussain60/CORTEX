"""
Tier Selector - Determines response complexity tier

Logic:
1. Check for factual queries → TIER 1 (INSTANT)
2. Check for single concepts → TIER 2 (FOCUSED)
3. Check for multi-faceted → TIER 3 (STRUCTURED)
4. Default to TIER 4 (COMPREHENSIVE)
"""

import re
from typing import Dict, Any

from src.templates.types import ResponseTier, TemplateContext


class TierSelector:
    """Selects the appropriate response tier based on request context"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the tier selector.
        
        Args:
            config: Template configuration dictionary
        """
        self.config = config
        self.routing = config.get("routing", {})
    
    def select_tier(self, context: TemplateContext) -> ResponseTier:
        """
        Select the appropriate tier for the request.
        
        Args:
            context: Template context with request details
        
        Returns:
            Selected ResponseTier
        """
        # Check for success template (overrides normal tier selection)
        if context.all_work_complete and context.no_errors and context.no_user_action_required:
            # Success responses are always TIER 4 (COMPREHENSIVE)
            return ResponseTier.COMPREHENSIVE
        
        # TIER 1: Instant responses for factual queries
        if self._is_tier1_instant(context):
            return ResponseTier.INSTANT
        
        # TIER 2: Focused responses for single concepts
        if self._is_tier2_focused(context):
            return ResponseTier.FOCUSED
        
        # TIER 3: Structured responses for multi-faceted requests
        if self._is_tier3_structured(context):
            return ResponseTier.STRUCTURED
        
        # TIER 4: Comprehensive responses (default)
        return ResponseTier.COMPREHENSIVE
    
    def _is_tier1_instant(self, context: TemplateContext) -> bool:
        """Check if request qualifies for TIER 1 (INSTANT)"""
        tier1_config = self.routing.get("tier1_instant", {})
        triggers = tier1_config.get("triggers", {})
        
        # Check for question words
        question_words = triggers.get("question_words", [])
        request_lower = context.request.lower()
        has_question_word = any(word in request_lower for word in question_words)
        
        # Check for factual lookup patterns
        is_factual = context.is_factual_query or triggers.get("factual_lookup", False)
        
        # Check token estimate
        token_limit_str = triggers.get("estimated_tokens", "< 50")
        token_limit = self._parse_token_limit(token_limit_str)
        within_token_limit = context.estimated_tokens > 0 and context.estimated_tokens < token_limit
        
        # Must have question word OR be marked factual, AND be within token limit
        if (has_question_word or is_factual) and (within_token_limit or context.estimated_tokens == 0):
            return not context.requires_explanation
        
        return False
    
    def _is_tier2_focused(self, context: TemplateContext) -> bool:
        """Check if request qualifies for TIER 2 (FOCUSED)"""
        tier2_config = self.routing.get("tier2_focused", {})
        triggers = tier2_config.get("triggers", {})
        
        # Check for single concept
        is_single_concept = context.is_single_concept or triggers.get("single_concept", False)
        
        # Check token range
        token_range = triggers.get("estimated_tokens", [50, 200])
        if isinstance(token_range, list) and len(token_range) == 2:
            within_range = token_range[0] <= context.estimated_tokens <= token_range[1]
        else:
            within_range = context.estimated_tokens < 200
        
        # Check sections needed
        sections_range = triggers.get("sections_needed", [1, 2])
        needs_few_sections = not context.has_architecture and not context.has_technical_depth
        
        return is_single_concept and (within_range or context.estimated_tokens == 0) and needs_few_sections
    
    def _is_tier3_structured(self, context: TemplateContext) -> bool:
        """Check if request qualifies for TIER 3 (STRUCTURED)"""
        tier3_config = self.routing.get("tier3_structured", {})
        triggers = tier3_config.get("triggers", {})
        
        # Check for multi-faceted nature
        is_multi_faceted = context.requires_multiple_aspects or triggers.get("multi_faceted", False)
        
        # Check token range
        token_range = triggers.get("estimated_tokens", [200, 600])
        if isinstance(token_range, list) and len(token_range) == 2:
            within_range = token_range[0] <= context.estimated_tokens <= token_range[1]
        else:
            within_range = 200 <= context.estimated_tokens < 600
        
        # Check sections needed
        sections_range = triggers.get("sections_needed", [2, 4])
        has_moderate_sections = context.has_modifications or context.requires_explanation
        
        return is_multi_faceted and (within_range or context.estimated_tokens == 0) and has_moderate_sections
    
    def _parse_token_limit(self, limit_str: str) -> int:
        """Parse token limit string like '< 50' or '[50, 200]'"""
        # Handle comparison operators
        match = re.search(r'<\s*(\d+)', limit_str)
        if match:
            return int(match.group(1))
        
        # Handle numeric values
        match = re.search(r'(\d+)', limit_str)
        if match:
            return int(match.group(1))
        
        return 50  # Default
