"""MCP Tool Discovery - Auto-discovery and registration of MCP tools.

Provides tool discovery mechanism that automatically finds, categorizes,
and registers all MCP tools in the framework. Scans tool modules and
populates the registry.

Author: CORTEX Framework
"""

import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import logging

from cortex.brain.tier1.orchestrators.cleaners.registry import get_mcp_tool_registry
from cortex.mcp.tool_governance import (
    ToolCategory,
    AuthLevel,
    ComplianceMode,
    ToolGovernancePolicy,
    get_governance_manager,
)

logger = logging.getLogger(__name__)


class ToolDiscoveryEngine:
    """Auto-discovers and registers MCP tools.
    
    Scans tool modules by category and populates the tool registry
    and governance manager with discovered tools.
    """
    
    # Tool categories and their modules
    TOOL_MODULES = {
        ToolCategory.GOVERNANCE: "cortex.brain.mcp.tools.governance_tools",
        ToolCategory.ORCHESTRATION: "cortex.brain.mcp.tools.orchestrator_tools",
        ToolCategory.KNOWLEDGE: "cortex.brain.mcp.tools.knowledge_tools",
        ToolCategory.UTILITY: "cortex.brain.mcp.tools.utility_tools",
        # Phase 8.2-8.4: Security analysis tools
        "security": "cortex.mcp.tools.security",  # New security tools category
    }
    
    # Default authorization levels by category
    DEFAULT_AUTH_LEVELS = {
        ToolCategory.GOVERNANCE: AuthLevel.PRIVILEGED,
        ToolCategory.ORCHESTRATION: AuthLevel.AUTHENTICATED,
        ToolCategory.KNOWLEDGE: AuthLevel.AUTHENTICATED,
        ToolCategory.UTILITY: AuthLevel.PUBLIC,
        "security": AuthLevel.AUTHENTICATED,  # Security tools require authentication
    }
    
    # Default compliance modes by category
    DEFAULT_COMPLIANCE_MODES = {
        ToolCategory.GOVERNANCE: ComplianceMode.STRICT,
        ToolCategory.ORCHESTRATION: ComplianceMode.NORMAL,
        ToolCategory.KNOWLEDGE: ComplianceMode.NORMAL,
        ToolCategory.UTILITY: ComplianceMode.LIGHTWEIGHT,
        "security": ComplianceMode.STRICT,  # Security tools require strict compliance
    }
    
    def __init__(self):
        """Initialize tool discovery engine."""
        self.registry = get_mcp_tool_registry()
        self.governance = get_governance_manager()
        self.discovered_tools: Dict[str, Dict[str, Any]] = {}
    
    def discover_tools(self) -> Dict[str, Dict[str, Any]]:
        """Discover all MCP tools.
        
        Returns:
            Dict of discovered tools by category
        """
        self.discovered_tools = {}
        
        for category, module_name in self.TOOL_MODULES.items():
            try:
                module = importlib.import_module(module_name)
                tools = self._extract_tools_from_module(module, category)
                self.discovered_tools[category.value] = tools
                logger.info(f"Discovered {len(tools)} {category.value} tools")
            except (ImportError, ModuleNotFoundError) as e:
                logger.warning(f"Could not import {module_name}: {e}")
        
        return self.discovered_tools
    
    def _extract_tools_from_module(self, module: Any, category: ToolCategory) -> Dict[str, Callable]:
        """Extract tool functions from a module.
        
        Args:
            module: Module to scan
            category: Tool category
            
        Returns:
            Dict of tool functions
        """
        tools = {}
        
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and hasattr(obj, "_mcp_tool_metadata"):
                tool_id = obj._mcp_tool_metadata.get("name", name)
                tools[tool_id] = {
                    "function": obj,
                    "metadata": obj._mcp_tool_metadata,
                    "category": category,
                }
        
        return tools
    
    def register_discovered_tools(self) -> int:
        """Register all discovered tools.
        
        Returns:
            Number of tools registered
        """
        count = 0
        
        for category_str, tools in self.discovered_tools.items():
            category = ToolCategory(category_str)
            
            for tool_id, tool_info in tools.items():
                try:
                    self._register_tool(tool_id, tool_info, category)
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to register tool {tool_id}: {e}")
        
        return count
    
    def _register_tool(
        self,
        tool_id: str,
        tool_info: Dict[str, Any],
        category: ToolCategory,
    ) -> None:
        """Register a single tool.
        
        Args:
            tool_id: Tool identifier
            tool_info: Tool metadata and function
            category: Tool category
        """
        # Register in tool registry
        self.registry.register_tool(
            tool_id=tool_id,
            tool_name=tool_info["metadata"].get("description", tool_id),
            description=tool_info["metadata"].get("description", ""),
            category=category,
            parameters=tool_info["metadata"].get("parameters", {}),
            metadata={
                "category": category.value,
                "function": tool_info["function"].__name__,
                "module": tool_info["function"].__module__,
            },
        )
        
        # Register governance policy
        policy = ToolGovernancePolicy(
            tool_id=tool_id,
            tool_name=tool_id,
            category=category,
            auth_level=self.DEFAULT_AUTH_LEVELS.get(category, AuthLevel.AUTHENTICATED),
            compliance_mode=self.DEFAULT_COMPLIANCE_MODES.get(category, ComplianceMode.NORMAL),
            description=tool_info["metadata"].get("description", ""),
        )
        self.governance.register_policy(policy)
    
    def print_discovery_summary(self) -> None:
        """Print discovery summary."""
        total_tools = sum(len(tools) for tools in self.discovered_tools.values())
        
        print(f"\n{'='*60}")
        print(f"MCP Tool Discovery Summary")
        print(f"{'='*60}")
        print(f"Total tools discovered: {total_tools}\n")
        
        for category_str, tools in self.discovered_tools.items():
            print(f"{category_str.upper()} ({len(tools)} tools):")
            for tool_id in sorted(tools.keys()):
                print(f"  - {tool_id}")
            print()


def auto_discover_and_register_tools() -> int:
    """Auto-discover and register all MCP tools.
    
    Returns:
        Number of tools registered
    """
    engine = ToolDiscoveryEngine()
    engine.discover_tools()
    count = engine.register_discovered_tools()
    logger.info(f"Auto-registered {count} MCP tools")
    return count


__all__ = [
    "ToolDiscoveryEngine",
    "auto_discover_and_register_tools",
]
