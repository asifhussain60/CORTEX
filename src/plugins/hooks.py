"""
Plugin Hook Definitions for CORTEX 2.0

Centralizes all plugin lifecycle hooks for consistency.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from enum import Enum


class HookPoint(Enum):
    """
    Lifecycle hooks for plugin execution.
    
    Plugins register for hooks to execute at specific points
    in the CORTEX lifecycle.
    """
    
    # System lifecycle
    ON_STARTUP = "on_startup"
    ON_SHUTDOWN = "on_shutdown"
    
    # Documentation hooks
    ON_DOC_REFRESH = "on_doc_refresh"
    
    # Maintenance hooks
    ON_SELF_REVIEW = "on_self_review"
    ON_BRAIN_UPDATE = "on_brain_update"
    
    # Conversation lifecycle
    ON_CONVERSATION_START = "on_conversation_start"
    ON_CONVERSATION_END = "on_conversation_end"
    
    # Error handling
    ON_ERROR = "on_error"
    
    # Extension scaffolding
    ON_EXTENSION_SCAFFOLD = "on_extension_scaffold"
    
    # Workflow hooks
    ON_WORKFLOW_START = "on_workflow_start"
    ON_WORKFLOW_END = "on_workflow_end"
    ON_WORKFLOW_ERROR = "on_workflow_error"
    
    # Agent hooks
    ON_AGENT_EXECUTION = "on_agent_execution"
    ON_AGENT_ERROR = "on_agent_error"
