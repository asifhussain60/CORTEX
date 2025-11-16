"""Parse import errors."""

import re
from typing import Dict, Any
from .base_parser import BaseErrorParser


class ImportErrorParser(BaseErrorParser):
    """Parser for import errors."""
    
    def can_parse(self, output: str) -> bool:
        """Check if output is import error."""
        return "ImportError" in output or "ModuleNotFoundError" in output
    
    def parse(self, output: str) -> Dict[str, Any]:
        """
        Parse import error.
        
        Returns:
            Dict with type, file, line, category, message, missing_module, missing_name
        """
        result = {"type": "import", "category": "import"}
        
        # Look for: "ModuleNotFoundError: No module named 'xyz'"
        module_match = re.search(r"No module named ['\"]([^'\"]+)['\"]", output)
        if module_match:
            result["missing_module"] = module_match.group(1)
            result["message"] = f"Missing module: {module_match.group(1)}"
        
        # Look for: "ImportError: cannot import name 'xyz'"
        name_match = re.search(r"cannot import name ['\"]([^'\"]+)['\"]", output)
        if name_match:
            result["missing_name"] = name_match.group(1)
            result["message"] = f"Cannot import: {name_match.group(1)}"
        
        # Get file and line
        file_match = re.search(r'File "([^"]+)", line (\d+)', output)
        if file_match:
            result["file"] = file_match.group(1)
            result["line"] = int(file_match.group(2))
        
        return result
