"""
CORTEX Brain - Tier 1 Package

Tier 1: Working Memory (Short-term Conversation History)

Purpose: Manage last 20 conversations with full message history
FIFO Queue: When conversation #21 starts, #1 gets deleted
Performance: <100ms read for active conversation + recent 19

Components:
- Tier1API: Unified high-level interface (RECOMMENDED)
- ConversationManager: Core CRUD operations for conversations
- EntityExtractor: Extract and link entities from messages
- FileTracker: Track file modifications per conversation
- RequestLogger: Log raw requests with privacy-aware redaction

Recommended Usage:
    from src.brain.tier1 import Tier1API
    
    api = Tier1API()  # Uses ConfigManager for tier-specific path
    conv_id = api.log_conversation(
        agent_name="copilot",
        request="Fix bug in auth.py",
        response="Fixed authentication issue"
    )
"""

__version__ = "1.0.0"
__all__ = [
    "Tier1API",
    "get_tier1_api",
    "ConversationManager",
    "EntityExtractor",
    "FileTracker",
    "RequestLogger",
    "get_request_logger"
]

from .tier1_api import Tier1API, get_tier1_api
from .conversation_manager import ConversationManager
from .entity_extractor import EntityExtractor
from .file_tracker import FileTracker
from .request_logger import RequestLogger, get_request_logger
