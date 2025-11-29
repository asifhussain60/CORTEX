"""
Dependency Mapper for CORTEX Entry Point Modules

Analyzes import relationships and dependencies between Python modules
to create dependency graphs and relationship maps for documentation.

Features:
- Import relationship extraction
- Circular dependency detection
- External vs internal dependency classification
- Dependency graph generation
- Module coupling analysis
"""

import ast
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque

from .parser import EPMASTParser, EPMAnalysis


@dataclass
class DependencyRelationship:
    """Represents a dependency between two modules."""
    source_module: str
    target_module: str
    import_type: str  # 'direct', 'from', 'relative'
    line_number: int
    is_external: bool = False
    is_relative: bool = False


@dataclass
class ModuleDependencies:
    """Complete dependency information for a module."""
    module_path: str
    internal_dependencies: List[str] = field(default_factory=list)
    external_dependencies: List[str] = field(default_factory=list)
    imported_by: List[str] = field(default_factory=list)  # Reverse dependencies
    circular_dependencies: List[str] = field(default_factory=list)
    coupling_score: float = 0.0


@dataclass
class DependencyGraph:
    """Complete dependency graph for an EPMO."""
    epmo_path: str
    modules: Dict[str, ModuleDependencies] = field(default_factory=dict)
    relationships: List[DependencyRelationship] = field(default_factory=list)
    circular_chains: List[List[str]] = field(default_factory=list)
    external_packages: Set[str] = field(default_factory=set)
    dependency_layers: List[List[str]] = field(default_factory=list)  # Topologically sorted layers


