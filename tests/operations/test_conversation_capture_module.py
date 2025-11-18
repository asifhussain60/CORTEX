"""
Tests for Conversation Capture Module

Tests natural language trigger detection, entity extraction, intent detection,
and database storage.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.operations.modules.conversation_capture_module import (
    ConversationCaptureModule,
    capture_conversation
)
from src.operations.base_operation_module import OperationStatus


class TestShouldCapture:
    """Test natural language capture trigger detection."""
    
    def test_detects_remember_this(self):
        """Should detect 'remember this' trigger"""
        module = ConversationCaptureModule()
        assert module.should_capture("This is great, remember this for next time")
    
    def test_detects_capture_conversation(self):
        """Should detect 'capture conversation' trigger"""
        module = ConversationCaptureModule()
        assert module.should_capture("capture this conversation please")
    
    def test_detects_save_chat(self):
        """Should detect 'save chat' trigger"""
        module = ConversationCaptureModule()
        assert module.should_capture("save this chat")
    
    def test_detects_store_conversation(self):
        """Should detect 'store conversation' trigger"""
        module = ConversationCaptureModule()
        assert module.should_capture("please store this conversation")
    
    def test_detects_save_context(self):
        """Should detect 'save context' trigger"""
        module = ConversationCaptureModule()
        assert module.should_capture("save context for later")
    
    def test_detects_keep_in_memory(self):
        """Should detect 'keep in memory' trigger"""
        module = ConversationCaptureModule()
        assert module.should_capture("keep this in memory")
    
    def test_returns_false_for_normal_request(self):
        """Should return false for requests without capture trigger"""
        module = ConversationCaptureModule()
        assert not module.should_capture("Make the button purple")
        assert not module.should_capture("Fix the login bug")
    
    def test_case_insensitive(self):
        """Should be case insensitive"""
        module = ConversationCaptureModule()
        assert module.should_capture("REMEMBER THIS")
        assert module.should_capture("Remember This")


class TestDetectIntent:
    """Test conversation intent detection."""
    
    def test_detects_plan_intent(self):
        """Should detect PLAN intent"""
        module = ConversationCaptureModule()
        conversation = "Let's plan the architecture for the new feature"
        assert module.detect_intent(conversation) == 'PLAN'
    
    def test_detects_execute_intent(self):
        """Should detect EXECUTE intent"""
        module = ConversationCaptureModule()
        conversation = "Let's implement the authentication system"
        assert module.detect_intent(conversation) == 'EXECUTE'
    
    def test_detects_fix_intent(self):
        """Should detect FIX intent"""
        module = ConversationCaptureModule()
        conversation = "I need to fix the bug in the login system"
        assert module.detect_intent(conversation) == 'FIX'
    
    def test_detects_refactor_intent(self):
        """Should detect REFACTOR intent"""
        module = ConversationCaptureModule()
        conversation = "Let's refactor this code to improve performance"
        assert module.detect_intent(conversation) == 'REFACTOR'
    
    def test_detects_test_intent(self):
        """Should detect TEST intent"""
        module = ConversationCaptureModule()
        conversation = "We need to test the new feature thoroughly"
        assert module.detect_intent(conversation) == 'TEST'
    
    def test_detects_document_intent(self):
        """Should detect DOCUMENT intent"""
        module = ConversationCaptureModule()
        conversation = "Please document this API endpoint"
        assert module.detect_intent(conversation) == 'DOCUMENT'
    
    def test_detects_research_intent(self):
        """Should detect RESEARCH intent"""
        module = ConversationCaptureModule()
        conversation = "Let's investigate why the performance is slow"
        assert module.detect_intent(conversation) == 'RESEARCH'
    
    def test_returns_general_for_no_match(self):
        """Should return GENERAL if no intent detected"""
        module = ConversationCaptureModule()
        conversation = "Hello, how are you today?"
        assert module.detect_intent(conversation) == 'GENERAL'
    
    def test_chooses_highest_scoring_intent(self):
        """Should choose intent with most matches"""
        module = ConversationCaptureModule()
        # Multiple fix keywords should win
        conversation = "Fix the bug and debug the error in the issue tracker"
        assert module.detect_intent(conversation) == 'FIX'


class TestExtractEntities:
    """Test entity extraction from conversations."""
    
    def test_extracts_python_files(self):
        """Should extract Python file names"""
        module = ConversationCaptureModule()
        text = "Update the context_formatter.py and test_formatter.py files"
        entities = module.extract_entities(text)
        
        assert 'context_formatter.py' in entities['files']
        assert 'test_formatter.py' in entities['files']
    
    def test_extracts_csharp_files(self):
        """Should extract C# file names"""
        module = ConversationCaptureModule()
        text = "Modify AuthService.cs and LoginController.cs"
        entities = module.extract_entities(text)
        
        assert 'AuthService.cs' in entities['files']
        assert 'LoginController.cs' in entities['files']
    
    def test_extracts_classes(self):
        """Should extract PascalCase class names"""
        module = ConversationCaptureModule()
        text = "The ContextFormatter and WorkingMemory classes need updates"
        entities = module.extract_entities(text)
        
        assert 'ContextFormatter' in entities['classes']
        assert 'WorkingMemory' in entities['classes']
    
    def test_filters_common_words(self):
        """Should filter out common PascalCase words"""
        module = ConversationCaptureModule()
        text = "This is a Test for the Phase implementation"
        entities = module.extract_entities(text)
        
        # Common words should be filtered
        assert 'This' not in entities['classes']
        assert 'Test' not in entities['classes']
        assert 'Phase' not in entities['classes']
    
    def test_extracts_methods(self):
        """Should extract method names"""
        module = ConversationCaptureModule()
        text = "Call getUserById and formatContext methods"
        entities = module.extract_entities(text)
        
        assert 'getUserById' in entities['methods']
        assert 'formatContext' in entities['methods']
    
    def test_extracts_ui_components(self):
        """Should extract UI component keywords"""
        module = ConversationCaptureModule()
        text = "Update the button and form on the dialog"
        entities = module.extract_entities(text)
        
        assert 'button' in entities['ui_components']
        assert 'form' in entities['ui_components']
        assert 'dialog' in entities['ui_components']
    
    def test_limits_entity_counts(self):
        """Should limit entities to reasonable numbers"""
        module = ConversationCaptureModule()
        # Create text with many classes
        classes = ' '.join([f"Class{i}" for i in range(20)])
        text = f"Update these classes: {classes}"
        entities = module.extract_entities(text)
        
        # Should limit to 10 classes
        assert len(entities['classes']) <= 10


