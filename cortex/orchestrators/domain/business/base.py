"""BusinessDomainOrchestrator — base class for all business domain orchestrators."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin


class BusinessDomainOrchestrator(OrchestratorProtocolMixin, ABC):
    """Abstract base orchestrator for business domains.

    Inherits cross-cutting LENS, KnSynth, and GovGate hooks from
    ``OrchestratorProtocolMixin`` (Phase 58) while preserving the
    domain-specific ``process()`` abstraction via ``ABC``.

    CORE-011: All public methods carry type hints.
    CORE-012: All public APIs carry docstrings.
    """

    _orch_version: str = "1.0.0"

    def __init__(self, domain_name: str) -> None:
        """Initialize instance.

        Args:
            domain_name: Human-readable name for this business domain.
        """
        self.domain_name = domain_name
        self._context: Dict[str, Any] = {}

    # ── OrchestratorProtocolMixin override ───────────────────
    def get_name(self) -> str:
        """Return orchestrator name derived from domain_name."""
        return f"{self.domain_name.capitalize()}Orchestrator"

    @abstractmethod
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a domain-specific request.

        Args:
            request: Incoming request payload.

        Returns:
            Response payload dict.
        """

    def get_domain_name(self) -> str:
        """Return the domain name for this orchestrator."""
        return self.domain_name

    def set_context(self, key: str, value: Any) -> None:
        """Store a key-value pair in the orchestrator context.

        Args:
            key: Context key.
            value: Context value.
        """
        self._context[key] = value

    def get_context(self) -> Dict[str, Any]:
        """Return a copy of the current orchestrator context."""
        return dict(self._context)

    def validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate that the incoming request is a well-formed dict.

        Args:
            request: Request payload to validate.

        Returns:
            True if request is a valid dict, False otherwise.
        """
        return isinstance(request, dict)

    def get_capabilities(self) -> List[str]:
        """Return the list of capabilities supported by this domain."""
        return []
