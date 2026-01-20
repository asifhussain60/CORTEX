"""Intent Classifier - Multi-label intent classification with confidence scoring.

Classifies user intents from natural language text using keyword matching,
signal detection, and confidence scoring.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
import re
from datetime import datetime


class IntentCategory(str, Enum):
    """Intent categories for development operations."""
    CREATE = "create"
    FIX = "fix"
    ANALYZE = "analyze"
    OPTIMIZE = "optimize"
    REFACTOR = "refactor"
    TEST = "test"
    DOCUMENT = "document"
    MODIFY = "modify"
    QUERY = "query"
    COMMAND = "command"
    NAVIGATION = "navigation"


class IntentSignal(str, Enum):
    """Linguistic signals indicating intent."""
    IMPERATIVE = "imperative"
    PROBLEM_STATEMENT = "problem_statement"
    FEATURE_REQUEST = "feature_request"
    IMPROVEMENT_REQUEST = "improvement_request"
    INTERROGATIVE = "interrogative"


@dataclass
class ClassificationResult:
    """Result of intent classification."""
    primary_intent: IntentCategory
    confidence_score: float
    secondary_intents: List[tuple[IntentCategory, float]] = field(default_factory=list)
    detected_signals: List[IntentSignal] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    reasoning: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class IntentClassifier:
    """Classify user intents from natural language text.
    
    Uses keyword matching, signal detection, and confidence scoring to
    determine primary and secondary intents with multi-label support.
    
    Attributes:
        keyword_mappings: Dict mapping intents to keyword sets
        signal_patterns: Dict mapping signals to compiled regex patterns
        classification_cache: LRU cache of recent classifications
        metrics: Classification performance metrics
    """
    
    def __init__(self):
        """Initialize intent classifier."""
        self.keyword_mappings: Dict[IntentCategory, Set[str]] = self._build_keyword_mappings()
        self.signal_patterns: Dict[IntentSignal, re.Pattern] = self._compile_signal_patterns()
        self.classification_cache: Dict[str, ClassificationResult] = {}
        self.metrics: Dict[str, Any] = {
            "total_classifications": 0,
            "cache_hits": 0,
            "avg_confidence": 0.0,
            "confidence_sum": 0.0
        }
        self._cache_max_size = 1000
    
    def _build_keyword_mappings(self) -> Dict[IntentCategory, Set[str]]:
        """Build keyword mappings for each intent category."""
        return {
            IntentCategory.CREATE: {
                "create", "build", "add", "implement", "make", "generate",
                "develop", "establish", "construct", "new", "setup", "initialize"
            },
            IntentCategory.FIX: {
                "fix", "repair", "resolve", "correct", "debug", "patch",
                "address", "solve", "remedy", "bug", "issue", "error"
            },
            IntentCategory.ANALYZE: {
                "analyze", "examine", "investigate", "review", "inspect",
                "study", "evaluate", "assess", "check", "audit"
            },
            IntentCategory.OPTIMIZE: {
                "optimize", "improve", "enhance", "speed", "performance",
                "faster", "efficient", "reduce", "minimize", "streamline"
            },
            IntentCategory.REFACTOR: {
                "refactor", "restructure", "reorganize", "clean", "simplify",
                "modularize", "rewrite", "improve structure", "consolidate"
            },
            IntentCategory.TEST: {
                "test", "verify", "validate", "check", "ensure", "confirm",
                "assert", "coverage", "unit test", "integration test"
            },
            IntentCategory.DOCUMENT: {
                "document", "doc", "explain", "describe", "comment", "annotate",
                "readme", "guide", "manual", "documentation"
            },
            IntentCategory.MODIFY: {
                "modify", "change", "update", "alter", "adjust", "edit",
                "revise", "amend", "tweak", "customize"
            },
            IntentCategory.QUERY: {
                "what", "how", "why", "when", "where", "which", "who",
                "show", "tell", "explain", "is", "are", "can", "does"
            },
            IntentCategory.COMMAND: {
                "run", "execute", "start", "stop", "restart", "deploy",
                "install", "configure", "enable", "disable"
            },
            IntentCategory.NAVIGATION: {
                "go", "navigate", "open", "show", "display", "view",
                "switch", "move", "jump", "find"
            }
        }
    
    def _compile_signal_patterns(self) -> Dict[IntentSignal, re.Pattern]:
        """Compile regex patterns for signal detection."""
        return {
            IntentSignal.IMPERATIVE: re.compile(
                r'\b(create|build|fix|make|add|implement|remove|delete)\b',
                re.IGNORECASE
            ),
            IntentSignal.PROBLEM_STATEMENT: re.compile(
                r'\b(problem|issue|bug|error|broken|failing|not working)\b',
                re.IGNORECASE
            ),
            IntentSignal.FEATURE_REQUEST: re.compile(
                r'\b(need|want|should|would like|feature|capability|add)\b',
                re.IGNORECASE
            ),
            IntentSignal.IMPROVEMENT_REQUEST: re.compile(
                r'\b(improve|better|enhance|optimize|faster|more|less)\b',
                re.IGNORECASE
            ),
            IntentSignal.INTERROGATIVE: re.compile(
                r'\b(what|how|why|when|where|which|who|can|does)\b',
                re.IGNORECASE
            )
        }
    
    def classify(self, text: str) -> ClassificationResult:
        """Classify intent from text.
        
        Args:
            text: Input text to classify
            
        Returns:
            ClassificationResult with primary intent, confidence, and metadata
            
        Raises:
            ValueError: If text is None, empty, or non-string
        """
        # Validation
        if text is None:
            raise ValueError("Text cannot be None")
        if not isinstance(text, str):
            raise ValueError(f"Text must be string, got {type(text).__name__}")
        if text.strip() == "":
            raise ValueError("Text cannot be empty")
        
        # Check cache
        cache_key = text.lower().strip()
        if cache_key in self.classification_cache:
            self.metrics["cache_hits"] += 1
            return self.classification_cache[cache_key]
        
        # Normalize text
        normalized = text.lower().strip()
        
        # Score all intents
        intent_scores: Dict[IntentCategory, float] = {}
        for intent, keywords in self.keyword_mappings.items():
            score = sum(1.0 for keyword in keywords if keyword in normalized)
            if score > 0:
                intent_scores[intent] = score / len(keywords)  # Normalize
        
        # Detect signals
        detected_signals = []
        for signal, pattern in self.signal_patterns.items():
            if pattern.search(normalized):
                detected_signals.append(signal)
        
        # Determine primary intent
        if not intent_scores:
            primary = IntentCategory.QUERY
            confidence = 0.5
        else:
            sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
            primary = sorted_intents[0][0]
            confidence = min(sorted_intents[0][1] * 1.5, 1.0)  # Boost confidence
        
        # Extract keywords (up to 5)
        words = [w for w in normalized.split() if len(w) > 3][:5]
        
        # Build secondary intents
        secondary = [(intent, score) for intent, score in intent_scores.items()
                    if intent != primary and score > 0.1][:3]
        
        # Create result
        result = ClassificationResult(
            primary_intent=primary,
            confidence_score=confidence,
            secondary_intents=secondary,
            detected_signals=detected_signals,
            keywords=words,
            reasoning=f"Detected {len(intent_scores)} intent signals, confidence={confidence:.2f}"
        )
        
        # Update metrics
        self.metrics["total_classifications"] += 1
        self.metrics["confidence_sum"] += confidence
        self.metrics["avg_confidence"] = (
            self.metrics["confidence_sum"] / self.metrics["total_classifications"]
        )
        
        # Cache result
        if len(self.classification_cache) >= self._cache_max_size:
            # Simple LRU: remove oldest
            self.classification_cache.pop(next(iter(self.classification_cache)))
        self.classification_cache[cache_key] = result
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get classification metrics.
        
        Returns:
            Dictionary with performance metrics
        """
        return self.metrics.copy()
    
    def clear_cache(self) -> None:
        """Clear classification cache."""
        self.classification_cache.clear()


__all__ = ["IntentCategory", "IntentSignal", "IntentClassifier", "ClassificationResult"]
