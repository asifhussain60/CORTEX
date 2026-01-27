"""Knowledge Protocol specification and message types."""

from typing import Any, Dict, List
from dataclasses import dataclass
from enum import Enum


class MessageType(Enum):
    """Protocol message types."""

    QUERY = "query"
    RESULT = "result"
    UPDATE = "update"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"


@dataclass
class QueryMessage:
    """Query message type."""

    message_id: str
    query: str
    filters: Dict[str, Any]

    def __post_init__(self) -> None:
        """Validate message."""
        if not self.message_id:
            raise ValueError("message_id cannot be empty")
        if not self.query:
            raise ValueError("query cannot be empty")


@dataclass
class ResultMessage:
    """Result message type."""

    message_id: str
    query_id: str
    results: List[Dict[str, Any]]
    count: int

    def __post_init__(self) -> None:
        """Validate message."""
        if not self.message_id:
            raise ValueError("message_id cannot be empty")
        if not self.query_id:
            raise ValueError("query_id cannot be empty")
        if self.count < 0:
            raise ValueError("count cannot be negative")


@dataclass
class UpdateMessage:
    """Update message type."""

    message_id: str
    entity_id: str
    changes: Dict[str, Any]

    def __post_init__(self) -> None:
        """Validate message."""
        if not self.message_id:
            raise ValueError("message_id cannot be empty")
        if not self.entity_id:
            raise ValueError("entity_id cannot be empty")


@dataclass
class SubscribeMessage:
    """Subscribe message type."""

    message_id: str
    subscription_id: str
    topic: str

    def __post_init__(self) -> None:
        """Validate message."""
        if not self.message_id:
            raise ValueError("message_id cannot be empty")
        if not self.subscription_id:
            raise ValueError("subscription_id cannot be empty")
        if not self.topic:
            raise ValueError("topic cannot be empty")


@dataclass
class UnsubscribeMessage:
    """Unsubscribe message type."""

    message_id: str
    subscription_id: str

    def __post_init__(self) -> None:
        """Validate message."""
        if not self.message_id:
            raise ValueError("message_id cannot be empty")
        if not self.subscription_id:
            raise ValueError("subscription_id cannot be empty")


class KnowledgeProtocolSpec:
    """Knowledge Protocol specification."""

    def __init__(self) -> None:
        """Initialize protocol specification."""
        self.version = "1.0"
        self.message_types = MessageType
        self.constraints = {
            "max_query_length": 10000,
            "max_result_count": 10000,
            "max_filters": 50,
            "required_message_id": True,
            "required_timestamps": False,
        }

    def validate_message_id(self, message_id: str) -> bool:
        """Validate message ID format.
        
        Args:
            message_id: Message ID to validate
            
        Returns:
            True if valid
        """
        return bool(message_id) and len(message_id) > 0

    def validate_query_length(self, query: str) -> bool:
        """Validate query length constraint.
        
        Args:
            query: Query string
            
        Returns:
            True if valid
        """
        return len(query) <= self.constraints["max_query_length"]

    def validate_result_count(self, count: int) -> bool:
        """Validate result count constraint.
        
        Args:
            count: Number of results
            
        Returns:
            True if valid
        """
        return count <= self.constraints["max_result_count"] and count >= 0

    def get_specification(self) -> Dict[str, Any]:
        """Get full protocol specification.
        
        Returns:
            Specification dictionary
        """
        return {
            "version": self.version,
            "message_types": [t.value for t in MessageType],
            "constraints": self.constraints,
            "description": "Knowledge Protocol for knowledge entity sharing and updates"
        }
