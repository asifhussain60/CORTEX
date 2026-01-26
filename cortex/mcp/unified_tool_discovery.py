"""
Unified MCP Tool Discovery API - Single Source of Truth for all MCP tools.

AC-MCP-CENTRALIZED-DISCOVERY: Central registry for all MCP tools across CORTEX
- Aggregates tools from all 23 orchestrators
- Provides single discovery endpoint
- Enables SaaS-style multi-repo tool exposure
- Auto-discovers tools from orchestrator.get_mcp_tools()

Authority: CORE-035 (Single Canonical Implementation)
Date: 2026-01-26
"""

from __future__ import annotations

import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from cortex.core.result import Result, Ok, Err

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """MCP Tool Categories"""
    GOVERNANCE = "governance"
    ORCHESTRATION = "orchestration"
    KNOWLEDGE = "knowledge"
    UTILITY = "utility"
    DISCOVERY = "discovery"


@dataclass
class MCPTool:
    """Unified MCP Tool definition"""
    name: str
    description: str
    category: ToolCategory
    parameters: Dict[str, Any] = field(default_factory=dict)
    orchestrator_source: str = "unknown"
    version: str = "1.0.0"
    discoverable: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "parameters": self.parameters,
            "orchestrator_source": self.orchestrator_source,
            "version": self.version,
            "discoverable": self.discoverable
        }


