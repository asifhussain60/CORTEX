"""MSBuild ProjectReference Dependency Resolver.

Resolves inter-project dependencies in .NET solutions by analyzing:
- ProjectReference elements in .csproj files
- Relative path resolution
- Transitive dependency graphs
- Circular dependency detection
- Layer violation identification

AC-PHASE55-S2: MSBuild resolver builds project dependency graph
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


@dataclass
class ProjectNode:
    """Represents a single project in the dependency graph."""

    name: str
    path: Path
    project_type: str = "unknown"  # app, library, test, database
    dependencies: Set[str] = field(default_factory=set)  # Direct dependencies

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "path": str(self.path),
            "project_type": self.project_type,
            "dependencies": list(self.dependencies),
        }


@dataclass
class DependencyGraph:
    """Project-to-project dependency graph."""

    nodes: Dict[str, ProjectNode] = field(default_factory=dict)
    edges: List[Dict[str, str]] = field(default_factory=list)
    circular_dependencies: List[List[str]] = field(default_factory=list)
    layer_violations: List[Dict[str, str]] = field(default_factory=list)

    def add_node(self, project_name: str, path: Path, project_type: str = "unknown") -> None:
        """Add a project node to the graph."""
        if project_name not in self.nodes:
            self.nodes[project_name] = ProjectNode(
                name=project_name,
                path=path,
                project_type=project_type,
            )

    def add_edge(self, from_project: str, to_project: str) -> None:
        """Add a dependency edge from one project to another."""
        if from_project in self.nodes and to_project in self.nodes:
            self.nodes[from_project].dependencies.add(to_project)
            self.edges.append({"from": from_project, "to": to_project})

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "project_dependencies": {
                name: list(node.dependencies) for name, node in self.nodes.items()
            },
            "dependency_graph": {
                "nodes": [node.to_dict() for node in self.nodes.values()],
                "edges": self.edges,
            },
            "circular_dependencies": self.circular_dependencies,
            "layer_violations": self.layer_violations,
        }


class MSBuildProjectReferenceResolver:
    """Resolves ProjectReference elements to build dependency graphs."""

    # Architectural layers for violation detection
    LAYERS = {
        "presentation": ["ui", "web", "aspnet"],
        "service": ["service", "business", "logic"],
        "data": ["data", "database", "dal", "repository"],
        "infrastructure": ["infra", "config", "utils", "common"],
    }

    def __init__(self, solution_root: Path):
        """Initialize resolver with solution root path.

        Args:
            solution_root: Path to solution directory
        """
        self.solution_root = Path(solution_root)
        self.graph = DependencyGraph()
        self.visited = set()

    def resolve_project_references(self) -> DependencyGraph:
        """Resolve all ProjectReference elements in solution.

        Returns:
            DependencyGraph with all dependencies mapped

        Raises:
            FileNotFoundError: If solution root doesn't exist
        """
        if not self.solution_root.exists():
            raise FileNotFoundError(f"Solution root not found: {self.solution_root}")

        # Find all .csproj files
        csproj_files = list(self.solution_root.rglob("*.csproj"))

        if not csproj_files:
            logger.warning(f"No .csproj files found in {self.solution_root}")
            return self.graph

        # Build initial graph with all projects
        for csproj_path in csproj_files:
            project_name = csproj_path.stem
            project_type = self._detect_project_type(csproj_path)
            self.graph.add_node(project_name, csproj_path, project_type)

        # Parse ProjectReference elements
        for csproj_path in csproj_files:
            self._parse_project_file(csproj_path)

        # Detect issues
        self._detect_circular_dependencies()
        self._detect_layer_violations()

        return self.graph

    def _parse_project_file(self, csproj_path: Path) -> None:
        """Parse .csproj file for ProjectReference elements.

        Args:
            csproj_path: Path to .csproj file
        """
        try:
            tree = ET.parse(str(csproj_path))
            root = tree.getroot()

            project_name = csproj_path.stem

            # Find all ProjectReference elements (with and without namespace)
            # Try with namespace first, then without
            proj_refs = []

            # Try with namespace
            for proj_ref in root.findall(".//{{http://schemas.microsoft.com/developer/msbuild/2003}}ProjectReference"):
                proj_refs.append(proj_ref)

            # Try without namespace (simple .csproj files)
            if not proj_refs:
                for proj_ref in root.findall(".//ProjectReference"):
                    proj_refs.append(proj_ref)

            # Process references
            for proj_ref in proj_refs:
                include = proj_ref.get("Include", "")
                if include:
                    ref_path = self._resolve_relative_path(csproj_path, include)
                    ref_name = ref_path.stem

                    # Add dependency
                    if ref_name in self.graph.nodes:
                        self.graph.add_edge(project_name, ref_name)

        except ET.ParseError as e:
            logger.error(f"Failed to parse {csproj_path}: {e}")
        except Exception as e:
            logger.error(f"Error processing {csproj_path}: {e}")

    def _resolve_relative_path(self, csproj_path: Path, relative_include: str) -> Path:
        """Resolve relative ProjectReference path to absolute path.

        Args:
            csproj_path: Path to .csproj file containing the reference
            relative_include: Relative path from Include attribute

        Returns:
            Absolute path to referenced project
        """
        # Remove quotes if present
        relative_include = relative_include.strip('"\'')

        # Resolve relative to .csproj directory
        base_dir = csproj_path.parent
        resolved = (base_dir / relative_include).resolve()

        return resolved

    def _detect_project_type(self, csproj_path: Path) -> str:
        """Detect project type from .csproj file.

        Args:
            csproj_path: Path to .csproj file

        Returns:
            Project type: 'app', 'library', 'test', or 'unknown'
        """
        project_name = csproj_path.stem.lower()

        # Simple heuristics
        if "test" in project_name or "spec" in project_name:
            return "test"

        try:
            tree = ET.parse(str(csproj_path))
            root = tree.getroot()

            # Check OutputType
            namespace = {}
            if root.tag.startswith("{"):
                ns = root.tag.split("}")[0] + "}"
                namespace[""] = ns.strip("{}")

            output_type = root.findtext(".//{*}OutputType", "").lower()
            if output_type == "exe" or output_type == "winexe":
                return "app"
            elif output_type == "library":
                return "library"

        except Exception as e:
            logger.debug(f"Could not detect project type for {csproj_path}: {e}")

        # Default heuristic based on name
        if "app" in project_name or "console" in project_name:
            return "app"
        elif "test" in project_name:
            return "test"

        return "library"  # Default to library

    def _detect_circular_dependencies(self) -> None:
        """Detect circular dependencies in project graph."""
        for project_name in self.graph.nodes:
            visited = set()
            if self._has_cycle(project_name, visited):
                cycle = self._find_cycle_path(project_name, set(), [])
                if cycle:
                    self.graph.circular_dependencies.append(cycle)

    def _has_cycle(self, node: str, visited: Set[str]) -> bool:
        """Check if node has circular dependency.

        Args:
            node: Current project name
            visited: Set of visited nodes in current path

        Returns:
            True if cycle detected, False otherwise
        """
        if node in visited:
            return True

        if node not in self.graph.nodes:
            return False

        visited.add(node)

        for dep in self.graph.nodes[node].dependencies:
            if self._has_cycle(dep, visited.copy()):
                return True

        return False

    def _find_cycle_path(
        self, node: str, visited: Set[str], path: List[str]
    ) -> Optional[List[str]]:
        """Find the actual cycle path.

        Args:
            node: Current project name
            visited: Set of visited nodes
            path: Current path in search

        Returns:
            List representing cycle if found, None otherwise
        """
        if node in visited:
            # Found cycle - return from cycle start to current
            if node in path:
                return path[path.index(node) :] + [node]
            return None

        if node not in self.graph.nodes:
            return None

        visited.add(node)
        path.append(node)

        for dep in self.graph.nodes[node].dependencies:
            cycle = self._find_cycle_path(dep, visited.copy(), path.copy())
            if cycle:
                return cycle

        return None

    def _detect_layer_violations(self) -> None:
        """Detect architectural layer violations.

        Layer hierarchy: Infrastructure → Data → Service → Presentation
        Violations occur when higher layers depend on lower layers.
        """
        layer_map = {}

        # Map each project to its layer
        for project_name in self.graph.nodes:
            layer_map[project_name] = self._detect_project_layer(project_name)

        # Check for violations
        for from_project, from_layer in layer_map.items():
            for to_project in self.graph.nodes[from_project].dependencies:
                to_layer = layer_map.get(to_project)
                if to_layer and self._is_layer_violation(from_layer, to_layer):
                    self.graph.layer_violations.append(
                        {
                            "from": from_project,
                            "from_layer": from_layer,
                            "to": to_project,
                            "to_layer": to_layer,
                            "violation": f"{from_layer} depends on {to_layer}",
                        }
                    )

    def _detect_project_layer(self, project_name: str) -> Optional[str]:
        """Detect architectural layer of a project.

        Args:
            project_name: Name of project

        Returns:
            Layer name or None if unable to detect
        """
        project_lower = project_name.lower()

        for layer, keywords in self.LAYERS.items():
            for keyword in keywords:
                if keyword in project_lower:
                    return layer

        return None

    def _is_layer_violation(self, from_layer: Optional[str], to_layer: Optional[str]) -> bool:
        """Check if dependency represents a layer violation.

        Args:
            from_layer: Source layer
            to_layer: Target layer

        Returns:
            True if dependency violates layer hierarchy
        """
        if not from_layer or not to_layer or from_layer == to_layer:
            return False

        layer_order = ["presentation", "service", "data", "infrastructure"]

        try:
            from_idx = layer_order.index(from_layer)
            to_idx = layer_order.index(to_layer)
            # Violation: higher layer depends on lower layer
            return from_idx < to_idx
        except ValueError:
            return False
