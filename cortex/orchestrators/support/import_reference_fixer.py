"""
AC_START: AC-PHASE44-S4-002
ImportReferenceFixer - Automated import reference fixing
Phase 44 Stage 4 - Production Readiness Infrastructure
"""

import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ImportReferenceFixer:
    """
    Automated import reference fixing after file relocations.
    
    Features:
    - Fix absolute imports (update module paths)
    - Fix relative imports (recalculate relative levels)
    - Update __init__.py files
    - Validate imports post-fix
    - Detect circular imports
    
    Usage:
        fixer = ImportReferenceFixer()
        fixer.fix_absolute_imports(file_path, relocations)
        validation = fixer.validate_imports(file_path)
    """
    
    def __init__(self) -> None:
        """Initialize ImportReferenceFixer."""
        self.import_fixes: List[Dict[str, Any]] = []
        self.validation_errors: List[Dict[str, Any]] = []
    
    def fix_absolute_imports(self, file_path: str, relocations: Dict[str, str]) -> bool:
        """
        Fix absolute imports based on relocation map.
        
        AC-044-S4-01: Updates module paths correctly
        AC-044-S4-02: Handles multi-level imports (a.b.c.d)
        
        Args:
            file_path: Path to Python file to fix
            relocations: Dictionary mapping old module → new module
        
        Returns:
            True if fixes applied, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix imports in content
            for old_module, new_module in relocations.items():
                # Pattern for: from old_module import ...
                pattern = rf'from\s+{re.escape(old_module)}(\.\w+)*\s+import'
                replacement = f'from {new_module}\\1 import'
                content = re.sub(pattern, replacement, content)
                
                # Pattern for: import old_module
                pattern = rf'import\s+{re.escape(old_module)}(\.\w+)*'
                replacement = f'import {new_module}\\1'
                content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.import_fixes.append({
                    "file": file_path,
                    "fixes": len(relocations),
                    "status": "success"
                })
                logger.info(f"Fixed absolute imports in {file_path}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Failed to fix imports in {file_path}: {e}")
            return False
    
    def fix_relative_imports(self, file_path: str, depth_change: int) -> bool:
        """
        Fix relative imports based on directory depth change.
        
        AC-044-S4-03: Recalculates relative paths
        AC-044-S4-04: Handles parent directory imports (..)
        
        Args:
            file_path: Path to Python file to fix
            depth_change: Change in directory depth (+1 = deeper, -1 = shallower)
        
        Returns:
            True if fixes applied, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                # Match relative imports: from .module import ... or from ..module import ...
                match = re.match(r'^(\s*)from\s+(\.+)(\w*)\s+(import.*)$', line)
                if match:
                    indent = match.group(1)
                    dots = match.group(2)
                    module = match.group(3)
                    import_clause = match.group(4)
                    
                    # Adjust dot count based on depth change
                    new_dots = '.' * (len(dots) + depth_change)
                    
                    if new_dots:  # Only if dots remain
                        lines[i] = f"{indent}from {new_dots}{module} {import_clause}"
            
            content = '\n'.join(lines)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.import_fixes.append({
                    "file": file_path,
                    "depth_change": depth_change,
                    "status": "success"
                })
                logger.info(f"Fixed relative imports in {file_path}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Failed to fix relative imports in {file_path}: {e}")
            return False
    
    def validate_imports(self, file_path: str) -> Dict[str, Any]:
        """
        Validate imports in file by attempting to parse with AST.
        
        AC-044-S4-05: Validates imports post-fix
        AC-044-S4-06: Reports validation failures
        
        Args:
            file_path: Path to Python file to validate
        
        Returns:
            Dictionary with validation results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse with AST
            ast.parse(content)
            
            return {
                "valid": True,
                "file": file_path,
                "errors": []
            }
        
        except SyntaxError as e:
            error = {
                "line": e.lineno,
                "message": str(e),
                "type": "SyntaxError"
            }
            self.validation_errors.append(error)
            
            return {
                "valid": False,
                "file": file_path,
                "errors": [error]
            }
        
        except Exception as e:
            error = {
                "message": str(e),
                "type": type(e).__name__
            }
            self.validation_errors.append(error)
            
            return {
                "valid": False,
                "file": file_path,
                "errors": [error]
            }
    
    def detect_circular_imports(self, file_paths: List[str]) -> List[tuple]:
        """
        Detect circular import dependencies.
        
        AC-044-S4-07: Detects circular imports
        
        Args:
            file_paths: List of Python files to analyze
        
        Returns:
            List of circular import pairs
        """
        from cortex.orchestrators.support.import_reference_analyzer import ImportReferenceAnalyzer
        
        analyzer = ImportReferenceAnalyzer()
        return analyzer.detect_circular_imports(file_paths)
    
    def update_init_file(self, init_path: str, relocations: Dict[str, str]) -> bool:
        """
        Update __init__.py file imports after relocations.
        
        AC-044-S4-09: Updates package imports
        AC-044-S4-10: Maintains package structure
        
        Args:
            init_path: Path to __init__.py file
            relocations: Dictionary mapping old imports → new imports
        
        Returns:
            True if updates applied, False otherwise
        """
        try:
            with open(init_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix relative package imports
            for old_import, new_import in relocations.items():
                # Pattern for: from .old_module import ...
                pattern = rf'from\s+{re.escape(old_import)}\s+import'
                replacement = f'from {new_import} import'
                content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                with open(init_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"Updated __init__.py: {init_path}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Failed to update {init_path}: {e}")
            return False
    
    def get_fix_summary(self) -> Dict[str, Any]:
        """
        Get summary of import fixes applied.
        
        Returns:
            Dictionary with fix statistics
        """
        return {
            "total_fixes": len(self.import_fixes),
            "fixes": self.import_fixes,
            "validation_errors": self.validation_errors
        }


# AC_COMPLETE: AC-PHASE44-S4-002 ✅ ImportReferenceFixer implemented with 5 core methods
