# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: IR-002-01 - Intent Understanding & Canonicalization Tests
"""
Tests for Intent Understanding & Canonicalization.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-002-01 - Intent Understanding & Canonicalization

Tests cover:
- Natural language intent parsing
- Intent type canonicalization
- Target scope extraction
- Confidence scoring
- Clarification generation
"""

import textwrap
from typing import Any, Dict, List

import pytest


# =============================================================================
# TEST FIXTURES
# =============================================================================


@pytest.fixture
def implement_requests() -> List[Dict[str, Any]]:
    """Sample implementation requests."""
    return [
        {
            "text": "implement user authentication for the API",
            "expected_intent": "IMPLEMENT",
            "expected_scope": ["API", "authentication"],
        },
        {
            "text": "add a new endpoint for fetching orders",
            "expected_intent": "IMPLEMENT",
            "expected_scope": ["endpoint", "orders"],
        },
        {
            "text": "create a cache layer for database queries",
            "expected_intent": "IMPLEMENT",
            "expected_scope": ["cache", "database"],
        },
    ]


@pytest.fixture
def fix_requests() -> List[Dict[str, Any]]:
    """Sample fix requests."""
    return [
        {
            "text": "fix the bug in the login function",
            "expected_intent": "FIX",
            "expected_scope": ["login"],
        },
        {
            "text": "resolve the authentication error",
            "expected_intent": "FIX",
            "expected_scope": ["authentication"],
        },
        {
            "text": "the test is failing, please fix it",
            "expected_intent": "FIX",
            "expected_scope": ["test"],
        },
    ]


@pytest.fixture
def refactor_requests() -> List[Dict[str, Any]]:
    """Sample refactor requests."""
    return [
        {
            "text": "refactor the database module to use async",
            "expected_intent": "REFACTOR",
            "expected_scope": ["database"],
        },
        {
            "text": "clean up the user service code",
            "expected_intent": "REFACTOR",
            "expected_scope": ["user service"],
        },
        {
            "text": "improve the code structure in utils.py",
            "expected_intent": "REFACTOR",
            "expected_scope": ["utils.py"],
        },
    ]


@pytest.fixture
def query_requests() -> List[Dict[str, Any]]:
    """Sample query/info requests."""
    return [
        {
            "text": "what does the UserService class do?",
            "expected_intent": "QUERY",
            "expected_scope": ["UserService"],
        },
        {
            "text": "how does the authentication flow work?",
            "expected_intent": "QUERY",
            "expected_scope": ["authentication"],
        },
        {
            "text": "explain the database schema",
            "expected_intent": "QUERY",
            "expected_scope": ["database"],
        },
    ]


@pytest.fixture
def ambiguous_requests() -> List[Dict[str, Any]]:
    """Sample ambiguous requests requiring clarification."""
    return [
        {
            "text": "work on the login",
            "expected_confidence": "LOW",
        },
        {
            "text": "something is wrong",
            "expected_confidence": "LOW",
        },
        {
            "text": "the user thing",
            "expected_confidence": "LOW",
        },
    ]


@pytest.fixture
def scoped_requests() -> List[Dict[str, Any]]:
    """Requests with specific file/function scope."""
    return [
        {
            "text": "fix the calculate_total function in orders.py",
            "expected_scope_type": "function",
            "expected_file": "orders.py",
            "expected_target": "calculate_total",
        },
        {
            "text": "implement AC-ID FR-008-01",
            "expected_scope_type": "ac_id",
            "expected_target": "FR-008-01",
        },
        {
            "text": "refactor the UserModel class",
            "expected_scope_type": "class",
            "expected_target": "UserModel",
        },
    ]


# =============================================================================
# TEST CLASSES: INTENT TYPE EXTRACTION
# =============================================================================


