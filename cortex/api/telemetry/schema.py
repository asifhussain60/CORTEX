"""Telemetry event schema definitions for CORTEX unified deployment."""

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionEvent:
    """Execution event telemetry data."""

    event_type: str  # e.g., "orchestrator_invocation", "mcp_tool_call"
    tool_name: str
    duration_ms: float
    success: bool
    timestamp: str
    environment_signature: str  # Hash of environment (OS, Python version, etc.)
    repo_identifier: str  # Hash of repo path or name
    stage: Optional[str] = None  # LENS stage, if applicable
    output_size_bytes: Optional[int] = None


@dataclass
class ErrorEvent:
    """Error event telemetry data."""

    error_id: str  # Hash of error message for deduplication
    error_category: str  # e.g., "parsing", "api_timeout", "memory_exceeded"
    reproducibility_score: float  # 0.0-1.0: how consistently it reproduces
    environment_signature: str
    repo_identifier: str
    first_seen_at: str
    last_seen_at: str
    occurrence_count: int
    error_message_hash: str  # SHA256 of sanitized error message


@dataclass
class PerformanceEvent:
    """Performance aggregate metric event."""

    metric_name: str  # e.g., "mcp_tool_latency", "cache_hit_ratio"
    value: float
    unit: str  # e.g., "ms", "percent", "bytes"
    environment_signature: str
    repo_identifier: str
    timestamp: str
    context: Optional[Dict[str, Any]] = None


@dataclass
class FeedbackEvent:
    """User feedback event (consent-gated)."""

    feedback_type: str  # e.g., "feature_request", "bug_report", "usability"
    feedback_text: str  # User's message (user code stripped)
    user_consent_verified: bool
    timestamp: str
    environment_signature: str
    repo_identifier: str


class TelemetryEventSchema:
    """Schema validator and converter for telemetry events."""

    # PII patterns to scrub
    PII_PATTERNS = [
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        r"\b(?:\d{1,5}[.-]?)?\d{1,5}[.-]?\d{1,5}[.-]?\d{1,5}\b",  # IP-like
        r"/home/[\w/\-._]+",  # Unix home paths
        r"C:\\Users\\[\w\\]+",  # Windows paths
        r"(password|secret|token|api[_-]?key)\s*[:=]\s*[^\s]+",  # Secrets
    ]

    @classmethod
    def scrub_pii(cls, text: str) -> str:
        """
        Scrub personally identifiable information from text.

        Args:
            text: Input text potentially containing PII.

        Returns:
            Scrubbed text with PII replaced by [REDACTED].
        """
        scrubbed = text
        for pattern in cls.PII_PATTERNS:
            scrubbed = re.sub(pattern, "[REDACTED]", scrubbed, flags=re.IGNORECASE)
        return scrubbed

    @classmethod
    def compute_error_id(cls, error_message: str, environment_sig: str) -> str:
        """
        Compute deterministic error ID for deduplication.

        Args:
            error_message: Sanitized error message.
            environment_sig: Environment signature.

        Returns:
            SHA256 hash of combined message and environment.
        """
        combined = f"{cls.scrub_pii(error_message)}:{environment_sig}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    @classmethod
    def validate_execution_event(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize execution event.

        Args:
            data: Raw event data.

        Returns:
            Validated event dict.

        Raises:
            ValueError: If validation fails.
        """
        required_fields = [
            "event_type",
            "tool_name",
            "duration_ms",
            "success",
            "timestamp",
            "environment_signature",
            "repo_identifier",
        ]
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        # Validate types
        if not isinstance(data["duration_ms"], (int, float)) or data["duration_ms"] < 0:
            raise ValueError("duration_ms must be non-negative number")
        if not isinstance(data["success"], bool):
            raise ValueError("success must be boolean")

        return data

    @classmethod
    def validate_error_event(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize error event.

        Args:
            data: Raw event data.

        Returns:
            Validated event dict.

        Raises:
            ValueError: If validation fails.
        """
        required_fields = [
            "error_id",
            "error_category",
            "reproducibility_score",
            "environment_signature",
            "repo_identifier",
            "first_seen_at",
            "last_seen_at",
            "occurrence_count",
        ]
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        # Validate reproducibility_score range
        score = data["reproducibility_score"]
        if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
            raise ValueError("reproducibility_score must be between 0.0 and 1.0")

        # Validate occurrence_count is positive
        if not isinstance(data["occurrence_count"], int) or data["occurrence_count"] <= 0:
            raise ValueError("occurrence_count must be positive integer")

        return data

    @classmethod
    def validate_performance_event(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize performance event.

        Args:
            data: Raw event data.

        Returns:
            Validated event dict.

        Raises:
            ValueError: If validation fails.
        """
        required_fields = [
            "metric_name",
            "value",
            "unit",
            "environment_signature",
            "repo_identifier",
            "timestamp",
        ]
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        if not isinstance(data["value"], (int, float)):
            raise ValueError("value must be numeric")

        return data

    @classmethod
    def validate_feedback_event(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize feedback event.

        Args:
            data: Raw event data.

        Returns:
            Validated event dict.

        Raises:
            ValueError: If validation fails.
        """
        required_fields = [
            "feedback_type",
            "feedback_text",
            "user_consent_verified",
            "timestamp",
            "environment_signature",
            "repo_identifier",
        ]
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        if not isinstance(data["user_consent_verified"], bool):
            raise ValueError("user_consent_verified must be boolean")

        # Scrub user feedback
        data["feedback_text"] = cls.scrub_pii(data["feedback_text"])

        return data

    @classmethod
    def validate_batch(cls, events: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[str]]:
        """
        Validate a batch of mixed events.

        Args:
            events: List of raw event dicts.

        Returns:
            Tuple of (valid_events, error_messages).
        """
        valid_events = []
        errors = []

        for idx, event in enumerate(events):
            try:
                event_type = event.get("event_type")

                if event_type == "execution":
                    validated = cls.validate_execution_event(event)
                    valid_events.append(validated)
                elif event_type == "error":
                    validated = cls.validate_error_event(event)
                    valid_events.append(validated)
                elif event_type == "performance":
                    validated = cls.validate_performance_event(event)
                    valid_events.append(validated)
                elif event_type == "feedback":
                    validated = cls.validate_feedback_event(event)
                    valid_events.append(validated)
                else:
                    errors.append(f"Event {idx}: unknown event_type '{event_type}'")
            except ValueError as e:
                errors.append(f"Event {idx}: {str(e)}")
            except Exception as e:
                errors.append(f"Event {idx}: unexpected error: {str(e)}")

        return valid_events, errors

    @classmethod
    def to_dict(cls, event: object) -> Dict[str, Any]:
        """Convert dataclass event to dict."""
        if isinstance(event, (ExecutionEvent, ErrorEvent, PerformanceEvent, FeedbackEvent)):
            return asdict(event)
        raise ValueError(f"Unknown event type: {type(event)}")
