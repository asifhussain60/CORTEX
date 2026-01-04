"""
Test suite for CrossSessionContextMiddleware token budget enforcement.

Tests cover:
- Token budget enforcement when under limit
- Progressive trimming of file relationships
- Context priority preservation (Vision > Session > Files)
- Token counting accuracy

Author: CORTEX Development Team
Created: 2026-01-04 (C50-05 Phase 4)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json

from src.orchestrators.context_middleware import CrossSessionContextMiddleware


class TestTokenBudgetEnforcement(unittest.TestCase):
    """Test token budget enforcement and priority-based context trimming."""
    
    def setUp(self):
        """Set up test fixtures - no mocking needed for pure context manipulation."""
        self.middleware = CrossSessionContextMiddleware()
    
    def test_no_enforcement_when_under_budget(self):
        """Test that context is unchanged when under 500 token budget."""
        context = {
            'session_metadata': {
                'orchestrator_sessions': [
                    {'orchestrator': 'planning_v5', 'status': 'complete'}
                ]
            },
            'vision_context': {
                'image1.png': {
                    'description': 'Simple image',
                    'confidence': 0.95
                }
            },
            'file_relationships': [
                {
                    'source': 'src/auth.py',
                    'target': 'src/user.py',
                    'relationship': 'imports',
                    'strength': 0.9
                }
            ],
            'mentioned_files': ['src/auth.py']
        }
        
        # Estimate tokens: Should be well under 500
        token_count = self.middleware.get_context_token_count(context)
        self.assertLess(token_count, 500, "Test context should be under budget")
        
        # Enforce budget
        result = self.middleware._enforce_token_budget(context, max_tokens=500)
        
        # Context should be unchanged
        self.assertEqual(result, context)
        self.assertIn('file_relationships', result)
        self.assertEqual(len(result['file_relationships']), 1)
    
    def test_trim_file_relationships_when_over_budget(self):
        """Test that file relationships are trimmed to 3 items when over budget."""
        # Create context that exceeds 500 tokens
        large_sessions = [
            {
                'orchestrator': f'orchestrator_{i}',
                'status': 'complete',
                'summary': 'A' * 1200,  # Very large summary
                'phase': i,
                'tasks': [f'task_{j}' * 30 for j in range(15)],
                'metrics': {
                    'duration': 120,
                    'files_changed': 50,
                    'tests_added': 100,
                    'coverage': 85.0,
                    'lines_added': 3000,
                    'lines_removed': 1500
                },
                'notes': 'N' * 400
            }
            for i in range(10)  # More sessions
        ]
        
        large_file_rels = [
            {
                'source': f'src/module_{i}.py',
                'target': f'src/module_{i+1}.py',
                'relationship': 'imports',
                'strength': 0.8,
                'details': 'X' * 300  # Much larger details
            }
            for i in range(5)
        ]
        
        context = {
            'session_metadata': {
                'orchestrator_sessions': large_sessions
            },
            'file_relationships': large_file_rels,
            'mentioned_files': [f'src/module_{i}.py' for i in range(5)]
        }
        
        # Verify we're over budget
        initial_tokens = self.middleware.get_context_token_count(context)
        self.assertGreater(initial_tokens, 500, f"Test context has {initial_tokens} tokens, should exceed 500")
        
        # Enforce budget
        result = self.middleware._enforce_token_budget(context, max_tokens=500)
        
        # File relationships should be trimmed to 3
        self.assertIn('file_relationships', result)
        self.assertEqual(len(result['file_relationships']), 3)
        
        # Session metadata should be preserved (higher priority)
        self.assertIn('session_metadata', result)
        self.assertEqual(len(result['session_metadata']['orchestrator_sessions']), 10)
    
    def test_remove_file_relationships_when_still_over_budget(self):
        """Test that file relationships are removed entirely if trimming to 3 isn't enough."""
        # Create very large context that will still exceed budget even after trimming
        very_large_sessions = [
            {
                'orchestrator': f'orchestrator_{i}',
                'status': 'complete',
                'summary': 'A' * 1000,  # Very large summary
                'phase': i,
                'tasks': [f'task_{j}' * 30 for j in range(20)],
                'details': 'X' * 500,
                'metrics': {
                    'duration': 180,
                    'files_changed': 100,
                    'tests_added': 200,
                    'coverage': 90.0,
                    'lines_added': 5000,
                    'lines_removed': 2000
                }
            }
            for i in range(5)  # Many sessions
        ]
        
        large_vision = {
            f'image{i}.png': {
                'description': 'Y' * 400,
                'confidence': 0.95,
                'objects': [f'object_{j}' * 10 for j in range(15)],
                'ui_elements': [f'element_{j}' * 10 for j in range(15)],
                'text_content': 'Z' * 300
            }
            for i in range(3)  # Multiple images
        }
        
        large_file_rels = [
            {
                'source': f'src/module_{i}.py',
                'target': f'src/module_{i+1}.py',
                'relationship': 'imports',
                'strength': 0.8,
                'details': 'X' * 200
            }
            for i in range(5)
        ]
        
        context = {
            'session_metadata': {
                'orchestrator_sessions': very_large_sessions
            },
            'vision_context': large_vision,
            'file_relationships': large_file_rels,
            'mentioned_files': [f'src/module_{i}.py' for i in range(5)]
        }
        
        # Verify we're way over budget
        initial_tokens = self.middleware.get_context_token_count(context)
        self.assertGreater(initial_tokens, 700, f"Test context has {initial_tokens} tokens, should far exceed 700")
        
        # Enforce budget
        result = self.middleware._enforce_token_budget(context, max_tokens=500)
        
        # File relationships should be removed entirely
        self.assertNotIn('file_relationships', result)
        self.assertNotIn('mentioned_files', result)
        
        # High-priority context should be preserved
        self.assertIn('session_metadata', result)
        self.assertIn('vision_context', result)
        self.assertEqual(len(result['session_metadata']['orchestrator_sessions']), 5)
        self.assertEqual(len(result['vision_context']), 3)
    
    def test_vision_and_session_context_preserved(self):
        """Test that Vision (P1) and Session (P2) context are always preserved."""
        # Create context with all sources, designed to trigger file removal
        context = {
            'session_metadata': {
                'orchestrator_sessions': [
                    {
                        'orchestrator': 'planning_v5',
                        'status': 'complete',
                        'summary': 'B' * 400
                    }
                ]
            },
            'vision_context': {
                'screenshot.png': {
                    'description': 'C' * 300,
                    'confidence': 0.98,
                    'ui_elements': ['button', 'input', 'label']
                }
            },
            'file_relationships': [
                {
                    'source': f'src/file_{i}.py',
                    'target': f'src/file_{i+1}.py',
                    'relationship': 'imports',
                    'strength': 0.7
                }
                for i in range(5)
            ],
            'mentioned_files': [f'src/file_{i}.py' for i in range(5)]
        }
        
        # Enforce budget
        result = self.middleware._enforce_token_budget(context, max_tokens=500)
        
        # Priority 1 (Vision) and Priority 2 (Session) must be preserved
        self.assertIn('vision_context', result, "Vision context (P1) must be preserved")
        self.assertIn('session_metadata', result, "Session metadata (P2) must be preserved")
        
        # Verify content is intact
        self.assertIn('screenshot.png', result['vision_context'])
        self.assertEqual(result['vision_context']['screenshot.png']['confidence'], 0.98)
        self.assertEqual(result['session_metadata']['orchestrator_sessions'][0]['orchestrator'], 'planning_v5')


if __name__ == '__main__':
    unittest.main()
