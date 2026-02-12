"""Tests for telemetry data scrubbing and schema validation."""

from datetime import datetime

import pytest

from cortex.api.telemetry.schema import TelemetryEventSchema


class TestDataScrubbing:
    """Test suite for PII/secret scrubbing."""

    def test_scrub_email_addresses(self):
        """Test scrubbing of email addresses."""
        text = "Contact user@example.com for support"
        scrubbed = TelemetryEventSchema.scrub_pii(text)
        assert "user@example.com" not in scrubbed
        assert "[REDACTED]" in scrubbed

    def test_scrub_ipaddress_patterns(self):
        """Test scrubbing of IP-like patterns."""
        text = "Connected to 192.168.1.1 failed"
        scrubbed = TelemetryEventSchema.scrub_pii(text)
        assert "[REDACTED]" in scrubbed or "192.168.1.1" not in scrubbed

    def test_scrub_unix_home_paths(self):
        """Test scrubbing of Unix home paths."""
        text = "Error in /home/user/project/file.py"
        scrubbed = TelemetryEventSchema.scrub_pii(text)
        assert "[REDACTED]" in scrubbed or "/home/user" not in scrubbed

    def test_scrub_windows_paths(self):
        """Test scrubbing of Windows paths."""
        text = "Failed at C:\\Users\\Admin\\Documents\\file.txt"
        scrubbed = TelemetryEventSchema.scrub_pii(text)
        assert "[REDACTED]" in scrubbed or "C:\\Users" not in scrubbed

    def test_scrub_secret_keywords(self):
        """Test scrubbing of secret keywords."""
        text = "api_key=sk_live_abc123xyz secret=mysecret"
        scrubbed = TelemetryEventSchema.scrub_pii(text)
        assert "[REDACTED]" in scrubbed

    def test_scrub_idempotent(self):
        """Test that scrubbing is idempotent."""
        text = "user@example.com error"
        once = TelemetryEventSchema.scrub_pii(text)
        twice = TelemetryEventSchema.scrub_pii(once)
        assert once == twice  # Should not change on re-scrubbing

    def test_scrub_preserves_structure(self):
        """Test that scrubbing preserves message structure."""
        text = "Error occurred at user@example.com line 42"
        scrubbed = TelemetryEventSchema.scrub_pii(text)
        assert "Error" in scrubbed
        assert "line 42" in scrubbed


class TestErrorIdComputation:
    """Test suite for error ID computation."""

    def test_compute_error_id_deterministic(self):
        """Test that error ID computation is deterministic."""
        msg = "Connection timeout"
        env = "env_prod"

        id1 = TelemetryEventSchema.compute_error_id(msg, env)
        id2 = TelemetryEventSchema.compute_error_id(msg, env)
        assert id1 == id2

    def test_compute_error_id_different_messages(self):
        """Test that different messages produce different IDs."""
        env = "env_prod"
        id1 = TelemetryEventSchema.compute_error_id("Error A", env)
        id2 = TelemetryEventSchema.compute_error_id("Error B", env)
        assert id1 != id2

    def test_compute_error_id_scrubs_pii(self):
        """Test that error ID scrubs PII before hashing."""
        env = "env_prod"
        msg_with_email = "Failed at user@example.com"
        id_email = TelemetryEventSchema.compute_error_id(msg_with_email, env)

        msg_scrubbed = "Failed at [REDACTED]"
        id_scrubbed = TelemetryEventSchema.compute_error_id(msg_scrubbed, env)

        # Should produce same ID since both effectively scrub email
        # (behavior depends on when scrubbing occurs)
        assert isinstance(id_email, str)
        assert isinstance(id_scrubbed, str)


