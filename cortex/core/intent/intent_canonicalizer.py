"""Module: Canonicalizes intents to prevent misinterpretation

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import re
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


class IntentType(str, Enum):
    """Standard intent types."""
    IMPLEMENT = "IMPLEMENT"
    FIX = "FIX"
    REFACTOR = "REFACTOR"
    QUERY = "QUERY"
    ANALYZE = "ANALYZE"
    VALIDATE = "VALIDATE"
    MIGRATE = "MIGRATE"
    UNKNOWN = "UNKNOWN"


@dataclass
class Scope:
    """Scope information for an intent."""
    file_path: Optional[str] = None
    class_name: Optional[str] = None
    function_name: Optional[str] = None
    ac_id: Optional[str] = None
    module_path: Optional[str] = None


@dataclass
class CanonicalIntent:
    """CanonicalIntent - Represents a canonicalized intent with structured information."""
    
    intent_type: str
    scope: Scope
    confidence: float
    keywords: List[str]
    needs_clarification: bool = False
    clarification_prompt: Optional[str] = None
    original_text: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            dict: Dictionary with all intent fields
        """
        return {
            "intent_type": self.intent_type,
            "scope": {
                "file_path": self.scope.file_path,
                "class_name": self.scope.class_name,
                "function_name": self.scope.function_name,
                "ac_id": self.scope.ac_id,
                "module_path": self.scope.module_path,
            },
            "confidence": self.confidence,
            "keywords": self.keywords,
            "needs_clarification": self.needs_clarification,
            "clarification_prompt": self.clarification_prompt,
            "original_text": self.original_text,
        }


