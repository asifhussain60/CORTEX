"""Response Header Injector - Injects contextual headers into responses.

Adds metadata headers to responses for tracking, auditing, and control flow.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class ResponseHeader:
    """Response header with metadata.

    Attributes:
        request_id: Trace request ID.
        timestamp: When response was generated.
        version: API version.
        domain: Domain that processed the request.
        execution_time_ms: Execution time in milliseconds.
        custom_headers: Custom header values.
    """

    request_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    domain: str = "cortex"
    execution_time_ms: int = 0
    custom_headers: Dict[str, str] = field(default_factory=dict)


class ResponseHeaderInjector:
    """Injects headers into responses."""

    def __init__(self, default_version: str = "1.0.0") -> None:
        """Initialize header injector.

        Args:
            default_version: Default API version.
        """
        self.default_version = default_version
        self.request_counter = 0

    def generate_header(
        self,
        request_id: Optional[str] = None,
        domain: str = "cortex",
        execution_time_ms: int = 0,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> ResponseHeader:
        """Generate a response header.

        Args:
            request_id: Optional trace request ID.
            domain: Domain name.
            execution_time_ms: Execution time.
            custom_headers: Custom headers to include.

        Returns:
            ResponseHeader with all metadata.
        """
        if not request_id:
            self.request_counter += 1
            request_id = f"req-{self.request_counter:06d}"

        return ResponseHeader(
            request_id=request_id,
            version=self.default_version,
            domain=domain,
            execution_time_ms=execution_time_ms,
            custom_headers=custom_headers or {},
        )

    def inject(
        self,
        response: Dict[str, Any],
        request_id: Optional[str] = None,
        domain: str = "cortex",
        execution_time_ms: int = 0,
    ) -> Dict[str, Any]:
        """Inject headers into a response dictionary.

        Args:
            response: Response dictionary.
            request_id: Optional trace request ID.
            domain: Domain name.
            execution_time_ms: Execution time.

        Returns:
            Response with headers injected.
        """
        header = self.generate_header(
            request_id=request_id,
            domain=domain,
            execution_time_ms=execution_time_ms,
        )

        # Add headers to response
        response["__headers__"] = {
            "request_id": header.request_id,
            "timestamp": header.timestamp.isoformat(),
            "version": header.version,
            "domain": header.domain,
            "execution_time_ms": header.execution_time_ms,
        }

        # Add custom headers
        if header.custom_headers:
            response["__headers__"].update(header.custom_headers)

        return response

    def extract_header(self, response: Dict[str, Any]) -> Optional[ResponseHeader]:
        """Extract header from response.

        Args:
            response: Response dictionary.

        Returns:
            ResponseHeader or None if not found.
        """
        headers = response.get("__headers__")
        if not headers:
            return None

        return ResponseHeader(
            request_id=headers.get("request_id", "unknown"),
            version=headers.get("version", "1.0.0"),
            domain=headers.get("domain", "cortex"),
            execution_time_ms=headers.get("execution_time_ms", 0),
        )


__all__ = [
    "ResponseHeaderInjector",
    "ResponseHeader",
]
