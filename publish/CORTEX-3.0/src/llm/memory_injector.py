from __future__ import annotations

from typing import List, Dict, Optional

# Placeholder: will integrate with tier2 knowledge graph to pull namespace-aware memory

def build_memory_context(
    user_query: str,
    namespace: Optional[str] = None,
    include_generic: bool = True,
    limit: int = 5,
) -> List[Dict[str, str]]:
    """Return a list of memory snippets to inject into prompts.

    Each snippet is a dict like {"title": ..., "content": ..., "source": ...}.
    This is a stub; wire to Tier 2 KnowledgeGraph later.
    """
    snippets: List[Dict[str, str]] = []
    if namespace:
        snippets.append({
            "title": f"namespace:{namespace}",
            "content": f"Context for namespace {namespace} (stub)",
            "source": "memory_injector",
        })
    if include_generic:
        snippets.append({
            "title": "cortex:generic",
            "content": "Generic CORTEX memory summary (stub)",
            "source": "memory_injector",
        })
    return snippets[:limit]
