"""
BrittlenessScanner - Layer 2 Runtime Regression Guard

Detects architectural brittleness patterns:
- Circular dependencies
- Tight coupling violations
- Anti-patterns (God objects, feature envy, etc.)

Author: Asif Hussain
Phase: 24.2
TDD: GREEN phase - make tests pass

Usage:
    scanner = BrittlenessScanner()
    result = scanner.scan("/path/to/codebase")
    
    if result.has_violations():
        print(f"Brittleness score: {result.brittleness_score}")
        for cycle in result.circular_dependencies:
            print(f"Circular: {cycle.cycle_path}")
"""
import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


@dataclass
class CircularDependencyViolation:
    """Represents a circular dependency cycle"""
    cycle_path: List[str]  # e.g., ["module_a", "module_b", "module_a"]
    severity: str  # "HIGH", "MEDIUM", "LOW"
    description: str
    
    def __str__(self) -> str:
        return f"Circular: {' → '.join(self.cycle_path)} ({self.severity})"


@dataclass
class CouplingViolation:
    """Represents tight coupling between modules"""
    module_name: str
    fan_in: int  # Number of modules importing this module
    fan_out: int  # Number of modules this module imports
    coupling_score: float  # 0-1.0
    severity: str  # "HIGH", "MEDIUM", "LOW"
    description: str
    
    def __str__(self) -> str:
        return f"{self.module_name}: fan-in={self.fan_in}, fan-out={self.fan_out} ({self.severity})"


@dataclass
class AntiPatternViolation:
    """Represents an anti-pattern detection"""
    pattern_name: str  # "GodObject", "FeatureEnvy", etc.
    location: str  # File path
    severity: str  # "HIGH", "MEDIUM", "LOW"
    description: str
    method_count: Optional[int] = None
    complexity: Optional[int] = None
    
    def __str__(self) -> str:
        return f"{self.pattern_name} in {self.location}: {self.description} ({self.severity})"


@dataclass
class BrittlenessReport:
    """Overall brittleness scan report"""
    brittleness_score: float  # 0-1.0 (0=solid, 1=extremely brittle)
    circular_dependencies: List[CircularDependencyViolation] = field(default_factory=list)
    coupling_violations: List[CouplingViolation] = field(default_factory=list)
    anti_pattern_violations: List[AntiPatternViolation] = field(default_factory=list)
    scan_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    scanned_path: str = ""
    
    def has_violations(self) -> bool:
        """Returns True if any violations detected"""
        return (
            len(self.circular_dependencies) > 0
            or len(self.coupling_violations) > 0
            or len(self.anti_pattern_violations) > 0
        )
    
    def has_circular_dependencies(self) -> bool:
        """Returns True if circular dependencies detected"""
        return len(self.circular_dependencies) > 0


