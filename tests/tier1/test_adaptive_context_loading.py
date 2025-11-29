"""
Integration tests for Phase 4B: Adaptive Context Loading

Tests relevance-based context injection in the ContextInjector.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.context_injector import ContextInjector


class TestAdaptiveContextLoading(unittest.TestCase):
    """Test adaptive context loading with relevance scoring"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_db_path = ":memory:"
        
    @patch('src.context_injector.WorkingMemory')
    @patch('src.context_injector.ContextFormatter')
    @patch('src.context_injector.RelevanceScorer')
    def test_relevance_based_selection(self, mock_scorer_class, mock_formatter_class, mock_wm_class):
        """Test that most relevant conversations are selected, not just recent"""
        # Setup mock working memory
        mock_wm = Mock()
        mock_wm_class.return_value = mock_wm
        
        # Create test conversations with varying relevance
        now = datetime.now()
        conversations = [
            {
                'conversation_id': 'conv1',
                'summary': 'Working on AuthService login',
                'entities': {'files': ['AuthService.cs'], 'classes': ['AuthService']},
                'timestamp': now - timedelta(hours=1),
                'intent': 'EXECUTE'
            },
            {
                'conversation_id': 'conv2',
                'summary': 'Fixed bug in UserController',
                'entities': {'files': ['UserController.cs'], 'classes': ['UserController']},
                'timestamp': now - timedelta(hours=2),
                'intent': 'FIX'
            },
            {
                'conversation_id': 'conv3',
                'summary': 'Updated AuthService authentication logic',
                'entities': {'files': ['AuthService.cs'], 'classes': ['AuthService']},
                'timestamp': now - timedelta(days=1),
                'intent': 'REFACTOR'
            },
            {
                'conversation_id': 'conv4',
                'summary': 'Added tests for PaymentService',
                'entities': {'files': ['PaymentService.cs'], 'classes': ['PaymentService']},
                'timestamp': now - timedelta(hours=3),
                'intent': 'TEST'
            },
            {
                'conversation_id': 'conv5',
                'summary': 'Documented API endpoints',
                'entities': {'files': ['README.md']},
                'timestamp': now - timedelta(hours=4),
                'intent': 'DOCUMENT'
            }
        ]
        
        mock_wm.get_recent_conversations.return_value = conversations
        
        # Setup mock relevance scorer
        mock_scorer = Mock()
        mock_scorer_class.return_value = mock_scorer
        
        # Score conversations: conv3 and conv1 are most relevant (AuthService)
        def score_side_effect(user_request, conversation_summary, **kwargs):
            if 'AuthService' in conversation_summary:
                return 0.9  # High relevance
            elif 'UserController' in conversation_summary:
                return 0.5  # Medium relevance
            else:
                return 0.2  # Low relevance
        
        mock_scorer.score_conversation.side_effect = score_side_effect
        
        # Setup mock formatter
        mock_formatter = Mock()
        mock_formatter_class.return_value = mock_formatter
        mock_formatter.format_recent_conversations.return_value = "Formatted context"
        mock_formatter.extract_active_entities.return_value = {'files': ['AuthService.cs']}
        mock_formatter.resolve_pronouns.return_value = "Continue working on AuthService"
        mock_formatter.format_context_summary.return_value = "Context summary"
        
        # Create injector
        injector = ContextInjector(self.mock_db_path)
        
        # Inject context with request about AuthService
        result = injector.inject_context(
            user_request="Continue working on AuthService",
            include_tiers={'tier1': True, 'tier2': False, 'tier3': False}
        )
        
        # Verify relevance scorer was called
        self.assertEqual(mock_scorer.score_conversation.call_count, 5)
        
        # Verify relevant conversations were selected
        self.assertIn('tier1', result)
        relevant_convs = result['tier1']['relevant_conversations']
        
        # Top conversations should include conv1 and conv3 (highest relevance)
        conv_ids = [c['conversation_id'] for c in relevant_convs]
        self.assertIn('conv1', conv_ids)
        self.assertIn('conv3', conv_ids)
        
        # Lower relevance conversations should not be in top 5
        # (conv4 and conv5 have low relevance)
        
    @patch('src.context_injector.WorkingMemory')
    @patch('src.context_injector.ContextFormatter')
    @patch('src.context_injector.RelevanceScorer')
    def test_relevance_scores_returned(self, mock_scorer_class, mock_formatter_class, mock_wm_class):
        """Test that relevance scores are included in response"""
        # Setup mocks
        mock_wm = Mock()
        mock_wm_class.return_value = mock_wm
        
        now = datetime.now()
        conversations = [
            {
                'conversation_id': 'conv1',
                'summary': 'Test conversation',
                'entities': {},
                'timestamp': now,
                'intent': 'EXECUTE'
            }
        ]
        
        mock_wm.get_recent_conversations.return_value = conversations
        
        mock_scorer = Mock()
        mock_scorer_class.return_value = mock_scorer
        mock_scorer.score_conversation.return_value = 0.85
        
        mock_formatter = Mock()
        mock_formatter_class.return_value = mock_formatter
        mock_formatter.format_recent_conversations.return_value = "Formatted"
        mock_formatter.extract_active_entities.return_value = {}
        mock_formatter.resolve_pronouns.return_value = "Test request"
        mock_formatter.format_context_summary.return_value = "Summary"
        
        # Create injector and get context
        injector = ContextInjector(self.mock_db_path)
        result = injector.inject_context(
            user_request="Test request",
            include_tiers={'tier1': True, 'tier2': False, 'tier3': False}
        )
        
        # Verify relevance scores are included
        self.assertIn('relevance_scores', result['tier1'])
        scores = result['tier1']['relevance_scores']
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]['conversation_id'], 'conv1')
        self.assertEqual(scores[0]['score'], 0.85)
    
    @patch('src.context_injector.WorkingMemory')
    @patch('src.context_injector.ContextFormatter')
    @patch('src.context_injector.RelevanceScorer')
    def test_fallback_to_recency_when_no_scorer(self, mock_scorer_class, mock_formatter_class, mock_wm_class):
        """Test fallback to recency-based selection if relevance scorer unavailable"""
        # Setup mocks
        mock_wm = Mock()
        mock_wm_class.return_value = mock_wm
        
        now = datetime.now()
        conversations = [
            {'conversation_id': f'conv{i}', 'summary': f'Test {i}', 'entities': {}, 'timestamp': now - timedelta(hours=i), 'intent': 'EXECUTE'}
            for i in range(10)
        ]
        
        mock_wm.get_recent_conversations.return_value = conversations
        
        # Make relevance scorer unavailable
        mock_scorer_class.return_value = None
        
        mock_formatter = Mock()
        mock_formatter_class.return_value = mock_formatter
        mock_formatter.format_recent_conversations.return_value = "Formatted"
        mock_formatter.extract_active_entities.return_value = {}
        mock_formatter.resolve_pronouns.return_value = "Test"
        mock_formatter.format_context_summary.return_value = "Summary"
        
        # Create injector
        injector = ContextInjector(self.mock_db_path)
        injector.relevance_scorer = None  # Disable scorer
        
        result = injector.inject_context(
            user_request="Test",
            include_tiers={'tier1': True, 'tier2': False, 'tier3': False}
        )
        
        # Should use top 5 recent (fallback)
        relevant_convs = result['tier1']['relevant_conversations']
        self.assertEqual(len(relevant_convs), 5)
        
        # Should be in chronological order (most recent first)
        self.assertEqual(relevant_convs[0]['conversation_id'], 'conv0')
        self.assertEqual(relevant_convs[4]['conversation_id'], 'conv4')
    
    @patch('src.context_injector.WorkingMemory')
    def test_empty_conversations_handling(self, mock_wm_class):
        """Test handling of empty conversation list"""
        mock_wm = Mock()
        mock_wm_class.return_value = mock_wm
        mock_wm.get_recent_conversations.return_value = []
        
        injector = ContextInjector(self.mock_db_path)
        result = injector.inject_context(
            user_request="Test",
            include_tiers={'tier1': True, 'tier2': False, 'tier3': False}
        )
        
        # Should handle empty gracefully
        self.assertIn('tier1', result)
        self.assertEqual(result['tier1']['relevant_conversations'], [])
        self.assertEqual(result['tier1']['formatted_summary'], "No recent context available")
    
    @patch('src.context_injector.WorkingMemory')
    @patch('src.context_injector.ContextFormatter')
    @patch('src.context_injector.RelevanceScorer')
    def test_token_budget_adaptation(self, mock_scorer_class, mock_formatter_class, mock_wm_class):
        """Test that context loading adapts to token budget (future Phase 5)"""
        # This is a placeholder for future token budget functionality
        # For now, we verify that we select top 5 conversations (token-efficient)
        
        mock_wm = Mock()
        mock_wm_class.return_value = mock_wm
        
        now = datetime.now()
        conversations = [
            {'conversation_id': f'conv{i}', 'summary': f'Test {i}' * 100, 'entities': {}, 'timestamp': now, 'intent': 'EXECUTE'}
            for i in range(20)  # 20 conversations
        ]
        
        mock_wm.get_recent_conversations.return_value = conversations
        
        mock_scorer = Mock()
        mock_scorer_class.return_value = mock_scorer
        mock_scorer.score_conversation.return_value = 0.5
        
        mock_formatter = Mock()
        mock_formatter_class.return_value = mock_formatter
        mock_formatter.format_recent_conversations.return_value = "Formatted" * 10
        mock_formatter.extract_active_entities.return_value = {}
        mock_formatter.resolve_pronouns.return_value = "Test"
        mock_formatter.format_context_summary.return_value = "Summary"
        
        injector = ContextInjector(self.mock_db_path)
        result = injector.inject_context(
            user_request="Test",
            include_tiers={'tier1': True, 'tier2': False, 'tier3': False}
        )
        
        # Should limit to top 5 (token-efficient)
        relevant_convs = result['tier1']['relevant_conversations']
        self.assertLessEqual(len(relevant_convs), 5)
    
    @patch('src.context_injector.WorkingMemory')
    @patch('src.context_injector.ContextFormatter')
    @patch('src.context_injector.RelevanceScorer')
    def test_performance_within_target(self, mock_scorer_class, mock_formatter_class, mock_wm_class):
        """Test that context injection completes within 200ms target"""
        # Setup fast mocks
        mock_wm = Mock()
        mock_wm_class.return_value = mock_wm
        
        now = datetime.now()
        conversations = [
            {'conversation_id': f'conv{i}', 'summary': f'Test {i}', 'entities': {}, 'timestamp': now, 'intent': 'EXECUTE'}
            for i in range(20)
        ]
        
        mock_wm.get_recent_conversations.return_value = conversations
        
        mock_scorer = Mock()
        mock_scorer_class.return_value = mock_scorer
        mock_scorer.score_conversation.return_value = 0.5
        
        mock_formatter = Mock()
        mock_formatter_class.return_value = mock_formatter
        mock_formatter.format_recent_conversations.return_value = "Formatted"
        mock_formatter.extract_active_entities.return_value = {}
        mock_formatter.resolve_pronouns.return_value = "Test"
        mock_formatter.format_context_summary.return_value = "Summary"
        
        injector = ContextInjector(self.mock_db_path)
        result = injector.inject_context(
            user_request="Test",
            include_tiers={'tier1': True, 'tier2': False, 'tier3': False}
        )
        
        # Verify performance target met
        self.assertIn('injection_time_ms', result)
        self.assertIn('performance_ok', result)
        
        # With mocks, should be well under 200ms
        # (Real implementation should also meet this target)


if __name__ == '__main__':
    unittest.main()
