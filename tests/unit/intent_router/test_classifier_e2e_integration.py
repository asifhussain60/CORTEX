"""
Tests for IntentClassifier with E2E rule integration.

Authority: AC-GOLDEN-E2E-016
"""

import pytest

from cortex.brain.intent_router.classifier import IntentClassifier, IntentCategory


class TestIntentClassifierE2EIntegration:
    """Test IntentClassifier with E2E testing rule."""
    
    @pytest.fixture
    def classifier(self) -> IntentClassifier:
        """Create classifier instance."""
        return IntentClassifier()
    
    def test_classifier_has_custom_rules(self, classifier: IntentClassifier):
        """Classifier should have custom_rules list."""
        assert hasattr(classifier, 'custom_rules')
        assert isinstance(classifier.custom_rules, list)
    
    def test_classifier_registers_e2e_rule_by_default(self, classifier: IntentClassifier):
        """Classifier should auto-register E2E testing rule."""
        # Should have at least one rule (E2ETestingRule)
        assert len(classifier.custom_rules) >= 1
    
    def test_classifier_detects_golden_tests_intent(self, classifier: IntentClassifier):
        """Classifier should detect 'golden tests' as TEST intent with high confidence."""
        result = classifier.classify("golden tests")
        
        assert result.primary_intent == IntentCategory.TEST
        assert result.confidence_score >= 0.95  # E2E rule has 0.95 confidence
    
    def test_classifier_detects_e2e_tests_intent(self, classifier: IntentClassifier):
        """Classifier should detect 'e2e tests' as TEST intent."""
        result = classifier.classify("run e2e tests")
        
        assert result.primary_intent == IntentCategory.TEST
        assert result.confidence_score >= 0.95
    
    def test_classifier_detects_end_to_end_tests(self, classifier: IntentClassifier):
        """Classifier should detect 'end-to-end tests'."""
        result = classifier.classify("execute end-to-end tests")
        
        assert result.primary_intent == IntentCategory.TEST
        assert result.confidence_score >= 0.95
    
    def test_rule_takes_precedence_over_keywords(self, classifier: IntentClassifier):
        """Custom rule should take precedence over keyword matching."""
        # "golden tests" might match CREATE keywords too
        # But E2E rule should win
        result = classifier.classify("create golden tests")
        
        assert result.primary_intent == IntentCategory.TEST
        # Should indicate rule match in metadata
        assert 'rule_matched' in result.metadata
        assert result.metadata['rule_matched'] == 'E2ETestingRule'
    
    def test_normal_test_keyword_uses_keyword_matching(self, classifier: IntentClassifier):
        """Normal test keywords should use standard keyword matching."""
        result = classifier.classify("write unit tests")
        
        # Should classify as TEST but not via E2E rule
        assert result.primary_intent == IntentCategory.TEST
        # Should NOT have rule_matched in metadata
        assert 'rule_matched' not in result.metadata or result.metadata.get('rule_matched') is None
    
    def test_add_rule_method_works(self, classifier: IntentClassifier):
        """add_rule method should allow adding custom rules."""
        from cortex.brain.intent_router.classifier import ClassificationRule, IntentSignal
        
        class TestRule(ClassificationRule):
            def matches(self, text: str) -> bool:
                return "test_pattern" in text
            
            def get_intent(self) -> IntentCategory:
                return IntentCategory.ANALYZE
            
            def get_signal_strength(self) -> float:
                return 0.99
            
            def get_signals(self) -> list:
                return [IntentSignal.IMPERATIVE]
        
        initial_count = len(classifier.custom_rules)
        classifier.add_rule(TestRule())
        
        assert len(classifier.custom_rules) == initial_count + 1
    
    def test_custom_rule_precedence(self, classifier: IntentClassifier):
        """Custom rules should be checked before keyword matching."""
        from cortex.brain.intent_router.classifier import ClassificationRule, IntentSignal
        
        class HighPriorityRule(ClassificationRule):
            def matches(self, text: str) -> bool:
                return "special_keyword" in text
            
            def get_intent(self) -> IntentCategory:
                return IntentCategory.OPTIMIZE
            
            def get_signal_strength(self) -> float:
                return 1.0
            
            def get_signals(self) -> list:
                return [IntentSignal.IMPERATIVE]
        
        classifier.add_rule(HighPriorityRule())
        
        result = classifier.classify("special_keyword implementation")
        
        # Should match custom rule even though "implementation" suggests CREATE
        assert result.primary_intent == IntentCategory.OPTIMIZE
        assert result.confidence_score == 1.0