class TestCreateConversationSummary:
    """Test conversation summary creation."""
    
    def test_returns_first_user_message_if_short(self):
        """Should return first user message if under max length"""
        module = ConversationCaptureModule()
        history = [
            {'role': 'user', 'content': 'Fix the login bug'},
            {'role': 'assistant', 'content': 'I will help you fix that'}
        ]
        
        summary = module.create_conversation_summary(history)
        assert summary == 'Fix the login bug'
    
    def test_truncates_long_messages(self):
        """Should truncate long messages with ellipsis"""
        module = ConversationCaptureModule()
        long_message = 'a' * 300
        history = [{'role': 'user', 'content': long_message}]
        
        summary = module.create_conversation_summary(history, max_length=200)
        assert len(summary) == 200
        assert summary.endswith('...')
    
    def test_handles_empty_history(self):
        """Should handle empty conversation history"""
        module = ConversationCaptureModule()
        summary = module.create_conversation_summary([])
        assert summary == ''


class TestValidatePrerequisites:
    """Test prerequisite validation."""
    
    def test_fails_if_brain_not_initialized(self):
        """Should fail if brain not initialized"""
        module = ConversationCaptureModule()
        context = {
            'brain_initialized': False,
            'user_request': 'remember this'
        }
        
        valid, issues = module.validate_prerequisites(context)
        assert not valid
        assert len(issues) > 0
        assert 'brain must be initialized' in issues[0].lower()
    
    def test_fails_if_no_capture_trigger(self):
        """Should fail (silently) if no capture trigger in request"""
        module = ConversationCaptureModule()
        context = {
            'brain_initialized': True,
            'user_request': 'Fix the button color'
        }
        
        valid, issues = module.validate_prerequisites(context)
        assert not valid
        assert len(issues) == 0  # No error message - just not requested
    
    def test_passes_with_valid_context(self):
        """Should pass with valid context"""
        module = ConversationCaptureModule()
        context = {
            'brain_initialized': True,
            'user_request': 'remember this conversation'
        }
        
        valid, issues = module.validate_prerequisites(context)
        assert valid
        assert len(issues) == 0


