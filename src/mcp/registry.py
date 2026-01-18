"""Tool Registry - Centralized tool management."""
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from src.mcp.protocol import ToolDefinition, MCPTool, ErrorCode

@dataclass
class ToolEntry:
    """Registry entry for a tool."""
    definition: ToolDefinition
    tool: MCPTool
    registered_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    execution_count: int = 0
    error_count: int = 0

class ToolRegistry:
    """Centralized registry for MCP tools."""
    
    def __init__(self):
        """Initialize registry."""
        self.tools: Dict[str, ToolEntry] = {}
        self.by_tag: Dict[str, List[str]] = {}
        self.search_index: Dict[str, List[str]] = {}
        self.listeners: List[Callable] = []
    
    def register(self, tool: MCPTool) -> bool:
        """Register a tool."""
        definition = tool.get_definition()
        
        if definition.id in self.tools:
            return False  # Already registered
        
        entry = ToolEntry(definition=definition, tool=tool)
        self.tools[definition.id] = entry
        
        # Index by tags
        for tag in definition.tags:
            if tag not in self.by_tag:
                self.by_tag[tag] = []
            self.by_tag[tag].append(definition.id)
        
        # Index by name and description for search
        self._index_for_search(definition.id, definition.name, definition.description)
        
        self._notify_listeners("tool_registered", definition.id)
        return True
    
    def unregister(self, tool_id: str) -> bool:
        """Unregister a tool."""
        if tool_id not in self.tools:
            return False
        
        entry = self.tools[tool_id]
        definition = entry.definition
        
        # Remove from tag index
        for tag in definition.tags:
            if tag in self.by_tag and tool_id in self.by_tag[tag]:
                self.by_tag[tag].remove(tool_id)
        
        # Remove from search index
        for key in list(self.search_index.keys()):
            if tool_id in self.search_index[key]:
                self.search_index[key].remove(tool_id)
        
        del self.tools[tool_id]
        self._notify_listeners("tool_unregistered", tool_id)
        return True
    
    def get_tool(self, tool_id: str) -> Optional[MCPTool]:
        """Get tool by ID."""
        entry = self.tools.get(tool_id)
        if entry:
            entry.last_used = datetime.now()
            entry.usage_count += 1
            return entry.tool
        return None
    
    def get_definition(self, tool_id: str) -> Optional[ToolDefinition]:
        """Get tool definition by ID."""
        entry = self.tools.get(tool_id)
        return entry.definition if entry else None
    
    def list_tools(self) -> List[ToolDefinition]:
        """List all registered tools."""
        return [entry.definition for entry in self.tools.values() if not entry.definition.deprecated]
    
    def find_by_tag(self, tag: str) -> List[ToolDefinition]:
        """Find tools by tag."""
        tool_ids = self.by_tag.get(tag, [])
        return [self.tools[tid].definition for tid in tool_ids if not self.tools[tid].definition.deprecated]
    
    def search(self, query: str) -> List[ToolDefinition]:
        """Search tools by name or description."""
        query_lower = query.lower()
        results = []
        
        for tool_id, entry in self.tools.items():
            if entry.definition.deprecated:
                continue
            
            # Search name and description
            if (query_lower in entry.definition.name.lower() or
                query_lower in entry.definition.description.lower()):
                results.append(entry.definition)
        
        return results
    
    def record_execution(self, tool_id: str, success: bool) -> None:
        """Record tool execution."""
        if tool_id in self.tools:
            entry = self.tools[tool_id]
            entry.execution_count += 1
            if not success:
                entry.error_count += 1
    
    def get_statistics(self, tool_id: str) -> Optional[Dict[str, any]]:
        """Get tool statistics."""
        if tool_id not in self.tools:
            return None
        
        entry = self.tools[tool_id]
        return {
            "tool_id": tool_id,
            "registered_at": entry.registered_at,
            "last_used": entry.last_used,
            "usage_count": entry.usage_count,
            "execution_count": entry.execution_count,
            "error_count": entry.error_count,
            "error_rate": entry.error_count / entry.execution_count if entry.execution_count > 0 else 0
        }
    
    def subscribe(self, listener: Callable) -> None:
        """Subscribe to registry events."""
        self.listeners.append(listener)
    
    def unsubscribe(self, listener: Callable) -> None:
        """Unsubscribe from registry events."""
        if listener in self.listeners:
            self.listeners.remove(listener)
    
    def _notify_listeners(self, event: str, tool_id: str) -> None:
        """Notify all listeners of event."""
        for listener in self.listeners:
            try:
                listener(event, tool_id)
            except Exception:
                pass
    
    def _index_for_search(self, tool_id: str, name: str, description: str) -> None:
        """Create search index entries."""
        words = (name + " " + description).lower().split()
        for word in words:
            if len(word) > 2:  # Index words > 2 chars
                if word not in self.search_index:
                    self.search_index[word] = []
                if tool_id not in self.search_index[word]:
                    self.search_index[word].append(tool_id)
