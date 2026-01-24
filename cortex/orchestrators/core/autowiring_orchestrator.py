"""
Declarative Autowiring Orchestrator.

AC-ID: AC-AR-AUTOWIRING-001
Purpose: Git-safe orchestrator wiring via YAML specs (CORE-031 compliance)

Discovers *_wiring.yaml specs and validates dependency graphs at startup.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import yaml

from cortex.core.result import Err, Ok, Result


class WiringSpec:
    """Represents a parsed orchestrator wiring specification."""

    def __init__(self, data: Dict[str, Any], source_path: Path) -> None:
        """
        Initialize wiring spec from parsed YAML data.

        Args:
            data: Parsed YAML content
            source_path: Path to the source YAML file
        """
        self.module_name: str = data.get("module_name", "")
        self.version: str = data.get("version", "1.0.0")
        self.dependencies: List[Dict[str, Any]] = data.get("dependencies", [])
        self.provides: List[Dict[str, Any]] = data.get("provides", [])
        self.entry_points: List[Dict[str, Any]] = data.get("entry_points", [])
        self.initialization_order: int = data.get("initialization_order", 1000)
        self.conflict_resolution: Dict[str, str] = data.get("conflict_resolution", {})
        self.source_path: Path = source_path

    def get_dependency_names(self) -> Set[str]:
        """
        Extract dependency module names.

        Returns:
            Set of dependency module names
        """
        return {dep.get("name", "") for dep in self.dependencies if dep.get("required", True)}


class AutowiringOrchestrator:
    """
    Discovers and validates declarative orchestrator wiring.

    Implements CORE-031: Declarative Autowiring Registry.
    Makes orchestrator wiring Git-safe by using YAML specs instead of
    imperative Python registration code.
    """

    def __init__(self, orchestrators_root: Optional[Path] = None) -> None:
        """
        Initialize autowiring orchestrator.

        Args:
            orchestrators_root: Root path for orchestrator discovery.
                              Defaults to cortex/orchestrators/
        """
        if orchestrators_root is None:
            orchestrators_root = Path(__file__).parent.parent
        self.orchestrators_root = orchestrators_root
        self._specs: Dict[str, WiringSpec] = {}
        self._validated: bool = False

    def discover_wiring_specs(self) -> Union[Ok[Dict[str, WiringSpec]], Err[str]]:
        """
        Discover all *_wiring.yaml files in orchestrators directory.

        Returns:
            Result containing dict of module_name -> WiringSpec
        """
        specs: Dict[str, WiringSpec] = {}
        wiring_files = list(self.orchestrators_root.rglob("*_wiring.yaml"))

        for wiring_file in wiring_files:
            try:
                with open(wiring_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                if data is None:
                    continue

                spec = WiringSpec(data, wiring_file)
                if spec.module_name:
                    specs[spec.module_name] = spec

            except yaml.YAMLError as e:
                return Err(f"Invalid YAML in {wiring_file}: {e}")
            except OSError as e:
                return Err(f"Failed to read {wiring_file}: {e}")

        self._specs = specs
        return Ok(specs)

    def validate_dependency_graph(
        self, specs: Optional[Dict[str, WiringSpec]] = None
    ) -> Union[Ok[List[str]], Err[str]]:
        """
        Validate dependency graph for cycles and missing dependencies.

        Args:
            specs: Wiring specs to validate. Uses discovered specs if None.

        Returns:
            Result containing topologically sorted module names
        """
        if specs is None:
            specs = self._specs

        if not specs:
            return Ok([])

        # Build dependency graph
        graph: Dict[str, Set[str]] = {}
        for name, spec in specs.items():
            graph[name] = spec.get_dependency_names()

        # Check for missing dependencies
        all_modules = set(specs.keys())
        for name, deps in graph.items():
            missing = deps - all_modules
            # Allow external dependencies (not in our specs)
            # Only flag if dependency is marked as internal
            for dep_name in missing:
                dep_spec = next(
                    (d for d in specs[name].dependencies if d.get("name") == dep_name),
                    None,
                )
                if dep_spec and dep_spec.get("internal", False):
                    return Err(f"Module '{name}' has missing internal dependency: '{dep_name}'")

        # Topological sort with cycle detection
        sorted_modules: List[str] = []
        visited: Set[str] = set()
        in_stack: Set[str] = set()

        def visit(node: str) -> Optional[str]:
            if node in in_stack:
                return f"Circular dependency detected involving '{node}'"
            if node in visited:
                return None

            in_stack.add(node)
            for dep in graph.get(node, set()):
                if dep in specs:  # Only visit internal dependencies
                    error = visit(dep)
                    if error:
                        return error
            in_stack.remove(node)
            visited.add(node)
            sorted_modules.append(node)
            return None

        for module in specs:
            error = visit(module)
            if error:
                return Err(error)

        self._validated = True
        return Ok(sorted_modules)

    def resolve_dependencies(self) -> Union[Ok[List[WiringSpec]], Err[str]]:
        """
        Resolve and sort dependencies for initialization order.

        Returns:
            Result containing specs sorted by initialization order
        """
        if not self._specs:
            discovery_result = self.discover_wiring_specs()
            if not discovery_result.is_ok():
                return Err(discovery_result.error)

        validation_result = self.validate_dependency_graph()
        if not validation_result.is_ok():
            return Err(validation_result.error)

        # Sort by initialization_order, then by topological order
        topo_order = validation_result.unwrap()
        topo_index = {name: i for i, name in enumerate(topo_order)}

        sorted_specs = sorted(
            self._specs.values(),
            key=lambda s: (s.initialization_order, topo_index.get(s.module_name, 999)),
        )

        return Ok(sorted_specs)

    def validate(self) -> Union[Ok[bool], Err[str]]:
        """
        Full validation of autowiring configuration.

        Returns:
            Result[True] if validation passes
        """
        discovery_result = self.discover_wiring_specs()
        if not discovery_result.is_ok():
            return Err(discovery_result.error)

        validation_result = self.validate_dependency_graph()
        if not validation_result.is_ok():
            return Err(validation_result.error)

        return Ok(True)

    def query_wiring_state(self) -> Dict[str, Any]:
        """
        Expose wiring state for inspection.

        Returns:
            Dict with wiring state information
        """
        return {
            "discovered_specs": len(self._specs),
            "validated": self._validated,
            "modules": list(self._specs.keys()),
            "orchestrators_root": str(self.orchestrators_root),
        }

    def get_missing_wiring_specs(self) -> Union[Ok[List[Path]], Err[str]]:
        """
        Find orchestrator Python files without corresponding wiring specs.

        Returns:
            Result containing list of paths missing wiring specs
        """
        missing: List[Path] = []

        # Find all orchestrator Python files
        py_files = list(self.orchestrators_root.rglob("*_orchestrator.py"))
        py_files.extend(self.orchestrators_root.rglob("*Orchestrator.py"))

        for py_file in py_files:
            if "__pycache__" in str(py_file):
                continue

            # Expected wiring file
            expected_wiring = py_file.with_name(
                py_file.stem.replace("_orchestrator", "").replace("Orchestrator", "")
                + "_wiring.yaml"
            )

            if not expected_wiring.exists():
                # Also check for exact name match
                alt_wiring = py_file.with_suffix(".yaml").with_name(
                    py_file.stem + "_wiring.yaml"
                )
                if not alt_wiring.exists():
                    missing.append(py_file)

        return Ok(missing)
