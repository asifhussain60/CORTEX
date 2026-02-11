"""
OrchestratorLookup - Registry Adapter for Intent Router

AC-PHASE-8.2-01 / Task ROUTE-002
Bridges IntentRouter to Git-backed YAML orchestrator registry.
Provides orchestrator instance resolution by name, capabilities, and keywords.

CORE Governance:
  - CORE-008: TDD (tests created first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging
  - CORE-030: Implementation Truth (verify registry, not docs)
  - CORE-035: Single Canonical Implementation

Author: Asif Hussain
Date: 2026-01-30
"""

import importlib
import threading
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, List, Optional, Set, Tuple

from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator
from cortex.core.result import Err, Ok, Result
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

# AC-CORE-035-01: Import canonical WiringMetadata
from cortex.models.orchestrator_metadata import WiringMetadata as OrchestratorMetadata


class OrchestratorLookup:
    """
    Adapter for resolving orchestrator instances from wiring registry.

    Provides keyword-based, capability-based, and name-based lookup
    of orchestrators for the IntentRouter.

    Thread-safe singleton pattern with instance caching.

    Example:
        lookup = OrchestratorLookup.instance()
        orch = lookup.get_by_name("OnboardingOrchestrator")
        if orch is not None:
            result = orch.execute(parameters)

    CORE Governance:
      - CORE-008: TDD (tests first)
      - CORE-011: Type hints on all methods
      - CORE-012: Docstrings (Google style)
      - CORE-030: Verifies actual registry, not documentation
    """

    _instance: Optional['OrchestratorLookup'] = None
    _lock = threading.RLock()

    def __init__(self) -> None:
        """
        Initialize OrchestratorLookup.

        Loads orchestrator registry from wiring.yaml and caches
        orchestrator instances for fast lookup.

        Raises:
            RuntimeError: If audit logger cannot be initialized
        """
        self.logger: EnhancedAuditLogger = EnhancedAuditLogger.instance()
        self._registry_cache: Dict[str, OrchestratorMetadata] = {}
        self._instance_cache: Dict[str, IOrchestrator] = {}
        self._keyword_index: Dict[str, List[str]] = {}
        self._capability_index: Dict[str, List[str]] = {}

        # Load registry on initialization
        self._load_registry()

        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.2-01",
            operation="ORCHESTRATOR_LOOKUP_INIT",
            success=True,
            details={
                "orchestrators_registered": len(self._registry_cache),
                "keywords_indexed": len(self._keyword_index),
                "capabilities_indexed": len(self._capability_index)
            }
        )

    @classmethod
    def instance(cls) -> 'OrchestratorLookup':
        """
        Get singleton instance of OrchestratorLookup.

        Thread-safe singleton pattern.

        Returns:
            OrchestratorLookup: Singleton instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = OrchestratorLookup()
        return cls._instance

    def _load_registry(self) -> None:
        """
        Load orchestrator registry from wiring.yaml (SSOT).

        Builds indexes for fast keyword and capability lookup.

        FIX: After moving intelligence from prompts to code, this must load
        from the actual wiring registry, not hardcoded values.

        Uses GitBackedRegistry to load all 26 orchestrators from wiring.yaml.
        """
        try:
            # Import the wiring bootstrap to get actual orchestrator registry
            from cortex.wiring import bootstrap_cortex

            # Get the wiring registry (loads from wiring.yaml)
            wiring_registry = bootstrap_cortex()
            orchestrator_names = wiring_registry.list_orchestrators()

            # Load each orchestrator's metadata from wiring
            for name in orchestrator_names:
                spec = wiring_registry.get_orchestrator_spec(name)
                if spec:
                    # FIX: wiring.yaml has 'name' (alias) and 'class' (actual class name)
                    # E.g., name="DocumentationOrchestrator", class="EnhancedDocumentationOrchestrator"
                    # We need to use 'class' for instantiation but 'name' as registry key
                    metadata = OrchestratorMetadata(
                        name=name,
                        module=spec.get("module", ""),
                        category=spec.get("category", "unknown"),
                        capabilities=spec.get("capabilities", []),
                        priority=spec.get("priority", 50),
                        wired=True,
                        class_name=spec.get("class", name)  # Use actual class name for import
                    )
                    self._registry_cache[name] = metadata

                    # Build capability index
                    for capability in metadata.capabilities:
                        if capability not in self._capability_index:
                            self._capability_index[capability] = []
                        self._capability_index[capability].append(name)

            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.2-01",
                operation="REGISTRY_LOADED_FROM_WIRING",
                success=True,
                details={
                    "orchestrators": len(self._registry_cache),
                    "source": "wiring.yaml",
                    "capabilities_indexed": len(self._capability_index)
                }
            )

        except (ImportError, ValueError, Exception) as e:
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.2-01",
                operation="REGISTRY_LOAD_FAILED",
                success=False,
                details={"error": str(e), "fallback": "empty_registry"}
            )
            # Fallback: empty registry (graceful degradation)
            self._registry_cache = {}

    def _register_orchestrator(
        self,
        config: Dict[str, Any],
        category: str
    ) -> None:
        """
        Register an orchestrator from wiring config.

        Args:
            config: Orchestrator configuration from wiring.yaml
            category: Orchestrator category (core, domain, support)
        """
        name = config.get("name", "")
        if not name:
            return

        metadata = OrchestratorMetadata(
            name=name,
            module=config.get("module", ""),
            category=category,
            capabilities=config.get("capabilities", []),
            priority=config.get("priority", 0),
            wired=True
        )

        self._registry_cache[name] = metadata

        # Build capability index
        for capability in metadata.capabilities:
            if capability not in self._capability_index:
                self._capability_index[capability] = []
            self._capability_index[capability].append(name)

    def get_by_name(self, name: str) -> Optional[IOrchestrator]:
        """
        Get orchestrator instance by name (case-insensitive).

        Looks up orchestrator in registry, loads module dynamically,
        and returns cached instance.

        Args:
            name: Orchestrator class name (e.g., "OnboardingOrchestrator")

        Returns:
            Orchestrator instance or None if not found

        Example:
            lookup = OrchestratorLookup.instance()
            orch = lookup.get_by_name("OnboardingOrchestrator")
            if orch is not None:
                orch.execute(params)
        """
        # AC-ROUTE-002-AC04: Case-insensitive lookup
        # Normalize to match registry keys (original case)
        normalized_name = None
        for registry_name in self._registry_cache.keys():
            if registry_name.lower() == name.lower():
                normalized_name = registry_name
                break

        if normalized_name is None:
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.2-01",
                operation="ORCHESTRATOR_NOT_FOUND",
                success=False,
                details={"name": name}
            )
            return None

        # Check instance cache first (use normalized name)
        if normalized_name in self._instance_cache:
            return self._instance_cache[normalized_name]

        # Check registry
        metadata = self._registry_cache.get(normalized_name)
        if metadata is None:
            return None

        # Load orchestrator instance
        instance = self._load_orchestrator_instance(metadata)
        if instance is not None:
            self._instance_cache[normalized_name] = instance

        return instance

    def _load_orchestrator_instance(
        self,
        metadata: OrchestratorMetadata
    ) -> Optional[IOrchestrator]:
        """
        Load orchestrator instance from module.

        Args:
            metadata: Orchestrator metadata from registry

        Returns:
            Orchestrator instance or None if loading failed
        """
        try:
            # Import module
            module = importlib.import_module(metadata.module)

            # Get class - use class_name if available, otherwise use name
            # FIX: wiring.yaml has name (alias) vs class (actual class)
            # E.g., name="DocumentationOrchestrator", class="EnhancedDocumentationOrchestrator"
            class_name = metadata.class_name if metadata.class_name else metadata.name
            orchestrator_class = getattr(module, class_name)

            # Instantiate (assuming no-arg constructor)
            instance = orchestrator_class()

            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.2-01",
                operation="ORCHESTRATOR_LOADED",
                success=True,
                details={
                    "name": metadata.name,
                    "class": class_name,
                    "module": metadata.module
                }
            )

            return instance

        except (ImportError, AttributeError, TypeError, Exception) as e:
            # Catch all exceptions to prevent crashes during loading
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.2-01",
                operation="ORCHESTRATOR_LOAD_FAILED",
                success=False,
                details={
                    "name": metadata.name,
                    "class": metadata.class_name if metadata.class_name else metadata.name,
                    "module": metadata.module,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            return None

    def find_by_capabilities(
        self,
        capabilities: List[str]
    ) -> List[IOrchestrator]:
        """
        Find orchestrators by required capabilities.

        Args:
            capabilities: List of required capabilities

        Returns:
            List of orchestrator instances matching capabilities

        Example:
            lookup = OrchestratorLookup.instance()
            orchs = lookup.find_by_capabilities(["lens_protocol", "comprehension"])
        """
        matching_names: Set[str] = set()

        for capability in capabilities:
            if capability in self._capability_index:
                matching_names.update(self._capability_index[capability])

        # Load orchestrator instances
        instances: List[IOrchestrator] = []
        for name in matching_names:
            instance = self.get_by_name(name)
            if instance is not None:
                instances.append(instance)

        return instances

    def find_by_keywords(
        self,
        keywords: List[str],
        orchestrator_config: Dict[str, Any]
    ) -> List[Tuple[str, float]]:
        """
        Find orchestrators by keyword matching.

        Scores orchestrators based on keyword overlap with routing config.

        Args:
            keywords: List of keywords from user request
            orchestrator_config: Routing configuration from intent-routing.yaml

        Returns:
            List of (orchestrator_name, confidence_score) tuples

        Example:
            lookup = OrchestratorLookup.instance()
            matches = lookup.find_by_keywords(
                ["onboard", "setup"],
                routing_config
            )
        """
        matches: List[Tuple[str, float]] = []

        for intent_type, domains in orchestrator_config.items():
            if not isinstance(domains, dict):
                continue

            for domain, config in domains.items():
                if not isinstance(config, dict):
                    continue

                orchestrator_name = config.get("orchestrator")
                config_keywords = config.get("keywords", [])
                confidence_boost = config.get("confidence_boost", 0.0)

                if not orchestrator_name or not config_keywords:
                    continue

                # Calculate keyword overlap
                matched_keywords = set(keywords) & set(config_keywords)
                if matched_keywords:
                    # Score = (matched / total) + confidence_boost
                    overlap_score = len(matched_keywords) / len(config_keywords)
                    total_score = min(1.0, overlap_score + confidence_boost)

                    matches.append((orchestrator_name, total_score))

        # Sort by confidence (descending)
        matches.sort(key=lambda x: x[1], reverse=True)

        return matches

    def list_by_domain(self, domain: str) -> List[IOrchestrator]:
        """
        List all orchestrators in a domain.

        Args:
            domain: Domain name (core, domain, support)

        Returns:
            List of orchestrator instances in domain

        Example:
            lookup = OrchestratorLookup.instance()
            core_orchs = lookup.list_by_domain("core")
        """
        matching_names = [
            name for name, metadata in self._registry_cache.items()
            if metadata.category == domain
        ]

        instances: List[IOrchestrator] = []
        for name in matching_names:
            instance = self.get_by_name(name)
            if instance is not None:
                instances.append(instance)

        return instances

    def resolve_instance(self, orchestrator_name: str) -> Result[IOrchestrator]:
        """
        Resolve orchestrator instance with Result pattern.

        Args:
            orchestrator_name: Orchestrator class name

        Returns:
            Result[IOrchestrator]: Ok with instance or Err with message

        Example:
            lookup = OrchestratorLookup.instance()
            result = lookup.resolve_instance("OnboardingOrchestrator")
            if result.is_ok():
                orch = result.unwrap()
                orch.execute(params)
        """
        instance = self.get_by_name(orchestrator_name)

        if instance is None:
            return Err(f"Orchestrator '{orchestrator_name}' not found in registry")

        return Ok(instance)

    def validate_orchestrator_exists(self, name: str) -> bool:
        """
        Check if orchestrator exists in registry.

        Args:
            name: Orchestrator class name

        Returns:
            True if orchestrator exists, False otherwise

        Example:
            lookup = OrchestratorLookup.instance()
            if lookup.validate_orchestrator_exists("OnboardingOrchestrator"):
                print("Orchestrator available")
        """
        return name in self._registry_cache

    @lru_cache(maxsize=128)
    def get_orchestrator_metadata(self, name: str) -> Optional[OrchestratorMetadata]:
        """
        Get orchestrator metadata without loading instance.

        Cached for performance.

        Args:
            name: Orchestrator class name

        Returns:
            OrchestratorMetadata or None if not found
        """
        return self._registry_cache.get(name)

    def clear_cache(self) -> None:
        """Clear instance and metadata caches (for testing)."""
        self._instance_cache.clear()
        self.get_orchestrator_metadata.cache_clear()

    def get_multiple(
        self,
        names: List[str],
        filter_none: bool = False
    ) -> List[Optional[IOrchestrator]]:
        """
        Get multiple orchestrator instances at once.

        AC-ID: AC-ROUTE-002-AC06, AC-ROUTE-002-AC07
        Purpose: Bulk resolution of orchestrators (e.g., for fallback chains)

        Args:
            names: List of orchestrator class names
            filter_none: If True, filter out None values from result

        Returns:
            List of orchestrator instances (may contain None if not filter_none)

        Example:
            lookup = OrchestratorLookup.instance()
            orchs = lookup.get_multiple(["TDDOrchestrator", "LENSOrchestrator"])
        """
        instances = []

        for name in names:
            instance = self.get_by_name(name)
            if filter_none:
                if instance is not None:
                    instances.append(instance)
            else:
                instances.append(instance)

        return instances

    def list_available(self) -> List[str]:
        """
        List all available orchestrator names in registry.

        AC-ID: AC-ROUTE-002-AC08
        Purpose: Discovery of available orchestrators for routing

        Returns:
            List of orchestrator class names

        Example:
            lookup = OrchestratorLookup.instance()
            available = lookup.list_available()
            print(f"Available orchestrators: {available}")
        """
        return list(self._registry_cache.keys())


# Module-level exports
__all__ = [
    "OrchestratorLookup",
    "OrchestratorMetadata",
]
