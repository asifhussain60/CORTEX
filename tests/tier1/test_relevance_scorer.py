"""
Tests for Relevance Scorer

Tests entity overlap, temporal proximity, topic similarity, and work continuity scoring.
"""

import pytest
from datetime import datetime, timedelta
from src.tier1.relevance_scorer import RelevanceScorer


class TestScoreConversationRelevance:
    """Test overall relevance scoring."""
    
    def test_scores_high_for_matching_entities(self):
        """Should score high when entities match"""
        scorer = RelevanceScorer()
        
        conversation = {
            'title': 'Fix bug in AuthService.cs',
            'summary': 'Fixed getUserById method',
            'created_at': datetime.now().isoformat(),
            'metadata': {
                'files': ['AuthService.cs'],
                'classes': ['AuthService'],
                'methods': ['getUserById']
            }
        }
        
        score = scorer.score_conversation_relevance(
            conversation,
            current_request="Update the getUserById method in AuthService",
            current_file="/project/src/AuthService.cs",
            active_entities={'files': ['AuthService.cs'], 'methods': ['getUserById']}
        )
        
        assert score > 0.7  # High relevance due to entity matches
    
    def test_scores_low_for_unrelated_conversation(self):
        """Should score low when conversation is unrelated"""
        scorer = RelevanceScorer()
        
        conversation = {
            'title': 'Add button to dashboard',
            'summary': 'Created purple button',
            'created_at': (datetime.now() - timedelta(days=30)).isoformat(),
            'metadata': {
                'files': ['Dashboard.cs'],
                'ui_components': ['button']
            }
        }
        
        score = scorer.score_conversation_relevance(
            conversation,
            current_request="Fix authentication bug",
            current_file="/project/src/AuthService.cs"
        )
        
        assert score < 0.3  # Low relevance - different topic and old
    
    def test_combines_all_scoring_factors(self):
        """Should combine entity, temporal, topic, and continuity scores"""
        scorer = RelevanceScorer()
        
        conversation = {
            'title': 'Implement authentication',
            'summary': 'Added login with JWT tokens',
            'created_at': datetime.now().isoformat(),
            'metadata': {
                'files': ['AuthService.cs'],
                'classes': ['AuthService']
            }
        }
        
        score = scorer.score_conversation_relevance(
            conversation,
            current_request="Continue working on authentication system",
            current_file="/project/src/AuthService.cs"
        )
        
        # Should score high: entity match + recent + topic match + continuation
        assert score > 0.8


class TestCalculateEntityOverlap:
    """Test entity overlap scoring."""
    
    def test_scores_high_for_exact_file_match(self):
        """Should give high score when files match exactly"""
        scorer = RelevanceScorer()
        
        conv_entities = {
            'files': {'AuthService.cs'},
            'classes': set(),
            'methods': set(),
            'ui_components': set()
        }
        
        score = scorer._calculate_entity_overlap(
            conv_entities,
            "Update AuthService",
            current_file="/project/src/AuthService.cs",
            active_entities=None
        )
        
        assert score >= 0.5  # File matches are weighted heavily
    
    def test_scores_zero_for_no_overlap(self):
        """Should return zero when no entities match"""
        scorer = RelevanceScorer()
        
        conv_entities = {
            'files': {'Dashboard.cs'},
            'classes': set(),
            'methods': set(),
            'ui_components': set()
        }
        
        score = scorer._calculate_entity_overlap(
            conv_entities,
            "Fix login bug",
            current_file=None,
            active_entities=None
        )
        
        assert score == 0.0
    
    def test_matches_entities_in_request_text(self):
        """Should detect entities mentioned in request"""
        scorer = RelevanceScorer()
        
        conv_entities = {
            'files': set(),
            'classes': {'AuthService'},
            'methods': {'getUserById'},
            'ui_components': set()
        }
        
        score = scorer._calculate_entity_overlap(
            conv_entities,
            "The getUserById method in AuthService needs updating",
            current_file=None,
            active_entities=None
        )
        
        assert score > 0.5  # Both class and method mentioned
    
    def test_matches_active_entities(self):
        """Should match against active entities from recent work"""
        scorer = RelevanceScorer()
        
        conv_entities = {
            'files': {'AuthService.cs'},
            'classes': {'AuthService'},
            'methods': {'getUserById'},
            'ui_components': set()
        }
        
        score = scorer._calculate_entity_overlap(
            conv_entities,
            "Update authentication",
            current_file=None,
            active_entities={
                'files': ['AuthService.cs'],
                'classes': ['AuthService'],
                'methods': ['getUserById']
            }
        )
        
        assert score > 0.8  # All entities match


