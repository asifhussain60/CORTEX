"""
ArchitectureGraphBuilder - Multi-language dependency graph generation.

Generates D3.js-compatible node/edge graph data for architecture visualization.
Supports Python, JavaScript, TypeScript, and C# import detection.

Performance Target: <1s for 50K files, ≥90% import accuracy

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ModuleNode:
    """Represents a module/file in the dependency graph."""
    id: str  # Unique identifier (relative path)
    label: str  # Display name
    type: str  # 'module', 'package', 'file'
    loc: int  # Lines of code
    file_path: str  # Full file path
    language: str  # python, javascript, typescript, csharp


@dataclass
class DependencyEdge:
    """Represents an import/dependency relationship."""
    source: str  # Source module ID
    target: str  # Target module ID
    weight: int  # Number of imports from source to target


class ArchitectureGraphBuilder:
    """
    Build dependency graphs for repository architecture visualization.
    
    Analyzes source code to extract import relationships and generate
    D3.js force-directed graph data (nodes and edges).
    """
    
    def __init__(self):
        """Initialize ArchitectureGraphBuilder."""
        self.nodes: Dict[str, ModuleNode] = {}
        self.edges: Dict[tuple, int] = defaultdict(int)  # (source, target) -> weight
        
        # Language extensions
        self.language_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.cs': 'csharp',
        }
        
        # Standard library modules to exclude
        self.python_stdlib = {
            'os', 'sys', 'pathlib', 'typing', 'dataclasses', 'json', 'yaml',
            're', 'time', 'datetime', 'collections', 'itertools', 'functools',
            'logging', 'unittest', 'pytest', 'sqlite3', 'asyncio', 'threading',
            'subprocess', 'shutil', 'tempfile', 'argparse', 'configparser',
        }
    
    def build_graph(self, repo_path: str, file_extensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Build dependency graph for repository.
        
        Args:
            repo_path: Root path of repository to analyze
            file_extensions: Optional list of extensions to include (e.g., ['.py', '.js'])
        
        Returns:
            Dictionary with structure:
            {
                "nodes": [
                    {"id": "src/auth", "label": "auth", "type": "module", "loc": 500, "language": "python"},
                    {"id": "src/user", "label": "user", "type": "module", "loc": 300, "language": "python"}
                ],
                "edges": [
                    {"source": "src/auth", "target": "src/user", "weight": 5}
                ]
            }
        """
        repo = Path(repo_path)
        
        if not repo.exists():
            return {"nodes": [], "edges": [], "error": "Repository path does not exist"}
        
        # Reset state
        self.nodes = {}
        self.edges = defaultdict(int)
        
        # Determine extensions to scan
        if file_extensions is None:
            extensions = list(self.language_extensions.keys())
        else:
            extensions = file_extensions
        
        # Scan repository for source files
        source_files = []
        for ext in extensions:
            source_files.extend(repo.rglob(f'*{ext}'))
        
        # Filter out common exclusion patterns
        source_files = self._filter_files(source_files, repo)
        
        # Phase 1: Build nodes (analyze each file for metadata)
        for file_path in source_files:
            self._add_node(file_path, repo)
        
        # Phase 2: Build edges (extract import relationships)
        for file_path in source_files:
            self._extract_dependencies(file_path, repo)
        
        # Convert to D3.js format
        return self._to_d3_format()
    
    def _filter_files(self, files: List[Path], repo_root: Path) -> List[Path]:
        """Filter out excluded directories and files."""
        exclusions = {
            'node_modules', 'venv', '.venv', 'env', '__pycache__', '.git',
            'dist', 'build', '.pytest_cache', '.mypy_cache', 'coverage',
            'cortex-brain/archives', 'cortex-brain/cache', '.vs', 'bin', 'obj'
        }
        
        filtered = []
        for file_path in files:
            # Check if any part of the path contains exclusion patterns
            relative = file_path.relative_to(repo_root)
            parts = set(relative.parts)
            
            if not parts.intersection(exclusions):
                filtered.append(file_path)
        
        return filtered
    
    def _add_node(self, file_path: Path, repo_root: Path) -> None:
        """Add a node for the given file."""
        try:
            relative_path = file_path.relative_to(repo_root)
            node_id = str(relative_path).replace('\\', '/')
            
            label = file_path.stem
            
            # Determine language
            language = self.language_extensions.get(file_path.suffix, 'unknown')
            
            # Count lines of code
            loc = self._count_loc(file_path)
            
            node = ModuleNode(
                id=node_id,
                label=label,
                type='module',
                loc=loc,
                file_path=str(file_path),
                language=language
            )
            
            self.nodes[node_id] = node
            
        except Exception:
            # Skip files that can't be processed
            pass
    
    def _count_loc(self, file_path: Path) -> int:
        """Count non-empty, non-comment lines of code."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Simple LOC count (non-empty lines)
            loc = sum(1 for line in lines if line.strip())
            return loc
            
        except Exception:
            return 0
    
    def _extract_dependencies(self, file_path: Path, repo_root: Path) -> None:
        """Extract import dependencies from a file."""
        language = self.language_extensions.get(file_path.suffix, 'unknown')
        
        if language == 'python':
            self._extract_python_imports(file_path, repo_root)
        elif language in ('javascript', 'typescript'):
            self._extract_js_imports(file_path, repo_root)
        elif language == 'csharp':
            self._extract_csharp_usings(file_path, repo_root)
    
    def _extract_python_imports(self, file_path: Path, repo_root: Path) -> None:
        """Extract Python import statements using AST."""
        try:
            source = file_path.read_text(encoding='utf-8')
            tree = ast.parse(source)
            
            source_id = str(file_path.relative_to(repo_root)).replace('\\', '/')
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._add_edge_if_internal(source_id, alias.name, repo_root)
                
                elif isinstance(node, ast.ImportFrom):
                    # from module import name
                    if node.module:
                        self._add_edge_if_internal(source_id, node.module, repo_root)
        
        except Exception:
            # Skip files with syntax errors
            pass
    
    def _extract_js_imports(self, file_path: Path, repo_root: Path) -> None:
        """Extract JavaScript/TypeScript import statements using regex."""
        try:
            source = file_path.read_text(encoding='utf-8')
            source_id = str(file_path.relative_to(repo_root)).replace('\\', '/')
            
            # ES6 imports: import ... from 'module'
            import_pattern = re.compile(
                r"import\s+(?:[\w\s{},*]+\s+from\s+)?['\"]([^'\"]+)['\"]",
                re.MULTILINE
            )
            
            # CommonJS requires: require('module')
            require_pattern = re.compile(
                r"require\(['\"]([^'\"]+)['\"]\)",
                re.MULTILINE
            )
            
            # Extract all imports
            imports = import_pattern.findall(source)
            requires = require_pattern.findall(source)
            
            all_imports = set(imports + requires)
            
            for imported_module in all_imports:
                self._add_edge_if_internal_js(source_id, imported_module, file_path, repo_root)
        
        except Exception:
            pass
    
    def _extract_csharp_usings(self, file_path: Path, repo_root: Path) -> None:
        """Extract C# using directives using regex."""
        try:
            source = file_path.read_text(encoding='utf-8')
            source_id = str(file_path.relative_to(repo_root)).replace('\\', '/')
            
            # using Namespace.Module;
            using_pattern = re.compile(
                r"using\s+([\w\.]+)\s*;",
                re.MULTILINE
            )
            
            usings = using_pattern.findall(source)
            
            for using_module in usings:
                # Only track internal project usings (heuristic: not System.*)
                if not using_module.startswith('System'):
                    self._add_edge_if_internal_csharp(source_id, using_module, repo_root)
        
        except Exception:
            pass
    
    def _add_edge_if_internal(self, source_id: str, import_name: str, repo_root: Path) -> None:
        """Add edge if import refers to internal module (Python)."""
        # Skip standard library
        top_level = import_name.split('.')[0]
        if top_level in self.python_stdlib:
            return
        
        # Try to resolve import to a file in the repository
        target_id = self._resolve_python_import(import_name, repo_root)
        
        if target_id and target_id in self.nodes:
            # Add edge (increment weight if already exists)
            self.edges[(source_id, target_id)] += 1
    
    def _resolve_python_import(self, import_name: str, repo_root: Path) -> Optional[str]:
        """Resolve Python import name to file path."""
        # Convert module.submodule to module/submodule.py
        module_path = import_name.replace('.', '/')
        
        # Try as file
        file_path = repo_root / f"{module_path}.py"
        if file_path.exists():
            relative = file_path.relative_to(repo_root)
            return str(relative).replace('\\', '/')
        
        # Try as package
        package_path = repo_root / module_path / "__init__.py"
        if package_path.exists():
            relative = package_path.relative_to(repo_root)
            return str(relative).replace('\\', '/')
        
        # Try src/ prefix (common pattern)
        file_path = repo_root / "src" / f"{module_path}.py"
        if file_path.exists():
            relative = file_path.relative_to(repo_root)
            return str(relative).replace('\\', '/')
        
        return None
    
    def _add_edge_if_internal_js(self, source_id: str, import_path: str, source_file: Path, repo_root: Path) -> None:
        """Add edge if import refers to internal module (JavaScript/TypeScript)."""
        # Skip node_modules imports
        if import_path.startswith('.') or import_path.startswith('/'):
            # Relative or absolute import - resolve it
            target_id = self._resolve_js_import(import_path, source_file, repo_root)
            
            if target_id and target_id in self.nodes:
                self.edges[(source_id, target_id)] += 1
    
    def _resolve_js_import(self, import_path: str, source_file: Path, repo_root: Path) -> Optional[str]:
        """Resolve JavaScript/TypeScript import path to file."""
        # Handle relative imports
        if import_path.startswith('.'):
            # Resolve relative to source file
            resolved = (source_file.parent / import_path).resolve()
            
            # Try with various extensions
            for ext in ['.js', '.jsx', '.ts', '.tsx']:
                if resolved.with_suffix(ext).exists():
                    relative = resolved.with_suffix(ext).relative_to(repo_root)
                    return str(relative).replace('\\', '/')
                
                # Try as directory with index file
                index_file = resolved / f"index{ext}"
                if index_file.exists():
                    relative = index_file.relative_to(repo_root)
                    return str(relative).replace('\\', '/')
        
        return None
    
    def _add_edge_if_internal_csharp(self, source_id: str, using_name: str, repo_root: Path) -> None:
        """Add edge if using refers to internal namespace (C#)."""
        # Convert namespace to potential file path
        # This is heuristic-based since C# namespaces don't map 1:1 to files
        target_id = self._resolve_csharp_using(using_name, repo_root)
        
        if target_id and target_id in self.nodes:
            self.edges[(source_id, target_id)] += 1
    
    def _resolve_csharp_using(self, using_name: str, repo_root: Path) -> Optional[str]:
        """Resolve C# using directive to file path (heuristic)."""
        # Convert Namespace.Class to search pattern
        parts = using_name.split('.')
        
        # Try to find file with matching class name
        if len(parts) > 0:
            class_name = parts[-1]
            
            # Search for files matching class name
            for cs_file in repo_root.rglob(f"{class_name}.cs"):
                relative = cs_file.relative_to(repo_root)
                node_id = str(relative).replace('\\', '/')
                if node_id in self.nodes:
                    return node_id
        
        return None
    
    def _to_d3_format(self) -> Dict[str, Any]:
        """Convert nodes and edges to D3.js-compatible format."""
        # Convert nodes
        nodes_list = [
            {
                "id": node.id,
                "label": node.label,
                "type": node.type,
                "loc": node.loc,
                "language": node.language
            }
            for node in self.nodes.values()
        ]
        
        # Convert edges
        edges_list = [
            {
                "source": source,
                "target": target,
                "weight": weight
            }
            for (source, target), weight in self.edges.items()
        ]
        
        return {
            "nodes": nodes_list,
            "edges": edges_list,
            "metadata": {
                "total_nodes": len(nodes_list),
                "total_edges": len(edges_list),
                "languages": self._get_language_distribution()
            }
        }
    
    def _get_language_distribution(self) -> Dict[str, int]:
        """Get distribution of languages in the graph."""
        distribution = defaultdict(int)
        for node in self.nodes.values():
            distribution[node.language] += 1
        return dict(distribution)
