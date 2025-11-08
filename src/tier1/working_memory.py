"""
CORTEX Tier 1: Working Memory (Modularized)
Short-term memory storage with FIFO queue (20 conversation limit).

This is a facade that coordinates between modular components while maintaining
backward compatibility with the original API.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# Import modular components
from .conversations import ConversationManager, ConversationSearch, Conversation
from .messages import MessageStore
from .entities import EntityExtractor, EntityType, Entity
from .fifo import QueueManager


class WorkingMemory:
    """
    Tier 1: Working Memory (Short-Term Memory) - Modular Facade
    
    Manages recent conversations with FIFO eviction when capacity (20) is reached.
    Stores conversations, messages, and extracted entities in SQLite.
    
    This class acts as a facade, delegating to specialized modules while
    maintaining full backward compatibility with the original API.
    """
    
    MAX_CONVERSATIONS = 20
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize working memory.
        
        Args:
            db_path: Path to SQLite database. If None, uses default location.
        """
        if db_path is None:
            db_path = Path("cortex-brain/tier1/working_memory.db")
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_database()
        
        # Initialize modular components
        self.conversation_manager = ConversationManager(self.db_path)
        self.conversation_search = ConversationSearch(self.db_path)
        self.message_store = MessageStore(self.db_path)
        self.entity_extractor = EntityExtractor(self.db_path)
        self.queue_manager = QueueManager(self.db_path)
    
    def _init_database(self) -> None:
        """Initialize database schema."""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 0,
                summary TEXT,
                tags TEXT
            )
        """)
        
        # Create entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_name TEXT NOT NULL,
                file_path TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 1,
                UNIQUE(entity_type, entity_name, file_path)
            )
        """)
        
        # Create conversation-entity relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_entities (
                conversation_id TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                relevance_score REAL DEFAULT 1.0,
                PRIMARY KEY (conversation_id, entity_id),
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
                FOREIGN KEY (entity_id) REFERENCES entities(id)
            )
        """)
        
        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        """)
        
        # Create eviction log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eviction_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_created 
            ON conversations(created_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_active 
            ON conversations(is_active)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_entities_type 
            ON entities(entity_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_entities_accessed 
            ON entities(last_accessed DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation 
            ON messages(conversation_id)
        """)
        
        conn.commit()
        conn.close()
    
    # ========== Conversation Management (Delegated) ==========
    
    def add_conversation(
        self,
        conversation_id: str,
        title: str,
        messages: List[Dict[str, str]],
        tags: Optional[List[str]] = None
    ) -> Conversation:
        """
        Add a new conversation to working memory.
        
        Args:
            conversation_id: Unique conversation identifier
            title: Conversation title
            messages: List of message dicts with 'role' and 'content'
            tags: Optional list of tags
        
        Returns:
            Created Conversation object
        """
        # Enforce FIFO limit before adding
        self.queue_manager.enforce_fifo_limit()
        
        # Add conversation
        conversation = self.conversation_manager.add_conversation(
            conversation_id=conversation_id,
            title=title,
            message_count=len(messages),
            tags=tags
        )
        
        # Add messages
        self.message_store.add_messages(conversation_id, messages)
        
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self.conversation_manager.get_conversation(conversation_id)
    
    def get_recent_conversations(self, limit: int = 20) -> List[Conversation]:
        """Get recent conversations ordered by creation date (newest first)."""
        return self.conversation_manager.get_recent_conversations(limit)
    
    def set_active_conversation(self, conversation_id: str) -> None:
        """Mark a conversation as active."""
        self.conversation_manager.set_active_conversation(conversation_id)
    
    def get_active_conversation(self) -> Optional[Conversation]:
        """Get the currently active conversation."""
        return self.conversation_manager.get_active_conversation()
    
    def update_conversation(
        self,
        conversation_id: str,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """Update conversation properties."""
        self.conversation_manager.update_conversation(conversation_id, title, summary, tags)
    
    def get_conversation_count(self) -> int:
        """Get the total number of conversations in working memory."""
        return self.conversation_manager.get_conversation_count()
    
    # ========== Message Management (Delegated) ==========
    
    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a conversation."""
        return self.message_store.get_messages(conversation_id)
    
    def add_messages(
        self,
        conversation_id: str,
        messages: List[Dict[str, str]]
    ) -> None:
        """Append new messages to an existing conversation."""
        self.message_store.add_messages(conversation_id, messages)
        self.conversation_manager.increment_message_count(conversation_id, len(messages))
    
    # ========== Entity Extraction (Delegated) ==========
    
    def extract_entities(self, conversation_id: str) -> List[Entity]:
        """Extract entities from a conversation's messages."""
        messages = self.message_store.get_messages(conversation_id)
        
        if not messages:
            return []
        
        # Combine all message content
        text = " ".join(msg['content'] for msg in messages)
        
        return self.entity_extractor.extract_entities(conversation_id, text)
    
    def get_conversation_entities(self, conversation_id: str) -> List[Entity]:
        """Get all entities associated with a conversation."""
        return self.entity_extractor.get_conversation_entities(conversation_id)
    
    def get_entity_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics on entity usage."""
        return self.entity_extractor.get_entity_statistics()
    
    # ========== Search Operations (Delegated) ==========
    
    def search_conversations(self, keyword: str) -> List[Conversation]:
        """Search conversations by keyword in title or messages."""
        return self.conversation_search.search_by_keyword(keyword)
    
    def find_conversations_with_entity(
        self,
        entity_type: EntityType,
        entity_name: str
    ) -> List[Conversation]:
        """Find conversations that mention a specific entity."""
        return self.conversation_search.search_by_entity(entity_type.value, entity_name)
    
    def get_conversations_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Conversation]:
        """Get conversations within a date range."""
        return self.conversation_search.search_by_date_range(start_date, end_date)
    
    # ========== Queue Management (Delegated) ==========
    
    def get_eviction_log(self) -> List[Dict[str, Any]]:
        """Get the eviction log."""
        return self.queue_manager.get_eviction_log()
    
    def _enforce_fifo_limit(self) -> None:
        """Enforce FIFO limit (maintained for compatibility, delegates to QueueManager)."""
        self.queue_manager.enforce_fifo_limit()
    
    # ========== Utility Methods ==========
    
    def close(self) -> None:
        """Close any open connections (for cleanup in tests)."""
        # SQLite connections are per-operation, so nothing to close
        pass