class TestCalculateTemporalProximity:
    """Test temporal proximity scoring."""
    
    def test_scores_full_for_recent_conversations(self):
        """Should return 1.0 for conversations within 24 hours"""
        scorer = RelevanceScorer()
        
        recent_time = datetime.now() - timedelta(hours=12)
        score = scorer._calculate_temporal_proximity(recent_time.isoformat())
        
        assert score == 1.0
    
    def test_applies_decay_for_older_conversations(self):
        """Should apply exponential decay for conversations older than 24h"""
        scorer = RelevanceScorer()
        
        # 7 days old = one half-life
        old_time = datetime.now() - timedelta(days=7)
        score = scorer._calculate_temporal_proximity(old_time.isoformat())
        
        assert 0.4 <= score <= 0.6  # Should be around 0.5
    
    def test_scores_very_low_for_very_old_conversations(self):
        """Should score very low for conversations months old"""
        scorer = RelevanceScorer()
        
        very_old_time = datetime.now() - timedelta(days=60)
        score = scorer._calculate_temporal_proximity(very_old_time.isoformat())
        
        assert score < 0.1  # Very low score for 60+ days
    
    def test_handles_missing_timestamp(self):
        """Should return 0.0 for missing timestamps"""
        scorer = RelevanceScorer()
        
        score = scorer._calculate_temporal_proximity(None)
        assert score == 0.0
    
    def test_handles_datetime_objects(self):
        """Should handle datetime objects as well as strings"""
        scorer = RelevanceScorer()
        
        recent_time = datetime.now() - timedelta(hours=12)
        score = scorer._calculate_temporal_proximity(recent_time)
        
        assert score == 1.0


class TestCalculateTopicSimilarity:
    """Test topic similarity scoring."""
    
    def test_scores_high_for_matching_keywords(self):
        """Should score high when keywords match"""
        scorer = RelevanceScorer()
        
        conv_text = "Implement user authentication with JWT tokens and login form"
        current_request = "Continue working on authentication system"
        
        score = scorer._calculate_topic_similarity(conv_text, current_request)
        
        assert score > 0.3  # 'authentication' keyword matches
    
    def test_scores_zero_for_no_keyword_match(self):
        """Should score low when no keywords match"""
        scorer = RelevanceScorer()
        
        conv_text = "Add purple button to dashboard"
        current_request = "Fix database migration script"
        
        score = scorer._calculate_topic_similarity(conv_text, current_request)
        
        assert score < 0.2  # No meaningful overlap
    
    def test_detects_topic_categories(self):
        """Should detect and match topic categories"""
        scorer = RelevanceScorer()
        
        conv_text = "Fix authentication bug with login tokens"
        current_request = "Debug JWT token validation issue"
        
        score = scorer._calculate_topic_similarity(conv_text, current_request)
        
        # Both mention authentication-related topics
        assert score >= 0.4
    
    def test_handles_empty_text(self):
        """Should handle empty text gracefully"""
        scorer = RelevanceScorer()
        
        score = scorer._calculate_topic_similarity("", "test request")
        assert score == 0.0
        
        score = scorer._calculate_topic_similarity("test text", "")
        assert score == 0.0


class TestCalculateWorkContinuity:
    """Test work continuity scoring."""
    
    def test_scores_high_for_same_file(self):
        """Should score high when working on same file"""
        scorer = RelevanceScorer()
        
        conversation = {
            'metadata': {
                'files': ['AuthService.cs']
            }
        }
        
        score = scorer._calculate_work_continuity(
            conversation,
            "Update authentication logic",
            current_file="/project/src/AuthService.cs"
        )
        
        assert score >= 0.5
    
    def test_detects_continuation_phrases(self):
        """Should detect continuation phrases in request"""
        scorer = RelevanceScorer()
        
        conversation = {'metadata': {}}
        
        continuation_requests = [
            "continue working on authentication",
            "resume the implementation",
            "finish the login feature",
            "complete the setup",
            "keep working on the bug fix"
        ]
        
        for request in continuation_requests:
            score = scorer._calculate_work_continuity(
                conversation,
                request,
                current_file=None
            )
            assert score >= 0.5, f"Failed to detect continuation in: {request}"
    
    def test_scores_zero_for_unrelated_work(self):
        """Should score zero when no continuity detected"""
        scorer = RelevanceScorer()
        
        conversation = {
            'metadata': {
                'files': ['Dashboard.cs']
            }
        }
        
        score = scorer._calculate_work_continuity(
            conversation,
            "Add new button",
            current_file="/project/src/AuthService.cs"
        )
        
        assert score == 0.0


class TestExtractKeywords:
    """Test keyword extraction."""
    
    def test_extracts_meaningful_words(self):
        """Should extract meaningful words ignoring stop words"""
        scorer = RelevanceScorer()
        
        text = "the user authentication system with login tokens"
        keywords = scorer._extract_keywords(text)
        
        assert 'user' in keywords
        assert 'authentication' in keywords
        assert 'system' in keywords
        assert 'login' in keywords
        assert 'tokens' in keywords
        
        # Stop words should not be included
        assert 'the' not in keywords
        assert 'with' not in keywords
    
    def test_filters_short_words(self):
        """Should filter out words shorter than 3 characters"""
        scorer = RelevanceScorer()
        
        text = "a bb ccc dddd"
        keywords = scorer._extract_keywords(text)
        
        assert 'a' not in keywords
        assert 'bb' not in keywords
        assert 'ccc' in keywords
        assert 'dddd' in keywords


