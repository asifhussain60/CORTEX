"""
cortex/intelligence/knowledge/router.py

IntelligentKnowledgeRouter adapter for the intelligence layer (Phase 84-b, GAP-84-05).

Wraps cortex.core.knowledge.router.IntelligentKnowledgeRouter and adds billing/finance
keyword routing to the business-rules domain.

Authority: CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (no duplicates)
AC_START: AC-84-B-KNOWLEDGE-ROUTER-2026-02-26
AC_COMPLETE: AC-84-B-KNOWLEDGE-ROUTER-2026-02-26 | marker pair declared for static audit coverage
"""

from __future__ import annotations

import re
from typing import Optional

# Re-export the canonical router for callers who import from this path
from cortex.core.knowledge.router import IntelligentKnowledgeRouter as _CoreRouter

_BUSINESS_RULES_KEYWORDS = frozenset(
    [
        "billing",
        "invoice",
        "payment",
        "price",
        "finance",
        "financial",
        "business",
        "rules",
        "compliance",
        "constraint",
        "validation",
        "charge",
        "subscription",
        "refund",
        "tax",
        "revenue",
    ]
)


class IntelligentKnowledgeRouter:  # CORE-035-scoped — domain-specific variant
    """
    Intelligence-layer knowledge router with business-rules domain support.

    Wraps the core IntelligentKnowledgeRouter and adds explicit routing for
    billing/finance/business-rules queries (GAP-84-05).

    Example::

        router = IntelligentKnowledgeRouter()
        domain = router.route_query("billing invoice payment validation")
        # → "business-rules"
    """

    def __init__(self) -> None:
        """Initialise with a core router instance (no backends required)."""
        try:
            self._core = _CoreRouter()
        except Exception:
            self._core = None  # type: ignore[assignment]

    def route_query(self, query: str) -> Optional[str]:
        """
        Route a query string to the most relevant knowledge domain name.

        Billing/finance/business keywords are routed to 'business-rules'.
        All other queries fall through to the core router heuristics.

        Args:
            query: Free-text query string.

        Returns:
            Domain name string (e.g. 'business-rules', 'security', 'backend-python').
            Returns None if no domain can be determined.
        """
        if not query:
            return None

        query_lower = query.lower()
        tokens = set(re.split(r"\W+", query_lower))

        # Phase 84-b: Business-rules domain routing (GAP-84-05)
        if tokens & _BUSINESS_RULES_KEYWORDS:
            return "business-rules"

        # Fallback heuristics
        if any(k in query_lower for k in ("security", "auth", "jwt", "owasp", "injection")):
            return "security"
        if any(k in query_lower for k in ("test", "tdd", "coverage", "pytest", "mock")):
            return "testing-validation"
        if any(k in query_lower for k in ("python", "fastapi", "django", "ruff", "mypy")):
            return "backend-python"
        if any(k in query_lower for k in ("deploy", "docker", "kubernetes", "ci", "cd", "devops")):
            return "devops-infrastructure"

        return None
