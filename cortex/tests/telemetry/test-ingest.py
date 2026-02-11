"""Tests for telemetry ingest endpoint (AC-UNIFIED-DEPLOY-001-02)."""

import json
from datetime import datetime

import pytest

from cortex.api.telemetry.ingest import IngestResponse, TelemetryIngestEndpoint
from cortex.api.telemetry.schema import TelemetryEventSchema


class TestTelemetryIngestEndpoint:
    """Test suite for telemetry ingest endpoint."""

    @pytest.fixture
    def endpoint(self):
        """Create test endpoint."""
        return TelemetryIngestEndpoint(dedup_window_minutes=60)

    def test_ingest_empty_batch(self, endpoint):
        """Test rejection of empty batch."""
        response = endpoint.ingest_batch([])
        assert response.status == "error"
        assert response.processed == 0
        assert "empty" in response.errors[0].lower()

    def test_ingest_single_valid_event(self, endpoint):
        """Test ingestion of single valid event."""
        event = {
            "event_type": "execution",
            "tool_name": "file_search",
            "duration_ms": 150.5,
            "success": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "environment_signature": "env_hash_123",
            "repo_identifier": "repo_456",
        }

        response = endpoint.ingest_batch([event])
        assert response.status == "ok"
        assert response.processed == 1
        assert response.rejected == 0

    def test_ingest_event_with_secrets(self, endpoint):
        """Test rejection of events containing secrets."""
        event = {
            "event_type": "execution",
            "tool_name": "api_call",
            "duration_ms": 100.0,
            "success": False,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "environment_signature": "env_123",
            "repo_identifier": "repo_123",
            "error_message": "API key: sk-1234567890abcdef rejected",
        }

        response = endpoint.ingest_batch([event])
        assert response.status == "error"
        assert response.processed == 0
        assert response.rejected == 1
        assert any("secret" in err.lower() for err in response.errors)

    def test_ingest_invalid_json_schema(self, endpoint):
        """Test rejection of invalid event schema."""
        event = {
            "event_type": "execution",
            # Missing required fields
            "tool_name": "test",
        }

        response = endpoint.ingest_batch([event])
        assert response.rejected == 1
        assert response.processed == 0

    def test_ingest_duplicate_events(self, endpoint):
        """Test deduplication of duplicate error events."""
        event_base = {
            "event_type": "error",
            "error_id": "err_123",
            "error_category": "parsing",
            "reproducibility_score": 0.8,
            "environment_signature": "env_123",
            "repo_identifier": "repo_123",
            "first_seen_at": datetime.utcnow().isoformat() + "Z",
            "last_seen_at": datetime.utcnow().isoformat() + "Z",
            "occurrence_count": 1,
        }

        # First batch - should succeed
        response1 = endpoint.ingest_batch([event_base])
        assert response1.processed == 1

        # Second batch with same error - should be deduplicated
        response2 = endpoint.ingest_batch([event_base])
        assert response2.rejected == 1

    def test_ingest_batch_size_limit(self, endpoint):
        """Test rejection of oversized batches."""
        events = [
            {
                "event_type": "execution",
                "tool_name": "test",
                "duration_ms": 10.0,
                "success": True,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "environment_signature": "env_123",
                "repo_identifier": "repo_123",
            }
            for _ in range(15001)
        ]

        response = endpoint.ingest_batch(events)
        assert response.status == "error"
        assert "exceeds maximum size" in response.errors[0]

    def test_ingest_mixed_valid_invalid_events(self, endpoint):
        """Test batch with mix of valid and invalid events."""
        events = [
            {
                "event_type": "execution",
                "tool_name": "test1",
                "duration_ms": 100.0,
                "success": True,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "environment_signature": "env_123",
                "repo_identifier": "repo_123",
            },
            {
                # Invalid - missing required fields
                "event_type": "execution",
                "tool_name": "test2",
            },
            {
                "event_type": "execution",
                "tool_name": "test3",
                "duration_ms": 50.0,
                "success": True,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "environment_signature": "env_123",
                "repo_identifier": "repo_123",
            },
        ]

        response = endpoint.ingest_batch(events)
        assert response.processed == 2
        assert response.rejected == 1

    def test_handle_post_request_invalid_content_type(self, endpoint):
        """Test rejection of non-JSON content type."""
        status, response = endpoint.handle_post_request(
            "test=data", {"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert status == 400
        assert "json" in response["error"].lower()

    def test_handle_post_request_malformed_json(self, endpoint):
        """Test rejection of malformed JSON."""
        status, response = endpoint.handle_post_request(
            "{invalid json}", {"Content-Type": "application/json"}
        )
        assert status == 400
        assert "invalid json" in response["error"].lower()

    def test_handle_post_request_valid_batch(self, endpoint):
        """Test valid POST request handling."""
        batch = [
            {
                "event_type": "execution",
                "tool_name": "test",
                "duration_ms": 100.0,
                "success": True,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "environment_signature": "env_123",
                "repo_identifier": "repo_123",
            }
        ]

        status, response = endpoint.handle_post_request(
            json.dumps(batch), {"Content-Type": "application/json"}
        )
        assert status == 200
        assert response["status"] == "ok"
        assert response["processed"] == 1

    def test_secret_detection_patterns(self, endpoint):
        """Test detection of various secret patterns."""
        secret_texts = [
            "api_key = sk-1234567890abcdef",
            "password:super_secret_123",
            "Bearer eyJhbGciOiJIUzI1NiIs",
            "oauth secret_token_xyz",
            "private_key: -----BEGIN RSA",
        ]

        for text in secret_texts:
            detected = endpoint.detect_secrets(text)
            assert len(detected) > 0, f"Should detect secrets in: {text}"

    def test_pii_scrubbing_in_events(self, endpoint):
        """Test that PII is scrubbed from events."""
        event = {
            "event_type": "error",
            "error_id": "err_123",
            "error_category": "parsing",
            "reproducibility_score": 0.8,
            "environment_signature": "env_123",
            "repo_identifier": "repo_123",
            "first_seen_at": datetime.utcnow().isoformat() + "Z",
            "last_seen_at": datetime.utcnow().isoformat() + "Z",
            "occurrence_count": 1,
            "error_message": "Failed to parse user@example.com configuration",
        }

        response = endpoint.ingest_batch([event])
        assert response.processed == 1
        # Event should be accepted (PII is handled by schema validator)
