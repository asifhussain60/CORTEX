"""Fix import-related errors."""

from pathlib import Path
from typing import Dict, Any, Optional
from .base_strategy import BaseFixStrategy


class ImportFixStrategy(BaseFixStrategy):
    """Strategy for fixing import errors."""
    
    # Common import suggestions
    IMPORT_MAP = {
        "Path": "from pathlib import Path",
        "datetime": "from datetime import datetime",
        "json": "import json",
        "re": "import re",
        "os": "import os",
        "sys": "import sys",
    }
    
    def can_fix(self, parsed_error: Dict[str, Any], fix_pattern: Dict[str, Any]) -> bool:
        """Check if this is an import-related error."""
        return (
            parsed_error.get("category") in ["import", "undefined_name", "unused_import"] or
            fix_pattern.get("action") in ["add_import", "remove_import"]
        )
    
    def apply_fix(
        self, 
        parsed_error: Dict[str, Any], 
        fix_pattern: Dict[str, Any],
        file_path: Optional[str]
    ) -> Dict[str, Any]:
        """
        Fix import errors by adding or removing imports.
        
        Returns:
            Fix result with success, message, changes, import_statement
        """
        action = fix_pattern.get("action")
        params = fix_pattern.get("params", {})
        
        if action == "add_import":
            return self._add_import(parsed_error, params)
        elif action == "remove_import":
            return self._remove_import(file_path, parsed_error)
        else:
            return {
                "success": False,
                "message": f"Unknown import action: {action}"
            }
    
    def _add_import(self, parsed_error: Dict, params: Dict) -> Dict[str, Any]:
        """Suggest adding import statement."""
        name = params.get("name") or parsed_error.get("undefined_name")
        
        if not name:
            return {
                "success": False,
                "message": "Cannot determine what to import"
            }
        
        # Get suggested import
        suggested_import = self.IMPORT_MAP.get(name, f"import {name}")
        
        return {
            "success": True,
            "message": f"Add import: {suggested_import}",
            "changes": [suggested_import],
            "import_statement": suggested_import
        }
    
    def _remove_import(self, file_path: Optional[str], parsed_error: Dict) -> Dict[str, Any]:
        """Suggest removing unused import."""
        if not file_path:
            return {
                "success": False,
                "message": "File path required"
            }
        
        line_num = parsed_error.get("line")
        
        return {
            "success": True,
            "message": f"Remove unused import at line {line_num}",
            "changes": [f"Delete line {line_num}"],
            "line_to_remove": line_num
        }
