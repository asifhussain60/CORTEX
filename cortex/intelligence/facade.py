"""Intelligence Facade — Single unified entry point for all CORTEX intelligence.

Consolidates 3 prior entry points into 1 Mediator:
  1. UnifiedIntelligenceProvider (cortex/intelligence/provider.py)
  2. LENSIntelligenceFacade (cortex/lens/facade.py)
  3. KnowledgeRegistryProxy (cortex/knowledge/registry_proxy.py)

Phase 123 extends the facade with 5 registry intelligence methods:
  4. load_governance()  — delegates to GovernanceRegistry (GAP-123-01)
  5. load_workflows()   — delegates to WorkflowTemplateRegistry (GAP-123-02)
  6. load_patterns()    — delegates to CustomPatternRegistry (GAP-123-03)
  7. load_plans()       — parses cortex-master.yaml → MasterPlanIndex (GAP-123-04)
  8. registry_index()   — cross-domain cortex-registry/ scan (GAP-123-05)

External callers should use IntelligenceFacade for all intelligence operations.
The 3 legacy entry points remain as compat imports.

Authority: Phase 107 Sub-Phase C (GAP-107-06) | Phase 123 (GAP-123-01–GAP-123-05)
CORE Rules: CORE-008, CORE-011, CORE-012, CORE-035 (single canonical)
"""
from __future__ import annotations

import logging
from pathlib import Path
import threading
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

__all__ = ["IntelligenceFacade", "get_intelligence_facade"]

# ── Singleton state (process-level) ──────────────────────────────────────────
_SINGLETON_LOCK: threading.Lock = threading.Lock()
_SINGLETON_INSTANCE: Optional["IntelligenceFacade"] = None