class TestIntentTypeExtraction:
    """Tests for extracting intent types from requests."""

    def test_detect_implement_intent(
        self, implement_requests: List[Dict[str, Any]]
    ) -> None:
        """Test detection of IMPLEMENT intent."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        
        for request in implement_requests:
            result = canonicalizer.canonicalize(request["text"])
            assert result.intent_type == "IMPLEMENT", f"Failed for: {request['text']}"

    def test_detect_fix_intent(
        self, fix_requests: List[Dict[str, Any]]
    ) -> None:
        """Test detection of FIX intent."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        
        for request in fix_requests:
            result = canonicalizer.canonicalize(request["text"])
            assert result.intent_type == "FIX", f"Failed for: {request['text']}"

    def test_detect_refactor_intent(
        self, refactor_requests: List[Dict[str, Any]]
    ) -> None:
        """Test detection of REFACTOR intent."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        
        for request in refactor_requests:
            result = canonicalizer.canonicalize(request["text"])
            assert result.intent_type == "REFACTOR", f"Failed for: {request['text']}"

    def test_detect_query_intent(
        self, query_requests: List[Dict[str, Any]]
    ) -> None:
        """Test detection of QUERY intent."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        
        for request in query_requests:
            result = canonicalizer.canonicalize(request["text"])
            assert result.intent_type == "QUERY", f"Failed for: {request['text']}"

    def test_extract_keywords(
        self, implement_requests: List[Dict[str, Any]]
    ) -> None:
        """Test keyword extraction from requests."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        request = implement_requests[0]  # "implement user authentication for the API"
        
        result = canonicalizer.canonicalize(request["text"])
        
        # Should extract relevant keywords
        assert result.keywords is not None
        assert len(result.keywords) > 0


# =============================================================================
# TEST CLASSES: SCOPE EXTRACTION
# =============================================================================


class TestScopeExtraction:
    """Tests for extracting target scope from requests."""

    def test_extract_file_scope(
        self, scoped_requests: List[Dict[str, Any]]
    ) -> None:
        """Test extraction of file scope."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        request = scoped_requests[0]  # "fix the calculate_total function in orders.py"
        
        result = canonicalizer.canonicalize(request["text"])
        
        assert result.scope.file_path is not None
        assert "orders.py" in result.scope.file_path

    def test_extract_function_scope(
        self, scoped_requests: List[Dict[str, Any]]
    ) -> None:
        """Test extraction of function scope."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        request = scoped_requests[0]
        
        result = canonicalizer.canonicalize(request["text"])
        
        assert result.scope.function_name is not None
        assert result.scope.function_name == "calculate_total"

    def test_extract_ac_id_scope(
        self, scoped_requests: List[Dict[str, Any]]
    ) -> None:
        """Test extraction of AC-ID scope."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        request = scoped_requests[1]  # "implement AC-ID FR-008-01"
        
        result = canonicalizer.canonicalize(request["text"])
        
        assert result.scope.ac_id is not None
        assert result.scope.ac_id == "FR-008-01"

    def test_extract_class_scope(
        self, scoped_requests: List[Dict[str, Any]]
    ) -> None:
        """Test extraction of class scope."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        request = scoped_requests[2]  # "refactor the UserModel class"
        
        result = canonicalizer.canonicalize(request["text"])
        
        assert result.scope.class_name is not None
        assert result.scope.class_name == "UserModel"


# =============================================================================
# TEST CLASSES: CONFIDENCE SCORING
# =============================================================================


class TestConfidenceScoring:
    """Tests for confidence score assignment."""

    def test_high_confidence_clear_intent(
        self, implement_requests: List[Dict[str, Any]]
    ) -> None:
        """Test high confidence for clear intents."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        request = implement_requests[0]
        
        result = canonicalizer.canonicalize(request["text"])
        
        assert result.confidence >= 0.7

    def test_low_confidence_ambiguous_intent(
        self, ambiguous_requests: List[Dict[str, Any]]
    ) -> None:
        """Test low confidence for ambiguous requests."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        
        for request in ambiguous_requests:
            result = canonicalizer.canonicalize(request["text"])
            assert result.confidence < 0.7, f"Should be low confidence: {request['text']}"

    def test_confidence_ranges(self) -> None:
        """Test that confidence is always in valid range."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        
        test_texts = [
            "implement the feature",
            "fix",
            "do something",
            "",
            "refactor all the things in the system properly",
        ]
        
        for text in test_texts:
            result = canonicalizer.canonicalize(text)
            assert 0.0 <= result.confidence <= 1.0


# =============================================================================
# TEST CLASSES: CLARIFICATION GENERATION
# =============================================================================


