"""Dashboard extensibility helpers for optional business-domain endpoint integration."""

from __future__ import annotations

import os
from typing import Optional


DOMAIN_BRAIN_ENDPOINT_ENV = "DOMAIN_BRAIN_ENDPOINT"
DEFAULT_TIMEOUT_SECONDS = 2


def get_domain_brain_endpoint(default: Optional[str] = None) -> Optional[str]:
    """Resolve configurable domain brain endpoint.

    Defaults to None when endpoint is not configured.
    """
    endpoint = os.getenv(DOMAIN_BRAIN_ENDPOINT_ENV, default)
    if endpoint is None or str(endpoint).strip() == "":
        return None
    return str(endpoint)


def get_domain_timeout_seconds(default_timeout: int = DEFAULT_TIMEOUT_SECONDS) -> int:
    """Resolve timeout value for domain endpoint calls."""
    raw_timeout = os.getenv("DOMAIN_BRAIN_TIMEOUT_SECONDS")
    if raw_timeout is None:
        return default_timeout
    try:
        parsed = int(raw_timeout)
        return parsed if parsed > 0 else default_timeout
    except Exception:
        return default_timeout


def fetch_domain_data(payload: str) -> dict:
    """Placeholder integration hook with fallback strategy.

    If endpoint is not configured, returns fallback response.
    """
    endpoint = get_domain_brain_endpoint()
    timeout = get_domain_timeout_seconds()

    if endpoint is None:
        return {
            "status": "fallback",
            "endpoint": None,
            "timeout": timeout,
            "payload": payload,
        }

    try:
        return {
            "status": "configured",
            "endpoint": endpoint,
            "timeout": timeout,
            "payload": payload,
        }
    except Exception:
        return {
            "status": "fallback",
            "endpoint": None,
            "timeout": timeout,
            "payload": payload,
        }
