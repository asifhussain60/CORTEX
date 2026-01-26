"""
Unified MCP Tools Registry & Catalog (AC-CONSOLIDATION-002)

CANONICAL MCP TOOLS SSOT - Single Source of Truth for all MCP tool exposure.

Provides:
1. Central discovery endpoint for all CORTEX MCP tools
2. Tool validation & versioning
3. SaaS-ready exposure layer
4. Orchestrator tool aggregation
5. Tool deprecation tracking

Architecture:
- MCPToolsCatalog: Central registry (SSOT)
- Tool discovery: Orchestrators → Tools mapping
- Tool versioning: Track API compatibility
- Tool governance: Validation & deprecation
- SaaS exposure: REST endpoint for external clients

Author: Asif Hussain
AC-CONSOLIDATION: AC-CONSOLIDATION-002
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ToolStatus(Enum):
    """Tool status in lifecycle"""
    EXPERIMENTAL = "experimental"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class MCPToolMetadata:
    """Metadata for a single MCP tool"""
    name: str
    description: str
    category: str  # orchestration, governance, knowledge, utility
    version: str
    status: ToolStatus = ToolStatus.STABLE
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    return_type: str = "dict"
    exposed_by_orchestrators: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    deprecation_note: Optional[str] = None
    replacement_tool: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict (for serialization)"""
        data = asdict(self)
        data['status'] = self.status.value
        data['exposed_by_orchestrators'] = list(self.exposed_by_orchestrators)
        data['tags'] = list(self.tags)
        return data


