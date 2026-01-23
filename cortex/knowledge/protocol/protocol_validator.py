"""Protocol validator for validating knowledge protocol messages."""

from typing import Union, Any
from cortex.knowledge.protocol.knowledge_protocol_spec import (
    QueryMessage,
    ResultMessage,
    UpdateMessage,
    SubscribeMessage,
    UnsubscribeMessage,
    KnowledgeProtocolSpec,
)


class ProtocolValidator:
    """Validator for knowledge protocol messages."""

    def __init__(self) -> None:
        """Initialize validator."""
        self.spec = KnowledgeProtocolSpec()

    def validate(
        self,
        message: Union[
            QueryMessage,
            ResultMessage,
            UpdateMessage,
            SubscribeMessage,
            UnsubscribeMessage,
        ]
    ) -> bool:
        """Validate a protocol message.
        
        Args:
            message: Message to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if isinstance(message, QueryMessage):
                return self._validate_query(message)
            elif isinstance(message, ResultMessage):
                return self._validate_result(message)
            elif isinstance(message, UpdateMessage):
                return self._validate_update(message)
            elif isinstance(message, SubscribeMessage):
                return self._validate_subscribe(message)
            elif isinstance(message, UnsubscribeMessage):
                return self._validate_unsubscribe(message)
            else:
                return False
        except (ValueError, AttributeError):
            return False

    def _validate_query(self, message: QueryMessage) -> bool:
        """Validate query message.
        
        Args:
            message: Query message
            
        Returns:
            True if valid
        """
        # Validate message ID
        if not self.spec.validate_message_id(message.message_id):
            return False
        
        # Validate query length
        if not self.spec.validate_query_length(message.query):
            return False
        
        # Validate filters
        if message.filters:
            if "limit" in message.filters:
                limit = message.filters["limit"]
                if not isinstance(limit, int) or limit < 0:
                    return False
            if "offset" in message.filters:
                offset = message.filters["offset"]
                if not isinstance(offset, int) or offset < 0:
                    return False
        
        return True

    def _validate_result(self, message: ResultMessage) -> bool:
        """Validate result message.
        
        Args:
            message: Result message
            
        Returns:
            True if valid
        """
        if not self.spec.validate_message_id(message.message_id):
            return False
        
        if not self.spec.validate_message_id(message.query_id):
            return False
        
        if not self.spec.validate_result_count(message.count):
            return False
        
        if len(message.results) != message.count:
            return False
        
        return True

    def _validate_update(self, message: UpdateMessage) -> bool:
        """Validate update message.
        
        Args:
            message: Update message
            
        Returns:
            True if valid
        """
        if not self.spec.validate_message_id(message.message_id):
            return False
        
        if not message.entity_id:
            return False
        
        if not isinstance(message.changes, dict):
            return False
        
        return True

    def _validate_subscribe(self, message: SubscribeMessage) -> bool:
        """Validate subscribe message.
        
        Args:
            message: Subscribe message
            
        Returns:
            True if valid
        """
        if not self.spec.validate_message_id(message.message_id):
            return False
        
        if not message.subscription_id:
            return False
        
        if not message.topic:
            return False
        
        return True

    def _validate_unsubscribe(self, message: UnsubscribeMessage) -> bool:
        """Validate unsubscribe message.
        
        Args:
            message: Unsubscribe message
            
        Returns:
            True if valid
        """
        if not self.spec.validate_message_id(message.message_id):
            return False
        
        if not message.subscription_id:
            return False
        
        return True

    def validate_format(self, data: dict[str, Any]) -> bool:
        """Validate message format.
        
        Args:
            data: Message data dictionary
            
        Returns:
            True if valid format
        """
        required_fields = ["message_id"]
        return all(field in data for field in required_fields)
