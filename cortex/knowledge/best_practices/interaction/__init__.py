"""
cortex.knowledge.best-practices.interaction — Agent/Orchestrator Interaction Patterns
=====================================================================================

Provides access to interaction best-practice knowledge: agent-orchestrator
communication protocols, MCP tool patterns, intent routing standards, and
HEXA-MODE interaction guidelines.

CORE Rules: CORE-035, CORE-011, CORE-012
AC_START: AC-KNOWLEDGE-INTERACTION-001
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from cortex.knowledge.registry_proxy import KnowledgeRegistryProxy

_proxy = KnowledgeRegistryProxy()

__all__ = ["get_interaction_knowledge"]


def get_interaction_knowledge(pattern: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return interaction best-practice entries.

    Args:
        pattern: Optional interaction pattern filter (e.g. ``"mcp"``,
                 ``"intent-routing"``, ``"agent-protocol"``).

    Returns:
        List of interaction knowledge dicts from the registry.
    """
    return _proxy.query(domain=pattern or "interaction")


# AC_COMPLETE: AC-KNOWLEDGE-INTERACTION-001 ✅
