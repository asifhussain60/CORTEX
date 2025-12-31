"""
Dependency Manager - Tool Dependency Graph Management.

Phase 4 of Toolkit Manager Implementation
Manages inter-tool dependencies with circular detection and topological sorting.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from collections import defaultdict
import logging


logger = logging.getLogger(__name__)


class CircularDependencyError(Exception):
    """Raised when circular dependencies are detected."""
    
    def __init__(self, cycle: List[str], message: str = None):
        self.cycle = cycle
        self.message = message or f"Circular dependency detected: {' -> '.join(cycle)}"
        super().__init__(self.message)


class UnmetDependencyError(Exception):
    """Raised when required dependencies are not available."""
    
    def __init__(self, tool: str, missing: List[str]):
        self.tool = tool
        self.missing = missing
        self.message = f"Tool '{tool}' has unmet dependencies: {missing}"
        super().__init__(self.message)


@dataclass
class DependencyCheck:
    """
    Result of a dependency validation check.
    
    Attributes:
        satisfied: Whether all dependencies are met
        missing: List of missing dependency names
        tool: Optional tool name this check is for
        dependencies: Optional list of all dependencies
    """
    satisfied: bool
    missing: List[str]
    tool: Optional[str] = None
    dependencies: Optional[List[str]] = None


class DependencyGraph:
    """
    Directed graph representation of tool dependencies.
    
    Uses adjacency list representation:
    - graph[tool] = list of tools it depends on
    - reverse_graph[tool] = list of tools that depend on it
    """
    
    def __init__(self):
        """Initialize empty dependency graph."""
        # tool -> [dependencies]
        self._graph: Dict[str, List[str]] = {}
        # tool -> [dependents] (reverse edges)
        self._reverse: Dict[str, List[str]] = defaultdict(list)
    
    def add_tool(self, name: str, dependencies: List[str]) -> None:
        """
        Add a tool with its dependencies to the graph.
        
        Args:
            name: Tool name
            dependencies: List of tool names this tool depends on
        """
        self._graph[name] = dependencies
        
        # Build reverse edges
        for dep in dependencies:
            self._reverse[dep].append(name)
    
    def get_dependencies(self, name: str) -> List[str]:
        """
        Get direct dependencies of a tool.
        
        Args:
            name: Tool name
            
        Returns:
            List of dependency names (empty if tool not found or has no deps)
        """
        return self._graph.get(name, [])
    
    def get_dependents(self, name: str) -> List[str]:
        """
        Get tools that depend on the given tool.
        
        Args:
            name: Tool name
            
        Returns:
            List of tool names that depend on this tool
        """
        return self._reverse.get(name, [])
    
    def has_dependencies(self, name: str) -> bool:
        """
        Check if a tool has any dependencies.
        
        Args:
            name: Tool name
            
        Returns:
            True if tool has at least one dependency
        """
        return len(self._graph.get(name, [])) > 0
    
    def get_all_tools(self) -> List[str]:
        """
        Get all tools in the graph.
        
        Returns:
            List of all tool names
        """
        return list(self._graph.keys())
    
    def __contains__(self, name: str) -> bool:
        """Check if tool is in graph."""
        return name in self._graph


class DependencyManager:
    """
    Manages inter-tool dependencies for the toolkit.
    
    Provides:
    - Dependency graph building from registry
    - Circular dependency detection
    - Topological sorting for execution order
    - Dependency validation
    
    Example:
        manager = DependencyManager(registry)
        
        # Check for circular dependencies
        cycles = manager.detect_circular()
        if cycles:
            raise CircularDependencyError(cycles[0])
        
        # Get execution order
        order = manager.get_execution_order(["reporter", "analyzer"])
        # Returns: ["core", "utils", "analyzer", "reporter"]
        
        # Validate dependencies
        check = manager.validate_dependencies("reporter")
        if not check.satisfied:
            print(f"Missing: {check.missing}")
    """
    
    def __init__(self, registry):
        """
        Initialize DependencyManager.
        
        Args:
            registry: ToolkitRegistry instance for tool lookups
        """
        self.registry = registry
        self.graph = self._build_graph()
        logger.info(f"DependencyManager initialized with {len(self.graph.get_all_tools())} tools")
    
    def _build_graph(self) -> DependencyGraph:
        """
        Build dependency graph from registry.
        
        Returns:
            Populated DependencyGraph
        """
        graph = DependencyGraph()
        
        for tool in self.registry.list_tools():
            name = tool.get("name", "")
            dependencies = tool.get("depends_on", [])
            graph.add_tool(name, dependencies)
        
        return graph
    
    def rebuild_graph(self) -> None:
        """Rebuild the dependency graph from registry."""
        self.graph = self._build_graph()
    
    def detect_circular(self) -> List[List[str]]:
        """
        Detect all circular dependencies in the graph.
        
        Uses DFS with coloring to find back edges indicating cycles.
        
        Returns:
            List of cycles, where each cycle is a list of tool names
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[str, int] = {t: WHITE for t in self.graph.get_all_tools()}
        parent: Dict[str, Optional[str]] = {t: None for t in self.graph.get_all_tools()}
        cycles: List[List[str]] = []
        
        def dfs(node: str) -> None:
            color[node] = GRAY
            
            for neighbor in self.graph.get_dependencies(node):
                if neighbor not in color:
                    # Dependency references unknown tool - skip
                    continue
                    
                if color[neighbor] == GRAY:
                    # Back edge found - cycle detected
                    cycle = self._extract_cycle(node, neighbor, parent)
                    cycles.append(cycle)
                elif color[neighbor] == WHITE:
                    parent[neighbor] = node
                    dfs(neighbor)
            
            color[node] = BLACK
        
        for tool in self.graph.get_all_tools():
            if color[tool] == WHITE:
                dfs(tool)
        
        return cycles
    
    def _extract_cycle(
        self,
        start: str,
        end: str,
        parent: Dict[str, Optional[str]]
    ) -> List[str]:
        """Extract cycle path from DFS parent pointers."""
        cycle = [end]
        current = start
        
        while current != end and current is not None:
            cycle.append(current)
            current = parent.get(current)
        
        cycle.append(end)  # Complete the cycle
        return list(reversed(cycle))
    
    def validate_dependencies(self, tool: str) -> DependencyCheck:
        """
        Validate that all dependencies of a tool are satisfied.
        
        Args:
            tool: Tool name to validate
            
        Returns:
            DependencyCheck with satisfaction status and missing deps
        """
        dependencies = self.graph.get_dependencies(tool)
        missing = []
        
        for dep in dependencies:
            if not self.registry.get_tool(dep):
                missing.append(dep)
        
        return DependencyCheck(
            satisfied=len(missing) == 0,
            missing=missing,
            tool=tool,
            dependencies=dependencies,
        )
    
    def get_execution_order(
        self,
        tools: List[str],
        strict: bool = False
    ) -> List[str]:
        """
        Get topologically sorted execution order for tools.
        
        Args:
            tools: List of tools to execute
            strict: If True, raise UnmetDependencyError for missing deps
            
        Returns:
            List of tools in execution order (dependencies first)
            
        Raises:
            CircularDependencyError: If circular dependencies exist
            UnmetDependencyError: If strict=True and dependencies missing
        """
        if not tools:
            return []
        
        # First check for circular dependencies
        cycles = self.detect_circular()
        if cycles:
            # Check if any requested tool is in a cycle
            for cycle in cycles:
                for tool in tools:
                    if tool in cycle:
                        raise CircularDependencyError(cycle)
        
        # Collect all needed tools (including transitive dependencies)
        needed: Set[str] = set()
        
        def collect_deps(tool: str, visited: Set[str]) -> None:
            if tool in visited:
                return
            visited.add(tool)
            
            for dep in self.graph.get_dependencies(tool):
                if dep in self.graph:
                    collect_deps(dep, visited)
                elif strict:
                    raise UnmetDependencyError(tool, [dep])
            
            needed.add(tool)
        
        for tool in tools:
            if tool in self.graph:
                collect_deps(tool, set())
            else:
                needed.add(tool)  # Include even if not in graph
        
        # Topological sort using Kahn's algorithm
        return self._topological_sort(list(needed))
    
    def _topological_sort(self, tools: List[str]) -> List[str]:
        """
        Perform topological sort on subset of tools.
        
        Args:
            tools: Tools to sort
            
        Returns:
            Topologically sorted list
        """
        # Build in-degree map for the subset
        in_degree: Dict[str, int] = {t: 0 for t in tools}
        tool_set = set(tools)
        
        for tool in tools:
            for dep in self.graph.get_dependencies(tool):
                if dep in tool_set:
                    in_degree[tool] += 1
        
        # Start with tools that have no dependencies in the subset
        queue = [t for t in tools if in_degree[t] == 0]
        result = []
        
        while queue:
            # Pop the tool with lowest dependencies
            tool = queue.pop(0)
            result.append(tool)
            
            # Reduce in-degree of dependents
            for dependent in self.graph.get_dependents(tool):
                if dependent in in_degree:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        
        return result
    
    def can_execute(self, tool: str) -> DependencyCheck:
        """
        Check if a tool can be executed (all dependencies satisfied).
        
        Alias for validate_dependencies for integration with ToolkitManager.
        
        Args:
            tool: Tool name
            
        Returns:
            DependencyCheck result
        """
        return self.validate_dependencies(tool)
    
    def get_all_dependencies(self, tool: str) -> List[str]:
        """
        Get all transitive dependencies of a tool.
        
        Args:
            tool: Tool name
            
        Returns:
            List of all dependencies (direct and transitive)
        """
        all_deps: Set[str] = set()
        
        def collect(t: str) -> None:
            for dep in self.graph.get_dependencies(t):
                if dep not in all_deps:
                    all_deps.add(dep)
                    collect(dep)
        
        collect(tool)
        return list(all_deps)
    
    def get_dependency_depth(self, tool: str) -> int:
        """
        Calculate the maximum dependency depth of a tool.
        
        Depth 0 = no dependencies
        Depth 1 = depends on tools with depth 0
        etc.
        
        Args:
            tool: Tool name
            
        Returns:
            Maximum dependency depth
        """
        memo: Dict[str, int] = {}
        
        def calc_depth(t: str, visited: Set[str]) -> int:
            if t in memo:
                return memo[t]
            
            if t in visited:
                return 0  # Circular - treat as 0 to avoid infinite loop
            
            visited.add(t)
            deps = self.graph.get_dependencies(t)
            
            if not deps:
                memo[t] = 0
                return 0
            
            max_dep_depth = max(
                calc_depth(d, visited) for d in deps if d in self.graph
            ) if deps else -1
            
            memo[t] = max_dep_depth + 1
            return memo[t]
        
        return calc_depth(tool, set())
    
    def get_dependency_tree(self, tool: str) -> Dict[str, Any]:
        """
        Get a tree representation of dependencies.
        
        Args:
            tool: Tool name
            
        Returns:
            Nested dict representing dependency tree
        """
        visited: Set[str] = set()
        
        def build_tree(t: str) -> Dict[str, Any]:
            if t in visited:
                return {t: {"circular_ref": True}}
            
            visited.add(t)
            deps = self.graph.get_dependencies(t)
            
            if not deps:
                return {t: {}}
            
            children = {}
            for dep in deps:
                if dep in self.graph:
                    children.update(build_tree(dep))
                else:
                    children[dep] = {"missing": True}
            
            visited.discard(t)
            return {t: children}
        
        return build_tree(tool)
