"""
MCP Authentication Middleware — API key gate for all MCP tool calls.

Authority: Phase 99-B (Secure MCP wiring)
AC-ID: AC-P99-B-001
CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


# ============================================================================
# EXCEPTIONS
# ============================================================================


class AuthenticationError(Exception):
    """Raised when an MCP request fails API key authentication.

    The message is intentionally generic — never echoes key material.
    """


# ============================================================================
# MIDDLEWARE
# ============================================================================


class ApiKeyAuthMiddleware:
    """Validates API keys on incoming MCP requests.

    Extracts the API key from a configurable request header and delegates
    validation to the injected ``SecretsManager``.  Provides three levels
    of interaction:

    * ``extract_key(request)`` — raw header extraction, no validation.
    * ``authenticate(request)`` — returns ``True`` / ``False``.
    * ``enforce(request)``     — raises ``AuthenticationError`` on failure.

    Args:
        secrets_manager: A ``SecretsManager`` instance that owns the key store.
        header_name: HTTP-style header key to read the API key from.
                     Defaults to ``"X-API-Key"``.

    Example::

        middleware = ApiKeyAuthMiddleware(secrets_manager=sm)
        middleware.enforce({"headers": {"X-API-Key": raw_key}})
    """

    def __init__(
        self,
        secrets_manager: Any,
        header_name: str = "X-API-Key",
    ) -> None:
        """Initialise the middleware with a SecretsManager and header name.

        Args:
            secrets_manager: Provides ``validate_api_key(key) -> bool``.
            header_name: Header key to extract the API key from.
        """
        self.secrets_manager = secrets_manager
        self.header_name = header_name

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_key(self, request: Dict[str, Any]) -> Optional[str]:
        """Return the raw API key value from the request headers, or ``None``.

        Args:
            request: MCP request dict, expected to have a ``"headers"`` key.

        Returns:
            The string value of the configured header, or ``None`` if absent.
        """
        headers: Dict[str, Any] = request.get("headers", {})
        value = headers.get(self.header_name)
        if not isinstance(value, str):
            return None
        return value or None

    def authenticate(self, request: Dict[str, Any]) -> bool:
        """Return ``True`` if the request carries a valid API key.

        Delegates to ``SecretsManager.validate_api_key`` for constant-time
        comparison.  Never raises — callers that want an exception should use
        ``enforce()``.

        Args:
            request: MCP request dict.

        Returns:
            ``True`` if authentication succeeds, ``False`` otherwise.
        """
        try:
            raw_key = self.extract_key(request)
            if not raw_key:
                logger.debug("ApiKeyAuthMiddleware: no key in header '%s'", self.header_name)
                return False
            result: bool = self.secrets_manager.validate_api_key(raw_key)
            if not result:
                logger.warning("ApiKeyAuthMiddleware: key validation failed")
            return result
        except Exception as exc:  # pragma: no cover — defensive
            logger.error("ApiKeyAuthMiddleware: unexpected error during auth: %s", exc)
            return False

    def enforce(self, request: Dict[str, Any]) -> None:
        """Authenticate the request or raise ``AuthenticationError``.

        Args:
            request: MCP request dict.

        Raises:
            AuthenticationError: If the API key is missing or invalid.
        """
        if not self.authenticate(request):
            raise AuthenticationError(
                "Unauthorized: invalid or missing API key. Access denied."
            )
