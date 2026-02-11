"""
DiscoveryOrchestrator - Infrastructure Topology Discovery

Unified orchestrator for discovering infrastructure topology including:
- Configuration files (web.config, appsettings.json, docker-compose, etc.)
- Database connections (ORMs, migrations, schemas)
- API endpoints (Swagger/OpenAPI, REST, GraphQL, gRPC)
- Microservices topology (service mesh, API gateways, message brokers)
- Testing frameworks (pytest, Jest, coverage configs)
- Security/monitoring (auth, logging, APM)

Task: DISC-001
Authority: PHASE-9-DISCOVERY-ORCHESTRATOR.yaml
Status: Phase 9.1 - Stage 1

Governance:
- CORE-008: TDD (tests written first)
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
- CORE-027: Audit trail logging
- CORE-030: Implementation Truth verification
- CORE-035: Single Canonical Implementation
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from cortex.brain.discovery import DiscoveryPlugin, TopologyMap
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

logger = logging.getLogger(__name__)


class DiscoveryType(Enum):
    """
    Types of infrastructure discovery.

    Attributes:
        CONFIG: Configuration file discovery
        DATABASE: Database topology discovery
        API: API endpoint mapping
        MICROSERVICES: Microservices topology
        TESTING: Testing framework detection
        SECURITY: Security/monitoring discovery
        LENS: LENS-powered code analysis
    """
    CONFIG = "config"
    DATABASE = "database"
    API = "api"
    MICROSERVICES = "microservices"
    TESTING = "testing"
    SECURITY = "security"
    LENS = "lens"


@dataclass
class DiscoveryResult:
    """
    Result from a discovery operation.

    Attributes:
        discovery_type: Type of discovery performed
        data: Discovered data
        success: Whether discovery succeeded
        error: Error message if failed
        execution_time_ms: Time taken for discovery
    """
    discovery_type: DiscoveryType
    data: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    execution_time_ms: float = 0.0


class DiscoveryOrchestrator:
    """
    Unified infrastructure topology discovery orchestrator.

    Coordinates multiple discovery plugins to build complete topology map
    of application infrastructure. Supports plugin-based architecture for
    extensibility, caching for performance, and parallel execution.

    Features:
    - Plugin registration for different discovery types
    - Multi-level caching (memory, optional file/Redis)
    - Parallel plugin execution for performance
    - Error isolation (plugin failures don't crash others)
    - LENS integration for code-based config analysis

    Example:
        ```python
        orchestrator = DiscoveryOrchestrator(repo_path=Path("/my/repo"))

        # Register plugins
        orchestrator.register_plugin(DiscoveryType.CONFIG, ConfigDiscovery())
        orchestrator.register_plugin(DiscoveryType.DATABASE, DatabaseDiscovery())

        # Discover complete topology
        topology = orchestrator.discover_topology()

        # Or discover specific type
        db_topology = orchestrator.discover_by_type(DiscoveryType.DATABASE)
        ```

    Attributes:
        repo_path: Path to repository to analyze
        plugins: Registered discovery plugins
        cache_enabled: Whether caching is enabled
        parallel_execution: Whether to run plugins in parallel
        audit_logger: Audit trail logger
    """

    def __init__(
        self,
        repo_path: Path,
        enable_cache: bool = True,
        parallel_execution: bool = True,
        max_workers: int = 4,
    ):
        """
        Initialize DiscoveryOrchestrator.

        Args:
            repo_path: Path to repository to analyze
            enable_cache: Enable caching of discovery results
            parallel_execution: Run plugins in parallel
            max_workers: Maximum parallel workers
        """
        self.repo_path = repo_path
        self.cache_enabled = enable_cache
        self.parallel_execution = parallel_execution
        self.max_workers = max_workers

        self.plugins: Dict[DiscoveryType, DiscoveryPlugin] = {}
        self._cache: Dict[str, TopologyMap] = {}
        self._cache_key = str(repo_path)

        self.audit_logger = EnhancedAuditLogger()

        logger.info(
            f"DiscoveryOrchestrator initialized for {repo_path} "
            f"(cache={enable_cache}, parallel={parallel_execution})"
        )

    def register_plugin(
        self,
        discovery_type: DiscoveryType,
        plugin: DiscoveryPlugin,
    ) -> None:
        """
        Register a discovery plugin for a specific type.

        Args:
            discovery_type: Type of discovery this plugin handles
            plugin: Plugin instance implementing DiscoveryPlugin interface
        """
        self.plugins[discovery_type] = plugin
        logger.info(f"Registered {discovery_type.value} discovery plugin")

    def discover_topology(self) -> TopologyMap:
        """
        Discover complete infrastructure topology.

        Runs all registered plugins to build unified topology map.
        Uses caching if enabled. Executes plugins in parallel if configured.

        Returns:
            Complete topology map with all discovered data
        """
        # AC_START logging
        self.audit_logger.log_operation_start(
            ac_id="DISC-001",
            operation="AC_START",
            details={"action": "discover_topology", "repo_path": str(self.repo_path)},
        )

        start_time = time.time()

        # Check cache
        if self.cache_enabled and self._cache_key in self._cache:
            logger.info("Cache hit - returning cached topology")
            topology = self._cache[self._cache_key]

            self.audit_logger.log_operation_complete(
                ac_id="DISC-001",
                operation="AC_COMPLETE",
                success=True,
                details={"action": "discover_topology", "cache_hit": True},
            )

            return topology

        # No cache - run discovery
        logger.info(f"Cache miss - discovering topology ({len(self.plugins)} plugins)")

        topology = TopologyMap()

        if self.parallel_execution and len(self.plugins) > 1:
            # Parallel execution
            results = self._discover_parallel()
        else:
            # Sequential execution
            results = self._discover_sequential()

        # Aggregate results into topology
        for result in results:
            if result.success:
                self._merge_result_into_topology(topology, result)
            else:
                logger.warning(
                    f"{result.discovery_type.value} discovery failed: {result.error}"
                )

        # Add metadata
        topology.metadata = {
            "discovery_time_ms": (time.time() - start_time) * 1000,
            "cache_hit": False,
            "plugins_run": len(self.plugins),
            "repo_path": str(self.repo_path),
        }

        # Cache result
        if self.cache_enabled:
            self._cache[self._cache_key] = topology
            logger.info("Topology cached for future requests")

        # AC_COMPLETE logging
        self.audit_logger.log_operation_complete(
            ac_id="DISC-001",
            operation="AC_COMPLETE",
            success=True,
            details={
                "action": "discover_topology",
                "discovery_time_ms": topology.metadata["discovery_time_ms"],
                "cache_hit": False,
            },
        )

        return topology

    def discover_by_type(self, discovery_type: DiscoveryType) -> Dict[str, Any]:
        """
        Discover specific topology type only.

        Args:
            discovery_type: Type of discovery to perform

        Returns:
            Discovery results for specified type

        Raises:
            ValueError: If no plugin registered for type
        """
        if discovery_type not in self.plugins:
            raise ValueError(f"No plugin registered for {discovery_type.value}")

        logger.info(f"Discovering {discovery_type.value} topology")

        plugin = self.plugins[discovery_type]

        try:
            start_time = time.time()
            data = plugin.discover(self.repo_path)
            execution_time = (time.time() - start_time) * 1000

            logger.info(
                f"{discovery_type.value} discovery complete "
                f"({execution_time:.2f}ms)"
            )

            return data

        except Exception as e:
            logger.error(f"{discovery_type.value} discovery failed: {e}")
            return {}

    def invalidate_cache(
        self,
        file_patterns: Optional[List[str]] = None,
    ) -> None:
        """
        Invalidate cached topology.

        Forces re-discovery on next request. Optionally specify file patterns
        that triggered invalidation for logging.

        Args:
            file_patterns: File patterns that triggered invalidation
        """
        if self._cache_key in self._cache:
            del self._cache[self._cache_key]
            logger.info(
                f"Cache invalidated for {self.repo_path} "
                f"(patterns: {file_patterns or 'manual'})"
            )

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Cache statistics including size and hit/miss info
        """
        return {
            "cache_enabled": self.cache_enabled,
            "cache_size": len(self._cache),
            "cached_repos": list(self._cache.keys()),
        }

    def _discover_sequential(self) -> List[DiscoveryResult]:
        """
        Run discovery plugins sequentially.

        Returns:
            List of discovery results
        """
        results = []

        for discovery_type, plugin in self.plugins.items():
            result = self._run_plugin(discovery_type, plugin)
            results.append(result)

        return results

    def _discover_parallel(self) -> List[DiscoveryResult]:
        """
        Run discovery plugins in parallel.

        Returns:
            List of discovery results
        """
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all plugin tasks
            future_to_type = {
                executor.submit(self._run_plugin, dtype, plugin): dtype
                for dtype, plugin in self.plugins.items()
            }

            # Collect results as they complete
            for future in as_completed(future_to_type):
                result = future.result()
                results.append(result)

        return results

    def _run_plugin(
        self,
        discovery_type: DiscoveryType,
        plugin: DiscoveryPlugin,
    ) -> DiscoveryResult:
        """
        Run a single discovery plugin with error handling.

        Args:
            discovery_type: Type of discovery
            plugin: Plugin to run

        Returns:
            Discovery result with success/failure info
        """
        start_time = time.time()

        try:
            logger.debug(f"Running {discovery_type.value} discovery...")
            data = plugin.discover(self.repo_path)
            execution_time = (time.time() - start_time) * 1000

            return DiscoveryResult(
                discovery_type=discovery_type,
                data=data,
                success=True,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_msg = str(e)

            logger.error(
                f"{discovery_type.value} discovery failed: {error_msg}",
                exc_info=True,
            )

            return DiscoveryResult(
                discovery_type=discovery_type,
                data={},
                success=False,
                error=error_msg,
                execution_time_ms=execution_time,
            )

    def _merge_result_into_topology(
        self,
        topology: TopologyMap,
        result: DiscoveryResult,
    ) -> None:
        """
        Merge discovery result into topology map.

        Args:
            topology: Topology map to update
            result: Discovery result to merge
        """
        if result.discovery_type == DiscoveryType.CONFIG:
            topology.config = result.data
        elif result.discovery_type == DiscoveryType.DATABASE:
            topology.databases = result.data
        elif result.discovery_type == DiscoveryType.API:
            topology.apis = result.data
        elif result.discovery_type == DiscoveryType.MICROSERVICES:
            topology.microservices = result.data
        elif result.discovery_type == DiscoveryType.TESTING:
            topology.testing = result.data
        elif result.discovery_type == DiscoveryType.SECURITY:
            topology.security = result.data


def get_discovery_orchestrator(
    repo_path: Path,
    **kwargs: Any,
) -> DiscoveryOrchestrator:
    """
    Factory function to create DiscoveryOrchestrator instance.

    Args:
        repo_path: Path to repository to analyze
        **kwargs: Additional configuration options

    Returns:
        Configured DiscoveryOrchestrator instance
    """
    return DiscoveryOrchestrator(repo_path=repo_path, **kwargs)
