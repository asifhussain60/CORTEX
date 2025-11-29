"""
Tier 1 Unified API
-----------------
High-level wrapper combining all Tier 1 components (ConversationManager,
EntityExtractor, FileTracker) into a single, easy-to-use interface.

This is the PRIMARY entry point for CORTEX agents to interact with Tier 1 storage.

Design Philosophy:
- Single Responsibility: This class ONLY coordinates Tier 1 components
- Auto-extraction: Automatically extracts entities and tracks files from conversations
- Smart defaults: Reasonable defaults for all operations
- Performance: <100ms for common operations

Example Usage:
    from src.brain.tier1.tier1_api import Tier1API
    
    # Initialize
    api = Tier1API(db_path="cortex-brain/tier1/conversations.db")
    
    # Log a conversation (auto-extracts entities and tracks files)
    conv_id = api.log_conversation(
        agent_name="copilot",
        request="Fix bug in auth.py",
        response="Fixed authentication issue",
        related_files=["src/auth.py"]
    )
    
    # Search conversations
    results = api.search("authentication bug")
    
    # Get co-modified files
    patterns = api.get_file_patterns("src/auth.py", min_confidence=0.3)
"""

from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
import logging
from datetime import datetime

from .conversation_manager import ConversationManager
from .entity_extractor import EntityExtractor
from .file_tracker import FileTracker
from .request_logger import RequestLogger
from src.config import ConfigManager


logger = logging.getLogger(__name__)


