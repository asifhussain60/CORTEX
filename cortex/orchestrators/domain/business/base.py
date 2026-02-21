"""BusinessDomainOrchestrator — base class for all business domain orchestrators."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BusinessDomainOrchestrator(ABC):
    """Abstract base orchestrator for business domains."""

    def __init__(self, domain_name: str) -> None:
        """Initialize instance."""
        self.domain_name = domain_name
        self._context: Dict[str, Any] = {}

    @abstractmethod
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a domain-specific request."""

    def get_domain_name(self) -> str:
        """Return the domain name for this orchestrator."""
        return self.domain_name

    def set_context(self, key: str, value: Any) -> None:
        """Store a key-value pair in the orchestrator context."""
        self._context[key] = value

    def get_context(self) -> Dict[str, Any]:
        """Return a copy of the current orchestrator context."""
        return dict(self._context)

    def validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate that the incoming request is a well-formed dict."""
        return isinstance(request, dict)

    def get_capabilities(self) -> List[str]:
        """Return the list of capabilities supported by this domain."""
        return []
