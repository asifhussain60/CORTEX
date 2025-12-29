"""
Response Tier Selector for CORTEX 4.0

Intelligent tier selection for adaptive minimalist response system.
Routes requests to appropriate tier (INSTANT/FOCUSED/STRUCTURED/COMPREHENSIVE)
based on complexity, content type, and token estimation.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class ResponseTier(Enum):
    """Response tier levels."""
    TIER1_INSTANT = "tier1_instant"  # <50 tokens, direct answer
    TIER2_FOCUSED = "tier2_focused"  # 50-200 tokens, single concept
    TIER3_STRUCTURED = "tier3_structured"  # 200-600 tokens, multi-faceted
    TIER4_COMPREHENSIVE = "tier4_comprehensive"  # 600+ tokens, complex


@dataclass
class RequestAnalysis:
    """Analysis of user request for tier selection."""
    request: str
    is_factual: bool
    is_single_concept: bool
    is_multi_faceted: bool
    requires_explanation: bool
    estimated_tokens: int
    question_type: Optional[str]
    complexity_score: float


class ResponseTierSelector:
    """
    Intelligent tier selector for CORTEX 4.0 response system.
    
    Decision algorithm:
    1. Check if factual query without explanation needed → TIER1
    2. Estimate token count
    3. Check single concept vs multi-faceted
    4. Route to appropriate tier
    
    Usage:
        selector = ResponseTierSelector()
        tier = selector.select_tier("what's the square root of 144?")
        # Returns: ResponseTier.TIER1_INSTANT
    """
    
    # Factual question patterns
    FACTUAL_PATTERNS = [
        r"\bwhat\s+is\s+the\s+\w+\s+of\b",  # "what is the X of Y"
        r"\bhow\s+many\b",  # "how many"
        r"\bhow\s+much\b",  # "how much"
        r"\bwhich\s+(file|directory|folder)\b",  # "which file/directory"
        r"\bwhere\s+is\b",  # "where is"
        r"\bwhen\s+was\b",  # "when was"
        r"\bwho\s+(is|wrote|created)\b",  # "who is/wrote/created"
    ]
    
    # Question word indicators
    QUESTION_WORDS = {
        "what", "where", "when", "which", "who", 
        "how many", "how much", "list", "show"
    }
    
    # Single value response indicators
    SINGLE_VALUE_INDICATORS = [
        "square root", "calculate", "count", "sum", "average",
        "list files", "show directory", "version", "status"
    ]
    
    # Explanation requirement indicators
    EXPLANATION_INDICATORS = [
        "explain", "why", "how does", "describe", "what's the difference",
        "compare", "analyze", "review", "understand"
    ]
    
    # Multi-phase/complex indicators
    COMPLEX_INDICATORS = [
        "implement", "create", "build", "design", "architect",
        "migrate", "refactor", "optimize", "plan", "orchestrate",
        "system", "workflow", "maintenance", "deployment"
    ]
    
    def __init__(self):
        """Initialize tier selector."""
        self.logger = logging.getLogger(__name__)
    
    def select_tier(
        self,
        request: str,
        context: Optional[Dict] = None
    ) -> ResponseTier:
        """
        Select appropriate response tier for request.
        
        Args:
            request: User's request string
            context: Optional context dictionary with hints
                - has_discovery: bool
                - multi_phase: bool
                - estimated_tokens: int
        
        Returns:
            Selected ResponseTier
        """
        context = context or {}
        
        # Analyze request
        analysis = self._analyze_request(request, context)
        
        # Decision tree
        
        # Step 1: Factual check
        if analysis.is_factual and not analysis.requires_explanation:
            self.logger.debug(f"Selected TIER1 (factual): {request[:50]}")
            return ResponseTier.TIER1_INSTANT
        
        # Step 2: Token estimate check
        if analysis.estimated_tokens < 200:
            # Check if single concept
            if analysis.is_single_concept:
                self.logger.debug(f"Selected TIER2 (focused): {request[:50]}")
                return ResponseTier.TIER2_FOCUSED
            else:
                self.logger.debug(f"Selected TIER3 (structured): {request[:50]}")
                return ResponseTier.TIER3_STRUCTURED
        
        # Step 3: Complexity check
        if analysis.estimated_tokens < 600 and not context.get("multi_phase"):
            self.logger.debug(f"Selected TIER3 (structured): {request[:50]}")
            return ResponseTier.TIER3_STRUCTURED
        else:
            self.logger.debug(f"Selected TIER4 (comprehensive): {request[:50]}")
            return ResponseTier.TIER4_COMPREHENSIVE
    
    def _analyze_request(
        self,
        request: str,
        context: Dict
    ) -> RequestAnalysis:
        """
        Analyze request characteristics.
        
        Args:
            request: User's request string
            context: Context dictionary
        
        Returns:
            RequestAnalysis with all characteristics
        """
        request_lower = request.lower()
        
        # Check factual
        is_factual = self._is_factual_query(request_lower)
        
        # Check explanation requirement
        requires_explanation = self._requires_explanation(request_lower)
        
        # Check single concept vs multi-faceted
        is_single_concept = self._is_single_concept(request_lower)
        is_multi_faceted = not is_single_concept and self._is_multi_faceted(request_lower)
        
        # Estimate tokens (use context hint if available)
        estimated_tokens = context.get("estimated_tokens") or self._estimate_tokens(
            request,
            is_single_concept,
            is_multi_faceted,
            requires_explanation
        )
        
        # Determine question type
        question_type = self._get_question_type(request_lower)
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity(
            request_lower,
            is_factual,
            is_single_concept,
            is_multi_faceted,
            requires_explanation
        )
        
        return RequestAnalysis(
            request=request,
            is_factual=is_factual,
            is_single_concept=is_single_concept,
            is_multi_faceted=is_multi_faceted,
            requires_explanation=requires_explanation,
            estimated_tokens=estimated_tokens,
            question_type=question_type,
            complexity_score=complexity_score
        )
    
    def _is_factual_query(self, request_lower: str) -> bool:
        """Check if request is factual query."""
        # Check patterns
        for pattern in self.FACTUAL_PATTERNS:
            if re.search(pattern, request_lower):
                return True
        
        # Check single value indicators
        for indicator in self.SINGLE_VALUE_INDICATORS:
            if indicator in request_lower:
                return True
        
        # Check question words at start
        for word in self.QUESTION_WORDS:
            if request_lower.startswith(word):
                return True
        
        return False
    
    def _requires_explanation(self, request_lower: str) -> bool:
        """Check if request requires explanation."""
        for indicator in self.EXPLANATION_INDICATORS:
            if indicator in request_lower:
                return True
        return False
    
    def _is_single_concept(self, request_lower: str) -> bool:
        """Check if request focuses on single concept."""
        # Single concept indicators:
        # - Short request (<100 chars)
        # - No "and" connectors
        # - No multiple verbs
        # - Starts with explanation request
        
        if len(request_lower) < 100:
            if " and " not in request_lower:
                if request_lower.startswith(("explain ", "what is ", "how does ")):
                    return True
        
        return False
    
    def _is_multi_faceted(self, request_lower: str) -> bool:
        """Check if request is multi-faceted."""
        # Multi-faceted indicators:
        # - Multiple "and" connectors
        # - Multiple verbs (implement + test + deploy)
        # - Complex operation keywords
        
        if request_lower.count(" and ") >= 2:
            return True
        
        for indicator in self.COMPLEX_INDICATORS:
            if indicator in request_lower:
                return True
        
        return False
    
    def _estimate_tokens(
        self,
        request: str,
        is_single_concept: bool,
        is_multi_faceted: bool,
        requires_explanation: bool
    ) -> int:
        """
        Estimate response token count.
        
        Heuristics:
        - Factual, no explanation: 10-30 tokens
        - Single concept with explanation: 80-150 tokens
        - Multi-faceted: 300-500 tokens
        - Complex operations: 600-1000 tokens
        """
        request_lower = request.lower()
        
        # Check for complex indicators (workflow, system, orchestration)
        complex_high_token_indicators = [
            "workflow", "system", "orchestration", "migration",
            "maintenance", "deployment"
        ]
        
        for indicator in complex_high_token_indicators:
            if indicator in request_lower:
                return 650  # Force TIER4
        
        # Base estimate from request length
        request_length = len(request)
        
        if request_length < 30 and not requires_explanation:
            return 20  # Quick factual
        
        if is_single_concept:
            return 120  # Focused explanation
        
        if is_multi_faceted:
            # Check if really complex (3+ connectors or complex keywords)
            if request.lower().count(" and ") >= 2:
                return 650  # TIER4
            return 400  # TIER3
        
        # Default to moderate
        return 250
    
    def _get_question_type(self, request_lower: str) -> Optional[str]:
        """Identify question type."""
        if request_lower.startswith("what"):
            return "what"
        elif request_lower.startswith("how"):
            return "how"
        elif request_lower.startswith("why"):
            return "why"
        elif request_lower.startswith("which"):
            return "which"
        elif request_lower.startswith("where"):
            return "where"
        elif request_lower.startswith("when"):
            return "when"
        return None
    
    def _calculate_complexity(
        self,
        request_lower: str,
        is_factual: bool,
        is_single_concept: bool,
        is_multi_faceted: bool,
        requires_explanation: bool
    ) -> float:
        """
        Calculate complexity score (0.0-1.0).
        
        Used for edge case tie-breaking.
        """
        score = 0.0
        
        # Factual queries are simple
        if is_factual and not requires_explanation:
            return 0.1
        
        # Single concept is moderate
        if is_single_concept:
            score += 0.3
        
        # Explanation adds complexity
        if requires_explanation:
            score += 0.2
        
        # Multi-faceted is complex
        if is_multi_faceted:
            score += 0.5  # Increased from 0.4
        
        # Complex keywords
        for indicator in self.COMPLEX_INDICATORS:
            if indicator in request_lower:
                score += 0.2  # Increased from 0.1
                break
        
        return min(score, 1.0)
    
    def get_analysis(
        self,
        request: str,
        context: Optional[Dict] = None
    ) -> Tuple[ResponseTier, RequestAnalysis]:
        """
        Get full analysis with selected tier.
        
        Useful for debugging and logging.
        
        Args:
            request: User's request
            context: Optional context dict
        
        Returns:
            Tuple of (selected_tier, analysis)
        """
        context = context or {}
        analysis = self._analyze_request(request, context)
        tier = self.select_tier(request, context)
        return tier, analysis
