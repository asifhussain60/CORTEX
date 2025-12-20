"""
INCREMENT 12: Rollback Command Parsing Tests

Purpose: Test suite for parsing rollback commands from natural language input
Author: Asif Hussain
Created: 2025-11-27

Test Coverage:
- Command format validation ("rollback to checkpoint-X")
- Checkpoint ID extraction
- Invalid syntax handling
- Alternative command formats (shortcuts, variations)
- Error messaging for malformed commands

Integration Points:
- RollbackOrchestrator: Uses parsed checkpoint_id for validation/execution
- User interaction: Translates natural language to structured commands
"""

import pytest
from pathlib import Path
from src.orchestrators.rollback_command_parser import RollbackCommandParser


class TestRollbackCommandParser:
    """Test suite for rollback command parsing functionality."""
    
    @pytest.fixture
    def parser(self):
        """Create RollbackCommandParser instance."""
        return RollbackCommandParser()
    
    def test_parser_extracts_checkpoint_id_from_standard_format(self, parser):
        """
        Test: Parser extracts checkpoint ID from standard 'rollback to checkpoint-X' format
        
        Given: Command string "rollback to checkpoint-abc123"
        When: parse_command() called
        Then: Returns dict with checkpoint_id="checkpoint-abc123", valid=True
        """
        result = parser.parse_command("rollback to checkpoint-abc123")
        
        assert result['valid'] is True
        assert result['checkpoint_id'] == "checkpoint-abc123"
        assert result['session_id'] is None  # Not extracted from command
        assert 'error_message' not in result
    
    def test_parser_handles_session_id_in_command(self, parser):
        """
        Test: Parser extracts both session_id and checkpoint_id when provided
        
        Given: Command "rollback session session-1 to checkpoint-xyz789"
        When: parse_command() called
        Then: Returns session_id="session-1", checkpoint_id="checkpoint-xyz789"
        """
        result = parser.parse_command("rollback session session-1 to checkpoint-xyz789")
        
        assert result['valid'] is True
        assert result['session_id'] == "session-1"
        assert result['checkpoint_id'] == "checkpoint-xyz789"
    
    def test_parser_accepts_shorthand_rollback_command(self, parser):
        """
        Test: Parser accepts shorthand format without 'to' keyword
        
        Given: Command "rollback checkpoint-def456"
        When: parse_command() called
        Then: Extracts checkpoint_id="checkpoint-def456"
        """
        result = parser.parse_command("rollback checkpoint-def456")
        
        assert result['valid'] is True
        assert result['checkpoint_id'] == "checkpoint-def456"
    
    def test_parser_rejects_command_without_checkpoint_id(self, parser):
        """
        Test: Parser rejects command missing checkpoint ID
        
        Given: Command "rollback to"
        When: parse_command() called
        Then: Returns valid=False with descriptive error message
        """
        result = parser.parse_command("rollback to")
        
        assert result['valid'] is False
        assert 'checkpoint id' in result['error_message'].lower()
        assert result['checkpoint_id'] is None
    
    def test_parser_rejects_malformed_checkpoint_id(self, parser):
        """
        Test: Parser validates checkpoint ID format (alphanumeric + hyphens)
        
        Given: Command "rollback to invalid@checkpoint#123"
        When: parse_command() called
        Then: Returns valid=False with format error message
        """
        result = parser.parse_command("rollback to invalid@checkpoint#123")
        
        assert result['valid'] is False
        assert 'invalid format' in result['error_message'].lower()
    
    def test_parser_provides_help_for_empty_command(self, parser):
        """
        Test: Parser returns help message for empty/invalid input
        
        Given: Empty string ""
        When: parse_command() called
        Then: Returns valid=False with usage examples
        """
        result = parser.parse_command("")
        
        assert result['valid'] is False
        assert 'usage' in result['error_message'].lower()
        assert 'example' in result['error_message'].lower()
    
    def test_parser_handles_case_insensitive_keywords(self, parser):
        """
        Test: Parser accepts commands with different casing
        
        Given: Command "ROLLBACK TO CHECKPOINT-ABC123"
        When: parse_command() called
        Then: Successfully extracts checkpoint_id (case-preserved)
        """
        result = parser.parse_command("ROLLBACK TO CHECKPOINT-ABC123")
        
        assert result['valid'] is True
        assert result['checkpoint_id'] == "CHECKPOINT-ABC123"
    
    def test_parser_strips_whitespace_from_checkpoint_id(self, parser):
        """
        Test: Parser removes leading/trailing whitespace from checkpoint ID
        
        Given: Command "rollback to  checkpoint-xyz   "
        When: parse_command() called
        Then: Returns checkpoint_id="checkpoint-xyz" (trimmed)
        """
        result = parser.parse_command("rollback to  checkpoint-xyz   ")
        
        assert result['valid'] is True
        assert result['checkpoint_id'] == "checkpoint-xyz"
        assert not result['checkpoint_id'].startswith(' ')
        assert not result['checkpoint_id'].endswith(' ')
