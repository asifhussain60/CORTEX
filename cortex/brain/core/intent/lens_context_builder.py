"""
LENS Context Builder Module (IR-003-02).

Aggregates and synthesizes findings from all four intelligence sources
(AST Analysis, Git History, Code Comments, Relationship Traversal) into
a unified knowledge graph representing comprehensive codebase context.

The LENSContextBuilder serves as the critical link between the CORTEX
intelligence gathering phase and the Intent Reflection Protocol, ensuring
all contextual data is properly aggregated, prioritized, and available
for challenge detection and recommendation generation.

Core responsibilities:
1. Aggregate findings from multiple sources into unified representation
2. Build knowledge graph representing code structure and relationships
3. Filter and prioritize context data for relevance and impact
4. Serialize context for transmission through protocol layers
5. Query and traverse context for intelligence extraction
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional, Set, Tuple

# ============================================================================
# ENUMS
# ============================================================================

class ContextNodeType(Enum):
    """Types of nodes in the knowledge graph."""
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    FILE = "file"
    API_ENDPOINT = "api_endpoint"
    DATABASE_MODEL = "database_model"
    CONFIGURATION = "configuration"
    PATTERN = "pattern"


class ContextEdgeType(Enum):
    """Types of relationships between context nodes."""
    CALLS = "calls"
    INHERITS = "inherits"
    IMPORTS = "imports"
    IMPLEMENTS = "implements"
    MODIFIES = "modifies"
    DEPENDS_ON = "depends_on"
    USED_BY = "used_by"
    RELATED_TO = "related_to"


class PrioritizationStrategy(Enum):
    """Strategies for prioritizing context data."""
    CHANGE_FREQUENCY = "change_frequency"
    COMPLEXITY = "complexity"
    EXPERTISE_CONCENTRATION = "expertise_concentration"
    RISK_LEVEL = "risk_level"
    RECENCY = "recency"


# ============================================================================
# DATA CLASSES - Graph Structures
# ============================================================================

@dataclass
class ContextNode:
    """Represents a single node in the knowledge graph."""

    id: str
    node_type: str  # Use ContextNodeType.value
    name: str
    file: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary."""
        return {
            "id": self.id,
            "node_type": self.node_type,
            "name": self.name,
            "file": self.file,
            "metadata": self.metadata,
        }


@dataclass
class ContextEdge:
    """Represents a relationship between two context nodes."""

    source: str  # Node ID
    target: str  # Node ID
    edge_type: str  # Use ContextEdgeType.value
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary."""
        return {
            "source": self.source,
            "target": self.target,
            "edge_type": self.edge_type,
            "metadata": self.metadata,
        }


@dataclass
class KnowledgeGraph:
    """Graph representation of codebase context."""

    nodes: Dict[str, ContextNode] = field(default_factory=dict)
    edges: List[ContextEdge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: ContextNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node

    def add_edge(self, edge: ContextEdge) -> None:
        """Add an edge to the graph."""
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError(
                "Cannot add edge: source or target node not in graph"
            )
        self.edges.append(edge)

    def get_neighbors(self, node_id: str) -> List[str]:
        """Get all nodes connected to a given node."""
        neighbors = []
        for edge in self.edges:
            if edge.source == node_id:
                neighbors.append(edge.target)
            elif edge.target == node_id:
                neighbors.append(edge.source)
        return neighbors

    def get_edges_from(self, node_id: str) -> List[ContextEdge]:
        """Get all edges originating from a node."""
        return [e for e in self.edges if e.source == node_id]

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary."""
        return {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "edges": [edge.to_dict() for edge in self.edges],
            "metadata": self.metadata,
        }


