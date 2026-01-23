"""Tests for Knowledge Protocol implementation."""

import pytest
from typing import Dict, List, Any
from cortex.knowledge.protocol.knowledge_protocol_spec import (
    KnowledgeProtocolSpec,
    MessageType,
    QueryMessage,
    ResultMessage,
    UpdateMessage,
    SubscribeMessage,
    UnsubscribeMessage,
)
from cortex.knowledge.protocol.protocol_encoder import ProtocolEncoder
from cortex.knowledge.protocol.protocol_decoder import ProtocolDecoder
from cortex.knowledge.protocol.protocol_validator import ProtocolValidator


class TestProtocolSpecification:
    """Tests for protocol specification."""

    def test_spec_initialization(self) -> None:
        """Test protocol specification initialization."""
        spec = KnowledgeProtocolSpec()
        assert spec is not None

    def test_message_types_defined(self) -> None:
        """Test message types are defined."""
        assert MessageType.QUERY is not None
        assert MessageType.RESULT is not None
        assert MessageType.UPDATE is not None
        assert MessageType.SUBSCRIBE is not None
        assert MessageType.UNSUBSCRIBE is not None

    def test_query_message_creation(self) -> None:
        """Test creating a query message."""
        msg = QueryMessage(
            message_id="q1",
            query="find entity type:User",
            filters={"limit": 10}
        )
        assert msg.message_id == "q1"
        assert "User" in msg.query

    def test_result_message_creation(self) -> None:
        """Test creating a result message."""
        msg = ResultMessage(
            message_id="r1",
            query_id="q1",
            results=[{"id": "entity1", "type": "User"}],
            count=1
        )
        assert msg.query_id == "q1"
        assert len(msg.results) == 1

    def test_update_message_creation(self) -> None:
        """Test creating an update message."""
        msg = UpdateMessage(
            message_id="u1",
            entity_id="entity1",
            changes={"status": "active"}
        )
        assert msg.entity_id == "entity1"
        assert msg.changes["status"] == "active"

    def test_subscribe_message_creation(self) -> None:
        """Test creating a subscribe message."""
        msg = SubscribeMessage(
            message_id="s1",
            subscription_id="sub1",
            topic="entity:updated"
        )
        assert msg.subscription_id == "sub1"

    def test_unsubscribe_message_creation(self) -> None:
        """Test creating an unsubscribe message."""
        msg = UnsubscribeMessage(
            message_id="us1",
            subscription_id="sub1"
        )
        assert msg.subscription_id == "sub1"


class TestProtocolEncoder:
    """Tests for protocol encoder."""

    def test_encoder_initialization(self) -> None:
        """Test encoder initialization."""
        encoder = ProtocolEncoder()
        assert encoder is not None

    def test_encode_query_message(self) -> None:
        """Test encoding a query message."""
        encoder = ProtocolEncoder()
        msg = QueryMessage(
            message_id="q1",
            query="find entity",
            filters={}
        )
        encoded = encoder.encode(msg)
        assert encoded is not None
        assert "q1" in str(encoded) or isinstance(encoded, (str, bytes))

    def test_encode_result_message(self) -> None:
        """Test encoding a result message."""
        encoder = ProtocolEncoder()
        msg = ResultMessage(
            message_id="r1",
            query_id="q1",
            results=[],
            count=0
        )
        encoded = encoder.encode(msg)
        assert encoded is not None

    def test_encode_update_message(self) -> None:
        """Test encoding an update message."""
        encoder = ProtocolEncoder()
        msg = UpdateMessage(
            message_id="u1",
            entity_id="e1",
            changes={}
        )
        encoded = encoder.encode(msg)
        assert encoded is not None

    def test_encode_subscribe_message(self) -> None:
        """Test encoding a subscribe message."""
        encoder = ProtocolEncoder()
        msg = SubscribeMessage(
            message_id="s1",
            subscription_id="sub1",
            topic="topic"
        )
        encoded = encoder.encode(msg)
        assert encoded is not None

    def test_encode_unsubscribe_message(self) -> None:
        """Test encoding an unsubscribe message."""
        encoder = ProtocolEncoder()
        msg = UnsubscribeMessage(
            message_id="us1",
            subscription_id="sub1"
        )
        encoded = encoder.encode(msg)
        assert encoded is not None

    def test_encoder_handles_complex_data(self) -> None:
        """Test encoder handles complex data structures."""
        encoder = ProtocolEncoder()
        msg = ResultMessage(
            message_id="r1",
            query_id="q1",
            results=[
                {"id": "e1", "nested": {"key": "value"}},
                {"id": "e2", "list": [1, 2, 3]}
            ],
            count=2
        )
        encoded = encoder.encode(msg)
        assert encoded is not None


