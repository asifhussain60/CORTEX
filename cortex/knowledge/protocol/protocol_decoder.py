"""Protocol decoder for deserializing knowledge protocol messages."""

import json
from typing import Any, Union

from cortex.knowledge.protocol.knowledge_protocol_spec import (
    QueryMessage,
    ResultMessage,
    SubscribeMessage,
    UnsubscribeMessage,
    UpdateMessage,
)


class ProtocolDecoder:
    """Decoder for knowledge protocol messages."""

    def __init__(self) -> None:
        """Initialize decoder."""
        self.format = "json"

    def decode(
        self,
        data: str
    ) -> Union[
        QueryMessage,
        ResultMessage,
        UpdateMessage,
        SubscribeMessage,
        UnsubscribeMessage,
    ]:
        """Decode a protocol message.

        Args:
            data: Encoded message string

        Returns:
            Decoded message object
        """
        msg_dict = json.loads(data)
        return self._dict_to_message(msg_dict)

    def _dict_to_message(
        self,
        msg_dict: dict[str, Any]
    ) -> Union[
        QueryMessage,
        ResultMessage,
        UpdateMessage,
        SubscribeMessage,
        UnsubscribeMessage,
    ]:
        """Convert dictionary to message object.

        Args:
            msg_dict: Dictionary representation

        Returns:
            Message object
        """
        msg_type = msg_dict.get("type")

        if msg_type == "query":
            return QueryMessage(
                message_id=msg_dict["message_id"],
                query=msg_dict["query"],
                filters=msg_dict.get("filters", {}),
            )
        elif msg_type == "result":
            return ResultMessage(
                message_id=msg_dict["message_id"],
                query_id=msg_dict["query_id"],
                results=msg_dict.get("results", []),
                count=msg_dict.get("count", 0),
            )
        elif msg_type == "update":
            return UpdateMessage(
                message_id=msg_dict["message_id"],
                entity_id=msg_dict["entity_id"],
                changes=msg_dict.get("changes", {}),
            )
        elif msg_type == "subscribe":
            return SubscribeMessage(
                message_id=msg_dict["message_id"],
                subscription_id=msg_dict["subscription_id"],
                topic=msg_dict["topic"],
            )
        elif msg_type == "unsubscribe":
            return UnsubscribeMessage(
                message_id=msg_dict["message_id"],
                subscription_id=msg_dict["subscription_id"],
            )
        else:
            raise ValueError(f"Unknown message type: {msg_type}")
