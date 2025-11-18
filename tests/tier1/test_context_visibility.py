"""
Tests for Phase 5: Context Visibility & User Controls

Tests context display module, control commands, quality indicators,
and response template integration.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
from src.operations.modules.context_display_module import ContextDisplayModule
from src.operations.modules.context_control_module import ContextControlModule
from src.tier1.response_context_integration import ResponseContextIntegration


# --- Fixtures ---

@pytest.fixture
def sample_context_data():
    """Sample context data with conversations and scores."""
    return {
        'relevant_conversations': [
            {
                'conversation_id': 'conv-001',
                'summary': 'Discussed authentication implementation',
                'timestamp': datetime.now() - timedelta(hours=2),
                'entities': {
                    'files': ['auth.py', 'login.js'],
                    'classes': ['AuthService', 'UserManager']
                },
                'intent': 'EXECUTE'
            },
            {
                'conversation_id': 'conv-002',
                'summary': 'Fixed bug in payment processing',
                'timestamp': datetime.now() - timedelta(hours=5),
                'entities': {
                    'files': ['payment.py'],
                    'methods': ['process_payment', 'validate_card']
                },
                'intent': 'FIX'
            },
            {
                'conversation_id': 'conv-003',
                'summary': 'Refactored database queries',
                'timestamp': datetime.now() - timedelta(days=1),
                'entities': {
                    'files': ['db.py', 'models.py'],
                    'classes': ['QueryBuilder']
                },
                'intent': 'REFACTOR'
            }
        ],
        'relevance_scores': [
            {'conversation_id': 'conv-001', 'score': 0.85},
            {'conversation_id': 'conv-002', 'score': 0.65},
            {'conversation_id': 'conv-003', 'score': 0.45}
        ]
    }


@pytest.fixture
def empty_context_data():
    """Empty context data."""
    return {
        'relevant_conversations': [],
        'relevance_scores': []
    }


@pytest.fixture
def display_module():
    """Context display module instance."""
    return ContextDisplayModule()


@pytest.fixture
def control_module():
    """Context control module instance with mock working memory."""
    mock_wm = MagicMock()
    return ContextControlModule(working_memory=mock_wm)


# --- Context Display Module Tests ---

def test_format_context_display_with_conversations(display_module, sample_context_data):
    """Test formatting context display with loaded conversations."""
    display = display_module._format_context_display(
        sample_context_data,
        "implement user authentication"
    )
    
    assert "🧠 CORTEX Context Memory" in display
    assert "Loaded Conversations:** 3" in display  # Markdown format with **
    assert "Quality Score:" in display
    assert "Freshness:" in display
    assert "Entity Coverage:" in display
    assert "conv-001" in display
    assert "authentication implementation" in display
    assert "Relevance:" in display


def test_format_context_display_empty(display_module, empty_context_data):
    """Test formatting context display with no conversations."""
    display = display_module._format_context_display(
        empty_context_data,
        "implement feature"
    )
    
    assert "📭 Context Memory: Empty" in display
    assert "No recent conversations loaded" in display


def test_format_context_status(display_module, sample_context_data):
    """Test quick context status formatting."""
    status = display_module._format_context_status(sample_context_data)
    
    assert "📊 Context Status" in status
    assert "Conversations Loaded:** 3" in status  # Markdown format with **
    assert "Quality Score:" in status
    assert "Memory Health:" in status
    assert "show context" in status


def test_format_memory_health(display_module, sample_context_data):
    """Test memory health report formatting."""
    health = display_module._format_memory_health(sample_context_data)
    
    assert "Memory Health Report" in health
    assert "Status:" in health
    assert "Average Relevance:" in health
    assert "Conversation Span:" in health
    assert "High Relevance" in health
    assert "Medium Relevance" in health
    assert "Low Relevance" in health


def test_calculate_quality_indicators(display_module, sample_context_data):
    """Test quality indicator calculation."""
    quality = display_module._calculate_quality_indicators(sample_context_data)
    
    assert 'overall_score' in quality
    assert 'quality_emoji' in quality
    assert 'freshness_label' in quality
    assert 'hours_since_last' in quality
    assert 'entity_coverage' in quality
    assert 'memory_health' in quality
    
    # Score should be based on average (0.85 + 0.65 + 0.45) / 3 = 0.65 -> 6.5/10
    assert 6.0 <= quality['overall_score'] <= 7.0
    
    # Freshness should be "Fresh" (2 hours ago)
    assert quality['freshness_label'] in ['Very Fresh', 'Fresh']


def test_relevance_emoji_mapping(display_module):
    """Test relevance emoji for different scores."""
    assert display_module._get_relevance_emoji(0.85) == "🔥"
    assert display_module._get_relevance_emoji(0.65) == "✨"
    assert display_module._get_relevance_emoji(0.45) == "💡"
    assert display_module._get_relevance_emoji(0.25) == "📄"


def test_relevance_bar_visualization(display_module):
    """Test relevance bar generation."""
    bar_high = display_module._get_relevance_bar(0.85)
    bar_low = display_module._get_relevance_bar(0.25)
    
    assert "█" in bar_high
    assert "░" in bar_high
    assert bar_high.count("█") > bar_low.count("█")


def test_time_ago_formatting(display_module):
    """Test relative time formatting."""
    now = datetime.now()
    
    assert "just now" in display_module._format_time_ago(now)
    assert "m ago" in display_module._format_time_ago(now - timedelta(minutes=30))
    assert "h ago" in display_module._format_time_ago(now - timedelta(hours=5))
    assert "d ago" in display_module._format_time_ago(now - timedelta(days=3))
    assert "w ago" in display_module._format_time_ago(now - timedelta(weeks=2))


# --- Context Control Module Tests ---

def test_detect_show_command(control_module):
    """Test detection of show context command."""
    assert control_module._detect_command("show context") == "show"
    assert control_module._detect_command("what do you remember") == "show"
    assert control_module._detect_command("display context") == "show"


def test_detect_forget_command(control_module):
    """Test detection of forget command."""
    assert control_module._detect_command("forget authentication") == "forget"
    assert control_module._detect_command("remove from memory the payment stuff") == "forget"
    assert control_module._detect_command("delete conversation about bugs") == "forget"


def test_detect_clear_command(control_module):
    """Test detection of clear context command."""
    assert control_module._detect_command("clear context") == "clear"
    assert control_module._detect_command("reset memory") == "clear"
    assert control_module._detect_command("forget everything") == "clear"


def test_extract_topic_from_forget_command(control_module):
    """Test topic extraction from forget commands."""
    assert control_module._extract_topic("forget authentication") == "authentication"
    assert control_module._extract_topic("forget about payment processing") == "payment processing"
    assert control_module._extract_topic("remove from memory the bug fixes") == "the bug fixes"


def test_handle_show_context(control_module):
    """Test show context command handling."""
    result = control_module._handle_show_context({'user_request': 'show context'})
    
    assert result.success
    assert result.data['action'] == 'show_context'


def test_handle_forget_topic_no_topic(control_module):
    """Test forget command without topic specified."""
    result = control_module._handle_forget_topic({'user_request': 'forget'})
    
    assert not result.success
    assert "specify what to forget" in result.message


def test_handle_forget_topic_with_topic(control_module):
    """Test forget command with topic."""
    control_module.working_memory.get_recent_conversations.return_value = [
        {
            'conversation_id': 'conv-001',
            'summary': 'authentication implementation',
            'entities': {}
        }
    ]
    
    result = control_module._handle_forget_topic({
        'user_request': 'forget authentication'
    })
    
    assert result.success
    assert 'authentication' in result.data['topic']


def test_handle_clear_context_requires_confirmation(control_module):
    """Test clear context requires confirmation."""
    result = control_module._handle_clear_context({
        'confirmed': False
    })
    
    assert result.success
    assert result.data['requires_confirmation']
    assert "yes, clear context" in result.message


def test_handle_clear_context_with_confirmation(control_module):
    """Test clear context with confirmation."""
    control_module.working_memory.get_recent_conversations.return_value = [
        {'conversation_id': 'conv-001'},
        {'conversation_id': 'conv-002'}
    ]
    
    result = control_module._handle_clear_context({
        'confirmed': True
    })
    
    assert result.success
    assert 'cleared' in result.message.lower()


def test_detect_trigger(control_module):
    """Test trigger detection for context control commands."""
    assert control_module.detect_trigger("show context")
    assert control_module.detect_trigger("forget authentication")
    assert control_module.detect_trigger("clear memory")
    assert not control_module.detect_trigger("implement feature")


# --- Response Context Integration Tests ---

def test_inject_context_summary_with_context(sample_context_data):
    """Test injecting context summary into response."""
    response = """Response content here

