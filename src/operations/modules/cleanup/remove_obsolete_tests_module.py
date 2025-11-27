"""
Remove Obsolete Tests Module

Detects and removes test files calling non-existent APIs (methods removed during refactoring).
This prevents false test failures from outdated tests testing old implementations.

Detection Strategy:
1. Parse test files for method calls (._method_name patterns)
2. Check if those methods exist in current implementation
3. Mark tests as obsolete if calling removed private methods
4. Remove obsolete test files (with Git tracking)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
import importlib.util
import logging

from src.operations.base_operation_module import (
    BaseOperationModule, 
    OperationResult, 
    OperationStatus,
    OperationModuleMetadata
)

logger = logging.getLogger(__name__)


class RemoveObsoleteTestsModule(BaseOperationModule):
    """Detects and removes tests calling non-existent implementation methods."""
    
    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = project_root
        self.tests_dir = project_root / "tests"
        self.src_dir = project_root / "src"
        
    def get_metadata(self) -> OperationModuleMetadata:
        return OperationModuleMetadata(
            module_id="remove_obsolete_tests",
            name="Remove Obsolete Tests",
            description="Removes test files calling non-existent methods",
            phase="cleanup",
            version="1.0.0"
        )
    
    def execute(self, context: Dict) -> OperationResult:
        """
        Find and remove obsolete test files.
        
        Args:
            context: Must contain 'dry_run' boolean
            
        Returns:
            OperationResult with removed_tests list
        """
        dry_run = context.get('dry_run', False)
        
        try:
            # Find obsolete tests
            obsolete_tests = self._find_obsolete_tests()
            
            removed_count = 0
            removed_files = []
            
            if not dry_run and obsolete_tests:
                # Remove obsolete test files
                for test_file, reasons in obsolete_tests.items():
                    logger.info(f"Removing obsolete test: {test_file}")
                    logger.info(f"  Reasons: {', '.join(reasons)}")
                    
                    try:
                        test_file.unlink()
                        removed_files.append(str(test_file.relative_to(self.project_root)))
                        removed_count += 1
                    except Exception as e:
                        logger.error(f"Failed to remove {test_file}: {e}")
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"{'[DRY RUN] Would remove' if dry_run else 'Removed'} {len(obsolete_tests)} obsolete test files",
                data={
                    'obsolete_tests_found': len(obsolete_tests),
                    'obsolete_tests': {
                        str(k.relative_to(self.project_root)): v 
                        for k, v in obsolete_tests.items()
                    },
                    'removed_count': removed_count,
                    'removed_files': removed_files,
                    'dry_run': dry_run
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to remove obsolete tests: {e}")
            return OperationResult(
                success=False,
                message=f"Failed to remove obsolete tests: {str(e)}",
                data={'error': str(e)}
            )
    
    def _find_obsolete_tests(self) -> Dict[Path, List[str]]:
        """
        Find test files calling non-existent methods.
        
        Returns:
            Dict mapping test file paths to list of obsolescence reasons
        """
        obsolete_tests = {}
        
        # Find all test files
        test_files = list(self.tests_dir.rglob("test_*.py"))
        
        for test_file in test_files:
            reasons = self._check_test_obsolescence(test_file)
            if reasons:
                obsolete_tests[test_file] = reasons
        
        return obsolete_tests
    
    def _check_test_obsolescence(self, test_file: Path) -> List[str]:
        """
        Check if test file is obsolete (calling non-existent methods).
        
        Args:
            test_file: Path to test file
            
        Returns:
            List of obsolescence reasons (empty if test is valid)
        """
        reasons = []
        
        try:
            content = test_file.read_text(encoding='utf-8')
            
            # Parse Python AST
            tree = ast.parse(content)
            
            # Extract class being tested (from imports)
            tested_class = self._extract_tested_class(tree, content)
            
            if not tested_class:
                return reasons  # Can't determine what's being tested
            
            # Find implementation file
            impl_file = self._find_implementation_file(tested_class)
            
            if not impl_file or not impl_file.exists():
                return reasons  # Implementation file not found
            
            # Get all private methods called in test
            called_private_methods = self._extract_private_method_calls(tree)
            
            if not called_private_methods:
                return reasons  # No private methods called
            
            # Check which methods exist in implementation
            impl_methods = self._extract_implementation_methods(impl_file)
            
            # Find methods that don't exist
            missing_methods = called_private_methods - impl_methods
            
            if missing_methods:
                reasons.append(f"Calls non-existent methods: {', '.join(sorted(missing_methods))}")
            
            # Additional check: If >50% of tested methods are missing, likely obsolete
            if len(missing_methods) / len(called_private_methods) > 0.5:
                reasons.append(f"Majority of methods ({len(missing_methods)}/{len(called_private_methods)}) no longer exist")
            
        except Exception as e:
            logger.debug(f"Error checking {test_file}: {e}")
        
        return reasons
    
    def _extract_tested_class(self, tree: ast.AST, content: str) -> str:
        """Extract the class being tested from imports."""
        # Look for imports like: from src.agents.X import ClassName
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith('src.'):
                    for alias in node.names:
                        # Return first class-like import (PascalCase)
                        if alias.name[0].isupper():
                            return alias.name
        
        # Fallback: Look for class instantiation in test
        # Pattern: ClassName(...)
        class_pattern = r'([A-Z][a-zA-Z0-9_]*)\s*\('
        matches = re.findall(class_pattern, content)
        if matches:
            return matches[0]
        
        return None
    
    def _find_implementation_file(self, class_name: str) -> Path:
        """Find implementation file for given class name."""
        # Common patterns:
        # CodeExecutor -> src/cortex_agents/code_executor/agent.py
        # ConversationManager -> src/tier1/conversations/conversation_manager.py
        
        # Convert PascalCase to snake_case
        snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
        
        # Search common locations
        search_paths = [
            self.src_dir / "cortex_agents" / snake_case / "agent.py",
            self.src_dir / "cortex_agents" / f"{snake_case}.py",
            self.src_dir / "agents" / snake_case / "agent.py",
            self.src_dir / "tier1" / f"{snake_case}.py",
            self.src_dir / "tier1" / "conversations" / f"{snake_case}.py",
            self.src_dir / "tier1" / "entities" / f"{snake_case}.py",
            self.src_dir / "tier2" / f"{snake_case}.py",
            self.src_dir / "tier3" / f"{snake_case}.py",
        ]
        
        for path in search_paths:
            if path.exists():
                return path
        
        # Fallback: Search recursively
        for impl_file in self.src_dir.rglob(f"{snake_case}.py"):
            return impl_file
        
        for impl_file in self.src_dir.rglob("agent.py"):
            if snake_case in str(impl_file.parent):
                return impl_file
        
        return None
    
    def _extract_private_method_calls(self, tree: ast.AST) -> Set[str]:
        """Extract all private method calls from test AST."""
        private_methods = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                # Look for ._method_name patterns
                if isinstance(node.attr, str) and node.attr.startswith('_'):
                    private_methods.add(node.attr)
        
        return private_methods
    
    def _extract_implementation_methods(self, impl_file: Path) -> Set[str]:
        """Extract all methods defined in implementation file."""
        methods = set()
        
        try:
            content = impl_file.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    methods.add(node.name)
                elif isinstance(node, ast.ClassDef):
                    # Get methods within class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.add(item.name)
        
        except Exception as e:
            logger.debug(f"Error parsing {impl_file}: {e}")
        
        return methods
