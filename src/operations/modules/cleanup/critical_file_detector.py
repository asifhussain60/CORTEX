"""
Critical File Detector for Cleanup Validation

Automatically detects files that are critical to CORTEX operation
and should never be deleted during cleanup.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import ast
import logging
from pathlib import Path
from typing import Set, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ImportInfo:
    """Information about an import statement"""
    module: str
    file_path: Path
    line_number: int


class CriticalFileDetector:
    """Detect files that are critical to CORTEX operation"""
    
    # Entry points that MUST work
    ENTRY_POINTS = [
        'src/main.py',
        'src/entry_point/cortex_entry.py',
        'src/cortex_agents/intent_router.py'
    ]
    
    # Directories that are always protected
    PROTECTED_DIRECTORIES = [
        'src/',
        'tests/',
        'cortex-brain/tier0/',
        'cortex-brain/tier1/',
        'cortex-brain/tier2/',
        'cortex-brain/tier3/',
        '.git/',
        '.github/prompts/'
    ]
    
    # Individual files that are always protected
    PROTECTED_FILES = [
        'cortex.config.json',
        'VERSION',
        'requirements.txt',
        'pytest.ini',
        'setup.py',
        'pyproject.toml',
        'cortex-brain/response-templates.yaml',
        'cortex-brain/brain-protection-rules.yaml'
    ]
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self._import_cache: Dict[Path, Set[Path]] = {}
    
    def detect_critical_files(self) -> Set[Path]:
        """
        Build comprehensive list of critical files.
        
        Returns:
            Set of Path objects for files that must not be deleted
        """
        logger.info("Detecting critical files...")
        critical_files = set()
        
        # 1. Protected directories (all files within)
        for dir_pattern in self.PROTECTED_DIRECTORIES:
            dir_path = self.project_root / dir_pattern
            if dir_path.exists() and dir_path.is_dir():
                critical_files.update(dir_path.rglob('*'))
        
        # 2. Protected individual files
        for file_pattern in self.PROTECTED_FILES:
            file_path = self.project_root / file_pattern
            if file_path.exists():
                critical_files.add(file_path)
        
        # 3. Entry points and their dependencies
        for entry_point in self.ENTRY_POINTS:
            entry_path = self.project_root / entry_point
            if entry_path.exists():
                dependencies = self.trace_imports(entry_path)
                critical_files.update(dependencies)
        
        logger.info(f"Detected {len(critical_files)} critical files")
        return critical_files
    
    def trace_imports(self, file_path: Path, visited: Set[Path] = None) -> Set[Path]:
        """
        Recursively trace all imports from a Python file.
        
        Args:
            file_path: Starting Python file
            visited: Set of already visited files (prevents cycles)
        
        Returns:
            Set of all files in import chain
        """
        if visited is None:
            visited = set()
        
        if file_path in visited or not file_path.exists():
            return visited
        
        visited.add(file_path)
        
        # Parse imports from this file
        imports = self._parse_imports(file_path)
        
        # Recursively trace each import
        for import_info in imports:
            if import_info.file_path and import_info.file_path not in visited:
                self.trace_imports(import_info.file_path, visited)
        
        return visited
    
    def _parse_imports(self, file_path: Path) -> List[ImportInfo]:
        """
        Parse import statements from a Python file.
        
        Args:
            file_path: Python file to parse
        
        Returns:
            List of ImportInfo objects
        """
        # Check cache
        if file_path in self._import_cache:
            return [
                ImportInfo(module='', file_path=p, line_number=0)
                for p in self._import_cache[file_path]
            ]
        
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_path = self._resolve_import(alias.name, file_path)
                        if module_path:
                            imports.append(ImportInfo(
                                module=alias.name,
                                file_path=module_path,
                                line_number=node.lineno
                            ))
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_path = self._resolve_import(node.module, file_path)
                        if module_path:
                            imports.append(ImportInfo(
                                module=node.module,
                                file_path=module_path,
                                line_number=node.lineno
                            ))
        
        except Exception as e:
            logger.debug(f"Could not parse {file_path}: {e}")
        
        # Cache results
        self._import_cache[file_path] = {imp.file_path for imp in imports if imp.file_path}
        
        return imports
    
    def _resolve_import(self, module_name: str, from_file: Path) -> Path:
        """
        Resolve import statement to actual file path.
        
        Args:
            module_name: Import module name (e.g., 'src.tier1.working_memory')
            from_file: File containing the import
        
        Returns:
            Path to imported file, or None if not found
        """
        # Convert module name to path
        module_parts = module_name.split('.')
        
        # Try absolute import from project root
        module_path = self.project_root
        for part in module_parts:
            module_path = module_path / part
        
        # Check for .py file
        if (module_path.with_suffix('.py')).exists():
            return module_path.with_suffix('.py')
        
        # Check for __init__.py in directory
        if (module_path / '__init__.py').exists():
            return module_path / '__init__.py'
        
        # Try relative import from current file's directory
        relative_base = from_file.parent
        module_path = relative_base
        for part in module_parts:
            module_path = module_path / part
        
        if (module_path.with_suffix('.py')).exists():
            return module_path.with_suffix('.py')
        
        if (module_path / '__init__.py').exists():
            return module_path / '__init__.py'
        
        return None
    
    def is_critical(self, file_path: Path, critical_files: Set[Path] = None) -> bool:
        """
        Check if a file is critical.
        
        Args:
            file_path: File to check
            critical_files: Pre-computed set of critical files (optional)
        
        Returns:
            True if file is critical, False otherwise
        """
        if critical_files is None:
            critical_files = self.detect_critical_files()
        
        return file_path in critical_files
    
    def find_importers(self, file_path: Path) -> List[ImportInfo]:
        """
        Find all files that import the given file.
        
        Args:
            file_path: File to search for
        
        Returns:
            List of ImportInfo for files that import this file
        """
        importers = []
        
        # Search all Python files in project
        for py_file in self.project_root.rglob('*.py'):
            if py_file == file_path:
                continue
            
            imports = self._parse_imports(py_file)
            for import_info in imports:
                if import_info.file_path == file_path:
                    importers.append(ImportInfo(
                        module=import_info.module,
                        file_path=py_file,
                        line_number=import_info.line_number
                    ))
        
        return importers
