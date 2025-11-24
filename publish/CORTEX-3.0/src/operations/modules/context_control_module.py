"""
Context Control Module - User commands to manage Tier 1 memory

This module provides user control over CORTEX's memory with commands like
forget [topic], clear context, and show context.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Any
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationResult,
    OperationModuleMetadata,
    OperationPhase,
    OperationStatus
)


class ContextControlModule(BaseOperationModule):
    """
    Provides user control commands for Tier 1 context management.
    
    Commands:
    - show context: Display loaded conversations
    - forget [topic]: Remove conversations about specific topic
    - clear context: Clear all Tier 1 memory (requires confirmation)
    """
    
    # Natural language triggers for commands
    SHOW_TRIGGERS = [
        "show context", "what do you remember", "what's in memory",
        "show memory", "context status", "what context is loaded",
        "display context", "view context"
    ]
    
    FORGET_TRIGGERS = [
        "forget", "remove from memory", "delete conversation",
        "forget about", "remove context", "clear topic"
    ]
    
    CLEAR_TRIGGERS = [
        "clear context", "clear memory", "reset memory",
        "forget everything", "clear all context", "wipe memory"
    ]
    
    def __init__(self, working_memory=None):
        super().__init__()
        self.module_name = "context_control"
        self.working_memory = working_memory
        self.pending_confirmation = None  # Store pending destructive operation
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="context_control",
            name="Context Control Module",
            description="User commands to manage Tier 1 memory (show, forget, clear)",
            phase=OperationPhase.PROCESSING,
            priority=50,
            version="1.0",
            author="Asif Hussain",
            tags=["tier1", "context", "control", "memory"]
        )
    
    def execute(self, operation_data: Dict[str, Any]) -> OperationResult:
        """
        Execute context control command.
        
        Args:
            operation_data: Contains:
                - command: show | forget | clear
                - topic: For forget command
                - confirmed: For destructive operations
                - user_request: Original request
        
        Returns:
            OperationResult with command execution result
        """
        user_request = operation_data.get('user_request', '')
        command = self._detect_command(user_request)
        
        if command == "show":
            return self._handle_show_context(operation_data)
        elif command == "forget":
            return self._handle_forget_topic(operation_data)
        elif command == "clear":
            return self._handle_clear_context(operation_data)
        else:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Unknown context control command",
                data={},
                duration_seconds=0.0
            )
    
    def _detect_command(self, user_request: str) -> str:
        """
        Detect which command user wants.
        
        Args:
            user_request: User's natural language request
        
        Returns:
            Command type: show | forget | clear | unknown
        """
        request_lower = user_request.lower()
        
        # Check clear triggers FIRST (before forget, since "forget everything" should be clear)
        if any(trigger in request_lower for trigger in self.CLEAR_TRIGGERS):
            return "clear"
        
        # Check show triggers
        if any(trigger in request_lower for trigger in self.SHOW_TRIGGERS):
            return "show"
        
        # Check forget triggers LAST
        if any(trigger in request_lower for trigger in self.FORGET_TRIGGERS):
            return "forget"
        
        return "unknown"
    
    def _handle_show_context(self, operation_data: Dict[str, Any]) -> OperationResult:
        """
        Handle show context command.
        
        Args:
            operation_data: Operation parameters
        
        Returns:
            OperationResult with context display instructions
        """
        # Delegate to context_display_module
        return OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Use context_display_module to show context",
            data={
                "action": "show_context",
                "command": "show context"
            },
            duration_seconds=0.0
        )
    
    def _handle_forget_topic(self, operation_data: Dict[str, Any]) -> OperationResult:
        """
        Handle forget [topic] command.
        
        Args:
            operation_data: Contains topic to forget
        
        Returns:
            OperationResult with forget operation result
        """
        user_request = operation_data.get('user_request', '')
        topic = self._extract_topic(user_request)
        
        if not topic:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Please specify what to forget (e.g., 'forget authentication')",
                data={},
                duration_seconds=0.0
            )
        
        if not self.working_memory:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Working memory not available",
                data={},
                duration_seconds=0.0
            )
        
        # Find and remove conversations about topic
        removed_count = self._remove_topic_conversations(topic)
        
        return OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message=f"Removed {removed_count} conversation(s) about '{topic}'",
            data={
                "topic": topic,
                "removed_count": removed_count
            },
            duration_seconds=0.0
        )
    
    def _handle_clear_context(self, operation_data: Dict[str, Any]) -> OperationResult:
        """
        Handle clear context command (requires confirmation).
        
        Args:
            operation_data: Contains confirmation status
        
        Returns:
            OperationResult with clear operation result
        """
        confirmed = operation_data.get('confirmed', False)
        
        if not confirmed:
            # Request confirmation
            self.pending_confirmation = "clear_context"
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message="⚠️ This will clear ALL context memory. Type 'yes, clear context' to confirm.",
                data={
                    "requires_confirmation": True,
                    "pending_action": "clear_context"
                },
                duration_seconds=0.0
            )
        
        if not self.working_memory:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Working memory not available",
                data={},
                duration_seconds=0.0
            )
        
        # Clear all conversations
        cleared_count = self._clear_all_conversations()
        
        return OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message=f"✅ Cleared {cleared_count} conversation(s) from memory",
            data={
                "cleared_count": cleared_count
            },
            duration_seconds=0.0
        )
    
    def _extract_topic(self, user_request: str) -> Optional[str]:
        """
        Extract topic to forget from user request.
        
        Args:
            user_request: User's natural language request
        
        Returns:
            Topic string or None
        """
        request_lower = user_request.lower()
        
        # Common patterns
        patterns = [
            "forget about ",
            "forget ",
            "remove from memory ",
            "delete conversation about ",
            "clear topic "
        ]
        
        for pattern in patterns:
            if pattern in request_lower:
                # Extract everything after pattern
                topic = request_lower.split(pattern, 1)[1].strip()
                # Remove common suffixes
                for suffix in [" from memory", " please", " context"]:
                    topic = topic.replace(suffix, "")
                return topic.strip()
        
        return None
    
    def _remove_topic_conversations(self, topic: str) -> int:
        """
        Remove conversations matching topic.
        
        Args:
            topic: Topic to remove
        
        Returns:
            Number of conversations removed
        """
        if not self.working_memory:
            return 0
        
        # Get all conversations
        conversations = self.working_memory.get_recent_conversations(limit=20)
        
        removed_count = 0
        for conv in conversations:
            # Check if conversation is about topic
            summary = conv.get('summary', '').lower()
            entities = conv.get('entities', {})
            
            # Match in summary
            if topic.lower() in summary:
                conv_id = conv.get('conversation_id')
                if conv_id:
                    self.working_memory.remove_conversation(conv_id)
                    removed_count += 1
                continue
            
            # Match in entities
            for entity_list in entities.values():
                if any(topic.lower() in str(e).lower() for e in entity_list):
                    conv_id = conv.get('conversation_id')
                    if conv_id:
                        self.working_memory.remove_conversation(conv_id)
                        removed_count += 1
                    break
        
        return removed_count
    
    def _clear_all_conversations(self) -> int:
        """
        Clear all conversations from working memory.
        
        Returns:
            Number of conversations cleared
        """
        if not self.working_memory:
            return 0
        
        # Get count before clearing
        conversations = self.working_memory.get_recent_conversations(limit=20)
        count = len(conversations)
        
        # Clear all
        for conv in conversations:
            conv_id = conv.get('conversation_id')
            if conv_id:
                self.working_memory.remove_conversation(conv_id)
        
        return count
    
    def can_handle(self, operation_type: str) -> bool:
        """Check if this module can handle the operation."""
        return operation_type in [
            "context_control",
            "show_context",
            "forget_topic",
            "clear_context"
        ]
    
    def detect_trigger(self, user_request: str) -> bool:
        """
        Detect if user request matches any context control triggers.
        
        Args:
            user_request: User's natural language request
        
        Returns:
            True if matches control command trigger
        """
        command = self._detect_command(user_request)
        return command != "unknown"
