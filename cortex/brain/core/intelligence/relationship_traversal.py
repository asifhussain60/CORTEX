# AC-ID: IR-001-04 - Relationship Traversal Engine
"""
Relationship Traversal Engine for code relationships.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-001-04 - Relationship Traversal Engine

Detects and tracks relationships between:
- API endpoints
- Database models
- Configuration references
- Cross-file dependencies
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class APIEndpoint:
    """An API endpoint definition."""
    path: str
    methods: List[str]
    function_name: str
    line_number: int
    framework: str = "unknown"  # flask, fastapi, django
    prefix: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "methods": self.methods,
            "function_name": self.function_name,
            "line_number": self.line_number,
            "framework": self.framework,
            "prefix": self.prefix,
        }


@dataclass
class ForeignKeyRef:
    """A foreign key reference."""
    column: str
    reference: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"column": self.column, "reference": self.reference}


@dataclass
class ModelRelationship:
    """A model relationship (ORM)."""
    name: str
    target: str
    relationship_type: str = "relationship"  # relationship, backref
    back_populates: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "target": self.target,
            "relationship_type": self.relationship_type,
            "back_populates": self.back_populates,
        }


@dataclass
class DatabaseModel:
    """A database model definition."""
    name: str
    table_name: str
    columns: List[str]
    foreign_keys: List[ForeignKeyRef]
    relationships: List[ModelRelationship]
    line_number: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "table_name": self.table_name,
            "columns": self.columns,
            "foreign_keys": [fk.to_dict() for fk in self.foreign_keys],
            "relationships": [r.to_dict() for r in self.relationships],
            "line_number": self.line_number,
        }


@dataclass
class EnvReference:
    """An environment variable reference."""
    name: str
    line_number: int
    default_value: Optional[str] = None
    required: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "line_number": self.line_number,
            "default_value": self.default_value,
            "required": self.required,
        }


@dataclass
class ConfigReference:
    """A configuration reference."""
    key: str
    source: str  # settings, config, etc.
    line_number: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "source": self.source,
            "line_number": self.line_number,
        }


@dataclass
class FileDependency:
    """A file dependency."""
    source_file: str
    source_module: str
    imports: List[str]
    line_number: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_file": self.source_file,
            "source_module": self.source_module,
            "imports": self.imports,
            "line_number": self.line_number,
        }


@dataclass
class DependencyGraph:
    """A graph of file dependencies."""
    nodes: Set[str] = field(default_factory=set)
    edges: List[Tuple[str, str]] = field(default_factory=list)

    def add_node(self, node: str) -> None:
        """Add a node to the graph."""
        self.nodes.add(node)

    def add_edge(self, from_node: str, to_node: str) -> None:
        """Add an edge to the graph."""
        self.nodes.add(from_node)
        self.nodes.add(to_node)
        self.edges.append((from_node, to_node))


@dataclass
class ModelGraph:
    """A graph of model relationships."""
    nodes: Set[str] = field(default_factory=set)
    edges: List[Tuple[str, str, str]] = field(default_factory=list)  # (from, to, type)

    def add_node(self, node: str) -> None:
        """Add a node to the graph."""
        self.nodes.add(node)

    def add_edge(self, from_node: str, to_node: str, edge_type: str = "relates") -> None:
        """Add an edge to the graph."""
        self.nodes.add(from_node)
        self.nodes.add(to_node)
        self.edges.append((from_node, to_node, edge_type))


@dataclass
class ImpactAnalysis:
    """Impact analysis results."""
    source_file: str
    affected_files: List[str]
    affected_endpoints: List[str]
    affected_models: List[str]
    impact_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_file": self.source_file,
            "affected_files": self.affected_files,
            "affected_endpoints": self.affected_endpoints,
            "affected_models": self.affected_models,
            "impact_level": self.impact_level,
        }


@dataclass
class RelationshipAnalysisResult:
    """Result of relationship analysis."""
    api_endpoints: List[APIEndpoint] = field(default_factory=list)
    database_models: List[DatabaseModel] = field(default_factory=list)
    env_references: List[EnvReference] = field(default_factory=list)
    config_references: List[ConfigReference] = field(default_factory=list)
    file_dependencies: List[FileDependency] = field(default_factory=list)
    dependency_graph: Optional[DependencyGraph] = None
    model_graph: Optional[ModelGraph] = None
    _file_path_map: Dict[str, str] = field(default_factory=dict)

    def get_file_dependencies(self, file_path: str) -> List[FileDependency]:
        """Get dependencies for a specific file."""
        return [d for d in self.file_dependencies if d.source_file == file_path]

    def get_related_models(self, model_name: str) -> List[str]:
        """Get models related to the given model."""
        related = []
        if self.model_graph:
            for from_node, to_node, _ in self.model_graph.edges:
                if from_node == model_name:
                    related.append(to_node)
                elif to_node == model_name:
                    related.append(from_node)
        return list(set(related))

    def calculate_impact(self, file_path: str) -> ImpactAnalysis:
        """Calculate impact of changing a file."""
        affected_files = []
        affected_endpoints = []
        affected_models = []

        # Find files that depend on this file
        if self.dependency_graph:
            file_name = Path(file_path).stem
            for from_node, to_node in self.dependency_graph.edges:
                if to_node == file_name:
                    affected_files.append(from_node)

        # Find endpoints in affected files
        for endpoint in self.api_endpoints:
            if endpoint.function_name in [d.source_module for d in self.file_dependencies]:
                affected_endpoints.append(endpoint.path)

        # Determine impact level
        impact_level = "LOW"
        if len(affected_files) > 5:
            impact_level = "CRITICAL"
        elif len(affected_files) > 2:
            impact_level = "HIGH"
        elif len(affected_files) > 0:
            impact_level = "MEDIUM"

        return ImpactAnalysis(
            source_file=file_path,
            affected_files=affected_files,
            affected_endpoints=affected_endpoints,
            affected_models=affected_models,
            impact_level=impact_level,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "api_endpoints": [e.to_dict() for e in self.api_endpoints],
            "database_models": [m.to_dict() for m in self.database_models],
            "env_references": [e.to_dict() for e in self.env_references],
            "config_references": [c.to_dict() for c in self.config_references],
            "file_dependencies": [d.to_dict() for d in self.file_dependencies],
        }

    def to_graphviz(self) -> str:
        """Export to graphviz DOT format."""
        lines = ["digraph relationships {"]
        lines.append("  rankdir=LR;")
        lines.append("  node [shape=box];")

        # Add model nodes and relationships
        if self.model_graph:
            for node in self.model_graph.nodes:
                lines.append(f'  "{node}" [style=filled,fillcolor=lightblue];')
            for from_node, to_node, edge_type in self.model_graph.edges:
                lines.append(f'  "{from_node}" -> "{to_node}" [label="{edge_type}"];')

        # Add file dependency nodes
        if self.dependency_graph:
            for node in self.dependency_graph.nodes:
                lines.append(f'  "{node}" [style=filled,fillcolor=lightyellow];')
            for from_node, to_node in self.dependency_graph.edges:
                lines.append(f'  "{from_node}" -> "{to_node}" [style=dashed];')

        lines.append("}")
        return "\n".join(lines)


# =============================================================================
# RELATIONSHIP ENGINE
# =============================================================================


class RelationshipEngine:
    """Engine for analyzing code relationships."""

    # Flask route decorator pattern
    FLASK_ROUTE_PATTERN = re.compile(
        r"@\w+\.route\s*\(\s*['\"]([^'\"]+)['\"]"
        r"(?:.*?methods\s*=\s*\[([^\]]+)\])?"
    )

    # FastAPI route decorator patterns
    FASTAPI_PATTERNS = {
        "get": re.compile(r"@\w+\.get\s*\(\s*['\"]([^'\"]+)['\"]"),
        "post": re.compile(r"@\w+\.post\s*\(\s*['\"]([^'\"]+)['\"]"),
        "put": re.compile(r"@\w+\.put\s*\(\s*['\"]([^'\"]+)['\"]"),
        "delete": re.compile(r"@\w+\.delete\s*\(\s*['\"]([^'\"]+)['\"]"),
        "patch": re.compile(r"@\w+\.patch\s*\(\s*['\"]([^'\"]+)['\"]"),
    }

    def __init__(self):
        """Initialize the relationship engine."""
        pass

    def analyze_file(self, file_path: Path) -> RelationshipAnalysisResult:
        """Analyze relationships in a file.

        Args:
            file_path: Path to the Python file.

        Returns:
            RelationshipAnalysisResult with detected relationships.
        """
        content = file_path.read_text(encoding="utf-8")
        result = self.analyze_string(content)
        return result

    def analyze_string(self, source: str) -> RelationshipAnalysisResult:
        """Analyze relationships in source code.

        Args:
            source: Python source code.

        Returns:
            RelationshipAnalysisResult with detected relationships.
        """
        result = RelationshipAnalysisResult()

        # Parse AST
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return result

        # Extract API endpoints
        result.api_endpoints = self._extract_api_endpoints(tree, source)

        # Extract database models
        result.database_models = self._extract_database_models(tree, source)

        # Extract environment references
        result.env_references = self._extract_env_references(tree, source)

        # Extract config references
        result.config_references = self._extract_config_references(tree, source)

        # Build model graph
        result.model_graph = self._build_model_graph(result.database_models)

        return result

    def analyze_directory(self, dir_path: Path) -> RelationshipAnalysisResult:
        """Analyze relationships across a directory.

        Args:
            dir_path: Path to the directory.

        Returns:
            RelationshipAnalysisResult with aggregated relationships.
        """
        result = RelationshipAnalysisResult()
        result.dependency_graph = DependencyGraph()

        # Find all Python files
        py_files = list(dir_path.glob("*.py"))

        for py_file in py_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                file_result = self.analyze_string(content)

                # Aggregate results
                result.api_endpoints.extend(file_result.api_endpoints)
                result.database_models.extend(file_result.database_models)
                result.env_references.extend(file_result.env_references)
                result.config_references.extend(file_result.config_references)

                # Extract file dependencies
                deps = self._extract_file_dependencies(content, str(py_file))
                result.file_dependencies.extend(deps)

                # Build dependency graph
                file_name = py_file.stem
                result.dependency_graph.add_node(file_name)
                for dep in deps:
                    result.dependency_graph.add_edge(file_name, dep.source_module)

            except Exception:
                continue

        # Build model graph from all models
        result.model_graph = self._build_model_graph(result.database_models)

        return result

    def _extract_api_endpoints(
        self, tree: ast.AST, source: str
    ) -> List[APIEndpoint]:
        """Extract API endpoints from AST and source.

        Args:
            tree: Parsed AST.
            source: Original source code.

        Returns:
            List of detected API endpoints.
        """
        endpoints = []
        lines = source.split('\n')

        # Find decorated functions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check decorators
                for decorator in node.decorator_list:
                    decorator_line = lines[decorator.lineno - 1] if decorator.lineno <= len(lines) else ""

                    # Check for Flask-style route
                    flask_match = self.FLASK_ROUTE_PATTERN.search(decorator_line)
                    if flask_match:
                        path = flask_match.group(1)
                        methods_str = flask_match.group(2) if flask_match.lastindex >= 2 else None

                        if methods_str:
                            methods = [m.strip().strip("'\"") for m in methods_str.split(',')]
                        else:
                            methods = ['GET']

                        endpoints.append(APIEndpoint(
                            path=path,
                            methods=methods,
                            function_name=node.name,
                            line_number=node.lineno,
                            framework="flask",
                        ))
                        continue

                    # Check for FastAPI-style routes
                    for method, pattern in self.FASTAPI_PATTERNS.items():
                        match = pattern.search(decorator_line)
                        if match:
                            path = match.group(1)
                            endpoints.append(APIEndpoint(
                                path=path,
                                methods=[method.upper()],
                                function_name=node.name,
                                line_number=node.lineno,
                                framework="fastapi",
                            ))
                            break

        return endpoints

    def _extract_database_models(
        self, tree: ast.AST, source: str
    ) -> List[DatabaseModel]:
        """Extract database model definitions.

        Args:
            tree: Parsed AST.
            source: Original source code.

        Returns:
            List of detected database models.
        """
        models = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a SQLAlchemy model (has Base or __tablename__)
                table_name = None
                columns = []
                foreign_keys = []
                relationships = []

                for item in node.body:
                    # Check for __tablename__
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == '__tablename__':
                                if isinstance(item.value, ast.Constant):
                                    table_name = item.value.value

                    # Check for Column definitions
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                col_name = target.id
                                if isinstance(item.value, ast.Call):
                                    func = item.value.func
                                    if isinstance(func, ast.Name) and func.id == 'Column':
                                        columns.append(col_name)

                                        # Check for ForeignKey
                                        for arg in item.value.args:
                                            if isinstance(arg, ast.Call):
                                                if isinstance(arg.func, ast.Name) and arg.func.id == 'ForeignKey':
                                                    if arg.args and isinstance(arg.args[0], ast.Constant):
                                                        foreign_keys.append(ForeignKeyRef(
                                                            column=col_name,
                                                            reference=arg.args[0].value,
                                                        ))

                                    # Check for relationship
                                    if isinstance(func, ast.Name) and func.id == 'relationship':
                                        if item.value.args and isinstance(item.value.args[0], ast.Constant):
                                            target = item.value.args[0].value
                                            back_populates = None

                                            for keyword in item.value.keywords:
                                                if keyword.arg == 'back_populates':
                                                    if isinstance(keyword.value, ast.Constant):
                                                        back_populates = keyword.value.value

                                            relationships.append(ModelRelationship(
                                                name=col_name,
                                                target=target,
                                                back_populates=back_populates,
                                            ))

                # Only add if it looks like a model
                if table_name or columns or foreign_keys or relationships:
                    models.append(DatabaseModel(
                        name=node.name,
                        table_name=table_name or node.name.lower(),
                        columns=columns,
                        foreign_keys=foreign_keys,
                        relationships=relationships,
                        line_number=node.lineno,
                    ))

        return models

    def _extract_env_references(
        self, tree: ast.AST, source: str
    ) -> List[EnvReference]:
        """Extract environment variable references.

        Args:
            tree: Parsed AST.
            source: Original source code.

        Returns:
            List of environment variable references.
        """
        env_refs = []

        for node in ast.walk(tree):
            # Check for os.environ.get() or os.getenv()
            if isinstance(node, ast.Call):
                func = node.func

                # os.environ.get('VAR') or os.environ['VAR']
                if isinstance(func, ast.Attribute):
                    if func.attr in ('get', 'getenv'):
                        if node.args and isinstance(node.args[0], ast.Constant):
                            var_name = node.args[0].value
                            default = None
                            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                                default = str(node.args[1].value)

                            env_refs.append(EnvReference(
                                name=var_name,
                                line_number=node.lineno,
                                default_value=default,
                                required=False,
                            ))

                # Check for os.environ access without get
            elif isinstance(node, ast.Subscript):
                if isinstance(node.value, ast.Attribute):
                    if isinstance(node.value.value, ast.Name):
                        if node.value.value.id == 'os' and node.value.attr == 'environ':
                            if isinstance(node.slice, ast.Constant):
                                env_refs.append(EnvReference(
                                    name=node.slice.value,
                                    line_number=node.lineno,
                                    required=True,
                                ))

        return env_refs

    def _extract_config_references(
        self, tree: ast.AST, source: str
    ) -> List[ConfigReference]:
        """Extract configuration references.

        Args:
            tree: Parsed AST.
            source: Original source code.

        Returns:
            List of configuration references.
        """
        config_refs = []

        for node in ast.walk(tree):
            # Check for settings.ATTR access
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    if node.value.id in ('settings', 'config', 'Config', 'Settings'):
                        config_refs.append(ConfigReference(
                            key=node.attr,
                            source=node.value.id,
                            line_number=node.lineno,
                        ))

        return config_refs

    def _extract_file_dependencies(
        self, source: str, file_path: str
    ) -> List[FileDependency]:
        """Extract file/module dependencies from imports.

        Args:
            source: Python source code.
            file_path: Path to the source file.

        Returns:
            List of file dependencies.
        """
        dependencies = []

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return dependencies

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(FileDependency(
                        source_file=file_path,
                        source_module=alias.name.split('.')[0],
                        imports=[alias.name],
                        line_number=node.lineno,
                    ))

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split('.')[0]
                    imported = [alias.name for alias in node.names]
                    dependencies.append(FileDependency(
                        source_file=file_path,
                        source_module=module_name,
                        imports=imported,
                        line_number=node.lineno,
                    ))

        return dependencies

    def _build_model_graph(self, models: List[DatabaseModel]) -> ModelGraph:
        """Build a graph of model relationships.

        Args:
            models: List of database models.

        Returns:
            ModelGraph with nodes and edges.
        """
        graph = ModelGraph()

        for model in models:
            graph.add_node(model.name)

            # Add edges from relationships
            for rel in model.relationships:
                graph.add_edge(model.name, rel.target, "relationship")

            # Add edges from foreign keys
            for fk in model.foreign_keys:
                # Extract table name from reference (e.g., 'users.id' -> 'users')
                ref_table = fk.reference.split('.')[0]
                # Find model with matching table name
                for other_model in models:
                    if other_model.table_name == ref_table:
                        graph.add_edge(model.name, other_model.name, "foreign_key")
                        break

        return graph


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "RelationshipEngine",
    "RelationshipAnalysisResult",
    "APIEndpoint",
    "DatabaseModel",
    "EnvReference",
    "ConfigReference",
    "FileDependency",
    "DependencyGraph",
    "ModelGraph",
    "ImpactAnalysis",
    "ForeignKeyRef",
    "ModelRelationship",
]
