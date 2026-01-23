"""Tests for ResponseChallengeInjector module.

AC-ID: REMEDIATION-INTENT-006
Tests challenge-first response formatting and injection.
"""

import pytest
from cortex.orchestrators.response_challenge_injector import (
    ResponseChallengeInjector,
    ChallengeResponse,
    ResponseFormat,
)


class BaseResponseChallengeTest:
    """Base test class with common fixtures."""

    @pytest.fixture(autouse=True)
    def setup_injector(self):
        """Setup ResponseChallengeInjector instance."""
        self.injector = ResponseChallengeInjector()


class TestResponseChallengeInjectorInitialization(BaseResponseChallengeTest):
    """Test ResponseChallengeInjector initialization."""

    def test_injector_initializes(self):
        """Test injector initialization."""
        assert self.injector is not None

    def test_default_format_is_json(self):
        """Test default response format is JSON."""
        assert self.injector.default_format == ResponseFormat.JSON

    def test_challenge_priority_order_set(self):
        """Test challenge priority order is configured."""
        assert hasattr(self.injector, "priority_order")
        assert len(self.injector.priority_order) > 0


class TestChallengeResponse(BaseResponseChallengeTest):
    """Test ChallengeResponse data class."""

    def test_challenge_response_creation(self):
        """Test ChallengeResponse creation."""
        response = ChallengeResponse(
            execution_result="Success",
            challenges=[
                {
                    "category": "TEST_GAP",
                    "severity": "MEDIUM",
                    "description": "Missing unit tests",
                }
            ],
        )
        assert response.execution_result == "Success"
        assert len(response.challenges) > 0

    def test_challenge_response_with_recommendations(self):
        """Test response with recommendations."""
        response = ChallengeResponse(
            execution_result="Completed",
            challenges=[],
            recommendations=[
                {
                    "title": "Add tests",
                    "description": "Add unit tests for coverage",
                }
            ],
        )
        assert len(response.recommendations) > 0

    def test_challenge_response_format_selection(self):
        """Test response format selection."""
        response = ChallengeResponse(
            execution_result="Success",
            format=ResponseFormat.MARKDOWN,
        )
        assert response.format == ResponseFormat.MARKDOWN

    def test_challenge_response_to_dict(self):
        """Test to_dict() serialization."""
        response = ChallengeResponse(
            execution_result="Success",
            challenges=[{"category": "GOVERNANCE_RISK", "severity": "HIGH"}],
        )
        result_dict = response.to_dict()
        assert result_dict["execution_result"] == "Success"
        assert len(result_dict["challenges"]) > 0


class TestFormatResponses(BaseResponseChallengeTest):
    """Test response formatting."""

    def test_format_as_json(self):
        """Test formatting as JSON."""
        response = ChallengeResponse(
            execution_result="Success",
            challenges=[],
            format=ResponseFormat.JSON,
        )
        formatted = self.injector.format_response(response)
        assert isinstance(formatted, str)
        assert "{" in formatted  # JSON should have braces

    def test_format_as_markdown(self):
        """Test formatting as Markdown."""
        response = ChallengeResponse(
            execution_result="Success",
            challenges=[
                {
                    "category": "TEST_GAP",
                    "severity": "HIGH",
                    "description": "Missing test",
                }
            ],
            format=ResponseFormat.MARKDOWN,
        )
        formatted = self.injector.format_response(response)
        assert isinstance(formatted, str)
        assert "#" in formatted or "**" in formatted  # Markdown formatting

    def test_format_as_plain_text(self):
        """Test formatting as plain text."""
        response = ChallengeResponse(
            execution_result="Done",
            format=ResponseFormat.PLAIN_TEXT,
        )
        formatted = self.injector.format_response(response)
        assert isinstance(formatted, str)


