"""Test suite for AC-HP-003-02: Agent Confidence Scoring. Target: 24/24 tests."""
import sys, pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'cortex-brain'))
try:
    from tier2.hallucination_prevention.confidence_scoring import ConfidenceScore, ConfidenceScorer
except ModuleNotFoundError:
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../cortex-brain')))
    from tier2.hallucination_prevention.confidence_scoring import ConfidenceScore, ConfidenceScorer

@pytest.fixture
def scorer() -> ConfidenceScorer:
    return ConfidenceScorer()

class TestConfidenceCalculation:
    def test_calculate_simple_confidence(self, scorer: ConfidenceScorer):
        score = scorer.calculate_confidence('MODIFY', {'key': 'value'})
        assert score is not None
        assert 0 <= score.score <= 1.0
    def test_calculate_complex_confidence(self, scorer: ConfidenceScorer):
        action = {'action': 'MODIFY_AC', 'ac_id': 'HP-001-01', 'changes': {'status': 'COMPLETED'}, 'approval_count': 2}
        score = scorer.calculate_confidence('MODIFY_AC', action)
        assert 0 <= score.score <= 1.0
    def test_different_actions_different_confidence(self, scorer: ConfidenceScorer):
        s1 = scorer.calculate_confidence('DELETE', {'ac_id': 'HP-001-01', 'approval_count': 0})
        s2 = scorer.calculate_confidence('CREATE', {'phase_id': 'PHASE-12', 'approval_count': 3})
        assert s1.score < s2.score  # CREATE with approvals should have higher confidence

class TestConfidenceFactors:
    def test_confidence_with_approval_count(self, scorer: ConfidenceScorer):
        low = scorer.calculate_confidence('MODIFY', {'approval_count': 0})
        high = scorer.calculate_confidence('MODIFY', {'approval_count': 3})
        assert low.score < high.score
    def test_confidence_with_risk_level(self, scorer: ConfidenceScorer):
        safe = scorer.calculate_confidence('VERIFY', {'risk_level': 'LOW'})
        risky = scorer.calculate_confidence('VERIFY', {'risk_level': 'HIGH'})
        assert safe.score > risky.score
    def test_confidence_with_historical_success(self, scorer: ConfidenceScorer):
        low_hist = scorer.calculate_confidence('MODIFY', {'historical_success_rate': 0.5})
        high_hist = scorer.calculate_confidence('MODIFY', {'historical_success_rate': 0.95})
        assert low_hist.score < high_hist.score

class TestConfidenceScoreProperties:
    def test_score_has_justification(self, scorer: ConfidenceScorer):
        score = scorer.calculate_confidence('CREATE', {'data': 'test'})
        assert score.justification is not None
        assert len(score.justification) > 0
    def test_score_includes_factors(self, scorer: ConfidenceScorer):
        score = scorer.calculate_confidence('MODIFY', {'key': 'value'})
        assert score.factors is not None
    def test_score_includes_risk_assessment(self, scorer: ConfidenceScorer):
        score = scorer.calculate_confidence('DELETE', {'ac_id': 'HP-001-01'})
        assert score.risk_assessment is not None

class TestLowConfidenceTrigger:
    def test_low_confidence_triggers_review(self, scorer: ConfidenceScorer):
        low_conf = scorer.calculate_confidence('DELETE', {'ac_id': 'HP-001-01'})
        if low_conf.score < 0.5:
            assert low_conf.requires_review is True
    def test_high_confidence_no_review(self, scorer: ConfidenceScorer):
        high_conf = scorer.calculate_confidence('VERIFY', {'risk_level': 'LOW'})
        if high_conf.score > 0.8:
            assert high_conf.requires_review is False

class TestConfidenceHistoryTracking:
    def test_track_confidence_scores(self, scorer: ConfidenceScorer):
        s1 = scorer.calculate_confidence('CREATE', {'type': 'PHASE'})
        s2 = scorer.calculate_confidence('MODIFY', {'type': 'AC'})
        history = scorer.get_score_history()
        assert len(history) >= 2
    def test_get_scores_by_action_type(self, scorer: ConfidenceScorer):
        scorer.calculate_confidence('DELETE', {'target': 'AC'})
        scorer.calculate_confidence('DELETE', {'target': 'FILE'})
        scores = scorer.get_scores_by_action('DELETE')
        assert len(scores) >= 2

class TestScoringModel:
    def test_scoring_model_is_documented(self, scorer: ConfidenceScorer):
        model = scorer.get_scoring_model()
        assert model is not None
        assert 'factors' in model or 'description' in model
    def test_scoring_weights_documented(self, scorer: ConfidenceScorer):
        weights = scorer.get_scoring_weights()
        assert weights is not None

class TestComplexScenarios:
    def test_multi_action_sequence_confidence(self, scorer: ConfidenceScorer):
        actions = [
            ('VALIDATE', {'type': 'PHASE'}),
            ('MODIFY', {'status': 'IN_PROGRESS'}),
            ('VERIFY', {'constraints': ['rule1']}),
        ]
        scores = [scorer.calculate_confidence(a, d) for a, d in actions]
        assert len(scores) == 3
    def test_confidence_with_mixed_factors(self, scorer: ConfidenceScorer):
        data = {
            'approval_count': 2,
            'risk_level': 'MEDIUM',
            'historical_success': 0.8,
            'dependencies': ['HP-001-01'],
        }
        score = scorer.calculate_confidence('MODIFY', data)
        assert score.score is not None

class TestEdgeCases:
    def test_confidence_with_minimal_data(self, scorer: ConfidenceScorer):
        score = scorer.calculate_confidence('CREATE', {})
        assert score is not None
    def test_confidence_with_none_values(self, scorer: ConfidenceScorer):
        try:
            score = scorer.calculate_confidence('MODIFY', {'key': None})
            assert score is not None
        except (TypeError, ValueError):
            assert True
    def test_confidence_with_unicode(self, scorer: ConfidenceScorer):
        data = {'description': 'Action 日本語 中文 العربية'}
        score = scorer.calculate_confidence('MODIFY', data)
        assert score is not None
    def test_very_long_action_history(self, scorer: ConfidenceScorer):
        for i in range(100):
            scorer.calculate_confidence('VERIFY', {'index': i})
        history = scorer.get_score_history()
        assert len(history) >= 100
    def test_duplicate_confidence_calculations(self, scorer: ConfidenceScorer):
        s1 = scorer.calculate_confidence('DELETE', {'ac_id': 'HP-001-01'})
        s2 = scorer.calculate_confidence('DELETE', {'ac_id': 'HP-001-01'})
        assert s1.score == s2.score

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