class TestProtocolDecoder:
    """Tests for protocol decoder."""

    def test_decoder_initialization(self) -> None:
        """Test decoder initialization."""
        decoder = ProtocolDecoder()
        assert decoder is not None

    def test_decode_query_message(self) -> None:
        """Test decoding a query message."""
        encoder = ProtocolEncoder()
        decoder = ProtocolDecoder()
        
        original = QueryMessage(
            message_id="q1",
            query="test query",
            filters={"limit": 10}
        )
        encoded = encoder.encode(original)
        decoded = decoder.decode(encoded)
        
        assert decoded is not None

    def test_decode_result_message(self) -> None:
        """Test decoding a result message."""
        encoder = ProtocolEncoder()
        decoder = ProtocolDecoder()
        
        original = ResultMessage(
            message_id="r1",
            query_id="q1",
            results=[{"id": "e1"}],
            count=1
        )
        encoded = encoder.encode(original)
        decoded = decoder.decode(encoded)
        
        assert decoded is not None

    def test_decode_preserves_data(self) -> None:
        """Test that decoding preserves message data."""
        encoder = ProtocolEncoder()
        decoder = ProtocolDecoder()
        
        original = QueryMessage(
            message_id="q1",
            query="find entity",
            filters={"type": "User", "limit": 100}
        )
        encoded = encoder.encode(original)
        decoded = decoder.decode(encoded)
        
        assert decoded.message_id == "q1"

    def test_decode_handles_all_message_types(self) -> None:
        """Test decoder handles all message types."""
        encoder = ProtocolEncoder()
        decoder = ProtocolDecoder()
        
        messages = [
            QueryMessage(message_id="q1", query="test", filters={}),
            ResultMessage(message_id="r1", query_id="q1", results=[], count=0),
            UpdateMessage(message_id="u1", entity_id="e1", changes={}),
            SubscribeMessage(message_id="s1", subscription_id="sub1", topic="t1"),
            UnsubscribeMessage(message_id="us1", subscription_id="sub1"),
        ]
        
        for msg in messages:
            encoded = encoder.encode(msg)
            decoded = decoder.decode(encoded)
            assert decoded is not None


class TestProtocolValidator:
    """Tests for protocol validator."""

    def test_validator_initialization(self) -> None:
        """Test validator initialization."""
        validator = ProtocolValidator()
        assert validator is not None

    def test_validate_query_message(self) -> None:
        """Test validating a query message."""
        validator = ProtocolValidator()
        msg = QueryMessage(
            message_id="q1",
            query="valid query",
            filters={}
        )
        result = validator.validate(msg)
        assert result is True

    def test_validate_invalid_message_id(self) -> None:
        """Test validation fails for empty message ID."""
        validator = ProtocolValidator()
        try:
            msg = QueryMessage(
                message_id="",
                query="query",
                filters={}
            )
            result = validator.validate(msg)
            assert result is False
        except ValueError:
            # Expected: __post_init__ raises ValueError
            assert True

    def test_validate_empty_query(self) -> None:
        """Test validation fails for empty query."""
        validator = ProtocolValidator()
        try:
            msg = QueryMessage(
                message_id="q1",
                query="",
                filters={}
            )
            result = validator.validate(msg)
            assert result is False
        except ValueError:
            # Expected: __post_init__ raises ValueError
            assert True

    def test_validate_result_message(self) -> None:
        """Test validating a result message."""
        validator = ProtocolValidator()
        msg = ResultMessage(
            message_id="r1",
            query_id="q1",
            results=[],
            count=0
        )
        result = validator.validate(msg)
        assert result is True

    def test_validate_update_message(self) -> None:
        """Test validating an update message."""
        validator = ProtocolValidator()
        msg = UpdateMessage(
            message_id="u1",
            entity_id="e1",
            changes={"field": "value"}
        )
        result = validator.validate(msg)
        assert result is True

    def test_validate_semantic_constraints(self) -> None:
        """Test validation of semantic constraints."""
        validator = ProtocolValidator()
        
        # Valid semantic structure
        msg = QueryMessage(
            message_id="q1",
            query="find entity type:Document",
            filters={"limit": 100, "offset": 0}
        )
        assert validator.validate(msg) is True
        
        # Invalid: negative limit
        msg2 = QueryMessage(
            message_id="q2",
            query="find entity",
            filters={"limit": -1}
        )
        assert validator.validate(msg2) is False