class BrittlenessScanner:
    """
    Scans Python codebase for architectural brittleness patterns.
    
    Detection algorithms:
    - Circular dependencies: DFS graph traversal
    - Coupling: Fan-in/fan-out analysis
    - Anti-patterns: AST-based heuristics
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Thresholds
        self.god_object_method_threshold = 10
        self.high_coupling_threshold = 2  # Lower threshold to catch module_a/module_b
        self.circular_dep_severity = "HIGH"
    
    def scan(self, path: str) -> BrittlenessReport:
        """
        Scan codebase at given path for brittleness patterns.
        
        Args:
            path: Path to Python codebase (file or directory)
        
        Returns:
            BrittlenessReport with violations and brittleness score
        """
        path_obj = Path(path)
        
        if not path_obj.exists():
            self.logger.warning(f"Path does not exist: {path}")
            return BrittlenessReport(
                brittleness_score=0.0,
                scanned_path=path
            )
        
        # Collect Python files
        python_files = self._collect_python_files(path_obj)
        
        if not python_files:
            return BrittlenessReport(
                brittleness_score=0.0,
                scanned_path=path
            )
        
        # Build dependency graph
        dependency_graph = self._build_dependency_graph(python_files)
        
        # Detect violations
        circular_deps = self._detect_circular_dependencies(dependency_graph)
        coupling_violations = self._detect_tight_coupling(dependency_graph)
        anti_patterns = self._detect_anti_patterns(python_files)
        
        # Calculate brittleness score
        brittleness_score = self._calculate_brittleness_score(
            circular_deps, coupling_violations, anti_patterns
        )
        
        return BrittlenessReport(
            brittleness_score=brittleness_score,
            circular_dependencies=circular_deps,
            coupling_violations=coupling_violations,
            anti_pattern_violations=anti_patterns,
            scanned_path=path
        )
    
    def _collect_python_files(self, path: Path) -> List[Path]:
        """Collect all Python files from path"""
        if path.is_file() and path.suffix == ".py":
            return [path]
        elif path.is_dir():
            return list(path.rglob("*.py"))
        return []
    
    def _build_dependency_graph(self, files: List[Path]) -> Dict[str, Set[str]]:
        """
        Build module dependency graph.
        
        Returns:
            Dict mapping module name to set of imported modules
        """
        graph: Dict[str, Set[str]] = {}
        
        for file_path in files:
            module_name = file_path.stem
            imports = self._extract_imports(file_path)
            graph[module_name] = imports
        
        return graph
    
    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Extract imported module names from Python file"""
        imports: Set[str] = set()
        
        try:
            content = file_path.read_text()
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except Exception as e:
            self.logger.warning(f"Failed to parse {file_path}: {e}")
        
        return imports
    
    def _detect_circular_dependencies(
        self, graph: Dict[str, Set[str]]
    ) -> List[CircularDependencyViolation]:
        """
        Detect circular dependencies using DFS.
        
        Algorithm: For each node, run DFS. If we revisit a node in the current path,
        we have a cycle.
        """
        violations = []
        visited = set()
        
        def dfs(node: str, path: List[str]) -> None:
            if node in path:
                # Cycle detected - extract cycle path
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                
                # Avoid duplicate cycles (e.g., A→B→A and B→A→B are same)
                cycle_key = tuple(sorted(cycle[:-1]))  # Exclude last duplicate node
                if cycle_key not in visited:
                    visited.add(cycle_key)
                    violations.append(CircularDependencyViolation(
                        cycle_path=cycle,
                        severity=self.circular_dep_severity,
                        description=f"Circular dependency detected: {' → '.join(cycle)}"
                    ))
                return
            
            path.append(node)
            for neighbor in graph.get(node, set()):
                if neighbor in graph:  # Only follow if neighbor is in our codebase
                    dfs(neighbor, path.copy())
        
        for node in graph:
            dfs(node, [])
        
        return violations
    
    def _detect_tight_coupling(
        self, graph: Dict[str, Set[str]]
    ) -> List[CouplingViolation]:
        """
        Detect tight coupling using fan-in/fan-out metrics.
        
        High coupling: fan-in + fan-out > threshold
        """
        violations = []
        
        # Calculate fan-in (how many modules import this module)
        fan_in: Dict[str, int] = {module: 0 for module in graph}
        for module, imports in graph.items():
            for imported in imports:
                if imported in fan_in:
                    fan_in[imported] += 1
        
        # Calculate fan-out (how many modules this module imports)
        fan_out: Dict[str, int] = {
            module: len(imports & graph.keys())  # Only count internal imports
            for module, imports in graph.items()
        }
        
        # Detect violations
        for module in graph:
            total_coupling = fan_in[module] + fan_out[module]
            coupling_score = min(total_coupling / 10.0, 1.0)  # Normalize to 0-1
            
            if total_coupling >= self.high_coupling_threshold:
                severity = "HIGH" if total_coupling >= 8 else "MEDIUM"
                violations.append(CouplingViolation(
                    module_name=module,
                    fan_in=fan_in[module],
                    fan_out=fan_out[module],
                    coupling_score=coupling_score,
                    severity=severity,
                    description=f"High coupling detected (fan-in={fan_in[module]}, fan-out={fan_out[module]})"
                ))
        
        return violations
    
    def _detect_anti_patterns(self, files: List[Path]) -> List[AntiPatternViolation]:
        """Detect anti-patterns using AST analysis"""
        violations = []
        
        for file_path in files:
            try:
                content = file_path.read_text()
                tree = ast.parse(content, filename=str(file_path))
                
                # Detect God Objects (classes with >10 methods)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        methods = [
                            n for n in node.body
                            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                        ]
                        method_count = len(methods)
                        
                        if method_count > self.god_object_method_threshold:
                            violations.append(AntiPatternViolation(
                                pattern_name="GodObject",
                                location=str(file_path),
                                severity="HIGH",
                                description=f"Class {node.name} has {method_count} methods (threshold: {self.god_object_method_threshold})",
                                method_count=method_count
                            ))
            except Exception as e:
                self.logger.warning(f"Failed to analyze {file_path}: {e}")
        
        return violations
    
    def _calculate_brittleness_score(
        self,
        circular_deps: List[CircularDependencyViolation],
        coupling_violations: List[CouplingViolation],
        anti_patterns: List[AntiPatternViolation]
    ) -> float:
        """
        Calculate overall brittleness score (0-1.0).
        
        Formula:
            score = 0.5 * circular_weight + 0.3 * coupling_weight + 0.3 * anti_pattern_weight
        
        Where:
            - circular_weight = min(num_circular_deps / 2, 1.0)
            - coupling_weight = min(num_high_coupling / 3, 1.0)
            - anti_pattern_weight = min(num_anti_patterns / 3, 1.0)
        """
        circular_weight = min(len(circular_deps) / 2.0, 1.0)
        coupling_weight = min(len(coupling_violations) / 3.0, 1.0)
        anti_pattern_weight = min(len(anti_patterns) / 3.0, 1.0)
        
        score = (
            0.5 * circular_weight +
            0.3 * coupling_weight +
            0.3 * anti_pattern_weight
        )
        
        return round(score, 2)