class TestExecute:
    """Test conversation capture execution."""
    
    @patch('src.tier1.working_memory.WorkingMemory')
    def test_captures_conversation_successfully(self, mock_wm_class):
        """Should capture conversation to database"""
        # Setup mock
        mock_wm = Mock()
        mock_wm.add_conversation.return_value = 1
        mock_wm.message_store = Mock()
        mock_wm.entity_extractor = Mock()
        mock_wm_class.return_value = mock_wm
        
        module = ConversationCaptureModule()
        context = {
            'brain_initialized': True,
            'user_request': 'remember this',
            'conversation_history': [
                {'role': 'user', 'content': 'Fix the button in LoginForm.cs'},
                {'role': 'assistant', 'content': 'I will help you fix that'}
            ],
            'project_root': Path('/tmp/test')
        }
        
        result = module.execute(context)
        
        assert result.success
        assert result.status == OperationStatus.SUCCESS
        assert 'conversation_id' in result.data
        assert 'intent' in result.data
        assert 'entities' in result.data
        
        # Verify WorkingMemory was called
        mock_wm.add_conversation.assert_called_once()
        assert mock_wm.message_store.add_message.call_count == 2
    
    def test_fails_with_no_conversation_history(self):
        """Should fail gracefully if no conversation history"""
        module = ConversationCaptureModule()
        context = {
            'brain_initialized': True,
            'user_request': 'remember this',
            'conversation_history': [],
            'project_root': Path('/tmp/test')
        }
        
        result = module.execute(context)
        
        assert not result.success
        assert result.status == OperationStatus.FAILED
        assert 'no conversation history' in result.message.lower()
    
    @patch('src.tier1.working_memory.WorkingMemory')
    def test_extracts_entities_and_intent(self, mock_wm_class):
        """Should extract entities and detect intent"""
        # Setup mock
        mock_wm = Mock()
        mock_wm.add_conversation.return_value = 1
        mock_wm.message_store = Mock()
        mock_wm.entity_extractor = Mock()
        mock_wm_class.return_value = mock_wm
        
        module = ConversationCaptureModule()
        context = {
            'brain_initialized': True,
            'user_request': 'remember this',
            'conversation_history': [
                {'role': 'user', 'content': 'Fix the bug in UserService.cs and update the button'},
                {'role': 'assistant', 'content': 'I will fix that'}
            ],
            'project_root': Path('/tmp/test')
        }
        
        result = module.execute(context)
        
        assert result.success
        assert result.data['intent'] == 'FIX'
        assert 'UserService.cs' in result.data['entities']['files']
        assert 'button' in result.data['entities']['ui_components']


class TestCaptureConversationHelper:
    """Test convenience helper function."""
    
    @patch('src.tier1.working_memory.WorkingMemory')
    def test_captures_when_requested(self, mock_wm_class):
        """Should capture when trigger detected"""
        # Setup mock
        mock_wm = Mock()
        mock_wm.add_conversation.return_value = 1
        mock_wm.message_store = Mock()
        mock_wm.entity_extractor = Mock()
        mock_wm_class.return_value = mock_wm
        
        result = capture_conversation(
            user_request="remember this",
            conversation_history=[
                {'role': 'user', 'content': 'Test message'}
            ],
            project_root=Path('/tmp/test')
        )
        
        assert result is not None
        assert result['success']
        assert 'conversation_id' in result['data']
    
    def test_returns_none_when_not_requested(self):
        """Should return None when no trigger detected"""
        result = capture_conversation(
            user_request="Fix the button",
            conversation_history=[
                {'role': 'user', 'content': 'Test message'}
            ]
        )
        
        assert result is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
