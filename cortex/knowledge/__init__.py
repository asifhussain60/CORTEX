"""
cortex.knowledge — Knowledge Registry Module
=============================================

Phase 59-d: Converts the ghost directory into a live Python module.

Exposes ``KnowledgeRegistryProxy``, which loads domain knowledge from
YAML files stored in ``cortex-registry/knowledge/``.

CORE Rules: CORE-035 (single canonical), CORE-011 (type hints), CORE-012 (docstrings)
AC_START: AC-KNOWLEDGE-5904
"""
from cortex.knowledge.registry_proxy import KnowledgeRegistryProxy

__all__ = ["KnowledgeRegistryProxy"]

# AC_COMPLETE: AC-KNOWLEDGE-5904 (module __init__) ✅