class IntelligenceFacade:
    """Unified Mediator facade for all CORTEX intelligence operations.

    Process-level singleton (GAP-117-05, Phase 117-b): every call to
    ``IntelligenceFacade()`` or ``get_intelligence_facade()`` returns the
    same instance, eliminating duplicate provider/registry init across
    orchestrators.

    Provides three core capabilities through one entry point:

    - ``analyze()`` — LENS-based code analysis (delegates to LENSOrchestrator)
    - ``synthesize()`` — Knowledge synthesis (delegates to KnowledgeSynthesisEngine)
    - ``query()`` — Knowledge registry queries (delegates to KnowledgeRegistryProxy)

    This replaces the prior pattern where callers had to choose between
    UnifiedIntelligenceProvider, LENSIntelligenceFacade, or KnowledgeRegistryProxy.

    Usage::

        from cortex.intelligence.facade import get_intelligence_facade

        facade = get_intelligence_facade()
        analysis = facade.analyze(file_path="cortex/core/engine.py", intent="REFACTOR")
        knowledge = facade.synthesize(query="TDD best practices")
        rules = facade.query(query="governance compliance")

    Attributes:
        _provider: Lazy-loaded UnifiedIntelligenceProvider instance.
        _registry: Lazy-loaded KnowledgeRegistryProxy instance.
    """

    def __new__(cls) -> "IntelligenceFacade":
        """Enforce process-level singleton via double-checked locking."""
        global _SINGLETON_INSTANCE
        if _SINGLETON_INSTANCE is None:
            with _SINGLETON_LOCK:
                if _SINGLETON_INSTANCE is None:
                    instance = super().__new__(cls)
                    instance._provider = None  # type: ignore[attr-defined]
                    instance._registry = None  # type: ignore[attr-defined]
                    # Phase 123: registry intelligence lazy-load slots
                    instance._governance_registry = None  # type: ignore[attr-defined]
                    instance._workflow_registry = None  # type: ignore[attr-defined]
                    instance._pattern_registry = None  # type: ignore[attr-defined]
                    instance._registry_index_cache = None  # type: ignore[attr-defined]
                    _SINGLETON_INSTANCE = instance
        return _SINGLETON_INSTANCE

    def __init__(self) -> None:
        """No-op — state is initialised once in ``__new__``."""
        # Intentionally empty: __new__ sets _provider and _registry on first call.

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

    # ── Phase 123: Registry Intelligence lazy-loaders ───────────────────

    def _get_governance_registry(self) -> Any:
        """Lazy-load the GovernanceRegistry singleton.

        Returns:
            Initialised GovernanceRegistry instance, or a null fallback.
        """
        if self._governance_registry is None:
            try:
                from cortex.orchestrators.core.governance_registry import GovernanceRegistry
                self._governance_registry = GovernanceRegistry.instance()
            except Exception as exc:
                logger.debug("IntelligenceFacade: governance_registry unavailable — %s", exc)
                self._governance_registry = _NullGovernanceRegistry()
        return self._governance_registry

    def _get_workflow_registry(self) -> Any:
        """Lazy-load the WorkflowTemplateRegistry.

        Returns:
            Initialised WorkflowTemplateRegistry instance, or a null fallback.
        """
        if self._workflow_registry is None:
            try:
                from cortex.orchestrators.workflow.template_registry import (
                    WorkflowTemplateRegistry,
                )
                self._workflow_registry = WorkflowTemplateRegistry()
            except Exception as exc:
                logger.debug("IntelligenceFacade: workflow_registry unavailable — %s", exc)
                self._workflow_registry = _NullWorkflowRegistry()
        return self._workflow_registry

    def _get_pattern_registry(self) -> Any:
        """Lazy-load the CustomPatternRegistry.

        Returns:
            Initialised CustomPatternRegistry instance, or a null fallback.
        """
        if self._pattern_registry is None:
            try:
                from cortex.intelligence.patterns.registry import CustomPatternRegistry
                self._pattern_registry = CustomPatternRegistry()
            except Exception as exc:
                logger.debug("IntelligenceFacade: pattern_registry unavailable — %s", exc)
                self._pattern_registry = _NullPatternRegistry()
        return self._pattern_registry

    # ── Public API ──────────────────────────────────────────────────────

    def load_governance(
        self,
        severity: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return governance rules from the GovernanceRegistry.

        Delegates to the singleton ``GovernanceRegistry`` — does NOT re-parse
        YAML on every call (CORE-035: single canonical load via registry).

        Args:
            severity: Optional severity filter (e.g. ``'blocked'``, ``'warning'``).
                When ``None``, all rules are returned.

        Returns:
            List of rule dicts, each containing at minimum ``rule_id``,
            ``name``, ``severity``, ``tier``, and ``description`` keys.
        """
        try:
            gov = self._get_governance_registry()
            rules: List[Dict[str, Any]] = []
            if hasattr(gov, "get_rules"):
                rules = list(gov.get_rules())
            elif hasattr(gov, "rules"):
                rules = list(gov.rules)
            if severity is not None:
                rules = [r for r in rules if r.get("severity") == severity]
            return rules
        except Exception as exc:
            logger.debug("IntelligenceFacade.load_governance: %s", exc)
            return []

    def load_workflows(
        self,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return workflow templates from the WorkflowTemplateRegistry.

        Delegates to ``WorkflowTemplateRegistry`` — does NOT re-scan the
        cortex-registry/ tree on every call (lazy-loaded once, CORE-035).

        Args:
            category: Optional category filter (e.g. ``'sdlc'``, ``'audit'``).
                When ``None``, all discovered templates are returned.

        Returns:
            List of workflow template dicts.  Each dict contains at minimum
            ``id``, ``name``, and ``category`` when available.
        """
        try:
            wf = self._get_workflow_registry()
            templates: List[Dict[str, Any]] = []
            if hasattr(wf, "_templates"):
                for tmpl in wf._templates.values():
                    entry: Dict[str, Any] = {
                        "id": tmpl.id,
                        "name": tmpl.name,
                        "category": tmpl.category,
                    }
                    entry["steps_count"] = len(tmpl.steps)
                    entry["source"] = tmpl.source
                    templates.append(entry)
            if category is not None:
                templates = [t for t in templates if t.get("category") == category]
            return templates
        except Exception as exc:
            logger.debug("IntelligenceFacade.load_workflows: %s", exc)
            return []

    def load_patterns(
        self,
        tag: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return custom pattern definitions from the CustomPatternRegistry.

        Delegates to ``CustomPatternRegistry`` — does NOT re-parse YAML on
        every call (lazy-loaded once, CORE-035).

        Args:
            tag: Optional tag filter (e.g. ``'tdd'``, ``'security'``).
                When ``None``, all registered patterns are returned.

        Returns:
            List of pattern dicts derived from ``PatternMetadata.to_dict()``.
        """
        try:
            pr = self._get_pattern_registry()
            patterns: List[Dict[str, Any]] = []
            if hasattr(pr, "list_patterns"):
                raw = pr.list_patterns()
                for p in raw:
                    patterns.append(p.to_dict() if hasattr(p, "to_dict") else dict(p))
            if tag is not None:
                patterns = [p for p in patterns if tag in p.get("tags", [])]
            return patterns
        except Exception as exc:
            logger.debug("IntelligenceFacade.load_patterns: %s", exc)
            return []

    def load_plans(
        self,
        status: Optional[str] = None,
    ) -> "Any":
        """Parse ``cortex-master.yaml`` and return a typed ``MasterPlanIndex``.

        Reads the THIN INDEX (CORE: ≤500 lines) and constructs a
        ``MasterPlanIndex`` containing one ``PhaseEntry`` per phase.  When
        ``status`` is provided, the index is filtered before return.

        Args:
            status: Optional status filter (e.g. ``'PLANNED'``, ``'COMPLETE'``).
                When ``None``, all phases are included.

        Returns:
            :class:`cortex.intelligence.models.master_plan_index.MasterPlanIndex`
            instance.  On failure returns an empty ``MasterPlanIndex``.
        """
        from cortex.intelligence.models.master_plan_index import MasterPlanIndex, PhaseEntry
        try:
            import yaml as _yaml
            master_path = (
                Path(__file__).resolve().parent.parent.parent
                / "cortex-registry"
                / "cortex-master.yaml"
            )
            raw_text = master_path.read_text(encoding="utf-8")
            source_line_count = raw_text.count("\n") + 1
            data = _yaml.safe_load(raw_text) or {}

            phases_raw: List[Any] = data.get("phases", [])
            phase_entries: List[PhaseEntry] = []
            for entry in phases_raw:
                if isinstance(entry, dict) and entry.get("id"):
                    phase_entries.append(PhaseEntry.from_dict(entry))

            index = MasterPlanIndex(
                phases=phase_entries,
                source_line_count=source_line_count,
                source_path=str(master_path),
                metadata={k: v for k, v in data.items() if k != "phases"},
            )
            if status is not None:
                index = index.filter_by_status(status)
            return index
        except Exception as exc:
            logger.debug("IntelligenceFacade.load_plans: %s", exc)
            from cortex.intelligence.models.master_plan_index import MasterPlanIndex
            return MasterPlanIndex()

    def classify_archetype(self, repo_path: "Path") -> "Dict[str, Any]":
        """Classify a repository into a canonical archetype using signal scoring.

        Delegates to :class:`~cortex.intelligence.archetype_classifier.ArchetypeClassifier`.
        Gracefully returns ``GENERIC`` if the classifier is unavailable.

        Args:
            repo_path: Path to the repository root directory.

        Returns:
            Dict with ``archetype`` (str), ``score`` (int), and ``breakdown`` (dict).

        Phase: 131 — GAP-131-01
        """
        try:
            from cortex.intelligence.archetype_classifier import get_archetype_classifier
            return get_archetype_classifier().classify(repo_path)
        except Exception as exc:
            logger.debug("IntelligenceFacade.classify_archetype: %s", exc)
            return {"archetype": "GENERIC", "score": 0, "breakdown": {}}

    def is_cortex_framework(self, repo_path: "Path") -> bool:
        """Return True if *repo_path* is a CORTEX framework repository.

        Delegates to :class:`~cortex.lens.analyzers.cortex_framework_analyzer.CortexFrameworkAnalyzer`.
        Gracefully returns ``False`` if the analyzer is unavailable.

        Args:
            repo_path: Path to the repository root directory.

        Returns:
            True when the repository contains ≥2 CORTEX structural signals.

        Phase: 131 — GAP-131-02
        """
        try:
            from cortex.lens.analyzers.cortex_framework_analyzer import CortexFrameworkAnalyzer
            return CortexFrameworkAnalyzer().is_cortex_framework(repo_path)
        except Exception as exc:
            logger.debug("IntelligenceFacade.is_cortex_framework: %s", exc)
            return False

    def registry_index(
        self,
        domain: Optional[str] = None,
    ) -> "List[Any]":
        """Scan ``cortex-registry/`` and return a typed ``RegistryIndexEntry`` list.

        Results are cached in the process-level singleton after the first call —
        subsequent calls return the same list object (CORE-035: no redundant I/O).

        Args:
            domain: Optional domain filter (e.g. ``'governance'``, ``'workflows'``).
                When ``None``, all discovered YAML files are returned.

        Returns:
            List of :class:`cortex.intelligence.models.registry_index.RegistryIndexEntry`.
        """
        try:
            if self._registry_index_cache is None:
                self._registry_index_cache = self._scan_registry_tree()
            result = self._registry_index_cache
            if domain is not None:
                result = [e for e in result if e.domain == domain]
            return result
        except Exception as exc:
            logger.debug("IntelligenceFacade.registry_index: %s", exc)
            return []

    def _scan_registry_tree(self) -> "List[Any]":
        """Scan the cortex-registry/ directory tree and build the index.

        Walks all YAML files under ``cortex-registry/``, creates a
        ``RegistryIndexEntry`` for each, and returns the full list.
        Called once; result cached in ``_registry_index_cache``.

        Returns:
            List of RegistryIndexEntry instances (one per discovered YAML file).
        """
        from cortex.intelligence.models.registry_index import RegistryIndexEntry
        registry_root = (
            Path(__file__).resolve().parent.parent.parent / "cortex-registry"
        )
        entries: List[Any] = []
        if not registry_root.exists():
            logger.warning(
                "IntelligenceFacade._scan_registry_tree: registry root not found: %s",
                registry_root,
            )
            return entries
        for yaml_file in sorted(registry_root.rglob("*.yaml")):
            try:
                entry = RegistryIndexEntry.from_path(yaml_file, registry_root)
                entries.append(entry)
            except Exception as exc:
                logger.debug(
                    "IntelligenceFacade._scan_registry_tree: skipping %s — %s",
                    yaml_file,
                    exc,
                )
        return entries

    def analyze(
        self,
        file_path: str = "",
        intent: str = "IMPLEMENT",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Run LENS-based code analysis on a file or directory.

        GAP-117-01 (Phase 117-a): delegates to ``provider.get_lens_analysis()``
        which returns real LENS data (ast_analysis, git_analysis, comment_analysis).
        The prior implementation checked for ``provider.analyze`` which does not
        exist on UnifiedIntelligenceProvider → fell through to empty-analysis fallback
        on every call.

        Args:
            file_path: Path to the file or directory to analyze.
            intent: The intent context (IMPLEMENT, REFACTOR, FIX, etc.).
            **kwargs: Additional options forwarded to the analysis pipeline.

        Returns:
            Structured dict with ``status``, ``file_path``, ``intent``, and
            ``analysis`` containing LENS output keys (ast_analysis, git_analysis,
            comment_analysis).  On graceful degradation the ``analysis`` dict may
            be empty but ``status`` will still be ``"ok"``.
        """
        try:
            provider = self._get_provider()
            # GAP-117-01: use get_lens_analysis() — the real LENS delegation method.
            # provider.analyze() does not exist; get_lens_analysis() returns
            # {'ast_analysis': …, 'git_analysis': …, 'comment_analysis': …} for real files.
            if hasattr(provider, "get_lens_analysis") and file_path:
                lens_data = provider.get_lens_analysis(file_path)
                if isinstance(lens_data, dict):
                    return {
                        "status": "ok",
                        "file_path": file_path,
                        "intent": intent,
                        "source": "intelligence_facade",
                        "analysis": lens_data,
                    }
            # Fallback: provider unavailable or no file_path provided
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
                "status": "ok",
                "file_path": file_path,
                "intent": intent,
                "source": "intelligence_facade",
                "analysis": {},
                "degraded": True,
                "degradation_reason": str(exc),
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


class _NullGovernanceRegistry:
    """Null-object fallback when GovernanceRegistry is unavailable."""

    rules: List[Dict[str, Any]] = []

    def get_rules(self) -> List[Dict[str, Any]]:
        """Return empty rules list.

        Returns:
            Empty list.
        """
        return []


class _NullWorkflowRegistry:
    """Null-object fallback when WorkflowTemplateRegistry is unavailable."""

    _templates: Dict[str, Any] = {}


class _NullPatternRegistry:
    """Null-object fallback when CustomPatternRegistry is unavailable."""

    def list_patterns(self) -> List[Any]:
        """Return empty patterns list.

        Returns:
            Empty list.
        """
        return []


# ── Module-level convenience helper ──────────────────────────────────────────


def get_intelligence_facade() -> IntelligenceFacade:
    """Return the process-level :class:`IntelligenceFacade` singleton.

    Preferred over direct ``IntelligenceFacade()`` calls — makes intent
    explicit and matches the singleton accessor pattern used across CORTEX
    (e.g. ``get_intelligence_provider()``, ``get_knowledge_registry()``).

    Returns:
        The single shared ``IntelligenceFacade`` instance for this process.
    """
    return IntelligenceFacade()
