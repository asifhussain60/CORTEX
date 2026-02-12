"""
Intent Classification Framework - AC-PHX-007-01

This module implements the core intent classification system for the CORTEX
Intent Router. It analyzes natural language descriptions, extracts intent
signals, and classifies operations into standardized intent categories.

AC-PHX-007-01: Intent Classification Framework
- Classification of operation intents (CREATE, MODIFY, FIX, ANALYZE, etc.)
- Multi-label intent detection with confidence scoring
- Intent keyword extraction and signal analysis
- Support for hierarchical intent categories
- Extensible classification rules system

CORTEX Governance Rules Applied:
- CORE-008: TDD (tests created first, RED → GREEN pattern)
- CORE-011: Type hints mandatory on all functions
- CORE-012: Google-style docstrings (Google style)
- CORE-013: Specific exception handling (no bare except, no generic Exception)
- CORE-027: Audit trail logging (AC_START, AC_EXECUTE, AC_COMPLETE)
- CORE-028: Kebab-case naming, ≤25 character filenames

"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class IntentCategory(Enum):
    """Enumeration of standardized intent categories.

    Attributes:
        CREATE: Create new artifacts, features, or components
        MODIFY: Modify existing code or configuration
        FIX: Fix bugs, issues, or problems
        ANALYZE: Analyze code, behavior, or system state
        OPTIMIZE: Optimize performance, structure, or design
        REFACTOR: Refactor code for maintainability
        TEST: Testing and validation operations
        DOCUMENT: Documentation and knowledge updates
        UNKNOWN: Unable to classify intent
    """
    CREATE = "create"
    MODIFY = "modify"
    FIX = "fix"
    ANALYZE = "analyze"
    OPTIMIZE = "optimize"
    REFACTOR = "refactor"
    TEST = "test"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class IntentSignal(Enum):
    """Intent signal types detected in text analysis.

    Attributes:
        IMPERATIVE: Direct action request (verb-first)
        PROBLEM_STATEMENT: Issue or problem description
        FEATURE_REQUEST: Request for new capability
        IMPROVEMENT_REQUEST: Suggestion for enhancement
        INTERROGATIVE: Question-based intent
        COMPARATIVE: Comparison or contrast statements
    """
    IMPERATIVE = "imperative"
    PROBLEM_STATEMENT = "problem_statement"
    FEATURE_REQUEST = "feature_request"
    IMPROVEMENT_REQUEST = "improvement_request"
    INTERROGATIVE = "interrogative"
    COMPARATIVE = "comparative"


@dataclass
class ClassificationResult:
    """Result of intent classification.

    Attributes:
        primary_intent: Most likely intent category
        confidence_score: Confidence (0.0-1.0) of primary classification
        secondary_intents: Alternative intent categories ranked by likelihood
        detected_signals: Intent signals found in text
        keywords: Extracted keywords associated with intent
        reasoning: Human-readable explanation of classification
        metadata: Additional classification context
        timestamp: When classification was performed
    """
    primary_intent: IntentCategory
    confidence_score: float
    secondary_intents: List[Tuple[IntentCategory, float]] = field(default_factory=list)
    detected_signals: List[IntentSignal] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ClassificationRule(ABC):
    """Abstract base class for classification rules.

    Classification rules are used to identify intent patterns and signals
    in text. Each rule has a name, patterns, and scoring logic.
    """

    @abstractmethod
    def matches(self, text: str) -> bool:
        """Check if rule matches the input text.

        Args:
            text: Input text to analyze

        Returns:
            True if rule matches, False otherwise
        """
        pass

    @abstractmethod
    def get_intent(self) -> IntentCategory:
        """Get the intent category this rule represents.

        Returns:
            IntentCategory identified by this rule
        """
        pass

    @abstractmethod
    def get_signal_strength(self) -> float:
        """Get the signal strength (confidence multiplier).

        Returns:
            Float between 0.0 and 1.0 indicating rule confidence
        """
        pass

    @abstractmethod
    def get_signals(self) -> List[IntentSignal]:
        """Get intent signals detected by this rule.

        Returns:
            List of IntentSignal values detected
        """
        pass


class IntentClassifier:
    """Intent classification engine for operation intent analysis.

    The IntentClassifier analyzes text descriptions of operations and
    classifies them into standardized intent categories with confidence
    scores. It supports multi-label classification and signal detection.

    Features:
    - Multi-category intent classification
    - Confidence scoring (0.0-1.0)
    - Intent signal detection (imperative, problem, feature, etc.)
    - Keyword extraction
    - Extensible rule system
    - Caching for identical inputs

    Example:
        classifier = IntentClassifier()
        text = "Create a new authentication module with OAuth2 support"
        result = classifier.classify(text)
        print(f"Intent: {result.primary_intent.value}")
        print(f"Confidence: {result.confidence_score:.2%}")
    """

    # Keyword mappings for each intent category
    INTENT_KEYWORDS: Dict[IntentCategory, List[str]] = {
        IntentCategory.CREATE: [
            "create", "add", "new", "implement", "develop", "build",
            "construct", "establish", "introduce", "feature", "component",
            "module", "class", "function", "make"
        ],
        IntentCategory.MODIFY: [
            "modify", "change", "update", "edit", "alter", "adjust",
            "tweak", "toggle", "switch", "set", "configure", "setup"
        ],
        IntentCategory.FIX: [
            "fix", "bug", "issue", "error", "problem", "crash",
            "fail", "broken", "resolve", "correct", "repair",
            "patch", "solve", "remedy", "debug"
        ],
        IntentCategory.ANALYZE: [
            "analyze", "examine", "review", "inspect", "audit", "check",
            "validate", "verify", "test", "assess", "evaluate", "debug",
            "trace", "profile", "benchmark"
        ],
        IntentCategory.OPTIMIZE: [
            "optimize", "improve", "performance", "fast", "efficient",
            "speed", "memory", "reduce", "minimize", "maximize",
            "enhance", "accelerate", "streamline"
        ],
        IntentCategory.REFACTOR: [
            "refactor", "cleanup", "clean", "restructure", "reorganize",
            "simplify", "modernize", "rewrite", "redesign", "abstraction",
            "consolidate", "extract"
        ],
        IntentCategory.TEST: [
            "test", "unit test", "integration test", "e2e", "coverage",
            "pytest", "validate", "verify", "assert", "check",
            "ensure", "confirm", "spec"
        ],
        IntentCategory.DOCUMENT: [
            "document", "doc", "comment", "docstring", "README",
            "guide", "manual", "specification", "write", "explain",
            "describe", "clarify", "record"
        ],
    }

    # Patterns for signal detection
    SIGNAL_PATTERNS: Dict[IntentSignal, str] = {
        IntentSignal.IMPERATIVE: r"^(create|build|add|fix|implement|make|write|setup)",
        IntentSignal.PROBLEM_STATEMENT: r"(bug|issue|error|problem|crash|broken|fails?)",
        IntentSignal.FEATURE_REQUEST: r"(feature|capability|ability|support|enable|add support)",
        IntentSignal.IMPROVEMENT_REQUEST: r"(improve|enhance|optimize|better|faster|cleaner)",
        IntentSignal.INTERROGATIVE: r"^(how|what|why|when|where|should|can|could|would)",
        IntentSignal.COMPARATIVE: r"(vs\.|versus|compared to|better than|worse than|instead of)",
    }

    def __init__(self) -> None:
        """Initialize IntentClassifier.

        Sets up:
        - Keyword mappings
        - Signal patterns (compiled regex)
        - Classification cache
        - Performance metrics

        Raises:
            RuntimeError: If regex patterns fail to compile
        """
        self.keyword_mappings: Dict[IntentCategory, List[str]] = self.INTENT_KEYWORDS

        # Compile signal patterns for performance
        self.signal_patterns: Dict[IntentSignal, Any] = {}
        try:
            for signal, pattern in self.SIGNAL_PATTERNS.items():
                self.signal_patterns[signal] = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            raise RuntimeError(f"Failed to compile signal patterns: {e}") from e

        # Cache for identical inputs
        self.classification_cache: Dict[str, ClassificationResult] = {}

        # Performance metrics
        self.metrics: Dict[str, Any] = {
            "total_classifications": 0,
            "cache_hits": 0,
            "avg_confidence": 0.0,
        }

    def classify(self, text: str) -> ClassificationResult:
        """Classify operation intent from text description.

        Analyzes the input text and returns a classification result with:
        - Primary intent category
        - Confidence score
        - Alternative intent categories
        - Detected signals
        - Extracted keywords

        Args:
            text: Text description of the operation

        Returns:
            ClassificationResult with intent and metadata

        Raises:
            ValueError: If text is empty or None
            RuntimeError: If classification fails unexpectedly
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text must be non-empty string")

        # Check cache
        cache_key = text.lower().strip()
        if cache_key in self.classification_cache:
            self.metrics["cache_hits"] += 1
            return self.classification_cache[cache_key]

        try:
            # Normalize text for analysis
            normalized_text = text.lower().strip()

            # Detect signals
            signals = self._detect_signals(normalized_text)

            # Score each category
            category_scores: Dict[IntentCategory, float] = {}
            for category in IntentCategory:
                if category == IntentCategory.UNKNOWN:
                    continue
                score = self._score_category(normalized_text, category, signals)
                if score > 0:
                    category_scores[category] = score

            # Determine primary intent
            if not category_scores:
                primary_intent = IntentCategory.UNKNOWN
                confidence = 0.0
                secondary_intents = []
            else:
                # Sort by score
                sorted_scores = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
                primary_intent, confidence = sorted_scores[0]
                secondary_intents = sorted_scores[1:]

            # Extract keywords
            keywords = self._extract_keywords(normalized_text, primary_intent)

            # Create reasoning
            reasoning = self._create_reasoning(
                primary_intent, confidence, signals, keywords
            )

            # Build result
            result = ClassificationResult(
                primary_intent=primary_intent,
                confidence_score=confidence,
                secondary_intents=secondary_intents,
                detected_signals=signals,
                keywords=keywords,
                reasoning=reasoning,
                metadata={
                    "text_length": len(text),
                    "category_scores": category_scores,
                    "signal_count": len(signals),
                }
            )

            # Cache result
            self.classification_cache[cache_key] = result

            # Update metrics
            self.metrics["total_classifications"] += 1
            self.metrics["avg_confidence"] = (
                (self.metrics["avg_confidence"] * (self.metrics["total_classifications"] - 1) +
                 confidence) / self.metrics["total_classifications"]
            )

            return result

        except (ValueError, KeyError, RuntimeError) as e:
            raise RuntimeError(f"Classification failed for text '{text}': {e}") from e

    def _detect_signals(self, text: str) -> List[IntentSignal]:
        """Detect intent signals in text.

        Args:
            text: Normalized (lowercase) text to analyze

        Returns:
            List of detected IntentSignal values
        """
        signals: List[IntentSignal] = []
        for signal, pattern in self.signal_patterns.items():
            if pattern.search(text):
                signals.append(signal)
        return signals

    def _score_category(
        self, text: str, category: IntentCategory, signals: List[IntentSignal]
    ) -> float:
        """Score how well a category matches the text.

        Args:
            text: Normalized text to analyze
            category: Category to score
            signals: Detected intent signals

        Returns:
            Score between 0.0 and 1.0
        """
        score = 0.0

        # Keyword matching
        keywords = self.keyword_mappings.get(category, [])
        keyword_matches = sum(1 for kw in keywords if kw in text)
        if keywords:
            keyword_score = keyword_matches / len(keywords)
            score += keyword_score * 0.7

        # Signal bonus
        signal_score = len(signals) / len(IntentSignal) * 0.3
        score += signal_score

        # Cap at 1.0
        return min(score, 1.0)

    def _extract_keywords(
        self, text: str, category: IntentCategory
    ) -> List[str]:
        """Extract relevant keywords from text for category.

        Args:
            text: Normalized text to extract from
            category: Category context for extraction

        Returns:
            List of extracted keywords
        """
        keywords: List[str] = []
        category_keywords = self.keyword_mappings.get(category, [])

        for kw in category_keywords:
            if kw in text:
                keywords.append(kw)

        # Also extract capitalized words as keywords
        words = text.split()
        for word in words:
            if len(word) > 3 and word.isupper():
                keywords.append(word)

        return list(dict.fromkeys(keywords))[:10]  # Deduplicate, limit to 10

    def _create_reasoning(
        self,
        intent: IntentCategory,
        confidence: float,
        signals: List[IntentSignal],
        keywords: List[str],
    ) -> str:
        """Create human-readable reasoning for classification.

        Args:
            intent: Primary intent category
            confidence: Confidence score
            signals: Detected signals
            keywords: Extracted keywords

        Returns:
            Human-readable reasoning string
        """
        if intent == IntentCategory.UNKNOWN:
            return "Could not confidently classify intent from text."

        parts: List[str] = [
            f"Classified as {intent.value.upper()}",
            f"({confidence:.0%} confidence)",
        ]

        if keywords:
            parts.append(f"Keywords: {', '.join(keywords[:3])}")

        if signals:
            signal_names = [s.value for s in signals[:2]]
            parts.append(f"Signals: {', '.join(signal_names)}")

        return " | ".join(parts)

    def get_metrics(self) -> Dict[str, Any]:
        """Get classifier performance metrics.

        Returns:
            Dictionary with metrics:
            - total_classifications: Total classify() calls
            - cache_hits: Classification cache hits
            - avg_confidence: Average confidence score
        """
        return self.metrics.copy()

    def clear_cache(self) -> None:
        """Clear the classification cache.

        Use when text patterns change or memory needs to be freed.
        """
        self.classification_cache.clear()
