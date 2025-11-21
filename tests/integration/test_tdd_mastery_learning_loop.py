"""
Integration Tests for TDD Mastery Learning Loop - Phase 5.4

Tests the complete end-to-end learning loop with simplified integration focus.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import pytest
import json
from unittest.mock import Mock

from src.cortex_agents.test_generator.bug_driven_learner import (
    BugDrivenLearner,
    BugSeverity,
    BugCategory
)
from src.cortex_agents.test_generator.pattern_recommender import (
    PatternRecommender,
    FeedbackAction
)


@pytest.fixture
def mock_pattern_store():
    """Mock pattern store with simplified in-memory storage"""
    store = Mock()
    store.patterns = {}
    
    def store_pattern(**kwargs):
        pattern_id = kwargs.get('pattern_id')
        store.patterns[pattern_id] = {
            'id': pattern_id,
            'title': kwargs.get('title', ''),
            'category': kwargs.get('pattern_type', 'general'),
            'confidence': kwargs.get('confidence', 0.5),
            'namespace': kwargs.get('namespaces', ['cortex'])[0] if kwargs.get('namespaces') else 'cortex',
            'metadata': json.dumps(kwargs.get('metadata', {})),
            'tags': kwargs.get('metadata', {}).get('tags', [])
        }
        return {'success': True, 'pattern_id': pattern_id}
    
    def get_pattern(pattern_id):
        return store.patterns.get(pattern_id)
    
    def search_patterns(query, namespace, limit=100):
        results = []
        for pid, pattern in store.patterns.items():
            if pattern.get('namespace') == namespace or namespace == '*':
                results.append(pattern)
        return results[:limit]
    
    def update_pattern_confidence(pattern_id, new_confidence):
        if pattern_id in store.patterns:
            store.patterns[pattern_id]['confidence'] = new_confidence
            return True
        return False
    
    store.store_pattern = Mock(side_effect=store_pattern)
    store.get_pattern = Mock(side_effect=get_pattern)
    store.search_patterns = Mock(side_effect=search_patterns)
    store.update_pattern_confidence = Mock(side_effect=update_pattern_confidence)
    
    return store


class TestTDDMasteryLearningLoop:
    """Integration tests for TDD Mastery learning loop"""
    
    def test_complete_learning_loop(self, mock_pattern_store):
        """
        Test complete learning loop:
        Bug → Pattern Capture → Recommendation → Feedback → Improved Confidence
        """
        # Initialize components
        bug_learner = BugDrivenLearner(
            tier2_kg=None,
            pattern_store=mock_pattern_store
        )
        
        recommender = PatternRecommender(
            tier2_kg=None,
            pattern_store=mock_pattern_store,
            project_namespace="workspace.testapp"
        )
        
        # Step 1: Bug caught by test - capture pattern
        result = bug_learner.learn_from_bug(
            test_name='test_jwt_validation',
            test_file='tests/test_auth.py',
            bug_category=BugCategory.SECURITY,
            bug_severity=BugSeverity.HIGH,
            description='JWT token validation failed',
            expected_behavior='Token expires after configured time',
            actual_behavior='Token never expires',
            test_code='def test_jwt_validation():\n    assert validate_jwt(token)',
            root_cause='Missing expiration check',
            namespace='workspace.testapp'
        )
        
        # Verify pattern was stored
        assert result['stored'] is True
        pattern = result['pattern']
        pattern_id = pattern['pattern_id']
        assert pattern_id in mock_pattern_store.patterns
        
        # Step 2: Pattern available for recommendations
        stored_pattern = mock_pattern_store.patterns[pattern_id]
        assert stored_pattern['confidence'] == 0.85  # HIGH severity
        
        # Step 3: Get recommendations
        context = {'category': 'security', 'tags': ['jwt']}
        recommendations = recommender.recommend_patterns(
            context=context,
            limit=5,
            include_cortex_core=False
        )
        
        # Should find our pattern
        assert len(recommendations) >= 1
        rec = next((r for r in recommendations if r.pattern_id == pattern_id), None)
        assert rec is not None
        assert rec.confidence == 0.85
        
        # Step 4: User accepts recommendation
        feedback = recommender.record_feedback(
            recommendation_id=rec.recommendation_id,
            pattern_id=pattern_id,
            action=FeedbackAction.ACCEPT,
            comment="Helpful pattern!"
        )
        
        assert feedback.action == FeedbackAction.ACCEPT
        
        # Step 5: Confidence increased
        updated_pattern = mock_pattern_store.patterns[pattern_id]
        assert updated_pattern['confidence'] == 0.90  # 0.85 + 0.05
        
        print(f"✅ Learning loop complete: {pattern_id} confidence 0.85 → 0.90")
    
    def test_pattern_rejection_decreases_confidence(self, mock_pattern_store):
        """Test that rejecting a pattern decreases its confidence"""
        bug_learner = BugDrivenLearner(
            tier2_kg=None,
            pattern_store=mock_pattern_store
        )
        
        recommender = PatternRecommender(
            tier2_kg=None,
            pattern_store=mock_pattern_store,
            project_namespace="workspace.testapp"
        )
        
        # Capture pattern
        result = bug_learner.learn_from_bug(
            test_name='test_timeout',
            test_file='tests/test_db.py',
            bug_category=BugCategory.INTEGRATION,
            bug_severity=BugSeverity.MEDIUM,
            description='Database timeout',
            expected_behavior='Connection succeeds',
            actual_behavior='Connection times out',
            test_code='def test_timeout(): ...',
            namespace='workspace.testapp'
        )
        
        pattern_id = result['pattern']['pattern_id']
        assert mock_pattern_store.patterns[pattern_id]['confidence'] == 0.70
        
        # Get recommendation and reject
        context = {'category': 'integration'}
        recommendations = recommender.recommend_patterns(context, include_cortex_core=False)
        
        rec = next((r for r in recommendations if r.pattern_id == pattern_id), None)
        if rec:
            recommender.record_feedback(
                recommendation_id=rec.recommendation_id,
                pattern_id=pattern_id,
                action=FeedbackAction.REJECT
            )
            
            # Confidence decreased
            assert mock_pattern_store.patterns[pattern_id]['confidence'] == 0.60  # 0.70 - 0.10
    
    def test_pattern_modification_creates_variant(self, mock_pattern_store):
        """Test that modifying a pattern creates a variant"""
        bug_learner = BugDrivenLearner(
            tier2_kg=None,
            pattern_store=mock_pattern_store
        )
        
        recommender = PatternRecommender(
            tier2_kg=None,
            pattern_store=mock_pattern_store,
            project_namespace="workspace.testapp"
        )
        
        # Capture pattern
        result = bug_learner.learn_from_bug(
            test_name='test_rate_limit',
            test_file='tests/test_api.py',
            bug_category=BugCategory.SECURITY,
            bug_severity=BugSeverity.HIGH,
            description='Rate limit not enforced',
            expected_behavior='Requests blocked',
            actual_behavior='Unlimited requests',
            test_code='@rate_limit(100)\ndef endpoint(): ...',
            namespace='workspace.testapp'
        )
        
        original_id = result['pattern']['pattern_id']
        
        # Get recommendation and modify
        context = {'category': 'security'}
        recommendations = recommender.recommend_patterns(context, include_cortex_core=False)
        
        rec = next((r for r in recommendations if r.pattern_id == original_id), None)
        if rec:
            modified_code = '@rate_limit(50, window=60)\ndef endpoint(): ...'
            
            recommender.record_feedback(
                recommendation_id=rec.recommendation_id,
                pattern_id=original_id,
                action=FeedbackAction.MODIFY,
                modified_code=modified_code
            )
            
            # Variant created
            patterns = list(mock_pattern_store.patterns.values())
            variants = [p for p in patterns if 'variant' in p.get('id', '')]
            assert len(variants) >= 1
            
            print(f"✅ Variant created from pattern {original_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
