"""
CORTEX Tier 1: API Wrapper
Unified API for Tier 1 Working Memory operations

Task 1.5: CRUD Operations API
Duration: 1.5 hours
"""

from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .conversation_manager import ConversationManager
from .entity_extractor import EntityExtractor
from .file_tracker import FileTracker
from .request_logger import RequestLogger


class Tier1API:
    """
    Unified API for Tier 1 Working Memory
    
    Provides high-level interface for:
    - Conversation management
    - Entity extraction
    - File tracking
    - Request logging
    """
    
    def __init__(self, db_path: Path, log_path: Path):
        """
        Initialize Tier 1 API
        
        Args:
            db_path: Path to SQLite database
            log_path: Path to request log file
        """
        self.conversation_manager = ConversationManager(db_path)
        self.entity_extractor = EntityExtractor()
        self.file_tracker = FileTracker()
        self.request_logger = RequestLogger(log_path)
    
    # ========================================================================
    # HIGH-LEVEL CONVERSATION OPERATIONS
    # ========================================================================
    
    def start_conversation(
        self,
        agent_id: str,
        goal: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> str:
        """
        Start a new conversation with automatic entity extraction
        
        Args:
            agent_id: Agent identifier
            goal: Conversation goal (optional)
            context: Additional context (optional)
            
        Returns:
            conversation_id: New conversation ID
        """
        conversation_id = self.conversation_manager.create_conversation(
            agent_id=agent_id,
            goal=goal,
            context=context
        )
        
        return conversation_id
    
    def process_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        extract_entities: bool = True,
        track_files: bool = True,
        log_request: bool = True
    ) -> Dict:
        """
        Process a message with automatic extraction and tracking
        
        Args:
            conversation_id: Conversation ID
            role: Message role (user/assistant)
            content: Message content
            extract_entities: Extract entities from content
            track_files: Track file references
            log_request: Log to request log
            
        Returns:
            Processing results with message_id and extracted data
        """
        # Add message to conversation
        message_id = self.conversation_manager.add_message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        
        result = {
            'message_id': message_id,
            'conversation_id': conversation_id,
            'entities': [],
            'files': [],
            'request_id': None
        }
        
        # Extract entities
        if extract_entities:
            entities = self.entity_extractor.extract_all(content)
            
            # Add entities to database
            for entity_type, entity_list in entities.items():
                for entity in entity_list:
                    entity_value = entity if isinstance(entity, str) else entity.get('name', entity.get('term', ''))
                    self.conversation_manager.add_entity(
                        conversation_id=conversation_id,
                        entity_type=entity_type,
                        entity_value=entity_value
                    )
            
            result['entities'] = entities
        
        # Track files
        if track_files:
            files = self.file_tracker.extract_files_from_text(content)
            
            # Add files to database
            for file_path in files:
                self.conversation_manager.add_file(
                    conversation_id=conversation_id,
                    file_path=file_path,
                    operation='referenced'
                )
            
            result['files'] = files
        
        # Log request
        if log_request and role == 'user':
            intent = self._detect_intent(content)
            request_id = self.request_logger.log_request(
                request_text=content,
                conversation_id=conversation_id,
                intent=intent
            )
            result['request_id'] = request_id
        
        return result
    
    def end_conversation(
        self,
        conversation_id: str,
        outcome: Optional[str] = None
    ) -> Dict:
        """
        End a conversation with summary
        
        Args:
            conversation_id: Conversation ID
            outcome: Conversation outcome
            
        Returns:
            Conversation summary
        """
        self.conversation_manager.end_conversation(
            conversation_id=conversation_id,
            outcome=outcome
        )
        
        # Get conversation summary
        conversation = self.conversation_manager.get_conversation(conversation_id)
        
        # Handle case where conversation doesn't exist or was already deleted
        if not conversation:
            return {
                'conversation_id': conversation_id,
                'duration': 0,
                'message_count': 0,
                'outcome': outcome
            }
        
        return {
            'conversation_id': conversation_id,
            'duration': self._calculate_duration(
                conversation['start_time'],
                conversation['end_time']
            ),
            'message_count': conversation['message_count'],
            'outcome': outcome
        }
    
    # ========================================================================
    # QUERY OPERATIONS
    # ========================================================================
    
    def get_active_conversation(self, agent_id: str) -> Optional[Dict]:
        """
        Get active conversation for agent
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Active conversation or None
        """
        return self.conversation_manager.get_active_conversation(agent_id)
    
    def get_conversation_history(
        self,
        conversation_id: str,
        include_entities: bool = True,
        include_files: bool = True
    ) -> Dict:
        """
        Get full conversation history
        
        Args:
            conversation_id: Conversation ID
            include_entities: Include extracted entities
            include_files: Include file references
            
        Returns:
            Complete conversation data
        """
        conversation = self.conversation_manager.get_conversation(conversation_id)
        
        if not conversation:
            return {}
        
        result = {
            'conversation': conversation,
            'messages': self.conversation_manager.get_messages(conversation_id)
        }
        
        if include_entities:
            result['entities'] = self.conversation_manager.get_entities(conversation_id)
        
        if include_files:
            result['files'] = self.conversation_manager.get_files(conversation_id)
        
        return result
    
    def search_conversations(
        self,
        agent_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        has_goal: Optional[bool] = None
    ) -> List[Dict]:
        """
        Search conversations by criteria
        
        Args:
            agent_id: Filter by agent
            start_date: Start date filter
            end_date: End date filter
            has_goal: Filter by presence of goal
            
        Returns:
            List of matching conversations
        """
        return self.conversation_manager.search_conversations(
            agent_id=agent_id,
            start_date=start_date,
            end_date=end_date,
            has_goal=has_goal
        )
    
    # ========================================================================
    # ENTITY OPERATIONS
    # ========================================================================
    
    def extract_entities_from_text(self, text: str) -> Dict:
        """
        Extract all entities from text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of extracted entities by type
        """
        return self.entity_extractor.extract_all(text)
    
    def get_entity_frequency(
        self,
        conversation_id: str,
        entity_type: Optional[str] = None
    ) -> Dict:
        """
        Get entity frequency for conversation
        
        Args:
            conversation_id: Conversation ID
            entity_type: Filter by type (optional)
            
        Returns:
            Entity frequency counts
        """
        entities = self.conversation_manager.get_entities(
            conversation_id=conversation_id,
            entity_type=entity_type
        )
        
        frequency = {}
        for entity in entities:
            value = entity['entity_value']
            frequency[value] = frequency.get(value, 0) + 1
        
        return frequency
    
    # ========================================================================
    # FILE TRACKING OPERATIONS
    # ========================================================================
    
    def track_file_modification(
        self,
        conversation_id: str,
        file_path: str,
        operation: str = 'modified'
    ):
        """
        Track a file modification
        
        Args:
            conversation_id: Conversation ID
            file_path: Path to file
            operation: Operation type (created, modified, deleted)
        """
        normalized_path = self.file_tracker._normalize_path(file_path)
        self.conversation_manager.add_file(
            conversation_id=conversation_id,
            file_path=normalized_path,
            operation=operation
        )
    
    def get_file_patterns(self, conversation_id: str) -> Dict:
        """
        Get file patterns for conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            File patterns and statistics
        """
        files = self.conversation_manager.get_files(conversation_id)
        file_paths = [f['file_path'] for f in files]
        
        patterns = self.file_tracker.get_file_patterns(file_paths)
        stats = self.file_tracker.get_file_statistics(file_paths)
        
        return {
            'patterns': patterns,
            'statistics': stats
        }
    
    # ========================================================================
    # REQUEST LOGGING OPERATIONS
    # ========================================================================
    
    def log_response(
        self,
        request_id: str,
        response_text: str,
        status: str = 'success'
    ):
        """
        Log a response to a request
        
        Args:
            request_id: Request ID
            response_text: Response content
            status: Response status
        """
        self.request_logger.log_response(
            request_id=request_id,
            response_text=response_text,
            status=status
        )
    
    def log_error(
        self,
        request_id: str,
        error_message: str,
        error_type: Optional[str] = None
    ):
        """
        Log an error for a request
        
        Args:
            request_id: Request ID
            error_message: Error description
            error_type: Error type
        """
        self.request_logger.log_error(
            request_id=request_id,
            error_message=error_message,
            error_type=error_type
        )
    
    def get_request_history(
        self,
        conversation_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get request history
        
        Args:
            conversation_id: Filter by conversation (optional)
            limit: Maximum results
            
        Returns:
            List of requests
        """
        if conversation_id:
            return self.request_logger.get_conversation_requests(conversation_id)
        else:
            return self.request_logger.get_recent_requests(limit)
    
    # ========================================================================
    # EXPORT OPERATIONS
    # ========================================================================
    
    def export_conversation_to_jsonl(
        self,
        conversation_id: str,
        output_path: Path
    ):
        """
        Export conversation to JSONL format
        
        Args:
            conversation_id: Conversation ID
            output_path: Output file path
        """
        self.conversation_manager.export_to_jsonl(
            conversation_id=conversation_id,
            output_path=output_path
        )
    
    # ========================================================================
    # STATISTICS AND MONITORING
    # ========================================================================
    
    def get_tier1_statistics(self) -> Dict:
        """
        Get comprehensive Tier 1 statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            'conversations': self.conversation_manager.get_statistics(),
            'requests': self.request_logger.get_statistics()
        }
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _detect_intent(self, text: str) -> str:
        """
        Detect intent from text
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected intent
        """
        intents = self.entity_extractor.extract_intents(text)
        return intents[0] if intents else 'unknown'
    
    def _calculate_duration(
        self,
        start_time: Optional[str],
        end_time: Optional[str]
    ) -> Optional[float]:
        """
        Calculate duration between timestamps
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            
        Returns:
            Duration in seconds or None
        """
        if not start_time or not end_time:
            return None
        
        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            return (end - start).total_seconds()
        except (ValueError, AttributeError):
            return None
