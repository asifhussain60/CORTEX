"""
Session management for CORTEX Tier 1 Working Memory.

Provides workspace session tracking and conversation boundary detection.
"""

from .session_manager import SessionManager, Session

__all__ = ['SessionManager', 'Session']
