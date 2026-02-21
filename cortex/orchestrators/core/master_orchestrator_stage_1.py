"""Stage 1: Comprehension — Intent extraction and LENS language analysis.

Implements the first stage of the Master Orchestrator 4-stage pipeline.
Extracts intent, keywords, and confidence from the incoming request.

CORE Governance:
    CORE-008: TDD mandatory
    CORE-011: Type hints on all functions
    CORE-012: Docstrings on all public APIs
    CORE-027: Audit trail logging

AC-PROD-003-01
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Stage1ComprehensionContext:
    """Input context for Stage 1 comprehension.

    Attributes:
        request: Raw user request text
        turn_number: Conversation turn number
        session_id: Optional session identifier
        metadata: Additional context metadata
    """

    request: str
    turn_number: int = 1
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Stage1Output:
    """Output produced by Stage 1 comprehension.

    Attributes:
        operation: Classified operation type
        intent: Extracted intent string
        keywords: Key terms extracted from request
        domain: Inferred domain
        confidence_score: Classification confidence (0.0–1.0)
        raw_request: Original request text
        metadata: Additional output metadata
    """

    operation: str
    intent: str
    keywords: List[str] = field(default_factory=list)
    domain: str = "core"
    confidence_score: float = 0.85
    raw_request: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class MasterOrchestrationStage1:
    """Stage 1 of the Master Orchestrator pipeline — Comprehension.

    Extracts intent, classifies operation type, and prepares context
    for downstream stages via LENS language analysis.

    Example:
        >>> stage1 = MasterOrchestrationStage1()
        >>> ctx = Stage1ComprehensionContext(request="implement OAuth2 login")
        >>> output = stage1.comprehend(ctx)
        >>> assert output.operation is not None
    """

    def __init__(self) -> None:
        """Initialise Stage 1 with logger and empty history."""
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.comprehension_history: List[Dict[str, Any]] = []

    def comprehend(
        self, context: Stage1ComprehensionContext
    ) -> Stage1Output:
        """Comprehend the incoming request and extract intent.

        Args:
            context: Stage1ComprehensionContext with the raw request

        Returns:
            Stage1Output with classified intent, keywords, and confidence
        """
        if context is None:
            return Stage1Output(
                operation="unknown",
                intent="unknown",
                confidence_score=0.0,
            )

        request = context.request or ""
        operation = self._classify_operation(request)
        keywords = self._extract_keywords(request)
        domain = self._infer_domain(keywords)
        confidence = self._compute_confidence(request, operation)

        output = Stage1Output(
            operation=operation,
            intent=request,
            keywords=keywords,
            domain=domain,
            confidence_score=confidence,
            raw_request=request,
        )

        self.comprehension_history.append(
            {"request": request, "operation": operation, "confidence": confidence}
        )
        self.logger.debug("Stage1: comprehended request=%r op=%s", request, operation)
        return output

    def get_comprehension_history(self) -> List[Dict[str, Any]]:
        """Return the list of past comprehension results.

        Returns:
            List of comprehension result dicts in chronological order
        """
        return list(self.comprehension_history)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _classify_operation(self, request: str) -> str:
        """Classify the operation type from the request text.

        Args:
            request: Raw request string

        Returns:
            Operation type string (e.g. 'implement', 'fix', 'audit')
        """
        lower = request.lower()
        if any(kw in lower for kw in ("implement", "build", "create", "add")):
            return "implement"
        if any(kw in lower for kw in ("fix", "bug", "broken", "error")):
            return "fix"
        if any(kw in lower for kw in ("refactor", "improve", "optimize")):
            return "refactor"
        if any(kw in lower for kw in ("audit", "scan", "check")):
            return "audit"
        if any(kw in lower for kw in ("design", "architect", "structure")):
            return "design"
        return "query"

    def _extract_keywords(self, request: str) -> List[str]:
        """Extract meaningful keywords from request text.

        Args:
            request: Raw request string

        Returns:
            List of keyword strings
        """
        stop_words = {
            "the", "a", "an", "is", "in", "on", "at", "to", "for",
            "of", "and", "or", "with", "my", "please", "can", "you",
        }
        words = request.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 2]

    def _infer_domain(self, keywords: List[str]) -> str:
        """Infer the target domain from keywords.

        Args:
            keywords: Extracted keyword list

        Returns:
            Domain string (e.g. 'api', 'core', 'persistence')
        """
        domain_hints = {
            "api": ["api", "endpoint", "rest", "http", "route"],
            "persistence": ["db", "database", "sql", "sqlite", "model"],
            "auth": ["auth", "oauth", "login", "token", "security"],
            "mcp": ["mcp", "tool", "server", "protocol"],
        }
        for domain, hints in domain_hints.items():
            if any(hint in keywords for hint in hints):
                return domain
        return "core"

    def _compute_confidence(self, request: str, operation: str) -> float:
        """Compute classification confidence.

        Args:
            request: Raw request text
            operation: Classified operation

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not request:
            return 0.0
        if operation == "query":
            return 0.70
        return 0.85
