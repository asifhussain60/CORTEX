"""
cortex.knowledge.best-practices — Best-Practice Knowledge Subdomain
====================================================================

All best-practice knowledge is stored in ``cortex-registry/knowledge/``
and accessed via :class:`cortex.knowledge.KnowledgeRegistryProxy`.

Sub-packages:
- technical   — backend-python, architecture, security, performance
- governance  — CORE rules, TDD, compliance standards
- business    — domain patterns, SaaS, product practices
- interaction — agent/orchestrator interaction patterns
- performance — profiling, observability, optimisation

Usage::

    from cortex.knowledge.best_practices import get_best_practices
    items = get_best_practices(domain="architecture")

CORE Rules: CORE-035 (single canonical), CORE-011, CORE-012
AC_START: AC-KNOWLEDGE-BESTPRACTICES-001
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from cortex.knowledge.registry_proxy import KnowledgeRegistryProxy

_proxy = KnowledgeRegistryProxy()

__all__ = ["get_best_practices", "all_best_practices"]


def get_best_practices(domain: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return best-practice entries, optionally filtered by domain.

    Args:
        domain: Optional domain filter (e.g. ``"architecture"``, ``"backend-python"``).

    Returns:
        List of knowledge entry dicts matching the filter.
    """
    return _proxy.query(domain=domain)


def all_best_practices() -> List[Dict[str, Any]]:
    """Return all best-practice knowledge entries from the registry.

    Returns:
        All knowledge entries as a flat list of dicts.
    """
    return _proxy.all()


# AC_COMPLETE: AC-KNOWLEDGE-BESTPRACTICES-001 ✅
