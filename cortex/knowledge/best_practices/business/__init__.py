"""
cortex.knowledge.best-practices.business — Business Domain Best Practices
=========================================================================

Provides access to business-domain knowledge: SaaS patterns, domain modelling,
product engineering standards, and enterprise delivery practices.

CORE Rules: CORE-035, CORE-011, CORE-012
AC_START: AC-KNOWLEDGE-BUSINESS-001
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from cortex.knowledge.registry_proxy import KnowledgeRegistryProxy

_proxy = KnowledgeRegistryProxy()

__all__ = ["get_business_knowledge"]


def get_business_knowledge(domain: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return business-domain best-practice entries.

    Args:
        domain: Optional sub-domain filter (e.g. ``"saas"``, ``"product"``).

    Returns:
        List of business knowledge dicts from the registry.
    """
    return _proxy.query(domain=domain or "business")


# AC_COMPLETE: AC-KNOWLEDGE-BUSINESS-001 ✅