class DependencyMapper:
    """
    Analyzes and maps dependencies between Python modules in an EPMO.
    
    Creates dependency graphs, detects circular dependencies, and provides
    relationship analysis for documentation generation.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ast_parser = EPMASTParser()
        self.stdlib_modules = self._get_stdlib_modules()
    
    def analyze_dependencies(self, epmo_path: Path) -> DependencyGraph:
        """
        Analyze all dependencies within an Entry Point Module.
        
        Args:
            epmo_path: Path to the Entry Point Module directory
            
        Returns:
            DependencyGraph containing complete dependency analysis
        """
        # Parse all Python files in the EPMO
        analyses = self.ast_parser.parse_epmo(epmo_path)
        
        # Create dependency graph
        graph = DependencyGraph(epmo_path=str(epmo_path))
        
        # Extract all relationships
        for analysis in analyses:
            self._extract_module_dependencies(analysis, epmo_path, graph)
        
        # Calculate reverse dependencies (imported_by)
        self._calculate_reverse_dependencies(graph)
        
        # Detect circular dependencies
        self._detect_circular_dependencies(graph)
        
        # Calculate coupling scores
        self._calculate_coupling_scores(graph)
        
        # Determine dependency layers (topological sort)
        self._calculate_dependency_layers(graph)
        
        return graph
    
    def _extract_module_dependencies(
        self, 
        analysis: EPMAnalysis, 
        epmo_path: Path, 
        graph: DependencyGraph
    ) -> None:
        """Extract dependencies from a single module analysis."""
        module_path = str(analysis.file_path)
        relative_path = analysis.file_path.relative_to(epmo_path)
        module_name = str(relative_path).replace('/', '.').replace('.py', '')
        
        # Initialize module dependencies
        if module_name not in graph.modules:
            graph.modules[module_name] = ModuleDependencies(module_path=module_path)
        
        module_deps = graph.modules[module_name]
        
        # Process each import
        for import_info in analysis.imports:
            dependency = self._process_import(
                import_info, module_name, epmo_path, analysis.file_path
            )
            
            if dependency:
                graph.relationships.append(dependency)
                
                if dependency.is_external:
                    module_deps.external_dependencies.append(dependency.target_module)
                    graph.external_packages.add(dependency.target_module.split('.')[0])
                else:
                    module_deps.internal_dependencies.append(dependency.target_module)
    
    def _process_import(
        self, 
        import_info, 
        source_module: str, 
        epmo_path: Path, 
        source_file: Path
    ) -> Optional[DependencyRelationship]:
        """Process a single import statement."""
        if import_info.is_from_import:
            target_module = import_info.module
            import_type = 'from'
        else:
            target_module = import_info.module
            import_type = 'direct'
        
        if not target_module:  # Relative import without module
            return None
        
        # Determine if import is relative
        is_relative = target_module.startswith('.')
        
        # Resolve relative imports
        if is_relative:
            resolved_module = self._resolve_relative_import(
                target_module, source_file, epmo_path
            )
            if resolved_module:
                target_module = resolved_module
            else:
                return None
        
        # Determine if import is external
        is_external = self._is_external_import(target_module, epmo_path)
        
        return DependencyRelationship(
            source_module=source_module,
            target_module=target_module,
            import_type=import_type,
            line_number=import_info.line_number,
            is_external=is_external,
            is_relative=is_relative
        )
    
    def _resolve_relative_import(
        self, 
        import_module: str, 
        source_file: Path, 
        epmo_path: Path
    ) -> Optional[str]:
        """Resolve relative import to absolute module name."""
        try:
            # Count leading dots
            dots = len(import_module) - len(import_module.lstrip('.'))
            module_part = import_module[dots:]
            
            # Get source module path relative to EPMO
            source_relative = source_file.relative_to(epmo_path)
            source_parts = source_relative.parts[:-1]  # Remove filename
            
            # Navigate up the directory tree based on dots
            if dots > len(source_parts):
                return None
            
            target_parts = source_parts[:-dots+1] if dots > 1 else source_parts
            
            if module_part:
                target_parts = target_parts + tuple(module_part.split('.'))
            
            return '.'.join(target_parts)
            
        except Exception:
            return None
    
    def _is_external_import(self, module_name: str, epmo_path: Path) -> bool:
        """Determine if an import is external to the EPMO."""
        # Check if it's a standard library module
        if module_name.split('.')[0] in self.stdlib_modules:
            return True
        
        # Check if it exists within the EPMO
        module_path = epmo_path / f"{module_name.replace('.', '/')}.py"
        if module_path.exists():
            return False
        
        # Check if it's a package within the EPMO
        package_path = epmo_path / module_name.replace('.', '/') / "__init__.py"
        if package_path.exists():
            return False
        
        # Check if it's within the project root but outside EPMO
        project_module_path = self.project_root / f"{module_name.replace('.', '/')}.py"
        if project_module_path.exists():
            return False
        
        # Assume external if not found in project
        return True
    
    def _calculate_reverse_dependencies(self, graph: DependencyGraph) -> None:
        """Calculate which modules import each module (reverse dependencies)."""
        for relationship in graph.relationships:
            if not relationship.is_external:
                target = relationship.target_module
                source = relationship.source_module
                
                if target in graph.modules:
                    if source not in graph.modules[target].imported_by:
                        graph.modules[target].imported_by.append(source)
    
    def _detect_circular_dependencies(self, graph: DependencyGraph) -> None:
        """Detect circular dependency chains."""
        # Build adjacency list for internal dependencies only
        adj_list = defaultdict(list)
        for relationship in graph.relationships:
            if not relationship.is_external:
                adj_list[relationship.source_module].append(relationship.target_module)
        
        # Find strongly connected components (circular chains)
        visited = set()
        rec_stack = set()
        
        def dfs_cycle_detect(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Found a cycle - extract the cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                graph.circular_chains.append(cycle)
                
                # Mark all nodes in cycle as having circular dependencies
                for cycle_node in cycle[:-1]:  # Exclude duplicate end node
                    if cycle_node in graph.modules:
                        graph.modules[cycle_node].circular_dependencies.extend(
                            [n for n in cycle[:-1] if n != cycle_node]
                        )
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in adj_list[node]:
                dfs_cycle_detect(neighbor, path)
            
            path.pop()
            rec_stack.remove(node)
        
        # Check all nodes for cycles
        for module in graph.modules:
            if module not in visited:
                dfs_cycle_detect(module, [])
    
    def _calculate_coupling_scores(self, graph: DependencyGraph) -> None:
        """Calculate coupling scores for each module."""
        for module_name, module_deps in graph.modules.items():
            # Afferent coupling (incoming dependencies)
            afferent = len(module_deps.imported_by)
            
            # Efferent coupling (outgoing dependencies) 
            efferent = len(module_deps.internal_dependencies)
            
            # Calculate instability metric (I = Ce / (Ca + Ce))
            total_coupling = afferent + efferent
            if total_coupling > 0:
                instability = efferent / total_coupling
                # Convert to coupling score (lower is better)
                module_deps.coupling_score = instability
            else:
                module_deps.coupling_score = 0.0
    
    def _calculate_dependency_layers(self, graph: DependencyGraph) -> None:
        """Calculate dependency layers using topological sorting."""
        # Build adjacency list for internal dependencies only
        adj_list = defaultdict(list)
        in_degree = defaultdict(int)
        
        # Initialize all modules with in-degree 0
        for module in graph.modules:
            in_degree[module] = 0
        
        # Count incoming edges
        for relationship in graph.relationships:
            if not relationship.is_external:
                source = relationship.source_module
                target = relationship.target_module
                if target in graph.modules:  # Only count internal targets
                    adj_list[source].append(target)
                    in_degree[target] += 1
        
        # Topological sort by layers
        current_layer = []
        remaining_modules = set(graph.modules.keys())
        
        while remaining_modules:
            # Find modules with no incoming dependencies in this iteration
            layer_modules = [
                module for module in remaining_modules 
                if in_degree[module] == 0
            ]
            
            if not layer_modules:
                # If no modules with in-degree 0, we have cycles
                # Add remaining modules to final layer
                graph.dependency_layers.append(list(remaining_modules))
                break
            
            # Add this layer
            graph.dependency_layers.append(layer_modules)
            
            # Remove these modules and update in-degrees
            for module in layer_modules:
                remaining_modules.remove(module)
                for neighbor in adj_list[module]:
                    if neighbor in remaining_modules:
                        in_degree[neighbor] -= 1
    
    def _get_stdlib_modules(self) -> Set[str]:
        """Get set of Python standard library module names."""
        # This is a simplified list - in production, you might want to use
        # a more comprehensive approach like stdlib-list package
        return {
            'os', 'sys', 'json', 'ast', 'pathlib', 'typing', 'dataclasses',
            'collections', 'itertools', 'functools', 'operator', 'copy',
            'datetime', 'time', 're', 'math', 'random', 'string', 'io',
            'csv', 'sqlite3', 'pickle', 'base64', 'hashlib', 'uuid',
            'urllib', 'http', 'email', 'xml', 'html', 'logging',
            'unittest', 'pytest', 'argparse', 'configparser', 'shutil',
            'glob', 'fnmatch', 'tempfile', 'gzip', 'zipfile', 'tarfile'
        }


def analyze_epmo_dependencies(epmo_path: Path, project_root: Path = None) -> Dict[str, Any]:
    """
    Convenience function to analyze EPMO dependencies and return structured data.
    
    Args:
        epmo_path: Path to the Entry Point Module directory
        project_root: Root path of the project (defaults to current directory)
        
    Returns:
        Dictionary containing dependency analysis in JSON-serializable format
    """
    if project_root is None:
        project_root = Path('.')
    
    mapper = DependencyMapper(project_root)
    graph = mapper.analyze_dependencies(epmo_path)
    
    # Convert to serializable format
    result = {
        'epmo_path': graph.epmo_path,
        'total_modules': len(graph.modules),
        'total_relationships': len(graph.relationships),
        'external_packages': sorted(graph.external_packages),
        'circular_dependency_chains': graph.circular_chains,
        'dependency_layers': graph.dependency_layers,
        'modules': {}
    }
    
    # Add module information
    for module_name, deps in graph.modules.items():
        result['modules'][module_name] = {
            'module_path': deps.module_path,
            'internal_dependencies': deps.internal_dependencies,
            'external_dependencies': deps.external_dependencies,
            'imported_by': deps.imported_by,
            'circular_dependencies': deps.circular_dependencies,
            'coupling_score': round(deps.coupling_score, 3)
        }
    
    # Add relationship details
    result['relationships'] = [
        {
            'source': rel.source_module,
            'target': rel.target_module,
            'type': rel.import_type,
            'line_number': rel.line_number,
            'is_external': rel.is_external,
            'is_relative': rel.is_relative
        }
        for rel in graph.relationships
    ]
    
    return result