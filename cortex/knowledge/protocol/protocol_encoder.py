"""Protocol encoder for serializing knowledge protocol messages."""

import json
from typing import Any, Union

from cortex.knowledge.protocol.knowledge_protocol_spec import (
    QueryMessage,
    ResultMessage,
    SubscribeMessage,
    UnsubscribeMessage,
    UpdateMessage,
)


class ProtocolEncoder:
    """Encoder for knowledge protocol messages."""

    def __init__(self) -> None:
        """Initialize encoder."""
        self.format = "json"

    def encode(
        self,
        message: Union[
            QueryMessage,
            ResultMessage,
            UpdateMessage,
            SubscribeMessage,
            UnsubscribeMessage,
        ]
    ) -> str:
        """Encode a protocol message.

        Args:
            message: Message to encode

        Returns:
            Encoded message string
        """
        message_dict = self._message_to_dict(message)
        return json.dumps(message_dict)

    def _message_to_dict(self, message: Any) -> dict[str, Any]:
        """Convert message to dictionary.

        Args:
            message: Message to convert

        Returns:
            Dictionary representation
        """
        msg_dict: dict[str, Any] = {}

        if isinstance(message, QueryMessage):
            msg_dict = {
                "type": "query",
                "message_id": message.message_id,
                "query": message.query,
                "filters": message.filters,
            }
        elif isinstance(message, ResultMessage):
            msg_dict = {
                "type": "result",
                "message_id": message.message_id,
                "query_id": message.query_id,
                "results": message.results,
                "count": message.count,
            }
        elif isinstance(message, UpdateMessage):
            msg_dict = {
                "type": "update",
                "message_id": message.message_id,
                "entity_id": message.entity_id,
                "changes": message.changes,
            }
        elif isinstance(message, SubscribeMessage):
            msg_dict = {
                "type": "subscribe",
                "message_id": message.message_id,
                "subscription_id": message.subscription_id,
                "topic": message.topic,
            }
        elif isinstance(message, UnsubscribeMessage):
            msg_dict = {
                "type": "unsubscribe",
                "message_id": message.message_id,
                "subscription_id": message.subscription_id,
            }

        return msg_dict