class MCPToolsCatalog:
    """
    Central registry for all MCP tools (CORE-035 SSOT).
    
    Manages:
    - Tool registration and discovery
    - Version tracking and compatibility
    - Tool lifecycle (experimental → stable → deprecated → archived)
    - Orchestrator → tool mapping
    - SaaS exposure configuration
    """
    
    _instance: Optional['MCPToolsCatalog'] = None
    
    def __init__(self):
        """Initialize catalog (singleton)"""
        self._tools: Dict[str, MCPToolMetadata] = {}
        self._orchestrator_tools: Dict[str, List[str]] = {}  # orchestrator_name -> [tool_names]
        self._categories: Dict[str, List[str]] = {}  # category -> [tool_names]
        self._catalog_version = "1.0"
        self._last_sync = None
        self._initialized = False
        logger.info("MCPToolsCatalog initialized (AC-CONSOLIDATION-002)")
    
    @classmethod
    def instance(cls) -> 'MCPToolsCatalog':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register_tool(self, metadata: MCPToolMetadata) -> bool:
        """
        Register a new MCP tool.
        
        Args:
            metadata: Tool metadata
            
        Returns:
            True if registered, False if already exists
        """
        if metadata.name in self._tools:
            logger.warning(f"Tool already registered: {metadata.name}")
            return False
        
        self._tools[metadata.name] = metadata
        
        # Update category index
        if metadata.category not in self._categories:
            self._categories[metadata.category] = []
        self._categories[metadata.category].append(metadata.name)
        
        # Update orchestrator mapping
        for orch in metadata.exposed_by_orchestrators:
            if orch not in self._orchestrator_tools:
                self._orchestrator_tools[orch] = []
            self._orchestrator_tools[orch].append(metadata.name)
        
        logger.info(f"Tool registered: {metadata.name} v{metadata.version}")
        return True
    
    def get_tool(self, name: str) -> Optional[MCPToolMetadata]:
        """Get tool metadata by name"""
        return self._tools.get(name)
    
    def get_tools_by_category(self, category: str) -> List[MCPToolMetadata]:
        """Get all tools in a category"""
        tool_names = self._categories.get(category, [])
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def get_tools_by_orchestrator(self, orchestrator_name: str) -> List[MCPToolMetadata]:
        """Get all tools exposed by an orchestrator"""
        tool_names = self._orchestrator_tools.get(orchestrator_name, [])
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def get_stable_tools(self) -> List[MCPToolMetadata]:
        """Get all stable (non-experimental) tools"""
        return [
            tool for tool in self._tools.values()
            if tool.status in (ToolStatus.STABLE, ToolStatus.DEPRECATED)
        ]
    
    def deprecate_tool(
        self,
        tool_name: str,
        replacement: Optional[str] = None,
        note: Optional[str] = None
    ) -> bool:
        """Mark a tool as deprecated"""
        if tool_name not in self._tools:
            return False
        
        tool = self._tools[tool_name]
        tool.status = ToolStatus.DEPRECATED
        tool.replacement_tool = replacement
        tool.deprecation_note = note or f"Tool deprecated as of {datetime.now().isoformat()}"
        tool.last_updated = datetime.now().isoformat()
        
        logger.info(f"Tool deprecated: {tool_name}")
        return True
    
    def get_catalog_stats(self) -> Dict[str, Any]:
        """Get catalog statistics"""
        by_status = {}
        for tool in self._tools.values():
            status = tool.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            "total_tools": len(self._tools),
            "categories": list(self._categories.keys()),
            "tools_per_category": {
                cat: len(tools) for cat, tools in self._categories.items()
            },
            "by_status": by_status,
            "orchestrator_count": len(self._orchestrator_tools),
            "catalog_version": self._catalog_version,
            "last_sync": self._last_sync,
            "initialized": self._initialized
        }
    
    def export_catalog(self, format: str = "json") -> Dict[str, Any]:
        """
        Export full catalog for SaaS exposure.
        
        Args:
            format: Export format (json, yaml, etc)
            
        Returns:
            Catalog as dict
        """
        return {
            "version": self._catalog_version,
            "exported_at": datetime.now().isoformat(),
            "tools": {
                name: tool.to_dict()
                for name, tool in self._tools.items()
            },
            "categories": self._categories,
            "orchestrator_tools": self._orchestrator_tools,
            "stats": self.get_catalog_stats()
        }
    
    def sync_from_orchestrators(self) -> Dict[str, int]:
        """
        Sync tool definitions from all registered orchestrators.
        
        Returns:
            Statistics on sync operation
        """
        from cortex.orchestrators.core.database_registry import get_database_registry
        
        registry = get_database_registry()
        all_orchestrators = registry.get_all_orchestrators()
        
        total_tools_discovered = 0
        orchestrators_processed = 0
        
        for orch_name, orch_instance in all_orchestrators.items():
            try:
                # Get MCP tools from orchestrator
                if hasattr(orch_instance, 'get_mcp_tools'):
                    mcp_tools_result = orch_instance.get_mcp_tools()
                    
                    # Handle Result type
                    if hasattr(mcp_tools_result, 'is_ok'):
                        if mcp_tools_result.is_ok():
                            mcp_tools = mcp_tools_result.unwrap()
                        else:
                            continue
                    else:
                        mcp_tools = mcp_tools_result
                    
                    if isinstance(mcp_tools, dict):
                        for tool_name, tool_def in mcp_tools.items():
                            if not self.get_tool(tool_name):
                                metadata = MCPToolMetadata(
                                    name=tool_name,
                                    description=tool_def.get("description", ""),
                                    category=tool_def.get("category", "utility"),
                                    version=tool_def.get("version", "1.0"),
                                    status=ToolStatus(tool_def.get("status", "stable")),
                                    parameters=tool_def.get("parameters", []),
                                    exposed_by_orchestrators=[orch_name]
                                )
                                self.register_tool(metadata)
                                total_tools_discovered += 1
                            else:
                                # Update orchestrator mapping
                                tool = self.get_tool(tool_name)
                                if tool and orch_name not in tool.exposed_by_orchestrators:
                                    tool.exposed_by_orchestrators.append(orch_name)
                    
                    orchestrators_processed += 1
            except Exception as e:
                logger.warning(f"Failed to sync tools from {orch_name}: {e}")
        
        self._last_sync = datetime.now().isoformat()
        self._initialized = True
        
        logger.info(f"Sync complete: {total_tools_discovered} tools from {orchestrators_processed} orchestrators")
        
        return {
            "total_tools_discovered": total_tools_discovered,
            "orchestrators_processed": orchestrators_processed,
            "sync_time": self._last_sync
        }


def get_mcp_tools_catalog() -> MCPToolsCatalog:
    """Get singleton MCP tools catalog"""
    return MCPToolsCatalog.instance()


def sync_mcp_tools() -> Dict[str, Any]:
    """Sync MCP tools from all orchestrators into catalog"""
    catalog = get_mcp_tools_catalog()
    return catalog.sync_from_orchestrators()
