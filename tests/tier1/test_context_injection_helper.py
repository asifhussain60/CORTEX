"""
Tests for Context Injection Helper

Validates the simplified context injection interface.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.tier1.context_injection_helper import (
    inject_tier1_context,
    resolve_pronoun_only,
    get_context_display,
    get_context_injector
)


@pytest.fixture
def mock_working_memory():
    """Mock WorkingMemory with sample data"""
    wm = Mock()
    
    # Mock recent conversations
    wm.get_recent_conversations.return_value = [
        {
            'conversation_id': 'conv_001',
            'summary': 'Added purple FAB button',
            'created_at': datetime.now().isoformat(),
            'entities': ['FAB button', 'Dashboard.tsx', 'styles.css'],
            'status': 'complete'
        }
    ]
    
    return wm


@pytest.fixture
def mock_context_injector(mock_working_memory):
    """Mock ContextInjector with formatter"""
    with patch('src.tier1.context_injection_helper.ContextInjector') as MockInjector:
        injector = MockInjector.return_value
        injector.wm = mock_working_memory
        
        # Mock inject_context to return expected structure
        def mock_inject(user_request, conversation_id=None, include_tiers=None, current_file=None):
            return {
                'tier1': {
                    'resolved_request': 'Make the FAB button purple',
                    'formatted_summary': '--- Recent Work ---',
                    'active_entities': {
                        'ui_components': ['FAB button'],
                        'files': ['Dashboard.tsx'],
                        'most_recent_entity': 'FAB button'
                    },
                    'context_display': '🧠 Context Loaded\n📚 Recent Work:\n   • Added purple FAB button',
                    'recent_conversations': mock_working_memory.get_recent_conversations()
                },
                'injection_time_ms': 45.2
            }
        
        injector.inject_context = Mock(side_effect=mock_inject)
        injector._last_injection_time_ms = 45.2
        
        yield injector


class TestInjectTier1Context:
    """Test Tier 1 context injection"""
    
    def test_injects_context_successfully(self, mock_context_injector):
        """Should inject Tier 1 context and return expected structure"""
        with patch('src.tier1.context_injection_helper._context_injector', mock_context_injector):
            result = inject_tier1_context("Make it purple")
            
            assert 'resolved_request' in result
            assert 'formatted_summary' in result
            assert 'active_entities' in result
            assert 'context_display' in result
            assert 'injection_time_ms' in result
    
    def test_resolves_pronouns(self, mock_context_injector):
        """Should resolve pronouns in user request"""
        with patch('src.tier1.context_injection_helper._context_injector', mock_context_injector):
            result = inject_tier1_context("Make it purple")
            
            assert result['resolved_request'] == 'Make the FAB button purple'
            assert 'it' not in result['resolved_request'].lower() or 'it purple' not in result['resolved_request'].lower()
    
    def test_extracts_active_entities(self, mock_context_injector):
        """Should extract active entities from conversations"""
        with patch('src.tier1.context_injection_helper._context_injector', mock_context_injector):
            result = inject_tier1_context("Test request")
            
            entities = result['active_entities']
            assert 'FAB button' in entities.get('ui_components', [])
            assert 'Dashboard.tsx' in entities.get('files', [])
    
    def test_includes_raw_conversations(self, mock_context_injector):
        """Should include raw conversations for advanced use"""
        with patch('src.tier1.context_injection_helper._context_injector', mock_context_injector):
            result = inject_tier1_context("Test request")
            
            assert 'raw_conversations' in result
            assert len(result['raw_conversations']) > 0
    
    def test_tracks_injection_time(self, mock_context_injector):
        """Should track injection performance"""
        with patch('src.tier1.context_injection_helper._context_injector', mock_context_injector):
            result = inject_tier1_context("Test request")
            
            assert result['injection_time_ms'] > 0
            assert result['injection_time_ms'] < 200  # Performance target


class TestResolvePronounOnly:
    """Test quick pronoun resolution"""
    
    def test_resolves_pronoun_quickly(self, mock_context_injector):
        """Should resolve pronoun without full context"""
        with patch('src.tier1.context_injection_helper._context_injector', mock_context_injector):
            result = resolve_pronoun_only("Make it purple")
            
            assert result == 'Make the FAB button purple'
    
    def test_returns_original_if_no_pronouns(self, mock_context_injector):
        """Should return original request if no pronouns"""
        # Create new mock with different return value
        def mock_inject_no_pronoun(user_request, **kwargs):
            return {
                'tier1': {'resolved_request': 'Add a button'},
                'injection_time_ms': 10
            }
        
        mock_context_injector.inject_context = Mock(side_effect=mock_inject_no_pronoun)
        
        with patch('src.tier1.context_injection_helper._context_injector', mock_context_injector):
            result = resolve_pronoun_only("Add a button")
            
            assert result == 'Add a button'


class TestGetContextDisplay:
    """Test context display formatting"""
    
    def test_returns_formatted_display(self, mock_context_injector):
        """Should return emoji-formatted context display"""
        with patch('src.tier1.context_injection_helper._context_injector', mock_context_injector):
            result = get_context_display("Continue work")
            
            assert '🧠' in result  # Emoji header
            assert 'Context Loaded' in result or 'Recent Work' in result
    
    def test_display_includes_recent_work(self, mock_context_injector):
        """Should include recent work in display"""
        with patch('src.tier1.context_injection_helper._context_injector', mock_context_injector):
            result = get_context_display("Test")
            
            assert 'FAB button' in result or 'Recent' in result


class TestPerformanceMonitoring:
    """Test performance monitoring helpers"""
    
    def test_gets_last_injection_time(self, mock_context_injector):
        """Should retrieve last injection time"""
        with patch('src.tier1.context_injection_helper._context_injector', mock_context_injector):
            # Trigger injection
            inject_tier1_context("Test")
            
            from src.tier1.context_injection_helper import get_last_injection_time
            time_ms = get_last_injection_time()
            
            assert time_ms > 0
    
    def test_checks_performance_ok(self, mock_context_injector):
        """Should check if performance within target"""
        with patch('src.tier1.context_injection_helper._context_injector', mock_context_injector):
            # Trigger injection
            inject_tier1_context("Test")
            
            from src.tier1.context_injection_helper import is_injection_performance_ok
            is_ok = is_injection_performance_ok()
            
            assert is_ok is True  # Mock is under 200ms


class TestSingletonPattern:
    """Test context injector singleton"""
    
    def test_returns_same_instance(self):
        """Should return same injector instance"""
        injector1 = get_context_injector()
        injector2 = get_context_injector()
        
        assert injector1 is injector2
    
    def test_initializes_once(self):
        """Should only initialize once"""
        # Clear singleton
        import src.tier1.context_injection_helper as helper_module
        helper_module._context_injector = None
        
        with patch('src.tier1.context_injection_helper.ContextInjector') as MockInjector:
            get_context_injector()
            get_context_injector()
            get_context_injector()
            
            # Should only be called once
            assert MockInjector.call_count == 1
