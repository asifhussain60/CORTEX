"""
Orphan Detector - Identify orphaned test files using AST analysis.

Detects test files that reference non-existent source files:
- Parses Python test files to find import statements
- Maps test → source file relationships
- Identifies orphaned tests (missing source files)
- Handles relative imports, package structures

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Set, Any, Optional


logger = logging.getLogger(__name__)


class OrphanDetector:
    """
    Detects orphaned test files using AST analysis.
    
    Identifies test files that import modules that no longer exist,
    indicating the original source file was deleted but the test remains.
    """
    
    TEST_PATTERNS = ['test_*.py', '*_test.py']
    
    def __init__(self, project_root: Path):
        """
        Initialize orphan detector.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.stats = {
            'tests_scanned': 0,
            'imports_analyzed': 0,
            'orphans_found': 0
        }
        logger.info(f"Initialized OrphanDetector (root={project_root})")
    
    def find_orphaned_tests(self, test_files: List[Path]) -> Dict[str, Any]:
        """
        Find orphaned test files.
        
        Args:
            test_files: List of test file paths to analyze
        
        Returns:
            {
                'orphaned_tests': List[Dict],  # Each dict has 'test_path', 'missing_imports'
                'total_orphans': int,
                'stats': Dict[str, int]
            }
        """
        self.stats['tests_scanned'] = len(test_files)
        logger.info(f"Analyzing {len(test_files)} test files for orphans")
        
        orphaned_tests = []
        
        for test_path in test_files:
            missing_imports = self._check_test_imports(test_path)
            self.stats['imports_analyzed'] += len(missing_imports) if missing_imports else 0
            
            if missing_imports:
                orphaned_tests.append({
                    'test_path': test_path,
                    'missing_imports': missing_imports
                })
                self.stats['orphans_found'] += 1
        
        logger.info(f"Found {len(orphaned_tests)} orphaned test files")
        
        return {
            'orphaned_tests': orphaned_tests,
            'total_orphans': len(orphaned_tests),
            'stats': self.stats.copy()
        }
    
    def _check_test_imports(self, test_path: Path) -> List[str]:
        """
        Check if test file imports non-existent modules.
        
        Args:
            test_path: Test file to analyze
        
        Returns:
            List of missing module names
        """
        try:
            # Parse test file
            with test_path.open('r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(test_path))
            
            # Extract imports
            imports = self._extract_imports(tree)
            
            # Check if imported modules exist
            missing_imports = []
            for module_name in imports:
                if not self._module_exists(module_name, test_path):
                    missing_imports.append(module_name)
            
            return missing_imports
        
        except SyntaxError as e:
            logger.warning(f"Syntax error in {test_path}: {e}")
            return []
        
        except Exception as e:
            logger.warning(f"Error analyzing {test_path}: {e}")
            return []
    
    def _extract_imports(self, tree: ast.AST) -> Set[str]:
        """
        Extract all imported module names from AST.
        
        Args:
            tree: Parsed AST
        
        Returns:
            Set of module names
        """
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        
        return imports
    
    def _module_exists(self, module_name: str, test_path: Path) -> bool:
        """
        Check if imported module exists in the project.
        
        Args:
            module_name: Module to check (e.g., 'src.orchestrators.vacuum')
            test_path: Path of test file (for relative imports)
        
        Returns:
            True if module file exists
        """
        # Skip standard library and third-party modules
        if self._is_external_module(module_name):
            return True
        
        # Try to resolve module path
        module_path = self._resolve_module_path(module_name, test_path)
        
        if module_path:
            return module_path.exists()
        
        return False
    
    def _is_external_module(self, module_name: str) -> bool:
        """
        Check if module is external (stdlib or third-party).
        
        Args:
            module_name: Module name
        
        Returns:
            True if external module
        """
        # Common standard library top-level modules
        stdlib_modules = {
            'os', 'sys', 'pathlib', 'subprocess', 'typing', 'json', 'yaml',
            'logging', 'datetime', 'collections', 'hashlib', 'shutil', 'gzip',
            'ast', 're', 'argparse', 'unittest', 'pytest', 'mock'
        }
        
        top_level = module_name.split('.')[0]
        
        if top_level in stdlib_modules:
            return True
        
        # Third-party packages usually don't start with project structure
        # Heuristic: if doesn't start with 'src', 'cortex', 'tests', assume external
        project_prefixes = {'src', 'cortex', 'tests'}
        if top_level not in project_prefixes:
            return True
        
        return False
    
    def _resolve_module_path(self, module_name: str, test_path: Path) -> Optional[Path]:
        """
        Resolve module name to file path.
        
        Args:
            module_name: Module name (e.g., 'src.orchestrators.vacuum')
            test_path: Path of test file
        
        Returns:
            Resolved file path or None
        """
        # Convert module name to path
        parts = module_name.split('.')
        
        # Try absolute import from project root
        module_path = self.project_root / '/'.join(parts)
        
        # Check as file
        if module_path.with_suffix('.py').exists():
            return module_path.with_suffix('.py')
        
        # Check as package
        if (module_path / '__init__.py').exists():
            return module_path / '__init__.py'
        
        # Try relative to test file directory
        test_dir = test_path.parent
        relative_module_path = test_dir / '/'.join(parts)
        
        if relative_module_path.with_suffix('.py').exists():
            return relative_module_path.with_suffix('.py')
        
        if (relative_module_path / '__init__.py').exists():
            return relative_module_path / '__init__.py'
        
        return None