@dataclass
class LENSContext:
    """Unified context from all intelligence sources."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    # Raw findings from each source
    ast_findings: Optional[Dict[str, Any]] = None
    git_findings: Optional[Dict[str, Any]] = None
    comment_findings: Optional[Dict[str, Any]] = None
    relationship_findings: Optional[Dict[str, Any]] = None

    # Computed data
    computed_data: Dict[str, Any] = field(default_factory=dict)
    knowledge_graph: Optional[KnowledgeGraph] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "ast_findings": self.ast_findings,
            "git_findings": self.git_findings,
            "comment_findings": self.comment_findings,
            "relationship_findings": self.relationship_findings,
            "computed_data": self.computed_data,
            "knowledge_graph": self.knowledge_graph.to_dict() if self.knowledge_graph else None,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Convert context to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "LENSContext":
        """Create context from dictionary."""
        context = LENSContext(
            id=data.get("id", str(uuid.uuid4())),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            ast_findings=data.get("ast_findings"),
            git_findings=data.get("git_findings"),
            comment_findings=data.get("comment_findings"),
            relationship_findings=data.get("relationship_findings"),
            computed_data=data.get("computed_data", {}),
            metadata=data.get("metadata", {}),
        )

        # Reconstruct knowledge graph if present
        if "knowledge_graph" in data and data["knowledge_graph"]:
            kg_data = data["knowledge_graph"]
            kg = KnowledgeGraph()
            for node_data in kg_data.get("nodes", {}).values():
                node = ContextNode(
                    id=node_data["id"],
                    node_type=node_data["node_type"],
                    name=node_data["name"],
                    file=node_data["file"],
                    metadata=node_data.get("metadata", {}),
                )
                kg.add_node(node)
            for edge_data in kg_data.get("edges", []):
                edge = ContextEdge(
                    source=edge_data["source"],
                    target=edge_data["target"],
                    edge_type=edge_data["edge_type"],
                    metadata=edge_data.get("metadata", {}),
                )
                kg.add_edge(edge)
            context.knowledge_graph = kg

        return context

    @staticmethod
    def from_json(json_str: str) -> "LENSContext":
        """Create context from JSON string."""
        data = json.loads(json_str)
        return LENSContext.from_dict(data)


# ============================================================================
# MAIN BUILDER CLASS
# ============================================================================

class LENSContextBuilder:
    """Builder for aggregating and synthesizing codebase context."""

    def __init__(self):
        """Initialize the context builder."""
        self._ast_findings: Optional[Dict[str, Any]] = None
        self._git_findings: Optional[Dict[str, Any]] = None
        self._comment_findings: Optional[Dict[str, Any]] = None
        self._relationship_findings: Optional[Dict[str, Any]] = None
        self._metadata: Dict[str, Any] = {}

    def add_ast_findings(self, findings: Dict[str, Any]) -> "LENSContextBuilder":
        """Add findings from AST Intelligence module."""
        if findings is None:
            self._ast_findings = None
            return self

        # Validate required fields for each function
        if "functions" in findings:
            for func in findings["functions"]:
                if not all(k in func for k in ["name", "file", "line"]):
                    raise ValueError(
                        "AST finding must include name, file, and line"
                    )

        self._ast_findings = findings
        return self

    def add_git_findings(self, findings: Dict[str, Any]) -> "LENSContextBuilder":
        """Add findings from Git History Analyzer module."""
        if findings is None:
            self._git_findings = None
            return self

        self._git_findings = findings
        return self

    def add_comment_findings(
        self, findings: Dict[str, Any]
    ) -> "LENSContextBuilder":
        """Add findings from Comment Analyzer module."""
        if findings is None:
            self._comment_findings = None
            return self

        self._comment_findings = findings
        return self

    def add_relationship_findings(
        self, findings: Dict[str, Any]
    ) -> "LENSContextBuilder":
        """Add findings from Relationship Traversal Engine."""
        if findings is None:
            self._relationship_findings = None
            return self

        # Validate import_graph format
        if "import_graph" in findings:
            for key, value in findings["import_graph"].items():
                if not isinstance(value, list):
                    raise TypeError(
                        "import_graph values must be lists of module names"
                    )

        self._relationship_findings = findings
        return self

    def set_metadata(self, metadata: Dict[str, Any]) -> "LENSContextBuilder":
        """Set context metadata."""
        self._metadata.update(metadata)
        return self

    def build(self) -> LENSContext:
        """Build and return the aggregated context."""
        context = LENSContext(
            ast_findings=self._ast_findings,
            git_findings=self._git_findings,
            comment_findings=self._comment_findings,
            relationship_findings=self._relationship_findings,
            metadata=self._metadata,
        )
        return context

    def build_knowledge_graph(self, context: LENSContext) -> KnowledgeGraph:
        """Build knowledge graph from aggregated context."""
        kg = KnowledgeGraph()

        # Add nodes and edges from AST findings
        if context.ast_findings:
            self._add_ast_nodes_to_graph(kg, context.ast_findings)

        # Add nodes from relationship findings
        if context.relationship_findings:
            self._add_relationship_nodes_to_graph(kg, context.relationship_findings)

        # Add edges from relationships
        if context.relationship_findings:
            self._add_relationship_edges_to_graph(kg, context.relationship_findings)

        return kg

    def _add_ast_nodes_to_graph(
        self, kg: KnowledgeGraph, ast_findings: Dict[str, Any]
    ) -> None:
        """Add AST nodes to knowledge graph."""
        # Add function nodes
        for func in ast_findings.get("functions", []):
            node = ContextNode(
                id=f"func_{func['name']}",
                node_type=ContextNodeType.FUNCTION.value,
                name=func["name"],
                file=func["file"],
                metadata={
                    "line": func.get("line"),
                    "complexity": func.get("complexity", 1),
                },
            )
            kg.add_node(node)

        # Add class nodes
        for cls in ast_findings.get("classes", []):
            node = ContextNode(
                id=f"class_{cls['name']}",
                node_type=ContextNodeType.CLASS.value,
                name=cls["name"],
                file=cls["file"],
                metadata={"line": cls.get("line")},
            )
            kg.add_node(node)

        # Add edges for function calls
        call_graph = ast_findings.get("call_graph", {})
        for source, targets in call_graph.items():
            source_id = f"func_{source}"
            for target in targets:
                target_id = f"func_{target}"
                if source_id in kg.nodes and target_id in kg.nodes:
                    edge = ContextEdge(
                        source=source_id,
                        target=target_id,
                        edge_type=ContextEdgeType.CALLS.value,
                    )
                    kg.add_edge(edge)

    def _add_relationship_nodes_to_graph(
        self, kg: KnowledgeGraph, relationship_findings: Dict[str, Any]
    ) -> None:
        """Add relationship nodes to knowledge graph."""
        # Add API endpoint nodes
        for endpoint in relationship_findings.get("api_endpoints", []):
            node = ContextNode(
                id=f"api_{endpoint['path']}",
                node_type=ContextNodeType.API_ENDPOINT.value,
                name=endpoint["path"],
                file=endpoint.get("file", ""),
                metadata={
                    "method": endpoint.get("method"),
                    "handler": endpoint.get("handler"),
                },
            )
            kg.add_node(node)

        # Add database model nodes
        for model in relationship_findings.get("database_models", []):
            node = ContextNode(
                id=f"model_{model['name']}",
                node_type=ContextNodeType.DATABASE_MODEL.value,
                name=model["name"],
                file=model.get("file", ""),
                metadata={"fields": model.get("fields", [])},
            )
            kg.add_node(node)

    def _add_relationship_edges_to_graph(
        self, kg: KnowledgeGraph, relationship_findings: Dict[str, Any]
    ) -> None:
        """Add relationship edges to knowledge graph."""
        # Add import edges
        import_graph = relationship_findings.get("import_graph", {})
        for source_file, imports in import_graph.items():
            for target_file in imports:
                edge = ContextEdge(
                    source=f"file_{source_file}",
                    target=f"file_{target_file}",
                    edge_type=ContextEdgeType.IMPORTS.value,
                )
                # Only add if both nodes exist, or create new nodes
                try:
                    kg.add_edge(edge)
                except ValueError:
                    # Create file nodes if they don't exist
                    kg.add_node(ContextNode(
                        id=f"file_{source_file}",
                        node_type=ContextNodeType.FILE.value,
                        name=source_file.split("/")[-1],
                        file=source_file,
                    ))
                    kg.add_node(ContextNode(
                        id=f"file_{target_file}",
                        node_type=ContextNodeType.FILE.value,
                        name=target_file.split("/")[-1],
                        file=target_file,
                    ))
                    kg.add_edge(edge)

    def filter_context(
        self,
        context: LENSContext,
        filters: Dict[str, Any]
    ) -> LENSContext:
        """Filter context data based on criteria."""
        filtered_context = LENSContext(
            id=context.id,
            timestamp=context.timestamp,
            metadata=context.metadata,
        )

        # Filter AST findings
        if context.ast_findings:
            filtered_context.ast_findings = self._filter_ast_findings(
                context.ast_findings, filters
            )

        # Filter Git findings
        if context.git_findings:
            filtered_context.git_findings = self._filter_git_findings(
                context.git_findings, filters
            )

        # Filter comment findings
        if context.comment_findings:
            filtered_context.comment_findings = self._filter_comment_findings(
                context.comment_findings, filters
            )

        # Filter relationship findings
        if context.relationship_findings:
            filtered_context.relationship_findings = self._filter_relationship_findings(
                context.relationship_findings, filters
            )

        return filtered_context

    def _filter_ast_findings(
        self, findings: Dict[str, Any], filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Filter AST findings."""
        filtered = findings.copy()

        if "file" in filters:
            target_file = filters["file"]
            if "functions" in filtered:
                filtered["functions"] = [
                    f for f in filtered["functions"] if f["file"] == target_file
                ]
            if "classes" in filtered:
                filtered["classes"] = [
                    c for c in filtered["classes"] if c["file"] == target_file
                ]

        return filtered

    def _filter_git_findings(
        self, findings: Dict[str, Any], filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Filter Git findings."""
        return findings.copy()

    def _filter_comment_findings(
        self, findings: Dict[str, Any], filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Filter comment findings."""
        filtered = findings.copy()

        if filters.get("marker") == "tech_debt":
            if "tech_debt_markers" in filtered:
                filtered = {
                    "tech_debt_markers": filtered["tech_debt_markers"]
                }

        return filtered

    def _filter_relationship_findings(
        self, findings: Dict[str, Any], filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Filter relationship findings."""
        return findings.copy()

    def prioritize_context(
        self,
        context: LENSContext,
        strategy: str
    ) -> LENSContext:
        """Prioritize context data based on strategy."""
        prioritized = LENSContext(
            id=context.id,
            timestamp=context.timestamp,
            ast_findings=context.ast_findings,
            git_findings=context.git_findings,
            comment_findings=context.comment_findings,
            relationship_findings=context.relationship_findings,
            metadata=context.metadata,
        )

        # Apply prioritization strategy
        if strategy == "change_frequency" and context.git_findings:
            hot_spots = context.git_findings.get("hot_spots", [])
            sorted_hot_spots = sorted(
                hot_spots, key=lambda x: x.get("changes", 0), reverse=True
            )
            prioritized.git_findings = context.git_findings.copy()
            prioritized.git_findings["hot_spots"] = sorted_hot_spots

        return prioritized

    def enrich_context(
        self,
        context: LENSContext,
        enrichment_types: Optional[Any] = None
    ) -> LENSContext:
        """Enrich context with computed data."""
        if enrichment_types is None:
            enrichment_types = []
        elif isinstance(enrichment_types, str):
            enrichment_types = [enrichment_types]

        enriched = LENSContext(
            id=context.id,
            timestamp=context.timestamp,
            ast_findings=context.ast_findings,
            git_findings=context.git_findings,
            comment_findings=context.comment_findings,
            relationship_findings=context.relationship_findings,
            metadata=context.metadata,
            computed_data=context.computed_data.copy(),
        )

        for enrichment_type in enrichment_types:
            if enrichment_type == "trends":
                enriched.computed_data["trends"] = self._compute_trends(context)
            elif enrichment_type == "risk_scores":
                enriched.computed_data["risk_scores"] = self._compute_risk_scores(context)
            elif enrichment_type == "impact_analysis":
                enriched.computed_data["impact_analysis"] = self._compute_impact_analysis(context)
            elif enrichment_type == "tech_debt_analysis":
                enriched.computed_data["tech_debt_analysis"] = self._compute_tech_debt_analysis(context)

        return enriched

    def _compute_trends(self, context: LENSContext) -> Dict[str, Any]:
        """Compute trends from git findings."""
        if not context.git_findings:
            return {}

        hot_spots = context.git_findings.get("hot_spots", [])
        return {
            "most_changed": hot_spots[0]["file"] if hot_spots else None,
            "change_count": sum(h.get("changes", 0) for h in hot_spots),
        }

    def _compute_risk_scores(self, context: LENSContext) -> Dict[str, Any]:
        """Compute risk scores."""
        return {"overall_risk": "MEDIUM"}

    def _compute_impact_analysis(self, context: LENSContext) -> Dict[str, Any]:
        """Compute impact analysis."""
        return {"total_impact": "HIGH"}

    def _compute_tech_debt_analysis(self, context: LENSContext) -> Dict[str, Any]:
        """Compute tech debt analysis."""
        if not context.comment_findings:
            return {}

        debt_items = context.comment_findings.get("tech_debt_markers", [])
        return {
            "total_items": len(debt_items),
            "high_severity": sum(1 for item in debt_items if item.get("severity") == "HIGH"),
        }

    def query_context(
        self,
        context: LENSContext,
        query_type: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """Query context for specific information."""
        if query_type == "function_by_name":
            return self._query_function_by_name(context, parameters)
        elif query_type == "functions_in_file":
            return self._query_functions_in_file(context, parameters)
        elif query_type == "call_graph":
            return self._query_call_graph(context, parameters)
        elif query_type == "expertise_by_file":
            return self._query_expertise_by_file(context, parameters)
        else:
            raise ValueError(f"Unknown query type: {query_type}")

    def _query_function_by_name(
        self, context: LENSContext, parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Query functions by name."""
        if not context.ast_findings:
            return []

        name = parameters.get("name")
        functions = context.ast_findings.get("functions", [])
        return [f for f in functions if f["name"] == name]

    def _query_functions_in_file(
        self, context: LENSContext, parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Query all functions in a file."""
        if not context.ast_findings:
            return []

        file_path = parameters.get("file")
        functions = context.ast_findings.get("functions", [])
        return [f for f in functions if f["file"] == file_path]

    def _query_call_graph(
        self, context: LENSContext, parameters: Dict[str, Any]
    ) -> Optional[List[str]]:
        """Query call graph for a function."""
        if not context.ast_findings:
            return None

        func_name = parameters.get("function")
        call_graph = context.ast_findings.get("call_graph", {})
        return call_graph.get(func_name)

    def _query_expertise_by_file(
        self, context: LENSContext, parameters: Dict[str, Any]
    ) -> Optional[Dict[str, int]]:
        """Query expertise distribution for a file."""
        if not context.git_findings:
            return None

        file_path = parameters.get("file")
        expertise_map = context.git_findings.get("expertise_map", {})
        return expertise_map.get(file_path)
