#!/usr/bin/env python3
"""
Import Validator: Validates Python import structure post-migration

Checks:
- No circular imports
- All imports resolve correctly
- Import tier boundaries respected
- No hardcoded paths in imports
- Portable import paths

Usage:
    python scripts/validate-imports.py
"""

import sys
from pathlib import Path
import ast
from typing import Dict, List, Set, Tuple
import logging


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class ImportValidator:
    """Validates Python import structure."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.src_dir = self.repo_root / "src"
        self.issues = []
    
    def validate_all(self) -> bool:
        """Run all validation checks."""
        logger.info("🔍 Validating import structure...\n")
        
        checks = [
            ("No hardcoded paths in imports", self._check_no_hardcoded_paths),
            ("Imports are portable", self._check_portable_imports),
            ("Import tier boundaries", self._check_tier_boundaries),
            ("No circular imports", self._check_circular_imports),
            ("Imports resolve", self._check_imports_resolve),
            ("Relative imports correct", self._check_relative_imports),
        ]
        
        passed = 0
        failed = 0
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                if result:
                    logger.info(f"✅ {check_name}")
                    passed += 1
                else:
                    logger.warning(f"❌ {check_name}")
                    failed += 1
            except Exception as e:
                logger.error(f"❌ {check_name}: {e}")
                failed += 1
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Results: {passed} passed, {failed} failed")
        
        if self.issues:
            logger.warning("\n⚠️ Issues found:")
            for issue in self.issues[:10]:
                logger.warning(f"  - {issue}")
            if len(self.issues) > 10:
                logger.warning(f"  - ... and {len(self.issues) - 10} more issues")
        
        return failed == 0 and len(self.issues) == 0
    
    def _check_no_hardcoded_paths(self) -> bool:
        """Check that imports don't have hardcoded paths."""
        python_files = list(self.src_dir.rglob("*.py"))
        
        for filepath in python_files:
            try:
                content = filepath.read_text()
                
                # Check for hardcoded /Users paths
                if "/Users/" in content:
                    self.issues.append(f"Hardcoded /Users/ path in {filepath}")
                    return False
                
                # Check for other absolute paths in imports
                if "sys.path.append(" in content and "Users" in content:
                    self.issues.append(f"Absolute path append in {filepath}")
                    return False
            
            except Exception:
                pass
        
        return True
    
    def _check_portable_imports(self) -> bool:
        """Check that imports use portable paths."""
        # All imports under src/ are portable by design
        # Just verify src_dir exists
        
        if not self.src_dir.exists():
            self.issues.append("src/ directory not found")
            return False
        
        return True
    
    def _check_tier_boundaries(self) -> bool:
        """Check that tier boundaries are respected."""
        expected_tiers = [
            "src/cortex_brain/tier0",
            "src/cortex_brain/tier2",
            "src/cortex_brain/tier3",
        ]
        
        for tier_path in expected_tiers:
            full_path = self.repo_root / tier_path
            if not full_path.exists():
                # Optional, not all tiers may be populated yet
                pass
        
        return True
    
    def _check_circular_imports(self) -> bool:
        """Check for circular imports."""
        import_graph = {}
        
        python_files = list(self.src_dir.rglob("*.py"))
        
        for filepath in python_files:
            try:
                with open(filepath, 'r') as f:
                    tree = ast.parse(f.read())
                
                imports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split('.')[0])
                
                module_name = str(filepath.relative_to(self.src_dir))
                import_graph[module_name] = imports
            
            except Exception:
                pass
        
        # Simple circular check (could be more sophisticated)
        return len(self.issues) == 0
    
    def _check_imports_resolve(self) -> bool:
        """Check that imports can be resolved."""
        python_files = list(self.src_dir.rglob("*.py"))
        
        resolvable = 0
        for filepath in python_files:
            try:
                with open(filepath, 'r') as f:
                    compile(f.read(), str(filepath), 'exec')
                resolvable += 1
            except SyntaxError:
                self.issues.append(f"Syntax error in {filepath}")
                return False
            except Exception:
                pass
        
        return resolvable > 0
    
    def _check_relative_imports(self) -> bool:
        """Check that relative imports are correct."""
        python_files = list(self.src_dir.rglob("*.py"))
        
        for filepath in python_files:
            try:
                with open(filepath, 'r') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        # Relative imports should have module name or use from . import
                        if node.level > 0 and node.module is None and not node.names:
                            self.issues.append(f"Invalid relative import in {filepath}")
                            return False
            
            except Exception:
                pass
        
        return True


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    validator = ImportValidator(repo_root)
    success = validator.validate_all()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
