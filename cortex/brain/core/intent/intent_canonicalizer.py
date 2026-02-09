# AC-ID: IR-002-01 - Intent Canonicalizer
"""
Intent Understanding & Canonicalization.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-002-01 - Intent Understanding & Canonicalization

Transforms raw user requests into canonicalized, unambiguous intents.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from cortex.models.canonical_enums import IntentType


# =============================================================================
# ENUMS
# =============================================================================




# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class IntentScope:
    """Target scope for an intent."""
    file_path: Optional[str] = None
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    ac_id: Optional[str] = None
    module_name: Optional[str] = None
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "function_name": self.function_name,
            "class_name": self.class_name,
            "ac_id": self.ac_id,
            "module_name": self.module_name,
            "description": self.description,
        }


@dataclass
class CanonicalizedIntent:
    """A canonicalized intent extracted from user request."""
    original_text: str
    intent_type: str
    scope: IntentScope
    confidence: float
    keywords: List[str]
    needs_clarification: bool = False
    clarification_prompt: Optional[str] = None
    alternative_intents: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original_text": self.original_text,
            "intent_type": self.intent_type,
            "scope": self.scope.to_dict(),
            "confidence": self.confidence,
            "keywords": self.keywords,
            "needs_clarification": self.needs_clarification,
            "clarification_prompt": self.clarification_prompt,
            "alternative_intents": self.alternative_intents,
        }


# =============================================================================
# INTENT PATTERNS
# =============================================================================


# Pattern weights: (pattern, weight) - higher weight = stronger signal
INTENT_PATTERNS: Dict[str, List[tuple]] = {
    "IMPLEMENT": [
        (r"\bimplement\b", 1.0),
        (r"\badd\b", 0.8),
        (r"\bcreate\b", 0.9),
        (r"\bbuild\b", 0.8),
        (r"\bnew\b", 0.6),
        (r"\bwrite\b", 0.7),
        (r"\bdevelop\b", 0.8),
        (r"\bintroduce\b", 0.7),
        (r"\bset up\b", 0.7),
        (r"\bestablish\b", 0.6),
    ],
    "FIX": [
        (r"\bfix\b", 1.0),
        (r"\bresolve\b", 0.9),
        (r"\bbug\b", 0.8),
        (r"\berror\b", 0.8),
        (r"\bissue\b", 0.7),
        (r"\bfailing\b", 0.8),
        (r"\bbroken\b", 0.8),
        (r"\bcorrect\b", 0.7),
        (r"\brepair\b", 0.8),
        (r"\bhandle\b.*\berror\b", 0.7),
    ],
    "REFACTOR": [
        (r"\brefactor\b", 1.0),
        (r"\bclean\s*up\b", 0.9),
        (r"\bimprove\b", 0.7),
        (r"\brestructure\b", 0.9),
        (r"\breorganize\b", 0.8),
        (r"\bsimplify\b", 0.7),
        (r"\boptimize\b", 0.7),
        (r"\bstreamline\b", 0.7),
        (r"\bmodernize\b", 0.7),
        (r"\bcode\s+structure\b", 0.6),
    ],
    "QUERY": [
        (r"\bwhat\b", 0.8),
        (r"\bhow\b", 0.8),
        (r"\bexplain\b", 1.0),
        (r"\bdescribe\b", 0.9),
        (r"\bshow\b", 0.7),
        (r"\blist\b", 0.6),
        (r"\bwhere\b", 0.7),
        (r"\bwhy\b", 0.8),
        (r"\btell me\b", 0.8),
        (r"\bdoes\b.*\bwork\b", 0.6),
    ],
    "ANALYZE": [
        (r"\banalyze\b", 1.0),
        (r"\binvestigate\b", 0.9),
        (r"\bdebug\b", 0.9),
        (r"\bprofile\b", 0.8),
        (r"\bexamine\b", 0.8),
        (r"\bdiagnose\b", 0.9),
        (r"\bperformance\b", 0.6),
        (r"\bmemory\s+leak\b", 0.8),
        (r"\bbottleneck\b", 0.7),
        (r"\btrace\b", 0.7),
    ],
    "VALIDATE": [
        (r"\bvalidate\b", 1.0),
        (r"\bverify\b", 0.9),
        (r"\bcheck\b", 0.7),
        (r"\btest\b", 0.6),
        (r"\bconfirm\b", 0.7),
        (r"\bensure\b", 0.6),
        (r"\bpass\b", 0.5),
        (r"\bAC-ID\b", 0.7),
        (r"\bagainst\b", 0.4),
    ],
    "MIGRATE": [
        (r"\bmigrate\b", 1.0),
        (r"\bconvert\b", 0.8),
        (r"\btransform\b", 0.7),
        (r"\bupgrade\b", 0.8),
        (r"\bmove\b", 0.6),
        (r"\bport\b", 0.8),
        (r"\btransition\b", 0.7),
    ],
}


# Scope extraction patterns
SCOPE_PATTERNS = {
    "file": r"\b(?Union[in, from]|file)\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.py)?)\b",
    "function": r"\b(?Union[function, func]|method|def)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b",
    "function_in_file": r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s+(?Union[function, method])?\s*(?Union[in, from])\s+([a-zA-Z_][a-zA-Z0-9_]*\.py)\b",
    "class": r"\b(?Union[class, Class])\s+([A-Z][a-zA-Z0-9_]*)\b",
    "ac_id": r"\bAC-ID\s*([A-Z]{2,3}-\d{3}-\d{2})\b",
    "py_file": r"\b([a-zA-Z_][a-zA-Z0-9_]*\.py)\b",
    "class_mention": r"\b([A-Z][a-zA-Z0-9_]*(?Union[Model, Service]|Controller|Handler|Manager|Builder|Factory|Repository))\b",
}


# =============================================================================
# INTENT CANONICALIZER
# =============================================================================


class IntentCanonicalizer:
    """Transform user requests into canonicalized intents."""
    
    CONFIDENCE_THRESHOLD = 0.7
    
    def __init__(self):
        """Initialize the intent canonicalizer."""
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for efficiency."""
        self._intent_patterns: Dict[str, List[tuple]] = {}
        for intent_type, patterns in INTENT_PATTERNS.items():
            self._intent_patterns[intent_type] = [
                (re.compile(p, re.IGNORECASE), w) for p, w in patterns
            ]
        
        self._scope_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in SCOPE_PATTERNS.items()
        }
    
    def canonicalize(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> CanonicalizedIntent:
        """Canonicalize a user request into a structured intent.
        
        Args:
            text: Raw user request text.
            context: Optional context (current file, project info, etc.)
            
        Returns:
            CanonicalizedIntent with extracted information.
        """
        if not text or not text.strip():
            return self._create_unknown_intent(text)
        
        text_lower = text.lower()
        
        # Extract keywords
        keywords = self._extract_keywords(text)
        
        # Score each intent type
        intent_scores = self._score_intents(text_lower)
        
        # Get best intent and confidence
        best_intent, confidence = self._select_best_intent(intent_scores)
        
        # Adjust confidence based on context
        if context:
            confidence = self._adjust_confidence_with_context(
                confidence, best_intent, context
            )
        
        # Extract scope
        scope = self._extract_scope(text)
        
        # Determine if clarification needed
        needs_clarification = confidence < self.CONFIDENCE_THRESHOLD
        clarification_prompt = None
        
        if needs_clarification:
            clarification_prompt = self._generate_clarification(
                text, intent_scores, scope
            )
        
        # Get alternative intents
        alternatives = self._get_alternative_intents(intent_scores, best_intent)
        
        return CanonicalizedIntent(
            original_text=text,
            intent_type=best_intent,
            scope=scope,
            confidence=confidence,
            keywords=keywords,
            needs_clarification=needs_clarification,
            clarification_prompt=clarification_prompt,
            alternative_intents=alternatives,
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text.
        
        Args:
            text: Input text.
            
        Returns:
            List of keywords.
        """
        # Remove common stop words and extract meaningful terms
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "dare", "ought", "used", "to", "of", "in",
            "for", "on", "with", "at", "by", "from", "as", "into",
            "through", "during", "before", "after", "above", "below",
            "between", "under", "again", "further", "then", "once",
            "please", "it", "this", "that", "these", "those", "i", "me",
            "my", "we", "our", "you", "your",
        }
        
        # Tokenize
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', text.lower())
        
        # Filter and dedupe
        keywords = []
        seen: Set[str] = set()
        for word in words:
            if word not in stop_words and word not in seen and len(word) > 2:
                keywords.append(word)
                seen.add(word)
        
        return keywords[:10]  # Limit to top 10
    
    def _score_intents(self, text: str) -> Dict[str, float]:
        """Score text against all intent patterns.
        
        Args:
            text: Lowercased input text.
            
        Returns:
            Dict of intent type to score.
        """
        scores: Dict[str, float] = {}
        
        for intent_type, patterns in self._intent_patterns.items():
            total_score = 0.0
            max_score = 0.0
            
            for pattern, weight in patterns:
                if pattern.search(text):
                    total_score += weight
                    max_score = max(max_score, weight)
            
            # Use a combination of max and total for final score
            scores[intent_type] = min(1.0, max_score * 0.6 + total_score * 0.1)
        
        return scores
    
    def _select_best_intent(
        self, scores: Dict[str, float]
    ) -> tuple:
        """Select best intent based on scores.
        
        Args:
            scores: Intent scores.
            
        Returns:
            Tuple of (best_intent, confidence).
        """
        if not scores:
            return "UNKNOWN", 0.0
        
        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]
        
        # If no pattern matched at all
        if best_score == 0:
            return "UNKNOWN", 0.1
        
        return best_intent, best_score
    
    def _adjust_confidence_with_context(
        self, confidence: float, intent: str, context: Dict[str, Any]
    ) -> float:
        """Adjust confidence based on context.
        
        Args:
            confidence: Base confidence score.
            intent: Detected intent type.
            context: Additional context.
            
        Returns:
            Adjusted confidence.
        """
        adjustment = 0.0
        
        # If we have a current file, boost confidence slightly
        if context.get("current_file"):
            adjustment += 0.1
        
        # If project type is known, boost confidence
        if context.get("project_type"):
            adjustment += 0.05
        
        # If recent changes relate to the request
        if context.get("recent_changes"):
            adjustment += 0.05
        
        return min(1.0, confidence + adjustment)
    
    def _extract_scope(self, text: str) -> IntentScope:
        """Extract target scope from text.
        
        Args:
            text: Input text.
            
        Returns:
            IntentScope with extracted targets.
        """
        scope = IntentScope()
        
        # Check for AC-ID first (highest priority)
        ac_match = self._scope_patterns["ac_id"].search(text)
        if ac_match:
            scope.ac_id = ac_match.group(1)
        
        # Check for function in file pattern
        func_file_match = self._scope_patterns["function_in_file"].search(text)
        if func_file_match:
            scope.function_name = func_file_match.group(1)
            scope.file_path = func_file_match.group(2)
        else:
            # Check for standalone file
            file_match = self._scope_patterns["py_file"].search(text)
            if file_match:
                scope.file_path = file_match.group(1)
            
            # Check for function
            func_match = self._scope_patterns["function"].search(text)
            if func_match:
                scope.function_name = func_match.group(1)
        
        # Check for class
        class_match = self._scope_patterns["class"].search(text)
        if class_match:
            scope.class_name = class_match.group(1)
        else:
            # Check for class-like names
            class_like = self._scope_patterns["class_mention"].search(text)
            if class_like:
                scope.class_name = class_like.group(1)
        
        return scope
    
    def _generate_clarification(
        self, text: str, scores: Dict[str, float], scope: IntentScope
    ) -> str:
        """Generate clarification prompt for ambiguous request.
        
        Args:
            text: Original text.
            scores: Intent scores.
            scope: Extracted scope.
            
        Returns:
            Clarification prompt string.
        """
        # Get top 3 intents
        top_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        prompt_parts = ["I'd like to clarify your request."]
        
        if top_intents[0][1] > 0:
            options = [f"- **{i[0]}**: {self._intent_description(i[0])}" 
                       for i in top_intents if i[1] > 0]
            if options:
                prompt_parts.append("\nDid you mean to:")
                prompt_parts.extend(options)
        else:
            prompt_parts.append(
                "\nPlease specify what you'd like to do:\n"
                "- **IMPLEMENT**: Create new functionality\n"
                "- **FIX**: Resolve a bug or error\n"
                "- **REFACTOR**: Improve code structure\n"
                "- **EXPLAIN**: Get information about the code"
            )
        
        # Ask about scope if missing
        if not any([scope.file_path, scope.function_name, scope.class_name, scope.ac_id]):
            prompt_parts.append("\nAlso, please specify the target (file, function, or AC-ID).")
        
        return "\n".join(prompt_parts)
    
    def _intent_description(self, intent: str) -> str:
        """Get human-readable description for intent type.
        
        Args:
            intent: Intent type.
            
        Returns:
            Description string.
        """
        descriptions = {
            "IMPLEMENT": "Create new functionality",
            "FIX": "Resolve a bug or error",
            "REFACTOR": "Improve code without changing behavior",
            "QUERY": "Get information about the code",
            "ANALYZE": "Investigate or debug an issue",
            "VALIDATE": "Verify correctness or compliance",
            "MIGRATE": "Transform or upgrade code",
            "UNKNOWN": "Unknown action",
        }
        return descriptions.get(intent, "Perform an action")
    
    def _get_alternative_intents(
        self, scores: Dict[str, float], best_intent: str
    ) -> List[Dict[str, Any]]:
        """Get alternative intent interpretations.
        
        Args:
            scores: Intent scores.
            best_intent: The selected best intent.
            
        Returns:
            List of alternative intent dicts.
        """
        alternatives = []
        for intent, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            if intent != best_intent and score > 0.3:
                alternatives.append({
                    "intent_type": intent,
                    "confidence": score,
                    "description": self._intent_description(intent),
                })
        return alternatives[:3]  # Top 3 alternatives
    
    def _create_unknown_intent(self, text: str) -> CanonicalizedIntent:
        """Create an unknown intent for empty/invalid input.
        
        Args:
            text: Original text.
            
        Returns:
            CanonicalizedIntent with UNKNOWN type.
        """
        return CanonicalizedIntent(
            original_text=text,
            intent_type="UNKNOWN",
            scope=IntentScope(),
            confidence=0.0,
            keywords=[],
            needs_clarification=True,
            clarification_prompt="Please provide a request describing what you'd like me to do.",
        )


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "IntentCanonicalizer",
    "CanonicalizedIntent",
    "IntentScope",
    "IntentType",
]
