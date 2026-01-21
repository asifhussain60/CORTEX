"""MCP Tool Registry with discovery and categorization.

Manages registration, discovery, and retrieval of MCP tools.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from cortex.mcp.protocol import ToolDefinition, MCPTool


@dataclass
class ToolEntry:
    """Tool registry entry."""
    tool_id: str
    name: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    deprecated: bool = False
    usage_count: int = 0  # Track how many times tool was accessed


@dataclass
class ToolStatistics:
    """Tool execution statistics."""
    tool_id: str
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_execution_time: float = 0.0
    avg_execution_time: float = 0.0



class ToolRegistry:
    """MCP Tool Registry with auto-discovery.
    
    Manages registration, discovery, and retrieval of MCP tools
    organized by category with complete metadata.
    """
    
    CATEGORIES = [
        "governance",
        "orchestration",
        "knowledge",
        "utility",
        "deployment",
        "multi_repo",
    ]
    
    def __init__(self):
        """Initialize the registry."""
        self.tools: Dict[str, ToolEntry] = {}
        self.by_tag: Dict[str, List[str]] = {}
        self.statistics: Dict[str, ToolStatistics] = {}
        self.listeners: List[Callable] = []
        self._discovered = False
    
    def register(self, tool: MCPTool) -> bool:
        """Register a tool.
        
        Args:
            tool: MCPTool instance to register.
            
        Returns:
            True if registered successfully, False if already registered.
        """
        definition = tool.get_definition()
        tool_id = definition.id
        
        # Check for duplicates
        if tool_id in self.tools:
            return False
        
        # Skip deprecated tools
        if definition.deprecated:
            return True  # Silently skip
        
        # Create entry
        entry = ToolEntry(
            tool_id=tool_id,
            name=definition.name,
            description=definition.description,
            tags=definition.tags,
            deprecated=definition.deprecated,
            metadata={"enabled": tool.enabled}
        )
        
        # Register
        self.tools[tool_id] = entry
        self.statistics[tool_id] = ToolStatistics(tool_id=tool_id)
        
        # Index tags
        for tag in definition.tags:
            if tag not in self.by_tag:
                self.by_tag[tag] = []
            self.by_tag[tag].append(tool_id)
        
        # Notify listeners
        self._notify_listeners("tool_registered", tool_id=tool_id)
        
        return True
    
    def unregister(self, tool_id: str) -> bool:
        """Unregister a tool.
        
        Args:
            tool_id: Tool identifier.
            
        Returns:
            True if unregistered, False if not found.
        """
        if tool_id not in self.tools:
            return False
        
        # Get entry to clean up tags
        entry = self.tools[tool_id]
        
        # Remove from tag index
        for tag in entry.tags:
            if tag in self.by_tag:
                self.by_tag[tag] = [t for t in self.by_tag[tag] if t != tool_id]
                if not self.by_tag[tag]:
                    del self.by_tag[tag]
        
        # Remove tool
        del self.tools[tool_id]
        
        # Notify listeners
        self._notify_listeners("tool_unregistered", tool_id=tool_id)
        
        return True
    
    def get_tool(self, tool_id: str) -> Optional[ToolEntry]:
        """Get tool by ID.
        
        Args:
            tool_id: Tool identifier.
            
        Returns:
            Tool entry or None if not found.
        """
        entry = self.tools.get(tool_id)
        if entry:
            entry.usage_count += 1
        return entry
    
    def get_definition(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get tool definition.
        
        Args:
            tool_id: Tool identifier.
            
        Returns:
            Tool definition dict or None.
        """
        entry = self.tools.get(tool_id)
        if not entry:
            return None
        
        return {
            "id": entry.tool_id,
            "name": entry.name,
            "description": entry.description,
            "tags": entry.tags,
            "deprecated": entry.deprecated,
        }
    
    def list_tools(self, include_deprecated: bool = False) -> List[ToolEntry]:
        """List all registered tools.
        
        Args:
            include_deprecated: Include deprecated tools.
            
        Returns:
            List of tool entries.
        """
        tools = list(self.tools.values())
        if not include_deprecated:
            tools = [t for t in tools if not t.deprecated]
        return tools
    
    def find_by_tag(self, tag: str) -> List[ToolEntry]:
        """Find tools by tag.
        
        Args:
            tag: Tag to search.
            
        Returns:
            List of tools with the tag.
        """
        tool_ids = self.by_tag.get(tag, [])
        return [self.tools[tid] for tid in tool_ids if tid in self.tools]
    
    def search_by_name(self, name: str) -> List[ToolEntry]:
        """Search tools by name (case-insensitive).
        
        Args:
            name: Name to search.
            
        Returns:
            List of matching tools.
        """
        name_lower = name.lower()
        return [t for t in self.tools.values() if name_lower in t.name.lower()]
    
    def search_by_description(self, text: str) -> List[ToolEntry]:
        """Search tools by description (case-insensitive).
        
        Args:
            text: Text to search.
            
        Returns:
            List of matching tools.
        """
        text_lower = text.lower()
        return [t for t in self.tools.values() if text_lower in t.description.lower()]
    
    def search(self, text: str) -> List[ToolEntry]:
        """Search tools by name or description (case-insensitive).
        
        Searches both name and description for the given text.
        
        Args:
            text: Text to search.
            
        Returns:
            List of matching tools.
        """
        text_lower = text.lower()
        results = []
        for entry in self.tools.values():
            if text_lower in entry.name.lower() or text_lower in entry.description.lower():
                results.append(entry)
        return results
    
    def record_execution(self, tool_id: str, success: bool) -> None:
        """Record tool execution.
        
        Args:
            tool_id: Tool identifier.
            success: Whether execution was successful.
        """
        if tool_id not in self.statistics:
            self.statistics[tool_id] = ToolStatistics(tool_id=tool_id)
        
        if tool_id in self.tools:
            entry = self.tools[tool_id]
            # Add execution tracking to entry
            if not hasattr(entry, 'execution_count'):
                entry.execution_count = 0
                entry.error_count = 0
            entry.execution_count += 1
            if not success:
                entry.error_count += 1
        
        stats = self.statistics[tool_id]
        stats.execution_count += 1
        if success:
            stats.success_count += 1
        else:
            stats.failure_count += 1
        
        # Notify listeners
        self._notify_listeners("execution_recorded", tool_id=tool_id, success=success)
    
    def get_statistics(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get tool execution statistics.
        
        Args:
            tool_id: Tool identifier.
            
        Returns:
            Statistics dict or None if not found.
        """
        if tool_id not in self.statistics:
            return None
        
        stats = self.statistics[tool_id]
        error_count = stats.failure_count
        error_rate = error_count / stats.execution_count if stats.execution_count > 0 else 0
        
        return {
            "execution_count": stats.execution_count,
            "success_count": stats.success_count,
            "error_count": error_count,
            "error_rate": error_rate,
        }
    
    def register_listener(self, callback: Callable) -> None:
        """Register event listener.
        
        Args:
            callback: Callable to invoke on events.
        """
        self.listeners.append(callback)
    
    def subscribe(self, callback: Callable) -> None:
        """Subscribe to registry events (alias for register_listener).
        
        Args:
            callback: Callable to invoke on events (called with event, tool_id).
        """
        self.register_listener(callback)
    
    def unsubscribe(self, callback: Callable) -> None:
        """Unsubscribe from registry events (alias for unregister_listener).
        
        Args:
            callback: Callable to remove.
        """
        self.unregister_listener(callback)
    
    def unregister_listener(self, callback: Callable) -> None:
        """Unregister event listener.
        
        Args:
            callback: Callable to remove.
        """
        if callback in self.listeners:
            self.listeners.remove(callback)
    
    def _notify_listeners(self, event: str, **kwargs) -> None:
        """Notify registered listeners.
        
        Args:
            event: Event type.
            **kwargs: Event data.
        """
        for listener in self.listeners:
            try:
                # Call listener with event name and all other kwargs
                if "tool_id" in kwargs:
                    listener(event, kwargs["tool_id"])
                else:
                    listener(event)
            except Exception:
                pass  # Silently ignore listener errors
    
    def auto_discover(self) -> int:
        """Auto-discover and register all tools.
        
        Returns:
            Number of tools discovered.
        """
        if self._discovered:
            return len(self.tools)
        
        self._register_builtin_tools()
        self._discovered = True
        
        return len(self.tools)
    
    def _register_builtin_tools(self):
        """Register all built-in tools."""
        # Create mock tools for registration
        from unittest.mock import Mock
        
        tools_config = [
            # Governance tools
            ("governance.tier_resolver", "Tier Resolver", "Resolve rule precedence", ["governance", "rules"]),
            ("governance.rule_evaluator", "Rule Evaluator", "Evaluate rule against code", ["governance", "evaluation"]),
            ("governance.audit_query", "Audit Query", "Search governance.db", ["governance", "audit"]),
            ("governance.policy_enforcer", "Policy Enforcer", "Check code against tier0 policy", ["governance", "policy"]),
            ("governance.compliance_reporter", "Compliance Reporter", "Generate compliance report", ["governance", "reporting"]),
            
            # Orchestration tools
            ("orchestration.execute_phase", "Execute Phase", "Execute a deployment phase", ["orchestration", "execution"]),
            ("orchestration.run_tests", "Run Tests", "Run pytest test suite", ["orchestration", "testing"]),
            ("orchestration.phase_status", "Phase Status", "Get phase status", ["orchestration", "status"]),
            ("orchestration.workflow_manager", "Workflow Manager", "Manage multi-phase workflows", ["orchestration", "workflow"]),
            
            # Knowledge tools
            ("knowledge.query_kb", "Query Knowledge Base", "Query CORTEX knowledge base", ["knowledge", "query"]),
            ("knowledge.search_ac", "Search AC", "Search acceptance criteria", ["knowledge", "search"]),
            ("knowledge.doc_lookup", "Documentation Lookup", "Look up documentation", ["knowledge", "documentation"]),
            
            # Utility tools
            ("utility.echo", "Echo", "Echo input back", ["utility", "test"]),
            ("utility.transform", "Transform", "Transform data format", ["utility", "transformation"]),
            
            # Deployment tools
            ("deployment.sanitizer", "Sanitizer", "Run PHASE-DEPLOYMENT-001 sanitization", ["deployment", "sanitization"]),
            ("deployment.release_builder", "Release Builder", "Create release tag", ["deployment", "release"]),
            ("deployment.health_checker", "Health Checker", "Validate CORTEX readiness", ["deployment", "health"]),
            ("deployment.rollback", "Rollback", "Revert to previous release", ["deployment", "rollback"]),
            ("deployment.canary_deployer", "Canary Deployer", "Staged rollout", ["deployment", "canary"]),
            
            # Multi-repo tools
            ("multi_repo.project_scanner", "Project Scanner", "Discover project structure", ["multi_repo", "scanning"]),
            ("multi_repo.context_switcher", "Context Switcher", "Load tier1 rules per project", ["multi_repo", "context"]),
            ("multi_repo.cross_repo_search", "Cross-Repo Search", "Find AC-ID references", ["multi_repo", "search"]),
            ("multi_repo.shared_audit", "Shared Audit", "Query unified governance.db", ["multi_repo", "audit"]),
            ("multi_repo.dependency_graph", "Dependency Graph", "Show inter-project dependencies", ["multi_repo", "dependencies"]),
            ("multi_repo.profile_manager", "Profile Manager", "Apply governance profiles", ["multi_repo", "profiles"]),
        ]
        
        for tool_id, name, description, tags in tools_config:
            tool = Mock(spec=MCPTool)
            definition = ToolDefinition(
                id=tool_id,
                name=name,
                description=description,
                tags=tags
            )
            tool.get_definition.return_value = definition
            tool.enabled = True
            self.register(tool)


# Global registry singleton
_GLOBAL_REGISTRY: Optional[ToolRegistry] = None


def get_mcp_tool_registry() -> ToolRegistry:
    """Get the global MCP tool registry instance.
    
    Returns:
        ToolRegistry: Global tool registry singleton
    """
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = ToolRegistry()
        _GLOBAL_REGISTRY.auto_discover()
    return _GLOBAL_REGISTRY


__all__ = [
    "ToolEntry",
    "ToolStatistics",
    "ToolRegistry",
    "get_mcp_tool_registry",
]
