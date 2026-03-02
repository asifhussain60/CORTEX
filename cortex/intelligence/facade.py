"""Intelligence Facade — Single unified entry point for all CORTEX intelligence.

Consolidates 3 prior entry points into 1 Mediator:
  1. UnifiedIntelligenceProvider (cortex/intelligence/provider.py)
  2. LENSIntelligenceFacade (cortex/lens/facade.py)
  3. KnowledgeRegistryProxy (cortex/knowledge/registry_proxy.py)

External callers should use IntelligenceFacade for all intelligence operations.
The 3 legacy entry points remain as compat imports.

Authority: Phase 107 Sub-Phase C (GAP-107-06)
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical)
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

__all__ = ["IntelligenceFacade"]


class IntelligenceFacade:
    """Unified Mediator facade for all CORTEX intelligence operations.

    Provides three core capabilities through one entry point:

    - ``analyze()`` — LENS-based code analysis (delegates to LENSOrchestrator)
    - ``synthesize()`` — Knowledge synthesis (delegates to KnowledgeSynthesisEngine)
    - ``query()`` — Knowledge registry queries (delegates to KnowledgeRegistryProxy)

    This replaces the prior pattern where callers had to choose between
    UnifiedIntelligenceProvider, LENSIntelligenceFacade, or KnowledgeRegistryProxy.

    Usage::

        from cortex.intelligence.facade import IntelligenceFacade

        facade = IntelligenceFacade()
        analysis = facade.analyze(file_path="cortex/core/engine.py", intent="REFACTOR")
        knowledge = facade.synthesize(query="TDD best practices")
        rules = facade.query(query="governance compliance")

    Attributes:
        _provider: Lazy-loaded UnifiedIntelligenceProvider instance.
        _registry: Lazy-loaded KnowledgeRegistryProxy instance.
    """

    def __init__(self) -> None:
        """Initialise the IntelligenceFacade with lazy-loaded delegates."""
        self._provider: Optional[Any] = None
        self._registry: Optional[Any] = None

    # ── Lazy delegation ─────────────────────────────────────────────────

    def _get_provider(self) -> Any:
        """Lazy-load the UnifiedIntelligenceProvider."""
        if self._provider is None:
            try:
                from cortex.intelligence.provider import (
                    get_intelligence_provider,
                )
                self._provider = get_intelligence_provider()
            except Exception as exc:
                logger.debug("IntelligenceFacade: provider unavailable — %s", exc)
                self._provider = _NullProvider()
        return self._provider

    def _get_registry(self) -> Any:
        """Lazy-load the KnowledgeRegistryProxy."""
        if self._registry is None:
            try:
                from cortex.knowledge.registry_proxy import (
                    KnowledgeRegistryProxy,
                )
                self._registry = KnowledgeRegistryProxy()
            except Exception as exc:
                logger.debug("IntelligenceFacade: registry unavailable — %s", exc)
                self._registry = _NullRegistry()
        return self._registry

    # ── Public API ──────────────────────────────────────────────────────

    def analyze(
        self,
        file_path: str = "",
        intent: str = "IMPLEMENT",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Run LENS-based code analysis on a file or directory.

        Delegates to the UnifiedIntelligenceProvider's analysis pipeline.

        Args:
            file_path: Path to the file or directory to analyze.
            intent: The intent context (IMPLEMENT, REFACTOR, FIX, etc.).
            **kwargs: Additional options forwarded to the analysis pipeline.

        Returns:
            Structured dict with at least a ``status`` key.
        """
        try:
            provider = self._get_provider()
            if hasattr(provider, "analyze"):
                result = provider.analyze(file_path=file_path, intent=intent, **kwargs)
                if isinstance(result, dict):
                    return result
            # Provider doesn't have analyze or returned non-dict — graceful fallback
            return {
                "status": "ok",
                "file_path": file_path,
                "intent": intent,
                "source": "intelligence_facade",
                "analysis": {},
            }
        except Exception as exc:
            logger.debug("IntelligenceFacade.analyze: %s", exc)
            return {
                "status": "error",
                "file_path": file_path,
                "error": str(exc),
            }

    def synthesize(
        self,
        query: str = "",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Synthesize knowledge from CORTEX + Company sources.

        Delegates to the UnifiedIntelligenceProvider's synthesis pipeline.
        Maps the facade ``query`` param to the provider's ``intent`` param to
        bridge the API difference introduced in Phase 107 consolidation.

        Args:
            query: The query or topic to synthesize knowledge for.
            **kwargs: Additional options forwarded to the synthesis engine.

        Returns:
            Structured dict with at least a ``status`` key.
        """
        try:
            provider = self._get_provider()
            if hasattr(provider, "synthesize"):
                import inspect as _inspect
                _sig = _inspect.signature(provider.synthesize)
                _params = set(_sig.parameters.keys())
                if "intent" in _params:
                    # UnifiedIntelligenceProvider.synthesize(intent, ...) — map query → intent
                    _call_kwargs = {k: v for k, v in kwargs.items() if k in _params}
                    result = provider.synthesize(intent=query or "QUERY", **_call_kwargs)
                elif "query" in _params:
                    result = provider.synthesize(query=query, **kwargs)
                else:
                    result = provider.synthesize(**kwargs)
                if isinstance(result, dict):
                    return result
                # UnifiedIntelligenceContext returned — convert to dict
                if hasattr(result, "__dict__"):
                    return {
                        "status": "ok",
                        "query": query,
                        "source": "intelligence_facade",
                        "synthesis": vars(result),
                    }
            return {
                "status": "ok",
                "query": query,
                "source": "intelligence_facade",
                "synthesis": {},
            }
        except Exception as exc:
            logger.debug("IntelligenceFacade.synthesize: %s", exc)
            return {
                "status": "error",
                "query": query,
                "error": str(exc),
            }

    def query(
        self,
        query: str = "",
        domain: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Query the knowledge registry for matching entries.

        Delegates to KnowledgeRegistryProxy.

        Args:
            query: Search query string.
            domain: Optional domain filter (e.g. "governance", "security").
            **kwargs: Additional options forwarded to the registry proxy.

        Returns:
            Structured dict with at least a ``status`` key.
        """
        try:
            registry = self._get_registry()
            results: List[Dict[str, Any]] = []
            if hasattr(registry, "query"):
                raw = registry.query(domain=domain, **kwargs) if domain else registry.all()
                if isinstance(raw, list):
                    results = raw
            return {
                "status": "ok",
                "query": query,
                "domain": domain,
                "source": "intelligence_facade",
                "results": results,
                "count": len(results),
            }
        except Exception as exc:
            logger.debug("IntelligenceFacade.query: %s", exc)
            return {
                "status": "error",
                "query": query,
                "error": str(exc),
            }


# ── Null object fallbacks (avoid None checks) ─────────────────────────


class _NullProvider:
    """Null-object fallback when the real provider is unavailable."""

    def analyze(self, **kwargs: Any) -> Dict[str, Any]:
        return {"status": "unavailable", "source": "null_provider"}

    def synthesize(self, **kwargs: Any) -> Dict[str, Any]:
        return {"status": "unavailable", "source": "null_provider"}


class _NullRegistry:
    """Null-object fallback when the real registry is unavailable."""

    def all(self) -> List[Dict[str, Any]]:
        return []

    def query(self, **kwargs: Any) -> List[Dict[str, Any]]:
        return []
