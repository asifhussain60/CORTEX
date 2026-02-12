"""Intent Classifier - Multi-label intent classification with confidence scoring.

Classifies user intents from natural language text using keyword matching,
signal detection, and confidence scoring.

Author: CORTEX Framework
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


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
    ONBOARD = "onboard"  # AC-ONBOARD-001: Repository onboarding
    UNKNOWN = "unknown"


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
    metadata: Dict[str, Any] = field(default_factory=dict)
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
                "develop", "establish", "construct", "new", "setup", "initialize",
                "provision", "deploy", "instantiate", "form"
            },
            IntentCategory.FIX: {
                "fix", "repair", "resolve", "correct", "debug", "patch",
                "address", "solve", "remedy", "bug", "issue", "error",
                "broken", "failing"
            },
            IntentCategory.ANALYZE: {
                "analyze", "examine", "investigate", "review", "inspect",
                "study", "evaluate", "assess", "check", "audit", "explore"
            },
            IntentCategory.OPTIMIZE: {
                "optimize", "improve", "enhance", "speed", "performance",
                "faster", "efficient", "reduce", "minimize", "streamline",
                "accelerate", "boost"
            },
            IntentCategory.REFACTOR: {
                "refactor", "restructure", "reorganize", "clean", "simplify",
                "modularize", "rewrite", "improve structure", "consolidate",
                "redesign"
            },
            IntentCategory.TEST: {
                "test", "tests", "testing", "verify", "validate", "check",
                "ensure", "confirm", "assert", "coverage", "unit test",
                "integration test"
            },
            IntentCategory.DOCUMENT: {
                "document", "doc", "explain", "describe", "comment", "annotate",
                "readme", "guide", "manual", "documentation", "docs"
            },
            IntentCategory.MODIFY: {
                "modify", "change", "update", "alter", "adjust", "edit",
                "revise", "amend", "tweak", "customize"
            },
            IntentCategory.QUERY: {
                "what", "how", "why", "when", "where", "which", "who",
                "show", "tell", "explain", "is", "are", "can", "does", "?",
                "help", "info", "information"
            },
            IntentCategory.COMMAND: {
                "run", "execute", "start", "stop", "restart", "deploy",
                "install", "configure", "enable", "disable", "launch"
            },
            IntentCategory.NAVIGATION: {
                "navigate", "open", "display", "view",
                "switch", "move", "jump", "find", "locate"
            },
            # AC-ONBOARD-001: Repository onboarding keywords
            IntentCategory.ONBOARD: {
                "onboard", "onboarding", "setup", "initialize", "bootstrap",
                "register", "integrate", "import project", "analyze repository",
                "scan repo", "discover", "inventory", "profile", "assess"
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
        words = normalized.split()
        total_words = max(len(words), 1)

        for intent, keywords in self.keyword_mappings.items():
            matches = 0.0
            # Use whole-word matching to avoid substring issues (e.g., "go" in "governance")
            for keyword in keywords:
                # Check for whole word boundaries
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, normalized):
                    matches += 1.0

            if matches > 0:
                # Base score: keyword density
                density = matches / len(keywords)
                # Word ratio: matches relative to input length
                word_ratio = matches / total_words
                # Combined score with higher weight on density
                intent_scores[intent] = (density * 0.7) + (word_ratio * 0.3)

        # Detect signals
        detected_signals = []
        for signal, pattern in self.signal_patterns.items():
            if pattern.search(normalized):
                detected_signals.append(signal)

        # Determine primary intent
        if not intent_scores:
            # No clear intent = query with LOW confidence for ambiguous text
            primary = IntentCategory.QUERY
            confidence = 0.3  # Lower default for truly ambiguous text
        else:
            sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
            primary = sorted_intents[0][0]

            # Confidence calculation
            base_score = sorted_intents[0][1]

            # Boost for clear intents (multiple keyword matches)
            if base_score > 0.15:
                confidence = min(base_score * 2.0, 0.95)
            else:
                confidence = base_score * 1.5

            # Signal boost
            signal_boost = len(detected_signals) * 0.05
            confidence = min(confidence + signal_boost, 0.99)

        # Extract keywords (up to 5, filter short words)
        keywords_list = [w for w in words if len(w) > 2][:5]

        # Build secondary intents
        # Must be at least 50% of primary score to be considered secondary
        if intent_scores:
            primary_score = intent_scores[primary]
            threshold = max(primary_score * 0.5, 0.05)
            secondary = [(intent, score) for intent, score in intent_scores.items()
                        if intent != primary and score >= threshold][:3]
        else:
            secondary = []

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