class TestClarificationGeneration:
    """Tests for clarification prompt generation."""

    def test_generate_clarification_for_ambiguous(
        self, ambiguous_requests: List[Dict[str, Any]]
    ) -> None:
        """Test clarification generation for ambiguous requests."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        request = ambiguous_requests[0]  # "work on the login"
        
        result = canonicalizer.canonicalize(request["text"])
        
        assert result.needs_clarification
        assert result.clarification_prompt is not None
        assert len(result.clarification_prompt) > 0

    def test_no_clarification_for_clear_intent(
        self, implement_requests: List[Dict[str, Any]]
    ) -> None:
        """Test no clarification needed for clear intents."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        request = implement_requests[0]
        
        result = canonicalizer.canonicalize(request["text"])
        
        assert not result.needs_clarification

    def test_clarification_suggests_options(self) -> None:
        """Test that clarification prompt suggests valid options."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        result = canonicalizer.canonicalize("work on the code")
        
        if result.needs_clarification:
            # Should suggest specific actions
            prompt = result.clarification_prompt.lower()
            assert any(word in prompt for word in ["implement", "fix", "refactor", "explain"])


# =============================================================================
# TEST CLASSES: INTENT TYPES
# =============================================================================


class TestIntentTypes:
    """Tests for all supported intent types."""

    def test_all_intent_types_defined(self) -> None:
        """Test that all standard intent types are defined."""
        from cortex.core.intent.intent_canonicalizer import IntentType
        
        required_types = [
            "IMPLEMENT",
            "FIX",
            "REFACTOR",
            "QUERY",
            "ANALYZE",
            "VALIDATE",
            "MIGRATE",
        ]
        
        for intent_type in required_types:
            assert hasattr(IntentType, intent_type)

    def test_detect_analyze_intent(self) -> None:
        """Test detection of ANALYZE intent."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        
        requests = [
            "analyze the performance of the API",
            "investigate the memory leak",
            "debug the authentication flow",
        ]
        
        for text in requests:
            result = canonicalizer.canonicalize(text)
            assert result.intent_type == "ANALYZE", f"Failed for: {text}"

    def test_detect_validate_intent(self) -> None:
        """Test detection of VALIDATE intent."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        
        requests = [
            "validate the implementation against AC-ID",
            "check if the tests pass",
            "verify the database schema",
        ]
        
        for text in requests:
            result = canonicalizer.canonicalize(text)
            assert result.intent_type == "VALIDATE", f"Failed for: {text}"


# =============================================================================
# TEST CLASSES: INTEGRATION
# =============================================================================


class TestIntentCanonicalizerIntegration:
    """Integration tests for intent canonicalizer."""

    def test_full_canonicalization_pipeline(
        self, implement_requests: List[Dict[str, Any]]
    ) -> None:
        """Test complete canonicalization pipeline."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        request = implement_requests[0]
        
        result = canonicalizer.canonicalize(request["text"])
        
        assert result is not None
        assert result.intent_type is not None
        assert result.scope is not None
        assert result.confidence is not None
        assert isinstance(result.keywords, list)

    def test_serialization_to_dict(
        self, implement_requests: List[Dict[str, Any]]
    ) -> None:
        """Test serialization of canonicalized intent."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        request = implement_requests[0]
        
        result = canonicalizer.canonicalize(request["text"])
        serialized = result.to_dict()
        
        assert isinstance(serialized, dict)
        assert "intent_type" in serialized
        assert "scope" in serialized
        assert "confidence" in serialized
        assert "keywords" in serialized

    def test_canonicalize_with_context(
        self, implement_requests: List[Dict[str, Any]]
    ) -> None:
        """Test canonicalization with additional context."""
        from cortex.core.intent.intent_canonicalizer import IntentCanonicalizer
        
        canonicalizer = IntentCanonicalizer()
        
        context = {
            "current_file": "src/api/users.py",
            "project_type": "web_api",
            "recent_changes": ["authentication", "login"],
        }
        
        result = canonicalizer.canonicalize(
            "add validation",
            context=context,
        )
        
        assert result is not None
        # With context, should have higher confidence
        assert result.confidence > 0.5