class IntentCanonicalizer:
    """IntentCanonicalizer - Canonicalizes intents to prevent misinterpretation.
    
    This class analyzes natural language requests and extracts structured intent
    information including intent type, target scope, keywords, and confidence scores.
    """

    # Intent detection patterns
    INTENT_PATTERNS = {
        IntentType.IMPLEMENT: [
            r'\b(implement|create|add|build|develop|write)\b',
            r'\b(new\s+\w+|feature)\b',
        ],
        IntentType.FIX: [
            r'\b(fix|resolve|repair|correct|debug)\b',
            r'\b(bug|error|issue|problem|failure)\b',
        ],
        IntentType.REFACTOR: [
            r'\b(refactor|clean\s*up|improve|restructure|reorganize)\b',
            r'\b(simplify|optimize|better\s+structure)\b',
        ],
        IntentType.QUERY: [
            r'\b(what|how|why|when|where|who)\b',
            r'\b(explain|describe|tell\s+me|show\s+me)\b',
        ],
        IntentType.ANALYZE: [
            r'\b(analyze|investigate|examine|study|review)\b',
            r'\b(debug|profile|trace|inspect)\b',
            r'\b(performance|memory\s+leak)\b',
        ],
        IntentType.VALIDATE: [
            r'\b(validate|verify|check|test|confirm)\b',
            r'\b(against\s+AC|passes?|correct)\b',
        ],
        IntentType.MIGRATE: [
            r'\b(migrate|move|transfer|convert|upgrade)\b',
            r'\b(from\s+\w+\s+to\s+\w+)\b',
        ],
    }
    
    # Scope extraction patterns
    SCOPE_PATTERNS = {
        'file': r'(?:in|from|at)\s+([a-zA-Z0-9_/\-]+\.py)',
        'class': r'(?:the\s+)?([A-Z][a-zA-Z0-9_]+)\s+class',
        'function': r'(?:the\s+)?([a-z_][a-z0-9_]*)\s+function',
        'ac_id': r'AC[-_]?ID\s+([A-Z]{2,3}-\d{3}-\d{2})',
    }

    def __init__(self):
        """Initialize IntentCanonicalizer."""
        pass

    def canonicalize(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> CanonicalIntent:
        """Canonicalize a natural language intent into structured form.
        
        Args:
            text: Natural language intent text
            context: Optional context dictionary with project information
            
        Returns:
            CanonicalIntent: Structured intent with type, scope, and metadata
        """
        if not text or not text.strip():
            return self._create_unknown_intent(text, "Empty request")
        
        text_lower = text.lower()
        
        # Extract intent type
        intent_type = self._detect_intent_type(text_lower)
        
        # Extract scope
        scope = self._extract_scope(text, context)
        
        # Extract keywords
        keywords = self._extract_keywords(text_lower)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            text_lower,
            intent_type,
            scope,
            keywords,
            context
        )
        
        # Determine if clarification is needed
        needs_clarification = confidence < 0.7
        clarification_prompt = None
        if needs_clarification:
            clarification_prompt = self._generate_clarification(
                text,
                intent_type,
                scope
            )
        
        return CanonicalIntent(
            intent_type=intent_type.value if isinstance(intent_type, IntentType) else intent_type,
            scope=scope,
            confidence=confidence,
            keywords=keywords,
            needs_clarification=needs_clarification,
            clarification_prompt=clarification_prompt,
            original_text=text,
        )

    def _detect_intent_type(self, text_lower: str) -> IntentType:
        """Detect intent type from text.
        
        Args:
            text_lower: Lowercase text to analyze
            
        Returns:
            IntentType: Detected intent type
        """
        scores = {intent: 0.0 for intent in IntentType}
        
        # Check for ANALYZE indicators first (higher priority for investigation terms)
        if re.search(r'\b(analyze|investigate|examine|study|review|profile|trace|inspect)\b', text_lower):
            scores[IntentType.ANALYZE] += 2.0
        if re.search(r'\b(performance|memory\s+leak|bottleneck)\b', text_lower):
            scores[IntentType.ANALYZE] += 1.5
        
        # Debug can be ANALYZE or FIX depending on context
        if re.search(r'\bdebug\b', text_lower):
            # If followed by "the X flow" or similar, it's likely ANALYZE
            if re.search(r'debug\s+the\s+\w+\s+(flow|process|behavior|logic)', text_lower):
                scores[IntentType.ANALYZE] += 2.0
            else:
                scores[IntentType.FIX] += 1.0
        
        # Check other patterns
        for intent_type, patterns in self.INTENT_PATTERNS.items():
            # Skip ANALYZE since we handled it above
            if intent_type == IntentType.ANALYZE:
                continue
                
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    scores[intent_type] += 1.0
        
        # Find highest scoring intent
        max_score = max(scores.values())
        if max_score == 0:
            return IntentType.UNKNOWN
        
        # Get intent with highest score
        for intent, score in scores.items():
            if score == max_score:
                return intent
        
        return IntentType.UNKNOWN

    def _extract_scope(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Scope:
        """Extract scope information from text.
        
        Args:
            text: Text to analyze
            context: Optional context for scope extraction
            
        Returns:
            Scope: Extracted scope information
        """
        scope = Scope()
        
        # Extract file path
        file_match = re.search(self.SCOPE_PATTERNS['file'], text)
        if file_match:
            scope.file_path = file_match.group(1)
        elif context and 'current_file' in context:
            scope.file_path = context['current_file']
        
        # Extract class name
        class_match = re.search(self.SCOPE_PATTERNS['class'], text)
        if class_match:
            scope.class_name = class_match.group(1)
        
        # Extract function name
        func_match = re.search(self.SCOPE_PATTERNS['function'], text)
        if func_match:
            scope.function_name = func_match.group(1)
        
        # Extract AC-ID
        ac_match = re.search(self.SCOPE_PATTERNS['ac_id'], text)
        if ac_match:
            scope.ac_id = ac_match.group(1)
        
        return scope

    def _extract_keywords(self, text_lower: str) -> List[str]:
        """Extract relevant keywords from text.
        
        Args:
            text_lower: Lowercase text to analyze
            
        Returns:
            list: Extracted keywords
        """
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and',
            'or', 'but', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'it', 'its', 'they', 'them', 'their',
        }
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b[a-z][a-z0-9_]*\b', text_lower)
        
        # Filter stop words and short words
        keywords = [
            w for w in words
            if w not in stop_words and len(w) > 2
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
        
        return unique_keywords

    def _calculate_confidence(
        self,
        text_lower: str,
        intent_type: IntentType,
        scope: Scope,
        keywords: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate confidence score for the canonicalization.
        
        Args:
            text_lower: Lowercase text
            intent_type: Detected intent type
            scope: Extracted scope
            keywords: Extracted keywords
            context: Optional context
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        confidence = 0.5  # Base confidence
        
        # Boost if intent is not UNKNOWN
        if intent_type != IntentType.UNKNOWN:
            confidence += 0.2
        
        # Boost if we have scope information
        scope_count = sum([
            scope.file_path is not None,
            scope.class_name is not None,
            scope.function_name is not None,
            scope.ac_id is not None,
        ])
        confidence += scope_count * 0.1
        
        # Boost if we have keywords
        if len(keywords) >= 2:
            confidence += 0.1
        
        # Boost if text is detailed (longer)
        if len(text_lower.split()) > 5:
            confidence += 0.05
        
        # Boost if context provided
        if context:
            confidence += 0.05
        
        # Penalize very short or vague requests
        if len(text_lower.split()) <= 2:
            confidence -= 0.2
        
        # Ensure in range [0.0, 1.0]
        return max(0.0, min(1.0, confidence))

    def _generate_clarification(
        self,
        text: str,
        intent_type: IntentType,
        scope: Scope
    ) -> str:
        """Generate clarification prompt for ambiguous requests.
        
        Args:
            text: Original text
            intent_type: Detected intent type
            scope: Extracted scope
            
        Returns:
            str: Clarification prompt
        """
        if intent_type == IntentType.UNKNOWN:
            return (
                f"I'm not sure what you want to do with '{text}'. "
                "Could you clarify if you want to implement, fix, refactor, "
                "or explain something?"
            )
        
        if not any([scope.file_path, scope.class_name, scope.function_name, scope.ac_id]):
            return (
                f"I understand you want to {intent_type.value.lower()}, but could you "
                "specify which file, class, or function you're referring to?"
            )
        
        return (
            f"Could you provide more details about what you want to "
            f"{intent_type.value.lower()}?"
        )

    def _create_unknown_intent(self, text: str, reason: str) -> CanonicalIntent:
        """Create an unknown intent result.
        
        Args:
            text: Original text
            reason: Reason for unknown classification
            
        Returns:
            CanonicalIntent: Intent marked as unknown
        """
        return CanonicalIntent(
            intent_type=IntentType.UNKNOWN.value,
            scope=Scope(),
            confidence=0.0,
            keywords=[],
            needs_clarification=True,
            clarification_prompt=f"Unable to understand request: {reason}",
            original_text=text,
        )


__all__ = [
    "IntentCanonicalizer",
    "CanonicalIntent",
    "IntentType",
    "Scope",
]