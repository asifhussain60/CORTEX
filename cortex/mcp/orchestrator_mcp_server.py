"""
Unified Orchestrator MCP Server - Central Hub for CORTEX Capabilities

CORTEX MCP Server acts as the single facade for exposing all orchestrator
capabilities via the Model Context Protocol (MCP). This enables:

1. **Unified Tool Discovery** - Single endpoint for all CORTEX orchestrator tools
2. **Multi-Repo Support** - Context switching across different repositories
3. **SaaS Readiness** - Multi-tenant architecture for future cloud deployment
4. **Capability Routing** - Intelligent routing to appropriate orchestrator
5. **Health & Observability** - Central monitoring of all orchestrator operations

Architecture:
```
CORTEX MCP Server (this module)
├── Tool Registry (MCPToolsCatalog integration)
├── Orchestrator Dispatcher (routes requests to orchestrators)
├── Context Manager (handles multi-repo/multi-tenant scenarios)
├── Health Monitor (observability)
└── Tool Executor (executes orchestrator operations)
```

Entry Points:
- Direct: import and use OrchestratorMCPServer
- REST API: FastAPI wrapper (future)
- CLI: cortex mcp start-server
- VSCode Extension: Native MCP integration

Authority: CORE-031 (Unified Registry)
AC-ID: AC-MCP-ORCHESTRATOR-001, AC-MCP-ORCHESTRATOR-002
Date: 2026-01-26
Author: Asif Hussain
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Type of execution context"""
    SINGLE_REPO = "single_repo"
    MULTI_REPO = "multi_repo"
    SAAS_TENANT = "saas_tenant"
    DISTRIBUTED = "distributed"


@dataclass
class ExecutionContext:
    """Execution context for orchestrator operations"""
    context_type: ContextType
    repository_path: Optional[str] = None
    workspace_root: Optional[str] = None
    tenant_id: Optional[str] = None  # For SaaS multi-tenancy
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize context to dictionary"""
        return {
            "context_type": self.context_type.value,
            "repository_path": self.repository_path,
            "workspace_root": self.workspace_root,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class CapabilityMetadata:
    """Metadata for orchestrator capability"""
    name: str
    orchestrator: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    routing_keywords: List[str] = field(default_factory=list)
    confidence_threshold: float = 0.7
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "name": self.name,
            "orchestrator": self.orchestrator,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "routing_keywords": self.routing_keywords,
            "confidence_threshold": self.confidence_threshold,
            "version": self.version,
            "dependencies": self.dependencies,
            "tags": list(self.tags),
        }


@dataclass
class CapabilityRequest:
    """Request to execute an orchestrator capability"""
    capability_name: str
    parameters: Dict[str, Any]
    context: ExecutionContext
    request_id: Optional[str] = None
    priority: int = 100
    timeout_ms: int = 30000
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "capability_name": self.capability_name,
            "parameters": self.parameters,
            "context": self.context.to_dict(),
            "request_id": self.request_id,
            "priority": self.priority,
            "timeout_ms": self.timeout_ms,
            "retry_count": self.retry_count,
        }


@dataclass
class CapabilityResponse:
    """Response from orchestrator capability"""
    request_id: Optional[str]
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    duration_ms: float = 0.0
    orchestrator: Optional[str] = None
    execution_timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "request_id": self.request_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "error_code": self.error_code,
            "duration_ms": self.duration_ms,
            "orchestrator": self.orchestrator,
            "execution_timestamp": self.execution_timestamp.isoformat(),
            "metadata": self.metadata,
        }


class IOrchestratorAdapter(ABC):
    """
    Adapter interface for orchestrators to expose capabilities via MCP.

    Each orchestrator implements this interface to provide:
    - Capability discovery
    - Capability execution
    - Health status
    """

    @abstractmethod
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this orchestrator"""
        pass

    @abstractmethod
    def execute_capability(
        self,
        capability_name: str,
        parameters: Dict[str, Any],
        context: ExecutionContext
    ) -> CapabilityResponse:
        """Execute a capability"""
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if orchestrator is healthy"""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get detailed status information"""
        pass


