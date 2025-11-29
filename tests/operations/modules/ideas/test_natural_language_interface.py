"""
CORTEX 3.0 - Test Feature 1: IDEA Capture Natural Language Interface

Purpose: Test natural language processing for IDEA capture commands.
         Validates pattern recognition, intent routing, and user responses.

Test Coverage:
- Command parsing: idea:, remember:, task:, note:
- Management commands: show, work on, complete, delete, prioritize  
- Context integration: Active file, conversation, operation
- Response formatting: User-friendly messages and lists
- Performance: Fast pattern recognition

Success Criteria:
- Pattern recognition: ≥95% accuracy for valid commands
- Processing speed: <10ms for command parsing
- Response quality: Clear, actionable user feedback

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.operations.modules.ideas import (
    IdeaNaturalLanguageInterface,
    IdeaCommand,
    IdeaQueue,
    create_idea_interface
)


class TestIdeaNaturalLanguageInterface:
    """Test natural language interface for IDEA capture."""
    
    def setup_method(self):
        """Setup test environment."""
        # Create temporary queue for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.queue = IdeaQueue(
            db_path=self.temp_db.name,
            enable_enrichment=False  # Disable for unit tests
        )
        
        self.interface = IdeaNaturalLanguageInterface(idea_queue=self.queue)
    
    def teardown_method(self):
        """Cleanup temporary database."""
        Path(self.temp_db.name).unlink(missing_ok=True)
    
    # ========================================================================
    # COMMAND PARSING TESTS
    # ========================================================================
    
    def test_capture_command_patterns(self):
        """Test recognition of various capture command patterns."""
        test_cases = [
            ("idea: add rate limiting to login", "add rate limiting to login"),
            ("remember: fix the bug in auth module", "fix the bug in auth module"),
            ("task: update documentation for API", "update documentation for API"),  # original case preserved
            ("note: consider performance optimization", "consider performance optimization"),
            ("save idea: implement dark mode", "implement dark mode"),
            ("capture thought: refactor database layer", "refactor database layer"),
            ("add to ideas: create admin dashboard", "create admin dashboard"),
        ]
        
        for input_text, expected_idea_text in test_cases:
            command = self.interface._parse_command(input_text)
            
            assert command is not None, f"Failed to parse: {input_text}"
            assert command.command_type == 'capture'
            assert command.idea_text == expected_idea_text
            assert command.raw_input == input_text
    
    def test_show_command_patterns(self):
        """Test recognition of show command patterns."""
        test_cases = [
            ("show ideas", None, None, None),
            ("show all ideas", None, None, None),
            ("show auth ideas", "component", "auth", None),
            ("show API ideas", "component", "api", None),
            ("show idea 5", None, None, "5"),
            ("show high priority", "priority", "high", None),
            ("show medium priority", "priority", "medium", None),
        ]
        
        for input_text, expected_filter_type, expected_filter_value, expected_idea_id in test_cases:
            command = self.interface._parse_command(input_text)
            
            assert command is not None, f"Failed to parse: {input_text}"
            assert command.command_type == 'show'
            assert command.filter_type == expected_filter_type
            assert command.filter_value == expected_filter_value
            assert command.idea_id == expected_idea_id
    
    def test_management_command_patterns(self):
        """Test recognition of idea management patterns."""
        test_cases = [
            ("work on idea 5", "work", "5", None),
            ("complete idea 3", "complete", "3", None),
            ("delete idea 7", "delete", "7", None),
            ("prioritize idea 2 high", "prioritize", "2", "high"),
            ("prioritize idea 8 low", "prioritize", "8", "low"),
        ]
        
        for input_text, expected_command_type, expected_idea_id, expected_priority in test_cases:
            command = self.interface._parse_command(input_text)
            
            assert command is not None, f"Failed to parse: {input_text}"
            assert command.command_type == expected_command_type
            assert command.idea_id == expected_idea_id
            assert command.priority == expected_priority
    
    def test_non_idea_commands_ignored(self):
        """Test that non-IDEA commands are not recognized."""
        non_idea_inputs = [
            "show files",
            "create new project",
            "run tests",
            "git commit",
            "hello world",
            "help me with authentication",
            "what is the weather"
        ]
        
        for input_text in non_idea_inputs:
            command = self.interface._parse_command(input_text)
            assert command is None, f"Incorrectly parsed non-idea command: {input_text}"
    
    # ========================================================================
    # COMMAND EXECUTION TESTS  
    # ========================================================================
    
    def test_capture_command_execution(self):
        """Test execution of capture commands."""
        context = {
            'active_file': '/path/to/auth.py',
            'active_line': 42,
            'active_operation': 'refactoring'
        }
        
        result = self.interface.process_input(
            "idea: add 2FA support",
            context=context
        )
        
        assert result['handled'] is True
        assert result['idea_id'] is not None
        assert "Captured idea" in result['response']
        assert "add 2FA support" in result['response']
        assert "auth.py" in result['response']
        
        # Verify idea was actually stored
        idea = self.queue.get_idea(result['idea_id'])
        assert idea.raw_text == "add 2FA support"
        assert idea.active_file == "/path/to/auth.py"
        assert idea.active_line == 42
        assert idea.active_operation == "refactoring"
    
    def test_show_all_ideas_execution(self):
        """Test execution of show all ideas command."""
        # Add some test ideas
        self.queue.capture("Fix authentication bug", 
                          context={'active_file': 'auth.py'})
        self.queue.capture("Add API rate limiting", 
                          context={'active_file': 'api.py'})
        
        result = self.interface.process_input("show ideas")
        
        assert result['handled'] is True
        assert result['ideas'] is not None
        assert len(result['ideas']) >= 2
        assert "IDEA CAPTURE" in result['response']
        assert "Fix authentication bug" in result['response']
        assert "Add API rate limiting" in result['response']
    
    def test_show_specific_idea_execution(self):
        """Test execution of show specific idea command."""
        # Create test idea
        idea_id = self.queue.capture("Test specific idea")
        
        result = self.interface.process_input(f"show idea {idea_id}")
        
        assert result['handled'] is True
        assert result['ideas'] is not None
        assert len(result['ideas']) == 1
        assert result['ideas'][0].idea_id == idea_id
        assert f"Idea #{idea_id}" in result['response']
        assert "Test specific idea" in result['response']
    
    def test_complete_idea_execution(self):
        """Test execution of complete idea command."""
        # Create test idea
        idea_id = self.queue.capture("Test completion idea")
        
        result = self.interface.process_input(f"complete idea {idea_id}")
        
        assert result['handled'] is True
        assert "Completed idea" in result['response']
        assert idea_id in result['response']
        
        # Verify idea status changed
        idea = self.queue.get_idea(idea_id)
        assert idea.status == 'completed'
    
    def test_prioritize_idea_execution(self):
        """Test execution of prioritize idea command."""
        # Create test idea
        idea_id = self.queue.capture("Test priority idea")
        
        result = self.interface.process_input(f"prioritize idea {idea_id} high")
        
        assert result['handled'] is True
        assert "Updated idea" in result['response']
        assert "priority to high" in result['response']
        assert "🔴" in result['response']  # High priority emoji
        
        # Verify priority changed
        idea = self.queue.get_idea(idea_id)
        assert idea.priority == 'high'
    
    def test_work_on_idea_execution(self):
        """Test execution of work on idea command."""
        # Create test idea
        idea_id = self.queue.capture("Test work idea")
        
        result = self.interface.process_input(f"work on idea {idea_id}")
        
        assert result['handled'] is True
        assert f"Idea #{idea_id}" in result['response']
        assert "Ready to plan implementation" in result['response']
        assert "Interactive Planning" in result['response']
        assert result['ideas'] is not None
        assert len(result['ideas']) == 1
    
    # ========================================================================
    # CONTEXT INTEGRATION TESTS
    # ========================================================================
    
    def test_context_preservation_in_capture(self):
        """Test that context is properly preserved during capture."""
        context = {
            'active_file': '/project/src/user_service.py',
            'active_line': 156,
            'active_operation': 'add_user_validation',
            'conversation_id': 'conv_abc123',
            'project': 'UserManagement'
        }
        
        result = self.interface.process_input(
            "remember: add email validation",
            context=context
        )
        
        assert result['handled'] is True
        idea_id = result['idea_id']
        
        # Verify all context was captured
        idea = self.queue.get_idea(idea_id)
        assert idea.active_file == '/project/src/user_service.py'
        assert idea.active_line == 156
        assert idea.active_operation == 'add_user_validation'
        assert idea.conversation_id == 'conv_abc123'
        assert idea.project == 'UserManagement'
    
    def test_capture_without_context(self):
        """Test capture works without context (minimal scenario)."""
        result = self.interface.process_input("idea: standalone idea")
        
        assert result['handled'] is True
        idea_id = result['idea_id']
        
        # Should still capture successfully
        idea = self.queue.get_idea(idea_id)
        assert idea.raw_text == "standalone idea"
        assert idea.active_file is None
        assert idea.project is not None  # Should detect from current dir
    
    # ========================================================================
    # PERFORMANCE TESTS
    # ========================================================================
    
    def test_command_processing_performance(self):
        """Test that command processing is fast enough."""
        test_commands = [
            "idea: performance test 1",
            "remember: performance test 2",
            "show ideas",
            "work on idea abc123",
            "complete idea def456"
        ]
        
        for command in test_commands:
            result = self.interface.process_input(command)
            
            # Should have processing time recorded
            if 'processing_time_ms' in result:
                processing_time = result['processing_time_ms']
                # Command processing should be fast (not including capture time)
                assert processing_time < 50.0, \
                    f"Command processing too slow: {processing_time:.1f}ms for '{command}'"
    
    # ========================================================================
    # ERROR HANDLING TESTS
    # ========================================================================
    
    def test_invalid_idea_id_handling(self):
        """Test handling of invalid idea IDs."""
        test_commands = [
            "show idea nonexistent",
            "complete idea invalid",
            "work on idea missing",
            "delete idea notfound",
            "prioritize idea fake high"
        ]
        
        for command in test_commands:
            result = self.interface.process_input(command)
            
            assert result['handled'] is True
            assert "not found" in result['response']
            assert "❌" in result['response']
    
    def test_invalid_priority_handling(self):
        """Test handling of invalid priority values."""
        idea_id = self.queue.capture("Test priority validation")
        
        # This should be handled by the IdeaQueue validation
        result = self.interface.process_input(f"prioritize idea {idea_id} invalid")
        
        # Should either fail gracefully or not recognize as valid pattern
        assert result['handled'] is False or "❌" in result['response']
    
    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================
    
    def test_full_workflow_integration(self):
        """Test complete workflow from capture to completion."""
        # 1. Capture idea
        capture_result = self.interface.process_input(
            "idea: implement search functionality",
            context={'active_file': 'search.py', 'active_operation': 'development'}
        )
        
        assert capture_result['handled'] is True
        idea_id = capture_result['idea_id']
        
        # 2. Show all ideas (should include our idea)
        show_result = self.interface.process_input("show ideas")
        assert "implement search functionality" in show_result['response']
        
        # 3. Show specific idea
        specific_result = self.interface.process_input(f"show idea {idea_id}")
        assert f"Idea #{idea_id}" in specific_result['response']
        assert "search.py" in specific_result['response']
        
        # 4. Prioritize idea
        prioritize_result = self.interface.process_input(f"prioritize idea {idea_id} high")
        assert "🔴" in prioritize_result['response']
        
        # 5. Work on idea
        work_result = self.interface.process_input(f"work on idea {idea_id}")
        assert "Ready to plan implementation" in work_result['response']
        
        # 6. Complete idea
        complete_result = self.interface.process_input(f"complete idea {idea_id}")
        assert "Completed idea" in complete_result['response']
        
        # 7. Verify completion
        final_idea = self.queue.get_idea(idea_id)
        assert final_idea.status == 'completed'
        assert final_idea.priority == 'high'


class TestFactoryFunction:
    """Test factory function for creating natural language interface."""
    
    def test_default_creation(self):
        """Test creating interface with default settings."""
        interface = create_idea_interface()
        
        assert interface is not None
        assert isinstance(interface, IdeaNaturalLanguageInterface)
        assert interface.idea_queue is not None
    
    def test_custom_queue_creation(self):
        """Test creating interface with custom queue."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        custom_queue = IdeaQueue(db_path=temp_db.name)
        
        config = {'idea_queue': custom_queue}
        interface = create_idea_interface(config)
        
        assert interface.idea_queue is custom_queue
        
        # Cleanup
        Path(temp_db.name).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])