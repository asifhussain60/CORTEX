"""
CORTEX 3.0 - Conversation Capture Package
=========================================

Manual conversation capture system for solving the amnesia problem immediately.

Two-step workflow:
1. User: "capture conversation" → Creates capture file
2. User copies conversation → Pastes into file  
3. User: "import conversation [id]" → Imports to CORTEX brain

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Quick Win #5.1 (Week 2)
Effort: 20 hours total
Target: 100% capture success rate, immediate amnesia solution
"""

from .capture_manager import ConversationCaptureManager
from .command_processor import CaptureCommandProcessor, process_capture_command

# Export main interfaces
__all__ = [
    'ConversationCaptureManager',
    'CaptureCommandProcessor', 
    'process_capture_command'
]

# Version and feature info
__version__ = '3.0.0'
__feature__ = 'Quick Win 5.1: Manual Conversation Capture'
__status__ = 'Production Ready'