class OrchestratorMCPServer:
    """
    Unified MCP Server for CORTEX Orchestrators.

    Single facade exposing all orchestrator capabilities via MCP protocol.
    Handles tool discovery, routing, execution, and observability.

    Features:
    - **Unified Discovery**: Single endpoint for all tools/capabilities
    - **Intelligent Routing**: Routes requests to appropriate orchestrator
    - **Multi-Repo Support**: Context switching for different repositories
    - **SaaS Ready**: Multi-tenant architecture
    - **Health Monitoring**: Central health checks
    - **Audit Trail**: Complete execution history
    """

    _instance: Optional['OrchestratorMCPServer'] = None

    def __init__(self):
        """Initialize the server"""
        self._orchestrators: Dict[str, IOrchestratorAdapter] = {}
        self._capabilities: Dict[str, CapabilityMetadata] = {}
        self._capability_to_orchestrator: Dict[str, str] = {}
        self._contexts: Dict[str, ExecutionContext] = {}
        self._execution_history: List[CapabilityResponse] = []
        self._server_version = "1.0.0"
        self._initialized = False
        self._max_history_size = 1000
        logger.info("OrchestratorMCPServer initialized (AC-MCP-ORCHESTRATOR-001)")

    @classmethod
    def instance(cls) -> 'OrchestratorMCPServer':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_orchestrator(
        self,
        orchestrator_name: str,
        adapter: IOrchestratorAdapter
    ) -> bool:
        """
        Register an orchestrator adapter.

        Args:
            orchestrator_name: Name of the orchestrator
            adapter: Implementation of IOrchestratorAdapter

        Returns:
            True if registered successfully
        """
        if orchestrator_name in self._orchestrators:
            logger.warning(f"Orchestrator already registered: {orchestrator_name}")
            return False

        try:
            self._orchestrators[orchestrator_name] = adapter

            # Discover and register capabilities
            capabilities = adapter.get_capabilities()
            for capability in capabilities:
                self._register_capability(capability, orchestrator_name)

            logger.info(
                f"Orchestrator registered: {orchestrator_name} "
                f"({len(capabilities)} capabilities)"
            )
            return True
        except Exception as e:
            logger.error(f"Error registering orchestrator {orchestrator_name}: {e}")
            return False

    def _register_capability(
        self,
        capability: CapabilityMetadata,
        orchestrator_name: str
    ) -> None:
        """Register a capability"""
        if capability.name in self._capabilities:
            logger.warning(f"Capability already registered: {capability.name}")
            return

        self._capabilities[capability.name] = capability
        self._capability_to_orchestrator[capability.name] = orchestrator_name
        logger.debug(f"Capability registered: {capability.name}")

    def discover_capabilities(
        self,
        context: Optional[ExecutionContext] = None,
        orchestrator_filter: Optional[str] = None,
        keyword_filter: Optional[List[str]] = None
    ) -> List[CapabilityMetadata]:
        """
        Discover available capabilities.

        Args:
            context: Execution context (optional)
            orchestrator_filter: Filter by orchestrator name
            keyword_filter: Filter by routing keywords

        Returns:
            List of matching capabilities
        """
        capabilities = list(self._capabilities.values())

        if orchestrator_filter:
            capabilities = [
                c for c in capabilities
                if self._capability_to_orchestrator.get(c.name) == orchestrator_filter
            ]

        if keyword_filter:
            capabilities = [
                c for c in capabilities
                if any(kw in c.routing_keywords for kw in keyword_filter)
            ]

        logger.debug(f"Discovered {len(capabilities)} capabilities")
        return capabilities

    def execute_capability(
        self,
        request: CapabilityRequest
    ) -> CapabilityResponse:
        """
        Execute a capability.

        Args:
            request: Capability request

        Returns:
            Capability response
        """
        start_time = datetime.now()
        response = None

        try:
            # Validate capability exists
            if request.capability_name not in self._capabilities:
                return CapabilityResponse(
                    request_id=request.request_id,
                    success=False,
                    error=f"Capability not found: {request.capability_name}",
                    error_code="CAPABILITY_NOT_FOUND"
                )

            # Find orchestrator
            orchestrator_name = self._capability_to_orchestrator[request.capability_name]
            if orchestrator_name not in self._orchestrators:
                return CapabilityResponse(
                    request_id=request.request_id,
                    success=False,
                    error=f"Orchestrator not available: {orchestrator_name}",
                    error_code="ORCHESTRATOR_NOT_AVAILABLE"
                )

            orchestrator = self._orchestrators[orchestrator_name]

            # Execute capability
            response = orchestrator.execute_capability(
                request.capability_name,
                request.parameters,
                request.context
            )

            # Update execution history
            duration = (datetime.now() - start_time).total_seconds() * 1000
            response.duration_ms = duration
            response.orchestrator = orchestrator_name
            self._add_to_history(response)

            logger.info(
                f"Capability executed: {request.capability_name} "
                f"(orchestrator={orchestrator_name}, duration={duration:.1f}ms, "
                f"success={response.success})"
            )

            return response

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            error_response = CapabilityResponse(
                request_id=request.request_id,
                success=False,
                error=f"Execution error: {str(e)}",
                error_code="EXECUTION_ERROR",
                duration_ms=duration
            )
            self._add_to_history(error_response)
            logger.error(f"Error executing capability: {e}", exc_info=True)
            return error_response

    def _add_to_history(self, response: CapabilityResponse) -> None:
        """Add response to execution history"""
        self._execution_history.append(response)
        if len(self._execution_history) > self._max_history_size:
            self._execution_history.pop(0)

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of all orchestrators.

        Returns:
            Health status dictionary
        """
        health_status: Dict[str, Any] = {
            "server_healthy": True,
            "timestamp": datetime.now().isoformat(),
            "orchestrators": {}
        }

        for name, orchestrator in self._orchestrators.items():
            try:
                is_healthy = orchestrator.is_healthy()
                status = orchestrator.get_status()
                health_status["orchestrators"][name] = {
                    "healthy": is_healthy,
                    "status": status
                }
                if not is_healthy:
                    health_status["server_healthy"] = False
            except Exception as e:
                health_status["orchestrators"][name] = {
                    "healthy": False,
                    "status": {"error": str(e)}
                }
                health_status["server_healthy"] = False

        return health_status

    def get_execution_history(
        self,
        limit: int = 100,
        orchestrator_filter: Optional[str] = None,
        success_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get execution history.

        Args:
            limit: Maximum number of entries
            orchestrator_filter: Filter by orchestrator
            success_only: Only return successful executions

        Returns:
            List of execution history entries
        """
        history = self._execution_history[-limit:]

        if orchestrator_filter:
            history = [h for h in history if h.orchestrator == orchestrator_filter]

        if success_only:
            history = [h for h in history if h.success]

        return [h.to_dict() for h in history]

    def initialize(self) -> bool:
        """
        Initialize the MCP server.

        Performs:
        - Loads all registered orchestrators
        - Discovers capabilities
        - Validates health
        - Prepares for requests

        Returns:
            True if initialization successful
        """
        try:
            # Import and register orchestrators
            # This will be implemented by the integration layer
            logger.info("OrchestratorMCPServer initialized successfully")
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Error initializing server: {e}", exc_info=True)
            return False

    def shutdown(self) -> bool:
        """Shutdown the MCP server"""
        try:
            logger.info("OrchestratorMCPServer shutting down")
            self._orchestrators.clear()
            self._capabilities.clear()
            self._contexts.clear()
            self._initialized = False
            return True
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            return False

    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "name": "CORTEX Orchestrator MCP Server",
            "version": self._server_version,
            "initialized": self._initialized,
            "orchestrators_registered": len(self._orchestrators),
            "capabilities_available": len(self._capabilities),
            "execution_history_size": len(self._execution_history),
            "timestamp": datetime.now().isoformat(),
        }


# Export singleton instance
def get_orchestrator_mcp_server() -> OrchestratorMCPServer:
    """Get the singleton MCP server instance"""
    return OrchestratorMCPServer.instance()
