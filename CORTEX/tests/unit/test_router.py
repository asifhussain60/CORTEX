"""
Unit Tests for CortexRouter

Tests:
1. test_process_request() - Request processing works
2. test_intent_detection() - Intent detected via Phase 4
3. test_context_injection() - Context injected <200ms
4. test_conversation_logging() - Logged to Tier 1

Author: CORTEX Development Team
Version: 1.0
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import time
from datetime import datetime

# Add CORTEX to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.router import CortexRouter


class TestCortexRouter(unittest.TestCase):
    """Unit tests for CortexRouter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.db_path = ":memory:"  # In-memory SQLite for testing
        
        # Mock dependencies
        with patch('src.router.IntentRouter'), \
             patch('src.router.SessionManager'), \
             patch('src.router.ContextInjector'):
            self.router = CortexRouter(self.db_path)
    
    def test_process_request(self):
        """Test: Request processing works"""
        # Setup mocks
        self.router.intent_router.route_request = Mock(return_value={
            'intent': 'PLAN',
            'confidence': 0.95
        })
        
        self.router.session_manager.get_active_session = Mock(return_value=None)
        self.router.session_manager.start_session = Mock(return_value='test-conv-id')
        
        self.router.context_injector.inject_context = Mock(return_value={
            'tier1': {},
            'tier2': {},
            'tier3': {}
        })
        
        self.router._log_interaction = Mock()
        
        # Execute
        result = self.router.process_request(
            "Create a plan for authentication"
        )
        
        # Verify
        self.assertEqual(result['intent'], 'PLAN')
        self.assertEqual(result['confidence'], 0.95)
        self.assertEqual(result['workflow'], 'feature_creation')
        self.assertIn('conversation_id', result)
        self.assertIn('total_time_ms', result)
        
        # Verify dependencies called
        self.router.intent_router.route_request.assert_called_once()
        self.router.session_manager.start_session.assert_called_once()
        self.router.context_injector.inject_context.assert_called_once()
        self.router._log_interaction.assert_called_once()
    
    def test_intent_detection(self):
        """Test: Intent detected via Phase 4 agents"""
        test_cases = [
            ("Create a plan for authentication", "PLAN"),
            ("Implement the login form", "EXECUTE"),
            ("Run all tests", "TEST"),
            ("Fix the submit button bug", "FIX"),
            ("What did we discuss about exports?", "QUERY")
        ]
        
        for request, expected_intent in test_cases:
            with self.subTest(request=request):
                # Setup
                self.router.intent_router.route_request = Mock(return_value={
                    'intent': expected_intent,
                    'confidence': 0.9
                })
                
                self.router.session_manager.get_active_session = Mock(return_value='test-id')
                self.router.context_injector.inject_context = Mock(return_value={})
                self.router._log_interaction = Mock()
                
                # Execute
                result = self.router.process_request(request)
                
                # Verify
                self.assertEqual(result['intent'], expected_intent)
    
    def test_context_injection(self):
        """Test: Context injected <200ms"""
        # Setup
        self.router.intent_router.route_request = Mock(return_value={
            'intent': 'PLAN',
            'confidence': 0.9
        })
        
        self.router.session_manager.get_active_session = Mock(return_value='test-id')
        
        # Mock context injection with timing
        def mock_inject(*args, **kwargs):
            time.sleep(0.05)  # Simulate 50ms injection
            return {
                'tier1': {'entities': []},
                'tier2': {'patterns': []},
                'tier3': {'activity': []},
                'injection_time_ms': 50.0
            }
        
        self.router.context_injector.inject_context = Mock(side_effect=mock_inject)
        self.router._log_interaction = Mock()
        
        # Execute
        result = self.router.process_request("Test request")
        
        # Verify performance
        self.assertLess(result['context_time_ms'], 200,
                       "Context injection should be <200ms")
        
        # Verify no performance warnings for fast injection
        if result['context_time_ms'] < 200:
            context_warnings = [w for w in result.get('performance_warnings', [])
                              if 'Context injection' in w]
            self.assertEqual(len(context_warnings), 0)
    
    def test_conversation_logging(self):
        """Test: Conversation logged to Tier 1"""
        # Setup
        self.router.intent_router.route_request = Mock(return_value={
            'intent': 'EXECUTE',
            'confidence': 0.85
        })
        
        test_conv_id = 'test-conversation-123'
        self.router.session_manager.get_active_session = Mock(return_value=test_conv_id)
        self.router.context_injector.inject_context = Mock(return_value={})
        
        # Mock logging
        log_calls = []
        def mock_log(**kwargs):
            log_calls.append(kwargs)
        
        self.router._log_interaction = Mock(side_effect=mock_log)
        
        # Execute
        user_request = "Implement feature X"
        result = self.router.process_request(user_request)
        
        # Verify logging called
        self.router._log_interaction.assert_called_once()
        
        # Verify logging parameters
        call_args = self.router._log_interaction.call_args[1]
        self.assertEqual(call_args['conversation_id'], test_conv_id)
        self.assertEqual(call_args['user_request'], user_request)
        self.assertEqual(call_args['intent'], 'EXECUTE')
        self.assertIn('workflow', call_args)


class TestCortexRouterPerformance(unittest.TestCase):
    """Performance tests for CortexRouter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.db_path = ":memory:"
        
        with patch('src.router.IntentRouter'), \
             patch('src.router.SessionManager'), \
             patch('src.router.ContextInjector'):
            self.router = CortexRouter(self.db_path)
    
    def test_routing_performance_target(self):
        """Test: Intent routing meets <100ms target"""
        # Setup fast mock
        self.router.intent_router.route_request = Mock(return_value={
            'intent': 'PLAN',
            'confidence': 0.9
        })
        
        self.router.session_manager.get_active_session = Mock(return_value='test-id')
        self.router.context_injector.inject_context = Mock(return_value={})
        self.router._log_interaction = Mock()
        
        # Execute
        result = self.router.process_request("Test request")
        
        # Verify
        stats = self.router.get_performance_stats()
        self.assertTrue(stats['routing_ok'],
                       f"Routing took {stats['last_routing_ms']}ms (target: <100ms)")
    
    def test_total_performance_target(self):
        """Test: Total routing <300ms"""
        # Setup
        self.router.intent_router.route_request = Mock(return_value={
            'intent': 'TEST',
            'confidence': 0.88
        })
        
        self.router.session_manager.get_active_session = Mock(return_value='test-id')
        self.router.context_injector.inject_context = Mock(return_value={})
        self.router._log_interaction = Mock()
        
        # Execute
        result = self.router.process_request("Run tests")
        
        # Verify
        self.assertLess(result['total_time_ms'], 300,
                       f"Total routing took {result['total_time_ms']}ms (target: <300ms)")


if __name__ == '__main__':
    unittest.main()
