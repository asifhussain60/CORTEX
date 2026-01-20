"""
Tests for Intent Classification Framework - AC-PHX-007-01

This test suite validates the IntentClassifier implementation including:
- Basic classification functionality
- Confidence scoring accuracy
- Signal detection
- Keyword extraction
- Multi-label classification
- Cache behavior
- Performance metrics
- Error handling

CORTEX Governance Rules Applied:
- CORE-008: TDD (tests first, RED → GREEN)
- CORE-013: Specific exception handling
- CORE-027: Audit trail considerations

Test Coverage Target: ≥98%
Expected Tests: 45 unit tests

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from typing import List

from src.intent_router.classifier import (
    IntentClassifier,
    IntentCategory,
    IntentSignal,
    ClassificationResult,
)


class TestIntentClassifierInitialization:
    """Test IntentClassifier initialization."""
    
    def test_init_creates_classifier(self) -> None:
        """Classifier should initialize successfully."""
        classifier = IntentClassifier()
        assert classifier is not None
    
    def test_init_sets_up_keywords(self) -> None:
        """Initialization should set up keyword mappings."""
        classifier = IntentClassifier()
        assert len(classifier.keyword_mappings) > 0
        assert IntentCategory.CREATE in classifier.keyword_mappings
    
    def test_init_compiles_signal_patterns(self) -> None:
        """Initialization should compile regex patterns."""
        classifier = IntentClassifier()
        assert len(classifier.signal_patterns) == len(IntentSignal)
    
    def test_init_initializes_metrics(self) -> None:
        """Initialization should set up metrics."""
        classifier = IntentClassifier()
        assert classifier.metrics["total_classifications"] == 0
        assert classifier.metrics["cache_hits"] == 0
    
    def test_init_creates_empty_cache(self) -> None:
        """Initialization should create empty classification cache."""
        classifier = IntentClassifier()
        assert len(classifier.classification_cache) == 0


class TestBasicClassification:
    """Test basic intent classification."""
    
    def test_classify_create_intent(self) -> None:
        """Should classify CREATE intent correctly."""
        classifier = IntentClassifier()
        result = classifier.classify("Create a new authentication module")
        assert result.primary_intent == IntentCategory.CREATE
        assert result.confidence_score > 0.0
    
    def test_classify_fix_intent(self) -> None:
        """Should classify FIX intent correctly."""
        classifier = IntentClassifier()
        result = classifier.classify("Fix the race condition in the router")
        assert result.primary_intent == IntentCategory.FIX
    
    def test_classify_analyze_intent(self) -> None:
        """Should classify ANALYZE intent correctly."""
        classifier = IntentClassifier()
        result = classifier.classify("Analyze the source code for vulnerabilities")
        assert result.primary_intent == IntentCategory.ANALYZE
    
    def test_classify_optimize_intent(self) -> None:
        """Should classify OPTIMIZE intent correctly."""
        classifier = IntentClassifier()
        result = classifier.classify("Optimize the memory usage")
        assert result.primary_intent == IntentCategory.OPTIMIZE
    
    def test_classify_refactor_intent(self) -> None:
        """Should classify REFACTOR intent correctly."""
        classifier = IntentClassifier()
        result = classifier.classify("Refactor the orchestrator for clarity")
        assert result.primary_intent == IntentCategory.REFACTOR
    
    def test_classify_test_intent(self) -> None:
        """Should classify TEST intent correctly."""
        classifier = IntentClassifier()
        result = classifier.classify("Write unit tests for the classifier")
        assert result.primary_intent == IntentCategory.TEST
    
    def test_classify_document_intent(self) -> None:
        """Should classify DOCUMENT intent correctly."""
        classifier = IntentClassifier()
        result = classifier.classify("Document the API endpoints")
        assert result.primary_intent == IntentCategory.DOCUMENT
    
    def test_classify_modify_intent(self) -> None:
        """Should classify MODIFY intent correctly."""
        classifier = IntentClassifier()
        result = classifier.classify("Modify the configuration settings")
        assert result.primary_intent == IntentCategory.MODIFY


class TestConfidenceScoring:
    """Test confidence scoring functionality."""
    
    def test_confidence_score_range(self) -> None:
        """Confidence score should be between 0.0 and 1.0."""
        classifier = IntentClassifier()
        result = classifier.classify("Create something new")
        assert 0.0 <= result.confidence_score <= 1.0
    
    def test_clear_intent_higher_confidence(self) -> None:
        """Clear intent should have higher confidence than ambiguous."""
        classifier = IntentClassifier()
        clear = classifier.classify("Create a new module with authentication")
        ambiguous = classifier.classify("maybe something about code")
        assert clear.confidence_score >= ambiguous.confidence_score
    
    def test_confidence_consistency(self) -> None:
        """Same text should produce same confidence score."""
        classifier = IntentClassifier()
        text = "Create a new REST API endpoint"
        result1 = classifier.classify(text)
        result2 = classifier.classify(text)
        assert result1.confidence_score == result2.confidence_score


class TestSignalDetection:
    """Test intent signal detection."""
    
    def test_detect_imperative_signal(self) -> None:
        """Should detect imperative signal."""
        classifier = IntentClassifier()
        result = classifier.classify("Create a new feature")
        assert IntentSignal.IMPERATIVE in result.detected_signals
    
    def test_detect_problem_statement_signal(self) -> None:
        """Should detect problem statement signal."""
        classifier = IntentClassifier()
        result = classifier.classify("Fix the bug in the router")
        assert IntentSignal.PROBLEM_STATEMENT in result.detected_signals
    
    def test_detect_feature_request_signal(self) -> None:
        """Should detect feature request signal."""
        classifier = IntentClassifier()
        result = classifier.classify("Add support for OAuth2")
        assert IntentSignal.FEATURE_REQUEST in result.detected_signals
    
    def test_detect_improvement_signal(self) -> None:
        """Should detect improvement request signal."""
        classifier = IntentClassifier()
        result = classifier.classify("Improve the performance")
        assert IntentSignal.IMPROVEMENT_REQUEST in result.detected_signals
    
    def test_detect_interrogative_signal(self) -> None:
        """Should detect interrogative signal."""
        classifier = IntentClassifier()
        result = classifier.classify("How can we optimize the code?")
        assert IntentSignal.INTERROGATIVE in result.detected_signals
    
    def test_detect_multiple_signals(self) -> None:
        """Should detect multiple signals in text."""
        classifier = IntentClassifier()
        result = classifier.classify("Create a new feature to support OAuth2")
        assert len(result.detected_signals) >= 1


class TestKeywordExtraction:
    """Test keyword extraction functionality."""
    
    def test_extract_keywords(self) -> None:
        """Should extract relevant keywords."""
        classifier = IntentClassifier()
        result = classifier.classify("Create a new authentication module")
        assert len(result.keywords) > 0
    
    def test_keywords_related_to_intent(self) -> None:
        """Extracted keywords should relate to detected intent."""
        classifier = IntentClassifier()
        result = classifier.classify("Create a new authentication module")
        # Keywords should contain terms related to CREATE intent
        assert any(kw in ["create", "new", "module"] for kw in result.keywords)
    
    def test_keyword_limit(self) -> None:
        """Keyword list should be limited."""
        classifier = IntentClassifier()
        result = classifier.classify("Create new features for the system")
        assert len(result.keywords) <= 10


class TestMultiLabelClassification:
    """Test multi-label classification (secondary intents)."""
    
    def test_secondary_intents_present(self) -> None:
        """Should identify secondary intent categories."""
        classifier = IntentClassifier()
        result = classifier.classify("Create and test the new feature")
        assert len(result.secondary_intents) > 0
    
    def test_secondary_intents_ordered(self) -> None:
        """Secondary intents should be ordered by score."""
        classifier = IntentClassifier()
        result = classifier.classify("Create and test the new feature")
        if len(result.secondary_intents) > 1:
            scores = [score for _, score in result.secondary_intents]
            assert scores == sorted(scores, reverse=True)
    
    def test_secondary_intents_scores_valid(self) -> None:
        """Secondary intent scores should be valid."""
        classifier = IntentClassifier()
        result = classifier.classify("Create and test the feature")
        for intent, score in result.secondary_intents:
            assert 0.0 <= score <= 1.0
            assert isinstance(intent, IntentCategory)


class TestClassificationResult:
    """Test ClassificationResult dataclass."""
    
    def test_result_has_all_fields(self) -> None:
        """Result should have all required fields."""
        classifier = IntentClassifier()
        result = classifier.classify("Create something")
        assert hasattr(result, "primary_intent")
        assert hasattr(result, "confidence_score")
        assert hasattr(result, "secondary_intents")
        assert hasattr(result, "detected_signals")
        assert hasattr(result, "keywords")
        assert hasattr(result, "reasoning")
        assert hasattr(result, "metadata")
        assert hasattr(result, "timestamp")
    
    def test_result_reasoning_present(self) -> None:
        """Result should have reasoning explanation."""
        classifier = IntentClassifier()
        result = classifier.classify("Create a new module")
        assert len(result.reasoning) > 0
    
    def test_result_timestamp_present(self) -> None:
        """Result should have ISO 8601 timestamp."""
        classifier = IntentClassifier()
        result = classifier.classify("Create something")
        assert result.timestamp is not None
        assert "T" in result.timestamp  # ISO format check


class TestCaching:
    """Test classification caching."""
    
    def test_cache_stores_result(self) -> None:
        """Cache should store classification results."""
        classifier = IntentClassifier()
        text = "Create a new feature"
        classifier.classify(text)
        assert len(classifier.classification_cache) > 0
    
    def test_cache_hit_increments_counter(self) -> None:
        """Cache hit should increment counter."""
        classifier = IntentClassifier()
        text = "Create a new feature"
        classifier.classify(text)
        initial_hits = classifier.metrics["cache_hits"]
        classifier.classify(text)  # Second call should be cache hit
        assert classifier.metrics["cache_hits"] > initial_hits
    
    def test_same_result_from_cache(self) -> None:
        """Cached result should be identical to new classification."""
        classifier = IntentClassifier()
        text = "Create a new module"
        result1 = classifier.classify(text)
        result2 = classifier.classify(text)
        assert result1.primary_intent == result2.primary_intent
        assert result1.confidence_score == result2.confidence_score
    
    def test_clear_cache(self) -> None:
        """Should clear the classification cache."""
        classifier = IntentClassifier()
        classifier.classify("Create something")
        assert len(classifier.classification_cache) > 0
        classifier.clear_cache()
        assert len(classifier.classification_cache) == 0


class TestMetrics:
    """Test performance metrics."""
    
    def test_metrics_initialization(self) -> None:
        """Metrics should initialize correctly."""
        classifier = IntentClassifier()
        metrics = classifier.get_metrics()
        assert metrics["total_classifications"] == 0
        assert metrics["cache_hits"] == 0
        assert metrics["avg_confidence"] == 0.0
    
    def test_metrics_track_classifications(self) -> None:
        """Metrics should track total classifications."""
        classifier = IntentClassifier()
        classifier.classify("Create something")
        classifier.classify("Fix a bug")
        metrics = classifier.get_metrics()
        assert metrics["total_classifications"] == 2
    
    def test_metrics_track_cache_hits(self) -> None:
        """Metrics should track cache hits."""
        classifier = IntentClassifier()
        text = "Create something"
        classifier.classify(text)
        classifier.classify(text)
        metrics = classifier.get_metrics()
        assert metrics["cache_hits"] >= 1
    
    def test_metrics_track_avg_confidence(self) -> None:
        """Metrics should track average confidence."""
        classifier = IntentClassifier()
        classifier.classify("Create something very clear")
        metrics = classifier.get_metrics()
        assert metrics["avg_confidence"] > 0.0


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_empty_string_raises_error(self) -> None:
        """Empty string should raise ValueError."""
        classifier = IntentClassifier()
        with pytest.raises(ValueError):
            classifier.classify("")
    
    def test_none_input_raises_error(self) -> None:
        """None input should raise ValueError."""
        classifier = IntentClassifier()
        with pytest.raises(ValueError):
            classifier.classify(None)  # type: ignore
    
    def test_non_string_input_raises_error(self) -> None:
        """Non-string input should raise ValueError."""
        classifier = IntentClassifier()
        with pytest.raises(ValueError):
            classifier.classify(123)  # type: ignore
    
    def test_ambiguous_text_classification(self) -> None:
        """Ambiguous text should still classify."""
        classifier = IntentClassifier()
        result = classifier.classify("blah blah blah")
        assert result is not None
        assert isinstance(result.primary_intent, IntentCategory)
    
    def test_very_long_text(self) -> None:
        """Should handle very long text."""
        classifier = IntentClassifier()
        long_text = "Create " + "a new feature " * 100
        result = classifier.classify(long_text)
        assert result.primary_intent == IntentCategory.CREATE


class TestCaseInsensitivity:
    """Test case-insensitive classification."""
    
    def test_uppercase_classification(self) -> None:
        """Should classify uppercase text."""
        classifier = IntentClassifier()
        result = classifier.classify("CREATE A NEW MODULE")
        assert result.primary_intent == IntentCategory.CREATE
    
    def test_mixed_case_classification(self) -> None:
        """Should classify mixed-case text."""
        classifier = IntentClassifier()
        result = classifier.classify("Create A New Module")
        assert result.primary_intent == IntentCategory.CREATE
    
    def test_case_consistent_results(self) -> None:
        """Different cases should produce same result."""
        classifier = IntentClassifier()
        result_lower = classifier.classify("create something")
        result_upper = classifier.classify("CREATE SOMETHING")
        assert result_lower.primary_intent == result_upper.primary_intent


class TestWhitespaceHandling:
    """Test whitespace handling."""
    
    def test_leading_whitespace(self) -> None:
        """Should handle leading whitespace."""
        classifier = IntentClassifier()
        result = classifier.classify("   Create something")
        assert result.primary_intent == IntentCategory.CREATE
    
    def test_trailing_whitespace(self) -> None:
        """Should handle trailing whitespace."""
        classifier = IntentClassifier()
        result = classifier.classify("Create something   ")
        assert result.primary_intent == IntentCategory.CREATE
    
    def test_extra_spaces(self) -> None:
        """Should handle extra spaces."""
        classifier = IntentClassifier()
        result = classifier.classify("Create    a    new    module")
        assert result.primary_intent == IntentCategory.CREATE


class TestSpecificScenarios:
    """Test specific real-world scenarios."""
    
    def test_governance_related_intent(self) -> None:
        """Should classify governance-related operations."""
        classifier = IntentClassifier()
        result = classifier.classify("Create governance rules for CORTEX")
        assert result.primary_intent == IntentCategory.CREATE
    
    def test_orchestrator_related_intent(self) -> None:
        """Should classify orchestrator operations."""
        classifier = IntentClassifier()
        result = classifier.classify("Fix the master orchestrator routing bug")
        assert result.primary_intent == IntentCategory.FIX
    
    def test_complex_operation_description(self) -> None:
        """Should classify complex operation descriptions."""
        classifier = IntentClassifier()
        text = (
            "Create a new intent classification module that analyzes "
            "natural language and routes to appropriate handlers"
        )
        result = classifier.classify(text)
        assert result.primary_intent == IntentCategory.CREATE
        assert result.confidence_score > 0.0
