"""
cortex.knowledge.best-practices.technical — Technical Best Practices
====================================================================

Provides access to technical domain knowledge: backend-python, architecture,
security, performance-optimization, and testing-validation standards.

All knowledge content is stored in ``cortex-registry/knowledge/`` and served
via :class:`cortex.knowledge.KnowledgeRegistryProxy`.

CORE Rules: CORE-035, CORE-011, CORE-012
AC_START: AC-KNOWLEDGE-TECHNICAL-001
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from cortex.knowledge.registry_proxy import KnowledgeRegistryProxy

_proxy = KnowledgeRegistryProxy()

_TECHNICAL_DOMAINS = frozenset({
    "backend-python",
    "architecture",
    "security",
    "performance-optimization",
    "testing-validation",
})

__all__ = ["get_technical_knowledge", "TECHNICAL_DOMAINS"]

TECHNICAL_DOMAINS: frozenset = _TECHNICAL_DOMAINS


def get_technical_knowledge(domain: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return technical best-practice entries, optionally filtered by domain.

    Args:
        domain: Optional sub-domain filter (e.g. ``"architecture"``,
                ``"backend-python"``, ``"security"``).

    Returns:
        List of knowledge entry dicts. If *domain* is in :data:`TECHNICAL_DOMAINS`,
        results are filtered; otherwise all technical entries are returned.
    """
    if domain and domain in _TECHNICAL_DOMAINS:
        return _proxy.query(domain=domain)
    # Aggregate all technical sub-domains
    results: List[Dict[str, Any]] = []
    for tech_domain in sorted(_TECHNICAL_DOMAINS):
        results.extend(_proxy.query(domain=tech_domain))
    return results


# AC_COMPLETE: AC-KNOWLEDGE-TECHNICAL-001 ✅