class UnifiedMCPToolDiscovery:
    """
    Single source of truth for MCP tool discovery across all orchestrators.
    
    Replaces:
    - MCPToolsRegistry (static catalog)
    - Scattered get_mcp_tools() implementations
    - Ad-hoc tool discovery per orchestrator
    
    Provides:
    - Auto-discovery from all 23 orchestrators
    - Dynamic tool registration
    - Category-based filtering
    - Multi-repo SaaS preparation
    """
    
    _instance: Optional['UnifiedMCPToolDiscovery'] = None
    
    def __init__(self):
        """Initialize discovery engine"""
        self._tools: Dict[str, MCPTool] = {}
        self._tool_index: Dict[str, Set[str]] = {
            cat.value: set() for cat in ToolCategory
        }
        self._discovery_log: List[Dict[str, Any]] = []
        self._last_discovery: Optional[datetime] = None
        self._orchestrators_scanned: Set[str] = set()
    
    @classmethod
    def instance(cls) -> 'UnifiedMCPToolDiscovery':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset instance (for testing)"""
        cls._instance = None
    
    def register_tool(
        self,
        tool: MCPTool,
        replace_if_exists: bool = False
    ) -> Result[None]:
        """
        Register an MCP tool.
        
        Args:
            tool: MCPTool to register
            replace_if_exists: If True, replace existing tool
            
        Returns:
            Result indicating success or error
        """
        if tool.name in self._tools and not replace_if_exists:
            return Err(f"Tool already registered: {tool.name}")
        
        self._tools[tool.name] = tool
        self._tool_index[tool.category.value].add(tool.name)
        
        logger.debug(f"Registered tool: {tool.name} (category: {tool.category.value})")
        return Ok(None)
    
    def register_tools_batch(
        self,
        tools: List[MCPTool],
        replace_if_exists: bool = False
    ) -> Result[Dict[str, Any]]:
        """
        Register multiple tools atomically.
        
        Args:
            tools: List of MCPTool instances
            replace_if_exists: If True, replace existing tools
            
        Returns:
            Result with registration statistics
        """
        registered = 0
        skipped = 0
        errors: List[str] = []
        
        for tool in tools:
            result = self.register_tool(tool, replace_if_exists)
            if result.is_ok():
                registered += 1
            else:
                skipped += 1
                errors.append(f"{tool.name}: {result.error}")
        
        stats = {
            "total": len(tools),
            "registered": registered,
            "skipped": skipped,
            "errors": errors
        }
        
        logger.info(f"Batch registration: {stats}")
        return Ok(stats)
    
    def discover_from_orchestrator(
        self,
        orchestrator_name: str,
        orchestrator_instance: Any
    ) -> Result[List[MCPTool]]:
        """
        Auto-discover tools from an orchestrator instance.
        
        Args:
            orchestrator_name: Name of orchestrator
            orchestrator_instance: Orchestrator instance
            
        Returns:
            Result containing list of discovered tools
        """
        discovered: List[MCPTool] = []
        errors: List[str] = []
        
        try:
            # Check if orchestrator has get_mcp_tools method
            if not hasattr(orchestrator_instance, 'get_mcp_tools'):
                return Ok([])  # No tools to discover
            
            # Call get_mcp_tools()
            tools_result = orchestrator_instance.get_mcp_tools()
            
            # Handle both Result and direct dict returns
            if hasattr(tools_result, 'is_ok'):
                # Result type
                if tools_result.is_err():
                    errors.append(f"get_mcp_tools() returned error: {tools_result.error}")
                    return Ok([])  # Return empty list but don't fail
                tools_dict = tools_result.unwrap()
            else:
                # Direct dict return
                tools_dict = tools_result
            
            if not isinstance(tools_dict, dict):
                return Ok([])
            
            # Convert to MCPTool instances
            for tool_name, tool_info in tools_dict.items():
                try:
                    # Handle both dict and MCPTool instances
                    if isinstance(tool_info, dict):
                        tool = MCPTool(
                            name=tool_info.get('name', tool_name),
                            description=tool_info.get('description', ''),
                            category=ToolCategory(
                                tool_info.get('category', 'utility')
                            ),
                            parameters=tool_info.get('parameters', {}),
                            orchestrator_source=orchestrator_name,
                            version=tool_info.get('version', '1.0.0'),
                            discoverable=tool_info.get('discoverable', True)
                        )
                    elif isinstance(tool_info, MCPTool):
                        tool = tool_info
                        tool.orchestrator_source = orchestrator_name
                    else:
                        errors.append(f"Unknown tool format for {tool_name}: {type(tool_info)}")
                        continue
                    
                    discovered.append(tool)
                except Exception as e:
                    errors.append(f"Failed to convert {tool_name}: {str(e)}")
                    continue
            
            # Register all discovered tools
            if discovered:
                self.register_tools_batch(discovered, replace_if_exists=True)
            
            self._orchestrators_scanned.add(orchestrator_name)
            self._discovery_log.append({
                "timestamp": datetime.now().isoformat(),
                "orchestrator": orchestrator_name,
                "discovered_count": len(discovered),
                "errors": errors
            })
            
            logger.info(
                f"Discovered {len(discovered)} tools from {orchestrator_name}"
                f"{f' ({len(errors)} errors)' if errors else ''}"
            )
            
            return Ok(discovered)
            
        except Exception as e:
            logger.error(f"Discovery failed for {orchestrator_name}: {str(e)}")
            return Err(f"Discovery failed: {str(e)}")
    
    def auto_discover_from_registry(self) -> Result[Dict[str, Any]]:
        """
        Auto-discover tools from all registered orchestrators in DatabaseBackedRegistry.
        
        Returns:
            Result with discovery statistics
        """
        try:
            from cortex.orchestrators import get_database_registry
            
            registry = get_database_registry()
            all_orchestrators = registry.get_all_orchestrators()
            
            total_discovered = 0
            failed_orchestrators: List[str] = []
            
            for orch_name, orch_instance in all_orchestrators.items():
                result = self.discover_from_orchestrator(orch_name, orch_instance)
                if result.is_ok():
                    discovered = result.unwrap()
                    total_discovered += len(discovered)
                else:
                    failed_orchestrators.append(orch_name)
            
            self._last_discovery = datetime.now()
            
            stats = {
                "total_discovered": total_discovered,
                "orchestrators_scanned": len(self._orchestrators_scanned),
                "failed_orchestrators": failed_orchestrators,
                "last_discovery": self._last_discovery.isoformat()
            }
            
            logger.info(f"Auto-discovery complete: {stats}")
            return Ok(stats)
            
        except Exception as e:
            logger.error(f"Auto-discovery failed: {str(e)}")
            return Err(f"Auto-discovery failed: {str(e)}")
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def get_all_tools(self) -> Dict[str, MCPTool]:
        """Get all registered tools"""
        return dict(self._tools)
    
    def get_tools_by_category(self, category: ToolCategory) -> List[MCPTool]:
        """Get all tools in a category"""
        tool_names = self._tool_index.get(category.value, set())
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def get_discoverable_tools(self) -> List[MCPTool]:
        """Get all discoverable tools (for public APIs)"""
        return [tool for tool in self._tools.values() if tool.discoverable]
    
    def get_tool_count(self) -> int:
        """Get total tool count"""
        return len(self._tools)
    
    def get_category_counts(self) -> Dict[str, int]:
        """Get tool count by category"""
        return {
            cat.value: len(self._tool_index[cat.value])
            for cat in ToolCategory
        }
    
    def export_for_saas(self) -> Dict[str, Any]:
        """
        Export tool catalog in SaaS-ready format.
        
        Used for:
        - API gateway registration
        - Tool marketplace listing
        - Multi-repo orchestration
        """
        discoverable = self.get_discoverable_tools()
        
        return {
            "api_version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "tools": {
                tool.name: tool.to_dict()
                for tool in discoverable
            },
            "metadata": {
                "total_tools": len(discoverable),
                "categories": self.get_category_counts(),
                "orchestrators_scanned": list(self._orchestrators_scanned),
                "last_discovery": self._last_discovery.isoformat() if self._last_discovery else None
            }
        }
    
    def export_for_catalog(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Export tools organized by category for catalog/marketplace.
        """
        catalog: Dict[str, List[Dict[str, Any]]] = {}
        
        for category in ToolCategory:
            tools = self.get_tools_by_category(category)
            catalog[category.value] = [tool.to_dict() for tool in tools]
        
        return catalog


def get_unified_discovery() -> UnifiedMCPToolDiscovery:
    """Get singleton discovery instance"""
    return UnifiedMCPToolDiscovery.instance()
