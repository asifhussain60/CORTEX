"""
CORTEX MCP Orchestrator Tool Discovery.

Provides tool discovery functionality for MCP server endpoint:
- Queries all orchestrators for available tools
- Aggregates tool metadata (name, description, parameters)
- Returns JSON schema for each tool
- Caches results for 60 seconds

Phase 5 Task 3: Tool Discovery Endpoint
Date: 2026-01-27

CORE-011: All functions have type hints.
CORE-012: All public APIs have Google-style docstrings.
CORE-008: Implementation follows TDD specification from test suite.
CORE-030: No database_registry imports - Docker-first architecture.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from threading import Lock
import time


class OrchestratorToolDiscovery:
    """
    Discovers and caches tool definitions from all orchestrators.
    
    Queries orchestrators for their available tools and aggregates
    the results into a unified tool catalog with JSON schemas.
    
    Features:
    - Automatic caching with configurable TTL
    - Thread-safe cache access
    - Graceful handling of missing orchestrators
    - JSON Schema format for tool parameters
    
    Example:
        >>> discovery = OrchestratorToolDiscovery(cache_ttl=60)
        >>> tools = discovery.discover_all_tools()
        >>> print(f"Found {len(tools)} tools")
        Found 45 tools
    """
    
    def __init__(self, cache_ttl: int = 60) -> None:
        """
        Initialize tool discovery with cache configuration.
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default: 60)
        """
        self.cache_ttl = cache_ttl
        self._cache: Optional[List[Dict[str, Any]]] = None
        self._cache_timestamp: Optional[float] = None
        self._cache_lock = Lock()
    
    def discover_all_tools(self) -> List[Dict[str, Any]]:
        """
        Discover tools from all orchestrators.
        
        Queries all 23 orchestrators for their available tools and
        returns a unified list. Results are cached for cache_ttl seconds.
        
        Returns:
            List of tool definitions, each containing:
                - name: Tool name (string)
                - orchestrator: Orchestrator providing the tool (string)
                - description: Tool description (string)
                - parameters: JSON schema for tool parameters (dict)
        
        Example:
            >>> tools = discovery.discover_all_tools()
            >>> for tool in tools:
            ...     print(f"{tool['name']} from {tool['orchestrator']}")
        """
        with self._cache_lock:
            # Check if cache is still valid
            if self._is_cache_valid():
                return self._cache
            
            # Query all orchestrators
            tools = []
            orchestrator_names = get_all_orchestrator_names()
            
            for orch_name in orchestrator_names:
                try:
                    orch_tools = get_orchestrator_tools(orch_name)
                    tools.extend(orch_tools)
                except Exception as e:
                    # Log but don't fail - continue with other orchestrators
                    print(f"Warning: Failed to get tools from {orch_name}: {e}")
            
            # Update cache
            self._cache = tools
            self._cache_timestamp = time.time()
            
            return tools
    
    def get_discovery_response(self) -> Dict[str, Any]:
        """
        Get tool discovery response in MCP format.
        
        Returns a complete response with tools, count, cache status,
        and cache expiry timestamp.
        
        Returns:
            Dictionary containing:
                - tools: List of tool definitions
                - count: Number of tools
                - cached: Whether response is from cache
                - cache_expires_at: ISO 8601 timestamp of cache expiry
        
        Example:
            >>> response = discovery.get_discovery_response()
            >>> print(f"Found {response['count']} tools, cached: {response['cached']}")
        """
        tools = self.discover_all_tools()
        
        # Calculate cache expiry time
        if self._cache_timestamp:
            expiry_time = datetime.fromtimestamp(
                self._cache_timestamp + self.cache_ttl,
                tz=datetime.now().astimezone().tzinfo
            )
            cache_expires_at = expiry_time.isoformat()
        else:
            cache_expires_at = datetime.now().isoformat()
        
        return {
            "tools": tools,
            "count": len(tools),
            "cached": self.is_cached(),
            "cache_expires_at": cache_expires_at
        }
    
    def is_cached(self) -> bool:
        """
        Check if discovery results are cached.
        
        Returns:
            True if cache is valid, False otherwise.
        """
        return self._is_cache_valid()
    
    def invalidate_cache(self) -> None:
        """
        Manually invalidate the cache.
        
        Forces next discover_all_tools() call to query orchestrators.
        
        Example:
            >>> discovery.invalidate_cache()
            >>> tools = discovery.discover_all_tools()  # Queries orchestrators
        """
        with self._cache_lock:
            self._cache = None
            self._cache_timestamp = None
    
    def _is_cache_valid(self) -> bool:
        """
        Check if cache is still valid based on TTL.
        
        Returns:
            True if cache exists and hasn't expired, False otherwise.
        """
        if self._cache is None or self._cache_timestamp is None:
            return False
        
        elapsed = time.time() - self._cache_timestamp
        return elapsed < self.cache_ttl


def get_all_orchestrator_names() -> List[str]:
    """
    Get names of all available orchestrators.
    
    Returns:
        List of orchestrator names (23 total expected).
    
    Example:
        >>> names = get_all_orchestrator_names()
        >>> print(names)
        ['TDDOrchestrator', 'RefactoringOrchestrator', ...]
    """
    # Phase 5: Hardcoded list of 23 orchestrators
    # Future: Query from wiring.yaml when available
    return [
        # Core Orchestrators (6)
        "MasterOrchestrator",
        "InteractionOrchestrator",
        "IntentRouter",
        "TDDOrchestrator",
        "WorkflowOrchestrator",
        "WrappedTDDOrchestrator",
        
        # Domain Orchestrators (6)
        "RefactoringOrchestrator",
        "PlanningOrchestrator",
        "DomainOrchestrator",
        "ConversationOrchestrator",
        "SeleniumPlaywrightOrchestrator",
        "DocumentationOrchestrator",
        
        # Support Orchestrators (11)
        "OnboardingOrchestrator",
        "ToolDiscoveryOrchestrator",
        "UpgradeOrchestrator",
        "RollbackOrchestrator",
        "SetupOrchestrator",
        "ComposedOrchestrator",
        "ValidationOrchestrator",
        "DeploymentOrchestrator",
        "MonitoringOrchestrator",
        "SecurityOrchestrator",
        "IntegrationOrchestrator",
    ]


def get_orchestrator_tools(orchestrator_name: str) -> List[Dict[str, Any]]:
    """
    Get tool definitions from a specific orchestrator.
    
    Queries the orchestrator for its available tools and returns
    their definitions in a standardized format.
    
    Args:
        orchestrator_name: Name of orchestrator to query.
    
    Returns:
        List of tool definitions from the orchestrator.
    
    Raises:
        Exception: If orchestrator cannot be queried.
    
    Example:
        >>> tools = get_orchestrator_tools("TDDOrchestrator")
        >>> for tool in tools:
        ...     print(tool['name'])
    """
    # Phase 5: Mock implementation with sample tool schemas
    # Future: Query actual orchestrator instances
    
    # Sample tool definitions by orchestrator
    tool_map = {
        "TDDOrchestrator": [
            {
                "name": "generate_tests",
                "orchestrator": "TDDOrchestrator",
                "description": "Generate test cases using TDD methodology",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "module_path": {
                            "type": "string",
                            "description": "Path to module to test"
                        },
                        "test_type": {
                            "type": "string",
                            "enum": ["unit", "integration", "e2e"],
                            "description": "Type of tests to generate"
                        }
                    },
                    "required": ["module_path"]
                }
            }
        ],
        "RefactoringOrchestrator": [
            {
                "name": "refactor_code",
                "orchestrator": "RefactoringOrchestrator",
                "description": "Refactor code following best practices",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to file to refactor"
                        },
                        "strategy": {
                            "type": "string",
                            "enum": ["extract_method", "rename", "simplify"],
                            "description": "Refactoring strategy"
                        }
                    },
                    "required": ["file_path", "strategy"]
                }
            }
        ],
        "PlanningOrchestrator": [
            {
                "name": "create_plan",
                "orchestrator": "PlanningOrchestrator",
                "description": "Create implementation plan for feature",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "feature_description": {
                            "type": "string",
                            "description": "Description of feature to plan"
                        },
                        "complexity": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Feature complexity"
                        }
                    },
                    "required": ["feature_description"]
                }
            }
        ],
    }
    
    # Return tools for orchestrator, or empty list if not in map
    return tool_map.get(orchestrator_name, [])


# Global tool discovery instance
_tool_discovery: Optional[OrchestratorToolDiscovery] = None
_discovery_lock = Lock()


def get_orchestrator_tool_discovery() -> OrchestratorToolDiscovery:
    """
    Get or create global tool discovery instance.
    
    Thread-safe singleton pattern.
    
    Returns:
        Global OrchestratorToolDiscovery instance.
    
    Example:
        >>> discovery = get_orchestrator_tool_discovery()
        >>> tools = discovery.discover_all_tools()
    """
    global _tool_discovery
    
    if _tool_discovery is None:
        with _discovery_lock:
            if _tool_discovery is None:
                _tool_discovery = OrchestratorToolDiscovery()
    
    return _tool_discovery


def discover_orchestrator_tools() -> List[Dict[str, Any]]:
    """
    Discover all tools from orchestrators (convenience function).
    
    Uses global singleton instance and returns cached results
    when available.
    
    Returns:
        List of tool definitions.
    
    Example:
        >>> tools = discover_orchestrator_tools()
        >>> print(f"Found {len(tools)} tools")
    """
    discovery = get_orchestrator_tool_discovery()
    return discovery.discover_all_tools()


def get_orchestrator_tool_schema(tool_name: str) -> Optional[Dict[str, Any]]:
    """
    Get schema for a specific tool by name.
    
    Searches all discovered tools and returns the matching tool
    definition, or None if not found.
    
    Args:
        tool_name: Name of tool to find.
    
    Returns:
        Tool definition dict, or None if not found.
    
    Example:
        >>> schema = get_orchestrator_tool_schema("generate_tests")
        >>> if schema:
        ...     print(schema['description'])
    """
    tools = discover_orchestrator_tools()
    
    for tool in tools:
        if tool.get("name") == tool_name:
            return tool
    
    return None