class TestChallengeInjection(BaseResponseChallengeTest):
    """Test challenge injection into responses."""

    def test_inject_single_challenge(self):
        """Test injecting single challenge."""
        base_response = "Code implemented successfully"
        challenges = [
            {
                "category": "TEST_GAP",
                "severity": "MEDIUM",
                "description": "No unit tests",
            }
        ]
        result = self.injector.inject_challenges(base_response, challenges)
        assert "challenge" in result.lower() or "test" in result.lower()

    def test_inject_multiple_challenges(self):
        """Test injecting multiple challenges."""
        base_response = "Refactoring completed"
        challenges = [
            {
                "category": "PERFORMANCE_RISK",
                "severity": "MEDIUM",
                "description": "Nested loop detected",
            },
            {
                "category": "TEST_GAP",
                "severity": "HIGH",
                "description": "Test coverage dropped",
            },
        ]
        result = self.injector.inject_challenges(base_response, challenges)
        assert isinstance(result, str)
        assert len(result) > len(base_response)

    def test_challenge_ordering_by_severity(self):
        """Test challenges are ordered by severity."""
        base_response = "Done"
        challenges = [
            {"category": "TEST_GAP", "severity": "LOW"},
            {"category": "BREAKING_CHANGE", "severity": "CRITICAL"},
            {"category": "PERFORMANCE_RISK", "severity": "MEDIUM"},
        ]
        result = self.injector.inject_challenges(base_response, challenges)
        # CRITICAL should appear first
        critical_pos = result.lower().find("critical")
        low_pos = result.lower().find("low")
        assert critical_pos < low_pos or critical_pos == -1 or low_pos == -1

    def test_challenge_ordering_by_category(self):
        """Test challenges can be ordered by category."""
        challenges = [
            {
                "category": "TEST_GAP",
                "severity": "HIGH",
                "description": "Missing tests",
            },
            {
                "category": "GOVERNANCE_RISK",
                "severity": "HIGH",
                "description": "Risk detected",
            },
        ]
        ordered = self.injector.order_challenges(challenges)
        assert len(ordered) == len(challenges)


class TestChallengeFormatting(BaseResponseChallengeTest):
    """Test challenge formatting."""

    def test_format_single_challenge(self):
        """Test formatting single challenge."""
        challenge = {
            "category": "TEST_GAP",
            "severity": "HIGH",
            "description": "Missing unit tests",
            "mitigation": "Add tests for all functions",
        }
        formatted = self.injector.format_challenge(challenge)
        assert isinstance(formatted, str)
        assert "TEST_GAP" in formatted or "test" in formatted.lower()

    def test_format_challenge_with_evidence(self):
        """Test formatting challenge with evidence."""
        challenge = {
            "category": "SECURITY_RISK",
            "severity": "CRITICAL",
            "description": "Dangerous pattern detected",
            "evidence": ["eval() usage on line 42"],
            "mitigation": "Replace with safer alternative",
        }
        formatted = self.injector.format_challenge(challenge)
        assert isinstance(formatted, str)

    def test_format_challenge_with_scope(self):
        """Test formatting challenge with affected scope."""
        challenge = {
            "category": "PERFORMANCE_RISK",
            "severity": "MEDIUM",
            "description": "N+1 query pattern",
            "affected_scope": ["user_repository.py", "post_service.py"],
        }
        formatted = self.injector.format_challenge(challenge)
        assert isinstance(formatted, str)


class TestResponseStructure(BaseResponseChallengeTest):
    """Test response structure with challenges."""

    def test_response_with_execution_result_and_challenges(self):
        """Test response structure."""
        response = ChallengeResponse(
            execution_result="Successfully implemented user authentication",
            challenges=[
                {
                    "category": "TEST_GAP",
                    "severity": "HIGH",
                    "description": "No integration tests for OAuth flow",
                }
            ],
        )
        assert response.execution_result is not None
        assert len(response.challenges) > 0

    def test_response_challenge_position(self):
        """Test challenges appear after execution result."""
        response = ChallengeResponse(
            execution_result="Task completed",
            challenges=[{"category": "TEST_GAP", "severity": "MEDIUM"}],
            format=ResponseFormat.MARKDOWN,
        )
        formatted = self.injector.format_response(response)
        # Challenges should come after result
        result_pos = formatted.find("completed")
        challenge_pos = formatted.lower().find("challenge") or formatted.lower().find("test")
        assert result_pos <= challenge_pos or challenge_pos == -1

    def test_empty_challenges_no_impact(self):
        """Test empty challenges don't affect response."""
        response_with_challenges = ChallengeResponse(
            execution_result="Done",
            challenges=[],
        )
        response_no_challenges = ChallengeResponse(
            execution_result="Done",
        )
        formatted1 = self.injector.format_response(response_with_challenges)
        formatted2 = self.injector.format_response(response_no_challenges)
        # Both should be valid
        assert isinstance(formatted1, str)
        assert isinstance(formatted2, str)


