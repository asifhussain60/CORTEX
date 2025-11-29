"""
Rollback Command Parser

Purpose: Parse natural language rollback commands into structured format
Author: Asif Hussain
Created: 2025-11-27

Command Formats Supported:
- "rollback to checkpoint-X"
- "rollback session session-Y to checkpoint-X"  
- "rollback checkpoint-X" (shorthand)

Integration Points:
- RollbackOrchestrator: Uses parsed checkpoint_id for validation
- User interaction: Translates natural language to structured commands
"""

import re
from typing import Dict, Optional


class RollbackCommandParser:
    """
    Parse natural language rollback commands into structured format.
    
    Supports multiple command formats and validates checkpoint ID format.
    """
    
    # Regex patterns for command matching
    STANDARD_FORMAT = r'rollback\s+to\s+(.+)'
    SESSION_FORMAT = r'rollback\s+session\s+(\S+)\s+to\s+(.+)'
    SHORTHAND_FORMAT = r'rollback\s+(?!to(?:\s|$)|session(?:\s|$))(.+)'
    
    # Valid checkpoint ID pattern (alphanumeric + hyphens only)
    CHECKPOINT_ID_PATTERN = r'^[a-zA-Z0-9\-]+$'
    
    # Error message constants
    ERROR_EMPTY_COMMAND = 'Empty command. Usage: "rollback to <checkpoint-id>" or "rollback session <session-id> to <checkpoint-id>". Example: "rollback to checkpoint-abc123"'
    ERROR_MISSING_CHECKPOINT = 'Checkpoint ID is required. Use format: {format}'
    ERROR_INVALID_FORMAT = 'Invalid format: "{checkpoint_id}" contains invalid characters. Use only alphanumeric characters and hyphens.'
    ERROR_NO_PATTERN_MATCH = 'Missing checkpoint ID. Usage: "rollback to <checkpoint-id>" or "rollback session <session-id> to <checkpoint-id>". Example: "rollback to checkpoint-abc123"'
    
    def _create_error_response(self, error_message: str) -> Dict[str, any]:
        """Create standardized error response."""
        return {
            'valid': False,
            'checkpoint_id': None,
            'session_id': None,
            'error_message': error_message
        }
    
    def _create_success_response(self, checkpoint_id: str, session_id: Optional[str] = None) -> Dict[str, any]:
        """Create standardized success response."""
        return {
            'valid': True,
            'checkpoint_id': checkpoint_id,
            'session_id': session_id
        }
    
    def _validate_checkpoint_id(self, checkpoint_id: str, command_format: str) -> Optional[Dict[str, any]]:
        """
        Validate checkpoint ID format.
        
        Returns:
            Error response dict if invalid, None if valid
        """
        # Check for empty
        if not checkpoint_id:
            return self._create_error_response(
                self.ERROR_MISSING_CHECKPOINT.format(format=command_format)
            )
        
        # Check format (alphanumeric + hyphens only)
        if not re.match(self.CHECKPOINT_ID_PATTERN, checkpoint_id):
            return self._create_error_response(
                self.ERROR_INVALID_FORMAT.format(checkpoint_id=checkpoint_id)
            )
        
        return None  # Valid
    
    def parse_command(self, command: str) -> Dict[str, any]:
        """
        Parse rollback command into structured format.
        
        Args:
            command: Natural language rollback command
            
        Returns:
            Dict with keys:
            - valid (bool): Whether command is valid
            - checkpoint_id (str|None): Extracted checkpoint ID
            - session_id (str|None): Extracted session ID (if specified)
            - error_message (str|None): Error description if invalid
            
        Example:
            >>> parser = RollbackCommandParser()
            >>> parser.parse_command("rollback to checkpoint-abc123")
            {'valid': True, 'checkpoint_id': 'checkpoint-abc123', 'session_id': None}
            
            >>> parser.parse_command("rollback session session-1 to checkpoint-xyz")
            {'valid': True, 'checkpoint_id': 'checkpoint-xyz', 'session_id': 'session-1'}
        """
        # Handle empty command
        if not command or not command.strip():
            return self._create_error_response(self.ERROR_EMPTY_COMMAND)
        
        # Normalize command (strip whitespace, handle case-insensitive keywords)
        normalized = command.strip()
        
        # Try session format first (most specific)
        session_match = re.search(self.SESSION_FORMAT, normalized, re.IGNORECASE)
        if session_match:
            session_id = session_match.group(1).strip()
            checkpoint_id = session_match.group(2).strip()
            
            # Validate checkpoint ID
            error = self._validate_checkpoint_id(
                checkpoint_id, 
                "rollback session <session-id> to <checkpoint-id>"
            )
            if error:
                return error
            
            return self._create_success_response(checkpoint_id, session_id)
        
        # Try standard format
        standard_match = re.search(self.STANDARD_FORMAT, normalized, re.IGNORECASE)
        if standard_match:
            checkpoint_id = standard_match.group(1).strip()
            
            # Validate checkpoint ID
            error = self._validate_checkpoint_id(checkpoint_id, "rollback to <checkpoint-id>")
            if error:
                return error
            
            return self._create_success_response(checkpoint_id)
        
        # Try shorthand format
        shorthand_match = re.search(self.SHORTHAND_FORMAT, normalized, re.IGNORECASE)
        if shorthand_match:
            checkpoint_id = shorthand_match.group(1).strip()
            
            # Validate checkpoint ID
            error = self._validate_checkpoint_id(checkpoint_id, "rollback <checkpoint-id>")
            if error:
                return error
            
            return self._create_success_response(checkpoint_id)
        
        # No pattern matched - invalid command
        return self._create_error_response(self.ERROR_NO_PATTERN_MATCH)
