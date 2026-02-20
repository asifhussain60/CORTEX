"""DomainContextManager — manages context across domain orchestrators."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class DomainContextManager:
    """Manages shared context across multiple domain orchestrators."""

    def __init__(self) -> None:
        self._contexts: Dict[str, Dict[str, Any]] = {}
        self._history: List[Dict[str, Any]] = []

    def set(self, domain: str, key: str, value: Any) -> None:
        self._contexts.setdefault(domain, {})[key] = value

    def get(self, domain: str, key: str, default: Any = None) -> Any:
        return self._contexts.get(domain, {}).get(key, default)

    def get_domain_context(self, domain: str) -> Dict[str, Any]:
        return dict(self._contexts.get(domain, {}))

    def merge_contexts(self, domains: List[str]) -> Dict[str, Any]:
        merged: Dict[str, Any] = {}
        for domain in domains:
            merged.update(self._contexts.get(domain, {}))
        return merged

    def clear_domain(self, domain: str) -> None:
        self._contexts.pop(domain, None)

    def snapshot(self) -> Dict[str, Any]:
        import copy
        return copy.deepcopy(self._contexts)
