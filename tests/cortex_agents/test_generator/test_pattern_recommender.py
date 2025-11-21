"""
Tests for Pattern Recommender - Phase 5.3

Tests pattern recommendations, user feedback, confidence updates,
export/import functionality, and edge cases.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from src.cortex_agents.test_generator.pattern_recommender import (
    PatternRecommender,
    PatternRecommendation,
    UserFeedback,
    FeedbackAction,
    RecommendationSource
)


@pytest.fixture
def mock_tier2_kg():
    """Mock Tier 2 Knowledge Graph"""
    return Mock()


@pytest.fixture
def mock_pattern_store():
    """Mock pattern store with sample patterns"""
    store = Mock()
    
    # Sample patterns
    store.search_patterns = Mock(return_value=[
        {
            'id': 'auth_jwt_001',
            'title': 'JWT Authentication',
            'category': 'authentication',
            'description': 'JWT token-based authentication',
            'confidence': 0.85,
            'usage_count': 10,
            'metadata': json.dumps({
                'tags': ['security', 'jwt', 'api'],
                'code_sample': 'def verify_jwt_token(token): ...',
                'success_count': 8,
                'failure_count': 2
            })
        },
        {
            'id': 'auth_oauth_001',
            'title': 'OAuth2 Flow',
            'category': 'authentication',
            'description': 'OAuth2 authorization flow',
            'confidence': 0.75,
            'usage_count': 5,
            'metadata': json.dumps({
                'tags': ['security', 'oauth', 'api'],
                'code_sample': 'def oauth_authorize(): ...',
                'success_count': 4,
                'failure_count': 1
            })
        },
        {
            'id': 'db_connection_001',
            'title': 'Database Connection Pool',
            'category': 'database',
            'description': 'Connection pooling for database',
            'confidence': 0.90,
            'usage_count': 15,
            'metadata': json.dumps({
                'tags': ['database', 'pool', 'performance'],
                'code_sample': 'def get_db_connection(): ...',
                'success_count': 14,
                'failure_count': 1
            })
        }
    ])
    
    store.get_pattern = Mock(side_effect=lambda pid: {
        'auth_jwt_001': {
            'id': 'auth_jwt_001',
            'confidence': 0.85
        },
        'auth_oauth_001': {
            'id': 'auth_oauth_001',
            'confidence': 0.75
        }
    }.get(pid))
    
    store.update_pattern_confidence = Mock()
    store.store_pattern = Mock()
    
    return store


@pytest.fixture
def recommender(mock_tier2_kg, mock_pattern_store):
    """Create PatternRecommender instance"""
    return PatternRecommender(
        tier2_kg=mock_tier2_kg,
        pattern_store=mock_pattern_store,
        project_namespace="workspace.testapp"
    )


class TestPatternRecommender:
    """Test PatternRecommender class"""
    
    def test_init(self, recommender):
        """Test initialization"""
        assert recommender.project_namespace == "workspace.testapp"
        assert recommender.feedback_history == {}
    
    def test_recommend_patterns_auth_context(self, recommender, mock_pattern_store):
        """Test pattern recommendations for authentication context"""
        context = {
            'category': 'authentication',
            'tags': ['security', 'jwt', 'api']
        }
        
        recommendations = recommender.recommend_patterns(
            context=context,
            limit=5,
            include_cortex_core=False
        )
        
        # Should get at least one recommendation
        assert len(recommendations) >= 1
        
        # Authentication patterns should be present
        auth_patterns = [r for r in recommendations if r.pattern_category == 'authentication']
        assert len(auth_patterns) >= 1
        
        # JWT pattern should rank higher than OAuth (exact tag match)
        jwt_rec = next((r for r in recommendations if 'JWT' in r.pattern_title), None)
        assert jwt_rec is not None
        assert jwt_rec.relevance_score > 0
    
    def test_recommend_patterns_sorted_by_relevance(self, recommender):
        """Test recommendations are sorted by relevance"""
        context = {
            'category': 'authentication',
            'tags': ['security', 'jwt']
        }
        
        recommendations = recommender.recommend_patterns(
            context=context,
            limit=10,
            include_cortex_core=False
        )
        
        # Verify sorted in descending order
        for i in range(len(recommendations) - 1):
            assert recommendations[i].relevance_score >= recommendations[i + 1].relevance_score
    
    def test_recommend_patterns_limit(self, recommender):
        """Test recommendation limit"""
        context = {'category': 'authentication'}
        
        recommendations = recommender.recommend_patterns(
            context=context,
            limit=2,
            include_cortex_core=False
        )
        
        assert len(recommendations) <= 2
    
    def test_recommend_patterns_min_confidence(self, recommender, mock_pattern_store):
        """Test minimum confidence filter"""
        context = {'category': 'authentication'}
        
        recommendations = recommender.recommend_patterns(
            context=context,
            min_confidence=0.8,
            include_cortex_core=False
        )
        
        # Only patterns with confidence >= 0.8 should be returned
        assert all(r.confidence >= 0.8 for r in recommendations)
    
    def test_relevance_scoring_category_match(self, recommender):
        """Test relevance scoring with category match"""
        context = {
            'category': 'authentication',
            'tags': []
        }
        
        recommendations = recommender.recommend_patterns(
            context=context,
            limit=5,
            include_cortex_core=False
        )
        
        # Category matches should have higher relevance
        auth_recs = [r for r in recommendations if r.pattern_category == 'authentication']
        db_recs = [r for r in recommendations if r.pattern_category == 'database']
        
        if auth_recs and db_recs:
            assert auth_recs[0].relevance_score > db_recs[0].relevance_score
    
    def test_relevance_scoring_tag_overlap(self, recommender):
        """Test relevance scoring with tag overlap"""
        context = {
            'category': 'authentication',
            'tags': ['security', 'jwt', 'api']
        }
        
        recommendations = recommender.recommend_patterns(
            context=context,
            limit=5,
            include_cortex_core=False
        )
        
        # JWT pattern should rank highest (all 3 tags match)
        jwt_rec = next((r for r in recommendations if 'JWT' in r.pattern_title), None)
        oauth_rec = next((r for r in recommendations if 'OAuth' in r.pattern_title), None)
        
        if jwt_rec and oauth_rec:
            assert jwt_rec.relevance_score > oauth_rec.relevance_score
    
    def test_relevance_scoring_current_project_boost(self, recommender):
        """Test 20% boost for current project patterns"""
        pattern = {
            'id': 'test_001',
            'title': 'Test Pattern',
            'category': 'testing',
            'confidence': 0.7,
            'metadata': json.dumps({
                'tags': ['test'],
                'success_count': 5,
                'failure_count': 0
            })
        }
        
        context = {'category': 'testing', 'tags': ['test']}
        
        # Create recommendations from different sources
        rec_project = recommender._create_recommendation(
            pattern,
            RecommendationSource.CURRENT_PROJECT,
            context
        )
        
        rec_core = recommender._create_recommendation(
            pattern,
            RecommendationSource.CORTEX_CORE,
            context
        )
        
        # Calculate relevance
        score_project = recommender._calculate_relevance_score(rec_project, context)
        score_core = recommender._calculate_relevance_score(rec_core, context)
        
        # Project pattern should have 20% higher score
        assert score_project > score_core
    
    def test_record_feedback_accept(self, recommender, mock_pattern_store):
        """Test recording ACCEPT feedback"""
        feedback = recommender.record_feedback(
            recommendation_id="rec_123",
            pattern_id="auth_jwt_001",
            action=FeedbackAction.ACCEPT,
            comment="Very helpful!"
        )
        
        assert feedback.action == FeedbackAction.ACCEPT
        assert feedback.pattern_id == "auth_jwt_001"
        assert feedback.comment == "Very helpful!"
        
        # Verify feedback stored
        assert "auth_jwt_001" in recommender.feedback_history
        assert len(recommender.feedback_history["auth_jwt_001"]) == 1
        
        # Verify confidence updated
        mock_pattern_store.update_pattern_confidence.assert_called_once()
    
    def test_record_feedback_reject(self, recommender, mock_pattern_store):
        """Test recording REJECT feedback"""
        feedback = recommender.record_feedback(
            recommendation_id="rec_123",
            pattern_id="auth_oauth_001",
            action=FeedbackAction.REJECT,
            comment="Not relevant"
        )
        
        assert feedback.action == FeedbackAction.REJECT
        
        # Verify confidence decreased
        mock_pattern_store.update_pattern_confidence.assert_called_once()
    
    def test_record_feedback_modify(self, recommender, mock_pattern_store):
        """Test recording MODIFY feedback"""
        modified_code = "def custom_jwt_verify(): ..."
        
        feedback = recommender.record_feedback(
            recommendation_id="rec_123",
            pattern_id="auth_jwt_001",
            action=FeedbackAction.MODIFY,
            modified_code=modified_code
        )
        
        assert feedback.action == FeedbackAction.MODIFY
        assert feedback.modified_code == modified_code
        
        # Verify pattern variant created
        mock_pattern_store.store_pattern.assert_called_once()
    
    def test_confidence_update_accept(self, recommender, mock_pattern_store):
        """Test confidence increases on ACCEPT"""
        initial_confidence = 0.85
        
        recommender.record_feedback(
            recommendation_id="rec_123",
            pattern_id="auth_jwt_001",
            action=FeedbackAction.ACCEPT
        )
        
        # Verify confidence increased by 0.05
        call_args = mock_pattern_store.update_pattern_confidence.call_args
        assert call_args[0][0] == "auth_jwt_001"
        assert call_args[0][1] == min(1.0, initial_confidence + 0.05)
    
    def test_confidence_update_reject(self, recommender, mock_pattern_store):
        """Test confidence decreases on REJECT"""
        initial_confidence = 0.75
        
        recommender.record_feedback(
            recommendation_id="rec_123",
            pattern_id="auth_oauth_001",
            action=FeedbackAction.REJECT
        )
        
        # Verify confidence decreased by 0.10
        call_args = mock_pattern_store.update_pattern_confidence.call_args
        assert call_args[0][0] == "auth_oauth_001"
        assert call_args[0][1] == max(0.0, initial_confidence - 0.10)
    
    def test_confidence_capped_at_1(self, recommender, mock_pattern_store):
        """Test confidence doesn't exceed 1.0"""
        mock_pattern_store.get_pattern = Mock(return_value={
            'id': 'test_001',
            'confidence': 0.98
        })
        
        recommender.record_feedback(
            recommendation_id="rec_123",
            pattern_id="test_001",
            action=FeedbackAction.ACCEPT
        )
        
        # Confidence should be capped at 1.0
        call_args = mock_pattern_store.update_pattern_confidence.call_args
        assert call_args[0][1] == 1.0
    
    def test_feedback_summary(self, recommender):
        """Test feedback summary generation"""
        pattern_id = "auth_jwt_001"
        
        # Add multiple feedbacks
        recommender.record_feedback("rec_1", pattern_id, FeedbackAction.ACCEPT)
        recommender.record_feedback("rec_2", pattern_id, FeedbackAction.ACCEPT)
        recommender.record_feedback("rec_3", pattern_id, FeedbackAction.REJECT)
        recommender.record_feedback("rec_4", pattern_id, FeedbackAction.MODIFY)
        
        summary = recommender.get_feedback_summary(pattern_id)
        
        assert summary['total_feedbacks'] == 4
        assert summary['accept_rate'] == 0.5  # 2/4
        assert summary['reject_rate'] == 0.25  # 1/4
        assert summary['modify_rate'] == 0.25  # 1/4
        assert len(summary['recent_feedbacks']) == 4
    
    def test_feedback_summary_no_feedback(self, recommender):
        """Test feedback summary with no feedback"""
        summary = recommender.get_feedback_summary("nonexistent_pattern")
        
        assert summary['total_feedbacks'] == 0
        assert summary['accept_rate'] == 0.0
    
    def test_accept_rate_influences_relevance(self, recommender):
        """Test accept rate influences relevance scoring"""
        pattern_id = "auth_jwt_001"
        
        # Add positive feedback
        recommender.record_feedback("rec_1", pattern_id, FeedbackAction.ACCEPT)
        recommender.record_feedback("rec_2", pattern_id, FeedbackAction.ACCEPT)
        
        context = {
            'category': 'authentication',
            'tags': ['security', 'jwt']
        }
        
        recommendations = recommender.recommend_patterns(context, limit=5, include_cortex_core=False)
        
        jwt_rec = next((r for r in recommendations if r.pattern_id == pattern_id), None)
        assert jwt_rec is not None
        
        # Relevance should be boosted by high accept rate
        assert jwt_rec.relevance_score > 0.5
    
    def test_export_patterns(self, recommender, mock_pattern_store):
        """Test pattern export"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = f.name
        
        try:
            success = recommender.export_patterns(output_path, format='json')
            assert success
            
            # Verify export file
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            assert data['project_namespace'] == "workspace.testapp"
            assert 'patterns' in data
            assert 'feedback' in data
            assert 'exported_at' in data
            
        finally:
            Path(output_path).unlink()
    
    def test_import_patterns_skip_existing(self, recommender, mock_pattern_store):
        """Test pattern import with skip strategy"""
        # Create sample import file
        import_data = {
            'project_namespace': 'workspace.other',
            'patterns': [
                {
                    'id': 'auth_jwt_001',
                    'title': 'JWT Auth',
                    'category': 'auth',
                    'confidence': 0.9
                },
                {
                    'id': 'new_pattern_001',
                    'title': 'New Pattern',
                    'category': 'test',
                    'confidence': 0.7
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(import_data, f)
            import_path = f.name
        
        try:
            result = recommender.import_patterns(import_path, merge_strategy='skip')
            
            assert result['total'] == 2
            assert result['imported'] == 1  # Only new_pattern_001
            assert result['skipped'] == 1  # auth_jwt_001 exists
            
        finally:
            Path(import_path).unlink()
    
    def test_import_patterns_merge(self, recommender, mock_pattern_store):
        """Test pattern import with merge strategy"""
        import_data = {
            'patterns': [
                {
                    'id': 'auth_jwt_001',
                    'title': 'JWT Auth',
                    'category': 'auth',
                    'confidence': 0.9
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(import_data, f)
            import_path = f.name
        
        try:
            result = recommender.import_patterns(import_path, merge_strategy='merge')
            
            assert result['updated'] == 1
            
            # Verify merged confidence (average)
            call_args = mock_pattern_store.store_pattern.call_args
            stored_pattern = call_args[1]['pattern_data']
            assert stored_pattern['confidence'] == (0.85 + 0.9) / 2
            
        finally:
            Path(import_path).unlink()
    
    def test_empty_recommendations_no_patterns(self, recommender, mock_pattern_store):
        """Test empty recommendations when no patterns match"""
        mock_pattern_store.search_patterns = Mock(return_value=[])
        
        context = {'category': 'testing'}
        recommendations = recommender.recommend_patterns(context, include_cortex_core=False)
        
        assert len(recommendations) == 0
    
    def test_pattern_variant_creation(self, recommender, mock_pattern_store):
        """Test creation of pattern variant on MODIFY"""
        modified_code = "def modified_jwt(): pass"
        
        recommender.record_feedback(
            recommendation_id="rec_123",
            pattern_id="auth_jwt_001",
            action=FeedbackAction.MODIFY,
            modified_code=modified_code
        )
        
        # Verify variant created
        call_args = mock_pattern_store.store_pattern.call_args
        variant_data = call_args[1]['pattern_data']
        
        assert 'variant' in variant_data['id']
        assert variant_data['confidence'] == 0.6  # Initial variant confidence
        assert 'original_pattern_id' in json.loads(variant_data['metadata'])
    
    def test_success_rate_calculation(self, recommender):
        """Test success rate calculation from pattern metadata"""
        pattern = {
            'id': 'test_001',
            'metadata': json.dumps({
                'success_count': 8,
                'failure_count': 2
            })
        }
        
        success_rate = recommender._calculate_success_rate(pattern)
        assert success_rate == 0.8  # 8/10
    
    def test_success_rate_no_data(self, recommender):
        """Test success rate defaults to 0.5 with no data"""
        pattern = {
            'id': 'test_001',
            'metadata': json.dumps({})
        }
        
        success_rate = recommender._calculate_success_rate(pattern)
        assert success_rate == 0.5  # Default


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
