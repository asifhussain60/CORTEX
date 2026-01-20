"""REST endpoint for batch telemetry ingestion (AC-UNIFIED-DEPLOY-001-02)."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging

from .schema import TelemetryEventSchema


logger = logging.getLogger(__name__)


@dataclass
class IngestResponse:
    """Response from telemetry ingest endpoint."""

    status: str  # "ok" or "error"
    processed: int
    rejected: int
    errors: List[str]
    warnings: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "status": self.status,
            "processed": self.processed,
            "rejected": self.rejected,
            "errors": self.errors,
            "warnings": self.warnings or [],
        }


class TelemetryIngestEndpoint:
    """
    Server-side REST endpoint for batch telemetry ingestion.

    Endpoint: POST api.cortex-ai.io/v1/telemetry/ingest

    Handles:
    • Schema validation
    • PII scrubbing
    • Secret detection
    • Event deduplication
    """

    SECRET_PATTERNS = [
        r"(api[_-]?key|apikey)\s*[:=]\s*['\"]?[\w\-\.]+['\"]?",
        r"(password|passwd|pwd)\s*[:=]\s*['\"]?[^\s'\"]+['\"]?",
        r"(token|bearer)\s+[a-zA-Z0-9\._\-]+",
        r"(secret|oauth)\s*[:=]\s*['\"]?[^\s'\"]+['\"]?",
        r"(private[_-]?key|rsa[_-]?key)\s*[:=]",
    ]

    def __init__(self, dedup_window_minutes: int = 60):
        """
        Initialize telemetry ingest endpoint.

        Args:
            dedup_window_minutes: Deduplication window in minutes.
        """
        self.dedup_window = timedelta(minutes=dedup_window_minutes)
        self.recent_events: List[Dict[str, Any]] = []

    def detect_secrets(self, text: str) -> List[str]:
        """
        Detect potential secrets in text.

        Args:
            text: Text to scan for secrets.

        Returns:
            List of detected secret patterns (for rejection).
        """
        import re

        detected = []
        for pattern in self.SECRET_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(pattern)
        return detected

    def check_for_secrets_in_event(self, event: Dict[str, Any]) -> List[str]:
        """
        Check if event contains secrets.

        Args:
            event: Event dict.

        Returns:
            List of secret patterns found (empty if none).
        """
        secrets = []
        # Check event_type and any string fields
        for key, value in event.items():
            if isinstance(value, str):
                detected = self.detect_secrets(value)
                if detected:
                    secrets.extend(detected)
        return secrets

    def deduplicate_event(self, event: Dict[str, Any]) -> bool:
        """
        Check if event is a duplicate of a recent event.

        Uses error_id + environment_signature + timestamp (within window) for deduplication.

        Args:
            event: Event to check.

        Returns:
            True if event is considered duplicate, False otherwise.
        """
        if event.get("event_type") != "error":
            return False  # Only deduplicate error events

        event_id = event.get("error_id")
        env_sig = event.get("environment_signature")
        timestamp = event.get("first_seen_at")

        if not (event_id and env_sig and timestamp):
            return False

        # Parse timestamp
        try:
            event_time = datetime.fromisoformat(timestamp)
        except (ValueError, TypeError):
            return False

        # Check against recent events
        cutoff = datetime.now(event_time.tzinfo) - self.dedup_window
        for recent in self.recent_events:
            if (
                recent.get("error_id") == event_id
                and recent.get("environment_signature") == env_sig
            ):
                recent_time = datetime.fromisoformat(
                    recent.get("first_seen_at", "")
                )
                if recent_time >= cutoff:
                    return True

        return False

    def ingest_batch(
        self, batch: List[Dict[str, Any]]
    ) -> IngestResponse:
        """
        Ingest a batch of telemetry events.

        Args:
            batch: List of event dicts.

        Returns:
            IngestResponse with status and counts.
        """
        processed = 0
        rejected = 0
        errors = []
        warnings = []

        # Validate batch structure
        if not isinstance(batch, list):
            return IngestResponse(
                status="error",
                processed=0,
                rejected=0,
                errors=["Batch must be a list of events"],
            )

        if len(batch) == 0:
            return IngestResponse(
                status="error",
                processed=0,
                rejected=0,
                errors=["Batch is empty"],
            )

        if len(batch) > 10000:
            return IngestResponse(
                status="error",
                processed=0,
                rejected=0,
                errors=["Batch exceeds maximum size (10000 events)"],
            )

        # Process each event
        for idx, event in enumerate(batch):
            # Check for secrets (reject if found)
            secrets = self.check_for_secrets_in_event(event)
            if secrets:
                rejected += 1
                errors.append(
                    f"Event {idx}: Secret patterns detected (rejected for safety)"
                )
                logger.warning(f"Secret patterns detected in event {idx}, rejecting")
                continue

            # Validate event schema
            try:
                valid_events, validation_errors = TelemetryEventSchema.validate_batch(
                    [event]
                )
                if validation_errors:
                    rejected += 1
                    errors.extend(validation_errors)
                    continue

                # Check for duplication
                if self.deduplicate_event(event):
                    warnings.append(f"Event {idx}: Duplicate detected (same error_id within window)")
                    rejected += 1
                    continue

                # Event is valid
                processed += 1
                self.recent_events.append(event)

                # Clean up old events (outside dedup window)
                cutoff = datetime.now() - self.dedup_window
                self.recent_events = [
                    e
                    for e in self.recent_events
                    if (
                        datetime.fromisoformat(
                            e.get("first_seen_at", datetime.now().isoformat())
                        )
                        >= cutoff
                    )
                ]

            except Exception as e:
                rejected += 1
                errors.append(f"Event {idx}: Unexpected error: {str(e)}")
                logger.error(f"Error processing event {idx}: {str(e)}")

        status = "ok" if processed > 0 else "error"
        return IngestResponse(
            status=status,
            processed=processed,
            rejected=rejected,
            errors=errors,
            warnings=warnings,
        )

    def handle_post_request(
        self, body: str, headers: Dict[str, str]
    ) -> tuple[int, Dict[str, Any]]:
        """
        Handle POST request to telemetry endpoint.

        Args:
            body: JSON request body.
            headers: HTTP headers.

        Returns:
            Tuple of (status_code, response_dict).
        """
        # Check content type
        content_type = headers.get("Content-Type", "")
        if "application/json" not in content_type:
            return 400, {"error": "Content-Type must be application/json"}

        # Parse JSON
        try:
            batch = json.loads(body)
        except json.JSONDecodeError as e:
            return 400, {"error": f"Invalid JSON: {str(e)}"}

        # Process batch
        response = self.ingest_batch(batch)

        # Return response
        status_code = 200 if response.status == "ok" else 400
        return status_code, response.to_dict()