class TestProtocolIntegration:
    """Integration tests for protocol components."""

    def test_encode_decode_roundtrip(self) -> None:
        """Test encode-decode roundtrip maintains data integrity."""
        encoder = ProtocolEncoder()
        decoder = ProtocolDecoder()
        
        original = QueryMessage(
            message_id="q1",
            query="find entity type:User age>30",
            filters={"limit": 50, "offset": 0}
        )
        
        encoded = encoder.encode(original)
        decoded = decoder.decode(encoded)
        
        assert isinstance(decoded, QueryMessage)
        assert decoded.message_id == original.message_id
        assert decoded.query == original.query

    def test_full_protocol_workflow(self) -> None:
        """Test full protocol workflow: query -> result."""
        encoder = ProtocolEncoder()
        decoder = ProtocolDecoder()
        validator = ProtocolValidator()
        
        # 1. Client sends query
        query = QueryMessage(
            message_id="q1",
            query="find entity",
            filters={"limit": 10}
        )
        assert validator.validate(query) is True
        
        # 2. Encode for transmission
        encoded_query = encoder.encode(query)
        
        # 3. Decode on server
        decoded_query = decoder.decode(encoded_query)
        assert decoded_query is not None
        assert isinstance(decoded_query, QueryMessage)
        
        # 4. Server sends result
        result = ResultMessage(
            message_id="r1",
            query_id=decoded_query.message_id,
            results=[{"id": "e1", "type": "Entity"}],
            count=1
        )
        assert validator.validate(result) is True
        
        # 5. Encode result for transmission
        encoded_result = encoder.encode(result)
        
        # 6. Client receives and decodes result
        decoded_result = decoder.decode(encoded_result)
        assert decoded_result is not None
        assert isinstance(decoded_result, ResultMessage)
        assert len(decoded_result.results) == 1

    def test_protocol_with_knowledge_operations(self) -> None:
        """Test protocol integration with knowledge operations."""
        encoder = ProtocolEncoder()
        decoder = ProtocolDecoder()
        validator = ProtocolValidator()
        
        # Subscribe to updates
        sub = SubscribeMessage(
            message_id="s1",
            subscription_id="sub:user:updates",
            topic="entity:User:updated"
        )
        assert validator.validate(sub) is True
        
        # Receive update notification
        update = UpdateMessage(
            message_id="u1",
            entity_id="user:123",
            changes={"last_seen": "2026-01-23T14:00:00Z"}
        )
        assert validator.validate(update) is True
        
        # Unsubscribe
        unsub = UnsubscribeMessage(
            message_id="us1",
            subscription_id="sub:user:updates"
        )
        assert validator.validate(unsub) is True

    def test_protocol_handles_large_result_sets(self) -> None:
        """Test protocol handles large result sets."""
        encoder = ProtocolEncoder()
        decoder = ProtocolDecoder()
        validator = ProtocolValidator()
        
        # Create large result set
        large_results = [
            {"id": f"entity_{i}", "type": "Item", "index": i}
            for i in range(1000)
        ]
        
        msg = ResultMessage(
            message_id="r1",
            query_id="q1",
            results=large_results,
            count=1000
        )
        assert validator.validate(msg) is True
        
        encoded = encoder.encode(msg)
        decoded = decoder.decode(encoded)
        
        assert decoded is not None
        assert isinstance(decoded, ResultMessage)
        assert len(decoded.results) == 1000
        assert decoded.count == 1000
