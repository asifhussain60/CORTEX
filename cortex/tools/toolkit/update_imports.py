#!/usr/bin/env python3
"""
AC-AR-010-03: Import Path Update Script

Updates all imports across 116+ cortex files to use correct paths.
Handles tier isolation, cross-platform paths, and circular dependency prevention.

Author: CORTEX Framework
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImportUpdater:
    """Updates import statements across codebase to use correct paths."""
    
    # Mapping of old imports to new imports
    IMPORT_MAPPINGS: Dict[str, str] = {
        # Brain modules
        "from cortex_brain": "from cortex.brain",
        "import cortex_brain": "import cortex.brain",
        
        # Orchestrators
        "from orchestrators": "from cortex.orchestrators",
        "import orchestrators": "import cortex.orchestrators",
        
        # Core modules
        "from core.": "from cortex.core.",
        "import core.": "import cortex.core.",
        
        # Domain brain
        "from domain_brain": "from cortex.domain_brain",
        "import domain_brain": "import cortex.domain_brain",
    }
    
    # Tier isolation rules - prevents cross-tier imports
    TIER_ISOLATION_RULES: Dict[str, Set[str]] = {
        "tier0": {"tier0"},  # tier0 can only import tier0
        "tier1": {"tier0", "tier1"},  # tier1 can import tier0, tier1
        "tier2": {"tier0", "tier1", "tier2"},  # tier2 can import all lower tiers
        "tier3": {"tier0", "tier1", "tier2", "tier3"},  # tier3 can import all tiers
    }
    
    def __init__(self, root_path: Path):
        """Initialize importer with root path.
        
        Args:
            root_path: Root directory to scan.
        """
        self.root_path = Path(root_path)
        self.updated_files: List[Path] = []
        self.skip_dirs = {"__pycache__", ".git", ".venv", "node_modules"}
    
    def update_all_imports(self) -> Tuple[int, List[str]]:
        """Update all import statements in Python files.
        
        Returns:
            Tuple of (files_updated, errors).
        """
        errors = []
        count = 0
        
        for py_file in self.root_path.rglob("*.py"):
            if any(skip in py_file.parts for skip in self.skip_dirs):
                continue
            
            try:
                if self._update_file(py_file):
                    count += 1
                    self.updated_files.append(py_file)
            except Exception as e:
                errors.append(f"{py_file}: {str(e)}")
        
        logger.info(f"Updated imports in {count} files")
        return count, errors
    
    def _update_file(self, file_path: Path) -> bool:
        """Update imports in a single file.
        
        Args:
            file_path: Path to Python file.
            
        Returns:
            True if file was modified.
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, PermissionError):
            return False
        
        original_content = content
        
        # Apply import mappings
        for old_import, new_import in self.IMPORT_MAPPINGS.items():
            content = content.replace(old_import, new_import)
        
        # Check tier isolation
        if not self._validate_tier_isolation(file_path, content):
            logger.warning(f"Tier isolation violation in {file_path}")
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True
        
        return False
    
    def _validate_tier_isolation(self, file_path: Path, content: str) -> bool:
        """Validate tier isolation rules.
        
        Args:
            file_path: Path to Python file.
            content: File content.
            
        Returns:
            True if tier isolation is valid.
        """
        # Extract tier level from path
        tier_level = None
        for i in range(4):
            if f"/tier{i}/" in str(file_path) or f"\\tier{i}\\" in str(file_path):
                tier_level = f"tier{i}"
                break
        
        if tier_level is None:
            return True  # Not a tiered module, skip validation
        
        allowed_tiers = self.TIER_ISOLATION_RULES.get(tier_level, set())
        
        # Check imports
        import_pattern = r'from cortex\..*?(?:tier\d)'
        matches = re.findall(import_pattern, content)
        
        for match in matches:
            for tier in range(4):
                if f"tier{tier}" in match:
                    if f"tier{tier}" not in allowed_tiers:
                        return False
        
        return True
    
    def check_circular_dependencies(self) -> List[str]:
        """Check for circular dependencies.
        
        Returns:
            List of detected circular dependencies.
        """
        circular_deps = []
        import_graph: Dict[str, Set[str]] = {}
        
        # Build import graph
        for py_file in self.root_path.rglob("*.py"):
            if any(skip in py_file.parts for skip in self.skip_dirs):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                module_name = str(py_file.relative_to(self.root_path)).replace(".py", "").replace("/", ".").replace("\\", ".")
                import_graph[module_name] = self._extract_imports(content)
            except Exception:
                pass
        
        # Detect cycles using DFS
        for start_module in import_graph:
            visited = set()
            rec_stack = set()
            if self._has_cycle(start_module, import_graph, visited, rec_stack, []):
                circular_deps.append(start_module)
        
        return circular_deps
    
    def _extract_imports(self, content: str) -> Set[str]:
        """Extract import module names from content.
        
        Args:
            content: File content.
            
        Returns:
            Set of imported modules.
        """
        imports = set()
        
        # Match: from X import Y
        from_imports = re.findall(r'from (cortex\.[.\w]+)', content)
        imports.update(from_imports)
        
        # Match: import X
        direct_imports = re.findall(r'import (cortex\.[.\w]+)', content)
        imports.update(direct_imports)
        
        return imports
    
    def _has_cycle(self, node: str, graph: Dict[str, Set[str]], visited: Set[str],
                   rec_stack: Set[str], path: List[str]) -> bool:
        """DFS to detect cycles.
        
        Args:
            node: Current node.
            graph: Import graph.
            visited: Visited nodes.
            rec_stack: Recursion stack.
            path: Path from start.
            
        Returns:
            True if cycle detected.
        """
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        if node in graph:
            for neighbor in graph[node]:
                if neighbor not in visited:
                    if self._has_cycle(neighbor, graph, visited, rec_stack, path):
                        return True
                elif neighbor in rec_stack:
                    return True
        
        path.pop()
        rec_stack.remove(node)
        return False


def main():
    """Main entry point."""
    root = Path(__file__).parent.parent
    
    updater = ImportUpdater(root)
    
    # Update imports
    files_updated, errors = updater.update_all_imports()
    
    # Check circular dependencies
    circular_deps = updater.check_circular_dependencies()
    
    # Report results
    print(f"\n=== Import Update Results ===")
    print(f"Files updated: {files_updated}")
    print(f"Errors: {len(errors)}")
    print(f"Circular dependencies detected: {len(circular_deps)}")
    
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
    
    if circular_deps:
        print("\nCircular Dependencies:")
        for dep in circular_deps:
            print(f"  - {dep}")
    
    return 0 if not errors and not circular_deps else 1


if __name__ == "__main__":
    exit(main())