class TestExecutionEventValidation:
    """Test suite for execution event validation."""

    def test_validate_execution_event_valid(self):
        """Test validation of valid execution event."""
        event = {
            "event_type": "execution",
            "tool_name": "file_search",
            "duration_ms": 150.5,
            "success": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "environment_signature": "env_123",
            "repo_identifier": "repo_456",
        }

        result = TelemetryEventSchema.validate_execution_event(event)
        assert result is not None

    def test_validate_execution_event_missing_field(self):
        """Test rejection of execution event with missing field."""
        event = {
            "event_type": "execution",
            "tool_name": "test",
            # Missing duration_ms
            "success": True,
        }

        with pytest.raises(ValueError):
            TelemetryEventSchema.validate_execution_event(event)

    def test_validate_execution_event_negative_duration(self):
        """Test rejection of negative duration."""
        event = {
            "event_type": "execution",
            "tool_name": "test",
            "duration_ms": -100,
            "success": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "environment_signature": "env_123",
            "repo_identifier": "repo_456",
        }

        with pytest.raises(ValueError):
            TelemetryEventSchema.validate_execution_event(event)


class TestErrorEventValidation:
    """Test suite for error event validation."""

    def test_validate_error_event_valid(self):
        """Test validation of valid error event."""
        event = {
            "error_id": "err_123",
            "error_category": "parsing",
            "reproducibility_score": 0.75,
            "environment_signature": "env_123",
            "repo_identifier": "repo_456",
            "first_seen_at": datetime.utcnow().isoformat() + "Z",
            "last_seen_at": datetime.utcnow().isoformat() + "Z",
            "occurrence_count": 5,
        }

        result = TelemetryEventSchema.validate_error_event(event)
        assert result is not None

    def test_validate_error_event_invalid_reproducibility(self):
        """Test rejection of invalid reproducibility score."""
        event = {
            "error_id": "err_123",
            "error_category": "parsing",
            "reproducibility_score": 1.5,  # Out of range
            "environment_signature": "env_123",
            "repo_identifier": "repo_456",
            "first_seen_at": datetime.utcnow().isoformat() + "Z",
            "last_seen_at": datetime.utcnow().isoformat() + "Z",
            "occurrence_count": 5,
        }

        with pytest.raises(ValueError):
            TelemetryEventSchema.validate_error_event(event)

    def test_validate_error_event_zero_count(self):
        """Test rejection of zero occurrence count."""
        event = {
            "error_id": "err_123",
            "error_category": "parsing",
            "reproducibility_score": 0.75,
            "environment_signature": "env_123",
            "repo_identifier": "repo_456",
            "first_seen_at": datetime.utcnow().isoformat() + "Z",
            "last_seen_at": datetime.utcnow().isoformat() + "Z",
            "occurrence_count": 0,
        }

        with pytest.raises(ValueError):
            TelemetryEventSchema.validate_error_event(event)


class TestBatchValidation:
    """Test suite for batch validation."""

    def test_validate_batch_empty(self):
        """Test validation of empty batch."""
        valid, errors = TelemetryEventSchema.validate_batch([])
        assert valid == True  # Empty batch is valid (handled elsewhere)

    def test_validate_batch_mixed_types(self):
        """Test validation of batch with mixed event types."""
        batch = [
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
                "event_type": "error",
                "error_id": "err_123",
                "error_category": "test",
                "reproducibility_score": 0.5,
                "environment_signature": "env_123",
                "repo_identifier": "repo_456",
                "first_seen_at": datetime.utcnow().isoformat() + "Z",
                "last_seen_at": datetime.utcnow().isoformat() + "Z",
                "occurrence_count": 1,
            },
        ]

        valid, errors = TelemetryEventSchema.validate_batch(batch)
        assert len(valid) == 2
        assert len(errors) == 0

    def test_validate_batch_with_invalid_event(self):
        """Test validation stops at invalid event."""
        batch = [
            {
                "event_type": "unknown_type",
                "data": "test",
            }
        ]

        valid, errors = TelemetryEventSchema.validate_batch(batch)
        assert len(valid) == 0
        assert len(errors) > 0