[CONTEXT_SUMMARY]

More content here"""
    
    result = ResponseContextIntegration.inject_context_summary(
        response,
        sample_context_data
    )
    
    assert "[CONTEXT_SUMMARY]" not in result
    assert "Context Memory" in result
    assert "conversations loaded" in result
    assert "Quality:" in result
    assert "<details>" in result
    assert "</details>" in result


def test_inject_context_summary_without_context(empty_context_data):
    """Test injecting context summary when no context loaded."""
    response = """Response content here

[CONTEXT_SUMMARY]

More content here"""
    
    result = ResponseContextIntegration.inject_context_summary(
        response,
        empty_context_data
    )
    
    assert "[CONTEXT_SUMMARY]" not in result
    assert "Context Memory" not in result


def test_should_show_context(sample_context_data, empty_context_data):
    """Test should_show_context logic."""
    assert ResponseContextIntegration.should_show_context(sample_context_data)
    assert not ResponseContextIntegration.should_show_context(empty_context_data)
    assert not ResponseContextIntegration.should_show_context(None)


def test_generate_context_summary(sample_context_data):
    """Test context summary generation."""
    summary = ResponseContextIntegration._generate_context_summary(sample_context_data)
    
    assert "<details>" in summary
    assert "<summary>" in summary
    assert "🧠" in summary
    assert "3 conversations loaded" in summary
    assert "Quality:" in summary
    assert "Freshness:" in summary
    assert "Entity Coverage:" in summary
    assert "Memory Health:" in summary
    assert "show context" in summary


def test_quality_indicators_high_quality(sample_context_data):
    """Test quality indicators for high-quality context."""
    quality = ResponseContextIntegration._calculate_quality_indicators(
        sample_context_data['relevant_conversations'],
        sample_context_data['relevance_scores']
    )
    
    # Average score (0.85 + 0.65 + 0.45) / 3 = 0.65 -> 6.5/10
    assert quality['overall_score'] >= 6.0
    assert quality['quality_emoji'] in ['🟢', '🟡']
    assert quality['freshness_label'] in ['Very Fresh', 'Fresh']


def test_quality_indicators_empty_context():
    """Test quality indicators for empty context."""
    quality = ResponseContextIntegration._calculate_quality_indicators([], [])
    
    assert quality['overall_score'] == 0.0
    assert quality['quality_emoji'] == '📭'
    assert quality['freshness_label'] == 'N/A'
    assert quality['memory_health'] == 'Empty'


# --- Integration Tests ---

def test_full_display_workflow(display_module, sample_context_data):
    """Test complete display workflow."""
    # Execute display operation
    result = display_module.execute({
        'command': 'show context',
        'context_data': sample_context_data,
        'user_request': 'implement authentication'
    })
    
    assert result.success
    assert 'display' in result.data
    
    display = result.data['display']
    assert "CORTEX Context Memory" in display
    assert "3" in display  # conversation count
    assert "Quality Score:" in display


def test_full_control_workflow(control_module):
    """Test complete control workflow."""
    control_module.working_memory.get_recent_conversations.return_value = [
        {'conversation_id': 'conv-001', 'summary': 'authentication'},
        {'conversation_id': 'conv-002', 'summary': 'payments'}
    ]
    
    # Test show
    result = control_module.execute({
        'user_request': 'show context'
    })
    assert result.success
    
    # Test forget
    result = control_module.execute({
        'user_request': 'forget authentication'
    })
    assert result.success
    
    # Test clear (no confirmation)
    result = control_module.execute({
        'user_request': 'clear context'
    })
    assert result.success
    assert result.data.get('requires_confirmation')


def test_response_integration_workflow(sample_context_data):
    """Test response integration workflow."""
    # Create response with placeholder
    response = """🧠 **CORTEX Test**

🎯 **My Understanding:** Test request

⚠️ **Challenge:** ✓ Accept

💬 **Response:** Test response

[CONTEXT_SUMMARY]

📝 **Your Request:** Test

🔍 Next Steps:
   1. Step one"""
    
    # Inject context
    result = ResponseContextIntegration.inject_context_summary(
        response,
        sample_context_data
    )
    
    # Verify integration
    assert "[CONTEXT_SUMMARY]" not in result
    assert "Context Memory" in result
    assert "conversations loaded" in result
    assert "<details>" in result
    assert "Your Request:" in result  # Should preserve rest of response


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
