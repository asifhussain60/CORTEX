"""LENS Context Builder

Provides context aggregation for the LENS protocol, combining AST findings,
Git history, and other intelligence sources into a unified context.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, List, Optional


@dataclass
class LENSContext:
    """LENS context for intent routing."""
    intent: str
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    ast_findings: Optional[Dict[str, Any]] = None
    git_findings: Optional[Dict[str, Any]] = None
    test_findings: Optional[Dict[str, Any]] = None
    dependency_findings: Optional[Dict[str, Any]] = None
    comment_findings: Optional[Dict[str, Any]] = None
    relationship_findings: Optional[Dict[str, Any]] = None
    knowledge_graph: Optional["KnowledgeGraph"] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    computed_data: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary.
        
        Returns:
            Dictionary representation of the context.
        """
        result = {
            "intent": self.intent,
            "context": self.context,
            "confidence": self.confidence,
            "ast_findings": self.ast_findings,
            "git_findings": self.git_findings,
            "test_findings": self.test_findings,
            "dependency_findings": self.dependency_findings,
            "comment_findings": self.comment_findings,
            "relationship_findings": self.relationship_findings,
            "metadata": self.metadata,
            "computed_data": self.computed_data,
            "timestamp": self.timestamp,
        }
        
        # Handle knowledge_graph separately (it's an object)
        if self.knowledge_graph:
            result["knowledge_graph"] = {
                "nodes": [{"id": n.id, "type": n.node_type, "name": n.name} for n in self.knowledge_graph.nodes],
                "edges": [{"source": e.source, "target": e.target, "type": e.edge_type} for e in self.knowledge_graph.edges]
            }
        else:
            result["knowledge_graph"] = None
        
        return result
    
    def to_json(self) -> str:
        """Convert context to JSON string.
        
        Returns:
            JSON string representation.
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LENSContext":
        """Create LENSContext from dictionary.
        
        Args:
            data: Dictionary with context data
            
        Returns:
            LENSContext instance
        """
        # Remove knowledge_graph from data as it needs special handling
        kg_data = data.pop("knowledge_graph", None)
        context = cls(**data)
        
        # Reconstruct knowledge_graph if present
        if kg_data and kg_data.get("nodes"):
            nodes = [ContextNode(id=n["id"], node_type=n["type"], name=n["name"]) for n in kg_data["nodes"]]
            edges = [ContextEdge(source=e["source"], target=e["target"], edge_type=e["type"]) for e in kg_data.get("edges", [])]
            context.knowledge_graph = KnowledgeGraph(nodes=nodes, edges=edges)
        
        return context
    
    @classmethod
    def from_json(cls, json_str: str) -> "LENSContext":
        """Create LENSContext from JSON string.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            LENSContext instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class ContextNode:
    """Node in LENS context tree."""
    id: str
    node_type: str
    name: str
    file: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: list = field(default_factory=list)


