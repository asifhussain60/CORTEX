"""
Conversation repository interface.

Domain-specific repository interface for conversation entities.
"""

from abc import abstractmethod
from typing import List, Optional
from datetime import datetime
from .i_repository import IRepository


class IConversationRepository(IRepository['Conversation']):
    """
    Repository interface for conversation entities.
    
    Extends generic repository with conversation-specific queries.
    """
    
    @abstractmethod
    def find_by_namespace(self, namespace: str) -> List['Conversation']:
        """
        Find conversations by namespace.
        
        Args:
            namespace: Namespace pattern (e.g., 'workspace.myproject.*')
            
        Returns:
            List of conversations in the namespace
        """
        pass
    
    @abstractmethod
    def find_high_quality(self, min_quality: float = 0.85) -> List['Conversation']:
        """
        Find high-quality conversations.
        
        Args:
            min_quality: Minimum quality score (0.0-1.0)
            
        Returns:
            List of conversations meeting quality threshold
        """
        pass
    
    @abstractmethod
    def find_recent(self, days: int = 30) -> List['Conversation']:
        """
        Find recent conversations.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of conversations captured within the specified days
        """
        pass
    
    @abstractmethod
    def find_by_tags(self, tags: List[str]) -> List['Conversation']:
        """
        Find conversations by tags.
        
        Args:
            tags: List of tag names to search for
            
        Returns:
            List of conversations containing any of the specified tags
        """
        pass
    
    @abstractmethod
    def find_similar(self, conversation_id: int, threshold: float = 0.80) -> List['Conversation']:
        """
        Find similar conversations.
        
        Args:
            conversation_id: Reference conversation ID
            threshold: Similarity threshold (0.0-1.0)
            
        Returns:
            List of conversations similar to the reference
        """
        pass
    
    @abstractmethod
    def get_entity_count(self, conversation_id: int) -> int:
        """
        Get entity count for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Number of entities extracted from the conversation
        """
        pass