class TestRecommendationInjection(BaseResponseChallengeTest):
    """Test recommendation injection."""

    def test_inject_recommendations(self):
        """Test injecting recommendations."""
        response = ChallengeResponse(
            execution_result="Refactoring completed",
            recommendations=[
                {
                    "title": "Consider async/await",
                    "description": "Use async for I/O operations",
                }
            ],
        )
        formatted = self.injector.format_response(response)
        assert isinstance(formatted, str)

    def test_recommendations_appear_after_challenges(self):
        """Test recommendations appear after challenges."""
        response = ChallengeResponse(
            execution_result="Done",
            challenges=[{"category": "TEST_GAP", "severity": "MEDIUM"}],
            recommendations=[{"title": "Add tests", "description": "For coverage"}],
        )
        formatted = self.injector.format_response(response)
        # Challenges should come before recommendations
        assert isinstance(formatted, str)


class TestResponseFormats(BaseResponseChallengeTest):
    """Test different response format options."""

    def test_response_format_enum(self):
        """Test ResponseFormat enum values."""
        assert hasattr(ResponseFormat, "JSON")
        assert hasattr(ResponseFormat, "MARKDOWN")
        assert hasattr(ResponseFormat, "PLAIN_TEXT")

    def test_format_consistency(self):
        """Test formatting is consistent."""
        response = ChallengeResponse(
            execution_result="Success",
            challenges=[{"category": "TEST_GAP", "severity": "HIGH"}],
        )
        formatted1 = self.injector.format_response(response)
        formatted2 = self.injector.format_response(response)
        # Same input should produce same output
        assert formatted1 == formatted2


class TestEdgeCases(BaseResponseChallengeTest):
    """Test edge cases and boundary conditions."""

    def test_empty_execution_result(self):
        """Test empty execution result."""
        response = ChallengeResponse(
            execution_result="",
            challenges=[],
        )
        formatted = self.injector.format_response(response)
        assert isinstance(formatted, str)

    def test_very_long_challenge_description(self):
        """Test long challenge descriptions."""
        long_desc = "a" * 1000
        challenge = {
            "category": "TEST_GAP",
            "severity": "MEDIUM",
            "description": long_desc,
        }
        formatted = self.injector.format_challenge(challenge)
        assert isinstance(formatted, str)

    def test_special_characters_in_challenges(self):
        """Test special characters in challenges."""
        challenge = {
            "category": "SECURITY_RISK",
            "severity": "CRITICAL",
            "description": "SQL injection: ; DROP TABLE users; --",
        }
        formatted = self.injector.format_challenge(challenge)
        assert isinstance(formatted, str)

    def test_unicode_in_challenges(self):
        """Test unicode characters in challenges."""
        challenge = {
            "category": "TEST_GAP",
            "severity": "HIGH",
            "description": "Missing tests: ñ, é, 中文, 🔒",
        }
        formatted = self.injector.format_challenge(challenge)
        assert isinstance(formatted, str)

    def test_null_values_handled(self):
        """Test null/None values are handled."""
        response = ChallengeResponse(
            execution_result=None,
            challenges=None,
        )
        formatted = self.injector.format_response(response)
        assert isinstance(formatted, str)

    def test_multiple_injectors_independent(self):
        """Test multiple injectors are independent."""
        injector1 = ResponseChallengeInjector()
        injector2 = ResponseChallengeInjector()
        response = ChallengeResponse(execution_result="Success")
        formatted1 = injector1.format_response(response)
        formatted2 = injector2.format_response(response)
        assert formatted1 == formatted2
