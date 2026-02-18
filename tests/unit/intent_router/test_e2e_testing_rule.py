"""
Tests for E2ETestingRule.

Authority: AC-GOLDEN-E2E-007
TDD Phase: RED → GREEN
"""

import pytest

from cortex.brain.intent_router.e2e_testing_rule import E2ETestingRule
from cortex.brain.intent_router.classifier import IntentCategory, IntentSignal


class TestE2ETestingRule:
    """Test E2E testing intent classification rule."""
    
    @pytest.fixture
    def rule(self) -> E2ETestingRule:
        """Create E2E testing rule instance."""
        return E2ETestingRule()
    
    def test_rule_exists(self):
        """E2ETestingRule should exist."""
        rule = E2ETestingRule()
        assert rule is not None
    
    def test_rule_is_classification_rule(self, rule: E2ETestingRule):
        """E2ETestingRule should implement ClassificationRule interface."""
        from cortex.brain.intent_router.classifier import ClassificationRule
        assert isinstance(rule, ClassificationRule)
    
    def test_matches_golden_tests(self, rule: E2ETestingRule):
        """Should match 'golden tests' utterance."""
        assert rule.matches("golden tests") is True
    
    def test_matches_golden_test_singular(self, rule: E2ETestingRule):
        """Should match 'golden test' (singular)."""
        assert rule.matches("golden test") is True
    
    def test_matches_e2e_tests(self, rule: E2ETestingRule):
        """Should match 'e2e tests'."""
        assert rule.matches("e2e tests") is True
    
    def test_matches_e2e_test_singular(self, rule: E2ETestingRule):
        """Should match 'e2e test'."""
        assert rule.matches("e2e test") is True
    
    def test_matches_end_to_end_tests(self, rule: E2ETestingRule):
        """Should match 'end-to-end tests'."""
        assert rule.matches("end-to-end tests") is True
    
    def test_matches_end_to_end_hyphen(self, rule: E2ETestingRule):
        """Should match 'end-to-end' with hyphens."""
        assert rule.matches("run end-to-end test") is True
    
    def test_matches_end_to_end_spaces(self, rule: E2ETestingRule):
        """Should match 'end to end' with spaces."""
        assert rule.matches("run end to end test") is True
    
    def test_matches_golden_test_harness(self, rule: E2ETestingRule):
        """Should match 'golden test harness'."""
        assert rule.matches("golden test harness") is True
    
    def test_matches_case_insensitive(self, rule: E2ETestingRule):
        """Should match case-insensitively."""
        assert rule.matches("GOLDEN TESTS") is True
        assert rule.matches("Golden Tests") is True
        assert rule.matches("E2E TESTS") is True
    
    def test_matches_in_sentence(self, rule: E2ETestingRule):
        """Should match pattern within larger sentence."""
        assert rule.matches("run the golden tests for authentication") is True
        assert rule.matches("execute e2e tests now") is True
    
    def test_does_not_match_unrelated_text(self, rule: E2ETestingRule):
        """Should not match unrelated text."""
        assert rule.matches("implement user authentication") is False
        assert rule.matches("fix the login bug") is False
        assert rule.matches("analyze performance") is False
    
    def test_does_not_match_partial_words(self, rule: E2ETestingRule):
        """Should not match partial words."""
        assert rule.matches("goldening") is False
        assert rule.matches("testify") is False
    
    def test_get_intent_returns_test(self, rule: E2ETestingRule):
        """get_intent should return TEST category."""
        assert rule.get_intent() == IntentCategory.TEST
    
    def test_get_signal_strength_high_confidence(self, rule: E2ETestingRule):
        """get_signal_strength should return high confidence."""
        strength = rule.get_signal_strength()
        assert strength >= 0.90  # At least 90% confidence
        assert strength <= 1.0   # Max 100%
    
    def test_get_signals_returns_imperative(self, rule: E2ETestingRule):
        """get_signals should return IMPERATIVE signal."""
        signals = rule.get_signals()
        assert IntentSignal.IMPERATIVE in signals
    
    def test_get_keywords(self, rule: E2ETestingRule):
        """get_keywords should return E2E testing keywords."""
        keywords = rule.get_keywords()
        assert "golden" in keywords
        assert "e2e" in keywords
        assert "test" in keywords