@dataclass
class ContextEdge:
    """Edge connecting context nodes."""
    source: str
    target: str
    edge_type: str = "relates_to"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeGraph:
    """Knowledge graph for LENS context."""
    nodes: Dict[str, ContextNode] = field(default_factory=dict)
    edges: List[ContextEdge] = field(default_factory=list)
    
    def add_node(self, node: ContextNode) -> None:
        """Add node to knowledge graph.
        
        Args:
            node: ContextNode to add
        """
        self.nodes[node.id] = node
    
    def add_edge(self, edge: ContextEdge) -> None:
        """Add edge to knowledge graph.
        
        Args:
            edge: ContextEdge to add
        """
        self.edges.append(edge)
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get neighbor nodes connected to given node.
        
        Args:
            node_id: ID of node to find neighbors for
            
        Returns:
            List of neighbor node IDs
        """
        neighbors = []
        for edge in self.edges:
            if edge.source == node_id:
                neighbors.append(edge.target)
            elif edge.target == node_id:
                neighbors.append(edge.source)
        return neighbors


class LENSContextBuilder:
    """Build LENS context from multiple intelligence sources.
    
    Aggregates findings from AST analysis, Git history, test coverage,
    and dependency analysis into a unified context for intent reflection.
    """
    
    def __init__(self) -> None:
        """Initialize context builder with empty findings."""
        self._ast_findings: Optional[Dict[str, Any]] = None
        self._git_findings: Optional[Dict[str, Any]] = None
        self._test_findings: Optional[Dict[str, Any]] = None
        self._dependency_findings: Optional[Dict[str, Any]] = None
        self._comment_findings: Optional[Dict[str, Any]] = None
        self._relationship_findings: Optional[Dict[str, Any]] = None
        self._intent: str = ""
        self._context: Dict[str, Any] = {}
        self._metadata: Dict[str, Any] = {}
    
    @property
    def ast_findings(self) -> Optional[Dict[str, Any]]:
        """Get AST findings."""
        return self._ast_findings
    
    @property
    def git_findings(self) -> Optional[Dict[str, Any]]:
        """Get Git findings."""
        return self._git_findings
    
    @property
    def test_findings(self) -> Optional[Dict[str, Any]]:
        """Get test findings."""
        return self._test_findings
    
    @property
    def dependency_findings(self) -> Optional[Dict[str, Any]]:
        """Get dependency findings."""
        return self._dependency_findings
    
    @property
    def comment_findings(self) -> Optional[Dict[str, Any]]:
        """Get comment findings."""
        return self._comment_findings
    
    @property
    def relationship_findings(self) -> Optional[Dict[str, Any]]:
        """Get relationship findings."""
        return self._relationship_findings
    
    def add_ast_findings(self, findings: Dict[str, Any]) -> "LENSContextBuilder":
        """Add AST analysis findings to context.
        
        Args:
            findings: AST analysis results including functions, classes, etc.
            
        Returns:
            Self for method chaining.
            
        Raises:
            ValueError: If required fields are missing from function definitions.
        """
        # Handle None gracefully
        if findings is None:
            self._ast_findings = None
            return self
        
        # Validate function definitions if present
        if "functions" in findings:
            for func in findings["functions"]:
                if "name" in func and not all(k in func for k in ["file", "line"]):
                    raise ValueError(f"Function '{func.get('name')}' missing required fields: 'file' and 'line'")
        
        self._ast_findings = findings
        return self
    
    def add_git_findings(self, findings: Dict[str, Any]) -> "LENSContextBuilder":
        """Add Git history findings to context.
        
        Args:
            findings: Git analysis results including change frequency, hot spots.
            
        Returns:
            Self for method chaining.
        """
        self._git_findings = findings
        return self
    
    def add_test_findings(self, findings: Dict[str, Any]) -> "LENSContextBuilder":
        """Add test coverage findings to context.
        
        Args:
            findings: Test analysis results including coverage, gaps.
            
        Returns:
            Self for method chaining.
        """
        self._test_findings = findings
        return self
    
    def add_dependency_findings(self, findings: Dict[str, Any]) -> "LENSContextBuilder":
        """Add dependency analysis findings to context.
        
        Args:
            findings: Dependency analysis results including imports, cycles.
            
        Returns:
            Self for method chaining.
        """
        self._dependency_findings = findings
        return self
    
    def add_comment_findings(self, findings: Dict[str, Any]) -> "LENSContextBuilder":
        """Add comment analysis findings to context.
        
        Args:
            findings: Comment analysis results including docstrings, tech debt markers.
            
        Returns:
            Self for method chaining.
        """
        self._comment_findings = findings
        return self
    
    def add_relationship_findings(self, findings: Dict[str, Any]) -> "LENSContextBuilder":
        """Add relationship findings to context.
        
        Args:
            findings: Relationship analysis results including API endpoints, models.
            
        Returns:
            Self for method chaining.
            
        Raises:
            TypeError: If import_graph values are not lists.
        """
        # Validate import graph structure if present
        if "import_graph" in findings:
            for key, value in findings["import_graph"].items():
                if not isinstance(value, list):
                    raise TypeError(f"import_graph['{key}'] must be a list, got {type(value).__name__}")
        
        self._relationship_findings = findings
        return self
    
    def set_intent(self, intent: str) -> "LENSContextBuilder":
        """Set the user intent.
        
        Args:
            intent: User's stated intent or request.
            
        Returns:
            Self for method chaining.
        """
        self._intent = intent
        return self
    
    def add_context(self, key: str, value: Any) -> "LENSContextBuilder":
        """Add additional context data.
        
        Args:
            key: Context key.
            value: Context value.
            
        Returns:
            Self for method chaining.
        """
        self._context[key] = value
        return self
    
    def set_metadata(self, metadata: Dict[str, Any]) -> "LENSContextBuilder":
        """Set metadata for the context.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Self for method chaining.
        """
        self._metadata = metadata
        return self
    
    def build(self) -> LENSContext:
        """Build the complete LENS context.
        
        Returns:
            Constructed LENSContext with all aggregated findings.
        """
        return LENSContext(
            intent=self._intent,
            context=self._context,
            confidence=1.0,
            ast_findings=self._ast_findings,
            git_findings=self._git_findings,
            test_findings=self._test_findings,
            dependency_findings=self._dependency_findings,
            comment_findings=self._comment_findings,
            relationship_findings=self._relationship_findings,
            metadata=self._metadata,
        )
    
    def build_knowledge_graph(self, context: LENSContext) -> KnowledgeGraph:
        """Build a knowledge graph from aggregated context.
        
        Args:
            context: LENSContext to build graph from
            
        Returns:
            KnowledgeGraph with nodes and edges
        """
        kg = KnowledgeGraph()
        
        # Add nodes from AST findings
        if context.ast_findings:
            functions = context.ast_findings.get("functions", [])
            for func in functions:
                node = ContextNode(
                    id=f"func_{func['name']}",
                    node_type="function",
                    name=func["name"],
                    file=func.get("file", ""),
                    metadata={
                        "line": func.get("line"),
                        "parameters": func.get("parameters", []),
                        "return_type": func.get("return_type"),
                    }
                )
                kg.add_node(node)
            
            classes = context.ast_findings.get("classes", [])
            for cls in classes:
                node = ContextNode(
                    id=f"class_{cls['name']}",
                    node_type="class",
                    name=cls["name"],
                    file=cls.get("file", ""),
                    metadata={
                        "line": cls.get("line"),
                        "methods": cls.get("methods", []),
                        "inheritance": cls.get("inheritance", []),
                    }
                )
                kg.add_node(node)
            
            # Add edges from call graph
            call_graph = context.ast_findings.get("call_graph", {})
            for caller, callees in call_graph.items():
                for callee in callees:
                    edge = ContextEdge(
                        source=f"func_{caller}",
                        target=f"func_{callee}",
                        edge_type="calls"
                    )
                    kg.add_edge(edge)
        
        # Add nodes/edges from relationship findings
        if context.relationship_findings:
            api_endpoints = context.relationship_findings.get("api_endpoints", [])
            for endpoint in api_endpoints:
                node = ContextNode(
                    id=f"api_{endpoint.get('path', '').replace('/', '_')}",
                    node_type="api_endpoint",
                    name=endpoint.get("path", ""),
                    file=endpoint.get("file", ""),
                    metadata={
                        "method": endpoint.get("method"),
                        "handler": endpoint.get("handler"),
                    }
                )
                kg.add_node(node)
                
                # Link endpoint to handler function
                handler = endpoint.get("handler")
                if handler:
                    edge = ContextEdge(
                        source=f"api_{endpoint.get('path', '').replace('/', '_')}",
                        target=f"func_{handler}",
                        edge_type="routes_to"
                    )
                    kg.add_edge(edge)
        
        return kg
    
    def filter_context(
        self,
        context: Optional[LENSContext] = None,
        filters: Optional[Dict[str, Any]] = None,
        domains: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
    ) -> "LENSContextBuilder":
        """Filter the context based on criteria.
        
        Args:
            context: LENSContext to filter (optional, uses builder state if not provided)
            filters: Filter criteria dictionary
            domains: List of domain names to filter by
            files: List of file paths to filter by
            types: List of types to filter by (e.g., "function", "class")
            
        Returns:
            Self for method chaining
        """
        # Build filters dict from individual parameters
        combined_filters = filters or {}
        if domains:
            combined_filters["domains"] = domains
        if files:
            combined_filters["files"] = files
        if types:
            combined_filters["types"] = types
        
        if not combined_filters:
            return self
        
        # Apply domain filtering to AST findings
        if "domains" in combined_filters and self._ast_findings:
            domain_list = combined_filters["domains"]
            filtered_ast: Dict[str, Any] = {}
            
            if "functions" in self._ast_findings:
                filtered_ast["functions"] = [
                    f for f in self._ast_findings["functions"]
                    if any(domain in f.get("file", "").lower() for domain in domain_list)
                ]
            
            if "classes" in self._ast_findings:
                filtered_ast["classes"] = [
                    c for c in self._ast_findings["classes"]
                    if any(domain in c.get("file", "").lower() for domain in domain_list)
                ]
            
            self._ast_findings = filtered_ast
        
        # Filter AST findings by file
        if "files" in combined_filters and self._ast_findings:
            target_files = combined_filters["files"]
            filtered_ast = {}
            
            if "functions" in self._ast_findings:
                filtered_ast["functions"] = [
                    f for f in self._ast_findings["functions"]
                    if f.get("file") in target_files
                ]
            
            if "classes" in self._ast_findings:
                filtered_ast["classes"] = [
                    c for c in self._ast_findings["classes"]
                    if c.get("file") in target_files
                ]
            
            self._ast_findings = filtered_ast
        
        # Filter by type
        if "types" in combined_filters and self._ast_findings:
            type_list = combined_filters["types"]
            filtered_ast = {}
            
            if "function" in type_list:
                filtered_ast["functions"] = self._ast_findings.get("functions", [])
            if "class" in type_list:
                filtered_ast["classes"] = self._ast_findings.get("classes", [])
            
            self._ast_findings = filtered_ast
        
        # Filter tech debt markers
        if self._comment_findings and "marker" in combined_filters:
            if combined_filters["marker"] == "tech_debt":
                self._comment_findings = {
                    "tech_debt_markers": self._comment_findings.get("tech_debt_markers", [])
                }
        
        return self
        filtered_context.relationship_findings = context.relationship_findings
        
        return filtered_context
    
    def prioritize_context(
        self,
        context: LENSContext,
        strategy: str = "change_frequency"
    ) -> LENSContext:
        """Prioritize context elements based on a strategy.
        
        Args:
            context: LENSContext to prioritize
            strategy: Prioritization strategy ("change_frequency", "complexity", etc.)
            
        Returns:
            LENSContext with prioritized elements
        """
        prioritized_context = LENSContext(
            intent=context.intent,
            context=context.context.copy(),
            confidence=context.confidence,
            ast_findings=context.ast_findings,
            test_findings=context.test_findings,
            dependency_findings=context.dependency_findings,
            comment_findings=context.comment_findings,
            relationship_findings=context.relationship_findings,
            metadata=context.metadata.copy(),
            timestamp=context.timestamp,
        )
        
        # Prioritize by change frequency
        if strategy == "change_frequency" and context.git_findings:
            git_findings = context.git_findings.copy()
            if "hot_spots" in git_findings:
                hot_spots = sorted(
                    git_findings["hot_spots"],
                    key=lambda x: x.get("changes", 0),
                    reverse=True
                )
                git_findings["hot_spots"] = hot_spots
            prioritized_context.git_findings = git_findings
        
        # Prioritize by complexity
        elif strategy == "complexity" and context.ast_findings:
            # In a real implementation, we'd sort by complexity metrics
            prioritized_context.ast_findings = context.ast_findings
        
        else:
            prioritized_context.git_findings = context.git_findings
        
        return prioritized_context
    
    def query_context(
        self,
        context: LENSContext,
        query_type: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Query the context for specific information.
        
        Enables semantic queries over the aggregated LENS context to extract
        targeted information (e.g., call graphs, expertise distribution, hot spots).
        
        Args:
            context: The LENS context to query.
            query_type: Type of query (e.g., "call_graph", "expertise_by_file", "hot_spots").
            parameters: Optional query parameters.
            
        Returns:
            Query results (dict, list, or None).
        """
        params = parameters or {}
        
        # Handle function queries
        if query_type == "function_by_name":
            if context.ast_findings and "functions" in context.ast_findings:
                name = params.get("name")
                return [f for f in context.ast_findings["functions"] if f.get("name") == name]
            return []
        
        # Handle all functions in file query
        elif query_type in ["all_functions_in_file", "functions_in_file"]:
            if context.ast_findings and "functions" in context.ast_findings:
                file_path = params.get("file")
                return [f for f in context.ast_findings["functions"] if f.get("file") == file_path]
            return []
        
        # Handle call graph queries
        elif query_type == "call_graph":
            if context.ast_findings:
                function_name = params.get("function")
                if function_name and "call_graph" in context.ast_findings:
                    return {
                        "function": function_name,
                        "calls": context.ast_findings["call_graph"].get(function_name, [])
                    }
            return {}
        
        # Handle expertise queries
        elif query_type == "expertise_by_file":
            if context.git_findings:
                file_path = params.get("file")
                if file_path and "expertise_distribution" in context.git_findings:
                    expertise = context.git_findings["expertise_distribution"]
                    return {
                        "file": file_path,
                        "experts": expertise.get(file_path, [])
                    }
            return {}
        
        # Handle hot spot queries
        elif query_type == "hot_spots":
            if context.git_findings and "hot_spots" in context.git_findings:
                limit = params.get("limit", 10)
                return {
                    "hot_spots": context.git_findings["hot_spots"][:limit]
                }
            return {}
        
        return []
    
    def enrich_context(
        self,
        context: LENSContext,
        enrichment_types: Any,
    ) -> LENSContext:
        """Enrich context with computed data.
        
        Computes additional insights from the raw context data such as
        trends, risk scores, impact analysis, etc.
        
        Args:
            context: The LENS context to enrich.
            enrichment_types: Type(s) of enrichment - string or list of strings.
            
        Returns:
            Enriched LENSContext with computed_data populated.
        """
        # Normalize to list
        if isinstance(enrichment_types, str):
            enrichment_types = [enrichment_types]
        
        computed = {}
        
        for enrichment_type in enrichment_types:
            if enrichment_type == "trends" and context.git_findings:
                # Compute trends from git history
                computed["trends"] = {
                    "change_velocity": len(context.git_findings.get("hot_spots", [])),
                    "trend_direction": "increasing"
                }
            
            elif enrichment_type == "risk_scores" and context.comment_findings:
                # Compute risk scores from tech debt markers
                markers = context.comment_findings.get("tech_debt_markers", [])
                computed["risk_scores"] = {
                    "tech_debt_count": len(markers),
                    "overall_risk": "medium" if len(markers) > 5 else "low"
                }
            
            elif enrichment_type == "impact_analysis" and context.relationship_findings:
                # Compute impact from relationships
                import_graph = context.relationship_findings.get("import_graph", {})
                computed["impact_analysis"] = {
                    "dependency_count": len(import_graph),
                    "impact_radius": "high" if len(import_graph) > 10 else "low"
                }
            
            elif enrichment_type == "tech_debt_analysis" and context.comment_findings:
                # Tech debt analysis
                markers = context.comment_findings.get("tech_debt_markers", [])
                computed["tech_debt_analysis"] = {
                    "total_markers": len(markers),
                    "severity": "high" if len(markers) > 10 else "medium"
                }
        
        # Return new context with computed data
        enriched = LENSContext(
            intent=context.intent,
            context=context.context,
            confidence=context.confidence,
            ast_findings=context.ast_findings,
            git_findings=context.git_findings,
            test_findings=context.test_findings,
            dependency_findings=context.dependency_findings,
            comment_findings=context.comment_findings,
            relationship_findings=context.relationship_findings,
            knowledge_graph=context.knowledge_graph,
            metadata=context.metadata,
            computed_data=computed if computed else None,
            timestamp=context.timestamp
        )
        
        return enriched


__all__ = ["LENSContext", "ContextNode", "ContextEdge", "KnowledgeGraph", "LENSContextBuilder"]
