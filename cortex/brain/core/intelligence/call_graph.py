# AC-ID: IR-001-01 - AST-Based Code Intelligence - Call Graph Builder
"""
Call Graph Builder for CORTEX LENS.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-001-01 - AST-Based Code Intelligence

This module builds call graphs from parsed AST information to understand
function/method relationships and call patterns.

Part of CORTEX LENS context intelligence system.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from cortex.brain.core.intelligence.ast_intelligence import ParseResult


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class CallEdge:
    """Represents a call relationship between two nodes.
    
    Attributes:
        caller: Name of the calling function/method
        callee: Name of the called function/method
        call_type: Type of call (DIRECT, SUPER, METHOD, etc.)
        line_number: Line where call occurs
    """
    caller: str
    callee: str
    call_type: str = "DIRECT"
    line_number: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "caller": self.caller,
            "callee": self.callee,
            "call_type": self.call_type,
            "line_number": self.line_number,
        }


@dataclass
class CallGraph:
    """Represents the complete call graph for a module.
    
    Attributes:
        nodes: Set of node names (function/method identifiers)
        edges: List of call edges
        super_calls: Dict mapping method to its super().__init__ targets
    """
    nodes: Set[str] = field(default_factory=set)
    edges: List[CallEdge] = field(default_factory=list)
    super_calls: Dict[str, str] = field(default_factory=dict)
    
    @property
    def node_count(self) -> int:
        """Return number of nodes in the graph."""
        return len(self.nodes)
    
    @property
    def edge_count(self) -> int:
        """Return number of edges in the graph."""
        return len(self.edges)
    
    def has_node(self, name: str) -> bool:
        """Check if node exists in graph.
        
        Args:
            name: Node name to check
            
        Returns:
            True if node exists
        """
        return name in self.nodes
    
    def get_callers(self, callee: str) -> List[str]:
        """Get all functions that call the given function.
        
        Args:
            callee: Name of the called function
            
        Returns:
            List of caller names
        """
        return [
            edge.caller for edge in self.edges
            if edge.callee == callee
        ]
    
    def get_callees(self, caller: str) -> List[str]:
        """Get all functions called by the given function.
        
        Args:
            caller: Name of the calling function
            
        Returns:
            List of callee names
        """
        return [
            edge.callee for edge in self.edges
            if edge.caller == caller
        ]
    
    def has_super_call(self, caller: str, target: str) -> bool:
        """Check if caller has a super() call to target.
        
        Args:
            caller: Name of the method calling super()
            target: Expected target of super() call
            
        Returns:
            True if super call exists
        """
        return self.super_calls.get(caller) == target
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "nodes": list(self.nodes),
            "edges": [e.to_dict() for e in self.edges],
            "super_calls": self.super_calls,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
        }


# =============================================================================
# CALL GRAPH BUILDER
# =============================================================================


class CallGraphBuilder:
    """Builds call graphs from parsed AST information.
    
    Analyzes function and method definitions to identify call relationships
    and build a comprehensive call graph.
    
    Example:
        >>> from cortex.brain.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        >>> engine = ASTIntelligenceEngine()
        >>> result = engine.parse_file(Path("module.py"))
        >>> builder = CallGraphBuilder()
        >>> graph = builder.build(result)
        >>> callers = graph.get_callers("my_function")
    """
    
    def build(self, parse_result: "ParseResult") -> CallGraph:
        """Build call graph from parse result.
        
        Args:
            parse_result: Result from ASTIntelligenceEngine
            
        Returns:
            CallGraph containing nodes and edges
        """
        graph = CallGraph()
        
        if not parse_result.success or parse_result.ast_tree is None:
            return graph
        
        # Add nodes for all functions
        for func in parse_result.functions:
            graph.nodes.add(func.name)
        
        # Add nodes for all methods
        for cls in parse_result.classes:
            for method in cls.methods:
                node_name = f"{cls.name}.{method.name}"
                graph.nodes.add(node_name)
        
        # Build class hierarchy for super() resolution
        class_bases: Dict[str, List[str]] = {}
        for cls in parse_result.classes:
            class_bases[cls.name] = cls.bases
        
        # Extract calls from AST
        extractor = _CallExtractor(
            graph=graph,
            class_bases=class_bases,
            known_functions={f.name for f in parse_result.functions},
        )
        extractor.visit(parse_result.ast_tree)
        
        return graph


# =============================================================================
# CALL EXTRACTOR VISITOR
# =============================================================================


class _CallExtractor(ast.NodeVisitor):
    """AST visitor that extracts function/method calls."""
    
    def __init__(
        self,
        graph: CallGraph,
        class_bases: Dict[str, List[str]],
        known_functions: Set[str],
    ) -> None:
        """Initialize the call extractor.
        
        Args:
            graph: CallGraph to populate
            class_bases: Dict mapping class names to base classes
            known_functions: Set of known function names
        """
        self.graph = graph
        self.class_bases = class_bases
        self.known_functions = known_functions
        self._current_function: Optional[str] = None
        self._current_class: Optional[str] = None
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        old_class = self._current_class
        self._current_class = node.name
        self.generic_visit(node)
        self._current_class = old_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        self._process_function(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition."""
        self._process_function(node)
    
    def _process_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> None:
        """Process a function/method definition."""
        if self._current_class:
            func_name = f"{self._current_class}.{node.name}"
        else:
            func_name = node.name
        
        old_function = self._current_function
        self._current_function = func_name
        
        # Visit function body to find calls
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                self._process_call(child)
        
        self._current_function = old_function
    
    def _process_call(self, node: ast.Call) -> None:
        """Process a call expression."""
        if self._current_function is None:
            return
        
        # Handle different call types
        if isinstance(node.func, ast.Name):
            # Direct function call: func()
            callee = node.func.id
            if callee in self.known_functions or callee in self.graph.nodes:
                self.graph.edges.append(CallEdge(
                    caller=self._current_function,
                    callee=callee,
                    call_type="DIRECT",
                    line_number=node.lineno,
                ))
        
        elif isinstance(node.func, ast.Attribute):
            # Method call: obj.method() or Class.method()
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == "self":
                    # self.method() - method call on same class
                    if self._current_class:
                        callee = f"{self._current_class}.{node.func.attr}"
                        if callee in self.graph.nodes:
                            self.graph.edges.append(CallEdge(
                                caller=self._current_function,
                                callee=callee,
                                call_type="METHOD",
                                line_number=node.lineno,
                            ))
                else:
                    # Other.method() - could be class method or instance
                    potential_callee = f"{node.func.value.id}.{node.func.attr}"
                    if potential_callee in self.graph.nodes:
                        self.graph.edges.append(CallEdge(
                            caller=self._current_function,
                            callee=potential_callee,
                            call_type="METHOD",
                            line_number=node.lineno,
                        ))
            
            elif isinstance(node.func.value, ast.Call):
                # super().__init__() pattern
                if isinstance(node.func.value.func, ast.Name):
                    if node.func.value.func.id == "super":
                        self._handle_super_call(node)
    
    def _handle_super_call(self, node: ast.Call) -> None:
        """Handle super() call."""
        if self._current_class is None or self._current_function is None:
            return
        
        method_name = node.func.attr if isinstance(node.func, ast.Attribute) else "__init__"
        
        # Find base class
        bases = self.class_bases.get(self._current_class, [])
        if bases:
            base_class = bases[0]  # MRO order, first base
            target = f"{base_class}.{method_name}"
            
            # Record super call
            self.graph.super_calls[self._current_function] = target
            
            # Add edge if target exists
            if target in self.graph.nodes:
                self.graph.edges.append(CallEdge(
                    caller=self._current_function,
                    callee=target,
                    call_type="SUPER",
                    line_number=node.lineno,
                ))


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "CallGraphBuilder",
    "CallGraph",
    "CallEdge",
]
