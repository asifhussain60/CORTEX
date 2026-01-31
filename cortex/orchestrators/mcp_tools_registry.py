"""
MCP Tools Registry - Centralized catalog of all 15 MCP tools

AC-MCP-EXPOSURE-001: Central registry for model context protocol tools
- Catalogs all 15 available MCP tools
- Organizes tools by category (governance, orchestration, knowledge, utility)
- Provides discovery and validation methods
- Enables dynamic tool exposure through orchestrators

Total Tools: 15 (5 governance, 4 orchestration, 3 knowledge, 3 utility)

Author: GitHub Copilot
Date: 2026-01-24
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from cortex.mcp.tool_governance import ToolCategory


@dataclass
class ToolMetadata:
    """Metadata for an MCP tool"""
    name: str
    category: ToolCategory
    description: str
    parameters: Dict[str, str]
    authorization: str = "AUTHENTICATED"
    compliance: str = "NORMAL"
    location: str = ""


class MCPToolsRegistry:
    """Central registry for all 15 MCP tools.
    
    Provides unified access to tool definitions, categories, and metadata.
    Used by orchestrators to expose tools and by MCPServer to discover tools.
    """
    
    # Governance Tools (5)
    GOVERNANCE_TOOLS = {
        "query_governance_context": ToolMetadata(
            name="query_governance_context",
            category=ToolCategory.GOVERNANCE,
            description="Query execution context for governance rules",
            parameters={"operation_id": "string", "context_type": "string"},
            location="cortex/mcp/tools/governance/__init__.py",
        ),
        "validate_governance_compliance": ToolMetadata(
            name="validate_governance_compliance",
            category=ToolCategory.GOVERNANCE,
            description="Validate operation against governance rules",
            parameters={"operation": "dict", "ruleset": "string"},
            location="cortex/mcp/tools/governance/__init__.py",
        ),
        "execute_governance_check": ToolMetadata(
            name="execute_governance_check",
            category=ToolCategory.GOVERNANCE,
            description="Execute comprehensive governance check on operation",
            parameters={"operation": "dict", "check_type": "string"},
            location="cortex/mcp/tools/governance/__init__.py",
        ),
        "analyze_governance_impact": ToolMetadata(
            name="analyze_governance_impact",
            category=ToolCategory.GOVERNANCE,
            description="Analyze governance impact of proposed operation",
            parameters={"operation": "dict", "scope": "string"},
            location="cortex/mcp/tools/governance/__init__.py",
        ),
        "report_governance_status": ToolMetadata(
            name="report_governance_status",
            category=ToolCategory.GOVERNANCE,
            description="Generate governance status report",
            parameters={"scope": "string", "time_range": "string"},
            location="cortex/mcp/tools/governance/__init__.py",
        ),
    }
    
    # Orchestration Tools (4)
    ORCHESTRATION_TOOLS = {
        "get_operation_status": ToolMetadata(
            name="get_operation_status",
            category=ToolCategory.ORCHESTRATION,
            description="Get status of ongoing operation",
            parameters={"operation_id": "string"},
            location="cortex/mcp/tools/orchestration/__init__.py",
        ),
        "monitor_orchestrator_health": ToolMetadata(
            name="monitor_orchestrator_health",
            category=ToolCategory.ORCHESTRATION,
            description="Monitor orchestrator health and metrics",
            parameters={"orchestrator_id": "string"},
            location="cortex/mcp/tools/orchestration/__init__.py",
        ),
        "optimize_orchestrator_config": ToolMetadata(
            name="optimize_orchestrator_config",
            category=ToolCategory.ORCHESTRATION,
            description="Optimize orchestrator configuration based on metrics",
            parameters={"orchestrator_id": "string", "optimization_type": "string"},
            location="cortex/mcp/tools/orchestration/__init__.py",
        ),
        "diagnose_orchestrator_issues": ToolMetadata(
            name="diagnose_orchestrator_issues",
            category=ToolCategory.ORCHESTRATION,
            description="Diagnose issues in orchestrator operation",
            parameters={"orchestrator_id": "string"},
            location="cortex/mcp/tools/orchestration/__init__.py",
        ),
    }
    
    # Knowledge Tools (3)
    KNOWLEDGE_TOOLS = {
        "search_knowledge_base": ToolMetadata(
            name="search_knowledge_base",
            category=ToolCategory.KNOWLEDGE,
            description="Search knowledge base for relevant information",
            parameters={"query": "string", "domain": "string"},
            location="cortex/mcp/tools/knowledge/__init__.py",
        ),
        "analyze_knowledge_gap": ToolMetadata(
            name="analyze_knowledge_gap",
            category=ToolCategory.KNOWLEDGE,
            description="Analyze gaps in knowledge coverage",
            parameters={"domain": "string", "scope": "string"},
            location="cortex/mcp/tools/knowledge/__init__.py",
        ),
        "generate_knowledge_summary": ToolMetadata(
            name="generate_knowledge_summary",
            category=ToolCategory.KNOWLEDGE,
            description="Generate knowledge summary for a domain",
            parameters={"domain": "string", "detail_level": "string"},
            location="cortex/mcp/tools/knowledge/__init__.py",
        ),
    }
    
    # Utility Tools (3)
    UTILITY_TOOLS = {
        "echo_tool": ToolMetadata(
            name="echo_tool",
            category=ToolCategory.UTILITY,
            description="Echo tool for testing MCP connectivity",
            parameters={"message": "string"},
            authorization="PUBLIC",
            location="cortex/mcp/tools/utility/__init__.py",
        ),
        "sample_tool": ToolMetadata(
            name="sample_tool",
            category=ToolCategory.UTILITY,
            description="Sample tool demonstrating basic MCP functionality",
            parameters={"input": "dict"},
            authorization="PUBLIC",
            location="cortex/mcp/tools/utility/__init__.py",
        ),
        "transform_tool": ToolMetadata(
            name="transform_tool",
            category=ToolCategory.UTILITY,
            description="Transform data using specified transformation",
            parameters={"data": "dict", "transformation": "string"},
            authorization="PUBLIC",
            location="cortex/mcp/tools/utility/__init__.py",
        ),
    }
    
    @classmethod
    def get_all_tools(cls) -> Dict[str, Dict[str, ToolMetadata]]:
        """Get all 15 tools organized by category.
        
        Returns:
            Dict mapping category names to tool metadata dicts
        """
        return {
            "governance": cls.GOVERNANCE_TOOLS,
            "orchestration": cls.ORCHESTRATION_TOOLS,
            "knowledge": cls.KNOWLEDGE_TOOLS,
            "utility": cls.UTILITY_TOOLS,
        }
    
    @classmethod
    def get_tool_names(cls) -> Dict[str, List[str]]:
        """Get tool names organized by category.
        
        Returns:
            Dict mapping category names to lists of tool names
        """
        return {
            "governance": list(cls.GOVERNANCE_TOOLS.keys()),
            "orchestration": list(cls.ORCHESTRATION_TOOLS.keys()),
            "knowledge": list(cls.KNOWLEDGE_TOOLS.keys()),
            "utility": list(cls.UTILITY_TOOLS.keys()),
        }
    
    @classmethod
    def get_tool(cls, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool by name.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            ToolMetadata if found, None otherwise
        """
        all_tools = cls.get_all_tools()
        for category_tools in all_tools.values():
            if tool_name in category_tools:
                return category_tools[tool_name]
        return None
    
    @classmethod
    def get_tools_by_category(cls, category: str) -> Dict[str, ToolMetadata]:
        """Get all tools in a specific category.
        
        Args:
            category: Category name ('governance', 'orchestration', 'knowledge', 'utility')
            
        Returns:
            Dict of tool metadata in that category
        """
        all_tools = cls.get_all_tools()
        return all_tools.get(category, {})
    
    @classmethod
    def get_tool_count(cls) -> int:
        """Get total number of tools.
        
        Returns:
            Total count (should be 15)
        """
        all_tools = cls.get_all_tools()
        return sum(len(tools) for tools in all_tools.values())
    
    @classmethod
    def validate_registry(cls) -> Dict[str, Any]:
        """Validate registry consistency.
        
        Checks:
        - Total tool count == 15
        - No duplicate tool names
        - All tools have required metadata
        - Tool categories are correct
        
        Returns:
            Dict with validation results
        """
        all_tools = cls.get_all_tools()
        
        # Check total count
        total = cls.get_tool_count()
        if total != 15:
            return {
                "valid": False,
                "error": f"Expected 15 tools, found {total}",
                "total": total,
            }
        
        # Check for duplicates
        seen = set()
        for category_tools in all_tools.values():
            for tool_name in category_tools.keys():
                if tool_name in seen:
                    return {
                        "valid": False,
                        "error": f"Duplicate tool name: {tool_name}",
                        "total": total,
                    }
                seen.add(tool_name)
        
        # Check category counts
        counts = {
            "governance": len(cls.GOVERNANCE_TOOLS),
            "orchestration": len(cls.ORCHESTRATION_TOOLS),
            "knowledge": len(cls.KNOWLEDGE_TOOLS),
            "utility": len(cls.UTILITY_TOOLS),
        }
        
        expected_counts = {
            "governance": 5,
            "orchestration": 4,
            "knowledge": 3,
            "utility": 3,
        }
        
        for category, expected in expected_counts.items():
            if counts.get(category, 0) != expected:
                return {
                    "valid": False,
                    "error": f"Category '{category}' has {counts.get(category, 0)} tools, expected {expected}",
                    "counts": counts,
                }
        
        return {
            "valid": True,
            "message": "Registry validation passed",
            "total_tools": total,
            "category_counts": counts,
        }
    
    @classmethod
    def export_for_discovery(cls) -> Dict[str, Any]:
        """Export registry in format suitable for tool discovery.
        
        Returns:
            Dict with all tool definitions for MCPServer
        """
        all_tools = cls.get_all_tools()
        
        tools_list = []
        for category, tools in all_tools.items():
            for tool_name, metadata in tools.items():
                tools_list.append({
                    "name": metadata.name,
                    "category": metadata.category.value,
                    "description": metadata.description,
                    "parameters": metadata.parameters,
                    "authorization": metadata.authorization,
                    "compliance": metadata.compliance,
                    "location": metadata.location,
                })
        
        return {
            "status": "ok",
            "total_tools": len(tools_list),
            "tools": tools_list,
            "categories": list(all_tools.keys()),
        }


__all__ = ["MCPToolsRegistry", "ToolCategory", "ToolMetadata"]
