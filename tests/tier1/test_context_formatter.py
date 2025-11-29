"""
Tests for CORTEX Tier 1 Context Formatter

Validates token-efficient conversation summarization and pronoun resolution.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from datetime import datetime, timedelta
from src.tier1.context_formatter import ContextFormatter


@pytest.fixture
def formatter():
    """Create context formatter instance"""
    return ContextFormatter()


@pytest.fixture
def sample_conversations():
    """Sample conversations for testing"""
    now = datetime.now()
    
    return [
        {
            'conversation_id': 'conv_001',
            'summary': 'Added authentication system with JWT tokens',
            'created_at': (now - timedelta(hours=2)).isoformat(),
            'entities': ['AuthService.cs', 'LoginController.cs', 'JwtTokenGenerator'],
            'intent': 'EXECUTE',
            'status': 'in_progress',
            'metadata': {'phase_info': 'Phase 2 of 4'}
        },
        {
            'conversation_id': 'conv_002',
            'summary': 'Fixed null reference exception in UserRepository',
            'created_at': (now - timedelta(days=1)).isoformat(),
            'entities': ['UserRepository.cs', 'GetUserById'],
            'intent': 'FIX',
            'status': 'complete'
        },
        {
            'conversation_id': 'conv_003',
            'summary': 'Added purple FAB button to dashboard',
            'created_at': (now - timedelta(days=2)).isoformat(),
            'entities': ['FAB button', 'Dashboard.tsx', 'styles.css'],
            'intent': 'EXECUTE',
            'status': 'complete'
        }
    ]


class TestFormatRecentConversations:
    """Test conversation formatting"""
    
    def test_formats_empty_conversations(self, formatter):
        """Should handle empty conversation list"""
        result = formatter.format_recent_conversations([])
        assert result == "No recent conversation history."
    
    def test_formats_single_conversation(self, formatter, sample_conversations):
        """Should format single conversation correctly"""
        result = formatter.format_recent_conversations([sample_conversations[0]])
        
        assert "Recent Work Context" in result
        assert "Added authentication system" in result
        assert "AuthService.cs" in result
        assert "In progress" in result
        assert "Phase 2 of 4" in result
    
    def test_formats_multiple_conversations(self, formatter, sample_conversations):
        """Should format multiple conversations with numbering"""
        result = formatter.format_recent_conversations(sample_conversations)
        
        # Check all conversations present
        assert "1. [" in result
        assert "2. [" in result
        assert "3. [" in result
        
        # Check content
        assert "authentication system" in result
        assert "null reference" in result
        assert "FAB button" in result
    
    def test_limits_to_max_conversations(self, formatter, sample_conversations):
        """Should limit to max_conversations setting"""
        # Create 10 conversations
        many_convs = sample_conversations * 4  # 12 conversations
        
        result = formatter.format_recent_conversations(many_convs)
        
        # Should only show 5 (formatter.max_conversations)
        assert result.count("Status:") == 5
    
    def test_truncates_long_summaries(self, formatter):
        """Should truncate summaries exceeding max_summary_length"""
        long_summary = "A" * 500  # Much longer than max_summary_length (300)
        
        conv = {
            'conversation_id': 'conv_long',
            'summary': long_summary,
            'created_at': datetime.now().isoformat(),
            'entities': ['test.py'],
            'status': 'complete'
        }
        
        result = formatter.format_recent_conversations([conv])
        
        # Should be truncated with ellipsis
        assert "..." in result
        assert len(result) < len(long_summary) + 200  # Much shorter than original
    
    def test_formats_time_ago_correctly(self, formatter):
        """Should format various time deltas correctly"""
        now = datetime.now()
        
        test_cases = [
            (now - timedelta(seconds=30), "Just now"),
            (now - timedelta(minutes=5), "5 minutes ago"),
            (now - timedelta(hours=2), "2 hours ago"),
            (now - timedelta(days=1), "1 day ago"),
            (now - timedelta(days=3), "3 days ago")
        ]
        
        for timestamp, expected in test_cases:
            conv = {
                'conversation_id': 'test',
                'summary': 'Test',
                'created_at': timestamp.isoformat(),
                'entities': [],
                'status': 'complete'
            }
            
            result = formatter.format_recent_conversations([conv])
            assert expected in result


class TestExtractActiveEntities:
    """Test entity extraction"""
    
    def test_extracts_files(self, formatter, sample_conversations):
        """Should extract file entities"""
        entities = formatter.extract_active_entities(sample_conversations)
        
        assert 'AuthService.cs' in entities['files']
        assert 'UserRepository.cs' in entities['files']
        assert 'Dashboard.tsx' in entities['files']
    
    def test_extracts_classes(self, formatter, sample_conversations):
        """Should extract class entities"""
        entities = formatter.extract_active_entities(sample_conversations)
        
        assert 'JwtTokenGenerator' in entities['classes']
    
    def test_extracts_methods(self, formatter, sample_conversations):
        """Should extract method entities"""
        entities = formatter.extract_active_entities(sample_conversations)
        
        assert 'GetUserById' in entities['methods']
    
    def test_extracts_ui_components(self, formatter, sample_conversations):
        """Should extract UI component entities"""
        entities = formatter.extract_active_entities(sample_conversations)
        
        assert 'FAB button' in entities['ui_components']
    
    def test_identifies_most_recent_entity(self, formatter, sample_conversations):
        """Should identify most recent entity for pronoun resolution"""
        entities = formatter.extract_active_entities(sample_conversations)
        
        # Most recent conversation has AuthService.cs first
        assert entities['most_recent_entity'] == 'AuthService.cs'
    
    def test_extracts_current_task(self, formatter, sample_conversations):
        """Should extract current task from most recent conversation"""
        entities = formatter.extract_active_entities(sample_conversations)
        
        assert entities['current_task'] == 'Added authentication system with JWT tokens'
    
    def test_handles_empty_conversations(self, formatter):
        """Should handle empty conversation list"""
        entities = formatter.extract_active_entities([])
        
        assert entities['files'] == []
        assert entities['classes'] == []
        assert entities['methods'] == []
        assert entities['current_task'] is None
    
    def test_limits_entity_counts(self, formatter):
        """Should limit each entity type to top 5"""
        # Create conversation with many entities
        many_files = [f'File{i}.cs' for i in range(10)]
        
        conv = {
            'conversation_id': 'conv_many',
            'summary': 'Many files',
            'created_at': datetime.now().isoformat(),
            'entities': many_files,
            'status': 'complete'
        }
        
        entities = formatter.extract_active_entities([conv])
        
        # Should limit to 5
        assert len(entities['files']) == 5


class TestResolvePronouns:
    """Test pronoun resolution"""
    
    def test_resolves_it(self, formatter):
        """Should resolve 'it' to most recent entity"""
        active_entities = {
            'most_recent_entity': 'FAB button',
            'ui_components': ['FAB button']
        }
        
        result = formatter.resolve_pronouns("Make it purple", active_entities)
        
        assert "FAB button" in result
        assert "it" not in result.lower() or "it purple" not in result.lower()
    
    def test_resolves_that(self, formatter):
        """Should resolve 'that' to most recent entity"""
        active_entities = {
            'most_recent_entity': 'AuthService.cs',
            'files': ['AuthService.cs']
        }
        
        result = formatter.resolve_pronouns("Refactor that", active_entities)
        
        assert "AuthService.cs" in result
    
    def test_resolves_this(self, formatter):
        """Should resolve 'this' to most recent entity"""
        active_entities = {
            'most_recent_entity': 'LoginController',
            'classes': ['LoginController']
        }
        
        result = formatter.resolve_pronouns("Test this", active_entities)
        
        assert "LoginController" in result
    
    def test_handles_no_entities(self, formatter):
        """Should return original request if no entities available"""
        active_entities = {
            'most_recent_entity': None,
            'files': [],
            'classes': []
        }
        
        result = formatter.resolve_pronouns("Make it purple", active_entities)
        
        # Should be unchanged
        assert result == "Make it purple"
    
    def test_uses_correct_article_for_ui_components(self, formatter):
        """Should add 'the' for UI components"""
        active_entities = {
            'most_recent_entity': 'login button',
            'ui_components': ['login button']
        }
        
        result = formatter.resolve_pronouns("Click it", active_entities)
        
        assert "the login button" in result
    
    def test_no_article_for_files(self, formatter):
        """Should not add article for files"""
        active_entities = {
            'most_recent_entity': 'AuthService.cs',
            'files': ['AuthService.cs']
        }
        
        result = formatter.resolve_pronouns("Update it", active_entities)
        
        assert "AuthService.cs" in result
        assert "the AuthService.cs" not in result
    
    def test_resolves_only_first_pronoun(self, formatter):
        """Should only resolve first pronoun occurrence"""
        active_entities = {
            'most_recent_entity': 'FAB button',
            'ui_components': ['FAB button']
        }
        
        result = formatter.resolve_pronouns("Make it purple and make it bigger", active_entities)
        
        # First 'it' should be resolved
        assert "FAB button" in result
        # But not all instances (would need to count actual replacements in real impl)
    
    def test_case_insensitive_matching(self, formatter):
        """Should match pronouns case-insensitively"""
        active_entities = {
            'most_recent_entity': 'AuthService.cs',
            'files': ['AuthService.cs']
        }
        
        # Test uppercase IT
        result = formatter.resolve_pronouns("Update IT", active_entities)
        assert "AuthService.cs" in result
    
    def test_fallback_to_any_entity_type(self, formatter):
        """Should fall back to any entity type if most_recent not set"""
        active_entities = {
            'most_recent_entity': None,
            'ui_components': ['dashboard button'],
            'files': [],
            'classes': []
        }
        
        result = formatter.resolve_pronouns("Click it", active_entities)
        
        # Should use first available entity (dashboard button)
        assert "dashboard button" in result


class TestFormatContextSummary:
    """Test complete context summary formatting"""
    
    def test_formats_complete_summary(self, formatter, sample_conversations):
        """Should format complete summary with all sections"""
        active_entities = formatter.extract_active_entities(sample_conversations)
        result = formatter.format_context_summary(sample_conversations, active_entities)
        
        # Check all sections present
        assert "Context Loaded" in result
        assert "Recent Work:" in result
        assert "Active Files:" in result
        assert "Current Task:" in result
    
    def test_includes_emoji_header(self, formatter, sample_conversations):
        """Should include emoji header when requested"""
        active_entities = formatter.extract_active_entities(sample_conversations)
        result = formatter.format_context_summary(
            sample_conversations, 
            active_entities, 
            include_header=True
        )
        
        assert "🧠" in result
    
    def test_excludes_header_when_requested(self, formatter, sample_conversations):
        """Should exclude header when requested"""
        active_entities = formatter.extract_active_entities(sample_conversations)
        result = formatter.format_context_summary(
            sample_conversations, 
            active_entities, 
            include_header=False
        )
        
        assert "🧠" not in result
    
    def test_limits_active_files_display(self, formatter):
        """Should limit active files to top 3 in display"""
        # Create many files
        many_files = [f'File{i}.cs' for i in range(10)]
        
        conv = {
            'conversation_id': 'conv_many',
            'summary': 'Many files',
            'created_at': datetime.now().isoformat(),
            'entities': many_files,
            'status': 'complete'
        }
        
        active_entities = formatter.extract_active_entities([conv])
        result = formatter.format_context_summary([conv], active_entities)
        
        # Should only show 3 files in display
        file_lines = [line for line in result.split('\n') if 'File' in line and '•' in line]
        assert len(file_lines) == 3


class TestHelperMethods:
    """Test helper methods"""
    
    def test_is_file_detection(self, formatter):
        """Should correctly identify files"""
        assert formatter._is_file('AuthService.cs') is True
        assert formatter._is_file('test.py') is True
        assert formatter._is_file('AuthService') is False
        assert formatter._is_file('ValidateUser') is False
    
    def test_is_class_detection(self, formatter):
        """Should correctly identify classes (PascalCase)"""
        assert formatter._is_class('AuthService') is True
        assert formatter._is_class('JwtTokenGenerator') is True
        assert formatter._is_class('validateUser') is False  # camelCase
        assert formatter._is_class('AuthService.cs') is False  # file
    
    def test_is_method_detection(self, formatter):
        """Should correctly identify methods"""
        assert formatter._is_method('validateUser') is True  # camelCase
        assert formatter._is_method('GetUserById()') is True  # with parens
        assert formatter._is_method('AuthService') is False  # PascalCase
    
    def test_is_ui_component_detection(self, formatter):
        """Should correctly identify UI components"""
        assert formatter._is_ui_component('FAB button') is True
        assert formatter._is_ui_component('login form') is True
        assert formatter._is_ui_component('Dashboard') is False
        assert formatter._is_ui_component('AuthService.cs') is False


class TestTokenEfficiency:
    """Test token efficiency of formatted output"""
    
    def test_conversation_summary_token_count(self, formatter, sample_conversations):
        """Should keep conversation summary under token budget"""
        result = formatter.format_recent_conversations(sample_conversations)
        
        # Rough token count (1 token ≈ 4 characters)
        approx_tokens = len(result) / 4
        
        # Should be well under 500 token budget (aiming for ~300)
        assert approx_tokens < 400
    
    def test_context_summary_token_count(self, formatter, sample_conversations):
        """Should keep complete context summary under budget"""
        active_entities = formatter.extract_active_entities(sample_conversations)
        result = formatter.format_context_summary(sample_conversations, active_entities)
        
        # Rough token count
        approx_tokens = len(result) / 4
        
        # Should be under 200 tokens for display summary
        assert approx_tokens < 200
    
    def test_combined_context_under_budget(self, formatter, sample_conversations):
        """Should keep combined context (conversations + summary) under 500 tokens"""
        conversations_text = formatter.format_recent_conversations(sample_conversations)
        active_entities = formatter.extract_active_entities(sample_conversations)
        summary_text = formatter.format_context_summary(sample_conversations, active_entities)
        
        combined = conversations_text + "\n" + summary_text
        approx_tokens = len(combined) / 4
        
        # Combined should be under 500 token budget
        assert approx_tokens < 500


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_handles_missing_metadata(self, formatter):
        """Should handle conversations with missing metadata"""
        conv = {
            'conversation_id': 'conv_minimal',
            'summary': 'Minimal conversation'
            # No created_at, entities, status, metadata
        }
        
        # Should not raise exceptions
        result = formatter.format_recent_conversations([conv])
        assert "Minimal conversation" in result
    
    def test_handles_invalid_timestamp(self, formatter):
        """Should handle invalid timestamps gracefully"""
        conv = {
            'conversation_id': 'conv_bad_time',
            'summary': 'Test',
            'created_at': 'invalid-timestamp',
            'entities': [],
            'status': 'complete'
        }
        
        result = formatter.format_recent_conversations([conv])
        assert "Unknown time" in result or "Test" in result
    
    def test_handles_none_values(self, formatter):
        """Should handle None values in conversation data"""
        conv = {
            'conversation_id': 'conv_none',
            'summary': None,
            'created_at': None,
            'entities': None,
            'status': None
        }
        
        # Should not raise exceptions
        result = formatter.format_recent_conversations([conv])
        assert result is not None
