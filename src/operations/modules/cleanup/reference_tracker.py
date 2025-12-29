"""
CORTEX Cleanup: Reference Tracker

Tracks all file references across the codebase to enable safe reorganization.
Parses Python imports, file paths, markdown links, and config references.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from pathlib import Path
from typing import Dict, Any, List, Set, Tuple, Optional
from dataclasses import dataclass, field
import logging
import re
import ast
import json
import yaml

logger = logging.getLogger(__name__)


@dataclass
class FileReference:
    """Reference from one file to another"""
    source_file: str  # File containing the reference
    target_file: str  # File being referenced
    reference_type: str  # import, path, link, config
    line_number: int
    line_content: str
    context: str  # Additional context for updating


class ReferenceTracker:
    """
    Tracks all file references across codebase.
    
    Capabilities:
    - Parse Python imports (from/import statements)
    - Find file path references (Path(), open(), etc.)
    - Extract markdown links
    - Parse config file references
    - Build dependency graph
    - Generate update instructions for file moves
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize reference tracker.
        
        Args:
            project_root: Root directory of project
        """
        self.project_root = project_root
        
        # Reference tracking
        self.references: List[FileReference] = []
        self.import_graph: Dict[str, Set[str]] = {}  # file -> imported files
        self.dependency_graph: Dict[str, Set[str]] = {}  # file -> files that depend on it
        
        # Statistics
        self.total_imports = 0
        self.total_path_refs = 0
        self.total_links = 0
        self.total_config_refs = 0
    
    def scan(self, files: Dict[str, Any]) -> List[FileReference]:
        """
        Scan files for references.
        
        Args:
            files: Dictionary of relative_path -> FileMetadata
            
        Returns:
            List of all file references found
        """
        logger.info(f"Scanning {len(files)} files for references...")
        
        for relative_path, metadata in files.items():
            file_path = self.project_root / relative_path
            
            if not file_path.exists():
                continue
            
            # Skip binary files
            if metadata.is_binary:
                continue
            
            # Parse based on file type
            if file_path.suffix == '.py':
                self._scan_python_file(file_path, relative_path)
            elif file_path.suffix in ['.md', '.rst', '.txt']:
                self._scan_markdown_file(file_path, relative_path)
            elif file_path.suffix in ['.json', '.yaml', '.yml']:
                self._scan_config_file(file_path, relative_path)
        
        # Build dependency graph
        self._build_dependency_graph()
        
        logger.info(f"Found {len(self.references)} references:")
        logger.info(f"  - Imports: {self.total_imports}")
        logger.info(f"  - Path references: {self.total_path_refs}")
        logger.info(f"  - Links: {self.total_links}")
        logger.info(f"  - Config references: {self.total_config_refs}")
        
        return self.references
    
    def _scan_python_file(self, file_path: Path, relative_path: str) -> None:
        """Scan Python file for imports and path references"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Parse AST for imports
            try:
                tree = ast.parse(content, filename=str(file_path))
                self._extract_imports_from_ast(tree, file_path, relative_path)
            except SyntaxError as e:
                logger.debug(f"Syntax error parsing {relative_path}: {e}")
            
            # Scan for path references with regex
            self._scan_path_references(content, file_path, relative_path)
            
        except Exception as e:
            logger.error(f"Error scanning Python file {relative_path}: {e}")
    
    def _extract_imports_from_ast(self, tree: ast.AST, file_path: Path, relative_path: str) -> None:
        """Extract import statements from AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._add_import_reference(
                        relative_path,
                        alias.name,
                        node.lineno,
                        f"import {alias.name}"
                    )
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self._add_import_reference(
                        relative_path,
                        node.module,
                        node.lineno,
                        f"from {node.module} import ..."
                    )
    
    def _add_import_reference(self, source: str, module: str, line_num: int, line_content: str) -> None:
        """Add an import reference"""
        # Convert module to file path
        target_file = self._module_to_file_path(module)
        
        if target_file:
            ref = FileReference(
                source_file=source,
                target_file=target_file,
                reference_type='import',
                line_number=line_num,
                line_content=line_content,
                context=module
            )
            self.references.append(ref)
            self.total_imports += 1
            
            # Update import graph
            if source not in self.import_graph:
                self.import_graph[source] = set()
            self.import_graph[source].add(target_file)
    
    def _module_to_file_path(self, module: str) -> Optional[str]:
        """Convert Python module name to file path"""
        # Handle src-relative imports
        if module.startswith('src.'):
            parts = module.split('.')
            # Try as module (directory with __init__.py)
            module_path = Path(*parts) / '__init__.py'
            if (self.project_root / module_path).exists():
                return str(module_path)
            
            # Try as file
            file_path = Path(*parts).with_suffix('.py')
            if (self.project_root / file_path).exists():
                return str(file_path)
        
        return None
    
    def _scan_path_references(self, content: str, file_path: Path, relative_path: str) -> None:
        """Scan for file path references using regex"""
        # Patterns for path references
        patterns = [
            # Path("path/to/file")
            (r'Path\([\'"]([^\'"]+)[\'"]\)', 'path'),
            # open("path/to/file")
            (r'open\([\'"]([^\'"]+)[\'"]\)', 'path'),
            # with open("path/to/file")
            (r'with\s+open\([\'"]([^\'"]+)[\'"]\)', 'path'),
            # "path/to/file.ext"
            (r'[\'"]([^\'"]*(?:src|cortex-brain|docs|tests)/[^\'"]+\.[a-z]+)[\'"]', 'path'),
        ]
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern, ref_type in patterns:
                for match in re.finditer(pattern, line):
                    path_str = match.group(1)
                    
                    # Normalize path
                    normalized_path = self._normalize_path(path_str)
                    
                    if normalized_path:
                        ref = FileReference(
                            source_file=relative_path,
                            target_file=normalized_path,
                            reference_type=ref_type,
                            line_number=line_num,
                            line_content=line.strip(),
                            context=path_str
                        )
                        self.references.append(ref)
                        self.total_path_refs += 1
    
    def _scan_markdown_file(self, file_path: Path, relative_path: str) -> None:
        """Scan markdown file for links"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Patterns for markdown links
            patterns = [
                # [text](path/to/file.md)
                (r'\[([^\]]+)\]\(([^\)]+)\)', 'link'),
                # <path/to/file.md>
                (r'<([^>]+)>', 'link'),
            ]
            
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for pattern, ref_type in patterns:
                    for match in re.finditer(pattern, line):
                        link_target = match.group(2) if len(match.groups()) > 1 else match.group(1)
                        
                        # Skip external links
                        if link_target.startswith(('http://', 'https://', 'mailto:')):
                            continue
                        
                        # Normalize path
                        normalized_path = self._normalize_path(link_target)
                        
                        if normalized_path:
                            ref = FileReference(
                                source_file=relative_path,
                                target_file=normalized_path,
                                reference_type=ref_type,
                                line_number=line_num,
                                line_content=line.strip(),
                                context=link_target
                            )
                            self.references.append(ref)
                            self.total_links += 1
            
        except Exception as e:
            logger.error(f"Error scanning markdown file {relative_path}: {e}")
    
    def _scan_config_file(self, file_path: Path, relative_path: str) -> None:
        """Scan configuration file for file references"""
        try:
            # Parse config file
            if file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            elif file_path.suffix in ['.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            else:
                return
            
            # Find file paths in config
            self._extract_paths_from_config(config, relative_path)
            
        except Exception as e:
            logger.error(f"Error scanning config file {relative_path}: {e}")
    
    def _extract_paths_from_config(self, data: Any, source_file: str, path: str = '') -> None:
        """Recursively extract file paths from config data"""
        if isinstance(data, dict):
            for key, value in data.items():
                self._extract_paths_from_config(value, source_file, f"{path}.{key}" if path else key)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                self._extract_paths_from_config(item, source_file, f"{path}[{i}]")
        
        elif isinstance(data, str):
            # Check if string looks like a file path
            if '/' in data and any(ext in data for ext in ['.py', '.md', '.json', '.yaml', '.yml']):
                normalized_path = self._normalize_path(data)
                
                if normalized_path:
                    ref = FileReference(
                        source_file=source_file,
                        target_file=normalized_path,
                        reference_type='config',
                        line_number=0,  # Config files don't have line numbers
                        line_content=f"{path}: {data}",
                        context=path
                    )
                    self.references.append(ref)
                    self.total_config_refs += 1
    
    def _normalize_path(self, path_str: str) -> Optional[str]:
        """Normalize and validate file path"""
        try:
            # Remove anchor/query strings
            path_str = path_str.split('#')[0].split('?')[0]
            
            # Convert to Path
            path = Path(path_str)
            
            # Make absolute if relative
            if not path.is_absolute():
                path = self.project_root / path
            
            # Get relative to project root
            try:
                relative_path = path.relative_to(self.project_root)
                
                # Check if file exists (or could exist after reorganization)
                return str(relative_path).replace('\\', '/')
                
            except ValueError:
                # Path outside project root
                return None
        
        except Exception:
            return None
    
    def _build_dependency_graph(self) -> None:
        """Build reverse dependency graph (which files depend on each file)"""
        for ref in self.references:
            if ref.target_file not in self.dependency_graph:
                self.dependency_graph[ref.target_file] = set()
            
            self.dependency_graph[ref.target_file].add(ref.source_file)
    
    def get_dependents(self, file_path: str) -> Set[str]:
        """Get all files that depend on the given file"""
        return self.dependency_graph.get(file_path, set())
    
    def get_dependencies(self, file_path: str) -> Set[str]:
        """Get all files that the given file depends on"""
        return self.import_graph.get(file_path, set())
    
    def get_update_instructions(self, old_path: str, new_path: str) -> List[Dict[str, Any]]:
        """
        Generate update instructions for file move.
        
        Args:
            old_path: Original file path (relative to project root)
            new_path: New file path (relative to project root)
            
        Returns:
            List of update instructions for each reference that needs to change
        """
        instructions = []
        
        # Find all references to this file
        for ref in self.references:
            if ref.target_file == old_path:
                # Calculate new reference string
                new_ref = self._calculate_new_reference(
                    ref.source_file,
                    old_path,
                    new_path,
                    ref.reference_type,
                    ref.context
                )
                
                if new_ref:
                    instructions.append({
                        'file': ref.source_file,
                        'line': ref.line_number,
                        'old_content': ref.line_content,
                        'old_reference': ref.context,
                        'new_reference': new_ref,
                        'reference_type': ref.reference_type
                    })
        
        return instructions
    
    def _calculate_new_reference(
        self,
        source_file: str,
        old_target: str,
        new_target: str,
        ref_type: str,
        old_context: str
    ) -> Optional[str]:
        """Calculate new reference string after file move"""
        try:
            if ref_type == 'import':
                # Convert file path to module name
                return self._file_path_to_module(new_target)
            
            elif ref_type in ['path', 'config']:
                # Return new file path
                return new_target
            
            elif ref_type == 'link':
                # Calculate relative link from source to new target
                source_dir = Path(source_file).parent
                target_path = Path(new_target)
                
                # Calculate relative path
                try:
                    relative = target_path.relative_to(source_dir)
                    return str(relative).replace('\\', '/')
                except ValueError:
                    # Use absolute path from project root
                    return str(target_path).replace('\\', '/')
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating new reference: {e}")
            return None
    
    def _file_path_to_module(self, file_path: str) -> str:
        """Convert file path to Python module name"""
        # Remove extension
        path = Path(file_path)
        if path.suffix == '.py':
            path = path.with_suffix('')
        
        # Convert to module notation
        parts = path.parts
        
        # Remove __init__ if present
        if parts[-1] == '__init__':
            parts = parts[:-1]
        
        return '.'.join(parts)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get reference tracking statistics"""
        return {
            'total_references': len(self.references),
            'total_imports': self.total_imports,
            'total_path_refs': self.total_path_refs,
            'total_links': self.total_links,
            'total_config_refs': self.total_config_refs,
            'files_with_dependencies': len(self.import_graph),
            'files_with_dependents': len(self.dependency_graph)
        }
