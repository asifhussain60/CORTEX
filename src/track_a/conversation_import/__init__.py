"""
Conversation Import Module
=========================

Purpose: Manual conversation capture and import interface.
Provides user-facing functionality for importing captured conversations.

Components:
- ConversationImporter: Main import orchestrator
- ValidationRules: Conversation structure validation
- ImportReport: Import status and analytics

Status: Phase 1.2 (Week 1-2)
"""

from .conversation_importer import ConversationImporter

__all__ = ["ConversationImporter"]
