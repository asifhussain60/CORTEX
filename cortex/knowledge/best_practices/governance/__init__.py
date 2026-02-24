"""
cortex.knowledge.best-practices.governance — Governance Best Practices
=======================================================================

Provides access to CORTEX governance knowledge: CORE rules, TDD enforcement,
compliance standards, and audit practices.

Knowledge is sourced from ``cortex-registry/knowledge/`` via
:class:`cortex.knowledge.KnowledgeRegistryProxy` and supplemented with
canonical CORE rule metadata.

CORE Rules: CORE-035, CORE-011, CORE-012
AC_START: AC-KNOWLEDGE-GOVERNANCE-001
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from cortex.knowledge.registry_proxy import KnowledgeRegistryProxy

_proxy = KnowledgeRegistryProxy()

__all__ = ["get_governance_knowledge", "GOVERNANCE_CORE_RULES"]

# Canonical summary of active CORE rules for fast in-process access
GOVERNANCE_CORE_RULES: Dict[str, str] = {
    "CORE-002": "All output inline — never create .md/.txt report files",
    "CORE-008": "TDD mandatory — write failing test first, then implement",
    "CORE-011": "Type hints on all functions",
    "CORE-012": "Docstrings on all public APIs",
    "CORE-028": "File naming: snake_case only",
    "CORE-035": "Single canonical implementation — no duplicates",
    "CORE-048": "Holistic validation gate before IMPLEMENT/FIX/REFACTOR",
    "CORE-049": "Silent autonomous execution (progress bars only)",
    "CORE-050": "MCP tiered blocking",
    "CORE-064": "Sweep Completeness Contract — no partial sweeps",
}


def get_governance_knowledge(rule_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return governance best-practice entries, optionally filtered by CORE rule ID.

    Args:
        rule_id: Optional CORE rule ID (e.g. ``"CORE-008"``). If provided and found
                 in :data:`GOVERNANCE_CORE_RULES`, returns that rule's summary entry.

    Returns:
        List of governance knowledge dicts.
    """
    if rule_id and rule_id in GOVERNANCE_CORE_RULES:
        return [{"rule_id": rule_id, "description": GOVERNANCE_CORE_RULES[rule_id]}]
    registry_entries = _proxy.query(domain="governance")
    if not registry_entries:
        # Fall back to the canonical summary
        return [
            {"rule_id": rid, "description": desc}
            for rid, desc in GOVERNANCE_CORE_RULES.items()
        ]
    return registry_entries


# AC_COMPLETE: AC-KNOWLEDGE-GOVERNANCE-001 ✅
