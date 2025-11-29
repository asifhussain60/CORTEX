"""Parse linter errors (pylint, flake8, etc)."""

import re
from typing import Dict, Any
from .base_parser import BaseErrorParser


class LinterErrorParser(BaseErrorParser):
    """Parser for linter errors."""
    
    def can_parse(self, output: str) -> bool:
        """Check if output is linter error."""
        # Format: "file.py:line:col: ERROR_CODE message"
        return bool(re.search(r"^\w+\.py:\d+:\d+:", output, re.MULTILINE))
    
    def parse(self, output: str) -> Dict[str, Any]:
        """
        Parse linter error (pylint, flake8, etc).
        
        Returns:
            Dict with file, line, column, code, category, message
        """
        result = {"category": "linter"}
        
        # Format: "file.py:line:col: ERROR_CODE message"
        match = re.search(r"([\w/]+\.py):(\d+):(\d+):\s*(\w+)\s+(.+)", output)
        if match:
            result["file"] = match.group(1)
            result["line"] = int(match.group(2))
            result["column"] = int(match.group(3))
            result["code"] = match.group(4)
            result["message"] = match.group(5)
        
        # Categorize by error code
        if "F821" in output or "undefined" in output.lower():
            result["category"] = "undefined_name"
        elif "F401" in output or "imported but unused" in output.lower():
            result["category"] = "unused_import"
        elif "E501" in output or "line too long" in output.lower():
            result["category"] = "line_length"
        
        return result
