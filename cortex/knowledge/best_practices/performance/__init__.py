"""
cortex.knowledge.best-practices.performance — Performance Best Practices
========================================================================

Provides access to performance and observability knowledge: profiling,
metrics, monitoring, caching strategies, and system-optimisation standards.

CORE Rules: CORE-035, CORE-011, CORE-012
AC_START: AC-KNOWLEDGE-PERFORMANCE-001
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from cortex.knowledge.registry_proxy import KnowledgeRegistryProxy

_proxy = KnowledgeRegistryProxy()

__all__ = ["get_performance_knowledge"]


def get_performance_knowledge(topic: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return performance best-practice entries.

    Args:
        topic: Optional topic filter (e.g. ``"profiling"``, ``"monitoring"``,
               ``"caching"``).

    Returns:
        List of performance knowledge dicts from the registry.
    """
    return _proxy.query(domain="performance-optimization")


# AC_COMPLETE: AC-KNOWLEDGE-PERFORMANCE-001 ✅
