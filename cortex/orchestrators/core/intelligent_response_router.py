# AC_START: AC-WAVE-4-S1-002
"""
Intelligent Response Router - ENH-087 Track 2.

Provides intelligent response routing based on context analysis,
pattern matching, and template selection optimization.

Module: cortex/orchestrators/routing/intelligent_response_router.py
Authority: WAVE-4 Stage 1 - ENH-087 Track 2
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


@dataclass
class RoutingContext:
    """Context for intelligent routing decisions.
    
    Attributes:
        intent_type: Type of intent (IMPLEMENT, FIX, REFACTOR, etc.)
        user_query: Original user query
        domain: Target domain (authentication, security, etc.)
        complexity: Complexity score (1-10)
        user_preferences: User preferences for response formatting
    """
    intent_type: str
    user_query: str
    domain: str
    complexity: int
    user_preferences: Dict[str, Any]


@dataclass
class ContextAnalysisResult:
    """Result of context analysis.
    
    Attributes:
        context_type: Type classification (simple, moderate, complex)
        confidence: Confidence score (0.0-1.0)
        key_factors: List of key factors identified
        metadata: Additional metadata
        warnings: List of warnings
    """
    context_type: str
    confidence: float
    key_factors: List[str]
    metadata: Dict[str, Any]
    warnings: List[str]


@dataclass
class PatternMatchResult:
    """Result of pattern matching.
    
    Attributes:
        matched_patterns: List of matched pattern identifiers
        best_match: Best matching pattern (if any)
        confidence: Confidence score (0.0-1.0)
        metadata: Additional metadata including pattern scores
        warnings: List of warnings
    """
    matched_patterns: List[str]
    best_match: Optional[str]
    confidence: float
    metadata: Dict[str, Any]
    warnings: List[str]


@dataclass
class TemplateSelectionResult:
    """Result of template selection.
    
    Attributes:
        template_id: Selected template identifier
        complexity_level: Complexity level (simple, moderate, complex, detailed)
        template_attributes: Template attributes/tags
        optimization_applied: Whether optimization was applied
        is_fallback: Whether this is a fallback template
        confidence: Confidence score (0.0-1.0)
        metadata: Additional metadata
    """
    template_id: str
    complexity_level: str
    template_attributes: List[str]
    optimization_applied: bool
    is_fallback: bool
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntelligentResponseRouter:
    """Intelligent response router with context analysis and pattern matching.
    
    Provides three-stage routing pipeline:
    1. Context Analysis: Analyzes query context and complexity
    2. Pattern Matching: Matches patterns based on context
    3. Template Selection: Selects optimal response template
    
    Features:
        - Context-aware routing
        - Pattern similarity matching
        - Template optimization
        - Caching for performance
        - User preference integration
    
    Example:
        >>> router = IntelligentResponseRouter()
        >>> context = RoutingContext(
        ...     intent_type="IMPLEMENT",
        ...     user_query="implement login feature",
        ...     domain="authentication",
        ...     complexity=3,
        ...     user_preferences={}
        ... )
        >>> result = router.analyze_context(context)
        >>> pattern = router.match_patterns(result)
        >>> template = router.select_template(pattern)
    """

    # Pattern definitions for matching
    PATTERNS = {
        "implement_feature": ["implement", "create", "add", "build"],
        "refactor_code": ["refactor", "improve", "restructure", "reorganize"],
        "fix_bug": ["fix", "resolve", "debug", "correct"],
        "analyze_code": ["analyze", "review", "inspect", "examine"],
        "refactor_architecture": ["architecture", "design", "pattern", "structure"],
        "implement_pattern": ["pattern", "strategy", "factory", "observer"],
        "implement_api": ["api", "endpoint", "route", "controller"],
        "quick_fix": ["quick", "simple", "small", "minor"],
        "security_audit": ["security", "audit", "vulnerability", "threat"],
    }

    # Template definitions
    TEMPLATES = {
        "simple_implementation": {
            "complexity": "simple",
            "attributes": ["concise", "direct"],
            "patterns": ["implement_feature", "quick_fix"],
        },
        "detailed_refactor": {
            "complexity": "complex",
            "attributes": ["verbose", "detailed", "comprehensive"],
            "patterns": ["refactor_architecture", "implement_pattern"],
        },
        "analysis_report": {
            "complexity": "moderate",
            "attributes": ["structured", "analytical"],
            "patterns": ["analyze_code"],
        },
        "security_assessment": {
            "complexity": "complex",
            "attributes": ["thorough", "security-focused"],
            "patterns": ["security_audit"],
        },
        "api_documentation": {
            "complexity": "moderate",
            "attributes": ["structured", "technical"],
            "patterns": ["implement_api"],
        },
    }

    def __init__(self) -> None:
        """Initialize IntelligentResponseRouter."""
        self._template_cache: Dict[str, TemplateSelectionResult] = {}
        logger.info("IntelligentResponseRouter initialized")

    def analyze_context(self, context: RoutingContext) -> ContextAnalysisResult:
        """Analyze routing context and determine context type.
        
        Examines the routing context to determine:
        - Context type (simple, moderate, complex)
        - Key factors affecting routing
        - Confidence in the analysis
        - Any warnings or misalignments
        
        Args:
            context: RoutingContext with intent, query, domain, etc.
        
        Returns:
            ContextAnalysisResult with analysis findings
        """
        warnings = []
        key_factors = []
        
        # Analyze query length and content
        query_lower = context.user_query.lower()
        query_words = query_lower.split()
        
        # Extract key factors from query
        for word in query_words:
            if word in ["implement", "refactor", "fix", "analyze", "security", "api"]:
                key_factors.append(word)
        
        # Determine context type based on complexity
        if context.complexity <= 3:
            context_type = "simple"
            base_confidence = 0.92
        elif context.complexity <= 6:
            context_type = "moderate"
            base_confidence = 0.87
        else:
            context_type = "complex"
            base_confidence = 0.88  # Slightly higher for complex contexts
            warnings.append("high_complexity")
        
        # Check for intent-query alignment
        intent_keywords = {
            "IMPLEMENT": ["implement", "create", "add", "build"],
            "FIX": ["fix", "resolve", "debug", "correct"],
            "REFACTOR": ["refactor", "improve", "restructure"],
            "ANALYZE": ["analyze", "review", "inspect", "examine"],
        }
        
        expected_keywords = intent_keywords.get(context.intent_type, [])
        if expected_keywords and not any(kw in query_lower for kw in expected_keywords):
            warnings.append("intent_mismatch")
            base_confidence *= 0.9
        
        # Add domain to key factors if meaningful
        if context.domain and context.domain != "unknown":
            key_factors.append(context.domain)
        
        # Handle empty query
        if not context.user_query.strip():
            base_confidence = 0.4
            context_type = "simple"
        
        # Build confidence factors
        confidence_factors = {
            "query_clarity": 0.97 if len(query_words) >= 3 else 0.6,
            "domain_specificity": 0.95 if context.domain != "unknown" else 0.5,
            "complexity_reasonable": 0.97 if context.complexity <= 7 else 0.92,
        }
        
        metadata = {
            "confidence_factors": confidence_factors,
            "query_word_count": len(query_words),
        }
        
        # Include user preferences if provided
        if context.user_preferences:
            metadata["user_preferences"] = context.user_preferences
        
        # Calculate final confidence
        confidence = base_confidence * sum(confidence_factors.values()) / len(confidence_factors)
        
        return ContextAnalysisResult(
            context_type=context_type,
            confidence=min(confidence, 1.0),
            key_factors=key_factors,
            metadata=metadata,
            warnings=warnings,
        )

    def match_patterns(self, context_result: ContextAnalysisResult) -> PatternMatchResult:
        """Match patterns based on context analysis.
        
        Uses similarity matching to find patterns that match the
        analyzed context. Ranks patterns by confidence.
        
        Args:
            context_result: Result from analyze_context
        
        Returns:
            PatternMatchResult with matched patterns
        """
        matched_patterns = []
        pattern_scores: Dict[str, float] = {}
        
        # Get key factors from context
        key_factors = context_result.key_factors
        
        if not key_factors:
            # No patterns can be matched
            return PatternMatchResult(
                matched_patterns=[],
                best_match=None,
                confidence=0.4,
                metadata={"fallback_patterns": ["general_response"]},
                warnings=[],
            )
        
        # Match patterns using similarity
        for pattern_name, pattern_keywords in self.PATTERNS.items():
            score = 0.0
            for key_factor in key_factors:
                for keyword in pattern_keywords:
                    # Use SequenceMatcher for fuzzy matching
                    similarity = SequenceMatcher(None, key_factor, keyword).ratio()
                    if similarity > 0.7:  # Threshold for match
                        score += similarity
            
            if score > 0:
                pattern_scores[pattern_name] = score
                matched_patterns.append(pattern_name)
        
        # Sort patterns by score
        sorted_patterns = sorted(
            matched_patterns, key=lambda p: pattern_scores.get(p, 0), reverse=True
        )
        
        # Determine best match
        best_match = sorted_patterns[0] if sorted_patterns else None
        
        # Calculate confidence based on top score
        if pattern_scores:
            max_score = max(pattern_scores.values())
            # Normalize scores - ensure they're in 0-1 range first
            normalized_scores = {k: min(v / 1.5, 1.0) for k, v in pattern_scores.items()}
            pattern_scores = normalized_scores
            # Use normalized max for confidence with boost
            confidence = min(max(normalized_scores.values()) * 1.3, 1.0)
        else:
            confidence = 0.4
        
        # Build metadata
        metadata = {
            "pattern_scores": pattern_scores,
            "pattern_metadata": {
                "total_patterns": len(self.PATTERNS),
                "matched_count": len(matched_patterns),
            },
            "context_type": context_result.context_type,  # Propagate context type
        }
        
        # Add fallback patterns if needed
        if not matched_patterns:
            metadata["fallback_patterns"] = ["general_response"]
        
        # Propagate context metadata if present
        if "user_preferences" in context_result.metadata:
            metadata["user_preferences"] = context_result.metadata["user_preferences"]
        
        # Check for domain-specific patterns
        domain = context_result.metadata.get("domain")
        if domain:
            metadata["domain"] = domain
        
        return PatternMatchResult(
            matched_patterns=sorted_patterns,
            best_match=best_match,
            confidence=confidence,
            metadata=metadata,
            warnings=[],
        )

    def select_template(self, pattern_result: PatternMatchResult) -> TemplateSelectionResult:
        """Select optimal response template.
        
        Selects template based on matched patterns, complexity,
        and user preferences. Applies caching for performance.
        
        Args:
            pattern_result: Result from match_patterns
        
        Returns:
            TemplateSelectionResult with selected template
        """
        # Check cache first
        cache_key = f"{pattern_result.best_match}_{pattern_result.confidence}"
        if cache_key in self._template_cache:
            cached_result = self._template_cache[cache_key]
            cached_result.metadata["cache_hit"] = True
            return cached_result
        
        # Determine template based on best match
        if not pattern_result.best_match:
            # Fallback template
            return self._fallback_template()
        
        # Find matching template
        selected_template_id = None
        complexity_level = "moderate"
        attributes = []
        
        for template_id, template_config in self.TEMPLATES.items():
            if pattern_result.best_match in template_config["patterns"]:
                selected_template_id = template_id
                complexity_level = template_config["complexity"]
                attributes = template_config["attributes"]
                break
        
        # Apply user preferences if present
        user_prefs = pattern_result.metadata.get("user_preferences", {})
        if user_prefs.get("format") == "concise" and "concise" not in attributes:
            attributes.append("concise")
        
        # Check context type from metadata
        context_type = pattern_result.metadata.get("context_type")
        if not context_type:
            # Infer from pattern confidence and pattern name
            if pattern_result.best_match and "architecture" in pattern_result.best_match.lower():
                context_type = "complex"
            elif pattern_result.confidence > 0.85:
                context_type = "simple"
            elif pattern_result.confidence > 0.7:
                context_type = "moderate"
            else:
                context_type = "complex"
        
        # Override complexity level based on context type if not explicitly set
        if context_type == "complex" and complexity_level != "complex":
            complexity_level = "complex"
        
        # Use fallback if no template selected
        if not selected_template_id:
            selected_template_id = "general_response"
            attributes = ["flexible"]
        
        # Apply optimization for quick fixes
        optimization_applied = "quick" in pattern_result.best_match.lower()
        
        result = TemplateSelectionResult(
            template_id=selected_template_id or "general_response",
            complexity_level=complexity_level,
            template_attributes=attributes,
            optimization_applied=optimization_applied,
            is_fallback=(selected_template_id is None),
            confidence=pattern_result.confidence,
            metadata={
                "performance": "optimized" if optimization_applied else "standard",
                "template_metadata": {
                    "selected_from": len(self.TEMPLATES),
                    "match_quality": pattern_result.confidence,
                },
            },
        )
        
        # Cache result
        self._template_cache[cache_key] = result
        
        return result

    def _fallback_template(self) -> TemplateSelectionResult:
        """Provide fallback template when no patterns match.
        
        Returns:
            TemplateSelectionResult with fallback template
        """
        return TemplateSelectionResult(
            template_id="general_fallback",
            complexity_level="moderate",
            template_attributes=["flexible", "general"],
            optimization_applied=False,
            is_fallback=True,
            confidence=0.5,
            metadata={"fallback_reason": "no_patterns_matched"},
        )


# AC_COMPLETE: AC-WAVE-4-S1-002 (Implementation complete - GREEN phase)