class TestDetectTopics:
    """Test topic detection."""
    
    def test_detects_authentication_topic(self):
        """Should detect authentication-related topics"""
        scorer = RelevanceScorer()
        
        text = "implement login with jwt tokens"
        topics = scorer._detect_topics(text)
        
        assert 'authentication' in topics
    
    def test_detects_ui_topic(self):
        """Should detect UI-related topics"""
        scorer = RelevanceScorer()
        
        text = "add button to the form"
        topics = scorer._detect_topics(text)
        
        assert 'ui' in topics
    
    def test_detects_bug_topic(self):
        """Should detect bug-related topics"""
        scorer = RelevanceScorer()
        
        text = "fix the error in authentication"
        topics = scorer._detect_topics(text)
        
        assert 'bug' in topics
    
    def test_detects_multiple_topics(self):
        """Should detect multiple topics in one text"""
        scorer = RelevanceScorer()
        
        text = "fix the api endpoint error and optimize performance"
        topics = scorer._detect_topics(text)
        
        assert 'api' in topics
        assert 'bug' in topics
        assert 'performance' in topics


class TestRankConversations:
    """Test conversation ranking."""
    
    def test_ranks_by_relevance_score(self):
        """Should rank conversations by relevance score descending"""
        scorer = RelevanceScorer()
        
        conversations = [
            {
                'title': 'Unrelated work',
                'created_at': (datetime.now() - timedelta(days=30)).isoformat(),
                'metadata': {'files': ['Dashboard.cs']}
            },
            {
                'title': 'Fix auth bug',
                'created_at': datetime.now().isoformat(),
                'metadata': {'files': ['AuthService.cs'], 'classes': ['AuthService']}
            },
            {
                'title': 'Old auth work',
                'created_at': (datetime.now() - timedelta(days=7)).isoformat(),
                'metadata': {'files': ['AuthService.cs']}
            }
        ]
        
        ranked = scorer.rank_conversations(
            conversations,
            current_request="Update AuthService.cs",
            current_file="/project/src/AuthService.cs",
            top_n=3
        )
        
        # Should rank recent auth work highest
        assert 'Fix auth bug' in ranked[0][0]['title']
        assert ranked[0][1] > ranked[1][1]  # First score > second score
        assert ranked[1][1] > ranked[2][1]  # Second score > third score
    
    def test_respects_top_n_limit(self):
        """Should return only top N conversations"""
        scorer = RelevanceScorer()
        
        conversations = [
            {'title': f'Conversation {i}', 'created_at': datetime.now().isoformat(), 'metadata': {}}
            for i in range(10)
        ]
        
        ranked = scorer.rank_conversations(
            conversations,
            current_request="test",
            top_n=3
        )
        
        assert len(ranked) == 3
    
    def test_returns_all_if_fewer_than_top_n(self):
        """Should return all conversations if fewer than top_n"""
        scorer = RelevanceScorer()
        
        conversations = [
            {'title': 'Conv 1', 'created_at': datetime.now().isoformat(), 'metadata': {}},
            {'title': 'Conv 2', 'created_at': datetime.now().isoformat(), 'metadata': {}}
        ]
        
        ranked = scorer.rank_conversations(
            conversations,
            current_request="test",
            top_n=5
        )
        
        assert len(ranked) == 2


class TestExtractConversationEntities:
    """Test entity extraction from conversation."""
    
    def test_extracts_from_metadata(self):
        """Should extract entities from metadata"""
        scorer = RelevanceScorer()
        
        conversation = {
            'metadata': {
                'files': ['AuthService.cs', 'LoginController.cs'],
                'classes': ['AuthService'],
                'methods': ['getUserById']
            }
        }
        
        entities = scorer._extract_conversation_entities(conversation)
        
        assert 'AuthService.cs' in entities['files']
        assert 'LoginController.cs' in entities['files']
        assert 'AuthService' in entities['classes']
        assert 'getUserById' in entities['methods']
    
    def test_extracts_from_tags(self):
        """Should extract entities from tags"""
        scorer = RelevanceScorer()
        
        conversation = {
            'tags': ['AuthService.cs', 'LoginController', 'authentication'],
            'metadata': {}
        }
        
        entities = scorer._extract_conversation_entities(conversation)
        
        assert 'AuthService.cs' in entities['files']  # Has extension
        assert 'LoginController' in entities['classes']  # PascalCase
    
    def test_handles_missing_metadata(self):
        """Should handle conversations without metadata"""
        scorer = RelevanceScorer()
        
        conversation = {'title': 'Test'}
        
        entities = scorer._extract_conversation_entities(conversation)
        
        assert len(entities['files']) == 0
        assert len(entities['classes']) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
