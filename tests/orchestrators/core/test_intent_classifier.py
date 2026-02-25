"""
Tests for IntentClassifier — three-tier (regex + keyword + LLM) intent recognition.

AC-ID: AC-70-INTENT-CLASSIFIER-001
Phase 70 GAP-70-A4 — RED phase tests written before implementation.

Governance:
    CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from cortex.models.canonical_enums import IntentType
from cortex.orchestrators.core.intent_classifier import (
    IntentClassificationResult,
    IntentClassifier,
)


# ---------------------------------------------------------------------------
# Tier 0 — Exact operation match
# ---------------------------------------------------------------------------


class TestExactOperationMatch:
    """Tier 0: explicit operation field short-circuits all other tiers."""

    @pytest.fixture
    def clf(self) -> IntentClassifier:
        """Return classifier with LLM disabled."""
        return IntentClassifier(enable_llm=False)

    @pytest.mark.parametrize(
        "operation,expected",
        [
            ("fix", IntentType.FIX),
            ("audit", IntentType.AUDIT),
            ("refactor", IntentType.REFACTOR),
            ("design", IntentType.DESIGN),
            ("plan", IntentType.PLAN),
            ("investigate", IntentType.INVESTIGATE),
            ("analyze", IntentType.ANALYZE),
            ("digest", IntentType.DIGEST),
            ("implement", IntentType.IMPLEMENT),
            ("onboard", IntentType.ONBOARD),
        ],
    )
    def test_exact_match_returns_correct_intent(
        self, clf: IntentClassifier, operation: str, expected: IntentType
    ) -> None:
        """Exact operation field must map to the canonical IntentType."""
        result = clf.classify("some description", operation=operation)
        assert result.intent_type == expected, (
            f"operation='{operation}' should map to {expected}, got {result.intent_type}"
        )
        assert result.tier_used == 0, "Exact match must report tier_used=0"
        assert result.confidence == 1.0, "Exact match must have 100% confidence"


# ---------------------------------------------------------------------------
# Tier 1 — Regex
# ---------------------------------------------------------------------------


class TestTier1Regex:
    """Tier 1: regex patterns fire before keyword scoring."""

    @pytest.fixture
    def clf(self) -> IntentClassifier:
        """Classifier with LLM disabled — pure regex + keyword."""
        return IntentClassifier(enable_llm=False)

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("fix the broken authentication handler", IntentType.FIX),
            ("investigate why the audit trail writes are failing", IntentType.INVESTIGATE),
            ("digest /docs/architecture — summarize key patterns", IntentType.DIGEST),
            ("analyze the performance bottleneck in the query engine", IntentType.ANALYZE),
            ("design a caching layer for the API gateway", IntentType.DESIGN),
            ("audit the codebase for stale imports", IntentType.AUDIT),
            ("refactor the master orchestrator for clarity", IntentType.REFACTOR),
            ("plan the next phase of development", IntentType.PLAN),
        ],
    )
    def test_regex_fires_for_canonical_phrases(
        self, clf: IntentClassifier, text: str, expected: IntentType
    ) -> None:
        """Canonical trigger phrases must be caught by Tier 1 regex."""
        result = clf.classify(text)
        assert result.intent_type == expected, (
            f"'{text}' should classify as {expected.value}, got {result.intent_type.value}"
        )
        assert result.tier_used in (0, 1, 2), "tier_used must be 0, 1, or 2 (no LLM)"

    def test_audit_not_swallowed_by_fix_keywords(self, clf: IntentClassifier) -> None:
        """'audit the repository for issues' must not route to FIX despite 'issue' keyword."""
        result = clf.classify("audit the repository for issues", operation="")
        assert result.intent_type == IntentType.AUDIT, (
            f"'audit' should dominate 'issue'. Got: {result.intent_type.value}"
        )

    def test_investigate_not_swallowed_by_audit_keyword(
        self, clf: IntentClassifier
    ) -> None:
        """'investigate why the audit trail...' must map to INVESTIGATE not AUDIT."""
        result = clf.classify("investigate why the audit trail writes are failing")
        assert result.intent_type == IntentType.INVESTIGATE, (
            f"INVESTIGATE should win over AUDIT. Got: {result.intent_type.value}"
        )


# ---------------------------------------------------------------------------
# Tier 2 — Keyword scoring
# ---------------------------------------------------------------------------


class TestTier2Keywords:
    """Tier 2: keyword bag-of-words scoring fills gaps when regex gives no match."""

    @pytest.fixture
    def clf(self) -> IntentClassifier:
        """Classifier with LLM disabled."""
        return IntentClassifier(enable_llm=False)

    def test_keyword_scores_populated(self, clf: IntentClassifier) -> None:
        """tier2_scores must contain non-empty dict for known phrases."""
        result = clf.classify("implement a new logging endpoint")
        assert len(result.tier2_scores) > 0, "tier2_scores must not be empty"

    def test_implement_scores_highest_for_implement_phrase(
        self, clf: IntentClassifier
    ) -> None:
        """IMPLEMENT keywords must outscore others for a creation phrase."""
        result = clf.classify("implement a new logging endpoint for the service")
        # Either regex or keyword must resolve to IMPLEMENT
        assert result.intent_type == IntentType.IMPLEMENT, (
            f"Expected IMPLEMENT, got {result.intent_type.value}"
        )


# ---------------------------------------------------------------------------
# Tier 3 — LLM (mocked)
# ---------------------------------------------------------------------------


class TestTier3LLM:
    """Tier 3: LLM is called when confidence is below threshold."""

    def test_llm_called_when_confidence_low(self) -> None:
        """LLM tier must fire when tier 2 confidence is below threshold."""
        clf = IntentClassifier(enable_llm=True, llm_skip_threshold=1.0)  # Force LLM always

        mock_response = MagicMock()
        mock_response.content = "PLAN"

        mock_llm = MagicMock()
        mock_llm.generate.return_value = mock_response

        clf._llm = mock_llm  # inject mock provider directly

        # "orchestrate future efforts" has no strong regex or keyword match → forces LLM
        result = clf.classify("orchestrate future efforts towards our goal")
        assert result.intent_type == IntentType.PLAN, (
            f"LLM should have classified PLAN, got {result.intent_type.value}"
        )
        assert result.tier_used == 3, f"Expected tier_used=3, got {result.tier_used}"
        mock_llm.generate.assert_called_once()

    def test_llm_failure_falls_back_to_tier2(self) -> None:
        """LLM failure must be silently absorbed — fall back to tier 2 result."""
        clf = IntentClassifier(enable_llm=True, llm_skip_threshold=1.0)

        mock_llm = MagicMock()
        mock_llm.generate.side_effect = RuntimeError("LLM unavailable")
        clf._llm = mock_llm

        # Should not raise
        result = clf.classify("implement a new feature")
        assert result.intent_type is not None, "Must return a result even if LLM fails"
        assert result.tier_used in (1, 2), (
            f"Should fall back to tier 1/2, got tier_used={result.tier_used}"
        )

    def test_llm_disabled_never_calls_provider(self) -> None:
        """When enable_llm=False, LLM provider must never be called."""
        clf = IntentClassifier(enable_llm=False)

        with patch.object(clf, "_get_llm") as mock_get:
            clf.classify("some ambiguous request that is hard to classify")
            mock_get.assert_not_called()


# ---------------------------------------------------------------------------
# Integration: result shape
# ---------------------------------------------------------------------------


class TestResultShape:
    """Verify IntentClassificationResult has all expected fields."""

    @pytest.fixture
    def clf(self) -> IntentClassifier:
        """Classifier with LLM disabled."""
        return IntentClassifier(enable_llm=False)

    def test_result_has_intent_type(self, clf: IntentClassifier) -> None:
        """Result must always have a valid intent_type."""
        result = clf.classify("do something")
        assert isinstance(result.intent_type, IntentType)

    def test_result_has_confidence_in_range(self, clf: IntentClassifier) -> None:
        """Confidence must be in [0.0, 1.0]."""
        result = clf.classify("fix the login bug")
        assert 0.0 <= result.confidence <= 1.0, (
            f"confidence out of range: {result.confidence}"
        )

    def test_result_has_tier_used(self, clf: IntentClassifier) -> None:
        """tier_used must be 0, 1, 2, or 3."""
        result = clf.classify("audit the codebase")
        assert result.tier_used in (0, 1, 2, 3), (
            f"Invalid tier_used: {result.tier_used}"
        )

    def test_result_has_reasoning_string(self, clf: IntentClassifier) -> None:
        """reasoning must be a non-empty string."""
        result = clf.classify("refactor the database layer")
        assert isinstance(result.reasoning, str)
        assert len(result.reasoning) > 0, "reasoning must not be empty"


# ---------------------------------------------------------------------------
# Differentiation (mirrors golden test assertions)
# ---------------------------------------------------------------------------


class TestDifferentiation:
    """Intent classifier must produce distinct outputs for distinct intents."""

    @pytest.fixture
    def clf(self) -> IntentClassifier:
        """Classifier with LLM disabled."""
        return IntentClassifier(enable_llm=False)

    @pytest.mark.parametrize(
        "text,operation,expected",
        [
            ("fix the broken test in the health orchestrator", "fix", IntentType.FIX),
            ("audit the codebase for stale imports", "audit", IntentType.AUDIT),
            ("refactor the master orchestrator for clarity", "refactor", IntentType.REFACTOR),
            ("design the architecture for the new module", "design", IntentType.DESIGN),
            ("plan the next phase of development", "plan", IntentType.PLAN),
            ("audit the repository for issues", "", IntentType.AUDIT),
            ("investigate why the audit trail writes are failing", "", IntentType.INVESTIGATE),
            ("digest /docs/architecture — summarize key patterns", "", IntentType.DIGEST),
            ("analyze the performance bottleneck in the query engine", "", IntentType.ANALYZE),
        ],
    )
    def test_canonical_intent_routing(
        self,
        clf: IntentClassifier,
        text: str,
        operation: str,
        expected: IntentType,
    ) -> None:
        """All canonical trigger phrases must classify correctly."""
        result = clf.classify(text, operation=operation)
        assert result.intent_type == expected, (
            f"'{text}' (op='{operation}') → expected {expected.value}, "
            f"got {result.intent_type.value} (tier={result.tier_used}, "
            f"confidence={result.confidence:.2f})"
        )

    def test_at_least_four_distinct_intents(self, clf: IntentClassifier) -> None:
        """Five different requests must produce ≥4 distinct intent types."""
        requests = [
            ("fix the broken test", "fix"),
            ("audit the codebase", "audit"),
            ("refactor the module", "refactor"),
            ("design the architecture", "design"),
            ("plan the next phase", "plan"),
        ]
        intents = {clf.classify(t, operation=o).intent_type for t, o in requests}
        assert len(intents) >= 4, (
            f"5 different requests produced only {len(intents)} distinct intents: {intents}"
        )