class Tier1API:
    """
    Unified API for all Tier 1 operations.
    
    This class provides a high-level interface that automatically:
    - Extracts entities from conversations
    - Tracks file relationships
    - Manages FIFO queue (20 conversation limit)
    - Provides search functionality
    - Exports patterns to Tier 2
    
    Attributes:
        conversation_manager: Handles conversation CRUD operations
        entity_extractor: Extracts entities and intents from text
        file_tracker: Tracks file modifications and patterns
        request_logger: Logs raw requests with privacy-aware redaction
    """
    
    def __init__(self, db_path: str = None, enable_raw_logging: bool = True):
        """
        Initialize Tier 1 API with all components.
        
        Args:
            db_path: Path to SQLite database (deprecated - use ConfigManager)
            enable_raw_logging: Whether to log raw requests (default True)
        """
        # Use ConfigManager for tier-specific paths (CORTEX 2.0 distributed architecture)
        if db_path is None:
            config = ConfigManager()
            db_path = config.get_tier1_conversations_path()
        
        self.db_path = Path(db_path)
        self.conversation_manager = ConversationManager(str(self.db_path))
        self.entity_extractor = EntityExtractor()
        self.file_tracker = FileTracker(str(self.db_path))
        self.request_logger = RequestLogger(str(self.db_path)) if enable_raw_logging else None
        
        logger.info(f"Tier1API initialized with database: {self.db_path}, raw_logging={enable_raw_logging}")
    
    def log_conversation(
        self,
        agent_name: str,
        request: str,
        response: str,
        related_files: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        auto_extract: bool = True
    ) -> str:
        """
        Log a complete conversation with automatic entity extraction and file tracking.
        
        This is the PRIMARY method for logging agent conversations. It automatically:
        1. Creates a conversation record
        2. Adds request and response messages
        3. Extracts entities (files, components, features)
        4. Tracks file relationships
        5. Enforces FIFO queue (deletes oldest if >20 conversations)
        
        Args:
            agent_name: Name of agent (e.g., "copilot", "claude")
            request: User's request text
            response: Agent's response text
            related_files: Optional list of file paths
            metadata: Optional metadata (e.g., {"session_id": "abc123"})
            auto_extract: Whether to auto-extract entities (default True)
        
        Returns:
            conversation_id: UUID of created conversation
        
        Example:
            conv_id = api.log_conversation(
                agent_name="copilot",
                request="Add logging to database.py",
                response="Added logging statements to all methods",
                related_files=["src/database.py"]
            )
        """
        # Step 1: Extract entities if enabled
        extracted_files = []
        extracted_entities = {}
        extracted_intents = []
        
        if auto_extract:
            # Extract from request
            request_entities = self.entity_extractor.extract_entities(request)
            extracted_files.extend(request_entities.get('files', []))
            
            # Extract from response
            response_entities = self.entity_extractor.extract_entities(response)
            extracted_files.extend(response_entities.get('files', []))
            
            # Combine all entities
            extracted_entities = {
                'files': list(set(extracted_files)),  # Deduplicate
                'components': list(set(
                    request_entities.get('components', []) +
                    response_entities.get('components', [])
                )),
                'features': list(set(
                    request_entities.get('features', []) +
                    response_entities.get('features', [])
                ))
            }
            
            # Extract intents
            extracted_intents = self.entity_extractor.extract_intents(request)
        
        # Step 2: Combine manual and extracted files
        all_files = list(set((related_files or []) + extracted_files))
        
        # Step 3: Create conversation
        conv_id = self.conversation_manager.create_conversation(
            agent_name=agent_name,
            related_files=all_files,
            metadata=metadata
        )
        
        # Step 4: Add request message
        self.conversation_manager.add_message(
            conversation_id=conv_id,
            role="user",
            content=request,
            extracted_entities=extracted_entities if auto_extract else None
        )
        
        # Step 5: Add response message
        self.conversation_manager.add_message(
            conversation_id=conv_id,
            role="assistant",
            content=response,
            extracted_entities=extracted_entities if auto_extract else None
        )
        
        # Step 6: Track file relationships
        if len(all_files) > 0:
            self.file_tracker.track_files(conv_id, all_files)
        
        # Step 7: Log raw request/response (privacy-aware)
        if self.request_logger:
            self.request_logger.log_raw_request(
                raw_request=request,
                raw_response=response,
                agent_name=agent_name,
                conversation_id=conv_id,
                metadata=metadata
            )
        
        logger.info(
            f"Logged conversation {conv_id}: agent={agent_name}, "
            f"files={len(all_files)}, intents={extracted_intents}"
        )
        
        return conv_id
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        auto_extract: bool = True
    ) -> int:
        """
        Add a message to an existing conversation with auto-extraction.
        
        Args:
            conversation_id: UUID of conversation
            role: "user" or "assistant"
            content: Message text
            auto_extract: Whether to auto-extract entities (default True)
        
        Returns:
            message_id: Integer ID of created message
        """
        extracted_entities = None
        
        if auto_extract:
            entities = self.entity_extractor.extract_entities(content)
            extracted_entities = {
                'files': entities.get('files', []),
                'components': entities.get('components', []),
                'features': entities.get('features', [])
            }
            
            # Update conversation's related_files if new files found
            if entities.get('files'):
                conv = self.conversation_manager.get_conversation(conversation_id)
                if conv:
                    existing_files = conv.get('related_files', [])
                    new_files = list(set(existing_files + entities['files']))
                    self.conversation_manager.update_conversation(
                        conversation_id,
                        related_files=new_files
                    )
                    self.file_tracker.track_files(conversation_id, new_files)
        
        return self.conversation_manager.add_message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            extracted_entities=extracted_entities
        )
    
    def search(
        self,
        query: str,
        limit: int = 10,
        include_messages: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search conversations using full-text search.
        
        This uses SQLite FTS5 for fast, relevant search results.
        
        Args:
            query: Search query (supports AND, OR, NOT, quotes, *)
            limit: Maximum results (default 10)
            include_messages: Whether to include full message list (default True)
        
        Returns:
            List of conversation dicts with relevance scores
        
        Example:
            results = api.search("authentication bug", limit=5)
            for conv in results:
                print(f"Score: {conv['rank']}, Files: {conv['related_files']}")
        """
        return self.conversation_manager.search_conversations(
            query=query,
            limit=limit,
            include_messages=include_messages
        )
    
    def get_conversation(
        self,
        conversation_id: str,
        include_messages: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get a single conversation by ID.
        
        Args:
            conversation_id: UUID of conversation
            include_messages: Whether to include message list (default True)
        
        Returns:
            Conversation dict or None if not found
        """
        return self.conversation_manager.get_conversation(
            conversation_id,
            include_messages=include_messages
        )
    
    def get_recent_conversations(
        self,
        limit: int = 20,
        include_messages: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get most recent conversations (ordered by created_at DESC).
        
        Args:
            limit: Maximum results (default 20)
            include_messages: Whether to include message lists (default True)
        
        Returns:
            List of conversation dicts
        """
        return self.conversation_manager.get_recent_conversations(
            limit=limit,
            include_messages=include_messages
        )
    
    def get_file_patterns(
        self,
        file_path: str,
        min_confidence: float = 0.2,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get files frequently co-modified with the given file.
        
        This is useful for predicting which other files might need changes
        when modifying a specific file.
        
        Args:
            file_path: Path to file (e.g., "src/auth.py")
            min_confidence: Minimum confidence score (0.0-1.0, default 0.2)
            limit: Maximum results (default 10)
        
        Returns:
            List of {file_b, co_modifications, confidence, last_modified} dicts
        
        Example:
            patterns = api.get_file_patterns("src/auth.py", min_confidence=0.3)
            for p in patterns:
                print(f"{p['file_b']}: {p['confidence']:.1%} confidence")
        """
        return self.file_tracker.detect_co_modifications(
            file_path=file_path,
            min_confidence=min_confidence,
            limit=limit
        )
    
    def export_patterns_to_tier2(
        self,
        min_confidence: float = 0.3,
        limit: int = 100
    ) -> int:
        """
        Export high-confidence file patterns to Tier 2 for pattern learning.
        
        This is typically called periodically (e.g., once per day) to transfer
        learned patterns from Tier 1 (conversation-based) to Tier 2 (knowledge graph).
        
        Args:
            min_confidence: Minimum confidence to export (default 0.3)
            limit: Maximum patterns to export (default 100)
        
        Returns:
            Number of patterns exported
        
        Example:
            count = api.export_patterns_to_tier2(min_confidence=0.4)
            print(f"Exported {count} patterns to Tier 2")
        """
        patterns = self.file_tracker.export_for_tier2(
            min_confidence=min_confidence,
            limit=limit
        )
        
        # Note: This returns the patterns for export. The actual Tier 2 sync
        # is handled by sync_to_tier2() which will be implemented in Sub-Group 3C
        
        logger.info(f"Exported {len(patterns)} patterns to Tier 2")
        return len(patterns)
    
    def resolve_reference(
        self,
        reference: str,
        conversation_id: str
    ) -> Optional[str]:
        """
        Resolve an ambiguous reference (e.g., "it", "that file") to a concrete entity.
        
        This uses conversation context to resolve pronouns and vague references.
        
        Args:
            reference: Ambiguous reference text
            conversation_id: UUID of conversation for context
        
        Returns:
            Resolved entity or None if not resolvable
        
        Example:
            # User: "Fix the bug in auth.py"
            # Agent: "Done"
            # User: "Now add tests for it"
            resolved = api.resolve_reference("it", conv_id)
            # Returns: "auth.py"
        """
        # Get conversation context
        conv = self.conversation_manager.get_conversation(
            conversation_id,
            include_messages=True
        )
        
        if not conv or not conv.get('messages'):
            return None
        
        # Build context string from recent messages (last 5)
        recent_messages = conv['messages'][-5:]
        context = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in recent_messages
        ])
        
        return self.entity_extractor.resolve_reference(reference, context)
    
    def get_conversation_summary(self, conversation_id: str) -> Optional[str]:
        """
        Get a brief summary of a conversation (first user message).
        
        Args:
            conversation_id: UUID of conversation
        
        Returns:
            Summary text or None if not found
        """
        conv = self.conversation_manager.get_conversation(
            conversation_id,
            include_messages=True
        )
        
        if not conv or not conv.get('messages'):
            return None
        
        # Return first user message (truncated to 100 chars)
        first_message = conv['messages'][0]['content']
        return first_message[:100] + "..." if len(first_message) > 100 else first_message
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get Tier 1 statistics for monitoring and debugging.
        
        Returns:
            Dict with conversation count, message count, file count, etc.
        
        Example:
            stats = api.get_stats()
            print(f"Total conversations: {stats['total_conversations']}")
            print(f"Total messages: {stats['total_messages']}")
            print(f"Unique files tracked: {stats['unique_files']}")
        """
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get conversation count
        cursor.execute("SELECT COUNT(*) FROM tier1_conversations")
        total_conversations = cursor.fetchone()[0]
        
        # Get message count
        cursor.execute("SELECT COUNT(*) FROM tier1_messages")
        total_messages = cursor.fetchone()[0]
        
        # Get unique files tracked
        cursor.execute("""
            SELECT COUNT(DISTINCT file_a)
            FROM (
                SELECT file_a FROM tier1_file_tracking
                UNION
                SELECT file_b FROM tier1_file_tracking
            )
        """)
        unique_files = cursor.fetchone()[0]
        
        # Get file relationship count
        cursor.execute("SELECT COUNT(*) FROM tier1_file_tracking")
        total_relationships = cursor.fetchone()[0]
        
        # Get oldest and newest conversation dates
        cursor.execute("""
            SELECT MIN(created_at), MAX(created_at)
            FROM tier1_conversations
        """)
        oldest, newest = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'unique_files': unique_files,
            'total_relationships': total_relationships,
            'oldest_conversation': oldest,
            'newest_conversation': newest,
            'fifo_limit': 20,
            'database_path': str(self.db_path)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Tier 1 system.
        
        Returns:
            Dict with status, warnings, and performance metrics
        
        Example:
            health = api.health_check()
            if not health['healthy']:
                print(f"Warnings: {health['warnings']}")
        """
        warnings = []
        
        # Check FIFO queue size
        stats = self.get_stats()
        if stats['total_conversations'] > 20:
            warnings.append(
                f"FIFO queue exceeded: {stats['total_conversations']} > 20 conversations"
            )
        
        # Check database file exists
        if not self.db_path.exists():
            warnings.append(f"Database file not found: {self.db_path}")
        
        # Check FTS5 index exists
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type='table' AND name='tier1_conversations_fts'
        """)
        has_fts = cursor.fetchone()[0] > 0
        conn.close()
        
        if not has_fts:
            warnings.append("FTS5 index missing: tier1_conversations_fts")
        
        return {
            'healthy': len(warnings) == 0,
            'warnings': warnings,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }


# Convenience function for quick initialization
def get_tier1_api(db_path: str = None) -> Tier1API:
    """
    Convenience function to get a Tier1API instance.
    
    Args:
        db_path: Path to SQLite database (deprecated - use ConfigManager)
    
    Returns:
        Initialized Tier1API instance
    
    Example:
        from src.brain.tier1.tier1_api import get_tier1_api
        
        api = get_tier1_api()
        api.log_conversation(...)
    """
    return Tier1API(db_path)
